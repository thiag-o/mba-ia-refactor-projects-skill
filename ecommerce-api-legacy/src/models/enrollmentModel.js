'use strict';

/**
 * Enrollment persistence. All SQL touching the `enrollments` table lives here.
 */
class EnrollmentModel {
  constructor(db) {
    this.db = db;
  }

  async create(userId, courseId) {
    const result = await this.db.run(
      'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
      [userId, courseId],
    );
    return result.lastID;
  }

  deleteByUserId(userId) {
    return this.db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
  }
}

module.exports = EnrollmentModel;
