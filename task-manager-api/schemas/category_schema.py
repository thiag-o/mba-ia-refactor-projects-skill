"""Validation and serialization for categories."""
from config.constants import DEFAULT_COLOR
from errors import ApiError


def validate_create(data):
    if not data:
        raise ApiError("Dados inválidos", 400)
    name = data.get("name")
    if not name:
        raise ApiError("Nome é obrigatório", 400)
    return {
        "name": name,
        "description": data.get("description", ""),
        "color": data.get("color", DEFAULT_COLOR),
    }


def validate_update(data):
    if not data:
        raise ApiError("Dados inválidos", 400)
    changes = {}
    if "name" in data:
        changes["name"] = data["name"]
    if "description" in data:
        changes["description"] = data["description"]
    if "color" in data:
        changes["color"] = data["color"]
    return changes


def dump(category):
    return category.to_dict()


def dump_with_task_count(category, task_count):
    data = category.to_dict()
    data["task_count"] = task_count
    return data
