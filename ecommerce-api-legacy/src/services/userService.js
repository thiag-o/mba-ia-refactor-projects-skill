'use strict';

const { NotFoundError } = require('../errors/AppError');

/**
 * User management business logic. Deleting a user cascades to their enrollments
 * and payments so no orphaned rows are left behind (P-08 fixes the previous
 * "leaves dirty rows" behavior). Errors propagate instead of being swallowed.
 */
class UserService {
  constructor({ userModel, enrollmentModel, paymentModel, logger }) {
    this.userModel = userModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
    this.logger = logger;
  }

  async deleteUser(id) {
    const user = await this.userModel.findById(id);
    if (!user) {
      throw new NotFoundError('Usuário não encontrado');
    }

    // Cascade cleanup: payments -> enrollments -> user.
    await this.paymentModel.deleteByUserId(id);
    await this.enrollmentModel.deleteByUserId(id);
    await this.userModel.deleteById(id);

    this.logger.info('User deleted with cascade cleanup', { userId: id });
  }
}

module.exports = UserService;
