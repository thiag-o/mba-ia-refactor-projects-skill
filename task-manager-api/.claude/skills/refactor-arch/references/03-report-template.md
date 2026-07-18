# 03 — Report Template (Fase 2)

Formato **padronizado** do relatório de auditoria gravado em
`reports/audit-project.md`. O arquivo é **Markdown semântico legível**: ele
**NÃO** começa com ``` nem é envolvido por um bloco de código, e **não** usa
separadores de `=`. Use títulos (`#`, `##`, `###`), tabelas e listas reais para
que o arquivo renderize corretamente em qualquer visualizador de Markdown.

Preencha **exatamente** a estrutura abaixo. Os findings devem estar **ordenados
por severidade**: CRITICAL → HIGH → MEDIUM → LOW.

> Importante: o texto entre as duas linhas de `---` a seguir é **o conteúdo
> literal** que vai para o arquivo `.md` (começando na linha `# Architecture
> Audit Report`). O prompt de confirmação `Phase 2 complete...` **não** faz
> parte do arquivo — ele é emitido apenas na conversa, depois de gravar o
> relatório.

---

# Architecture Audit Report

- **Project:** <nome do projeto>
- **Stack:** <linguagem> + <framework>
- **Files:** <N> analyzed | ~<M> lines of code

## Summary

| Severity | Count |
| -------- | ----: |
| CRITICAL | <n>   |
| HIGH     | <n>   |
| MEDIUM   | <n>   |
| LOW      | <n>   |
| **Total**| **<N>** |

## Findings

### [CRITICAL] <Título do finding>

- **File:** `<arquivo:linha(s)>`
- **Description:** <o que é e por que ocorre, com o trecho quando possível>
- **Impact:** <consequência concreta — segurança, corrupção, manutenção>
- **Recommendation:** <correção objetiva; cite o padrão do playbook>

### [CRITICAL] <Título do próximo finding>

- **File:** `<arquivo:linha(s)>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

### [HIGH] <Título>

- **File:** `<arquivo:linha(s)>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

### [MEDIUM] <Título>

- **File:** `<arquivo:linha(s)>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

### [LOW] <Título>

- **File:** `<arquivo:linha(s)>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

## Deprecated APIs

- `<api obsoleta>` em `<arquivo:linha>` → usar `<equivalente moderno>`

<!-- Omita a seção "Deprecated APIs" inteira se nenhuma API deprecated for detectada. -->

---

## Regras de preenchimento

- O arquivo gravado começa em `# Architecture Audit Report` — **sem** ``` de
  abertura, **sem** front matter e **sem** linhas de `====`.
- **`File:`** sempre com `arquivo:linha` ou `arquivo:linha-inicial-linha-final`.
  Quando o mesmo problema ocorre em vários pontos, liste todos:
  `models.py:28, 48-49, 110` (finding único agrupado).
- **Ordenação:** todos os CRITICAL primeiro, depois HIGH, MEDIUM e LOW. Dentro de
  um mesmo nível, do maior para o menor impacto.
- **`Summary`** (tabela) deve bater com a contagem real de findings por nível, e
  a linha **Total** = soma de todos os findings listados.
- **`Deprecated APIs`**: inclua a seção apenas se aplicável; caso contrário,
  omita-a por completo (não escreva "nenhuma").
- **Nunca** escreva segredos reais no relatório — mascare valores sensíveis
  (ex.: `SECRET_KEY = "minha-****"`).
- Depois de gravar o arquivo, emita na conversa o prompt de confirmação
  **literal** e obrigatório; a skill só prossegue para a Fase 3 com um `y`
  explícito:

  ```
  Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
  ```
