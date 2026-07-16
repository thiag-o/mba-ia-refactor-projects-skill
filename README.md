# Criação de Skills — Refatoração Arquitetural Automatizada

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
 

## ecommerce-api-legacy
### PROBLEMAS

- CRITICAL: Uma única class ``AppManager`` lidando com absolutamente tudo "God Class";

- MEDIUM: Validações ausentes, a validação utilizada para aprovar um cartão válido é apenas de o número do cartão começar com o número "4", exemplo:
```javaScript
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
let status = cc.startsWith("4") ? "PAID" : "DENIED";
```

- MEDIUM: As rotas "/api/admin/financial-report" e "/api/users/:id" estão totalmente abertas, não possuem nenhum middleware ou guard para restringir o acesso. 

- LOW: Problemas de legibilidade, há diversas variáveis sem um nome legivel que dificultam entender do que se trata cada dado, aqui está um exemplo da ocorrência: 
```javaScript
let u = req.body.usr;
let e = req.body.eml;
let p = req.body.pwd;
let cid = req.body.c_id;
let cc = req.body.card;

if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");
```

- LOW: Magic number no arquivo ``utils.js``, dentro da função ``badCrypto`` há um número solto ``10000``, aqui está a evidência:
```javaScript
 for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
```

## task-manager-api
### PROBLEMAS

- HIGHT: Presença de regra de negócio pesada nas funções dos controllers;

- MEDIUM: Há duplicação de código. O trecho abaixo se repete em pelo menos em sete pontos do projeto, apresentando apenas pequenas algumas variações:
```python
if t.due_date < datetime.utcnow():
            if t.status != 'done' and t.status != 'cancelled':
``` 

- MEDIUM: Sem paginação para o GET /tasks, conforme os dados vão aumentando possívelmente isso poderá se tornar um gargalo à aplicação. 

- LOW: Há a presença de mágic numbers. Em ``user_report`` existe um if com ``t.priority <= 2``, o ideal seria definir um enum ou uma constante para armazenar o nível de prioridade.

- LOW: Repetição de regex de validação de email no arquivo ``user_routes``, o regex aparece duas vezes e já existe um regex de validação de email em ``helpers.py``.