"""Named domain constants (no magic numbers scattered across the code)."""

# Product domain
VALID_CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
DEFAULT_CATEGORY = "geral"
NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 200

# Order domain
VALID_ORDER_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
INITIAL_ORDER_STATUS = "pendente"

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# Sales report discount tiers: (revenue threshold, discount rate), highest first.
DISCOUNT_TIERS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]
