# Relatório de Problemas — Análise dos Projetos

> Data da análise: 2026-07-15
> Severidades: CRITICAL · HIGH · MEDIUM · LOW

## Sumário

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| code-smells-project | 5 | 4 | 3 | 3 | 15 |
| ecommerce-api-legacy | 5 | 4 | 3 | 3 | 15 |
| task-manager-api | 3 | 4 | 3 | 3 | 13 |
| **Total** | **13** | **12** | **9** | **9** | **43** |

---

## Projeto: code-smells-project

API de e-commerce em Python/Flask usando `sqlite3` puro (sem ORM). Estrutura em `app.py` (rotas), `controllers.py` (handlers) e `models.py` (acesso a dados). É o projeto com os problemas de segurança mais graves.

### 🔴 CRITICAL

1. **SQL Injection em praticamente todas as queries** — `code-smells-project/models.py:28,48-49,58-60,68,92,110,127-128,140,148-151,164-166,174,280,291-297`
   - **Problema:** todas as consultas são montadas por concatenação de strings com entrada do usuário, sem parametrização. Vale para IDs, filtros de busca, criação/atualização e — o mais grave — o login.
   - **Exemplo:**
     ```python
     # models.py:109-111 — login vulnerável a bypass de autenticação
     cursor.execute(
         "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
     )
     # senha = "' OR '1'='1" autentica como qualquer usuário
     ```
     ```python
     # models.py:291 — busca concatenando o termo direto no LIKE
     query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
     ```
   - **Impacto:** exposição/alteração/exclusão de todo o banco e bypass de login. Falha de segurança grave — CRITICAL por definição.
   - **Sugestão:** usar exclusivamente placeholders parametrizados (`cursor.execute("... WHERE id = ?", (id,))`).

2. **Endpoint que executa SQL arbitrário enviado pelo cliente** — `code-smells-project/app.py:59-78`
   - **Problema:** `/admin/query` recebe uma string SQL no corpo e a executa diretamente, sem autenticação nem restrição.
   - **Exemplo:**
     ```python
     @app.route("/admin/query", methods=["POST"])
     def executar_query():
         query = request.get_json().get("sql", "")
         cursor.execute(query)  # DROP TABLE, leitura total, etc.
     ```
   - **Impacto:** RCE de banco de dados — qualquer um lê/apaga tudo. CRITICAL.
   - **Sugestão:** remover o endpoint por completo; nunca expor SQL cru via HTTP.

3. **Endpoint destrutivo sem autenticação** — `code-smells-project/app.py:47-57`
   - **Problema:** `/admin/reset-db` apaga todas as tabelas sem qualquer verificação de identidade/permissão.
   - **Exemplo:**
     ```python
     @app.route("/admin/reset-db", methods=["POST"])
     def reset_database():
         cursor.execute("DELETE FROM itens_pedido")
         cursor.execute("DELETE FROM pedidos")
         # ...apaga produtos e usuarios
     ```
   - **Impacto:** qualquer requisição anônima destrói a base. CRITICAL.
   - **Sugestão:** exigir autenticação/role admin e proteger rotas administrativas; idealmente não expor em produção.

4. **Senhas armazenadas e trafegadas em texto plano** — `code-smells-project/models.py:83,99,127-128` · `database.py:76-78`
   - **Problema:** senhas são gravadas sem hash e devolvidas nos payloads de listagem/consulta de usuários.
   - **Exemplo:**
     ```python
     # models.py:79-86 — get_todos_usuarios devolve a senha
     result.append({ ..., "senha": row["senha"], ... })
     ```
   - **Impacto:** vazamento direto de credenciais de todos os usuários. CRITICAL.
   - **Sugestão:** hash com `bcrypt`/`argon2` na gravação e nunca serializar o campo `senha`.

5. **Segredo hardcoded e exposto via endpoint** — `code-smells-project/app.py:7,289`
   - **Problema:** `SECRET_KEY` fixa no código e, pior, devolvida em texto no `/health`.
   - **Exemplo:**
     ```python
     app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"  # app.py:7
     ...
     "secret_key": "minha-chave-super-secreta-123"  # health_check → controllers.py:289
     ```
   - **Impacto:** credencial sensível versionada e servida publicamente. CRITICAL.
   - **Sugestão:** carregar de variável de ambiente e nunca retornar em respostas.

