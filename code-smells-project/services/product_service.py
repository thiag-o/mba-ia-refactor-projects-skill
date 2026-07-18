"""Product business logic."""
import logging

from utils.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, product_repository):
        self._repo = product_repository

    def list_products(self, limit, offset):
        return self._repo.list_all(limit, offset)

    def get_product(self, product_id):
        product = self._repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Produto não encontrado")
        return product

    def create_product(self, data):
        product_id = self._repo.create(
            data["nome"], data["descricao"], data["preco"],
            data["estoque"], data["categoria"],
        )
        logger.info("Produto criado com ID %s", product_id)
        return product_id

    def update_product(self, product_id, data):
        if not self._repo.get_by_id(product_id):
            raise NotFoundError("Produto não encontrado")
        self._repo.update(
            product_id, data["nome"], data["descricao"], data["preco"],
            data["estoque"], data["categoria"],
        )
        return True

    def delete_product(self, product_id):
        if not self._repo.get_by_id(product_id):
            raise NotFoundError("Produto não encontrado")
        self._repo.delete(product_id)
        logger.info("Produto %s deletado", product_id)
        return True

    def search_products(self, term, category, price_min, price_max):
        return self._repo.search(term, category, price_min, price_max)
