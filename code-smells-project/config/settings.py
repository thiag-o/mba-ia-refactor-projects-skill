"""Application configuration sourced exclusively from environment variables.

No secrets are hardcoded. Local-dev placeholder defaults keep the app bootable
without a configured environment, but production must supply real values.
"""
import os

# Secret key: read from the environment, with a non-production placeholder.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

# Debug flag driven by the environment (defaults to off / production-safe).
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# SQLite database file path.
DB_PATH = os.environ.get("DB_PATH", "loja.db")

# Token required to call guarded admin endpoints.
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "local-dev-admin-token")

# Reported environment name (diagnostic only).
ENVIRONMENT = os.environ.get("ENVIRONMENT", "producao")

# Public API version string.
APP_VERSION = "1.0.0"

# Restrict CORS to a configured allow-list instead of a wildcard.
_raw_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:5000")
CORS_ORIGINS = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]
