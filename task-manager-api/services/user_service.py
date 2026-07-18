"""User business logic: registration, updates, auth and related tasks."""
from sqlalchemy.exc import SQLAlchemyError

from errors import ApiError
from models.user import User
from repositories import task_repository, user_repository
from services import auth_service
from utils.logger import get_logger

logger = get_logger(__name__)


def list_users():
    return user_repository.list_all()


def get_user(user_id):
    user = user_repository.get_by_id(user_id)
    if not user:
        raise ApiError("Usuário não encontrado", 404)
    return user


def get_user_tasks(user_id):
    get_user(user_id)  # raises 404 if missing
    return task_repository.list_by_user(user_id)


def create_user(fields):
    if user_repository.get_by_email(fields["email"]):
        raise ApiError("Email já cadastrado", 409)

    user = User()
    user.name = fields["name"]
    user.email = fields["email"]
    user.set_password(fields["password"])
    user.role = fields["role"]

    try:
        user_repository.add(user)
        user_repository.commit()
    except SQLAlchemyError as exc:
        user_repository.rollback()
        logger.error("Failed to create user: %s", exc)
        raise ApiError("Erro ao criar usuário", 500)

    logger.info("User created: %s - %s", user.id, user.name)
    return user


def update_user(user_id, changes):
    user = user_repository.get_by_id(user_id)
    if not user:
        raise ApiError("Usuário não encontrado", 404)

    if "email" in changes:
        existing = user_repository.get_by_email(changes["email"])
        if existing and existing.id != user_id:
            raise ApiError("Email já cadastrado", 409)
        user.email = changes["email"]
    if "name" in changes:
        user.name = changes["name"]
    if "password" in changes:
        user.set_password(changes["password"])
    if "role" in changes:
        user.role = changes["role"]
    if "active" in changes:
        user.active = changes["active"]

    try:
        user_repository.commit()
    except SQLAlchemyError as exc:
        user_repository.rollback()
        logger.error("Failed to update user %s: %s", user_id, exc)
        raise ApiError("Erro ao atualizar", 500)

    return user


def delete_user(user_id):
    user = user_repository.get_by_id(user_id)
    if not user:
        raise ApiError("Usuário não encontrado", 404)

    tasks = task_repository.list_by_user(user_id)
    try:
        for task in tasks:
            task_repository.delete(task)
        user_repository.delete(user)
        user_repository.commit()
    except SQLAlchemyError as exc:
        user_repository.rollback()
        logger.error("Failed to delete user %s: %s", user_id, exc)
        raise ApiError("Erro ao deletar", 500)

    logger.info("User deleted: %s", user_id)


def authenticate(email, password):
    """Validate credentials and return (user, token)."""
    user = user_repository.get_by_email(email)
    if not user or not user.check_password(password):
        raise ApiError("Credenciais inválidas", 401)
    if not user.active:
        raise ApiError("Usuário inativo", 403)

    token = auth_service.generate_token(user)
    return user, token
