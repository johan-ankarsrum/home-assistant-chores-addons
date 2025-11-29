"""Sensor platform for Household Chores Reminder."""
import logging
from homeassistant.components.sensor import SensorEntity
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
    """Set up the sensor platform."""
    async_add_entities(
        [HouseholdChoresStatusSensor(hass, entry)],
        update_before_add=True,
    )


class HouseholdChoresStatusSensor(SensorEntity):
    """Status sensor for Household Chores Reminder."""

    _attr_name = "Household Chores Status"
    _attr_unique_id = "household_chores_status"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry = entry

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return "active"

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            "url": self._entry.data.get("ha_url"),
            "timezone": self._entry.data.get("timezone", "Europe/Stockholm"),
            "port": self._entry.data.get("port", 8000),
        }
