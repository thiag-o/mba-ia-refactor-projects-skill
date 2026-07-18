'use strict';

/**
 * Application configuration.
 *
 * Every sensitive value is read from environment variables so that no secret is
 * ever hardcoded or versioned. Safe, non-sensitive defaults keep local/demo
 * boot working out of the box (P-01).
 */
function parseInteger(value, fallback) {
  const parsed = parseInt(value, 10);
  return Number.isNaN(parsed) ? fallback : parsed;
}

module.exports = {
  port: parseInteger(process.env.PORT, 3000),

  database: {
    // ':memory:' keeps the seeded demo DB by default; override with DB_FILE for
    // durable, file-backed persistence.
    filename: process.env.DB_FILE || ':memory:',
  },

  // Infrastructure credentials — supplied via env, never committed.
  db: {
    user: process.env.DB_USER || 'app_user',
    password: process.env.DB_PASSWORD || '',
  },

  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'dev-placeholder-key',
  smtpUser: process.env.SMTP_USER || 'no-reply@example.com',

  // Token expected by the admin auth middleware on sensitive/destructive routes.
  adminToken: process.env.ADMIN_TOKEN || 'dev-admin-token',

  // Password used only to seed the demo user (hashed on boot).
  seedUserPassword: process.env.SEED_USER_PASSWORD || 'dev-seed-password',

  logLevel: process.env.LOG_LEVEL || 'info',
};
