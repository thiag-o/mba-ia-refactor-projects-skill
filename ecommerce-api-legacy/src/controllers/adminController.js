'use strict';

/**
 * Admin controller. Delegates the financial report to its service and returns
 * the preserved response shape: [{ course, revenue, students: [...] }].
 */
class AdminController {
  constructor({ financialReportService }) {
    this.financialReportService = financialReportService;
    this.financialReport = this.financialReport.bind(this);
  }

  async financialReport(req, res) {
    const report = await this.financialReportService.generate();
    res.status(200).json(report);
  }
}

module.exports = AdminController;
