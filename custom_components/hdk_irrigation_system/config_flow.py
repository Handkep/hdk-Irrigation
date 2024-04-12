"""Config flow for Hello World integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    EntityFilterSelectorConfig,
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

# This is the schema that used to display the UI to the user. This simple
# schema has a single required host field, but it could include a number of fields
# such as username, password etc. See other components in the HA core code for
# further examples.
# Note the input displayed to the user will be translated. See the
# translations/<lang>.json file and strings.json. See here for further information:
# https://developers.home-assistant.io/docs/config_entries_config_flow_handler/#translations
# At the time of writing I found the translations created by the scaffold didn't
# quite work as documented and always gave me the "Lokalise key references" string
# (in square brackets), rather than the actual translated value. I did not attempt to
# figure this out or look further into it.

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("number_of_zones"): TextSelector(
            TextSelectorConfig(type=TextSelectorType.NUMBER, autocomplete="asdfggggg")
        ),
        vol.Required("number_of_cycles"): TextSelector(
            TextSelectorConfig(type=TextSelectorType.NUMBER, autocomplete="asdfggggg")
        ),
        # vol.Required("zone1"): EntitySelector(
        #     EntitySelectorConfig(multiple=False)
        # ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.
    NOT USED!.
    """

    _LOGGER.error(data)

    return {"title": "datajjjjj"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy hub will notify HA of
    # changes.
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self) -> None:
        """Initialize the Cloudflare config flow."""
        self.irrigation_config: dict[str, Any] = {}
        self.irrigation_config["zones"] = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if user_input is not None:
            try:
                # info = await validate_input(self.hass, user_input)
                self.irrigation_config.update(user_input)
                return await self.async_step_zones()

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_zones(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                # info = await validate_input(self.hass, user_input)
                self.irrigation_config["zones"].update(user_input)
                return self.async_create_entry(
                    title=self.irrigation_config["name"], data=self.irrigation_config
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        STEP_ZONES_DATA_SCHEMA = vol.Schema(
            {
                vol.Required(f"zone{zone_number}"): EntitySelector(
                    EntitySelectorConfig(
                        multiple=False,
                        filter=EntityFilterSelectorConfig(
                            domain=["switch", "input_boolean"]
                        ),
                    )
                )
                for zone_number in range(
                    1, int(self.irrigation_config["number_of_zones"]) + 1
                )
            }
        )
        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="zones", data_schema=STEP_ZONES_DATA_SCHEMA, errors=errors
        )

    # async def async_step_cycles(self, user_input=None):
    #     errors = {}
    #     if user_input is not None:
    #         try:
    #             # info = await validate_input(self.hass, user_input)
    #             self.irrigation_config["zones"].update(user_input)
    #             return self.async_create_entry(
    #                 title=self.irrigation_config["name"], data=self.irrigation_config
    #             )
    #         except Exception:  # pylint: disable=broad-except
    #             _LOGGER.exception("Unexpected exception")
    #             errors["base"] = "unknown"

    #     STEP_CYCLES_DATA_SCHEMA = vol.Schema(
    #         {
    #             vol.Required(f"cycle{zone_number}"): EntitySelector(
    #                 EntitySelectorConfig(
    #                     multiple=False,
    #                     filter=EntityFilterSelectorConfig(
    #                         domain=["switch", "input_boolean"]
    #                     ),
    #                 )
    #             )
    #             for zone_number in range(
    #                 1, int(self.irrigation_config["number_of_zones"]) + 1
    #             )
    #         }
    #     )
    #     # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
    #     return self.async_show_form(
    #         step_id="cycles", data_schema=STEP_CYCLES_DATA_SCHEMA, errors=errors
    #     )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
