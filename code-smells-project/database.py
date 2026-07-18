"""Database infrastructure: per-request SQLite connections + schema/seed.

Replaces the previous global, cross-thread singleton connection. Each request
gets its own connection stored on Flask's ``g`` and closed on teardown.
"""
import logging
import sqlite3

from flask import g

from config import settings
from utils.security import hash_password

logger = logging.getLogger(__name__)


def _connect():
    """Open a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    """Return the connection bound to the current request context.

    Injected into repositories as their connection provider (DIP).
    """
    if "db" not in g:
        g.db = _connect()
    return g.db


def close_db(exception=None):
    """Close and detach the request-scoped connection, if any."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """Register the teardown hook so connections are always released."""
    app.teardown_appcontext(close_db)


def _create_schema(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            preco REAL,
            estoque INTEGER,
            categoria TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            senha TEXT,
            tipo TEXT DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            status TEXT DEFAULT 'pendente',
            total REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unitario REAL
        )
        """
    )


def _seed(cursor):
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        produtos = [
            ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
            ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
            ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
            ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
            ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
            ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
            ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
            ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
            ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
            ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
        ]
        cursor.executemany(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            produtos,
        )

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        # Passwords are hashed at seed time so /login keeps working with the
        # documented sample credentials while nothing is stored in plaintext.
        usuarios = [
            ("Admin", "admin@loja.com", hash_password("admin123"), "admin"),
            ("João Silva", "joao@email.com", hash_password("123456"), "cliente"),
            ("Maria Santos", "maria@email.com", hash_password("senha123"), "cliente"),
        ]
        cursor.executemany(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            usuarios,
        )


def init_schema_and_seed():
    """Create tables and seed sample data on boot (own short-lived connection)."""
    conn = _connect()
    try:
        cursor = conn.cursor()
        _create_schema(cursor)
        conn.commit()
        _seed(cursor)
        conn.commit()
    finally:
        conn.close()
    logger.info("Database schema ready and seed verified.")
