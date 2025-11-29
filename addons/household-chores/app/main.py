"""
Home Assistant Chores Add-on - Main FastAPI Application
Handles task management, device management, and notification scheduling.
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.ha_client import HAClient
from app.models import (
    Device,
    DeviceCreateRequest,
    FrequencyType,
    Task,
    TaskCreateRequest,
    TaskPostponeRequest,
)
from app.scheduler import compute_next_due, get_current_time, get_notification_time, is_weekday
from app.storage import Storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Home Assistant Chores Add-on",
    description="Reminder system for household chores with notifications",
    version="1.0.0",
)

# Add CORS middleware for Home Assistant integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
storage: Storage = None
ha_client: HAClient = None
scheduler_task: asyncio.Task = None


class ActionRequest(BaseModel):
    """Request body for /ha/action endpoint."""
    action: str


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    ha_connected: bool = False


# ============================================================================
# Initialization and Cleanup
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global storage, ha_client, scheduler_task

    logger.info("Starting Home Assistant Chores Add-on...")

    # Initialize storage
    data_dir = os.getenv("DATA_DIR", "/data")
    storage = Storage(data_dir=data_dir)
    logger.info(f"Storage initialized at {data_dir}")

    # Initialize Home Assistant client
    # Get HA configuration from environment variables or use defaults
    ha_url = os.getenv("HA_URL", "http://localhost:8123")
    ha_token = os.getenv("HA_TOKEN", "")

    if not ha_token:
        logger.warning(
            "HA_TOKEN environment variable not set. "
            "Notifications will not work. "
            "Set HA_TOKEN to your Home Assistant long-lived access token."
        )

    ha_client = HAClient(ha_url=ha_url, ha_token=ha_token)

    # Test Home Assistant connection
    if ha_token:
        is_connected = await ha_client.check_connection()
        if is_connected:
            logger.info("Successfully connected to Home Assistant")
        else:
            logger.warning("Could not connect to Home Assistant")

    # Start the scheduler task
    scheduler_task = asyncio.create_task(scheduler_loop())
    logger.info("Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global scheduler_task
    logger.info("Shutting down Home Assistant Chores Add-on...")
    if scheduler_task:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass


# ============================================================================
# Scheduler Loop
# ============================================================================

async def scheduler_loop():
    """
    Main scheduler loop.
    Runs every minute and checks for tasks that need notifications.
    """
    logger.info("Scheduler loop started")
    last_notification_minute = -1

    while True:
        try:
            now = get_current_time()
            current_minute = now.minute

            # Only check once per minute
            if current_minute != last_notification_minute:
                last_notification_minute = current_minute

                # Get all tasks and check which ones are due
                tasks = storage.get_tasks()
                tasks_to_notify = []

                for task in tasks:
                    # Check if task is due and it's the right time to notify
                    if task.next_due <= now:
                        # Check if it's the correct notification time
                        notification_hour = 16 if is_weekday(now) else 8
                        if now.hour == notification_hour and now.minute < 5:
                            tasks_to_notify.append(task)

                # Send notifications for due tasks
                for task in tasks_to_notify:
                    await send_task_notification(task)

            # Sleep for 30 seconds before checking again
            await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}", exc_info=True)
            await asyncio.sleep(30)


async def send_task_notification(task: Task) -> None:
    """
    Send a notification for a task to all assigned devices.

    Args:
        task: The task to notify about
    """
    if not task.assigned_to:
        logger.warning(f"Task {task.id} has no assigned devices")
        return

    devices = storage.get_devices()
    device_map = {d.id: d for d in devices}

    actions = [
        {"action": f"TASK_DONE_{task.id}", "title": "Done"},
        {"action": f"TASK_POSTPONE_{task.id}", "title": "Postpone"},
    ]

    for device_id in task.assigned_to:
        device = device_map.get(device_id)
        if not device:
            logger.warning(f"Device {device_id} not found")
            continue

        # Send notification
        success = await ha_client.send_notification(
            notify_service=device.notify_service,
            title="Household Chore Reminder",
            message=f"Time to: {task.name}",
            actions=actions,
            data={"task_id": task.id},
        )

        if success:
            logger.info(f"Notification sent for task {task.id} to device {device_id}")
        else:
            logger.error(f"Failed to send notification for task {task.id} to device {device_id}")


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint."""
    ha_connected = await ha_client.check_connection() if ha_client else False
    return HealthCheckResponse(
        status="ok",
        ha_connected=ha_connected,
    )


# ============================================================================
# Task Endpoints
# ============================================================================

@app.get("/tasks", response_model=List[Task])
async def list_tasks() -> List[Task]:
    """List all tasks."""
    return storage.get_tasks()


