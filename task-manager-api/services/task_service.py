"""Task business logic: orchestrates validation, persistence and aggregation."""
from sqlalchemy.exc import SQLAlchemyError

from config.constants import CLOSED_STATUSES
from errors import ApiError
from models.task import Task
from repositories import category_repository, task_repository, user_repository
from utils.helpers import calculate_percentage, now_utc
from utils.logger import get_logger

logger = get_logger(__name__)


def _ensure_related_exist(user_id, category_id):
    if user_id and not user_repository.get_by_id(user_id):
        raise ApiError("Usuário não encontrado", 404)
    if category_id and not category_repository.get_by_id(category_id):
        raise ApiError("Categoria não encontrada", 404)


def list_tasks():
    return task_repository.list_all()


def get_task(task_id):
    task = task_repository.get_by_id_with_relations(task_id)
    if not task:
        raise ApiError("Task não encontrada", 404)
    return task


def search_tasks(query=None, status=None, priority=None, user_id=None):
    return task_repository.search(query, status, priority, user_id)


def create_task(fields):
    _ensure_related_exist(fields.get("user_id"), fields.get("category_id"))

    task = Task()
    task.title = fields["title"]
    task.description = fields["description"]
    task.status = fields["status"]
    task.priority = fields["priority"]
    task.user_id = fields["user_id"]
    task.category_id = fields["category_id"]
    task.due_date = fields["due_date"]
    task.tags = fields["tags"]

    try:
        task_repository.add(task)
        task_repository.commit()
    except SQLAlchemyError as exc:
        task_repository.rollback()
        logger.error("Failed to create task: %s", exc)
        raise ApiError("Erro ao criar task", 500)

    logger.info("Task created: %s - %s", task.id, task.title)
    return task


def update_task(task_id, changes):
    task = task_repository.get_by_id(task_id)
    if not task:
        raise ApiError("Task não encontrada", 404)

    if "user_id" in changes and changes["user_id"]:
        if not user_repository.get_by_id(changes["user_id"]):
            raise ApiError("Usuário não encontrado", 404)
    if "category_id" in changes and changes["category_id"]:
        if not category_repository.get_by_id(changes["category_id"]):
            raise ApiError("Categoria não encontrada", 404)

    for field, value in changes.items():
        setattr(task, field, value)
    task.updated_at = now_utc()

    try:
        task_repository.commit()
    except SQLAlchemyError as exc:
        task_repository.rollback()
        logger.error("Failed to update task %s: %s", task_id, exc)
        raise ApiError("Erro ao atualizar", 500)

    logger.info("Task updated: %s", task.id)
    return task


def delete_task(task_id):
    task = task_repository.get_by_id(task_id)
    if not task:
        raise ApiError("Task não encontrada", 404)

    try:
        task_repository.delete(task)
        task_repository.commit()
    except SQLAlchemyError as exc:
        task_repository.rollback()
        logger.error("Failed to delete task %s: %s", task_id, exc)
        raise ApiError("Erro ao deletar", 500)

    logger.info("Task deleted: %s", task_id)


def get_stats():
    tasks = task_repository.list_all()
    total = len(tasks)
    counts = {"pending": 0, "in_progress": 0, "done": 0, "cancelled": 0}
    overdue = 0
    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1
        if task.is_overdue():
            overdue += 1

    return {
        "total": total,
        "pending": counts["pending"],
        "in_progress": counts["in_progress"],
        "done": counts["done"],
        "cancelled": counts["cancelled"],
        "overdue": overdue,
        "completion_rate": calculate_percentage(counts["done"], total),
    }
