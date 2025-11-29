# Architecture & Implementation Details

## Overview

The Household Chores Reminder is a standalone Docker-based service that integrates with Home Assistant via its REST API. It follows a modular, clean architecture with clear separation of concerns.

```
┌─────────────────────────────────────────────────────────────┐
│                    Home Assistant                            │
│  (Handles notifications, mobile app integration)            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─ Calls REST API
                 └─ Listens for mobile_app_notification_action
                 
┌─────────────────────────────────────────────────────────────┐
│         Household Chores Add-on (Docker Container)           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Application (main.py)                       │  │
│  │  ├─ REST API Endpoints (Tasks, Devices, Actions)    │  │
│  │  ├─ Request/Response Handling                        │  │
│  │  └─ Integration with other modules                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │ Storage     │ │ Scheduler    │ │ HA Client    │         │
│  │ (JSON)      │ │ (Logic)      │ │ (API Calls)  │         │
│  └─────────────┘ └──────────────┘ └──────────────┘         │
│       │               │                   │                 │
│       ├─ Models       ├─ next_due calc    ├─ httpx         │
│       └─ I/O          └─ Notification     └─ Bearer Auth   │
│                          Timing                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Layer                                          │  │
│  │  ├─ tasks.json (persistent storage)                 │  │
│  │  └─ devices.json (persistent storage)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Module Breakdown

### `models.py` - Data Models

Defines Pydantic models for type-safe data handling:

- **`FrequencyType`**: Enum for task frequencies
- **`Task`**: Core task model with validation
- **`TaskCreateRequest`**: Input validation for task creation
- **`Device`**: Phone/notification device model
- **`DeviceCreateRequest`**: Input validation for device creation

**Why Pydantic?**
- Automatic validation of input data
- Type hints for IDE support
- JSON serialization/deserialization
- Clear API contracts

### `storage.py` - Persistence Layer

Handles reading/writing tasks and devices to JSON files.

**Key Design Decisions:**
- **JSON over SQLite**: For a small-scale home application, JSON is simpler to implement and deploy without external dependencies
- **File-based**: Compatible with Docker volume mounts
- **Single responsibility**: Storage logic isolated from business logic

**Methods:**
- `get_tasks()` / `get_task(id)`: Read operations
- `save_task(task)`: Create or update
- `delete_task(id)`: Remove task
- Similar methods for devices

**Future Extension:** Can be swapped with SQLite implementation without changing the API.

### `scheduler.py` - Scheduling Logic

Core business logic for task scheduling and notification timing.

**Key Functions:**

1. **`compute_next_due(frequency, last_done)`**
   - Calculates the next due date based on frequency
   - Handles month/year boundaries correctly
   - Adjusts time to notification schedule (16:00 weekday, 08:00 weekend)

2. **`is_weekday(dt)`**
   - Returns True for Monday-Friday
   - Used for notification time selection

3. **`get_notification_time(dt)`**
   - Returns the correct notification time for a given date
   - Ensures consistent timing across the system

4. **`should_notify_now(task)`**
   - Determines if we should send a notification right now
   - Checks both due date and correct time window

**Timezone Handling:**
- Uses Python 3.9+ `zoneinfo` module (no third-party dependency)
- Currently set to Europe/Stockholm
- Change `TZ` variable to switch timezones

### `ha_client.py` - Home Assistant Integration

Async HTTP client for calling Home Assistant REST API.

**Methods:**

1. **`send_notification()`**
   - Calls Home Assistant `notify.<service>` endpoint
   - Supports action buttons and custom data
   - Returns success/failure status
   - Async for non-blocking I/O

2. **`check_connection()`**
   - Verifies connection to Home Assistant
   - Used for health checks and startup validation

**Error Handling:**
- Network errors logged and handled gracefully
- Notifications continue even if one fails
- No exception propagation that would crash the scheduler

### `main.py` - FastAPI Application

Main application with all REST endpoints and scheduler loop.

**Components:**

1. **Startup/Shutdown**
   - `startup_event()`: Initializes storage, HA client, and scheduler
   - `shutdown_event()`: Gracefully stops scheduler

2. **Scheduler Loop**
   - Runs continuously in background task
   - Checks every 30 seconds
   - Sends notifications at correct times
   - Handles timezone and weekday logic

3. **API Endpoints**
   - `/tasks` - CRUD operations
   - `/devices` - CRUD operations
   - `/ha/action` - Webhook for notification actions
   - `/health` - Health check
   - `/docs` - Auto-generated API documentation

4. **Notification Handler**
   - `send_task_notification()`: Sends to all assigned devices
   - Handles device lookup
   - Formats action buttons with task ID

## Data Flow Diagrams

### Task Creation Flow

```
POST /tasks (name, frequency, assigned_to)
    │
    ├─→ Generate unique task ID
    ├─→ Set last_done = now
    ├─→ Compute next_due using scheduler.compute_next_due()
    └─→ Save to storage (tasks.json)
         │
         └─→ Response: 200 OK with Task object
