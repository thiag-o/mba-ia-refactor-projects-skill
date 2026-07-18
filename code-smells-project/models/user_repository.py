"""User persistence. Parameterized queries; password hash never serialized out."""
from utils.serializers import serialize_user_public


class UserRepository:
    def __init__(self, get_connection):
        self._get_connection = get_connection

    def list_all(self, limit, offset):
        cursor = self._get_connection().cursor()
        cursor.execute(
            "SELECT * FROM usuarios LIMIT ? OFFSET ?", (limit, offset)
        )
        return [serialize_user_public(row) for row in cursor.fetchall()]

    def get_by_id(self, user_id):
        cursor = self._get_connection().cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return serialize_user_public(row) if row else None

    def get_by_email_raw(self, email):
        """Return the raw row (including password hash) for authentication only."""
        cursor = self._get_connection().cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        return cursor.fetchone()

    def create(self, nome, email, senha_hash, tipo="cliente"):
        db = self._get_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
        db.commit()
        return cursor.lastrowid

    def count(self):
        cursor = self._get_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        return cursor.fetchone()[0]
