# Quick Start Guide - Household Chores Reminder Add-on

## 5-Minute Setup

### Step 1: Prepare Your Home Assistant Token

1. Open Home Assistant
2. Click your profile (bottom left)
3. Scroll to "Long-Lived Access Tokens" → Click "Create Token"
4. Name it: `Chores Add-on` → Copy the token

### Step 2: Configure the Add-on

1. Home Assistant Settings → Add-ons → Install from URL
2. Paste: `https://github.com/yourusername/home-assistant-chores`
3. Click Install
4. Go to Configuration tab:
   - **HA_URL**: `http://homeassistant.local:8123` (or your HA IP)
   - **HA_TOKEN**: Paste your token from Step 1
   - Leave other settings as default
5. Start the add-on

### Step 3: Set Up Automation

Add this to your `automations.yaml`:

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

And add to `configuration.yaml`:

```yaml
rest_command:
  chores_notification_action:
    url: "http://homeassistant.local:8000/ha/action"
    method: POST
    content_type: "application/json"
    payload: '{"action": "{{ action }}"}'
```

### Step 4: Add Your First Device

Replace `notify.mobile_app_johans_iphone` with your actual mobile app entity from Home Assistant Developer Tools → States (search for `notify.mobile_app_`).

Use the REST API or curl:

```bash
curl -X POST http://homeassistant.local:8000/devices \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my_phone",
    "notify_service": "notify.mobile_app_johans_iphone"
  }'
```

### Step 5: Create Your First Task

```bash
curl -X POST http://homeassistant.local:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clean the kitchen",
    "frequency": "weekly",
    "assigned_to": ["my_phone"]
  }'
```

**Done!** Your first task will send a notification at 16:00 (4 PM) on weekdays when it's due.

## API Endpoints Cheat Sheet

### Tasks
- `GET /tasks` - List all tasks
- `POST /tasks` - Create a task
- `POST /tasks/{id}/done` - Mark done
- `POST /tasks/{id}/postpone` - Postpone

### Devices  
- `GET /devices` - List all devices
- `POST /devices` - Add a device

### Status
- `GET /health` - Check add-on status
- `GET /docs` - Full API documentation

## Finding Your Notify Service

In Home Assistant:
1. Developer Tools (bottom left)
2. States tab
3. Search for `notify.mobile_app_`
4. Copy the entity ID exactly

Examples:
- `notify.mobile_app_johans_iphone`
- `notify.mobile_app_annas_android_phone`
- `notify.mobile_app_work_phone`

## Troubleshooting

**Q: Notifications not sending?**
- Check add-on logs: Settings → Add-ons → Household Chores → Logs
- Verify the `notify_service` is correct
- Ensure mobile app integration is enabled in Home Assistant

**Q: Tasks not appearing?**
- Test: `curl http://homeassistant.local:8000/tasks`
- Check browser console for errors

**Q: What time do notifications send?**
- Weekdays (Mon-Fri): 16:00
- Weekends (Sat-Sun): 08:00
- Change in `app/scheduler.py` if needed

**Q: How do I change the timezone?**
- Edit `app/scheduler.py` line 12: `TZ = ZoneInfo("Europe/Stockholm")`
- Use any IANA timezone (e.g., "America/New_York")

## Next Steps

- View full API docs: `http://homeassistant.local:8000/docs`
- Read the main [README.md](README.md) for detailed documentation
- Customize notification times in `app/scheduler.py`
