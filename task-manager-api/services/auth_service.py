"""Authentication logic: issue and verify signed, expiring tokens.

Uses ``itsdangerous`` (bundled with Flask) to produce a real signed token
keyed on the application ``SECRET_KEY`` — replacing the previous fake token —
without introducing a new dependency.
"""
from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from errors import ApiError

_SALT = "auth-token"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_SALT)


def generate_token(user):
    """Return a signed token embedding the user's id and role."""
    return _serializer().dumps({"user_id": user.id, "role": user.role})


def verify_token(token):
    """Decode and validate a token, raising ApiError(401) when invalid."""
    max_age = current_app.config.get("TOKEN_MAX_AGE")
    try:
        return _serializer().loads(token, max_age=max_age)
    except SignatureExpired:
        raise ApiError("Token expirado", 401)
    except BadSignature:
        raise ApiError("Token inválido", 401)
