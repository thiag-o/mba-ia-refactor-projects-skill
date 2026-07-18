"""Centralized error handling.

A single place converts exceptions into JSON responses, preserving the
``{"error": <message>}`` shape and the original status codes. Unexpected
exceptions are logged and reported as a generic 500 without leaking internals.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException

from errors import ApiError
from utils.logger import get_logger

logger = get_logger(__name__)


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Unhandled exception: %s", error)
        return jsonify({"error": "Erro interno"}), 500
