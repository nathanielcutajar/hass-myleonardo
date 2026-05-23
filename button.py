from datetime import datetime, timedelta
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.util import dt as dt_util

from .helpers import (
    get_device_identifier,
    get_device_info,
    get_entity_unique_id,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    device_identifier = get_device_identifier(entry)

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
        self._attr_unique_id = get_entity_unique_id(
            device_identifier,
            "button",
            "refresh",
        )

    @property
    def device_info(self):
        return get_device_info(self._device_identifier)

    async def async_press(self):
        coordinators = (
            getattr(self._entry.runtime_data, "realtime", None),
            getattr(self._entry.runtime_data, "energy", None),
            getattr(self._entry.runtime_data, "energy_monthly", None),
            getattr(self._entry.runtime_data, "advanced", None),
            getattr(self._entry.runtime_data, "advanced_complete", None),
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
