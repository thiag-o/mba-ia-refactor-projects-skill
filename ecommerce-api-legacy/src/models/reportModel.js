'use strict';

/**
 * Read model for the financial report. Fetches everything the report needs in a
 * single JOIN, eliminating the previous N+1 query pattern (P-07). Aggregation
 * itself is done in the service, in memory.
 */
class ReportModel {
  constructor(db) {
    this.db = db;
  }

  fetchReportRows() {
    return this.db.all(
      `SELECT
         c.id          AS course_id,
         c.title       AS course_title,
         e.id          AS enrollment_id,
         u.name        AS student_name,
         p.amount      AS payment_amount,
         p.status      AS payment_status
       FROM courses c
       LEFT JOIN enrollments e ON e.course_id = c.id
       LEFT JOIN users u       ON u.id = e.user_id
       LEFT JOIN payments p    ON p.enrollment_id = e.id
       ORDER BY c.id, e.id`,
      [],
    );
  }
}

module.exports = ReportModel;
