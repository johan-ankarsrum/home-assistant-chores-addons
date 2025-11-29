"""
Storage layer for tasks and devices using JSON files.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.models import Device, Task


class Storage:
    """Handle persistent storage of tasks and devices using JSON files."""

    def __init__(self, data_dir: str = "/data"):
        """Initialize storage with a data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.data_dir / "tasks.json"
        self.devices_file = self.data_dir / "devices.json"

        # Initialize files if they don't exist
        if not self.tasks_file.exists():
            self._write_tasks([])
        if not self.devices_file.exists():
            self._write_devices([])

    def _read_file(self, filepath: Path) -> dict:
        """Read JSON file safely."""
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_file(self, filepath: Path, data: dict) -> None:
        """Write JSON file safely."""
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _read_tasks(self) -> list:
        """Read tasks from file."""
        data = self._read_file(self.tasks_file)
        return data.get("tasks", [])

    def _write_tasks(self, tasks: list) -> None:
        """Write tasks to file."""
        self._write_file(self.tasks_file, {"tasks": tasks})

    def _read_devices(self) -> list:
        """Read devices from file."""
        data = self._read_file(self.devices_file)
        return data.get("devices", [])

    def _write_devices(self, devices: list) -> None:
        """Write devices to file."""
        self._write_file(self.devices_file, {"devices": devices})

    def get_tasks(self) -> List[Task]:
        """Get all tasks."""
        tasks_data = self._read_tasks()
        return [
            Task(
                id=t["id"],
                name=t["name"],
                frequency=t["frequency"],
                last_done=datetime.fromisoformat(t["last_done"]),
                next_due=datetime.fromisoformat(t["next_due"]),
                assigned_to=t.get("assigned_to", []),
            )
            for t in tasks_data
        ]

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a specific task by ID."""
        tasks = self.get_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def save_task(self, task: Task) -> None:
        """Save a task (create or update)."""
        tasks = self.get_tasks()
        # Remove existing task with same ID if it exists
        tasks = [t for t in tasks if t.id != task.id]
        # Add the new/updated task
        tasks.append(task)
        tasks_data = [
            {
                "id": t.id,
                "name": t.name,
                "frequency": t.frequency,
                "last_done": t.last_done.isoformat(),
                "next_due": t.next_due.isoformat(),
                "assigned_to": t.assigned_to,
            }
            for t in tasks
        ]
        self._write_tasks(tasks_data)

    def delete_task(self, task_id: str) -> None:
        """Delete a task by ID."""
        tasks = self.get_tasks()
        tasks = [t for t in tasks if t.id != task_id]
        tasks_data = [
            {
                "id": t.id,
                "name": t.name,
                "frequency": t.frequency,
                "last_done": t.last_done.isoformat(),
                "next_due": t.next_due.isoformat(),
                "assigned_to": t.assigned_to,
            }
            for t in tasks
        ]
        self._write_tasks(tasks_data)

    def get_devices(self) -> List[Device]:
        """Get all devices."""
        devices_data = self._read_devices()
        return [Device(id=d["id"], notify_service=d["notify_service"]) for d in devices_data]

    def get_device(self, device_id: str) -> Optional[Device]:
        """Get a specific device by ID."""
        devices = self.get_devices()
        for device in devices:
            if device.id == device_id:
                return device
        return None

    def save_device(self, device: Device) -> None:
        """Save a device (create or update)."""
        devices = self.get_devices()
        # Remove existing device with same ID if it exists
        devices = [d for d in devices if d.id != device.id]
        # Add the new/updated device
        devices.append(device)
        devices_data = [
            {"id": d.id, "notify_service": d.notify_service} for d in devices
        ]
        self._write_devices(devices_data)

    def delete_device(self, device_id: str) -> None:
        """Delete a device by ID."""
        devices = self.get_devices()
        devices = [d for d in devices if d.id != device_id]
        devices_data = [
            {"id": d.id, "notify_service": d.notify_service} for d in devices
        ]
        self._write_devices(devices_data)
