"""Authentication controller (login)."""
from flask import jsonify, request

from schemas import user_schema
from services import user_service


def login():
    credentials = user_schema.validate_login(request.get_json(silent=True))
    user, token = user_service.authenticate(
        credentials["email"], credentials["password"]
    )
    return (
        jsonify(
            {
                "message": "Login realizado com sucesso",
                "user": user_schema.dump(user),
                "token": token,
            }
        ),
        200,
    )
