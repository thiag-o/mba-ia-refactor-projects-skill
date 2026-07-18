# Architecture Audit Report

- **Project:** code-smells-project
- **Stack:** Python 3.12 + Flask 3.1.1
- **Files:** 4 analyzed | ~700 lines of code

## Summary

| Severity | Count |
| -------- | ----: |
| CRITICAL | 5     |
| HIGH     | 4     |
| MEDIUM   | 5     |
| LOW      | 3     |
| **Total**| **17** |

## Findings

### [CRITICAL] SQL Injection por concatenação de strings em todas as queries

- **File:** `models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 148-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 291-297`
- **Description:** Praticamente toda query em `models.py` é montada por concatenação de strings com valores vindos do request. Ex.: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))` (linha 28); `cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")` (linha 110, no login); e a busca dinâmica `query += " AND (nome LIKE '%" + termo + "%' ...)"` (linhas 291-297). Nenhum bind parametrizado é usado.
- **Impact:** Bypass de autenticação no `/login` (ex.: `senha' OR '1'='1`), leitura/alteração/exclusão de todo o banco, exfiltração de senhas. Falha de segurança gravíssima.
- **Recommendation:** Parametrizar 100% das queries com placeholders `?` e tupla de parâmetros (Playbook **P-02**). Ao mover para a camada de repositório, garantir binds em toda operação.

### [CRITICAL] Endpoint que executa SQL arbitrário via HTTP

- **File:** `app.py:59-78`
- **Description:** A rota `POST /admin/query` recebe uma string SQL no corpo (`dados.get("sql")`) e a executa diretamente contra o banco, sem autenticação nem restrição.
- **Impact:** RCE de banco de dados — qualquer cliente anônimo pode ler, alterar, apagar ou dropar qualquer tabela. Combinado com o SQLite local, é comprometimento total dos dados.
- **Recommendation:** Remover o endpoint por completo; nunca expor SQL cru via HTTP (Playbook **P-09** + remoção). Se houver necessidade administrativa legítima, expor operações específicas e autenticadas.

### [CRITICAL] Rota destrutiva sem autenticação (reset do banco)

- **File:** `app.py:47-57`
- **Description:** A rota `POST /admin/reset-db` apaga todas as linhas de `itens_pedido`, `pedidos`, `produtos` e `usuarios` sem qualquer autenticação/autorização.
- **Impact:** Qualquer cliente anônimo pode zerar toda a base de produção com uma única requisição. Destruição de dados.
- **Recommendation:** Exigir autenticação/autorização administrativa (Playbook **P-09**) e, preferencialmente, remover a rota do runtime de produção.

### [CRITICAL] Credenciais/segredos hardcoded e expostos na resposta

- **File:** `app.py:7`, `controllers.py:289`
- **Description:** `SECRET_KEY = "minha-****"` está hardcoded no código (`app.py:7`) e, pior, é devolvida na resposta do `/health` (`controllers.py:289`, junto de `debug`, `db_path` e `ambiente`).
- **Impact:** Segredo versionado no repositório e vazado por um endpoint público — permite forjar sessões/tokens e compromete toda a segurança da aplicação.
- **Recommendation:** Extrair a secret para variável de ambiente (`os.environ["SECRET_KEY"]`) e nunca retorná-la em respostas (Playbook **P-01**). Remover os campos sensíveis do payload de `/health`.

### [CRITICAL] Senhas em texto plano, sem hash, e expostas na serialização

- **File:** `database.py:31, 76-78`, `models.py:79-86, 122-131, 99`
- **Description:** As senhas são gravadas em texto plano (`criar_usuario` insere `senha` cru — `models.py:127-128`), incluindo usuários seed com senhas literais (`database.py:76-78`). Além disso, `get_todos_usuarios` e `get_usuario_por_id` retornam o campo `senha` no payload (`models.py:83, 99`).
- **Impact:** Vazamento trivial de todas as credenciais via `GET /usuarios` ou `GET /usuarios/<id>`; nenhuma proteção em caso de leak do banco. CRITICAL.
- **Recommendation:** Hash forte com salt (`bcrypt`/`argon2`) na criação e verificação; remover o campo `senha`/hash de toda serialização de resposta (Playbook **P-05**).

### [HIGH] God File: `models.py` concentra persistência, regra de negócio e formatação

- **File:** `models.py:1-315`
- **Description:** Um único módulo cobre múltiplos domínios (produtos, usuários, pedidos, relatórios) misturando SQL cru, regra de negócio (cálculo de total do pedido, baixa de estoque, desconto de faturamento em `relatorio_vendas` — linhas 256-262) e mapeamento row→dict. Não há separação model/repository/service.
- **Impact:** Violação de separação de responsabilidades; impossível testar regra de negócio isoladamente; qualquer mudança de schema ou regra reverbera por todo o arquivo. HIGH.
- **Recommendation:** Quebrar em camadas — repositories (acesso a dados) + services (regra de negócio) + models (entidades) (Playbook **P-03**).

### [HIGH] Lógica de negócio e efeitos colaterais no controller

- **File:** `controllers.py:208-210, 247-250`, `models.py:133-169, 235-273`
- **Description:** Os controllers disparam efeitos colaterais de negócio simulados (`print("ENVIANDO EMAIL...")`, SMS, PUSH — `controllers.py:208-210`; notificações de status — `247-250`). Regras como cálculo de total/estoque (`models.py:133-169`) e cálculo de desconto/ticket médio (`models.py:235-273`) estão na camada de persistência.
- **Impact:** Regra acoplada às camadas erradas (HTTP e DB), não reutilizável nem testável; notificações não isoláveis. HIGH.
- **Recommendation:** Mover regra para uma camada de service dedicada e extrair um `NotificationService` (Playbook **P-04**).

