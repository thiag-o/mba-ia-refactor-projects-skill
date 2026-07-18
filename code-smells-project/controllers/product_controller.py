"""HTTP orchestration for product endpoints. No SQL, no business math."""
from flask import jsonify, request

from utils.validators import parse_pagination, validate_product_payload


class ProductController:
    def __init__(self, product_service):
        self._service = product_service

    def list_products(self):
        limit, offset = parse_pagination(request.args)
        produtos = self._service.list_products(limit, offset)
        return jsonify({"dados": produtos, "sucesso": True}), 200

    def get_product(self, id):
        produto = self._service.get_product(id)
        return jsonify({"dados": produto, "sucesso": True}), 200

    def create_product(self):
        data = validate_product_payload(request.get_json(silent=True))
        product_id = self._service.create_product(data)
        return jsonify({
            "dados": {"id": product_id},
            "sucesso": True,
            "mensagem": "Produto criado",
        }), 201

    def update_product(self, id):
        data = validate_product_payload(request.get_json(silent=True))
        self._service.update_product(id, data)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def delete_product(self, id):
        self._service.delete_product(id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200

    def search_products(self):
        term = request.args.get("q", "")
        category = request.args.get("categoria", None)
        price_min = request.args.get("preco_min", None)
        price_max = request.args.get("preco_max", None)

        price_min = float(price_min) if price_min else None
        price_max = float(price_max) if price_max else None

        resultados = self._service.search_products(term, category, price_min, price_max)
        return jsonify({
            "dados": resultados,
            "total": len(resultados),
            "sucesso": True,
        }), 200
