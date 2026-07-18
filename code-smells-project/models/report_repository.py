"""Aggregate sales queries for reporting. Parameterized where applicable."""


class ReportRepository:
    def __init__(self, get_connection):
        self._get_connection = get_connection

    def sales_aggregates(self):
        """Return raw sales aggregates; business math lives in the service."""
        cursor = self._get_connection().cursor()

        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(total) FROM pedidos")
        faturamento = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = ?", ("pendente",)
        )
        pendentes = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = ?", ("aprovado",)
        )
        aprovados = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = ?", ("cancelado",)
        )
        cancelados = cursor.fetchone()[0]

        return {
            "total_pedidos": total_pedidos,
            "faturamento": faturamento,
            "pendentes": pendentes,
            "aprovados": aprovados,
            "cancelados": cancelados,
        }
