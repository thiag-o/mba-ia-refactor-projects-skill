# Architecture Audit Report

- **Project:** task-manager-api
- **Stack:** Python 3 + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1, SQLite)
- **Files:** 15 analyzed | ~750 lines of code

## Summary

| Severity | Count |
| -------- | ----: |
| CRITICAL | 2   |
| HIGH     | 3   |
| MEDIUM   | 5   |
| LOW      | 3   |
| **Total**| **13** |

## Findings

### [CRITICAL] Segredos e credenciais hardcoded no código-fonte

- **File:** `app.py:13`, `services/notification_service.py:9-10`
- **Description:** A `SECRET_KEY` da aplicação está embutida como literal (`SECRET_KEY = 'super-secret-****'`) e o serviço de notificação carrega usuário e senha de SMTP diretamente no código (`email_user = 'taskmanager@gmail.com'`, `email_password = '****'`). Nenhuma dessas configurações vem de variável de ambiente.
- **Impact:** Credenciais sensíveis ficam versionadas no repositório e vazam para qualquer pessoa com acesso ao código/histórico Git. A `SECRET_KEY` fixa permite forjar sessões/assinaturas; a senha de e-mail expõe a conta de envio real.
- **Recommendation:** Extrair toda configuração sensível para variáveis de ambiente (`os.environ[...]` / `python-dotenv`), com um módulo `config/` por ambiente. Playbook **P-01 (extrair configuração para env vars)**.

### [CRITICAL] Senha com hash fraco (MD5 sem salt) e exposta na serialização

- **File:** `models/user.py:11, 20-25, 29, 32`, `routes/user_routes.py:85, 209`
- **Description:** As senhas são hasheadas com `hashlib.md5` sem salt (`set_password`/`check_password`), algoritmo criptograficamente quebrado. Pior: o `to_dict()` do `User` inclui o campo `password` (o hash), que é devolvido nas respostas de criação de usuário (`create_user`) e de login (`login`).
- **Impact:** Hashes MD5 sem salt são quebráveis por rainbow tables em segundos, e o hash é entregue a qualquer cliente HTTP — comprometendo credenciais de todos os usuários.
- **Recommendation:** Trocar MD5 por `bcrypt`/`argon2` (com salt) e **remover** o campo `password` de qualquer payload de resposta (serializer sem o campo sensível). Playbook **P-05 (hash seguro + remover campo sensível da serialização)**.

### [HIGH] Regra de negócio e serialização dentro dos controllers

- **File:** `routes/task_routes.py:16-59, 71-80, 273-299`, `routes/user_routes.py:162-181`, `routes/report_routes.py:13-101, 104-155, 157-165`
- **Description:** Os handlers HTTP concentram lógica de domínio e montagem manual de dicionários: cálculo de "overdue" copiado em vários endpoints (a model já tem `is_overdue()`, mas não é usada), agregação de estatísticas/relatórios (`task_stats`, `summary_report`, `user_report`) e serialização `row → dict` feita à mão nas rotas em vez de reutilizar `to_dict()`. Existe `services/notification_service.py`, mas nunca é chamado.
- **Impact:** Regra acoplada à camada HTTP, não reutilizável nem testável isoladamente; divergência entre cópias da mesma lógica; controllers longos e frágeis.
- **Recommendation:** Mover cálculos e agregações para uma camada de **services** (ex.: `TaskService`, `ReportService`) e a serialização para schemas/`to_dict`. Playbook **P-04 (mover regra para service)**.

### [HIGH] Rotas sensíveis sem autenticação/autorização e token fake

- **File:** `routes/user_routes.py:134-151, 185-211`, `routes/task_routes.py:225-238`, `routes/report_routes.py:211-223`
- **Description:** Endpoints destrutivos e administrativos (`DELETE /users/<id>`, `DELETE /tasks/<id>`, `DELETE /categories/<id>`, atualização de role de usuário) não têm nenhum middleware de autenticação. O `login` devolve um "token" falso (`'fake-jwt-token-' + str(user.id)`) que nenhuma rota valida.
- **Impact:** Qualquer cliente anônimo pode deletar usuários, tasks e categorias ou alterar papéis. O token fake dá falsa sensação de segurança sem proteger nada.
- **Recommendation:** Introduzir autenticação real (JWT/sessão) e um middleware de autorização aplicado às rotas sensíveis. Playbook **P-09 (auth middleware em rotas sensíveis)**.

### [HIGH] Acoplamento direto à persistência sem camada de repositório/serviço

- **File:** `routes/task_routes.py:11-299`, `routes/user_routes.py:10-211`, `routes/report_routes.py:12-223`
- **Description:** Todos os controllers acessam diretamente o ORM/`db.session` (`Task.query...`, `db.session.add/commit/rollback`) sem qualquer camada de repositório ou serviço intermediária. As pastas `config/`, `middlewares/` e `schemas/` existem, mas estão **vazias** — a estrutura MVC foi apenas esboçada.
- **Impact:** Impossível trocar/mockar a fonte de dados nos testes; transações e regras espalhadas pelos handlers; violação do princípio de inversão de dependência.
- **Recommendation:** Criar camada de repositórios/serviços entre controllers e models e preencher a estrutura de camadas prevista. Playbook **P-06 (injeção de dependência)** + **P-03 (separar em camadas)**.

### [MEDIUM] Queries N+1 em listagens e relatórios

- **File:** `routes/task_routes.py:41-57`, `routes/report_routes.py:53-68, 157-164`
- **Description:** `get_tasks` executa `User.query.get()` e `Category.query.get()` dentro do loop de tasks (2 queries por item). `summary_report` faz uma query de tasks por usuário dentro do loop de usuários. `get_categories` roda um `count()` por categoria.
- **Impact:** O número de queries cresce linearmente com o volume de dados, degradando a performance à medida que a base cresce.
- **Recommendation:** Usar JOIN / eager loading (`joinedload`) e agregações no banco. Playbook **P-07 (JOIN / eager loading)**.

