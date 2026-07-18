"""Environment-driven application configuration.

Every secret, flag and connection string is read from environment variables so
that no sensitive value is ever hardcoded in the source tree. Sensible,
non-secret defaults keep local development and the validation flow working out
of the box. Copy ``.env.example`` to ``.env`` to override values locally.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Config:
    """Base configuration populated from the environment."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Never commit a real secret. Override via the SECRET_KEY env var in prod.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret-change-me")

    DEBUG = _as_bool(os.environ.get("FLASK_DEBUG"), default=False)

    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    # Comma-separated list of allowed CORS origins, or "*" to allow any.
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # Lifetime (seconds) of the signed auth token issued by /login.
    TOKEN_MAX_AGE = int(os.environ.get("TOKEN_MAX_AGE", "86400"))

    @staticmethod
    def cors_origins():
        raw = Config.CORS_ORIGINS
        if raw.strip() == "*":
            return "*"
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
