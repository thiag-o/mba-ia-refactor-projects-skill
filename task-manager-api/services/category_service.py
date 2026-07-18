"""Category business logic."""
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from database import db
from errors import ApiError
from models.category import Category
from models.task import Task
from repositories import category_repository
from utils.logger import get_logger

logger = get_logger(__name__)


def list_categories_with_counts():
    """Return each category paired with its task count.

    A single grouped query builds the counts, avoiding one query per category.
    """
    categories = category_repository.list_all()
    rows = (
        db.session.query(Task.category_id, func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )
    counts = {category_id: count for category_id, count in rows}
    return [(category, counts.get(category.id, 0)) for category in categories]


def create_category(fields):
    category = Category()
    category.name = fields["name"]
    category.description = fields["description"]
    category.color = fields["color"]

    try:
        category_repository.add(category)
        category_repository.commit()
    except SQLAlchemyError as exc:
        category_repository.rollback()
        logger.error("Failed to create category: %s", exc)
        raise ApiError("Erro ao criar categoria", 500)

    return category


def update_category(category_id, changes):
    category = category_repository.get_by_id(category_id)
    if not category:
        raise ApiError("Categoria não encontrada", 404)

    for field, value in changes.items():
        setattr(category, field, value)

    try:
        category_repository.commit()
    except SQLAlchemyError as exc:
        category_repository.rollback()
        logger.error("Failed to update category %s: %s", category_id, exc)
        raise ApiError("Erro ao atualizar", 500)

    return category


def delete_category(category_id):
    category = category_repository.get_by_id(category_id)
    if not category:
        raise ApiError("Categoria não encontrada", 404)

    try:
        category_repository.delete(category)
        category_repository.commit()
    except SQLAlchemyError as exc:
        category_repository.rollback()
        logger.error("Failed to delete category %s: %s", category_id, exc)
        raise ApiError("Erro ao deletar", 500)
