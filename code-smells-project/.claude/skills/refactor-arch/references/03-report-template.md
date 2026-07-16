# 03 — Report Template (Fase 2)

Formato **padronizado** do relatório de auditoria. Preencha **exatamente** esta
estrutura (espelha os blocos de exemplo de `OBJETIVOS.md`). Os findings devem
estar **ordenados por severidade**: CRITICAL → HIGH → MEDIUM → LOW.

---

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<M> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Título do finding>
File: <arquivo:linha(s)>
Description: <o que é e por que ocorre, com o trecho quando possível>
Impact: <consequência concreta — segurança, corrupção, manutenção>
Recommendation: <correção objetiva; cite o padrão do playbook>

### [CRITICAL] <Título do próximo finding>
File: <arquivo:linha(s)>
Description: ...
Impact: ...
Recommendation: ...

### [HIGH] <Título>
File: <arquivo:linha(s)>
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] <Título>
File: <arquivo:linha(s)>
Description: ...
Impact: ...
Recommendation: ...

### [LOW] <Título>
File: <arquivo:linha(s)>
Description: ...
Impact: ...
Recommendation: ...

## Deprecated APIs
- <api obsoleta> em <arquivo:linha> → usar <equivalente moderno>
  (Omita esta seção inteira se nenhuma API deprecated for detectada.)

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Regras de preenchimento

- **`File:`** sempre com `arquivo:linha` ou `arquivo:linha-inicial-linha-final`.
  Quando o mesmo problema ocorre em vários pontos, liste todos:
  `models.py:28, 48-49, 110` (finding único agrupado).
- **Ordenação:** todos os CRITICAL primeiro, depois HIGH, MEDIUM e LOW. Dentro de
  um mesmo nível, do maior para o menor impacto.
- **`Summary`** deve bater com a contagem real de findings por nível.
- **`Total:`** = soma de todos os findings listados.
- **`Deprecated APIs`**: inclua a subseção apenas se aplicável; caso contrário,
  omita-a por completo (não escreva "nenhuma").
- **Nunca** escreva segredos reais no relatório — mascare valores sensíveis
  (ex.: `SECRET_KEY = "minha-****"`).
- O prompt de confirmação final é **literal** e obrigatório; a skill só prossegue
  para a Fase 3 com um `y` explícito.
