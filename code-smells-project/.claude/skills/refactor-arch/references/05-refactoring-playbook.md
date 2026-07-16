# 05 — Refactoring Playbook (Fase 3)

Padrões de transformação **antes → depois**, cada um mapeado a um anti-pattern do
catálogo (área 2). Exemplos curtos e ilustrativos, em mais de uma stack quando
faz sentido, para reforçar o agnosticismo. Adapte ao contexto real do projeto.

---

## P-01 · Extrair configuração para `config/` (env vars) → AP-03, AP-15

**Sintoma:** secrets/credenciais/flags hardcoded no código.
**Estratégia:** mover para variáveis de ambiente lidas em um módulo de config;
nunca versionar valores reais.

```python
# ANTES — app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.run(debug=True)
```
```python
# DEPOIS — config/settings.py
import os
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
# app.py
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.run(debug=settings.DEBUG)
```
```javascript
// ANTES — utils.js
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_..." };
// DEPOIS — config/settings.js
module.exports = {
  dbPass: process.env.DB_PASS,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
};
```

---

## P-02 · Parametrizar queries (eliminar SQL Injection) → AP-01

**Sintoma:** query montada por concatenação/interpolação com entrada do usuário.
**Estratégia:** usar exclusivamente placeholders parametrizados.

```python
# ANTES
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
# DEPOIS
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha_hash = ?", (email, senha_hash))
```
```python
# Busca com LIKE — ANTES: query += " AND nome LIKE '%" + termo + "%'"
# DEPOIS
query += " AND nome LIKE ?"
params.append(f"%{termo}%")   # valor vinculado, não concatenado na SQL
cursor.execute(query, params)
```

---

## P-03 · Quebrar God Class em camadas → AP-05

**Sintoma:** uma classe/arquivo faz banco + rotas + validação + regra + pagamento.
**Estratégia:** separar em repository (dados), service (regra), controller
(orquestração) e routes (HTTP), um por responsabilidade/domínio.

```javascript
// ANTES — AppManager.js: initDb() + setupRoutes() + validação + pagamento + relatório
class AppManager { initDb(){/*...*/} setupRoutes(app){/* tudo aqui */} }

// DEPOIS
// models/user_repository.js   -> só persistência
// services/payment_service.js -> regra de pagamento
// controllers/checkout_controller.js -> orquestra
// routes/checkout_routes.js   -> define endpoints e delega ao controller
// app.js -> instancia e injeta as dependências (composition root)
```

---

## P-04 · Mover regra de negócio do controller/model para service → AP-06

**Sintoma:** cálculo de negócio ou efeito colateral (e-mail/SMS) dentro do
handler HTTP ou da model de persistência.
**Estratégia:** extrair para um service reutilizável e injetável.

```python
# ANTES — controllers.py
print("ENVIANDO EMAIL: Pedido " + str(pedido_id) + " criado")
print("ENVIANDO SMS: Seu pedido foi recebido!")
# DEPOIS — services/notification_service.py
class NotificationService:
    def notify_order_created(self, pedido_id): ...  # e-mail/SMS encapsulados
# controller
self.notifications.notify_order_created(pedido_id)
```

---

## P-05 · Hash seguro de senha + remover campo sensível → AP-04

**Sintoma:** senha em texto plano, MD5/base64 sem salt, ou `password` retornado
na resposta.
**Estratégia:** hash com bcrypt/argon2 na gravação; nunca serializar o campo.

```python
# ANTES — user.py
self.password = hashlib.md5(pwd.encode()).hexdigest()
def to_dict(self): return {"id": self.id, "password": self.password}
# DEPOIS
import bcrypt
def set_password(self, pwd):
    self.password = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
def check_password(self, pwd):
    return bcrypt.checkpw(pwd.encode(), self.password.encode())
def to_dict(self):  # sem 'password'
    return {"id": self.id, "email": self.email}
```

---

## P-06 · Substituir estado global / injetar dependência → AP-07, AP-08

**Sintoma:** conexão global entre threads ou dependência instanciada internamente.
**Estratégia:** escopo por-requisição (ex.: `flask.g`) ou injeção via construtor.

```python
# ANTES — database.py
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(path, check_same_thread=False)
    return db_connection
# DEPOIS — conexão por requisição
from flask import g
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(path)
    return g.db
```
```javascript
// ANTES: class AppManager { constructor(){ this.db = new sqlite3.Database(":memory:"); } }
// DEPOIS: injeta o repositório/conn
class CheckoutController { constructor(userRepo, paymentService){ this.userRepo = userRepo; } }
```

---

## P-07 · Eliminar N+1 (JOIN / eager loading) → AP-11

**Sintoma:** 1+ query por item dentro de um loop.
**Estratégia:** um único JOIN ou carregamento em lote / eager loading.

```python
# ANTES
for pedido in pedidos:
    itens = cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido["id"],))
# DEPOIS — um JOIN
cursor.execute("""
  SELECT p.*, i.* FROM pedidos p
  JOIN itens_pedido i ON i.pedido_id = p.id
""")
```
```python
# SQLAlchemy — ANTES: for t in tasks: User.query.get(t.user_id)
# DEPOIS
tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
```

---

## P-08 · Centralizar tratamento de erro em middleware → AP-14, AP-10, AP-17

**Sintoma:** `except:` genérico, `err` ignorado, `print` como log.
**Estratégia:** exceções específicas + um error handler central; logging estruturado.

```python
# ANTES
try: ...
except:
    return jsonify({"error": "Erro interno"}), 500
# DEPOIS — middlewares/error_handler.py
@app.errorhandler(Exception)
def handle(err):
    logger.exception(err)
    status = getattr(err, "status_code", 500)
    return jsonify({"error": str(err)}), status
```
```javascript
// DEPOIS — Express error middleware
app.use((err, req, res, next) => {
  logger.error(err);
  res.status(err.status || 500).json({ error: err.message });
});
```

---

## P-09 · Autenticação em rotas sensíveis → AP-09, AP-02

**Sintoma:** rota admin/destrutiva sem auth; token fake; endpoint que executa SQL.
**Estratégia:** middleware de auth/autorização; remover endpoints perigosos.

```python
# DEPOIS — middleware de auth aplicado às rotas sensíveis
def require_admin(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        user = verify_jwt(request.headers.get("Authorization"))
        if not user or not user.is_admin: abort(403)
        return fn(*a, **kw)
    return wrapper

@app.route("/admin/reports")
@require_admin
def reports(): ...
# Endpoint /admin/query que executava SQL cru: REMOVIDO.
```

---

## P-10 · Substituir callback hell por async/await → AP-10

**Sintoma:** callbacks aninhados com contadores manuais; erros não checados.

```javascript
// ANTES
enrPending--;
if (enrPending === 0) { report.push(courseData); coursesPending--;
  if (coursesPending === 0) res.json(report); }
// DEPOIS
const courses = await db.all("SELECT * FROM courses");
const report = await Promise.all(courses.map(async (c) => {
  const enr = await db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id]);
  return { ...c, enrollments: enr };
}));
res.json(report);
```

---

## P-11 · Adicionar paginação → AP-12

**Sintoma:** listagem sem limite retornando tudo.

```python
# ANTES: tasks = Task.query.all()
# DEPOIS
page = int(request.args.get("page", 1))
per_page = int(request.args.get("per_page", DEFAULT_PAGE_SIZE))
tasks = Task.query.paginate(page=page, per_page=per_page, error_out=False).items
```
```python
# SQL puro — DEPOIS
cursor.execute("SELECT * FROM produtos LIMIT ? OFFSET ?", (limit, offset))
```

---

## P-12 · Extrair validação duplicada para helper → AP-13

**Sintoma:** mesma validação repetida em create/update ou em várias rotas.

```python
# DEPOIS — utils/validators.py
def validate_task(data):
    errors = []
    if not data.get("title"): errors.append("title obrigatório")
    if data.get("status") not in VALID_STATUSES: errors.append("status inválido")
    return errors
# usada em create_task e update_task, sem duplicar regras
```

---

## P-13 · Extrair magic numbers para constantes → AP-16

**Sintoma:** limites/taxas/faixas soltos no código.

```python
# ANTES
if faturamento > 10000: desconto = faturamento * 0.1
elif faturamento > 5000: desconto = faturamento * 0.05
# DEPOIS — config/constants.py
DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
def compute_discount(faturamento):
    for limite, taxa in DISCOUNT_TIERS:
        if faturamento > limite: return faturamento * taxa
    return 0
```

---

## P-14 · Substituir APIs deprecated + limpeza de legibilidade → Deprecated APIs, AP-18

**Sintoma:** API obsoleta; imports não usados; nomes crípticos; retorno verboso.
**Estratégia:** trocar pela API moderna (ver tabela na área 2) e limpar o ruído.

```python
# Deprecated — ANTES: if t.due_date < datetime.utcnow():
# DEPOIS
from datetime import datetime, timezone
if t.due_date < datetime.now(timezone.utc): ...
```
```python
# Legibilidade — ANTES
def is_admin(self):
    if self.role == "admin": return True
    else: return False
# DEPOIS
def is_admin(self):
    return self.role == "admin"
```
```javascript
// Deprecated — ANTES: const b = new Buffer(pwd);
// DEPOIS: const b = Buffer.from(pwd);
// + remover imports não usados; renomear u/e/p/cc -> user/email/password/creditCard
```

---

> **Adaptação ao contexto:** em um monolito, a maioria destes padrões se aplica
> ao criar as camadas do zero (P-01..P-09). Em um projeto já parcialmente em
> camadas, foque nos débitos reais (P-05 hash/serialização, P-04 regra nas
> rotas, P-07/P-11/P-12/P-14) sem reescrever o que já está adequado.
