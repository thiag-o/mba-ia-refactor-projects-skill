"""Small, reusable helpers shared across the application."""
from datetime import datetime, timezone


def now_utc():
    """Return the current UTC time as a naive datetime.

    The database stores naive datetimes, so we drop the tzinfo after building a
    timezone-aware value with ``datetime.now(timezone.utc)`` (the modern
    replacement for the deprecated ``datetime.utcnow()``). This keeps
    comparisons against stored columns consistent.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    """Serialize a datetime (or None) to a string."""
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    """Return part/total as a rounded percentage, guarding against div-by-zero."""
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def paginate(items, args):
    """Opt-in pagination that preserves the plain-list response shape.

    When neither ``page`` nor ``per_page`` is present in the query string the
    full list is returned unchanged (backward compatible). Otherwise a
    limit/offset slice is applied.
    """
    from config.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

    if "page" not in args and "per_page" not in args:
        return items

    try:
        page = max(int(args.get("page", 1)), 1)
    except (ValueError, TypeError):
        page = 1
    try:
        per_page = int(args.get("per_page", DEFAULT_PAGE_SIZE))
    except (ValueError, TypeError):
        per_page = DEFAULT_PAGE_SIZE
    per_page = max(1, min(per_page, MAX_PAGE_SIZE))

    start = (page - 1) * per_page
    return items[start:start + per_page]
