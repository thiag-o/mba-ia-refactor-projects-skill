"""Validation and serialization for tasks.

Validation is centralized here (previously duplicated across create/update
handlers). Error messages and status codes are kept identical to the original
API so the external contract is preserved.
"""
from datetime import datetime

from config.constants import (
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    MAX_PRIORITY,
    VALID_STATUSES,
)
from errors import ApiError


def _validate_title(title):
    if len(title) < MIN_TITLE_LENGTH:
        raise ApiError("Título muito curto", 400)
    if len(title) > MAX_TITLE_LENGTH:
        raise ApiError("Título muito longo", 400)


def _validate_status(status):
    if status not in VALID_STATUSES:
        raise ApiError("Status inválido", 400)


def _validate_priority(priority):
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ApiError("Prioridade deve ser entre 1 e 5", 400)


def _parse_due_date(value, invalid_message):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ApiError(invalid_message, 400)


def _normalize_tags(tags):
    if isinstance(tags, list):
        return ",".join(tags)
    return tags


def validate_create(data):
    """Validate a task creation payload and return normalized fields."""
    if not data:
        raise ApiError("Dados inválidos", 400)

    title = data.get("title")
    if not title:
        raise ApiError("Título é obrigatório", 400)
    _validate_title(title)

    status = data.get("status", "pending")
    _validate_status(status)

    priority = data.get("priority", 3)
    _validate_priority(priority)

    result = {
        "title": title,
        "description": data.get("description", ""),
        "status": status,
        "priority": priority,
        "user_id": data.get("user_id"),
        "category_id": data.get("category_id"),
        "due_date": None,
        "tags": None,
    }

    if data.get("due_date"):
        result["due_date"] = _parse_due_date(
            data["due_date"], "Formato de data inválido. Use YYYY-MM-DD"
        )
    if data.get("tags"):
        result["tags"] = _normalize_tags(data["tags"])
    return result


def validate_update(data):
    """Validate a partial task update payload and return the changed fields."""
    if not data:
        raise ApiError("Dados inválidos", 400)

    changes = {}
    if "title" in data:
        _validate_title(data["title"])
        changes["title"] = data["title"]
    if "description" in data:
        changes["description"] = data["description"]
    if "status" in data:
        _validate_status(data["status"])
        changes["status"] = data["status"]
    if "priority" in data:
        _validate_priority(data["priority"])
        changes["priority"] = data["priority"]
    if "user_id" in data:
        changes["user_id"] = data["user_id"]
    if "category_id" in data:
        changes["category_id"] = data["category_id"]
    if "due_date" in data:
        if data["due_date"]:
            changes["due_date"] = _parse_due_date(
                data["due_date"], "Formato de data inválido"
            )
        else:
            changes["due_date"] = None
    if "tags" in data:
        changes["tags"] = _normalize_tags(data["tags"])
    return changes


def dump(task):
    """Serialize a task to its canonical dict representation."""
    return task.to_dict()


def dump_with_details(task):
    """Serialize a task including overdue flag and related names."""
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    data["user_name"] = task.user.name if task.user else None
    data["category_name"] = task.category.name if task.category else None
    return data


def dump_with_overdue(task):
    """Serialize a task adding only the overdue flag (GET /tasks/<id>)."""
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    return data


def dump_summary(task):
    """Reduced serialization used by GET /users/<id>/tasks."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "created_at": str(task.created_at),
        "due_date": str(task.due_date) if task.due_date else None,
        "overdue": task.is_overdue(),
    }
