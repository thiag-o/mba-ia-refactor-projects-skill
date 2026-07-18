"""Sales report business logic (discount tiers via named constants)."""
from config import constants


def compute_discount(faturamento):
    """Return the applicable discount for a given gross revenue."""
    for threshold, rate in constants.DISCOUNT_TIERS:
        if faturamento > threshold:
            return faturamento * rate
    return 0


class ReportService:
    def __init__(self, report_repository):
        self._repo = report_repository

    def sales_report(self):
        agg = self._repo.sales_aggregates()
        faturamento = agg["faturamento"]
        total_pedidos = agg["total_pedidos"]
        desconto = compute_discount(faturamento)

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": agg["pendentes"],
            "pedidos_aprovados": agg["aprovados"],
            "pedidos_cancelados": agg["cancelados"],
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }
