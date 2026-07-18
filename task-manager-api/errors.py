"""Application-level exceptions used across the layers.

Raising an ``ApiError`` anywhere in the request flow lets the centralized
error handler (see ``middlewares/error_handler.py``) format a consistent JSON
response while preserving the original status codes and message keys that
clients depend on.
"""


class ApiError(Exception):
    """Domain error carrying an HTTP status code and a client-facing message."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
