'use strict';

const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');

/**
 * Route definitions (the HTTP/View layer). Only wires endpoints to controllers
 * and applies middlewares — no business logic. Paths and methods are the
 * external contract and must not change. Admin/destructive routes are protected
 * by the auth middleware.
 */
function buildRouter({ checkoutController, adminController, userController, requireAdmin }) {
  const router = express.Router();

  router.post('/api/checkout', asyncHandler(checkoutController.handle));

  router.get(
    '/api/admin/financial-report',
    requireAdmin,
    asyncHandler(adminController.financialReport),
  );

  router.delete(
    '/api/users/:id',
    requireAdmin,
    asyncHandler(userController.remove),
  );

  return router;
}

module.exports = { buildRouter };
