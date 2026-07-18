"""Composition root / entry point.

Instantiates and wires the layers (dependency injection), registers routes and
the central error handler, and boots the server. No business logic lives here.
"""
import logging

from flask import Flask
from flask_cors import CORS

import database
from config import settings
from controllers.admin_controller import AdminController
from controllers.health_controller import HealthController
from controllers.order_controller import OrderController
from controllers.product_controller import ProductController
from controllers.report_controller import ReportController
from controllers.user_controller import UserController
from middlewares.error_handler import register_error_handlers
from models.order_repository import OrderRepository
from models.product_repository import ProductRepository
from models.report_repository import ReportRepository
from models.user_repository import UserRepository
from services.notification_service import NotificationService
from services.order_service import OrderService
from services.product_service import ProductService
from services.report_service import ReportService
from services.user_service import UserService
from views.routes import register_routes

logger = logging.getLogger(__name__)


def create_app():
    """Application factory: build, wire and configure the Flask app."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    # Restrict CORS to a configured allow-list (no open wildcard).
    CORS(app, origins=settings.CORS_ORIGINS)

    # Per-request DB connection lifecycle.
    database.init_app(app)

    # --- Dependency injection wiring (composition root) ---
    get_connection = database.get_db

    product_repository = ProductRepository(get_connection)
    user_repository = UserRepository(get_connection)
    order_repository = OrderRepository(get_connection)
    report_repository = ReportRepository(get_connection)

    notification_service = NotificationService()
    product_service = ProductService(product_repository)
    user_service = UserService(user_repository)
    order_service = OrderService(order_repository, notification_service)
    report_service = ReportService(report_repository)

    controllers = {
        "product": ProductController(product_service),
        "user": UserController(user_service),
        "order": OrderController(order_service),
        "report": ReportController(report_service),
        "health": HealthController(product_repository, user_repository, order_repository),
        "admin": AdminController(get_connection),
    }

    register_routes(app, controllers)
    register_error_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    database.init_schema_and_seed()
    logger.info("SERVIDOR INICIADO - http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)