### 🟠 HIGH

1. **Conexão de banco global compartilhada entre threads** — `code-smells-project/database.py:4-10`
   - **Problema:** singleton de conexão global com `check_same_thread=False` reutilizado por todas as requisições (estado global mutável).
   - **Exemplo:**
     ```python
     db_connection = None
     def get_db():
         global db_connection
         if db_connection is None:
             db_connection = sqlite3.connect(db_path, check_same_thread=False)
     ```
   - **Impacto:** condições de corrida e corrupção de dados sob concorrência. HIGH (estado global mutável em toda a app).
   - **Sugestão:** conexão por requisição (`flask.g`) ou pool.

2. **`DEBUG=True` em ambiente tratado como produção** — `code-smells-project/app.py:8,88`
   - **Problema:** debugger do Werkzeug ativo; o próprio `/health` reporta `"ambiente": "producao"`.
   - **Impacto:** o console interativo do Werkzeug permite execução de código remoto. HIGH.
   - **Sugestão:** `debug=False` em produção, controlado por env var.

3. **`models.py` mistura acesso a dados com regra de negócio** — `code-smells-project/models.py:235-273`
   - **Problema:** a camada de "model" calcula descontos e métricas de relatório, violando separação de responsabilidades.
   - **Exemplo:**
     ```python
     if faturamento > 10000: desconto = faturamento * 0.1
     elif faturamento > 5000: desconto = faturamento * 0.05
     ```
   - **Impacto:** lógica de negócio acoplada à camada de persistência, difícil de testar. HIGH.
   - **Sugestão:** extrair para uma camada de serviço.

4. **Efeitos colaterais de negócio dentro do controller via `print`** — `code-smells-project/controllers.py:208-210,248-250`
   - **Problema:** "envio" de e-mail/SMS/push e notificações são simulados com `print` no meio do handler HTTP.
   - **Exemplo:**
     ```python
     print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado ...")
     print("ENVIANDO SMS: Seu pedido foi recebido!")
     ```
   - **Impacto:** lógica de negócio (notificação) presa no controller, sem abstração. HIGH.
   - **Sugestão:** serviço de notificação injetável.

### 🟡 MEDIUM

1. **Queries N+1 na listagem de pedidos** — `code-smells-project/models.py:187-199,219-231`
   - **Problema:** para cada pedido roda-se uma query de itens e, para cada item, outra query de produto.
   - **Exemplo:**
     ```python
     for row in rows:                          # 1 por pedido
         cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
         for item in itens:                    # + 1 por item
             cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
     ```
   - **Impacto:** explosão de queries com o crescimento dos dados. MEDIUM (gargalo de performance).
   - **Sugestão:** `JOIN` único ou carregar produtos em lote.

2. **CORS totalmente aberto** — `code-smells-project/app.py:9`
   - **Problema:** `CORS(app)` libera qualquer origem.
   - **Impacto:** amplia superfície de ataque para APIs sem auth. MEDIUM.
   - **Sugestão:** restringir a origens conhecidas.

3. **Validação de produto duplicada** — `code-smells-project/controllers.py:28-54` e `64-90`
   - **Problema:** `criar_produto` e `atualizar_produto` repetem quase as mesmas validações.
   - **Impacto:** duplicação → divergência de regras (ex.: validação de categoria só existe no create). MEDIUM.
   - **Sugestão:** extrair função de validação compartilhada.

### 🟢 LOW

1. **`print` como mecanismo de log** — `code-smells-project/controllers.py:8,11,57,106,161,179` (e outros)
   - **Problema:** logging feito com `print` espalhado pelo código.
   - **Impacto:** sem níveis/estrutura de log. LOW.
   - **Sugestão:** módulo `logging`.

2. **"Magic numbers" nas faixas de desconto** — `code-smells-project/models.py:257-262`
   - **Problema:** limites `10000/5000/1000` e taxas `0.1/0.05/0.02` soltos no código.
   - **Impacto:** legibilidade/manutenção. LOW.
   - **Sugestão:** constantes nomeadas ou tabela de faixas.

