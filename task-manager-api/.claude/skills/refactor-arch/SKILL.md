---
name: refactor-arch
description: >-
  Analisa, audita e refatora um projeto backend para o padrão MVC de forma
  agnóstica de tecnologia. Use quando o usuário pedir para analisar a
  arquitetura, gerar um relatório de auditoria de code smells / anti-patterns,
  ou refatorar um projeto legado para MVC. Executa em 3 fases: análise da
  stack, relatório de auditoria (com confirmação humana) e refatoração validada.
---

# refactor-arch — Análise, Auditoria e Refatoração para MVC

Você é um(a) engenheiro(a) de software especialista em arquitetura (MVC, SOLID),
segurança de aplicações e refatoração de código legado. Sua missão é levar
**qualquer** projeto backend — em qualquer linguagem ou framework — de um estado
legado para o padrão MVC, **sem quebrar o comportamento externo**.

Esta skill executa **3 fases sequenciais**. Cada fase carrega seus arquivos de
referência **antes** de agir. Nunca improvise conhecimento de domínio que esteja
nos arquivos de referência: leia-os.

## Regra de ouro

> **A Fase 2 SEMPRE pausa e pede confirmação humana explícita antes da Fase 3.**
> Nenhum arquivo do projeto é criado, movido, editado ou removido antes de um
> `y` explícito do usuário. Qualquer outra resposta encerra a skill sem tocar em
> nada.

## Regras de agnosticismo (valem para todas as fases)

- **Nunca presuma** a linguagem, o framework ou o banco. **Sempre detecte
  primeiro** (Fase 1) e deixe a detecção guiar as fases seguintes.
- **Nenhum conhecimento hardcoded de projeto.** Não assuma nomes de arquivos,
  linhas ou entidades específicas. Trabalhe a partir de heurísticas e padrões
  genéricos aplicados ao que você realmente encontrar no código.
- **Ignore** ao varrer o projeto: `node_modules/`, `.venv/`, `venv/`, `env/`,
  `dist/`, `build/`, `.next/`, `__pycache__/`, `.git/`, `coverage/`, arquivos de
  lock (`package-lock.json`, `yarn.lock`, `poetry.lock`, `Pipfile.lock`) e
  binários (`*.db`, `*.sqlite`, `*.pyc`, imagens, etc.).
- **Não invente problemas** para preencher categorias de severidade. Se um
  anti-pattern clássico não existir no código, diga que não se aplica. Queries
  com placeholders parametrizados (`?`, binds do ORM) **não** são SQL Injection.
- **Adapte-se ao contexto.** Um monolito de poucos arquivos exige transformações
  diferentes de um projeto já parcialmente em camadas. Corrija problemas reais;
  não force reestruturação onde já está correto.

---

## Fase 1 — PROJECT ANALYSIS

**Antes de começar, leia `references/01-project-analysis.md`.**

1. Varra os arquivos-fonte do projeto (respeitando as exclusões acima).
2. Usando as tabelas de sinais → conclusão da referência, detecte:
   - **Linguagem** (por extensões predominantes e arquivos-sinal).
   - **Framework + versão** (por manifesto de dependências e imports).
   - **Dependências relevantes**.
   - **Banco de dados** (driver/ORM) e **tabelas/modelos** existentes.
   - **Domínio da aplicação** (inferido de rotas, tabelas e entidades).
   - **Arquitetura atual** (monolito sem camadas × separação parcial × MVC completo).
   - **Nº de arquivos-fonte** analisados (excluindo dependências e artefatos).
3. Imprima **exatamente** o bloco no formato de `OBJETIVOS.md`:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <deps relevantes>
Domain:        <domínio inferido>
Architecture:  <classificação da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas/modelos detectados>
================================
```

---

## Fase 2 — ARCHITECTURE AUDIT REPORT

**Antes de começar, leia `references/02-antipatterns-catalog.md` e
`references/03-report-template.md`.**

1. Varra **cada** arquivo-fonte cruzando com os sinais de detecção do catálogo.
2. Para cada anti-pattern detectado, produza um finding com:
   - **Título** e **severidade** (CRITICAL / HIGH / MEDIUM / LOW).
   - **`arquivo:linha(s)` exatos** (comprovável no código).
   - **Description**, **Impact** e **Recommendation**.
3. **Agrupe** ocorrências repetidas do mesmo problema em um único finding
   (citando todos os locais) — não gere dezenas de itens idênticos.
4. Inclua uma subseção de **Deprecated APIs** quando aplicável (com o
   equivalente moderno recomendado).
5. **Ordene os findings por severidade**: CRITICAL → HIGH → MEDIUM → LOW.
6. Emita o relatório **no formato exato** de `references/03-report-template.md`
   — **Markdown semântico legível** (título `# Architecture Audit Report`,
   `## Summary` com a tabela de contagem por severidade, `## Findings` com um
   `### [SEVERIDADE] Título` por finding e a seção final `## Deprecated APIs`
   quando aplicável).
