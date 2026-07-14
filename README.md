# Criação de Skills — Refatoração Arquitetural Automatizada

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.


## Análise Manual
## code-smells-project

### PROBLEMAS

- CRITICAL: ``app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`` CREDENCIAL hardcoded;

- MEDIUM: Queries N+1 no banco de dados. Esse problema ocorre na função get_pedidos_usuario, onde é realizado 1 query para puxar todos os pedidos do usuário, 1 query para puxar os itens do pedido e 1 query para puxar as informações dos produtos e tudo isso ocorre dentro de 2 for aninhados.

- MEDIUM: Falta validações de endpoints de usuário, um exemplo é a rota de deletar um produto, não há validação de usuário, ou seja, um produto pode ser deletado sem ser por um usuário logado, uma clara vulnerabilidade no sistema.  

- LOW: Mágic numbers, há a presença de números soltos em um trecho do código, o ideal seria armazená-los em uma variável autoexplicativa.
```python
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02
```

- LOW: Variáveis em 2 idiomas diferentes (inglês e português), exemplo:
```python
    dados = request.get_json()
    query = dados.get("sql", "")
```
 

