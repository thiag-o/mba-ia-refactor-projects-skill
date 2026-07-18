'use strict';

const { hashPassword } = require('../lib/password');
const { NotFoundError, PaymentDeniedError, BadRequestError } = require('../errors/AppError');

/**
 * Orchestrates the checkout business flow: validate the course, authorize the
 * payment, create the user if needed, enroll, record payment, audit and cache.
 * All collaborators are injected (DIP); this service contains no HTTP or SQL.
 */
class CheckoutService {
  constructor({
    userModel,
    courseModel,
    enrollmentModel,
    paymentModel,
    auditLogModel,
    paymentGateway,
    cache,
    logger,
  }) {
    this.userModel = userModel;
    this.courseModel = courseModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
    this.auditLogModel = auditLogModel;
    this.paymentGateway = paymentGateway;
    this.cache = cache;
    this.logger = logger;
  }

  async checkout({ name, email, password, courseId, card }) {
    const course = await this.courseModel.findActiveById(courseId);
    if (!course) {
      throw new NotFoundError('Curso não encontrado');
    }

    const authorization = this.paymentGateway.authorize(card, course.price);
    if (!authorization.approved) {
      throw new PaymentDeniedError('Pagamento recusado');
    }

    const userId = await this.resolveUser({ name, email, password });

    const enrollmentId = await this.enrollmentModel.create(userId, courseId);
    await this.paymentModel.create(enrollmentId, course.price, authorization.status);
    await this.auditLogModel.create(`Checkout course ${courseId} by user ${userId}`);

    this.cache.set(`last_checkout_${userId}`, course.title);
    this.logger.info('Checkout completed', { userId, courseId, enrollmentId });

    return { enrollmentId };
  }

  /**
   * Returns the id of the existing user for the email, or creates a new user.
   * A real password is required to create an account — no insecure default is
   * ever assigned (P-05).
   */
  async resolveUser({ name, email, password }) {
    const existingUser = await this.userModel.findByEmail(email);
    if (existingUser) {
      return existingUser.id;
    }

    if (!password) {
      throw new BadRequestError('Bad Request');
    }
    const passwordHash = await hashPassword(password);
    return this.userModel.create({ name, email, passwordHash });
  }
}

module.exports = CheckoutService;
