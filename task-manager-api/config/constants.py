"""Domain constants shared across layers (replaces scattered magic numbers)."""

VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]

# Statuses that make an overdue task no longer count as overdue.
CLOSED_STATUSES = ["done", "cancelled"]

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200

MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3

MIN_PASSWORD_LENGTH = 4

DEFAULT_COLOR = "#000000"

# High priority threshold used by reports (priority 1-2).
HIGH_PRIORITY_THRESHOLD = 2

# Rolling window (days) used by the summary report's recent-activity section.
RECENT_ACTIVITY_DAYS = 7

# Default page size when a client opts into pagination via ?page/?per_page.
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
