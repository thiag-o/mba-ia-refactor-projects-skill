"""Health check endpoint. Reports status/counts without leaking secrets."""
from flask import jsonify

from config import settings


class HealthController:
    def __init__(self, product_repository, user_repository, order_repository):
        self._products = product_repository
        self._users = user_repository
        self._orders = order_repository

    def health_check(self):
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": self._products.count(),
                "usuarios": self._users.count(),
                "pedidos": self._orders.count(),
            },
            "versao": settings.APP_VERSION,
            "ambiente": settings.ENVIRONMENT,
        }), 200