3. **Montagem repetida do dicionário de linha** — `code-smells-project/models.py:12-21,31-40,304-313`
   - **Problema:** o mesmo mapeamento `row → dict` de produto é reescrito em 3 lugares.
   - **Impacto:** duplicação. LOW.
   - **Sugestão:** um único helper `produto_to_dict(row)`.

> Observações: os problemas de SQL Injection são reais e comprovados (concatenação de strings). Não há uso de placeholders parametrizados no código de aplicação — apenas o seed em `database.py:70-82` usa `?`, corretamente.

---

## Projeto: ecommerce-api-legacy

LMS/checkout em Node.js/Express com `sqlite3` (banco em memória). Todo o comportamento vive em uma única classe `AppManager` mais um `utils.js` de estado global.

### 🔴 CRITICAL

1. **Credenciais e chaves hardcoded** — `ecommerce-api-legacy/src/utils.js:1-7`
   - **Problema:** senha de banco, chave de gateway de pagamento e usuário SMTP fixos no código.
   - **Exemplo:**
     ```javascript
     const config = {
         dbPass: "senha_super_secreta_prod_123",
         paymentGatewayKey: "pk_live_1234567890abcdef",
         smtpUser: "no-reply@fullcycle.com.br",
     };
     ```
   - **Impacto:** vazamento de credenciais de produção versionadas. CRITICAL.
   - **Sugestão:** variáveis de ambiente / secret manager.

2. **"God Class" `AppManager`** — `ecommerce-api-legacy/src/AppManager.js:4-141`
   - **Problema:** a mesma classe cria/seed do banco, define todas as rotas, faz validação, processa pagamento, matrícula, auditoria e cache — todas as responsabilidades num arquivo.
   - **Exemplo:**
     ```javascript
     class AppManager {
       initDb() { /* CREATE TABLE + INSERT seeds */ }
       setupRoutes(app) { /* checkout + pagamento + relatório + delete */ }
     }
     ```
   - **Impacto:** violação completa de separação de responsabilidades — exatamente o caso CRITICAL da definição.
   - **Sugestão:** separar em camadas (repositório, serviço de pagamento, controllers, rotas).

3. **Hashing de senha inseguro e senha default** — `ecommerce-api-legacy/src/utils.js:17-23` · `AppManager.js:68`
   - **Problema:** `badCrypto` não é hash criptográfico (base64 truncado, reversível) e o checkout cria usuário com senha padrão `"123456"` quando nenhuma é enviada.
   - **Exemplo:**
     ```javascript
     function badCrypto(pwd) {
         let hash = "";
         for (let i = 0; i < 10000; i++) { hash += Buffer.from(pwd).toString('base64').substring(0,2); }
         return hash.substring(0, 10);
     }
     ```
   - **Impacto:** senhas trivialmente quebráveis + contas com senha previsível. CRITICAL.
   - **Sugestão:** `bcrypt`/`argon2`; nunca criar conta com senha default.

4. **Número de cartão de crédito logado em texto** — `ecommerce-api-legacy/src/AppManager.js:45`
   - **Problema:** o cartão completo e a chave do gateway são impressos no console.
   - **Exemplo:**
     ```javascript
     console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
     ```
   - **Impacto:** exposição de dado de cartão (violação PCI-DSS). CRITICAL.
   - **Sugestão:** nunca logar PAN; mascarar e delegar ao gateway.

5. **Exclusão de usuário deixa dados órfãos** — `ecommerce-api-legacy/src/AppManager.js:131-137`
   - **Problema:** o `DELETE` remove só o usuário e mantém matrículas/pagamentos órfãos — o próprio código admite isso na resposta.
   - **Exemplo:**
     ```javascript
     this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
         res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
     });
     ```
   - **Impacto:** integridade referencial quebrada de forma consciente. CRITICAL (falha que compromete a consistência dos dados).
   - **Sugestão:** transação com cascata (ou FKs `ON DELETE CASCADE`) e tratamento de erro.

### 🟠 HIGH

