'use strict';

/**
 * Typed application errors carrying an HTTP status code. The central error
 * handler uses `statusCode` to build the response, so business/controller code
 * simply throws the right error and never touches res.status directly (P-08).
 */
class AppError extends Error {
  constructor(message, statusCode = 500) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    Error.captureStackTrace(this, this.constructor);
  }
}

class BadRequestError extends AppError {
  constructor(message = 'Bad Request') {
    super(message, 400);
  }
}

class NotFoundError extends AppError {
  constructor(message = 'Not Found') {
    super(message, 404);
  }
}

class PaymentDeniedError extends AppError {
  constructor(message = 'Pagamento recusado') {
    super(message, 400);
  }
}

class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 401);
  }
}

module.exports = {
  AppError,
  BadRequestError,
  NotFoundError,
  PaymentDeniedError,
  UnauthorizedError,
};
