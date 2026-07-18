'use strict';

const express = require('express');

const settings = require('./config/settings');
const createLogger = require('./lib/logger');
const { createDatabase } = require('./lib/db');
const Cache = require('./lib/cache');
const { hashPassword } = require('./lib/password');
const { createSchemaAndSeed } = require('./db/schema');

const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');

const PaymentGateway = require('./services/paymentGateway');
const CheckoutService = require('./services/checkoutService');
const FinancialReportService = require('./services/financialReportService');
const UserService = require('./services/userService');

const CheckoutController = require('./controllers/checkoutController');
const AdminController = require('./controllers/adminController');
const UserController = require('./controllers/userController');

const { createRequireAdmin } = require('./middlewares/auth');
const { createErrorHandler } = require('./middlewares/errorHandler');
const { buildRouter } = require('./routes');

/**
 * Composition root: instantiates and wires every dependency (injection), then
 * registers routes and middlewares. Contains no business logic.
 */
async function bootstrap() {
  const logger = createLogger(settings.logLevel);

  // Infrastructure.
  const db = createDatabase(settings.database.filename);
  const seedPasswordHash = await hashPassword(settings.seedUserPassword);
  await createSchemaAndSeed(db, { seedPasswordHash, logger });

  const cache = new Cache();

  // Models (persistence layer).
  const userModel = new UserModel(db);
  const courseModel = new CourseModel(db);
  const enrollmentModel = new EnrollmentModel(db);
  const paymentModel = new PaymentModel(db);
  const auditLogModel = new AuditLogModel(db);
  const reportModel = new ReportModel(db);

  // Services (business logic).
  const paymentGateway = new PaymentGateway({
    apiKey: settings.paymentGatewayKey,
    logger,
  });
  const checkoutService = new CheckoutService({
    userModel,
    courseModel,
    enrollmentModel,
    paymentModel,
    auditLogModel,
    paymentGateway,
    cache,
    logger,
  });
  const financialReportService = new FinancialReportService({ reportModel, logger });
  const userService = new UserService({
    userModel,
    enrollmentModel,
    paymentModel,
    logger,
  });

  // Controllers.
  const checkoutController = new CheckoutController({ checkoutService });
  const adminController = new AdminController({ financialReportService });
  const userController = new UserController({ userService });

  // Middlewares.
  const requireAdmin = createRequireAdmin(settings.adminToken);

  // HTTP app.
  const app = express();
  app.use(express.json());
  app.use(buildRouter({ checkoutController, adminController, userController, requireAdmin }));
  app.use(createErrorHandler(logger));

  app.listen(settings.port, () => {
    logger.info(`LMS API listening on port ${settings.port}`);
  });

  return app;
}

bootstrap().catch((err) => {
  // Fatal boot failure — log to stderr and exit non-zero.
  process.stderr.write(`Failed to start application: ${err.stack || err.message}\n`);
  process.exit(1);
});

module.exports = { bootstrap };