1. **Callback hell com contagem manual e sem tratamento de erro** — `ecommerce-api-legacy/src/AppManager.js:80-129`
   - **Problema:** o relatório financeiro aninha callbacks e controla conclusão com contadores (`coursesPending`/`enrPending`); erros de queries internas são ignorados.
   - **Exemplo:**
     ```javascript
     enrPending--;
     if (enrPending === 0) {
         report.push(courseData);
         coursesPending--;
         if (coursesPending === 0) res.json(report);
     }
     ```
   - **Impacto:** condições de corrida e resposta potencialmente incorreta/incompleta; difícil manutenção. HIGH.
   - **Sugestão:** `async/await` com `Promise.all` ou uma única query agregada.

2. **Estado global mutável** — `ecommerce-api-legacy/src/utils.js:9-10`
   - **Problema:** `globalCache` e `totalRevenue` são mutáveis e compartilhados por todo o processo.
   - **Exemplo:**
     ```javascript
     let globalCache = {};
     let totalRevenue = 0;
     ```
   - **Impacto:** estado global mutável em toda a aplicação. HIGH (item explícito da definição).
   - **Sugestão:** encapsular estado em serviço/cache com escopo controlado.

3. **Sem injeção de dependência / forte acoplamento ao driver** — `ecommerce-api-legacy/src/AppManager.js:6-8`
   - **Problema:** a classe instancia diretamente `new sqlite3.Database(...)`, impossibilitando troca/mocks.
   - **Impacto:** acoplamento forte, testes inviáveis sem banco real. HIGH.
   - **Sugestão:** injetar a dependência de banco/repositório via construtor.

4. **Rotas administrativas sem autenticação** — `ecommerce-api-legacy/src/AppManager.js:80,131`
   - **Problema:** `/api/admin/financial-report` e `DELETE /api/users/:id` não exigem autenticação/autorização.
   - **Impacto:** qualquer um lê o financeiro e apaga usuários. HIGH.
   - **Sugestão:** middleware de autenticação/autorização.

### 🟡 MEDIUM

1. **Erro do banco ignorado no delete** — `ecommerce-api-legacy/src/AppManager.js:133-136`
   - **Problema:** o callback recebe `err` mas nunca o verifica; sempre responde sucesso.
   - **Exemplo:**
     ```javascript
     this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
         res.send("Usuário deletado, ...");   // err nunca checado
     });
     ```
   - **Impacto:** falhas silenciosas retornadas como sucesso. MEDIUM.
   - **Sugestão:** checar `err` e responder status apropriado.

2. **Ausência de validação de entrada** — `ecommerce-api-legacy/src/AppManager.js:28-35`
   - **Problema:** só verifica presença dos campos; não valida formato de e-mail, cartão, tipos, etc.
   - **Impacto:** dados inconsistentes e lógica de pagamento frágil (`cc.startsWith("4")`). MEDIUM.
   - **Sugestão:** validar/normalizar entrada (schema de validação).

3. **Banco somente em memória** — `ecommerce-api-legacy/src/AppManager.js:7`
   - **Problema:** `:memory:` perde todos os dados a cada restart.
   - **Impacto:** inadequado para persistência real. MEDIUM.
   - **Sugestão:** arquivo/servidor de banco configurável por ambiente.

### 🟢 LOW

1. **Nomes de variáveis crípticos** — `ecommerce-api-legacy/src/AppManager.js:29-33`
   - **Problema:** `u`, `e`, `p`, `cid`, `cc` para usuário, e-mail, senha, curso e cartão.
   - **Impacto:** legibilidade. LOW.
   - **Sugestão:** nomes descritivos.

2. **Import não utilizado** — `ecommerce-api-legacy/src/AppManager.js:2`
   - **Problema:** `totalRevenue` é importado e nunca usado.
   - **Impacto:** ruído. LOW.
   - **Sugestão:** remover import.

3. **Mistura de `this` e `self`** — `ecommerce-api-legacy/src/AppManager.js:26,54,57`
   - **Problema:** `const self = this` convive com uso direto de `this` nos mesmos callbacks.
   - **Impacto:** inconsistência/confusão de contexto. LOW.
   - **Sugestão:** usar arrow functions e um único estilo.