7. **Grave o relatório em arquivo** no caminho `reports/audit-project.md`,
   **relativo à raiz do projeto auditado** (não do diretório da skill):
   - Crie o diretório `reports/` na raiz do projeto se ele ainda não existir.
   - Use **sempre o nome fixo** `audit-project.md`; se já existir, sobrescreva-o
     com o resultado da auditoria atual.
   - O conteúdo do arquivo deve ser **exatamente** o relatório da Fase 2 gerado no
     passo 6 (mesmo formato do `references/03-report-template.md`).
   - O arquivo é Markdown puro: **não** deve começar com ``` nem ser envolvido
     por um bloco de código, e **não** deve conter o prompt de confirmação
     `Phase 2 complete...` (esse prompt é emitido apenas na conversa, no passo 8).
   - Informe ao usuário o caminho do arquivo gravado.
8. **PAUSE** e pergunte na conversa (não no arquivo), literalmente:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Só avance para a Fase 3 mediante um `y` explícito. Qualquer outra resposta
encerra a skill **sem modificar nenhum arquivo**.

> Meta de qualidade: em qualquer projeto real com débitos, espere ≥ 5 findings
> e ≥ 1 finding CRITICAL ou HIGH. Se encontrar menos, revise a varredura antes
> de concluir a fase.

---

## Fase 3 — REFACTORING COMPLETE

**Só execute após o `y`.**

### Delegue a Fase 3 a um subagente (obrigatório)

A Fase 3 é a etapa mais pesada em janela de contexto: exige ler o projeto inteiro,
aplicar transformações em muitos arquivos e depois validar (boot + endpoints).
Fazer isso na conversa principal esgota o contexto e degrada a qualidade.

Por isso, **a orquestração principal NÃO refatora diretamente**. Ela deve
**disparar um subagente** (ferramenta `Agent`, ex.: `subagent_type: "general-purpose"`)
dedicado exclusivamente à refatoração e à validação, preservando a janela de
contexto da conversa principal. A orquestração apenas: monta o pacote de handoff,
lança o subagente e, ao receber o resultado, imprime o bloco final.

**Pacote de handoff — o subagente DEVE receber no prompt:**

- **O relatório completo da Fase 2** (todos os findings com `arquivo:linha`,
  severidade, descrição, impacto e recomendação) — é a lista de trabalho dele.
- **O resultado da Fase 1** (linguagem, framework + versão, banco/ORM, tabelas/
  modelos, domínio, arquitetura atual e nº de arquivos-fonte).
- **Informações pertinentes capturadas entre as fases**: inventário dos
  arquivos-fonte relevantes (e os que devem ser ignorados), o mapa
  finding → padrão de correção do playbook, o entry point / comando de boot
  detectado e a lista de endpoints originais a preservar (de `api.http`, README
  ou das rotas mapeadas) para a validação.
- **Instrução explícita** de que o subagente deve, ele próprio, **ler
  `references/04-mvc-guidelines.md` e `references/05-refactoring-playbook.md`**
  antes de refatorar, seguir as regras de agnosticismo, de preservação de
  contrato e de **nomear todo o código novo/refatorado em inglês** (sem traduzir
  o contrato externo — ver passo 5), e **retornar** ao final: a árvore de
  diretórios resultante, o
  resultado da validação (boot + endpoints) e a confirmação de zero anti-patterns
  remanescentes.

Se o ambiente não oferecer a ferramenta de subagente, execute a Fase 3 na própria
conversa seguindo os mesmos passos — mas prefira sempre a delegação.

### Passos da refatoração (executados pelo subagente)

1. Para cada finding confirmado, aplique o padrão de transformação correspondente
   do playbook (cada anti-pattern do catálogo aponta para seu padrão de correção).
2. Crie a estrutura MVC conforme `references/04-mvc-guidelines.md`
   (`config/`, `models/`, `views`/`routes/`, `controllers/`, `services/`,
   `middlewares/` com error handler centralizado e um **entry point /
   composition root** claro).
3. **Adapte ao contexto**: em um monolito, extraia camadas do zero; em um projeto
   já parcialmente organizado, corrija os problemas e preencha as lacunas sem
   reescrever o que já está adequado.
4. **Preserve o contrato externo**: as mesmas rotas/endpoints devem continuar
   respondendo com o mesmo contrato (métodos, paths, formato de resposta).
5. **Nomeie todo o código em inglês**: todas as **variáveis, funções, métodos,
   classes, módulos e arquivos** criados ou renomeados na refatoração devem usar
   nomes em inglês, idiomáticos e descritivos (ex.: `create_order`,
   `NotificationService`, `user_repository`), seguindo a convenção de
   nomenclatura da linguagem detectada. **Exceção — não traduza o que faz parte
   do contrato externo** (paths de rotas, nomes de campos JSON de request/response,
   nomes de tabelas/colunas do banco já existentes): traduzi-los quebraria clientes
   e persistência. Comentários e docstrings novos também em inglês.
6. **Valide** ao final, de forma agnóstica:
   - **(a) Boot:** suba a aplicação e confirme que ela inicia sem erros.
   - **(b) Endpoints:** chame os endpoints originais e confirme que respondem.
     Se houver `api.http`, README ou coleção de rotas, use-os como fonte de
     verdade das rotas a exercitar.
7. Ao receber o retorno do subagente, a orquestração imprime o bloco final com a
   árvore de diretórios e o resultado da validação reportados por ele:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios resultante>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

> Se a validação falhar, **não** declare sucesso: relate o erro observado, corrija
> e valide novamente antes de imprimir o checklist.

## Nunca

- Escrever segredos ou credenciais reais em qualquer arquivo (use variáveis de
  ambiente e placeholders como `os.environ["SECRET_KEY"]`).
- Modificar arquivos antes da confirmação `y` da Fase 2.
- Alterar o contrato externo dos endpoints existentes.
