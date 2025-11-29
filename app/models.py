"""
Data models for the Household Chores add-on.
"""
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class FrequencyType(str, Enum):
    """Supported task frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Task(BaseModel):
    """Task model representing a household chore."""
    id: str = Field(..., description="Unique identifier for the task")
    name: str = Field(..., description="Human-readable task name")
    frequency: FrequencyType = Field(..., description="How often the task repeats")
    last_done: datetime = Field(..., description="When the task was last completed")
    next_due: datetime = Field(..., description="When the task is next due")
    assigned_to: List[str] = Field(default_factory=list, description="List of device IDs to notify")


class TaskCreateRequest(BaseModel):
    """Request body for creating a new task."""
    name: str
    frequency: FrequencyType
    assigned_to: List[str] = Field(default_factory=list)
    # Optional: if not provided, next_due will be calculated based on current time


class TaskPostponeRequest(BaseModel):
    """Request body for postponing a task."""
    next_due: datetime


class Device(BaseModel):
    """Device model representing a phone."""
    id: str = Field(..., description="Unique identifier for the device (e.g. 'johan_phone')")
    notify_service: str = Field(..., description="Home Assistant notify service (e.g. 'notify.mobile_app_johans_iphone')")


class DeviceCreateRequest(BaseModel):
    """Request body for creating a new device."""
    id: str
    notify_service: str
