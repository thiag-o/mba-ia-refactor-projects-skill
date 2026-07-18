"""Authentication/authorization middleware for sensitive routes."""
from functools import wraps

from flask import request

from config import settings
from utils.exceptions import AuthError, ForbiddenError


def _extract_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):].strip()
    # Also accept a dedicated admin header for convenience.
    return request.headers.get("X-Admin-Token", "").strip()


def require_admin(fn):
    """Reject anonymous/non-admin callers before the handler runs."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            raise AuthError("Autenticação necessária")
        if token != settings.ADMIN_TOKEN:
            raise ForbiddenError("Acesso negado")
        return fn(*args, **kwargs)

    return wrapper
