"""HTTP orchestration for user + auth endpoints."""
from flask import jsonify, request

from utils.validators import (
    parse_pagination,
    validate_login_payload,
    validate_user_payload,
)


class UserController:
    def __init__(self, user_service):
        self._service = user_service

    def list_users(self):
        limit, offset = parse_pagination(request.args)
        usuarios = self._service.list_users(limit, offset)
        return jsonify({"dados": usuarios, "sucesso": True}), 200

    def get_user(self, id):
        usuario = self._service.get_user(id)
        return jsonify({"dados": usuario, "sucesso": True}), 200

    def create_user(self):
        data = validate_user_payload(request.get_json(silent=True))
        user_id = self._service.create_user(data)
        return jsonify({"dados": {"id": user_id}, "sucesso": True}), 201

    def login(self):
        data = validate_login_payload(request.get_json(silent=True))
        usuario = self._service.authenticate(data["email"], data["senha"])
        if usuario:
            return jsonify({
                "dados": usuario,
                "sucesso": True,
                "mensagem": "Login OK",
            }), 200
        return jsonify({
            "erro": "Email ou senha inválidos",
            "sucesso": False,
        }), 401
