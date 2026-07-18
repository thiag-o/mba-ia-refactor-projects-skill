'use strict';

/**
 * Payment persistence. All SQL touching the `payments` table lives here.
 */
class PaymentModel {
  constructor(db) {
    this.db = db;
  }

  create(enrollmentId, amount, status) {
    return this.db.run(
      'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
      [enrollmentId, amount, status],
    );
  }

  /**
   * Cascade cleanup: remove payments belonging to a user's enrollments.
   */
  deleteByUserId(userId) {
    return this.db.run(
      'DELETE FROM payments WHERE enrollment_id IN '
        + '(SELECT id FROM enrollments WHERE user_id = ?)',
      [userId],
    );
  }
}

module.exports = PaymentModel;
