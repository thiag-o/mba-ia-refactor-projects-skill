'use strict';

/**
 * Course persistence. All SQL touching the `courses` table lives here.
 */
class CourseModel {
  constructor(db) {
    this.db = db;
  }

  findActiveById(id) {
    return this.db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
  }

  findAll() {
    return this.db.all('SELECT * FROM courses', []);
  }
}

module.exports = CourseModel;