@app.post("/tasks", response_model=Task)
async def create_task(request: TaskCreateRequest) -> Task:
    """
    Create a new task.

    Example:
        {
            "name": "Vacuum the house",
            "frequency": "weekly",
            "assigned_to": ["johan_phone", "anna_phone"]
        }
    """
    from uuid import uuid4

    task_id = str(uuid4())[:8]
    now = get_current_time()

    # Calculate next_due: if not provided, set to next notification time
    # For a new task, assume it's being created just after being "done"
    next_due = compute_next_due(request.frequency, now)

    task = Task(
        id=task_id,
        name=request.name,
        frequency=request.frequency,
        last_done=now,
        next_due=next_due,
        assigned_to=request.assigned_to,
    )

    storage.save_task(task)
    logger.info(f"Created task {task.id}: {task.name}")
    return task


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str) -> Task:
    """Get a specific task by ID."""
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, request: TaskCreateRequest) -> Task:
    """Update a task (partially)."""
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Update fields
    task.name = request.name
    task.frequency = request.frequency
    task.assigned_to = request.assigned_to

    storage.save_task(task)
    logger.info(f"Updated task {task.id}: {task.name}")
    return task


@app.post("/tasks/{task_id}/done", response_model=Task)
async def mark_task_done(task_id: str) -> Task:
    """
    Mark a task as done and recalculate next_due.

    This is called when the user taps "Done" on the notification.
    """
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    now = get_current_time()
    task.last_done = now
    task.next_due = compute_next_due(task.frequency, now)

    storage.save_task(task)
    logger.info(f"Task {task_id} marked as done. Next due: {task.next_due}")
    return task


@app.post("/tasks/{task_id}/postpone", response_model=Task)
async def postpone_task(task_id: str, request: TaskPostponeRequest) -> Task:
    """
    Postpone a task to a new due date.

    Example:
        {
            "next_due": "2024-12-05T16:00:00"
        }
    """
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task.next_due = request.next_due

    storage.save_task(task)
    logger.info(f"Task {task_id} postponed. New due: {task.next_due}")
    return task


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str) -> dict:
    """Delete a task."""
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    storage.delete_task(task_id)
    logger.info(f"Task {task_id} deleted")
    return {"message": f"Task {task_id} deleted"}


# ============================================================================
# Device Endpoints
# ============================================================================

@app.get("/devices", response_model=List[Device])
async def list_devices() -> List[Device]:
    """List all devices."""
    return storage.get_devices()


@app.post("/devices", response_model=Device)
async def create_device(request: DeviceCreateRequest) -> Device:
    """
    Create a new device (phone).

    Example:
        {
            "id": "johan_phone",
            "notify_service": "notify.mobile_app_johans_iphone"
        }
    """
    # Check if device already exists
    existing = storage.get_device(request.id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Device {request.id} already exists")

    device = Device(id=request.id, notify_service=request.notify_service)
    storage.save_device(device)
    logger.info(f"Created device {device.id}")
    return device


@app.get("/devices/{device_id}", response_model=Device)
async def get_device(device_id: str) -> Device:
    """Get a specific device by ID."""
    device = storage.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return device


@app.put("/devices/{device_id}", response_model=Device)
async def update_device(device_id: str, request: DeviceCreateRequest) -> Device:
    """Update a device."""
    device = storage.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    device.notify_service = request.notify_service
    storage.save_device(device)
    logger.info(f"Updated device {device_id}")
    return device


@app.delete("/devices/{device_id}")
async def delete_device(device_id: str) -> dict:
    """Delete a device."""
    device = storage.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    storage.delete_device(device_id)
    logger.info(f"Device {device_id} deleted")
    return {"message": f"Device {device_id} deleted"}


# ============================================================================
# Home Assistant Integration Endpoint
# ============================================================================

@app.post("/ha/action")
async def handle_ha_action(request: ActionRequest) -> dict:
    """
    Handle notification action from Home Assistant.

    This endpoint is called by a Home Assistant automation that listens for
    'mobile_app_notification_action' events.

    The action string should be formatted as:
    - TASK_DONE_<task_id>
    - TASK_POSTPONE_<task_id>_<new_due_date>

    Example action: "TASK_DONE_abc123"
    """
    action = request.action

    try:
        if action.startswith("TASK_DONE_"):
            task_id = action.replace("TASK_DONE_", "")
            task = await mark_task_done(task_id)
            return {
                "status": "ok",
                "action": "task_done",
                "task_id": task_id,
                "next_due": task.next_due.isoformat(),
            }

        elif action.startswith("TASK_POSTPONE_"):
            # Format: TASK_POSTPONE_<task_id>
            # The actual postpone datetime comes from a follow-up request
            # For now, we implement a default postpone (+ 1 day at notification time)
            task_id = action.replace("TASK_POSTPONE_", "")
            task = storage.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

            now = get_current_time()
            new_due = get_notification_time(now + __import__("datetime").timedelta(days=1))
            task.next_due = new_due
            storage.save_task(task)

            logger.info(f"Task {task_id} postponed to {new_due}")
            return {
                "status": "ok",
                "action": "task_postponed",
                "task_id": task_id,
                "new_due": new_due.isoformat(),
            }

        else:
            logger.warning(f"Unknown action: {action}")
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling action {action}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": "Home Assistant Chores Add-on",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn
    # Configuration can be customized via environment variables
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )
