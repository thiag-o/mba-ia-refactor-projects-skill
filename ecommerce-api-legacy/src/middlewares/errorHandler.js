'use strict';

/**
 * Centralized Express error-handling middleware (P-08). Every controller/service
 * error flows here through next(err). Client errors (4xx) are logged as warnings
 * and returned with their message; unexpected errors (5xx) are logged with the
 * stack and returned with a generic message so internals are not leaked.
 *
 * Responses are sent as plain text to preserve the original contract messages
 * ("Bad Request", "Curso não encontrado", "Pagamento recusado").
 */
function createErrorHandler(logger) {
  // eslint-disable-next-line no-unused-vars -- Express requires the 4-arg signature.
  return function errorHandler(err, req, res, next) {
    const statusCode = err.statusCode || 500;

    if (statusCode >= 500) {
      logger.error('Unhandled error', { message: err.message, stack: err.stack });
      return res.status(statusCode).send('Internal Server Error');
    }

    logger.warn('Request error', { statusCode, message: err.message });
    return res.status(statusCode).send(err.message);
  };
}

module.exports = { createErrorHandler };
