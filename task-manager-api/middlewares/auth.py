"""Authentication/authorization middleware for sensitive routes."""
from functools import wraps

from flask import g, request

from errors import ApiError
from repositories import user_repository
from services import auth_service


def _extract_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):].strip()
    return header.strip() or None


def _load_current_user():
    token = _extract_token()
    if not token:
        raise ApiError("Token não fornecido", 401)
    payload = auth_service.verify_token(token)
    user = user_repository.get_by_id(payload.get("user_id"))
    if not user:
        raise ApiError("Credenciais inválidas", 401)
    g.current_user = user
    return user


def require_auth(fn):
    """Reject requests without a valid token; exposes g.current_user."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        _load_current_user()
        return fn(*args, **kwargs)

    return wrapper


def require_admin(fn):
    """Reject requests that are not authenticated as an admin user."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = _load_current_user()
        if not user.is_admin():
            raise ApiError("Acesso negado", 403)
        return fn(*args, **kwargs)

    return wrapper


def assert_admin():
    """Imperative admin guard for conditional protection (e.g. role changes)."""
    user = _load_current_user()
    if not user.is_admin():
        raise ApiError("Acesso negado", 403)
    return user
