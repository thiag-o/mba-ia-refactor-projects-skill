"""Notification side effects, extracted out of controllers/models.

Uses the logging module (not print). A real implementation would dispatch to
email/SMS/push providers; here the channels are logged.
"""
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def notify_order_created(self, pedido_id, usuario_id):
        logger.info("EMAIL: pedido %s criado para usuario %s", pedido_id, usuario_id)
        logger.info("SMS: pedido %s recebido", pedido_id)
        logger.info("PUSH: novo pedido %s recebido pelo sistema", pedido_id)

    def notify_order_status_change(self, pedido_id, status):
        if status == "aprovado":
            logger.info("NOTIFICAÇÃO: pedido %s aprovado, preparar envio", pedido_id)
        elif status == "cancelado":
            logger.info("NOTIFICAÇÃO: pedido %s cancelado, devolver estoque", pedido_id)
