"""Persistence access for users."""
from database import db
from models.user import User


def list_all():
    return User.query.all()

def get_by_id(user_id):
    return db.session.get(User, user_id)

def get_by_email(email):
    return User.query.filter_by(email=email).first()

def add(user):
    db.session.add(user)

def delete(user):
    db.session.delete(user)

def commit():
    db.session.commit()

def rollback():
    db.session.rollback()
