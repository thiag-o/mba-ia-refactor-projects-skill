# 04 — MVC Guidelines (Fase 3)

Regras do padrão MVC alvo, com as **responsabilidades de cada camada** e o que
**não** deve existir nelas. Aplique de forma agnóstica; adapte os nomes de
diretório às convenções da stack detectada.

## Princípio geral

Cada camada tem **uma** responsabilidade (SRP). Dependências fluem de fora para
dentro e são **injetadas**, não instanciadas dentro de quem as usa (DIP). O
**contrato externo** (rotas, métodos, formato de resposta) é preservado.

## Camadas

### Models
- **Responsabilidade:** representação/abstração dos dados e acesso à persistência
  (queries, mapeamento linha→objeto).
- **NÃO deve conter:** regra de negócio complexa, roteamento, serialização de
  campos sensíveis. Um model **nunca** retorna `password`/hash — exponha um
  `to_public_dict()` / DTO sem campos sensíveis.

### Views / Routes
- **Responsabilidade:** definição de endpoints e (de)serialização HTTP — receber
  request, delegar ao controller, devolver a resposta.
- **NÃO deve conter:** regra de negócio, acesso direto ao banco, SQL cru.

### Controllers
- **Responsabilidade:** orquestrar o fluxo — receber input **já validado**, chamar
  services/models, montar a resposta.
- **NÃO deve conter:** SQL cru, lógica de infraestrutura, efeitos colaterais de
  negócio embutidos (envio de e-mail/SMS direto no handler).

### Camadas de apoio
- **`config/`** — configuração via **variáveis de ambiente** (zero hardcoded):
  secret keys, credenciais, flags de debug, CORS, string de conexão.
- **`services/`** — regra de negócio reutilizável e efeitos colaterais
  (notificação, pagamento, cálculo de desconto). É aqui que vive a lógica que
  hoje está vazando para models/controllers.
- **`middlewares/`** — autenticação/autorização e **tratamento de erro
  centralizado** (um único handler que captura exceções e formata a resposta).
- **Entry point / composition root** — um único ponto (o arquivo de bootstrap da
  stack, ex.: `app.py`, `server.js`, `main.go`, `Application.java`) que instancia
  e "cabeia" as dependências (injeção) e registra rotas e middlewares. Sem lógica
  de negócio.

## Estrutura de diretórios alvo

Baseada no exemplo de `OBJETIVOS.md`. O que importa são os **papéis das camadas**,
não os nomes exatos: use a extensão de arquivo (`.<ext>`) e as convenções de
nomenclatura da linguagem detectada na Fase 1 (`snake_case`, `camelCase`,
`PascalCase`, etc.). `.<ext>` abaixo é um placeholder para a extensão real da stack.

```
src/                         (ou a raiz padrão da stack detectada)
├── config/                  # settings via env vars, zero hardcoded
│   └── settings.<ext>
├── models/                  # 1 arquivo por domínio; só dados + persistência
│   ├── <entidade>_model.<ext>
│   └── ...
├── views/ (ou routes/)      # endpoints + (de)serialização HTTP
│   └── routes.<ext>
├── controllers/             # orquestração do fluxo por domínio
│   ├── <dominio>_controller.<ext>
│   └── ...
├── services/                # regra de negócio + efeitos colaterais
│   └── <dominio>_service.<ext>
├── middlewares/             # auth + error handler centralizado
│   └── error_handler.<ext>
└── app.<ext>                # composition root / entry point
```

> Adapte os nomes de diretório às convenções idiomáticas da stack quando existirem
> (ex.: `pkg/`/`internal/` em Go, `app/` em algumas convenções) — desde que os
> papéis (config, models, views/routes, controllers, services, middlewares, entry
> point) fiquem claramente separados.

> **Projeto já parcialmente organizado:** não recrie o que já existe corretamente.
> Se já há `models/` e `routes/`, mantenha-os e adicione o que falta (ex.:
> `services/`, `middlewares/`, `config/`), movendo a regra de negócio das rotas
> para services e removendo campos sensíveis da serialização.

## Princípios SOLID aplicáveis

- **SRP** — cada módulo/camada com uma responsabilidade única.
- **DIP / Injeção de Dependência** — controllers/services recebem suas
  dependências (repositório, conexão, gateway) por construtor/parâmetro; não as
  criam internamente. Permite mocks e troca de implementação.

## Preservação de contrato (obrigatório)

- Os **mesmos paths, métodos HTTP e formato de resposta** dos endpoints originais
  devem ser mantidos após a refatoração.
- Mudanças que quebrariam clientes (renomear rota, alterar shape de resposta)
  **não** são permitidas nesta refatoração — exceto **remover** dados sensíveis
  que jamais deveriam ter sido expostos (ex.: campo `password` na resposta), que
  é uma correção de segurança esperada.
