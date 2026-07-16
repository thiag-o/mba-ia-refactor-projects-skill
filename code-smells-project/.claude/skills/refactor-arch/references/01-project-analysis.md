# 01 — Project Analysis (Fase 1)

Heurísticas **acionáveis e agnósticas** para detectar linguagem, framework, banco,
domínio e arquitetura de **qualquer** projeto backend. Detecte sempre a partir do
que existe no repositório — nunca presuma a stack.

> **Exclua** da varredura: `node_modules/`, `.venv/`, `venv/`, `env/`, `dist/`,
> `build/`, `.next/`, `__pycache__/`, `.git/`, `coverage/`, arquivos de lock e
> binários (`*.db`, `*.sqlite`, `*.pyc`, imagens).

## 1. Linguagem

Decida pela **extensão predominante** dos arquivos-fonte e por arquivos-sinal.

| Sinais | Conclusão |
|---|---|
| Muitos `.py`; `requirements.txt` / `pyproject.toml` / `Pipfile` | **Python** |
| Muitos `.js` / `.mjs` / `.cjs` / `.ts`; `package.json` | **JavaScript / TypeScript (Node.js)** |
| `.rb`; `Gemfile` | **Ruby** |
| `.go`; `go.mod` | **Go** |
| `.java` / `.kt`; `pom.xml` / `build.gradle` | **Java / Kotlin** |
| `.php`; `composer.json` | **PHP** |

## 2. Manifesto de dependências e versão

O manifesto é a fonte de verdade das dependências e versões.

| Arquivo | Ecossistema | Como ler |
|---|---|---|
| `requirements.txt` | Python (pip) | uma dep por linha; `pacote==versão` |
| `pyproject.toml` / `Pipfile` | Python (poetry/pipenv) | seção `[dependencies]` / `[packages]` |
| `package.json` | Node | chaves `dependencies` / `devDependencies`; versão em `^x.y.z` |
| `Gemfile` / `go.mod` / `pom.xml` | Ruby / Go / Java | listagem de deps + versão |

> Se a versão exata não estiver fixada, reporte a versão declarada (ex.: `^3.1`)
> ou, se um lockfile/`*.dist-info` estiver disponível, a versão resolvida.

## 3. Framework

Mapeie imports **e** dependências do manifesto para o framework.

| Sinais (import / dependência) | Framework |
|---|---|
| `from flask import` / `Flask` em `requirements.txt` | **Flask** (Python) |
| `django` / `manage.py` / `settings.py` | **Django** (Python) |
| `fastapi` / `from fastapi import` | **FastAPI** (Python) |
| `express` em `package.json` / `require('express')` / `import express` | **Express** (Node) |
| `@nestjs/core` | **NestJS** (Node) |
| `koa` | **Koa** (Node) |
| `fastify` | **Fastify** (Node) |

Para a **versão**: leia o manifesto (ex.: `Flask==3.1.1`, `"express": "^4.18"`).
Se não fixada, reporte a versão do manifesto ou a resolvida no lockfile.

## 4. Banco de dados

Detecte o **driver/ORM** e depois **liste tabelas/modelos**.

| Sinais | Banco / camada de dados |
|---|---|
| `import sqlite3` / `sqlite3.connect(...)` / arquivo `*.db` | SQLite via driver puro |
| `SQLAlchemy` / `db.Model` / `db = SQLAlchemy()` | SQLAlchemy ORM (Python) |
| `psycopg2` / `pg` | PostgreSQL |
| `mysql` / `mysql2` / `pymysql` | MySQL |
| `require('sqlite3')` / `new sqlite3.Database(...)` | SQLite (Node) |
| `sequelize` / `prisma` / `typeorm` / `mongoose` | ORM/ODM Node |

**Como listar tabelas/modelos** (use o que aplicar):

- Varra `CREATE TABLE <nome>` em strings SQL / migrations / seeds.
- Classes de modelo do ORM: `class X(db.Model)` (SQLAlchemy), `__tablename__`,
  `sequelize.define('X', ...)`, `@Entity` etc.
- Chamadas de query que citem nomes de tabela (`FROM <tabela>`, `INTO <tabela>`).

## 5. Domínio da aplicação

Infira o domínio a partir de **nomes de rotas, tabelas e entidades**.

| Entidades / rotas observadas | Domínio provável |
|---|---|
| `produtos`, `pedidos`, `usuarios`, `itens_pedido`, carrinho, checkout | **E-commerce API** |
| `courses`, `enrollments`, `students`, `lessons`, matrícula | **LMS / educação** |
| `tasks`, `categories`, `projects`, `due_date`, `priority` | **Task Manager** |
| `posts`, `comments`, `followers` | **Rede social / blog** |
| `payments`, `invoices`, `transactions` | **Financeiro / pagamentos** |

Descreva o domínio com as entidades reais encontradas, ex.:
`E-commerce API (produtos, pedidos, usuários)`.

## 6. Arquitetura atual

Classifique o nível de organização em uma das faixas:

| Sinais | Classificação |
|---|---|
| Toda a lógica (rotas + queries + regra + serialização) em 1–4 arquivos, sem pastas de camada | **Monolítica — sem separação de camadas** |
| Existem algumas pastas (`models/`, `routes/`, `services/`, `utils/`) mas com vazamentos (regra nas rotas, SQL nos controllers) | **Separação parcial de camadas** |
| Camadas claras: `models/`, `controllers/`, `views`/`routes/`, `services/`, `config/`, error handler central | **MVC completo** |
| Uma única "God Class" concentrando DB + rotas + regra | **Monolítica — God Class** |

**Contagem de arquivos-fonte:** conte apenas arquivos de código da aplicação
(nas extensões da linguagem detectada), **excluindo** dependências, artefatos,
locks, binários e a própria pasta `.claude/`.

## Saída da fase

Preencha o bloco `PHASE 1: PROJECT ANALYSIS` (ver `SKILL.md`) com uma linha por
dimensão: `Language / Framework / Dependencies / Domain / Architecture /
Source files / DB tables`.
