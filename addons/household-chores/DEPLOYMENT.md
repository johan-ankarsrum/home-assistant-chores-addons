# Deployment Guide

Complete guide for deploying the Household Chores Reminder add-on to Home Assistant.

## Option 1: Deploy from Repository (Recommended)

### Prerequisites
- Home Assistant 2024.1.0 or later
- Network access to the add-on repository

### Steps

1. **Add Repository to Home Assistant**
   - Settings → Add-ons → Add-on Store
   - Click the three-dot menu (⋮) → Repositories
   - Add: `https://github.com/yourusername/home-assistant-chores-addons`
   - Click "Create" (or your repo URL)

2. **Install the Add-on**
   - The "Household Chores Reminder" should appear in the store
   - Click on it → Click "Install"
   - Wait for installation to complete

3. **Configure**
   - Go to the add-on configuration tab
   - Set these values:
     ```
     ha_url: http://homeassistant.local:8123
     ha_token: [YOUR_LONG_LIVED_TOKEN]
     timezone: Europe/Stockholm
     port: 8000
     log_level: info
     ```

4. **Start the Add-on**
   - Click "Start"
   - Wait a few seconds
   - Check logs for "Scheduler started"

5. **Verify It's Running**
   - Open: `http://[your-ha-ip]:8000/health`
   - Should show: `{"status":"ok","ha_connected":true}`

---

## Option 2: Manual Docker Deployment

For advanced users or testing without Home Assistant add-on system.

### Prerequisites
- Docker installed
- Home Assistant network accessible to the container

### Steps

1. **Build the Docker Image**
   ```bash
   cd home-assistant-chores
   docker build -t household-chores:latest .
   ```

2. **Create Data Volume**
   ```bash
   docker volume create chores_data
   ```

3. **Run the Container**
   ```bash
   docker run -d \
     --name household-chores \
     -e HA_URL=http://192.168.1.100:8123 \
     -e HA_TOKEN=your_token_here \
     -e PORT=8000 \
     -v chores_data:/data \
     -p 8000:8000 \
     --restart unless-stopped \
     household-chores:latest
   ```

4. **Verify**
   ```bash
   docker logs household-chores
   curl http://localhost:8000/health
   ```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  household-chores:
    image: household-chores:latest
    build: .
    environment:
      HA_URL: "http://homeassistant:8123"
      HA_TOKEN: "${HA_TOKEN}"
      DATA_DIR: "/data"
      PORT: 8000
    volumes:
      - chores_data:/data
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  chores_data:
```

Run with:
```bash
HA_TOKEN=your_token_here docker-compose up -d
```

---

## Option 3: Home Assistant Yellow/Green with Docker Compose

If running Home Assistant on a server with Docker:

1. **Create folder structure**
   ```bash
   mkdir -p /path/to/addons/household-chores
   cd /path/to/addons/household-chores
   ```

2. **Copy these files:**
   - `Dockerfile`
   - `config.yaml`
   - `requirements.txt`
   - `app/` directory

3. **Update Home Assistant configuration**
   In `configuration.yaml`:
   ```yaml
   rest_command:
     chores_notification_action:
       url: "http://localhost:8000/ha/action"
       method: POST
       content_type: "application/json"
       payload: '{"action": "{{ action }}"}'
   ```

4. **Run via Docker Compose**
   ```bash
   docker-compose up -d
   ```

---

## Configuration After Deployment

### 1. Get Your Mobile App Service Name

In Home Assistant:
1. Developer Tools (Settings → Developer Tools)
2. States tab
3. Search for: `notify.mobile_app_`
4. Note the full entity name (e.g., `notify.mobile_app_johans_iphone`)

### 2. Create Devices

```bash
curl -X POST http://[HA_IP]:8000/devices \
  -H "Content-Type: application/json" \
  -d '{
    "id": "johan",
    "notify_service": "notify.mobile_app_johans_iphone"
  }'
```

Repeat for each family member.

### 3. Create Home Assistant Automation

Add to `automations.yaml`:

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

### 4. Create Your First Tasks

```bash
curl -X POST http://[HA_IP]:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vacuum the house",
    "frequency": "weekly",
    "assigned_to": ["johan", "anna"]
  }'
```

### 5. Test the System

1. Create a task with `next_due` set to current time (or soon)
2. Wait for notification time (16:00 weekday or 08:00 weekend)
3. Receive notification on your phone
4. Tap "Done" or "Postpone"
5. Verify task is updated in the API

---

## Troubleshooting Deployment

### Container Won't Start

1. Check logs:
   ```bash
   docker logs household-chores
   ```

2. Common issues:
   - Missing HA_TOKEN: Add `HA_TOKEN` environment variable
   - Port already in use: Change port in config or stop conflicting service
   - Network issues: Ensure Home Assistant is reachable from container

### Can't Connect to Home Assistant

1. Check if HA_URL is correct:
   - Use IP address instead of hostname
   - Ensure port matches (usually 8123)
   - Test: `docker exec household-chores curl http://[HA_IP]:8123/api/`

