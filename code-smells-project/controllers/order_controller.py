"""HTTP orchestration for order endpoints."""
from flask import jsonify, request

from utils.validators import (
    parse_pagination,
    validate_order_payload,
    validate_order_status,
)


class OrderController:
    def __init__(self, order_service):
        self._service = order_service

    def create_order(self):
        data = validate_order_payload(request.get_json(silent=True))
        resultado = self._service.create_order(data["usuario_id"], data["itens"])
        return jsonify({
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }), 201

    def list_orders(self):
        limit, offset = parse_pagination(request.args)
        pedidos = self._service.list_orders(limit, offset)
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def list_orders_by_user(self, usuario_id):
        pedidos = self._service.list_orders_by_user(usuario_id)
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def update_status(self, pedido_id):
        data = request.get_json(silent=True) or {}
        novo_status = validate_order_status(data.get("status", ""))
        self._service.update_status(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
