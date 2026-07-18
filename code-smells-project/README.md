# code-smells-project

API de E-commerce em Python/Flask, refatorada para uma arquitetura MVC em camadas
(config / models / services / controllers / views / middlewares / utils) com
injeção de dependência a partir de um composition root (`app.py`).

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado
automaticamente no primeiro boot, já com produtos e usuários de exemplo. As senhas
dos usuários seed são armazenadas com hash bcrypt; as credenciais de exemplo
continuam válidas (ex.: `admin@loja.com` / `admin123`).

## Configuração (variáveis de ambiente)

Todas possuem defaults de desenvolvimento; defina valores reais em produção.

| Variável        | Default                     | Descrição                                   |
|-----------------|-----------------------------|---------------------------------------------|
| `SECRET_KEY`    | `dev-only-change-me`        | Chave secreta do Flask.                     |
| `DEBUG`         | `false`                     | Ativa o modo debug quando `true`.           |
| `DB_PATH`       | `loja.db`                   | Caminho do arquivo SQLite.                  |
| `ADMIN_TOKEN`   | `local-dev-admin-token`     | Token exigido nos endpoints `/admin/*`.     |
| `ENVIRONMENT`   | `producao`                  | Nome do ambiente reportado no `/health`.    |
| `CORS_ORIGINS`  | `http://localhost:3000,...` | Lista (CSV) de origens permitidas no CORS.  |

## Endpoints administrativos

- `POST /admin/reset-db` exige autenticação admin:
  `Authorization: Bearer <ADMIN_TOKEN>` (ou header `X-Admin-Token`).
- `POST /admin/query` (execução de SQL arbitrário) foi **removido** por segurança.