> Observações: **não há SQL Injection** neste projeto — todas as queries usam placeholders parametrizados (`?`) com binds do `sqlite3`. O laço de 10.000 iterações em `badCrypto` é inútil (o resultado usa só os 10 primeiros caracteres), mas o problema relevante é a segurança do hash, já classificado como CRITICAL.

---

## Projeto: task-manager-api

Task Manager em Python/Flask com SQLAlchemy. Já possui separação de camadas (`models/`, `routes/`, `services/`, `utils/`), então os problemas são mais de segurança pontual, regra de negócio nas rotas e duplicação.

### 🔴 CRITICAL

1. **Hash de senha exposto nas respostas da API** — `task-manager-api/models/user.py:16-25` · `routes/user_routes.py:85,209`
   - **Problema:** `to_dict()` inclui o campo `password`, e ele é devolvido em criação de usuário e no login.
   - **Exemplo:**
     ```python
     # user.py:20 — to_dict serializa o hash da senha
     'password': self.password,
     ...
     # user_routes.py:207-210 — login devolve user.to_dict() (com password)
     return jsonify({'user': user.to_dict(), 'token': 'fake-jwt-token-' + str(user.id)})
     ```
   - **Impacto:** exposição de dado sensível (hash de senha) a qualquer cliente. CRITICAL.
   - **Sugestão:** remover `password` do `to_dict()` (ou criar um `to_public_dict`).

2. **Credenciais SMTP hardcoded** — `task-manager-api/services/notification_service.py:9-10`
   - **Problema:** usuário e senha do e-mail fixos no código.
   - **Exemplo:**
     ```python
     self.email_user = 'taskmanager@gmail.com'
     self.email_password = 'senha123'
     ```
   - **Impacto:** credencial de e-mail versionada e vazável. CRITICAL.
   - **Sugestão:** carregar de variáveis de ambiente.

3. **Hashing de senha com MD5 sem salt** — `task-manager-api/models/user.py:27-32`
   - **Problema:** senhas são "protegidas" com MD5 puro, algoritmo quebrado e sem salt (vulnerável a rainbow tables).
   - **Exemplo:**
     ```python
     def set_password(self, pwd):
         self.password = hashlib.md5(pwd.encode()).hexdigest()
     ```
   - **Impacto:** proteção de credenciais ineficaz — dados sensíveis efetivamente expostos. CRITICAL.
   - **Sugestão:** `bcrypt`/`argon2` com salt.

### 🟠 HIGH

1. **Autenticação falsa / token fake** — `task-manager-api/routes/user_routes.py:210`
   - **Problema:** o "JWT" é apenas uma string concatenada com o id; nenhum endpoint valida token nem protege recursos.
   - **Exemplo:**
     ```python
     'token': 'fake-jwt-token-' + str(user.id)
     ```
   - **Impacto:** não há autenticação real — qualquer operação (CRUD de tasks/users) é pública. HIGH.
   - **Sugestão:** JWT assinado + middleware de autorização.

2. **`SECRET_KEY` hardcoded** — `task-manager-api/app.py:13`
   - **Problema:** chave secreta fixa no código-fonte.
   - **Exemplo:**
     ```python
     app.config['SECRET_KEY'] = 'super-secret-key-123'
     ```
   - **Impacto:** compromete qualquer assinatura/sessão baseada nessa chave. HIGH.
   - **Sugestão:** variável de ambiente.

3. **Regra de negócio de "overdue" duplicada nas rotas em vez de usar o model** — `task-manager-api/routes/task_routes.py:30-39,71-80,283-287` · `routes/user_routes.py:171-180` · `routes/report_routes.py:34-37,132-135`
   - **Problema:** o mesmo bloco de decisão de atraso é reescrito em ~5 lugares, enquanto `Task.is_overdue()` (models/task.py:50-60) já existe e não é usado.
   - **Exemplo:**
     ```python
     if t.due_date:
         if t.due_date < datetime.utcnow():
             if t.status != 'done' and t.status != 'cancelled':
                 task_data['overdue'] = True
     ```
   - **Impacto:** lógica de negócio presa nos controllers e duplicada → risco de divergência. HIGH.
   - **Sugestão:** usar `task.is_overdue()` e centralizar serialização.

