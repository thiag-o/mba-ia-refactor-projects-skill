"""Admin endpoints. Destructive operations are guarded by admin auth.

The arbitrary-SQL endpoint (POST /admin/query) has been removed entirely.
"""
import logging

from flask import jsonify

logger = logging.getLogger(__name__)


class AdminController:
    def __init__(self, get_connection):
        self._get_connection = get_connection

    def reset_database(self):
        db = self._get_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM itens_pedido")
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM usuarios")
        db.commit()
        logger.warning("Banco de dados resetado via endpoint admin")
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
