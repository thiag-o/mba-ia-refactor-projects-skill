"""Domain-specific exceptions used across layers.

Each carries an HTTP status code so the central error handler can map it to a
response without leaking implementation details.
"""


class AppError(Exception):
    """Base application error."""

    status_code = 500

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    """Invalid client input."""

    status_code = 400


class BusinessRuleError(AppError):
    """A business rule was violated (e.g. insufficient stock)."""

    status_code = 400


class NotFoundError(AppError):
    """Requested resource does not exist."""

    status_code = 404


class AuthError(AppError):
    """Authentication failed."""

    status_code = 401


class ForbiddenError(AppError):
    """Authenticated but not authorized."""

    status_code = 403
