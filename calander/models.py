"""Data models for the calendar project."""

from dataclasses import dataclass
from typing import Optional


EVENT_TYPE_EXACT = "exact"
EVENT_TYPE_WEEKLY = "weekly"
EVENT_TYPE_MONTHLY = "monthly"
EVENT_TYPE_YEARLY = "yearly"

VALID_EVENT_TYPES = {
    EVENT_TYPE_EXACT,
    EVENT_TYPE_WEEKLY,
    EVENT_TYPE_MONTHLY,
    EVENT_TYPE_YEARLY,
}


@dataclass
class Event:
    """Represents an event.

    Attributes:
        id: Unique event identifier.
        title: Event title.
        description: Event description.
        event_type: One of exact/weekly/monthly/yearly.
        exact_date: Jalali date in YYYY-MM-DD for exact events.
        weekday: Weekday index in range 0..6 for weekly events.
        day_of_month: Day number in range 1..31 for monthly events.
        month_of_year: Jalali month in range 1..12 for yearly events.
        day_of_year: Day number in month for yearly events.
    """

    id: int
    title: str
    description: str
    event_type: str
    exact_date: Optional[str] = None
    weekday: Optional[int] = None
    day_of_month: Optional[int] = None
    month_of_year: Optional[int] = None
    day_of_year: Optional[int] = None


@dataclass
class Task:
    """Represents a task with an exact date and completion state."""

    id: int
    title: str
    description: str
    due_date: str
    done: bool = False



class Birthday:
    def __init__(self, id, name, month, day, description=""):
        self.id = id
        self.name = name
        self.month = month
        self.day = day
        self.description = description
