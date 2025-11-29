# Setup Checklist & Getting Started

Use this checklist to ensure successful deployment of the Household Chores Reminder add-on.

## Pre-Deployment Checklist

### Prerequisites
- [ ] Home Assistant 2024.1.0 or later installed and running
- [ ] Network access between your computer and Home Assistant
- [ ] Mobile app installed and working on at least one phone
- [ ] Git (optional, for cloning the repository)

### Required Information
- [ ] Home Assistant URL (e.g., http://192.168.1.100:8123)
- [ ] Home Assistant long-lived access token
  - Go to Home Assistant profile → Long-Lived Access Tokens
  - Create a new token named "Chores Add-on"
  - **Keep this secure!** Don't share or commit to git
- [ ] Mobile app notify service name (found in Developer Tools → States)
  - Example: `notify.mobile_app_johans_iphone`

## Deployment Checklist

### Step 1: Prepare the Project
- [ ] Copy project files to your system
- [ ] Verify all files are present:
  ```
  app/
  ├── main.py
  ├── models.py
  ├── storage.py
  ├── scheduler.py
  └── ha_client.py
  config.yaml
  Dockerfile
  requirements.txt
  ```

### Step 2: Deploy to Home Assistant (Choose One Method)

#### Option A: From Add-on Store (Easiest)
- [ ] Settings → Add-ons → Add-on Store
- [ ] Click three-dot menu → Repositories
- [ ] Add: `https://github.com/yourusername/home-assistant-chores`
- [ ] Click "Create"
- [ ] Install "Household Chores Reminder"
- [ ] Go to Configuration tab
- [ ] Set HA_URL: `http://homeassistant.local:8123`
- [ ] Set HA_TOKEN: (paste your token)
- [ ] Leave other fields as default
- [ ] Click "Save"
- [ ] Click "Start"

#### Option B: Manual Docker
- [ ] Build image: `docker build -t household-chores .`
- [ ] Create volume: `docker volume create chores_data`
- [ ] Run container with HA_URL and HA_TOKEN
- [ ] Verify running: `docker logs household-chores`

### Step 3: Verify Installation
- [ ] Open http://[HA_IP]:8000/health
- [ ] Response shows `"status":"ok"`
- [ ] Check add-on logs for "Scheduler started"
- [ ] No error messages in logs

### Step 4: Configure Home Assistant

#### Find Your Mobile App Service
- [ ] Open Home Assistant Developer Tools
- [ ] Go to States tab
- [ ] Search for `notify.mobile_app_`
- [ ] Note the exact service name(s)
- [ ] Repeat for each family member

#### Add Rest Command to configuration.yaml
- [ ] Add this to `configuration.yaml`:
  ```yaml
  rest_command:
    chores_notification_action:
      url: "http://homeassistant.local:8000/ha/action"
      method: POST
      content_type: "application/json"
      payload: '{"action": "{{ action }}"}'
  ```
- [ ] Reload automations: Developer Tools → Actions → Reload automations
- [ ] Restart Home Assistant (or just reload automations)

#### Add Automation
- [ ] Settings → Automations → Create Automation
- [ ] Switch to YAML mode
- [ ] Paste example from `example_automation.yaml`
- [ ] Click "Save"
- [ ] Click the toggle to enable

### Step 5: Set Up Tasks & Devices

#### Create First Device
```bash
curl -X POST http://homeassistant.local:8000/devices \
  -H "Content-Type: application/json" \
  -d '{
    "id": "your_name",
    "notify_service": "notify.mobile_app_your_phone"
  }'
```
- [ ] Replace `your_name` with a device ID
- [ ] Replace `notify.mobile_app_...` with your actual service
- [ ] Verify response shows created device

#### Create Repeat for Each Family Member
- [ ] Device 2: Create another device entry
- [ ] Device 3: Create another device entry (if needed)

#### Create First Task
```bash
curl -X POST http://homeassistant.local:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vacuum the house",
    "frequency": "weekly",
    "assigned_to": ["your_name"]
  }'
```
- [ ] Replace task name with your chore
- [ ] Choose frequency (daily, weekly, monthly, quarterly, yearly)
- [ ] Set assigned_to with device IDs you created
- [ ] Verify response shows created task

#### Create More Tasks
- [ ] Task 2: Create another task
- [ ] Task 3: Create another task
- [ ] etc.

## Testing Checklist

### Test the API
- [ ] `curl http://localhost:8000/tasks` returns your tasks
- [ ] `curl http://localhost:8000/devices` returns your devices
- [ ] `curl http://localhost:8000/health` shows connected

### Test Notifications (Wait for Notification Time)
- [ ] Wait until next notification time:
  - Weekday (Mon-Fri): 16:00
  - Weekend (Sat-Sun): 08:00
- [ ] Receive notification on your phone(s)
- [ ] Notification shows task name
- [ ] Notification shows "Done" and "Postpone" buttons

### Test Interaction
- [ ] Tap "Done" button on notification
- [ ] Check API: `curl http://localhost:8000/tasks`
- [ ] Verify `next_due` was updated to future date
- [ ] Create another task to test "Postpone"
- [ ] Tap "Postpone" button
- [ ] Verify task postponed by 1 day

## First Week Tasks

### Monitor & Verify
- [ ] Add 5-10 household tasks
- [ ] Assign tasks to family members
- [ ] Verify notifications arrive at correct times
- [ ] Verify family can tap Done/Postpone
- [ ] Check app logs for errors

### Customize
- [ ] Review notification times (lines 13-14 in scheduler.py if you want to change)
- [ ] Verify timezone is correct (default: Europe/Stockholm)
- [ ] Test different frequency types
- [ ] Create recurring tasks

### Backup
- [ ] Backup data volume:
  ```bash
  docker run --rm -v chores_data:/data -v $(pwd):/backup \
    alpine tar czf /backup/chores-backup.tar.gz -C /data .
  ```
- [ ] Save backup file to safe location

## Troubleshooting Checklist

### If Notifications Not Sending
- [ ] Verify HA_TOKEN is set: Settings → Add-ons → Configuration
- [ ] Check notify service exists: Developer Tools → States
- [ ] Verify service name spelling exactly matches
- [ ] Check add-on logs for connection errors
- [ ] Test: `curl http://localhost:8000/health`

### If Tasks Not Appearing
- [ ] Test API: `curl http://localhost:8000/tasks`
- [ ] Check browser console for errors
- [ ] Verify devices were created first
- [ ] Check add-on logs for errors

### If Add-on Won't Start
- [ ] Check logs: Settings → Add-ons → Logs
- [ ] Verify HA_TOKEN is set
- [ ] Verify HA_URL is correct
- [ ] Try restarting add-on
- [ ] Try restarting Home Assistant

### If Automation Not Working
- [ ] Verify automation is enabled
- [ ] Check automation condition (regex pattern)
- [ ] Verify rest_command is configured in config.yaml
- [ ] Check Home Assistant logs for automation errors

## Security Checklist

- [ ] HA_TOKEN stored only in add-on configuration (not in git)
- [ ] .gitignore contains `data/` directory
- [ ] Token not shared in logs or documentation
- [ ] Add-on only accessible on local network
- [ ] Backup files stored in secure location
- [ ] Consider using reverse proxy (nginx) for HTTPS if exposed

## Ongoing Maintenance

### Weekly
- [ ] Verify notifications are arriving
- [ ] Check family members are responding
- [ ] Monitor app logs for errors

### Monthly
- [ ] Back up data
- [ ] Review task completion rates
- [ ] Adjust frequencies if needed

### Quarterly
- [ ] Review and update documentation
- [ ] Update add-on if new version available
- [ ] Clean up completed tasks

## Getting Help

If something doesn't work:

1. **Check Documentation**
   - README.md - Overview
   - QUICKSTART.md - Quick setup
   - DEPLOYMENT.md - Detailed deployment
   - ARCHITECTURE.md - Technical details

2. **Check Logs**
   - Home Assistant: Settings → Add-ons → Logs
   - Docker: `docker logs household-chores`

3. **Test Connectivity**
   - `curl http://localhost:8000/health`
   - `curl http://localhost:8000/tasks`

4. **Review Examples**
   - API_EXAMPLES.md - Curl and Python examples
   - example_automation.yaml - HA automation
   - example_lovelace.yaml - Dashboard setup

## Performance Baseline

After deployment, typical performance should be:
- [ ] CPU usage: <1% idle, <5% during notification check
- [ ] Memory: 80-100MB
- [ ] Response time: <100ms per API call
- [ ] Notifications sent within 1 minute of scheduled time

## Customization Options

Ready to customize? See ARCHITECTURE.md for:
- [ ] Changing notification times
- [ ] Changing timezone
- [ ] Adjusting postpone duration
- [ ] Adding new API endpoints

## Success Criteria

You've successfully deployed when:
- ✅ Add-on is running (shows in Settings → Add-ons)
- ✅ API responds at http://localhost:8000/health
- ✅ Devices and tasks created
- ✅ First notification received at correct time
- ✅ Can tap Done/Postpone from notification
- ✅ Task is updated in API response
- ✅ Data persists across add-on restarts

---

## Quick Reference

### Important URLs
- **Home Assistant**: http://homeassistant.local:8123
- **Add-on API**: http://homeassistant.local:8000
- **API Docs**: http://homeassistant.local:8000/docs
- **Health Check**: http://homeassistant.local:8000/health

### Important Files
- **Tasks**: `/data/tasks.json`
- **Devices**: `/data/devices.json`
- **Logs**: Settings → Add-ons → Household Chores → Logs

### Important Frequencies
| Frequency | Next Due After Done |
|-----------|-------------------|
| daily | +1 day |
| weekly | +1 week |
| monthly | +1 month |
| quarterly | +3 months |
| yearly | +1 year |

### Important Notification Times
| Day | Time |
|-----|------|
| Mon-Fri | 16:00 (4 PM) |
| Sat-Sun | 08:00 (8 AM) |

---

**Start Here**: Follow the checklist above in order, then refer to QUICKSTART.md if you get stuck.

You've got this! 🎉
