"""Platform for sensor integration."""

from __future__ import annotations

from datetime import time
import logging

# These constants are relevant to the type of entity we are using.
# See below for how they are used.
from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .controller import Controller, Cycle, Zone

from homeassistant.helpers import config_validation as cv, entity_platform, service
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


# This function is called as part of the __init__.async_setup_entry (via the
# hass.config_entries.async_forward_entry_setup call)
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add cover for passed config_entry in HA."""
    # The hub is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    # controller = hass.data[DOMAIN][config_entry.entry_id]
    # hass.loop.create_task()
    # Add all entities to HA

    new_entities = []
    # new_entities.append(CycleTime(config_entry))
    controller = hass.data[DOMAIN][config_entry.entry_id]
    # new_devices.append(CycleTime(controller))
    for zone_name, zone in controller.zones.items():
        new_entities.append(ZoneDuration(controller, zone))
    for cycle_name, cycle in controller.cycles.items():
        new_entities.append(CycleTime(controller, cycle))
    async_add_entities(new_entities)

    platform = entity_platform.async_get_current_platform()

    # create service for start one cycle with service_start_cycle()
    platform.async_register_entity_service(
        "start_one_cycle",
        {
            vol.Required("irrigation_duration"): cv.time_period,
        },
        service_start_cycle,
    )

    platform.async_register_entity_service(
        "start_one_zone",
        {
            vol.Required("irrigation_duration"): cv.time_period,
        },
        service_start_zone,
    )


async def service_start_cycle(entity, service_call):
    """test service."""
    _LOGGER.warning("service triggered!")
    await entity._controller.cycles[entity._cycle_id].start_irrigation(
        service_call.data["irrigation_duration"]
    )


async def service_start_zone(entity, service_call):
    """test service."""
    _LOGGER.warning("service triggered!")
    await entity._controller.zones[entity._zone_id].start_irrigation(
        service_call.data["irrigation_duration"]
    )

    # if new_devices:
    #     async_add_entities(new_devices)

    # platform = entity_platform.current_platform.get()
    # platform.async_register_entity_service(
    #     "testt",
    #     {vol.Required("testmodus"): cv.string},
    #     "testmest",
    # )


class CycleTime(TimeEntity, RestoreEntity):
    """Represents the start time of one irrigation cycle."""

    def __init__(self, controller: Controller, cycle: Cycle) -> None:
        """Initialize the entity."""
        self._controller = controller
        self._cycle_id = cycle._id
        self._attr_name = f"{cycle.name} Start Time "
        self._attr_unique_id = f"{self._controller.controller_id}_cycle_time"
        # self._attr_native_value = time(hour=0, minute=2)
        # self._attr_state = time(hour=0, minute=2)
        # self._controller.cycle.start_time = time(hour=0, minute=2)

    @property
    def device_info(self) -> DeviceInfo:
        """Responsible for showing information in ha device page."""
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._controller.controller_id)},
            "name": self.name,
            "sw_version": self._controller.firmware_version,
            "model": self._controller.model,
            "manufacturer": self._controller.manufacturer,
            "suggested_area": "Garden",
        }

    @property
    def available(self) -> bool:
        """Return True if controller and hub is available."""
        return self._controller.online

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        self._controller.register_callback(self.async_write_ha_state)

        laststate = await self.async_get_last_state()
        # await self.async_set_value(time.fromisoformat(laststate.state))
        if not laststate or laststate.state == "unknown":
            await self.async_set_value(time(hour=10, minute=30))
        else:
            await self.async_set_value(time.fromisoformat(laststate.state))
        return True

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass. Remove any registered call backs here."""
        self._controller.remove_callback(self.async_write_ha_state)

    async def async_set_value(self, value: time) -> None:
        """Update the current value."""
        await self._controller.cycles[self._cycle_id].set_start_time(value)
        self._attr_native_value = value
        # self.async_write_ha_state() eigentlich nicht notwendig, wird im Controller gesammelt als callback aufgerufen

    @property
    def native_value(self) -> time:
        """Return value."""
        return self._controller.cycles[self._cycle_id].start_time


class ZoneDuration(TimeEntity, RestoreEntity):
    """Represents duration of one irrigation cycle."""

    native_value = native_value = time(hour=0, minute=8)

    def __init__(
        self,
        controller: Controller,
        zone: Zone,
    ) -> None:
        """Initialize the sensor."""
        self._controller = controller
        self._zone_id = zone._id
        self._attr_name = f"{zone.name} Irrigation Duration"
        self._attr_unique_id = f"{self._controller.controller_id}_{zone.name}_duration"

    @property
    def device_info(self) -> DeviceInfo:
        """Responsible for showing information in ha device page."""
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._controller.controller_id)},
            "name": self.name,
            "sw_version": self._controller.firmware_version,
            "model": self._controller.model,
            "manufacturer": self._controller.manufacturer,
            "suggested_area": "Garden",
        }

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self._controller.online

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA. Register callbacks for state changes."""
        # Sensors should also register callbacks to HA when their state changes
        self._controller.register_callback(self.async_write_ha_state)

        laststate = await self.async_get_last_state()
        if not laststate or laststate.state == "unknown":
            await self.async_set_value(time(hour=0, minute=5))
        else:
            await self.async_set_value(time.fromisoformat(laststate.state))
        return True

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass. Remove any registered call backs here."""
        self._controller.remove_callback(self.async_write_ha_state)

    async def async_set_value(self, value: time) -> None:
        """Update the current value."""
        await self._controller.zones[self._zone_id].set_zone_duration(value)
        self._attr_native_value = value
        # self.async_write_ha_state() eigentlich nicht notwendig, wird im Controller gesammelt als callback aufgerufen

    @property
    def native_value(self) -> time:
        """Return value."""
        return self._controller.zones[self._zone_id].duration
