# Household Chores Reminder for Home Assistant

A smart reminder system for household chores that sends notifications to your phones and integrates with Home Assistant.

## Features

- ✅ Define household tasks with flexible scheduling (daily, weekly, monthly, quarterly, yearly)
- ✅ Automatic reminders at optimal times (16:00 on weekdays, 08:00 on weekends)
- ✅ Send notifications to multiple family members' phones
- ✅ Mark tasks as done or postpone directly from notifications
- ✅ Persistent storage of tasks and device configurations
- ✅ Full REST API for managing tasks and devices
- ✅ Timezone support (Europe/Stockholm by default, customizable)
- ✅ Easy installation via HACS

## Installation

### Via HACS (Recommended)

1. Have [HACS](https://hacs.xyz/) installed in Home Assistant
2. Go to **HACS → Integrations**
3. Click **"Explore & Download Repositories"**
4. Search for **"Household Chores Reminder"**
5. Click **"Download"** and restart Home Assistant
6. Go to **Settings → Devices & Services → Create Automation**
7. Add the integration and configure with your preferences

### Manual Installation

1. Download this repository as a ZIP file
2. Extract to `custom_components/household_chores` in your Home Assistant config directory
3. Restart Home Assistant
4. Go to **Settings → Devices & Services** and add the integration

## Quick Start

After installation, refer to the documentation:
- [Quick Start Guide](addons/household-chores/QUICKSTART.md) - 5-minute setup
- [Full README](addons/household-chores/README.md) - Complete documentation
- [Deployment Guide](addons/household-chores/DEPLOYMENT.md) - Detailed setup instructions
- [API Examples](addons/household-chores/API_EXAMPLES.md) - Using the REST API

## Repository Structure

```
household-chores-addons/
├── custom_components/
│   └── household_chores/          # HACS-compatible integration
│       ├── manifest.json          # Integration metadata
│       ├── config_flow.py         # Configuration UI
│       ├── __init__.py            # Integration setup
│       ├── sensor.py              # Status sensor
│       ├── button.py              # Control buttons
│       └── strings.json           # Localization strings
├── addons/
│   └── household-chores/          # Original Docker add-on (for reference)
│       ├── Dockerfile
│       ├── config.yaml
│       ├── app/                   # FastAPI application
│       └── [documentation]
├── hacs.json                      # HACS configuration
└── README.md                      # This file

## Requirements

- Home Assistant 2024.1.0 or later
- HACS installed and configured
- Mobile app integration enabled in Home Assistant (for notifications)

## Configuration

The integration provides a configuration UI:

1. After installation, go to **Settings → Devices & Services**
2. Look for **"Household Chores Reminder"** and click **"Configure"**
3. Enter:
   - **Home Assistant URL**: Your HA instance URL (e.g., `http://homeassistant.local:8123`)
   - **Access Token**: Create a long-lived token in **Settings → Developer Tools → Long-Lived Access Tokens**
   - **Timezone**: Your timezone (default: Europe/Stockholm)
   - **Port**: Port for the service (default: 8000)
   - **Log Level**: Logging verbosity (default: info)

## Documentation

Complete documentation is located in `addons/household-chores/`:

- **[README.md](addons/household-chores/README.md)** - Full feature overview
- **[QUICKSTART.md](addons/household-chores/QUICKSTART.md)** - 5-minute setup guide
- **[ARCHITECTURE.md](addons/household-chores/ARCHITECTURE.md)** - Technical details
- **[API_EXAMPLES.md](addons/household-chores/API_EXAMPLES.md)** - API examples

## Support

If you encounter issues:

1. Check the relevant documentation in `addons/household-chores/`
2. Review the [troubleshooting section](addons/household-chores/DEPLOYMENT.md#troubleshooting-deployment) in the deployment guide
3. Check the add-on logs in Home Assistant (Settings → Add-ons → Household Chores → Logs)
4. Open an issue on GitHub

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
