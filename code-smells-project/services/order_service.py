"""Order business logic: stock validation, total calculation, notifications."""
import logging

from config import constants
from utils.exceptions import BusinessRuleError
from utils.validators import validate_order_status

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, order_repository, notification_service):
        self._repo = order_repository
        self._notifications = notification_service

    def create_order(self, usuario_id, itens):
        product_ids = [item["produto_id"] for item in itens]
        products = self._repo.get_products_by_ids(product_ids)

        total = 0
        prepared_items = []
        for item in itens:
            produto = products.get(item["produto_id"])
            if produto is None:
                raise BusinessRuleError(
                    "Produto " + str(item["produto_id"]) + " não encontrado"
                )
            if produto["estoque"] < item["quantidade"]:
                raise BusinessRuleError(
                    "Estoque insuficiente para " + produto["nome"]
                )
            total += produto["preco"] * item["quantidade"]
            prepared_items.append({
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"],
            })

        pedido_id = self._repo.create_order(
            usuario_id, constants.INITIAL_ORDER_STATUS, total, prepared_items
        )

        self._notifications.notify_order_created(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def list_orders(self, limit, offset):
        return self._repo.list_all(limit, offset)

    def list_orders_by_user(self, usuario_id):
        return self._repo.list_by_user(usuario_id)

    def update_status(self, pedido_id, status):
        validate_order_status(status)
        self._repo.update_status(pedido_id, status)
        self._notifications.notify_order_status_change(pedido_id, status)
        return True