### [MEDIUM] Ausência de paginação nas listagens

- **File:** `routes/task_routes.py:14, 266`, `routes/user_routes.py:12`, `routes/report_routes.py:159`
- **Description:** Endpoints de listagem usam `Task.query.all()` / `User.query.all()` / `Category.query.all()` sem `limit`/`offset`, retornando todos os registros.
- **Impact:** Payloads que crescem sem limite e consumo de memória/latência proporcional ao tamanho da tabela.
- **Recommendation:** Adicionar paginação (`page`/`per_page` com `limit`/`offset`). Playbook **P-11 (adicionar paginação)**.

### [MEDIUM] Duplicação de validação e helpers ignorados

- **File:** `routes/task_routes.py:96-114, 166-184`, `routes/user_routes.py:61, 106`
- **Description:** As validações de título/status/prioridade estão duplicadas entre `create_task` e `update_task`; a regex de e-mail é repetida em `create_user` e `update_user`. Já existem helpers prontos e não utilizados (`utils/helpers.py:process_task_data`, `validate_email`, e as constantes `VALID_STATUSES`, `MAX_TITLE_LENGTH`, etc.).
- **Impact:** Regras divergem entre cópias com o tempo; código de validação repetido e propenso a inconsistências.
- **Recommendation:** Centralizar validação em schemas (marshmallow, já disponível) ou helpers compartilhados. Playbook **P-12 (extrair validação para helper compartilhado)**.

### [MEDIUM] Tratamento de erro genérico e sem handler central

- **File:** `routes/task_routes.py:62-63, 236-238`, `routes/user_routes.py:130-132, 149-151`, `routes/report_routes.py:186-188, 207-209, 221-223`
- **Description:** Vários blocos usam `except:` sem tipo, devolvendo mensagens genéricas ("Erro interno", "Erro ao deletar") e engolindo a exceção real. Não há error handler central registrado no app.
- **Impact:** A causa raiz de falhas é mascarada; bugs ficam escondidos e falhas podem ser silenciadas ou reportadas de forma inútil ao cliente.
- **Recommendation:** Capturar exceções específicas e registrar um error handler central (`@app.errorhandler`). Playbook **P-08 (error handler central + exceções específicas)**.

### [MEDIUM] Configuração insegura de ambiente (debug e CORS aberto)

- **File:** `app.py:15, 34`
- **Description:** A aplicação sobe com `debug=True` (expõe o debugger interativo do Werkzeug) e habilita `CORS(app)` liberado para qualquer origem, sem restrição de domínios.
- **Impact:** `debug=True` permite execução de código via debugger; CORS totalmente aberto amplia a superfície para abuso cross-origin.
- **Recommendation:** Controlar `debug` por ambiente e restringir CORS a origens confiáveis. Playbook **P-01 (config por ambiente)** + restrição de CORS.

### [LOW] Magic numbers e faixas repetidas no código

- **File:** `models/task.py:39, 46`, `routes/task_routes.py:96-100, 110, 113`, `models/user.py`
- **Description:** Faixa de prioridade `1..5`, limites de tamanho de título (3/200) e listas de status válidos aparecem inline em vários pontos, apesar de já existirem constantes nomeadas em `utils/helpers.py` (não usadas).
- **Impact:** Alterar uma regra exige caçar valores espalhados; risco de inconsistência.
- **Recommendation:** Extrair para constantes nomeadas reutilizadas. Playbook **P-13 (extrair constantes nomeadas)**.

### [LOW] Logging via `print` em vez de logging estruturado

- **File:** `routes/task_routes.py:149, 153, 219, 234`, `routes/user_routes.py:83, 89, 147`, `services/notification_service.py:21, 24`
- **Description:** Mensagens operacionais e de erro são emitidas com `print(...)` espalhados pelos handlers e serviços.
- **Impact:** Sem níveis, formato ou destino configurável; inadequado para produção e difícil de filtrar/monitorar.
- **Recommendation:** Usar o módulo `logging` com níveis e formato configuráveis. Ver Playbook **P-08**.

### [LOW] Imports não usados, nomes crípticos e código verboso

- **File:** `app.py:7`, `routes/task_routes.py:7`, `routes/user_routes.py:6`, `models/task.py:38-60`, `models/user.py:34-38`
- **Description:** Imports declarados e nunca usados (`import os, sys, json, datetime` em `app.py`; `import json, os, sys, time` em `task_routes.py`; `hashlib, json` em `user_routes.py`), variáveis de uma letra (`u`, `t`, `c`, `p`) e padrões verbosos `if cond: return True else: return False` (`is_overdue`, `is_admin`, `validate_status`).
- **Impact:** Ruído que reduz legibilidade e induz a erro na manutenção.
- **Recommendation:** Remover imports mortos, renomear variáveis e simplificar retornos booleanos. Playbook **P-14 (limpeza de legibilidade)**.

## Deprecated APIs

- `datetime.utcnow()` em `models/task.py:15-16, 52`, `models/user.py:14`, `routes/task_routes.py:31, 285`, `routes/report_routes.py:35, 45, 71`, `utils/helpers.py:38` → usar `datetime.now(timezone.utc)`
- `hashlib.md5` para senhas em `models/user.py:29, 32` → usar `bcrypt` / `argon2` (com salt)
- `Model.query.get(id)` (padrão legado do SQLAlchemy 2.0) em `routes/task_routes.py:67, 117, 158, 227`, `routes/user_routes.py:29, 94, 136, 155`, `routes/report_routes.py:105, 192, 213` → usar `db.session.get(Model, id)`
