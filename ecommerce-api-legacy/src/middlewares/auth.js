'use strict';

const { UnauthorizedError } = require('../errors/AppError');

/**
 * Authentication/authorization middleware for sensitive and destructive routes
 * (P-09). Expects a bearer token matching the configured admin token:
 *
 *   Authorization: Bearer <ADMIN_TOKEN>
 *
 * The token is injected from config (env-driven) — never hardcoded here.
 */
function createRequireAdmin(adminToken) {
  return function requireAdmin(req, res, next) {
    const header = req.headers.authorization || '';
    const token = header.startsWith('Bearer ') ? header.slice(7) : header;

    if (!token || token !== adminToken) {
      return next(new UnauthorizedError('Unauthorized'));
    }
    return next();
  };
}

module.exports = { createRequireAdmin };
