# Household Chores Reminder Add-on

A smart reminder system for household chores that sends notifications to your phones and integrates with Home Assistant.

This add-on is part of the [home-assistant-chores-addons](https://github.com/johan-ankarsrum/home-assistant-chores-addons) repository.

## Features

- **Task Management**: Define household tasks with flexible scheduling (daily, weekly, monthly, quarterly, yearly)
- **Smart Notifications**: Automatic reminders at optimal times
  - Weekdays (Mon-Fri): 16:00 (4 PM)
  - Weekends (Sat-Sun): 08:00 (8 AM)
- **Multi-Device Support**: Send notifications to multiple family members' phones
- **Interactive Actions**: Mark tasks as done or postpone directly from notifications
- **Persistent Storage**: Tasks and device configurations stored locally
- **REST API**: Full API for managing tasks and devices
- **Timezone Support**: Uses Europe/Stockholm timezone by default (customizable)

## Installation

### 1. Add the Repository to Home Assistant

1. Go to Home Assistant Settings → Add-ons → Add-on Store
2. Click the three-dot menu and select "Repositories"
3. Add this repository URL: `https://github.com/yourusername/home-assistant-chores`
4. The "Household Chores Reminder" add-on will appear in the store

### 2. Install and Configure

1. Click on "Household Chores Reminder"
2. Click "Install"
3. Go to the "Configuration" tab and set:
   - **HA_URL**: Your Home Assistant URL (e.g., `http://homeassistant.local:8123`)
   - **HA_TOKEN**: A Home Assistant long-lived access token
   - **Timezone**: Your timezone (default: Europe/Stockholm)
   - **Port**: Port to run the service on (default: 8000)

### 3. Get a Home Assistant Token

1. Go to your Home Assistant profile (bottom left corner)
2. Scroll down to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Name it "Chores Add-on" and copy the token
5. Paste it in the add-on configuration

### 4. Start the Add-on

1. Click the "Start" button
2. Check the logs to ensure it started without errors
3. Verify connection in the "Info" tab

## Configuration

### Environment Variables

- `HA_URL`: Home Assistant base URL (default: `http://localhost:8123`)
- `HA_TOKEN`: Home Assistant long-lived access token
- `DATA_DIR`: Directory for storing tasks and devices (default: `/data`)
- `PORT`: Port to run the service on (default: `8000`)
- `HOST`: Host to bind to (default: `0.0.0.0`)

## API Usage

The add-on exposes a REST API on port 8000. Full documentation is available at `http://<your-ha>:8000/docs`.

### Health Check

```bash
GET http://localhost:8000/health
```

### Task Management

#### List all tasks
```bash
GET /tasks
```

#### Create a task
```bash
POST /tasks
Content-Type: application/json

{
  "name": "Vacuum the house",
  "frequency": "weekly",
  "assigned_to": ["johan_phone", "anna_phone"]
}
```

**Frequencies**: `daily`, `weekly`, `monthly`, `quarterly`, `yearly`

#### Mark task as done
```bash
POST /tasks/{task_id}/done
```

#### Postpone a task
```bash
POST /tasks/{task_id}/postpone
Content-Type: application/json

{
  "next_due": "2024-12-15T16:00:00"
}
```

### Device Management

#### List all devices
```bash
GET /devices
```

#### Create a device
```bash
POST /devices
Content-Type: application/json

{
  "id": "johan_phone",
  "notify_service": "notify.mobile_app_johans_iphone"
}
```

The `notify_service` should match your Home Assistant mobile app entity.

## Home Assistant Integration

### 1. Set Up Notification Action Automation

Add this automation to your Home Assistant `automations.yaml`:

```yaml
automation:
  - id: household_chores_notification_actions
    alias: Household Chores - Notification Actions
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
    condition:
      - condition: template
        value_template: >
          {{ trigger.event.data.action | default('') | regex_search('^TASK_(DONE|POSTPONE)_') }}
    action:
      - service: rest_command.chores_notification_action
        data:
          action: "{{ trigger.event.data.action }}"
```

And add this to your `configuration.yaml`:

```yaml
rest_command:
  chores_notification_action:
    url: "http://homeassistant.local:8000/ha/action"
    method: POST
    content_type: "application/json"
    payload: '{"action": "{{ action }}"}'
```

### 2. Find Your Mobile App Notify Service

In Home Assistant Developer Tools → States, search for `notify.mobile_app_` to find your app's service name.

Common formats:
- `notify.mobile_app_johans_iphone`
- `notify.mobile_app_annas_android_phone`

## Usage Examples

### Add a Device

```bash
curl -X POST http://localhost:8000/devices \
  -H "Content-Type: application/json" \
  -d '{
    "id": "johan_phone",
    "notify_service": "notify.mobile_app_johans_iphone"
  }'
```

### Create a Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vacuum the house",
    "frequency": "weekly",
    "assigned_to": ["johan_phone"]
  }'
