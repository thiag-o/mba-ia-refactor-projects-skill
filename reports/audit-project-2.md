# Architecture Audit Report

- **Project:** ecommerce-api-legacy (Frankenstein LMS)
- **Stack:** JavaScript (Node.js) + Express ^4.18.2 (SQLite via `sqlite3`)
- **Files:** 3 analyzed | ~180 lines of code

## Summary

| Severity | Count |
| -------- | ----: |
| CRITICAL | 4     |
| HIGH     | 5     |
| MEDIUM   | 3     |
| LOW      | 3     |
| **Total**| **15** |

## Findings

### [CRITICAL] Hardcoded credentials and secrets in source code

- **File:** `src/utils.js:1-7`, `src/AppManager.js:45`
- **Description:** The `config` object embeds real-looking secrets directly in source: `dbUser`, `dbPass = "senha_super_secreta_prod_123"`, `paymentGatewayKey = "pk_live_..."` and `smtpUser`. Worse, the payment gateway key is written to stdout on every checkout (`console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`).
- **Impact:** Sensitive production credentials are versioned in the repo and leaked into logs, allowing anyone with repo/log access to abuse the payment gateway, DB and SMTP. Full credential compromise.
- **Recommendation:** Extract all secrets to environment variables (`process.env.*`) with a config module; never log secrets or card numbers. Playbook **P-01**.

### [CRITICAL] Insecure password handling (weak custom hash, plaintext seed, default password)

- **File:** `src/utils.js:17-23`, `src/AppManager.js:18`, `src/AppManager.js:68`
- **Description:** Passwords are "hashed" by a homemade `badCrypto()` that base64-encodes and truncates to 10 chars (no salt, trivially reversible/colliding). The seed user is stored in plaintext (`pass = '123'`), and when no password is sent a default `"123456"` is silently assigned.
- **Impact:** Credentials are effectively unprotected — trivial to crack or forge, enabling account takeover. CRITICAL.
- **Recommendation:** Replace with `bcrypt`/`argon2` (per-user salt, proper cost). Require a real password; never assign defaults. Never store or return password fields. Playbook **P-05**.

### [CRITICAL] God Class concentrating DB, routing and business logic

- **File:** `src/AppManager.js:1-142`
- **Description:** `AppManager` owns everything: DB connection creation (`constructor`), schema + seed (`initDb`), all route definitions, request validation, payment processing, enrollment, auditing and cache writes (`setupRoutes`). No separation between config, models, controllers, services or routes.
- **Impact:** Complete violation of separation of responsibilities; impossible to unit-test in isolation, any change risks breaking unrelated behavior. CRITICAL.
- **Recommendation:** Decompose into `config/`, `models`/repositories, `controllers/`, `services/`, `routes/` and `middlewares/` with a clear composition root. Playbook **P-03**.

### [CRITICAL] Destructive route without authentication (DELETE /users/:id)

- **File:** `src/AppManager.js:131-137`
- **Description:** `DELETE /api/users/:id` deletes any user by id with no authentication/authorization. The handler even ignores the DB error and returns a message admitting it leaves orphaned enrollments and payments (`"Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."`).
- **Impact:** Any anonymous client can destroy user records and corrupt referential integrity (orphaned enrollments/payments). Destructive + unauthenticated = CRITICAL.
- **Recommendation:** Require auth/authorization middleware on sensitive/destructive routes; handle cascade/transaction and DB errors properly. Playbook **P-09** + **P-08**.

### [HIGH] Business logic and side effects inside HTTP handlers

- **File:** `src/AppManager.js:28-78`, `src/AppManager.js:80-129`
- **Description:** Payment decisioning (`status = cc.startsWith("4") ? "PAID" : "DENIED"`), enrollment creation, payment persistence, audit logging and cache writes all live directly in the checkout route handler; revenue aggregation logic lives in the report handler.
- **Impact:** Business rules are coupled to the transport layer — not reusable, not testable, duplicated risk. HIGH.
- **Recommendation:** Move rules into dedicated services (e.g. `CheckoutService`, `FinancialReportService`, `PaymentGateway`). Playbook **P-04**.

### [HIGH] Global mutable state shared across the process

- **File:** `src/utils.js:9-10`, `src/utils.js:12-15`
- **Description:** `globalCache = {}` and `totalRevenue = 0` are module-level mutable singletons; `logAndCache` mutates the shared cache from within request handling.
- **Impact:** Race conditions and unpredictable state under concurrency; data from one request bleeds into another. HIGH.
- **Recommendation:** Scope state per-request or use an injected cache abstraction with proper lifecycle. Playbook **P-06**.

### [HIGH] Tight coupling without dependency injection

- **File:** `src/AppManager.js:1-7`, `src/AppManager.js:2`
- **Description:** `AppManager` instantiates its own dependencies (`new sqlite3.Database(':memory:')` in the constructor) and imports helpers directly, with no constructor injection. Nothing can be mocked or swapped.
- **Impact:** Testing requires real infrastructure; violates DIP; hard to change persistence. HIGH.
- **Recommendation:** Inject the DB/connection and collaborators via constructor; wire them in the composition root. Playbook **P-06**.

