"""The irrigation controller wich controlls the individual zones."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import datetime, time, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(10)


class Controller:
    """Irrigation controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: list,
        entry_id,
    ) -> None:
        """Init Irrigation controller."""
        # static information
        self.firmware_version = VERSION
        self.model = "Irrigation System"
        self.manufacturer = "Paulus Handke"
        self.hass = hass
        self._config = config
        self._id = config["name"].lower()
        self._name = config["name"]
        self._entry_id = entry_id

        self._callbacks = set()
        self._loop = asyncio.get_event_loop()

        self._number_of_zones = int(config["number_of_zones"])
        # self._number_of_cycles = int(config["number_of_zones"]) TODO: number of cycles
        self._irrigation_running = False
        self.hass.states.get(self._entry_id)
        # self._cycles = Cycle(
        #     "Cycle",
        #     "Cycle",
        #     time(hour=0, minute=8),
        #     [
        #         Zone("1", zone, entity, time(hour=0, minute=9))
        #         for zone, entity in config["zones"].items()
        #     ],
        #     self,
        # )
        self._cycles = {
            f"{self._id}_cycle{cycle_numb}": Cycle(
                self,
                f"{self.controller_id}_cycle{cycle_numb}",
                f"Cycle {cycle_numb}",
                time(hour=16, minute=9),
            )
            for cycle_numb in range(1, int(config["number_of_cycles"]))
        }
        self._zones = {
            f"{self._id}_{zone}": Zone(
                self,
                f"{self.controller_id}_{zone}",
                # self.controller_id,
                zone,
                entity,
                time(hour=0, minute=9),
            )
            for zone, entity in config["zones"].items()
        }

        _LOGGER.warning(self._entry_id)

    # ======================???

    @property
    def controller_id(self) -> str:
        """Return ID for roller."""
        return self._id

    @property
    def name(self) -> str:
        """Return ID for roller."""
        return self._name

    @property
    def online(self) -> float:
        """Roller is online."""
        return True

    @property
    def irrigation_running(self) -> bool:
        """Roller is online."""
        return self._irrigation_running

    @property
    def number_of_zones(self) -> float:
        """Roller is online."""
        return self._number_of_zones

    @property
    def zones(self) -> list:
        """Roller is online."""
        return self._zones

    @property
    def cycles(self) -> list:
        """Roller is online."""
        return self._cycles

    @property
    def device_id(self) -> list:
        """Roller is online."""
        return self._id

        # ====== ??
        # self._loop.create_task(self.delayed_update())
        # ======

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when Controller changes any state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove registered callback."""
        self._callbacks.discard(callback)

    async def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()


class Cycle:
    """represents an irrigation cycle."""

    def __init__(
        self,
        controller: Controller,
        cycleid: str,
        name: str,
        cycle_start_time: time,
        # zones: list,
    ) -> None:
        """Initialize an irrigation cycle."""
        self._id = cycleid
        self.name = name
        self._start_time = cycle_start_time
        self._time_between_zones = 5
        # self._start_time = None
        # self.zones = zones
        self._controller = controller
        self._loop = asyncio.get_event_loop()
        # self.timer = self._loop.create_task(self.timing())
        self.timer = asyncio.create_task(self.timing())
        self._running = False
        # _LOGGER.error(zones)

    # async def timing(self, **kwargs: Any) -> None:

    @property
    def start_time(self) -> time | None:
        """Return start time."""
        return self._start_time

    async def set_start_time(self, value: time) -> None:
        """Set the start time of a cycle."""
        _LOGGER.debug(
            "Changing start time of %s from %s to %s",
            self.name,
            self._start_time,
            value,
        )
        self._start_time = value

    async def start_irrigation(self, value: timedelta) -> None:
        """Start one Cycle."""

        async def irrigation_task(self, **kwargs: Any):
            self._running = True
            time_wait = value.total_seconds()
            if time_wait > 0:
                _LOGGER.info("Irrigation Planned on %s - %s", self.name, value)
                await asyncio.sleep(time_wait)
            _LOGGER.info("Irrigation Started on %s", self.name)

            event_data = {
                "device_id": self._controller.device_id,
                "type": "irrigation_started",
            }
            self._controller.hass.bus.async_fire(DOMAIN, event_data)

            for _name, zone in self._controller.zones.items():
                await zone.start_irrigation(timedelta(seconds=5))
                await asyncio.sleep(4)
            _LOGGER.info("Irrigation Finished")

            event_data = {
                "device_id": self._controller.device_id,
                "type": "irrigation_stopped",
            }
            self._controller.hass.bus.async_fire(DOMAIN, event_data)

            self._running = False

        if not self._running:
            self._running_cycle_task = asyncio.create_task(irrigation_task(self))
        else:
            _LOGGER.info("%s is already running.", self.name)

    @property
    def next_run(self) -> time:
        """Return next cycle run."""
        return self._target_time

    @property
    def running(self) -> bool:
        """Return if is cycle running."""
        return self._running

    async def timing(self, **kwargs: Any) -> None:
        """Close the cover."""

        while True:
            await asyncio.sleep(1)
            now = datetime.now()
            _target_time = now.replace(second=self._start_time.minute, microsecond=0)
            await asyncio.sleep((_target_time - now).total_seconds())
            # if now > _target_time:
            if True:
                # _LOGGER.error(f"hallo ziel: {_target_time} aber: {datetime.now()} ")
                # _LOGGER.error(f"starttime: {self._start_time} ")
                self._controller.hass.states.async_set("input_boolean.testhelfer", "on")
                event_data = {
                    "device_id": self._controller.device_id,
                    "type": "irrigation_started",
                }
                # self._controller.hass.bus.async_fire(DOMAIN, event_data)
                _LOGGER.debug("turning on")
                await asyncio.sleep(30)
                _LOGGER.debug("turning off")

                self._controller.hass.states.async_set(
                    "input_boolean.testhelfer", "off"
                )
                event_data = {
                    "device_id": self._controller.device_id,
                    "type": "irrigation_stopped",
                }
                # self._controller.hass.bus.async_fire(DOMAIN, event_data)

            #     self._target_time += timedelta(minutes=1)

            #     time_difference = (self._target_time - now).total_seconds()

            #     # Warten bis zur Zielzeit
            #     # await asyncio.sleep(time_difference)
            #     _LOGGER.error(f"start time: {self.start_time.minute}")
            #     self._running = True
            #     # await self._controller.publish_updates()
            #     # for zone in self._controller.zones:
            #     #     zone.start_irrigation()
            #     await asyncio.sleep(30)
            #     # await self._controller.hass.states.async_set(
            #     #     "input_boolean.testhelfer", "off"
            #     # )
            #     self._running = False
            #     # await self._controller.publish_updates()


class Zone:
    """represents an irrigation Zone."""

    def __init__(
        self,
        controller: Controller,
        zoneid: str,
        name: str,
        entity: str,  # entity to control
        zone_duration: time,
    ) -> None:
        """Initialize an irrigation zone."""
        self._id = zoneid
        self.name = name
        self.length = zone_duration
        self._entity = entity
        self.enabled = True
        self._zone_duration = zone_duration
        self.controller = controller

    async def set_zone_duration(self, duration: time):
        """Set the irrigation duration of this zone."""
        self._zone_duration = duration
        await self.controller.publish_updates()

    async def start_irrigation(self, duration: timedelta):
        """Start irrigation of this zone."""
        # now = datetime.now()
        # targeted_time = now + self._zone_duration
        self.controller.hass.states.async_set(self._entity, "on")
        await asyncio.sleep(duration.total_seconds())
        self.controller.hass.states.async_set(self._entity, "off")
        # if now < targeted_time:
        #     self._controller.hass.states.async_set(self._entity, "on")
        # # irrigation for this zone finished
        # self._controller.hass.states.async_set(self._entity, "off")

    @property
    def duration(self) -> time:
        """Return the irrigation duration of this zone."""
        return self._zone_duration
