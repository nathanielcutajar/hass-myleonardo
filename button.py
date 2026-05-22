from datetime import datetime, timedelta
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.util import dt as dt_util

from .const import (
    CONF_MODBUS_HOST,
    CONF_PLANT_KEY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    device_identifier = entry.data.get(
        CONF_PLANT_KEY,
        entry.data.get(CONF_MODBUS_HOST),
    )

    async_add_entities([
        MyLeonardoRefreshButton(
            entry,
            device_identifier,
        )
    ])


class MyLeonardoRefreshButton(ButtonEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True
    _attr_name = "Refresh"
    _attr_translation_key = "refresh"

    def __init__(self, entry, device_identifier):
        self._entry = entry
        self._device_identifier = device_identifier
        self._last_manual_refresh = {}
        self._attr_unique_id = f"{device_identifier}_refresh".lower()

    @property
    def device_info(self):
        # Attach the refresh control to the same device as the sensors.
        return {
            "identifiers": {
                (
                    DOMAIN,
                    self._device_identifier,
                )
            },
            "manufacturer": "Western Co.",
            "name": f"MyLeonardo Solar {self._device_identifier}",
            "model": "Leonardo",
        }

    async def async_press(self):
        coordinators = (
            self._entry.runtime_data.realtime,
            self._entry.runtime_data.energy,
            self._entry.runtime_data.advanced,
        )
        now = dt_util.utcnow()

        for coordinator in coordinators:
            if coordinator is None:
                continue

            if self._manual_refresh_is_rate_limited(coordinator, now):
                continue

            self._last_manual_refresh[coordinator.name] = now
            await coordinator.async_request_refresh()

    def _manual_refresh_is_rate_limited(
        self,
        coordinator,
        now: datetime,
    ):
        last_refresh = self._last_manual_refresh.get(coordinator.name)
        update_interval = coordinator.update_interval or timedelta()

        if last_refresh is None or now - last_refresh >= update_interval:
            return False

        next_refresh = last_refresh + update_interval
        _LOGGER.info(
            "Skipping manual MyLeonardo refresh for %s because it was "
            "refreshed too recently. Try again after %s",
            coordinator.name,
            next_refresh.isoformat(),
        )

        return True