4. **Ausência de paginação (retorno de todos os registros)** — `task-manager-api/routes/task_routes.py:14,271` · `routes/user_routes.py:12`
   - **Problema:** listagens fazem `Task.query.all()` / `User.query.all()` sem limite.
   - **Impacto:** degradação de performance e payloads enormes conforme os dados crescem. HIGH.
   - **Sugestão:** paginação por `limit`/`offset` (ou `paginate`).

### 🟡 MEDIUM

1. **Queries N+1 nas listagens e relatórios** — `task-manager-api/routes/task_routes.py:41-57` · `routes/report_routes.py:53-68`
   - **Problema:** para cada task consultam-se usuário e categoria individualmente; no relatório, para cada usuário roda-se uma query de tasks.
   - **Exemplo:**
     ```python
     for t in tasks:
         user = User.query.get(t.user_id)      # 1 query por task
         cat = Category.query.get(t.category_id)
     ```
   - **Impacto:** número de queries cresce linearmente com os registros. MEDIUM.
   - **Sugestão:** `joinedload`/`selectinload` (ex.: `Task.query.options(joinedload(Task.user), joinedload(Task.category))`).

2. **`except` genérico engolindo erros** — `task-manager-api/routes/task_routes.py:62-63` (e `helpers.py:46-50,87-89`)
   - **Problema:** `except:` sem tipo captura tudo e devolve "Erro interno" mascarando a causa real.
   - **Exemplo:**
     ```python
     except:
         return jsonify({'error': 'Erro interno'}), 500
     ```
   - **Impacto:** dificulta diagnóstico e pode esconder bugs. MEDIUM.
   - **Sugestão:** capturar exceções específicas e logar o erro.

3. **Validação duplicada inline em vez de reutilizar helpers** — `task-manager-api/routes/task_routes.py:92-144,166-213`
   - **Problema:** `create_task`/`update_task` reimplementam validações de título/status/prioridade/data que já existem em `utils/helpers.py:57-108` (`process_task_data`) — que não é usado.
   - **Impacto:** duplicação e risco de regras divergentes. MEDIUM.
   - **Sugestão:** consolidar validação em `process_task_data` e chamá-la nas rotas.

### 🟢 LOW

1. **Imports não utilizados** — `task-manager-api/app.py:7` · `routes/task_routes.py:7` · `utils/helpers.py:3-7`
   - **Problema:** `os, sys, json, datetime/time, math, hashlib` importados sem uso em vários módulos.
   - **Impacto:** ruído/legibilidade. LOW.
   - **Sugestão:** remover imports não usados.

2. **Retornos booleanos verbosos** — `task-manager-api/models/user.py:34-38` · `models/task.py:38-48`
   - **Problema:** `if cond: return True else: return False` onde bastaria `return cond`.
   - **Exemplo:**
     ```python
     def is_admin(self):
         if self.role == 'admin':
             return True
         else:
             return False
     ```
   - **Impacto:** legibilidade. LOW.
   - **Sugestão:** `return self.role == 'admin'`.

3. **"Magic numbers" de prioridade espalhados** — `task-manager-api/routes/task_routes.py:113,182` · `models/task.py:46`
   - **Problema:** faixa `1..5` de prioridade repetida em literais por várias rotas (há `DEFAULT_PRIORITY` em helpers, mas não constantes de faixa reutilizadas).
   - **Impacto:** manutenção/consistência. LOW.
   - **Sugestão:** centralizar em constantes (`MIN_PRIORITY`/`MAX_PRIORITY`).

> Observações: **não há SQL Injection** — o acesso a dados é via SQLAlchemy ORM com filtros parametrizados; mesmo o `Task.title.like(f'%{query}%')` (task_routes.py:250-254) passa o padrão como valor vinculado (bind), não concatenado na query. O projeto possui a estrutura de camadas correta; os principais débitos são segurança de credenciais/senha e regra de negócio vazando para os controllers.
