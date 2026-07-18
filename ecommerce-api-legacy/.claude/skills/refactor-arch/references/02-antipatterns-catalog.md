# 02 — Anti-patterns Catalog (Fase 2)

Catálogo de anti-patterns com **sinais de detecção concretos**, **severidade
justificada** e **link para o padrão de correção** no playbook (área 5).
Aplique estes sinais a qualquer stack; não presuma linguagem.

## Escala de severidade oficial

- **CRITICAL** — falhas graves de arquitetura ou segurança que impedem o
  funcionamento correto, expõem dados sensíveis (credenciais hardcoded, SQL
  Injection) ou violam completamente a separação de responsabilidades (God Class
  com banco + lógica + roteamento no mesmo arquivo).
- **HIGH** — fortes violações de MVC/SOLID que dificultam muito manutenção e
  testes (lógica de negócio pesada em Controllers, forte acoplamento sem Injeção
  de Dependência, estado global mutável em toda a aplicação).
- **MEDIUM** — padronização, duplicação de código ou gargalos de performance
  moderada (N+1, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW** — legibilidade, nomenclatura ruim, magic numbers soltos.

## Regras de aplicação

- **Todo finding é comprovável** com `arquivo:linha(s)`.
- **Agrupe** ocorrências repetidas do mesmo problema em um único finding, citando
  todos os locais.
- **Não invente**: se o sinal não existir, o anti-pattern **não se aplica**.
  Placeholders parametrizados (`?`, binds do ORM) **não** são SQL Injection.

---

## AP-01 · SQL Injection por concatenação — **CRITICAL**

- **Sinais:** query construída com `+`, f-string (`f"... {var} ..."`), template
  string (`` `... ${var} ...` ``) ou `%`/`.format()` **contendo variável vinda do
  request** e passada a `execute`/`query`/`run`. Ex.: `cursor.execute("... WHERE
  email = '" + email + "'")`; `query += " AND nome LIKE '%" + termo + "%'"`.
- **Por que é problema:** permite bypass de autenticação, leitura/alteração/
  exclusão de todo o banco. Segurança grave → CRITICAL.
- **Não confundir:** `execute("... WHERE id = ?", (id,))` ou binds do ORM são
  seguros e **não** são findings.
- **Correção:** Playbook **P-02 (parametrizar queries)**.

## AP-02 · Endpoint que executa SQL/entrada arbitrária — **CRITICAL**

- **Sinais:** rota que recebe uma string SQL/comando no corpo e a executa direto
  (`cursor.execute(request...get("sql"))`, `eval`, `exec`), ou rota destrutiva
  (`DELETE`/`DROP`/`reset`) **sem autenticação**.
- **Por que é problema:** RCE de banco / destruição de dados por qualquer cliente.
- **Correção:** remover o endpoint; nunca expor SQL cru via HTTP. Playbook
  **P-09 (auth em rotas sensíveis)** + remoção.

## AP-03 · Credenciais / segredos hardcoded — **CRITICAL**

- **Sinais:** literais como `SECRET_KEY = "..."`, `password/senha = "..."`,
  `apiKey/paymentGatewayKey = "pk_live_..."`, `smtpUser/email_password = "..."`
  embutidos no código; pior ainda se **devolvidos em uma resposta** (ex.: um
  `/health` retornando a secret).
- **Por que é problema:** credencial sensível versionada e vazável. CRITICAL.
- **Correção:** Playbook **P-01 (extrair configuração para env vars)**.

## AP-04 · Senha insegura (texto plano / hash fraco / exposta) — **CRITICAL**

- **Sinais:** senha gravada sem hash; hash fraco/reversível (`hashlib.md5`,
  `sha1`, base64, "badCrypto" caseiro) e **sem salt**; campo `password`/`senha`/
  hash incluído em `to_dict()` / payload de resposta; senha default (`"123456"`)
  criada quando nenhuma é enviada.
- **Por que é problema:** vazamento/quebra trivial de credenciais. CRITICAL.
- **Correção:** Playbook **P-05 (hash seguro + remover campo sensível da
  serialização)**.

## AP-05 · God Class / God Method — **CRITICAL**

- **Sinais:** um único arquivo/classe concentra criação de banco, definição de
  todas as rotas, validação, regra de negócio, pagamento, cache, etc. (ex.: uma
  classe `AppManager` com `initDb()` + `setupRoutes()`); ou um `models.py` único
  cobrindo múltiplos domínios com SQL + regra + formatação.
- **Por que é problema:** violação completa de separação de responsabilidades;
  impossível testar em isolamento; qualquer mudança afeta tudo. CRITICAL.
- **Correção:** Playbook **P-03 (quebrar God Class em camadas)**.

## AP-06 · Lógica de negócio no controller / na camada errada — **HIGH**

- **Sinais:** cálculo de desconto/faturamento/regras dentro da model de
  persistência ou dentro do handler HTTP; efeitos colaterais de negócio
  (enviar e-mail/SMS/push, mesmo simulados com `print`/`console.log`) no meio do
  controller.
- **Por que é problema:** regra acoplada à camada errada, não reutilizável nem
  testável. HIGH.
- **Correção:** Playbook **P-04 (mover regra para service)**.

## AP-07 · Estado global mutável / conexão compartilhada — **HIGH**

- **Sinais:** conexão de banco como singleton global reutilizado entre requisições
  (`db_connection = None` + `global`, `check_same_thread=False`); variáveis
  mutáveis de módulo (`globalCache = {}`, `totalRevenue = 0`) compartilhadas por
  todo o processo.
- **Por que é problema:** condições de corrida, corrupção de dados sob
  concorrência, estado imprevisível. HIGH.
- **Correção:** Playbook **P-06 (escopo por-requisição / injeção)**.

## AP-08 · Forte acoplamento sem Injeção de Dependência — **HIGH**

- **Sinais:** classes instanciam suas dependências diretamente
  (`new sqlite3.Database(...)`, `Repo()` dentro do controller), impossibilitando
  mocks/troca; ausência de construtor recebendo dependências.
- **Por que é problema:** testes inviáveis sem infra real; violação de DIP. HIGH.
- **Correção:** Playbook **P-06 (injeção de dependência)**.

## AP-09 · Rota sensível sem autenticação/autorização — **HIGH**

- **Sinais:** rotas administrativas/financeiras/destrutivas
  (`/admin/...`, `financial-report`, `DELETE /users/:id`) sem middleware de auth;
  "token" fake (`'fake-jwt-token-' + id`) que ninguém valida.
- **Por que é problema:** qualquer anônimo lê dados sensíveis ou destrói recursos.
  HIGH (CRITICAL se combinada com ação destrutiva — ver AP-02).
- **Correção:** Playbook **P-09 (auth middleware em rotas sensíveis)**.

## AP-10 · Callback hell / concorrência manual sem tratamento de erro — **HIGH**

- **Sinais:** callbacks aninhados com contadores manuais de conclusão
  (`pending--; if (pending === 0) res.json(...)`); `err` recebido mas nunca
  verificado; ausência de `async/await`/`Promise.all`.
- **Por que é problema:** condições de corrida, respostas incompletas, difícil
  manutenção. HIGH.
- **Correção:** Playbook **P-10 (async/await + Promise.all)** e
  **P-08 (error handler central)**.

## AP-11 · Queries N+1 — **MEDIUM**

- **Sinais:** loop sobre resultados executando 1+ query por item
  (`for pedido in pedidos: cursor.execute("... WHERE pedido_id = ...")`;
  `for t in tasks: User.query.get(t.user_id)`).
- **Por que é problema:** nº de queries cresce linearmente com os dados. MEDIUM.
- **Correção:** Playbook **P-07 (JOIN / eager loading)**.

## AP-12 · Ausência de paginação — **MEDIUM**

- **Sinais:** listagens sem `limit`/`offset` (`Task.query.all()`,
  `SELECT * FROM ...` sem `LIMIT`) retornando todos os registros.
- **Por que é problema:** payloads enormes e degradação de performance. MEDIUM.
- **Correção:** Playbook **P-11 (adicionar paginação)**.

## AP-13 · Duplicação de validação / regra — **MEDIUM**

- **Sinais:** o mesmo bloco de validação (título/status/data, etc.) repetido em
  create/update ou em várias rotas; helper de validação existente **não usado**.
- **Por que é problema:** divergência de regras entre cópias. MEDIUM.
- **Correção:** Playbook **P-12 (extrair validação para helper compartilhado)**.

## AP-14 · Tratamento de erro genérico / ausente — **MEDIUM**

- **Sinais:** `except:` sem tipo devolvendo "Erro interno"; `catch` vazio; `err`
  ignorado; ausência de error handler central.
- **Por que é problema:** mascara a causa real, esconde bugs, falhas silenciosas
  retornadas como sucesso. MEDIUM.
- **Correção:** Playbook **P-08 (error handler central + exceções específicas)**.

## AP-15 · Configuração insegura de ambiente / CORS — **MEDIUM**

- **Sinais:** `debug=True`/`DEBUG=True` tratado como produção; `CORS(app)` aberto
  a qualquer origem; banco `:memory:` onde se espera persistência.
- **Por que é problema:** amplia superfície de ataque (RCE via debugger do
  Werkzeug, CSRF/abuso cross-origin). MEDIUM.
- **Correção:** Playbook **P-01 (config por ambiente)** + restringir CORS.

## AP-16 · Magic numbers — **LOW**

- **Sinais:** limites/taxas/faixas soltos no código (`if faturamento > 10000`,
  `desconto = x * 0.1`, faixa de prioridade `1..5` repetida).
- **Correção:** Playbook **P-13 (extrair constantes nomeadas)**.

## AP-17 · Logging via `print`/`console.log` — **LOW**

- **Sinais:** `print(...)` / `console.log(...)` espalhados como mecanismo de log.
- **Correção:** módulo de logging estruturado (níveis, formato). Ver P-08.

## AP-18 · Imports não usados / nomes crípticos / código verboso — **LOW**

- **Sinais:** imports declarados e nunca usados (`os, sys, json, hashlib`);
  variáveis `u`, `e`, `p`, `cc`; `if cond: return True else: return False`;
  mistura de `this`/`self`; duplicação de mapeamento `row → dict`.
- **Correção:** Playbook **P-14 (limpeza de legibilidade)**.

---

## Deprecated APIs (obrigatório detectar)

Identifique uso de APIs obsoletas e recomende o **equivalente moderno**.
Trate como finding próprio (severidade conforme o risco: segurança → alta).

| API deprecated / obsoleta | Stack | Equivalente moderno recomendado |
|---|---|---|
| `datetime.utcnow()` | Python 3.12+ | `datetime.now(timezone.utc)` |
| `hashlib.md5` / `sha1` para senhas | Python | `bcrypt` / `argon2` (com salt) |
| `crypto.createCipher` | Node | `crypto.createCipheriv` |
| `new Buffer(x)` | Node | `Buffer.from(x)` / `Buffer.alloc(n)` |
| callbacks de I/O | Node | `async/await` + versões `fs.promises`/`util.promisify` |
| `url.parse()` | Node | `new URL()` (WHATWG) |
| `request` (lib) | Node | `fetch` nativo / `axios` / `undici` |
| `flask.Markup`, `@app.before_first_request` | Flask ≥ 2.3 | `markupsafe.Markup`; init no app factory |
| `werkzeug.security` com esquemas legados | Flask | `bcrypt`/`argon2` explícitos |
| `Query.get(id)` (SQLAlchemy legado) | SQLAlchemy 2.0 | `session.get(Model, id)` |

> Regra: um placeholder parametrizado, um ORM com binds ou uma API atual **não**
> devem virar finding. Só reporte APIs comprovadamente obsoletas/deprecated.
