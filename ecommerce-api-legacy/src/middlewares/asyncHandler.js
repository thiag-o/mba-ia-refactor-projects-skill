'use strict';

/**
 * Wraps an async route handler so any rejected promise is forwarded to the
 * central error-handling middleware via next(err) (P-08/P-10).
 */
module.exports = function asyncHandler(handler) {
  return (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);
};
