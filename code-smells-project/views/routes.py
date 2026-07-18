"""Route definitions (HTTP layer).

Maps URLs/methods to controller methods, preserving the original external
contract. Endpoint names match the legacy ``add_url_rule`` names.
"""
from flask import jsonify

from config import settings
from middlewares.auth import require_admin


def register_routes(app, controllers):
    product = controllers["product"]
    user = controllers["user"]
    order = controllers["order"]
    report = controllers["report"]
    health = controllers["health"]
    admin = controllers["admin"]

    # Products
    app.add_url_rule("/produtos", "listar_produtos", product.list_products, methods=["GET"])
    app.add_url_rule("/produtos/busca", "buscar_produtos", product.search_products, methods=["GET"])
    app.add_url_rule("/produtos/<int:id>", "buscar_produto", product.get_product, methods=["GET"])
    app.add_url_rule("/produtos", "criar_produto", product.create_product, methods=["POST"])
    app.add_url_rule("/produtos/<int:id>", "atualizar_produto", product.update_product, methods=["PUT"])
    app.add_url_rule("/produtos/<int:id>", "deletar_produto", product.delete_product, methods=["DELETE"])

    # Users + auth
    app.add_url_rule("/usuarios", "listar_usuarios", user.list_users, methods=["GET"])
    app.add_url_rule("/usuarios/<int:id>", "buscar_usuario", user.get_user, methods=["GET"])
    app.add_url_rule("/usuarios", "criar_usuario", user.create_user, methods=["POST"])
    app.add_url_rule("/login", "login", user.login, methods=["POST"])

    # Orders
    app.add_url_rule("/pedidos", "criar_pedido", order.create_order, methods=["POST"])
    app.add_url_rule("/pedidos", "listar_todos_pedidos", order.list_orders, methods=["GET"])
    app.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", order.list_orders_by_user, methods=["GET"])
    app.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", order.update_status, methods=["PUT"])

    # Reports
    app.add_url_rule("/relatorios/vendas", "relatorio_vendas", report.sales_report, methods=["GET"])

    # Health
    app.add_url_rule("/health", "health_check", health.health_check, methods=["GET"])

    # Admin (guarded). /admin/query has been removed entirely.
    app.add_url_rule(
        "/admin/reset-db", "reset_database",
        require_admin(admin.reset_database), methods=["POST"],
    )

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": settings.APP_VERSION,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })
