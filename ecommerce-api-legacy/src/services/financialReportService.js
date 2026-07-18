'use strict';

const { PAYMENT_STATUS } = require('../config/constants');

/**
 * Builds the financial report by fetching all rows in a single query (via the
 * read model) and aggregating in memory (P-07). No SQL, no HTTP here.
 *
 * Output shape (external contract, must be preserved):
 *   [{ course, revenue, students: [{ student, paid }] }]
 */
class FinancialReportService {
  constructor({ reportModel, logger }) {
    this.reportModel = reportModel;
    this.logger = logger;
  }

  async generate() {
    const rows = await this.reportModel.fetchReportRows();

    const reportByCourse = new Map();

    for (const row of rows) {
      if (!reportByCourse.has(row.course_id)) {
        reportByCourse.set(row.course_id, {
          course: row.course_title,
          revenue: 0,
          students: [],
        });
      }

      const courseReport = reportByCourse.get(row.course_id);

      // A null enrollment_id means the course has no enrollments (LEFT JOIN).
      if (row.enrollment_id != null) {
        if (row.payment_status === PAYMENT_STATUS.PAID) {
          courseReport.revenue += row.payment_amount;
        }
        courseReport.students.push({
          student: row.student_name || 'Unknown',
          paid: row.payment_amount != null ? row.payment_amount : 0,
        });
      }
    }

    this.logger.info('Financial report generated', { courses: reportByCourse.size });
    return [...reportByCourse.values()];
  }
}

module.exports = FinancialReportService;