### [HIGH] Sensitive admin/financial route without authentication

- **File:** `src/AppManager.js:80`
- **Description:** `GET /api/admin/financial-report` exposes full revenue and student data (names, emails, amounts paid) with no auth middleware.
- **Impact:** Any anonymous client reads confidential financial and PII data. HIGH.
- **Recommendation:** Protect admin/financial routes with authentication + authorization middleware. Playbook **P-09**.

### [HIGH] Callback hell with manual concurrency and unchecked errors

- **File:** `src/AppManager.js:37-78`, `src/AppManager.js:83-128`
- **Description:** Deeply nested callbacks; the financial report uses manual completion counters (`coursesPending--; if (coursesPending === 0) res.json(report)`, `enrPending--`) to coordinate async work, and several `err` arguments are received but never checked (e.g. lines 92, 104, 106).
- **Impact:** Race conditions, partial/incomplete responses, and silent failures; very hard to maintain. HIGH.
- **Recommendation:** Convert to `async/await` (promisified DB access) with `Promise.all`, plus a central error handler. Playbook **P-10** + **P-08**.

### [MEDIUM] N+1 query pattern in financial report

- **File:** `src/AppManager.js:89-127`
- **Description:** For each course a query fetches its enrollments, then for each enrollment two more queries fetch the user and the payment — queries grow linearly with data volume.
- **Impact:** Query count explodes as courses/enrollments grow; degraded performance. MEDIUM.
- **Recommendation:** Replace with a single JOIN (courses ⋈ enrollments ⋈ users ⋈ payments) and aggregate in memory. Playbook **P-07**.

### [MEDIUM] Generic / missing error handling and no central error handler

- **File:** `src/AppManager.js:133-136`, `src/AppManager.js:38-41`, `src/AppManager.js:92`, `src/AppManager.js:104-106`
- **Description:** The DELETE handler ignores the DB error entirely and always returns success text; several callbacks discard `err`; errors are returned as ad-hoc `res.status(500).send("Erro DB")` strings with no consistent shape and no Express error-handling middleware.
- **Impact:** Failures are masked and reported as success, hiding bugs and returning inconsistent error contracts. MEDIUM.
- **Recommendation:** Introduce a centralized error-handling middleware and propagate specific errors via `next(err)`. Playbook **P-08**.

### [MEDIUM] In-memory database used as the persistence layer

- **File:** `src/AppManager.js:7`, `src/AppManager.js:10-23`
- **Description:** The application uses `sqlite3.Database(':memory:')` and re-creates schema + seeds on every boot, so all data is lost on restart.
- **Impact:** No durable persistence; data cannot survive a restart — unsuitable beyond a demo. MEDIUM.
- **Recommendation:** Make the DB path/driver configurable via environment (file-backed or a real DB) and separate schema/seed setup from runtime. Playbook **P-01**.

### [LOW] Logging via `console.log`

- **File:** `src/utils.js:13`, `src/AppManager.js:45`, `src/AppManager.js:57` (via `logAndCache`), `src/app.js:13`
- **Description:** Ad-hoc `console.log` used as the logging mechanism throughout, including logging sensitive data.
- **Impact:** No log levels/structure; noisy and leaks data. LOW.
- **Recommendation:** Use a structured logger with levels and redaction. See Playbook **P-08**.

### [LOW] Cryptic variable names and unused imports

- **File:** `src/AppManager.js:29-33`, `src/AppManager.js:2`, `src/AppManager.js:26`
- **Description:** One-letter/cryptic locals (`u`, `e`, `p`, `cid`, `cc`); `totalRevenue` is imported but never used; a `const self = this` workaround is mixed with `this` usage in the same handlers.
- **Impact:** Reduced readability and maintainability. LOW.
- **Recommendation:** Use descriptive English names, remove unused imports, and rely on arrow functions/lexical `this`. Playbook **P-14**.

### [LOW] Magic numbers / magic literals

- **File:** `src/AppManager.js:47`, `src/utils.js:19`, `src/utils.js:22`, `src/AppManager.js:68`
- **Description:** Payment approval keys off the literal card prefix `"4"`; `badCrypto` loops a magic `10000` and slices to `10`/`2`; default password `"123456"`.
- **Impact:** Intent is opaque and rules are hard to change safely. LOW.
- **Recommendation:** Extract named constants and move payment approval into a proper gateway abstraction. Playbook **P-13**.

## Deprecated APIs

- Callback-based SQLite I/O (`db.get`/`db.run`/`db.all` with callbacks) in `src/AppManager.js:37-128` → use `async/await` via `util.promisify` or a promise-based DB wrapper.
- Homemade weak hashing `badCrypto` in `src/utils.js:17-23` → use `bcrypt`/`argon2` with per-user salt.
