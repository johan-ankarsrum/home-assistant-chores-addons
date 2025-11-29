# API Examples & Test Cases

Complete curl examples for testing the Household Chores Add-on API.

## Setup for Testing

### Windows PowerShell

```powershell
$API_URL = "http://localhost:8000"
```

### bash/Linux

```bash
API_URL="http://localhost:8000"
```

---

## Health Check

### Test API is Running

```bash
curl "$API_URL/health"
```

**Response:**
```json
{
  "status": "ok",
  "ha_connected": true
}
```

---

## Device Management

### Create a Device

```bash
curl -X POST "$API_URL/devices" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "johan_phone",
    "notify_service": "notify.mobile_app_johans_iphone"
  }'
```

**Response:**
```json
{
  "id": "johan_phone",
  "notify_service": "notify.mobile_app_johans_iphone"
}
```

### Create Another Device

```bash
curl -X POST "$API_URL/devices" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "anna_phone",
    "notify_service": "notify.mobile_app_annas_android"
  }'
```

### List All Devices

```bash
curl "$API_URL/devices"
```

**Response:**
```json
[
  {
    "id": "johan_phone",
    "notify_service": "notify.mobile_app_johans_iphone"
  },
  {
    "id": "anna_phone",
    "notify_service": "notify.mobile_app_annas_android"
  }
]
```

### Get Specific Device

```bash
curl "$API_URL/devices/johan_phone"
```

### Update Device

```bash
curl -X PUT "$API_URL/devices/johan_phone" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "johan_phone",
    "notify_service": "notify.mobile_app_johans_iphone_new"
  }'
```

### Delete Device

```bash
curl -X DELETE "$API_URL/devices/anna_phone"
```

---

## Task Management

### Create a Task (Daily)

```bash
curl -X POST "$API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Brush teeth",
    "frequency": "daily",
    "assigned_to": ["johan_phone"]
  }'
```

**Response:**
```json
{
  "id": "a1b2c3d4",
  "name": "Brush teeth",
  "frequency": "daily",
  "last_done": "2024-11-29T14:30:00+01:00",
  "next_due": "2024-11-30T16:00:00+01:00",
  "assigned_to": ["johan_phone"]
}
```

### Create a Task (Weekly)

```bash
curl -X POST "$API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vacuum the house",
    "frequency": "weekly",
    "assigned_to": ["johan_phone", "anna_phone"]
  }'
```

### Create a Task (Monthly)

```bash
curl -X POST "$API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clean the oven",
    "frequency": "monthly",
    "assigned_to": ["johan_phone"]
  }'
```

### Create a Task (Quarterly)

```bash
curl -X POST "$API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Flip mattress",
    "frequency": "quarterly",
    "assigned_to": ["anna_phone"]
  }'
```

### Create a Task (Yearly)

```bash
curl -X POST "$API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clean gutters",
    "frequency": "yearly",
    "assigned_to": ["johan_phone", "anna_phone"]
  }'
```

### List All Tasks

```bash
curl "$API_URL/tasks"
```

**Response:**
```json
[
  {
    "id": "a1b2c3d4",
    "name": "Brush teeth",
    "frequency": "daily",
    "last_done": "2024-11-29T14:30:00+01:00",
    "next_due": "2024-11-30T16:00:00+01:00",
    "assigned_to": ["johan_phone"]
  },
  {
    "id": "e5f6g7h8",
    "name": "Vacuum the house",
    "frequency": "weekly",
    "last_done": "2024-11-29T14:30:00+01:00",
    "next_due": "2024-12-06T16:00:00+01:00",
    "assigned_to": ["johan_phone", "anna_phone"]
  }
]
```

### Get Specific Task

```bash
curl "$API_URL/tasks/a1b2c3d4"
```

### Update a Task

```bash
curl -X PUT "$API_URL/tasks/a1b2c3d4" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Brush teeth (morning and night)",
    "frequency": "daily",
    "assigned_to": ["johan_phone"]
  }'
```

### Mark Task as Done

```bash
curl -X POST "$API_URL/tasks/a1b2c3d4/done"
```

**Response:**
```json
{
  "id": "a1b2c3d4",
  "name": "Brush teeth",
  "frequency": "daily",
  "last_done": "2024-11-29T15:45:00+01:00",
  "next_due": "2024-11-30T16:00:00+01:00",
  "assigned_to": ["johan_phone"]
}
```

### Postpone a Task

```bash
curl -X POST "$API_URL/tasks/e5f6g7h8/postpone" \
  -H "Content-Type: application/json" \
  -d '{
    "next_due": "2024-12-13T16:00:00+01:00"
  }'
```

**Response:**
```json
{
  "id": "e5f6g7h8",
  "name": "Vacuum the house",
  "frequency": "weekly",
  "last_done": "2024-11-29T14:30:00+01:00",
  "next_due": "2024-12-13T16:00:00+01:00",
  "assigned_to": ["johan_phone", "anna_phone"]
}
```

### Delete a Task

```bash
curl -X DELETE "$API_URL/tasks/a1b2c3d4"
```

---

## Home Assistant Notification Action Webhook

### Handle "Done" Action

