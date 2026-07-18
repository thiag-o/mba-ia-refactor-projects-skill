"""Shared input validators.

Validators raise ValidationError on the first problem, preserving the original
single-message error contract. The product validator is shared between the
create and update flows (removing the previous duplication).
"""
from config import constants
from utils.exceptions import ValidationError


def validate_product_payload(data):
    """Validate the product create/update payload.

    Returns a normalized dict with defaults applied. Raises ValidationError.
    """
    if not data:
        raise ValidationError("Dados inválidos")
    if "nome" not in data:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in data:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in data:
        raise ValidationError("Estoque é obrigatório")

    nome = data["nome"]
    descricao = data.get("descricao", "")
    preco = data["preco"]
    estoque = data["estoque"]
    categoria = data.get("categoria", constants.DEFAULT_CATEGORY)

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < constants.NAME_MIN_LENGTH:
        raise ValidationError("Nome muito curto")
    if len(nome) > constants.NAME_MAX_LENGTH:
        raise ValidationError("Nome muito longo")
    if categoria not in constants.VALID_CATEGORIES:
        raise ValidationError(
            "Categoria inválida. Válidas: " + str(constants.VALID_CATEGORIES)
        )

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validate_user_payload(data):
    """Validate the user registration payload."""
    if not data:
        raise ValidationError("Dados inválidos")

    nome = data.get("nome", "")
    email = data.get("email", "")
    senha = data.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")

    return {"nome": nome, "email": email, "senha": senha}


def validate_login_payload(data):
    """Validate the login payload."""
    if not data:
        raise ValidationError("Email e senha são obrigatórios")

    email = data.get("email", "")
    senha = data.get("senha", "")

    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")

    return {"email": email, "senha": senha}


def validate_order_payload(data):
    """Validate the order creation payload."""
    if not data:
        raise ValidationError("Dados inválidos")

    usuario_id = data.get("usuario_id")
    itens = data.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not itens or len(itens) == 0:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    return {"usuario_id": usuario_id, "itens": itens}


def validate_order_status(status):
    """Validate an order status transition value."""
    if status not in constants.VALID_ORDER_STATUSES:
        raise ValidationError("Status inválido")
    return status


def parse_pagination(args):
    """Parse optional limit/offset query params with sensible, capped defaults."""
    try:
        limit = int(args.get("limit", constants.DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        limit = constants.DEFAULT_PAGE_SIZE
    try:
        offset = int(args.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0

    limit = max(1, min(limit, constants.MAX_PAGE_SIZE))
    offset = max(0, offset)
    return limit, offset