### [HIGH] Estado global mutável: conexão de banco singleton compartilhada

- **File:** `database.py:4-11`
- **Description:** A conexão é um singleton de módulo (`db_connection = None` + `global`) aberta com `check_same_thread=False` e reutilizada por todas as requisições e threads.
- **Impact:** Condições de corrida, cursores concorrentes sobre a mesma conexão, risco de corrupção/estado imprevisível sob concorrência. HIGH.
- **Recommendation:** Escopo de conexão por requisição (ou pool), injetado nas camadas que precisam (Playbook **P-06**).

### [HIGH] Forte acoplamento sem injeção de dependência

- **File:** `controllers.py:2-3`, `models.py:1`, `app.py:3-4`
- **Description:** Controllers importam `models` diretamente e `models` chama `get_db()` internamente; nenhuma dependência é injetada. Não há como substituir a camada de dados por um mock.
- **Impact:** Testes unitários inviáveis sem banco real; violação do DIP; troca de implementação exige editar o código-fonte. HIGH.
- **Recommendation:** Injetar repositories/serviços via construtor ou factory (composition root) (Playbook **P-06**).

### [MEDIUM] Queries N+1 na listagem de pedidos

- **File:** `models.py:171-201, 203-233`
- **Description:** `get_pedidos_usuario` e `get_todos_pedidos` iteram sobre pedidos e, para cada um, executam uma query de itens e, dentro dela, uma query por item para buscar o nome do produto (loops aninhados em `models.py:187-199` e `219-231`).
- **Impact:** Número de queries cresce linearmente (e quadraticamente com itens) com o volume de dados; degradação séria de performance. MEDIUM.
- **Recommendation:** Substituir por um único `JOIN` entre `pedidos`, `itens_pedido` e `produtos` (Playbook **P-07**).

### [MEDIUM] Ausência de paginação nas listagens

- **File:** `models.py:4-22, 72-87, 203-233`, `controllers.py:5-12, 128-134, 229-235`
- **Description:** `get_todos_produtos`, `get_todos_usuarios` e `get_todos_pedidos` executam `SELECT *` sem `LIMIT`/`OFFSET`, retornando todos os registros.
- **Impact:** Payloads que crescem sem limite e degradam memória e latência à medida que a base cresce. MEDIUM.
- **Recommendation:** Adicionar paginação (`limit`/`offset` com parâmetros de query) (Playbook **P-11**).

### [MEDIUM] Duplicação de validação entre criar e atualizar produto

- **File:** `controllers.py:24-62, 64-96`
- **Description:** Os blocos de validação de produto (campos obrigatórios, preço/estoque não negativos, categorias válidas) são repetidos quase idênticos em `criar_produto` e `atualizar_produto`.
- **Impact:** Regras podem divergir entre create e update; manutenção duplicada e propensa a inconsistência. MEDIUM.
- **Recommendation:** Extrair a validação para um helper/validador compartilhado (Playbook **P-12**).

### [MEDIUM] Tratamento de erro genérico e falhas silenciosas

- **File:** `controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292`, `app.py:77-78`
- **Description:** Todo handler embrulha a lógica num `try/except Exception` que devolve `str(e)` ao cliente. Não há tipos de exceção específicos nem error handler central; erros de validação e de infraestrutura são achatados no mesmo caminho.
- **Impact:** Mascara a causa real, vaza detalhes internos ao cliente e dificulta distinguir 4xx de 5xx. MEDIUM.
- **Recommendation:** Error handler central com exceções específicas de domínio e mapeamento para status HTTP (Playbook **P-08**).

### [MEDIUM] Configuração insegura de ambiente (DEBUG + CORS aberto)

- **File:** `app.py:8, 9, 88`
- **Description:** `DEBUG=True` está fixo no código e no `app.run(..., debug=True)` (linhas 8 e 88), e o CORS é liberado para qualquer origem com `CORS(app)` (linha 9).
- **Impact:** O debugger do Werkzeug em produção permite execução remota de código; CORS aberto habilita abuso cross-origin. MEDIUM.
- **Recommendation:** Controlar `DEBUG` por variável de ambiente e restringir CORS a origens confiáveis (Playbook **P-01**).

### [LOW] Magic numbers nas regras de desconto

- **File:** `models.py:257-262`
- **Description:** Faixas e taxas de desconto (`> 10000` → `0.1`, `> 5000` → `0.05`, `> 1000` → `0.02`) estão soltas no código de `relatorio_vendas`.
- **Impact:** Regra difícil de entender e manter; mudança de política exige caçar literais. LOW.
- **Recommendation:** Extrair constantes nomeadas / tabela de faixas (Playbook **P-13**).

### [LOW] Logging via `print`

- **File:** `controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248-250`, `app.py:56, 83-86`
- **Description:** `print(...)` é usado como mecanismo de log em toda a aplicação, inclusive para eventos de negócio e erros.
- **Impact:** Sem níveis, formato nem destino configurável; inviável em produção. LOW.
- **Recommendation:** Adotar o módulo `logging` estruturado com níveis (ver Playbook **P-08**).

### [LOW] Import não usado e mapeamento row→dict duplicado

- **File:** `models.py:2`, `models.py:12-21, 31-40, 79-86, 95-102, 304-313`
- **Description:** `import sqlite3` em `models.py:2` nunca é usado. O mesmo mapeamento de linha de produto/usuário para dict é reescrito em várias funções.
- **Impact:** Ruído e duplicação que dificultam manutenção. LOW.
- **Recommendation:** Remover import morto e centralizar a serialização row→dict (Playbook **P-14**).

## Deprecated APIs

- Senhas com armazenamento em texto plano em `models.py:127-128` e `database.py:76-78` → usar `bcrypt`/`argon2` com salt (nunca texto plano nem hash fraco).