```

### Mark a Task as Done

```bash
curl -X POST http://localhost:8000/tasks/abc123/done
```

The add-on will automatically calculate the next due date based on the frequency.

## How It Works

### Scheduling

The add-on runs a scheduler loop that:
1. Checks every minute if any tasks are due
2. At the correct notification time (16:00 on weekdays, 08:00 on weekends):
   - Finds all tasks where `next_due <= now`
   - Sends notifications to all assigned devices
   - The notification includes "Done" and "Postpone" buttons

### Next Due Calculation

When a task is marked as done, the `next_due` is calculated as:
- **Daily**: last_done + 1 day
- **Weekly**: last_done + 1 week
- **Monthly**: last_done + 1 month
- **Quarterly**: last_done + 3 months
- **Yearly**: last_done + 1 year

The time is then adjusted to the appropriate notification time based on the date:
- Weekday → 16:00
- Weekend → 08:00

### Notification Interaction

Users can interact with notifications in two ways:

1. **Quick Actions** (on the notification):
   - Tap "Done" to mark the task as complete immediately
   - Tap "Postpone" to delay by one day

2. **Web UI** (tap notification body):
   - Opens the management interface where users can:
     - View task details
     - Select a specific date/time to postpone to
     - Mark as done with comments

## Troubleshooting

### "HA_TOKEN environment variable not set"

Add a long-lived access token in the add-on configuration.

### Notifications not sending

1. Check the add-on logs for connection errors
2. Verify the `notify_service` matches your mobile app entity in Home Assistant
3. Ensure Home Assistant can reach the add-on (same network/host)
4. Test with: `curl http://localhost:8000/health`

### Tasks not appearing

1. Check the `tasks.json` file in the add-on storage
2. Verify the app is running with `curl http://localhost:8000/tasks`

### Timezone issues

The add-on uses `Europe/Stockholm` by default. Change it in the add-on configuration if needed.

## Project Structure

```
home-assistant-chores/
├── Dockerfile              # Docker image definition
├── config.yaml            # Home Assistant add-on config
├── requirements.txt       # Python dependencies
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app and scheduler
│   ├── models.py         # Pydantic data models
│   ├── storage.py        # JSON file storage layer
│   ├── scheduler.py      # Scheduling logic
│   └── ha_client.py      # Home Assistant API client
├── example_automation.yaml   # Example Home Assistant automation
├── example_lovelace.yaml    # Example dashboard card
└── README.md              # This file
```

## Development

### Running Locally

```bash
pip install -r requirements.txt
export HA_URL=http://localhost:8123
export HA_TOKEN=your_token_here
export DATA_DIR=./data
python -m uvicorn app.main:app --reload
```

API docs will be available at: http://localhost:8000/docs

### Running in Docker

```bash
docker build -t household-chores .
docker run -e HA_URL=http://host.docker.internal:8123 \
           -e HA_TOKEN=your_token \
           -v chores_data:/data \
           -p 8000:8000 \
           household-chores
```

## License

MIT License - Feel free to modify and distribute

## Support

For issues, feature requests, or questions, please open an issue on GitHub.