2. Check token:
   - Generate new long-lived token in HA
   - Update environment variable
   - Restart container

### Notifications Not Sending

1. Verify notify service exists:
   - Home Assistant Developer Tools → States
   - Search for `notify.`
   - Check exact spelling

2. Check add-on logs:
   - Look for "Notification sent" or "Failed to send"
   - Check Home Assistant connection status

3. Test manually:
   ```bash
   curl http://[HA_IP]:8000/health
   ```

### Tasks Not Persisting

1. Check data volume:
   ```bash
   docker volume inspect chores_data
   docker exec household-chores ls -la /data/
   ```

2. Verify permissions:
   - Files should be readable/writable in container
   - Volume should be mounted at `/data`

### Scheduler Not Running

1. Check logs for "Scheduler loop started"
2. Verify no errors in startup
3. Restart container:
   ```bash
   docker restart household-chores
   ```

---

## Updating the Add-on

### From Home Assistant Add-on Store

1. Settings → Add-ons
2. Click "Household Chores Reminder"
3. If update available, click "Update"
4. Go to Info tab and click "Restart"

### Manual Docker Update

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker build -t household-chores:latest .

# Stop old container
docker stop household-chores
docker rm household-chores

# Run new container (same as before)
docker run -d \
  --name household-chores \
  -e HA_URL=... \
  -e HA_TOKEN=... \
  -v chores_data:/data \
  -p 8000:8000 \
  --restart unless-stopped \
  household-chores:latest
```

---

## Backup and Restore

### Backup Data

```bash
# Backup the data volume
docker run --rm -v chores_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/chores-backup.tar.gz -C /data .

# Or manually copy files
docker exec household-chores cat /data/tasks.json > tasks_backup.json
docker exec household-chores cat /data/devices.json > devices_backup.json
```

### Restore Data

```bash
# Restore from backup
docker run --rm -v chores_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/chores-backup.tar.gz -C /data

# Restart container
docker restart household-chores
```

---

## Performance & Monitoring

### System Resources

Typical usage:
- CPU: <1% idle, <5% when checking tasks
- Memory: ~80-100MB
- Disk: ~2-5MB for tasks/devices storage

### Monitoring

#### Check Add-on Health

```bash
curl http://[HA_IP]:8000/health
```

#### View Logs

Home Assistant:
- Settings → Add-ons → Household Chores → Logs

Docker:
```bash
docker logs -f household-chores
```

#### Count Tasks and Devices

```bash
curl http://[HA_IP]:8000/tasks | jq 'length'
curl http://[HA_IP]:8000/devices | jq 'length'
```

---

## Production Checklist

- [ ] Home Assistant long-lived token created and saved
- [ ] HA_TOKEN configured in add-on settings
- [ ] HA_URL points to correct Home Assistant instance
- [ ] Add-on started and running (check logs)
- [ ] Health check passes: `/health` endpoint
- [ ] Mobile app notify service found in Developer Tools
- [ ] At least one device created
- [ ] Automation added and enabled
- [ ] Test task created with correct frequency
- [ ] Received notification at correct time
- [ ] Action buttons work (Done/Postpone)
- [ ] Data volume backed up
- [ ] Restart policy set to `unless-stopped`

---

## Rollback Instructions

If something goes wrong:

### Add-on System
1. Settings → Add-ons → Household Chores
2. Click three-dot menu → Uninstall
3. Reinstall from store
4. Data is preserved in volume

### Docker Manual
```bash
# Keep the data volume but remove container
docker stop household-chores
docker rm household-chores

# Restore previous version
docker run -d \
  --name household-chores \
  -e HA_URL=... \
  -e HA_TOKEN=... \
  -v chores_data:/data \
  -p 8000:8000 \
  --restart unless-stopped \
  household-chores:previous_version
```

---

## Support

If you encounter issues:

1. Check logs: Add-ons → Logs
2. Verify configuration: Double-check all settings
3. Test connectivity: `curl http://[HA_IP]:8000/health`
4. Check Mobile App: Ensure notify service is enabled
5. Review documentation: README.md and ARCHITECTURE.md
6. Check GitHub Issues: https://github.com/yourusername/home-assistant-chores

---

## Security Notes

1. **Long-Lived Token**: Keep this secret! Don't share in logs or public repos
2. **Network Access**: Only expose port 8000 on your local network
3. **HTTPS**: Consider reverse proxy (nginx) with HTTPS in production
4. **Backups**: Regularly backup your data volume

## Next Steps

Once deployed and running:
1. Create all household tasks
2. Assign to family members
3. Wait for first notifications
4. Gather feedback
5. Customize notification times if needed
6. Consider future enhancements (UI, database, etc.)
