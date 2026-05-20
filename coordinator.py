from datetime import timedelta
import logging
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from .api import MyLeonardoApiError, MyLeonardoAuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MyLeonardoBaseCoordinator(
    DataUpdateCoordinator,
):
    def __init__(
        self,
        hass,
        api,
        name,
        update_interval,
    ):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(
                seconds=update_interval,
            ),
        )

        self.api = api
        self._endpoint_name = name
        self._was_unavailable = False

    async def _async_fetch_data(self):
        raise NotImplementedError

    async def _async_update_data(self):
        try:
            data = await self._async_fetch_data()
        except MyLeonardoAuthError as err:
            # Tell Home Assistant to start the reauth flow.
            raise ConfigEntryAuthFailed from err
        except MyLeonardoApiError as err:
            if not self._was_unavailable:
                _LOGGER.warning(
                    "MyLeonardo endpoint %s became unavailable: %s",
                    self._endpoint_name,
                    err,
                )
                self._was_unavailable = True

            raise UpdateFailed(str(err)) from err

        if self._was_unavailable:
            _LOGGER.info(
                "MyLeonardo endpoint %s is available again",
                self._endpoint_name,
            )
            self._was_unavailable = False

        return data


class MyLeonardoCoordinator(
    MyLeonardoBaseCoordinator,
):
    def __init__(self, hass, api, update_interval):
        super().__init__(
            hass,
            api,
            DOMAIN,
            update_interval,
        )

    async def _async_fetch_data(self):
        return await self.api.async_get_realtime()


class MyLeonardoEnergyCoordinator(
    MyLeonardoBaseCoordinator,
):
    def __init__(self, hass, api, update_interval):
        super().__init__(
            hass,
            api,
            f"{DOMAIN}_energy",
            update_interval,
        )

    async def _async_fetch_data(self):
        return await self.api.async_get_energy()


class MyLeonardoAdvancedCoordinator(
    MyLeonardoBaseCoordinator,
):
    def __init__(self, hass, api, update_interval):
        super().__init__(
            hass,
            api,
            f"{DOMAIN}_advanced",
            update_interval,
        )

    async def _async_fetch_data(self):
        return await self.api.async_get_advanced()
