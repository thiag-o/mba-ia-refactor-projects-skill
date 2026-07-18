"""Persistence access for tasks. The only place that touches the ORM session."""
from sqlalchemy.orm import joinedload

from database import db
from models.task import Task


def _base_query():
    # Eager-load user and category to avoid N+1 queries during serialization.
    return Task.query.options(joinedload(Task.user), joinedload(Task.category))


def list_all():
    return _base_query().all()

def get_by_id(task_id):
    return db.session.get(Task, task_id)

def get_by_id_with_relations(task_id):
    return _base_query().filter(Task.id == task_id).first()

def list_by_user(user_id):
    return _base_query().filter(Task.user_id == user_id).all()

def search(query=None, status=None, priority=None, user_id=None):
    q = _base_query()
    if query:
        q = q.filter(
            db.or_(Task.title.like(f"%{query}%"), Task.description.like(f"%{query}%"))
        )
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == int(priority))
    if user_id:
        q = q.filter(Task.user_id == int(user_id))
    return q.all()

def add(task):
    db.session.add(task)

def delete(task):
    db.session.delete(task)

def commit():
    db.session.commit()

def rollback():
    db.session.rollback()
