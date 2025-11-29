# Home Assistant Chores Add-ons Repository

Repository containing Home Assistant add-ons for household chore management and notifications.

## Add-ons

### Household Chores Reminder

A smart reminder system for household chores that sends notifications to your phones and integrates with Home Assistant.

**Features:**
- Define household tasks with flexible scheduling (daily, weekly, monthly, quarterly, yearly)
- Automatic reminders at optimal times (16:00 on weekdays, 08:00 on weekends)
- Send notifications to multiple family members' phones
- Mark tasks as done or postpone directly from notifications
- Persistent storage of tasks and device configurations
- Full REST API for managing tasks and devices
- Timezone support (Europe/Stockholm by default, customizable)

**Installation:**

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**
2. Click the **three-dot menu (⋮)** and select **"Repositories"**
3. Add this repository: `https://github.com/johan-ankarsrum/home-assistant-chores-addons`
4. The **"Household Chores Reminder"** add-on will appear in the store
5. Click **"Install"** and follow the quick start guide

**Quick Start:**

Once installed, refer to the add-on documentation:
- [Quick Start Guide](addons/household-chores/QUICKSTART.md) - 5-minute setup
- [Full README](addons/household-chores/README.md) - Complete documentation
- [Deployment Guide](addons/household-chores/DEPLOYMENT.md) - Detailed setup instructions

## Repository Structure

```
home-assistant-chores-addons/
└── addons/
    └── household-chores/          # Household Chores Reminder add-on
        ├── Dockerfile             # Docker container definition
        ├── config.yaml            # Add-on configuration
        ├── requirements.txt       # Python dependencies
        ├── app/                   # Application code
        │   ├── main.py           # FastAPI application
        │   ├── models.py         # Data models
        │   ├── storage.py        # Persistence layer
        │   ├── scheduler.py      # Scheduling logic
        │   └── ha_client.py      # HA integration
        ├── README.md             # Add-on documentation
        ├── QUICKSTART.md         # Quick start guide
        ├── DEPLOYMENT.md         # Deployment instructions
        ├── ARCHITECTURE.md       # Technical architecture
        ├── API_EXAMPLES.md       # API examples
        └── [other docs...]
```

## Requirements

- Home Assistant 2024.1.0 or later
- Docker (if deploying manually)
- Mobile app integration enabled in Home Assistant

## Documentation

Complete documentation for the Household Chores Reminder add-on is located in `addons/household-chores/`:

- **[README.md](addons/household-chores/README.md)** - Full feature overview and setup
- **[QUICKSTART.md](addons/household-chores/QUICKSTART.md)** - 5-minute setup guide
- **[DEPLOYMENT.md](addons/household-chores/DEPLOYMENT.md)** - Deployment options and troubleshooting
- **[ARCHITECTURE.md](addons/household-chores/ARCHITECTURE.md)** - Technical architecture
- **[API_EXAMPLES.md](addons/household-chores/API_EXAMPLES.md)** - API testing examples
- **[CHECKLIST.md](addons/household-chores/CHECKLIST.md)** - Setup verification checklist

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