```

### Notification Flow

```
Scheduler Loop (every 30 sec)
    │
    ├─→ Get all tasks from storage
    ├─→ For each task:
    │   ├─→ Check if next_due <= now
    │   ├─→ Check if it's correct notification time
    │   └─→ If both true:
    │       ├─→ Get assigned devices
    │       ├─→ For each device:
    │       │   └─→ Call HA notify service via ha_client
    │       │       (includes "Done" and "Postpone" buttons)
    │       └─→ Log result
    │
    └─→ Sleep 30 seconds, repeat
```

### Notification Action Flow

```
User taps "Done" on notification
    │
    └─→ HA fires mobile_app_notification_action event
         │
         └─→ Automation routes to rest_command.chores_notification_action
             │
             └─→ POST /ha/action {action: "TASK_DONE_abc123"}
                  │
                  ├─→ Parse action string
                  ├─→ Mark task as done
                  ├─→ Compute new next_due
                  ├─→ Save to storage
                  └─→ Response: {status: "ok", next_due: ...}
```

## Time Handling

### Timezone Setup

```python
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Stockholm")  # Change this for different timezone
now = datetime.now(tz=TZ)
```

**Why `zoneinfo`?**
- Built into Python 3.9+
- Handles DST transitions automatically
- Standard library (no dependencies)

### Notification Scheduling

| Day | Time |
|-----|------|
| Mon-Fri | 16:00 (4 PM) |
| Sat-Sun | 08:00 (8 AM) |

**Adjustment Logic:**
When task is marked done, `next_due` is calculated as:
1. Add interval (1 day, 1 week, etc.)
2. Check if result is weekday or weekend
3. Set time accordingly

Example: Weekly task marked done on Friday at 14:30
1. Add 1 week → next Friday
2. Friday is weekday → set to 16:00
3. `next_due = Friday 16:00`

## Error Handling Strategy

### Graceful Degradation

```
HA Connection Failure
    ↓
Log warning
Notifications cannot be sent
But API continues working
Data is stored locally
Once HA recovers, notifications resume
```

### Per-Device Failure

```
Notification send fails for device A
    ↓
Log error
Continue with device B
Notification marked as failed
Task remains due for next retry
```

### API Validation

All endpoints validate input using Pydantic:
```python
@app.post("/tasks")
async def create_task(request: TaskCreateRequest) -> Task:
    # Pydantic validates: name (str), frequency (enum), assigned_to (list)
    # Invalid input returns 422 with detailed error
```

## Performance Considerations

### Scheduler Efficiency

- **Every 30 seconds**: Storage read (parse tasks.json)
- **Small overhead**: Only checks tasks due in past
- **No database overhead**: JSON files in memory

**For typical home use (10-20 tasks):**
- Storage read: <1ms
- Comparison logic: <1ms
- Total scheduler CPU time: <0.1% per cycle

### Scalability Notes

- **Current implementation**: Good for <1000 tasks
- **If you need more**: Migrate to SQLite (see storage.py refactor hints)
- **API performance**: FastAPI handles hundreds of concurrent requests easily

## Configuration & Customization

### Notification Times

Edit `app/scheduler.py`:
```python
WEEKDAY_NOTIFICATION_HOUR = 16  # Change to your preferred hour
WEEKEND_NOTIFICATION_HOUR = 8
```

### Timezone

Edit `app/scheduler.py`:
```python
TZ = ZoneInfo("Europe/Stockholm")  # Change to your timezone
```

### Storage Location

Edit `main.py` startup:
```python
data_dir = os.getenv("DATA_DIR", "/data")  # Default: /data, change as needed
```

### Postpone Duration

In `main.py`, `postpone_task()` currently adds 1 day. Change:
```python
new_due = get_notification_time(now + timedelta(days=1))  # Change days=1 to your preference
```

## Testing the Add-on Locally

Without Docker:
```bash
pip install -r requirements.txt
export HA_URL=http://localhost:8123
export HA_TOKEN=your_token
python -m uvicorn app.main:app --reload
```

With Docker:
```bash
docker build -t chores .
docker run -e HA_URL=http://host.docker.internal:8123 \
           -e HA_TOKEN=your_token \
           -v chores_data:/data \
           -p 8000:8000 \
           chores
```

## Future Enhancements

1. **Web UI**: Replace FastAPI docs with custom dashboard
2. **Database**: Migrate to SQLite for scalability
3. **Recurring Overrides**: Skip notifications on specific dates
4. **Analytics**: Track completion rates
5. **Chore Categories**: Group tasks by room/person
6. **Custom Schedules**: Support cron-like expressions
7. **Multi-user**: Per-user task filtering
8. **Mobile App**: Native iOS/Android integration
