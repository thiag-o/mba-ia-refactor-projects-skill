"""HTTP orchestration for reporting endpoints."""
from flask import jsonify


class ReportController:
    def __init__(self, report_service):
        self._service = report_service

    def sales_report(self):
        relatorio = self._service.sales_report()
        return jsonify({"dados": relatorio, "sucesso": True}), 200
