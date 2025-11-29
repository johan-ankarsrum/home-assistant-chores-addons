"""Config flow for Household Chores Reminder integration."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

_LOGGER = logging.getLogger(__name__)

DOMAIN = "household_chores"


class HouseholdChoresConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Household Chores Reminder."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate token is not empty
                if not user_input.get("ha_token"):
                    errors["ha_token"] = "invalid_token"
                else:
                    return self.async_create_entry(
                        title="Household Chores Reminder",
                        data=user_input,
                    )
            except Exception as err:
                _LOGGER.exception("Unexpected error: %s", err)
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required("ha_url", default="http://homeassistant.local:8123"): str,
                vol.Required("ha_token"): str,
                vol.Optional("timezone", default="Europe/Stockholm"): str,
                vol.Optional("port", default=8000): int,
                vol.Optional("log_level", default="info"): vol.In(
                    ["debug", "info", "warning", "error"]
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "setup_link": "https://github.com/johan-ankarsrum/home-assistant-chores-addons/blob/main/addons/household-chores/QUICKSTART.md"
            },
        )
