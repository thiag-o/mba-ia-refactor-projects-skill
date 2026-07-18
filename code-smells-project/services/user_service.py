"""User business logic: registration (hashing) and authentication."""
import logging

from utils.exceptions import NotFoundError
from utils.security import hash_password, verify_password
from utils.serializers import serialize_login

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repository):
        self._repo = user_repository

    def list_users(self, limit, offset):
        return self._repo.list_all(limit, offset)

    def get_user(self, user_id):
        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
        return user

    def create_user(self, data):
        senha_hash = hash_password(data["senha"])
        user_id = self._repo.create(data["nome"], data["email"], senha_hash)
        logger.info("Usuário criado: %s", data["email"])
        return user_id

    def authenticate(self, email, senha):
        """Return a public login payload on success, otherwise None."""
        row = self._repo.get_by_email_raw(email)
        if row and verify_password(senha, row["senha"]):
            logger.info("Login bem-sucedido: %s", email)
            return serialize_login(row)
        logger.info("Login falhou: %s", email)
        return None
