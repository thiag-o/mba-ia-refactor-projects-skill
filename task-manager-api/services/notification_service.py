"""Notification side effects (email), isolated from controllers and models.

Credentials are read from the environment — never hardcoded. If they are not
configured, the service logs and skips sending instead of failing the request.
"""
import os
import smtplib

from utils.helpers import now_utc
from utils.logger import get_logger

logger = get_logger(__name__)


class NotificationService:
    def __init__(self):
        self.notifications = []
        self.email_host = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
        self.email_port = int(os.environ.get("EMAIL_PORT", "587"))
        self.email_user = os.environ.get("EMAIL_USER")
        self.email_password = os.environ.get("EMAIL_PASSWORD")

    def send_email(self, to, subject, body):
        if not self.email_user or not self.email_password:
            logger.warning("Email credentials not configured; skipping send to %s", to)
            return False
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            logger.info("Email sent to %s", to)
            return True
        except smtplib.SMTPException as exc:
            logger.error("Failed to send email to %s: %s", to, exc)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append(
            {
                "type": "task_assigned",
                "user_id": user.id,
                "task_id": task.id,
                "timestamp": now_utc(),
            }
        )

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n["user_id"] == user_id]
