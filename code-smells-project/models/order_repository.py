"""Order persistence.

Reads use a single JOIN across pedidos/itens_pedido/produtos (eliminating the
previous N+1 query pattern). All queries are parameterized.
"""


class OrderRepository:
    def __init__(self, get_connection):
        self._get_connection = get_connection

    def get_products_by_ids(self, product_ids):
        """Fetch products referenced by an order in a single query (no N+1)."""
        if not product_ids:
            return {}
        placeholders = ",".join(["?"] * len(product_ids))
        cursor = self._get_connection().cursor()
        cursor.execute(
            f"SELECT * FROM produtos WHERE id IN ({placeholders})",
            list(product_ids),
        )
        return {row["id"]: row for row in cursor.fetchall()}

    def create_order(self, usuario_id, status, total, items):
        """Persist an order, its items and stock decrements as one transaction.

        ``items`` is a list of dicts: produto_id, quantidade, preco_unitario.
        """
        db = self._get_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, status, total),
        )
        pedido_id = cursor.lastrowid

        for item in items:
            cursor.execute(
                "INSERT INTO itens_pedido "
                "(pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        db.commit()
        return pedido_id

    def update_status(self, pedido_id, status):
        db = self._get_connection()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id)
        )
        db.commit()
        return True

    def _fetch_orders(self, where_clause="", params=(), limit=None, offset=0):
        """Load orders with nested items via a single LEFT JOIN query."""
        query = (
            "SELECT p.id AS pedido_id, p.usuario_id, p.status, p.total, "
            "p.criado_em, i.produto_id, i.quantidade, i.preco_unitario, "
            "pr.nome AS produto_nome "
            "FROM pedidos p "
            "LEFT JOIN itens_pedido i ON i.pedido_id = p.id "
            "LEFT JOIN produtos pr ON pr.id = i.produto_id "
        )
        query += where_clause
        query += " ORDER BY p.id"

        cursor = self._get_connection().cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        orders = {}
        order_sequence = []
        for row in rows:
            pedido_id = row["pedido_id"]
            if pedido_id not in orders:
                orders[pedido_id] = {
                    "id": pedido_id,
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": [],
                }
                order_sequence.append(pedido_id)
            if row["produto_id"] is not None:
                orders[pedido_id]["itens"].append({
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                })

        result = [orders[pid] for pid in order_sequence]

        # In-memory pagination keeps whole orders intact (rows are per-item).
        if limit is not None:
            result = result[offset:offset + limit]
        return result

    def list_all(self, limit, offset):
        return self._fetch_orders(limit=limit, offset=offset)

    def list_by_user(self, usuario_id):
        return self._fetch_orders(
            where_clause="WHERE p.usuario_id = ? ", params=(usuario_id,)
        )

    def count(self):
        cursor = self._get_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        return cursor.fetchone()[0]
