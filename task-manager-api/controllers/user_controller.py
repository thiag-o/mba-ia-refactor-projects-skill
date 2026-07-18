"""User controllers."""
from flask import jsonify, request

from middlewares.auth import assert_admin
from schemas import task_schema, user_schema
from services import user_service
from utils.helpers import paginate


def list_users():
    users = user_service.list_users()
    users = paginate(users, request.args)
    return jsonify([user_schema.dump_with_task_count(u) for u in users]), 200


def get_user(user_id):
    user = user_service.get_user(user_id)
    data = user_schema.dump(user)
    tasks = user_service.get_user_tasks(user_id)
    data["tasks"] = [task_schema.dump(t) for t in tasks]
    return jsonify(data), 200


def create_user():
    fields = user_schema.validate_create(request.get_json(silent=True))
    user = user_service.create_user(fields)
    return jsonify(user_schema.dump(user)), 201


def update_user(user_id):
    changes = user_schema.validate_update(request.get_json(silent=True))
    # Privilege escalation (role change) requires an admin token.
    if "role" in changes:
        assert_admin()
    user = user_service.update_user(user_id, changes)
    return jsonify(user_schema.dump(user)), 200


def delete_user(user_id):
    user_service.delete_user(user_id)
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id):
    tasks = user_service.get_user_tasks(user_id)
    return jsonify([task_schema.dump_summary(t) for t in tasks]), 200
