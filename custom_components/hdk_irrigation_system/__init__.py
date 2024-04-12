"""setup script."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, VERSION
from .controller import Controller

_LOGGER = logging.getLogger(__name__)

_LOGGER.info(
    """\n
    =========================================
    Custom Irrigation System by Paulus Handke
    Version: %s
    =========================================\n""",
    VERSION,
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Setup function."""
    # hass.states.async_set("hello_state.world", "Paulus")
    # hass.data.setdefault()
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub.Controller(
    # hass=hass, config_entry=entry.data, entry_id=entry.entry_id)
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = Controller(
        hass=hass, config=config_entry.data, entry_id=config_entry.entry_id
    )
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Return boolean to indicate that initialization was successful.

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
