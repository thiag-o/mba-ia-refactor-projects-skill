"""Persistence access for categories."""
from database import db
from models.category import Category


def list_all():
    return Category.query.all()

def get_by_id(category_id):
    return db.session.get(Category, category_id)

def add(category):
    db.session.add(category)

def delete(category):
    db.session.delete(category)

def commit():
    db.session.commit()

def rollback():
    db.session.rollback()
