"""Validation and serialization for users (never serializes the password)."""
import re

from config.constants import MIN_PASSWORD_LENGTH, VALID_ROLES
from errors import ApiError

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")


def _validate_email_format(email):
    if not EMAIL_REGEX.match(email):
        raise ApiError("Email inválido", 400)


def _validate_role(role):
    if role not in VALID_ROLES:
        raise ApiError("Role inválido", 400)


def validate_create(data):
    if not data:
        raise ApiError("Dados inválidos", 400)

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        raise ApiError("Nome é obrigatório", 400)
    if not email:
        raise ApiError("Email é obrigatório", 400)
    if not password:
        raise ApiError("Senha é obrigatória", 400)

    _validate_email_format(email)

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ApiError("Senha deve ter no mínimo 4 caracteres", 400)

    _validate_role(role)

    return {"name": name, "email": email, "password": password, "role": role}


def validate_update(data):
    if not data:
        raise ApiError("Dados inválidos", 400)

    changes = {}
    if "name" in data:
        changes["name"] = data["name"]
    if "email" in data:
        _validate_email_format(data["email"])
        changes["email"] = data["email"]
    if "password" in data:
        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            raise ApiError("Senha muito curta", 400)
        changes["password"] = data["password"]
    if "role" in data:
        _validate_role(data["role"])
        changes["role"] = data["role"]
    if "active" in data:
        changes["active"] = data["active"]
    return changes


def validate_login(data):
    if not data:
        raise ApiError("Dados inválidos", 400)
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise ApiError("Email e senha são obrigatórios", 400)
    return {"email": email, "password": password}


def dump(user):
    return user.to_dict()


def dump_with_task_count(user):
    data = user.to_dict()
    data["task_count"] = len(user.tasks)
    return data
