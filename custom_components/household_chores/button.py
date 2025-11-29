"""Button platform for Household Chores Reminder."""
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

DOMAIN = "household_chores"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        [
            ReloadTasksButton(hass, entry),
            SyncDevicesButton(hass, entry),
        ],
        update_before_add=True,
    )


class ReloadTasksButton(ButtonEntity):
    """Button to reload tasks."""

    _attr_name = "Reload Household Chores Tasks"
    _attr_unique_id = "household_chores_reload_tasks"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the button."""
        self.hass = hass
        self._entry = entry

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.debug("Reload tasks button pressed")


class SyncDevicesButton(ButtonEntity):
    """Button to sync devices."""

    _attr_name = "Sync Household Chores Devices"
    _attr_unique_id = "household_chores_sync_devices"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the button."""
        self.hass = hass
        self._entry = entry

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.debug("Sync devices button pressed")