```bash
curl -X POST "$API_URL/ha/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "TASK_DONE_a1b2c3d4"
  }'
```

**Response:**
```json
{
  "status": "ok",
  "action": "task_done",
  "task_id": "a1b2c3d4",
  "next_due": "2024-11-30T16:00:00+01:00"
}
```

### Handle "Postpone" Action

```bash
curl -X POST "$API_URL/ha/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "TASK_POSTPONE_e5f6g7h8"
  }'
```

**Response:**
```json
{
  "status": "ok",
  "action": "task_postponed",
  "task_id": "e5f6g7h8",
  "new_due": "2024-12-07T16:00:00+01:00"
}
```

---

## Full Workflow Example

### Complete Flow with All Steps

```bash
# 1. Add a device
DEVICE_RESP=$(curl -s -X POST "$API_URL/devices" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_phone",
    "notify_service": "notify.mobile_app_test"
  }')
echo "Device created: $DEVICE_RESP"

# 2. Create a task
TASK_RESP=$(curl -s -X POST "$API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test task",
    "frequency": "daily",
    "assigned_to": ["test_phone"]
  }')
echo "Task created: $TASK_RESP"
TASK_ID=$(echo $TASK_RESP | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Task ID: $TASK_ID"

# 3. List all tasks
curl -s "$API_URL/tasks" | jq '.'

# 4. Get specific task
curl -s "$API_URL/tasks/$TASK_ID" | jq '.'

# 5. Mark task as done
curl -s -X POST "$API_URL/tasks/$TASK_ID/done" | jq '.'

# 6. Check next_due was updated
curl -s "$API_URL/tasks/$TASK_ID" | jq '.next_due'

# 7. Postpone task
curl -s -X POST "$API_URL/tasks/$TASK_ID/postpone" \
  -H "Content-Type: application/json" \
  -d '{
    "next_due": "2024-12-15T16:00:00+01:00"
  }' | jq '.'

# 8. Clean up - delete task
curl -s -X DELETE "$API_URL/tasks/$TASK_ID" | jq '.'

# 9. Clean up - delete device
curl -s -X DELETE "$API_URL/devices/test_phone" | jq '.'
```

---

## Using Python Requests

### Setup

```python
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def print_response(response):
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
```

### Create Device

```python
device_data = {
    "id": "johan_phone",
    "notify_service": "notify.mobile_app_johans_iphone"
}
response = requests.post(f"{API_URL}/devices", json=device_data)
print_response(response)
```

### Create Task

```python
task_data = {
    "name": "Vacuum the house",
    "frequency": "weekly",
    "assigned_to": ["johan_phone"]
}
response = requests.post(f"{API_URL}/tasks", json=task_data)
print_response(response)
task_id = response.json()["id"]
```

### Mark Done

```python
response = requests.post(f"{API_URL}/tasks/{task_id}/done")
print_response(response)
```

### Postpone

```python
postpone_data = {
    "next_due": "2024-12-15T16:00:00+01:00"
}
response = requests.post(f"{API_URL}/tasks/{task_id}/postpone", json=postpone_data)
print_response(response)
```

---

## Testing from Home Assistant

### Service Call in Automation

```yaml
action:
  - service: rest_command.test_chores_api
    data:
      endpoint: "tasks"
      method: "GET"
```

### REST Sensor

```yaml
sensor:
  - platform: rest
    resource: "http://homeassistant.local:8000/tasks"
    name: "Chores Tasks"
    scan_interval: 300
    json_attributes_path: "$"
    value_template: "{{ value_json | length }}"
```

---

## Troubleshooting

### API Not Responding

```bash
# Check if service is running
curl "$API_URL/health"

# Check add-on logs in Home Assistant
# Settings → Add-ons → Household Chores → Logs
```

### Invalid Device Error

```bash
# List devices to verify spelling
curl "$API_URL/devices"

# Device ID and notify_service must match exactly
```

### Task Not Found

```bash
# List all tasks to get correct ID
curl "$API_URL/tasks" | jq '.[] | {id, name}'

# Copy the exact ID from response
```

### Notification Not Sending

1. Check HA_TOKEN is set correctly
2. Verify notify_service exists in Home Assistant (Developer Tools → States)
3. Check add-on logs for connection errors
4. Test Home Assistant connection: `curl "$API_URL/health"`

---

## Batch Operations (PowerShell)

```powershell
# Create multiple devices
@("johan", "anna", "kids") | ForEach-Object {
    $deviceData = @{
        id = "${_}_phone"
        notify_service = "notify.mobile_app_${_}"
    } | ConvertTo-Json
    
    Invoke-WebRequest -Method POST -Uri "$API_URL/devices" `
        -ContentType "application/json" `
        -Body $deviceData
}

# Create multiple tasks
@("Vacuum", "Dishes", "Laundry", "Bathrooms") | ForEach-Object {
    $taskData = @{
        name = $_
        frequency = "weekly"
        assigned_to = @("johan_phone", "anna_phone")
    } | ConvertTo-Json
    
    Invoke-WebRequest -Method POST -Uri "$API_URL/tasks" `
        -ContentType "application/json" `
        -Body $taskData
}
```
