"""Composition root / application entry point.

Wires configuration, database, blueprints and the centralized error handler
together via the ``create_app`` factory. No business logic lives here.
Running ``python app.py`` still boots the server on port 5000.
"""
from flask import Flask, jsonify
from flask_cors import CORS

from config.settings import Config
from database import db
from middlewares.error_handler import register_error_handlers
from utils.helpers import now_utc

# Import models so their tables are registered with SQLAlchemy metadata.
from models import Category, Task, User  # noqa: F401

from routes.category_routes import category_bp
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp


def register_blueprints(app):
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(category_bp)


def register_core_routes(app):
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "timestamp": str(now_utc())})

    @app.route("/")
    def index():
        return jsonify({"message": "Task Manager API", "version": "1.0"})


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(app, origins=Config.cors_origins())
    db.init_app(app)

    register_blueprints(app)
    register_core_routes(app)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
