"""Central error handling: maps exceptions to consistent JSON responses."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.exceptions import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        # Expected, domain-level errors: log at info/warning, no stack trace.
        logger.info("%s: %s", type(error).__name__, error.message)
        return jsonify({"erro": error.message, "sucesso": False}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"erro": error.description, "sucesso": False}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        # Unexpected failures: full stack trace to logs, generic message out.
        logger.exception("Erro inesperado")
        return jsonify({"erro": str(error), "sucesso": False}), 500
