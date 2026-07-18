"""Centralized row-to-dict serialization.

Keeps external JSON field names (Portuguese) intact and guarantees sensitive
fields (e.g. the password hash) are never exposed.
"""


def serialize_product(row):
    """Public representation of a product row."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def serialize_user_public(row):
    """Public representation of a user row (never includes the password)."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def serialize_login(row):
    """Minimal user payload returned after a successful login (no password)."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }
