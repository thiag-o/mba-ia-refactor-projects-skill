"""Reporting/aggregation business logic (moved out of the controllers)."""
from datetime import timedelta

from config.constants import (
    CLOSED_STATUSES,
    HIGH_PRIORITY_THRESHOLD,
    RECENT_ACTIVITY_DAYS,
)
from errors import ApiError
from repositories import category_repository, task_repository, user_repository
from utils.helpers import calculate_percentage, now_utc


def summary_report():
    tasks = task_repository.list_all()
    users = user_repository.list_all()
    total_categories = len(category_repository.list_all())
    now = now_utc()
    window_start = now - timedelta(days=RECENT_ACTIVITY_DAYS)

    status_counts = {"pending": 0, "in_progress": 0, "done": 0, "cancelled": 0}
    priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    overdue_list = []
    recent_created = 0
    recent_done = 0
    per_user = {u.id: {"name": u.name, "total": 0, "completed": 0} for u in users}

    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        if task.priority in priority_counts:
            priority_counts[task.priority] += 1

        if task.is_overdue():
            overdue_list.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "due_date": str(task.due_date),
                    "days_overdue": (now - task.due_date).days,
                }
            )

        if task.created_at and task.created_at >= window_start:
            recent_created += 1
        if task.status == "done" and task.updated_at and task.updated_at >= window_start:
            recent_done += 1

        if task.user_id in per_user:
            per_user[task.user_id]["total"] += 1
            if task.status == "done":
                per_user[task.user_id]["completed"] += 1

    user_stats = [
        {
            "user_id": user.id,
            "user_name": per_user[user.id]["name"],
            "total_tasks": per_user[user.id]["total"],
            "completed_tasks": per_user[user.id]["completed"],
            "completion_rate": calculate_percentage(
                per_user[user.id]["completed"], per_user[user.id]["total"]
            ),
        }
        for user in users
    ]

    return {
        "generated_at": str(now),
        "overview": {
            "total_tasks": len(tasks),
            "total_users": len(users),
            "total_categories": total_categories,
        },
        "tasks_by_status": {
            "pending": status_counts["pending"],
            "in_progress": status_counts["in_progress"],
            "done": status_counts["done"],
            "cancelled": status_counts["cancelled"],
        },
        "tasks_by_priority": {
            "critical": priority_counts[1],
            "high": priority_counts[2],
            "medium": priority_counts[3],
            "low": priority_counts[4],
            "minimal": priority_counts[5],
        },
        "overdue": {"count": len(overdue_list), "tasks": overdue_list},
        "recent_activity": {
            "tasks_created_last_7_days": recent_created,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }


def user_report(user_id):
    user = user_repository.get_by_id(user_id)
    if not user:
        raise ApiError("Usuário não encontrado", 404)

    tasks = task_repository.list_by_user(user_id)
    counts = {"done": 0, "pending": 0, "in_progress": 0, "cancelled": 0}
    overdue = 0
    high_priority = 0

    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1
        if task.priority <= HIGH_PRIORITY_THRESHOLD:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    total = len(tasks)
    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": counts["done"],
            "pending": counts["pending"],
            "in_progress": counts["in_progress"],
            "cancelled": counts["cancelled"],
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": calculate_percentage(counts["done"], total),
        },
    }
