"""
Scheduler for tasks and notifications.
Handles computing next_due dates and triggering notifications.
"""
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.models import FrequencyType, Task

logger = logging.getLogger(__name__)

# Timezone for scheduling (Europe/Stockholm - CET/CEST)
TZ = ZoneInfo("Europe/Stockholm")

# Notification times
WEEKDAY_NOTIFICATION_HOUR = 16  # 16:00 on weekdays
WEEKEND_NOTIFICATION_HOUR = 8   # 08:00 on weekends


def get_current_time() -> datetime:
    """Get current time in the configured timezone."""
    return datetime.now(tz=TZ)


def is_weekday(dt: datetime) -> bool:
    """Check if a datetime is a weekday (Monday=0, Sunday=6)."""
    return dt.weekday() < 5


def get_notification_time(dt: datetime) -> datetime:
    """
    Get the notification time for a given date.
    If weekday: return time at 16:00.
    If weekend: return time at 08:00.
    """
    hour = WEEKDAY_NOTIFICATION_HOUR if is_weekday(dt) else WEEKEND_NOTIFICATION_HOUR
    return dt.replace(hour=hour, minute=0, second=0, microsecond=0)


def compute_next_due(frequency: FrequencyType, last_done: datetime) -> datetime:
    """
    Compute the next due date for a task based on frequency.

    Args:
        frequency: The task frequency (daily, weekly, etc.)
        last_done: When the task was last completed

    Returns:
        The next due datetime, adjusted to the correct notification time
    """
    if frequency == FrequencyType.DAILY:
        next_date = last_done + timedelta(days=1)
    elif frequency == FrequencyType.WEEKLY:
        next_date = last_done + timedelta(weeks=1)
    elif frequency == FrequencyType.MONTHLY:
        # Add months by calculating year and month
        year = last_done.year
        month = last_done.month + 1
        if month > 12:
            month = 1
            year += 1
        # Handle day overflow (e.g., Jan 31 + 1 month)
        try:
            next_date = last_done.replace(year=year, month=month)
        except ValueError:
            # If the day doesn't exist in the target month, use last day of month
            next_date = last_done.replace(year=year, month=month, day=1) - timedelta(days=1)
    elif frequency == FrequencyType.QUARTERLY:
        # Add 3 months
        year = last_done.year
        month = last_done.month + 3
        if month > 12:
            month -= 12
            year += 1
        try:
            next_date = last_done.replace(year=year, month=month)
        except ValueError:
            next_date = last_done.replace(year=year, month=month, day=1) - timedelta(days=1)
    elif frequency == FrequencyType.YEARLY:
        next_date = last_done.replace(year=last_done.year + 1)
    else:
        raise ValueError(f"Unknown frequency: {frequency}")

    # Adjust time of day based on weekday/weekend
    notification_time = get_notification_time(next_date)
    return notification_time


def should_notify_now(task: Task) -> bool:
    """
    Check if we should send a notification for this task right now.

    Returns:
        True if next_due <= now and it's the correct notification time, False otherwise
    """
    now = get_current_time()

    # Task is due if next_due is in the past or now
    is_due = task.next_due <= now

    if not is_due:
        return False

    # Check if it's approximately the correct notification time
    # Allow a 5-minute window to avoid sending multiple notifications
    notification_hour = WEEKDAY_NOTIFICATION_HOUR if is_weekday(now) else WEEKEND_NOTIFICATION_HOUR
    current_hour = now.hour
    current_minute = now.minute

    # We notify if we're within the notification hour and first few minutes
    is_notification_time = (current_hour == notification_hour and current_minute < 5)

    return is_notification_time


def get_tasks_due_for_notification() -> list:
    """
    Get list of task IDs that should receive notifications now.
    (To be called by the scheduler loop)
    """
    # This will be implemented in the scheduler loop in main.py
    # It will query the storage and return tasks that need notifications
    pass
