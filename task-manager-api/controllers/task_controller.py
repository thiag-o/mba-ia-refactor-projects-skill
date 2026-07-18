"""Task controllers: orchestrate the request flow, no business/DB logic here."""
from flask import jsonify, request

from schemas import task_schema
from services import task_service
from utils.helpers import paginate


def list_tasks():
    tasks = task_service.list_tasks()
    tasks = paginate(tasks, request.args)
    return jsonify([task_schema.dump_with_details(t) for t in tasks]), 200


def get_task(task_id):
    task = task_service.get_task(task_id)
    return jsonify(task_schema.dump_with_overdue(task)), 200


def create_task():
    fields = task_schema.validate_create(request.get_json(silent=True))
    task = task_service.create_task(fields)
    return jsonify(task_schema.dump(task)), 201


def update_task(task_id):
    changes = task_schema.validate_update(request.get_json(silent=True))
    task = task_service.update_task(task_id, changes)
    return jsonify(task_schema.dump(task)), 200


def delete_task(task_id):
    task_service.delete_task(task_id)
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    tasks = task_service.search_tasks(
        query=request.args.get("q", ""),
        status=request.args.get("status", ""),
        priority=request.args.get("priority", ""),
        user_id=request.args.get("user_id", ""),
    )
    tasks = paginate(tasks, request.args)
    return jsonify([task_schema.dump(t) for t in tasks]), 200


def task_stats():
    return jsonify(task_service.get_stats()), 200
