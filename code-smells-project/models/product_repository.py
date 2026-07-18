"""Product persistence. All queries are parameterized (no SQL injection)."""
from utils.serializers import serialize_product


class ProductRepository:
    def __init__(self, get_connection):
        # Connection provider is injected (DIP) rather than imported globally.
        self._get_connection = get_connection

    def list_all(self, limit, offset):
        cursor = self._get_connection().cursor()
        cursor.execute(
            "SELECT * FROM produtos LIMIT ? OFFSET ?", (limit, offset)
        )
        return [serialize_product(row) for row in cursor.fetchall()]

    def get_by_id(self, product_id):
        cursor = self._get_connection().cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        return serialize_product(row) if row else None

    def create(self, nome, descricao, preco, estoque, categoria):
        db = self._get_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        db.commit()
        return cursor.lastrowid

    def update(self, product_id, nome, descricao, preco, estoque, categoria):
        db = self._get_connection()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, "
            "estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, product_id),
        )
        db.commit()
        return True

    def delete(self, product_id):
        db = self._get_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        db.commit()
        return True

    def search(self, term, category, price_min, price_max):
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []
        if term:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            like = f"%{term}%"
            params.extend([like, like])
        if category:
            query += " AND categoria = ?"
            params.append(category)
        if price_min is not None:
            query += " AND preco >= ?"
            params.append(price_min)
        if price_max is not None:
            query += " AND preco <= ?"
            params.append(price_max)

        cursor = self._get_connection().cursor()
        cursor.execute(query, params)
        return [serialize_product(row) for row in cursor.fetchall()]

    def count(self):
        cursor = self._get_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        return cursor.fetchone()[0]
