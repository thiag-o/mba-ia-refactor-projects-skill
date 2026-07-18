"""Password hashing helpers (bcrypt with per-password salt)."""
import bcrypt


def hash_password(plaintext):
    """Hash a plaintext password with a freshly generated salt."""
    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plaintext, hashed):
    """Constant-time verification of a plaintext password against its hash."""
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        # Stored value is not a valid bcrypt hash.
        return False
