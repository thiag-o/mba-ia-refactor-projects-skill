"""Category controllers."""
from flask import jsonify, request

from schemas import category_schema
from services import category_service
from utils.helpers import paginate


def list_categories():
    pairs = category_service.list_categories_with_counts()
    pairs = paginate(pairs, request.args)
    return (
        jsonify(
            [category_schema.dump_with_task_count(c, count) for c, count in pairs]
        ),
        200,
    )


def create_category():
    fields = category_schema.validate_create(request.get_json(silent=True))
    category = category_service.create_category(fields)
    return jsonify(category_schema.dump(category)), 201


def update_category(cat_id):
    changes = category_schema.validate_update(request.get_json(silent=True))
    category = category_service.update_category(cat_id, changes)
    return jsonify(category_schema.dump(category)), 200


def delete_category(cat_id):
    category_service.delete_category(cat_id)
    return jsonify({"message": "Categoria deletada"}), 200
