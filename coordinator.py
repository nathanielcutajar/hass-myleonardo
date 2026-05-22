from datetime import timedelta
import logging
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers import issue_registry as ir
from .api import MyLeonardoApiError, MyLeonardoAuthError
from .const import DOMAIN
from .modbus_api import MyLeonardoModbusError

_LOGGER = logging.getLogger(__name__)
REPAIR_ISSUE_FAILURE_THRESHOLD = 3


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
        self._failure_count = 0
        self._repair_issue_created = False

    async def _async_fetch_data(self):
        raise NotImplementedError

    async def _async_handle_unavailable(self, err):
        self._failure_count += 1

        if not self._was_unavailable:
            _LOGGER.warning(
                "MyLeonardo endpoint %s became unavailable: %s",
                self._endpoint_name,
                err,
            )
            self._was_unavailable = True

        if (
            self._failure_count >= REPAIR_ISSUE_FAILURE_THRESHOLD
            and not self._repair_issue_created
        ):
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                f"{self._endpoint_name}_unavailable",
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key="endpoint_unavailable",
                translation_placeholders={
                    "endpoint": self._endpoint_name,
                },
            )
            self._repair_issue_created = True

    async def _async_handle_available(self):
        self._failure_count = 0

        if self._repair_issue_created:
            ir.async_delete_issue(
                self.hass,
                DOMAIN,
                f"{self._endpoint_name}_unavailable",
            )
            self._repair_issue_created = False

        if self._was_unavailable:
            _LOGGER.info(
                "MyLeonardo endpoint %s is available again",
                self._endpoint_name,
            )
            self._was_unavailable = False

    async def _async_update_data(self):
        try:
            data = await self._async_fetch_data()
        except MyLeonardoAuthError as err:
            # Tell Home Assistant to start the reauth flow.
            raise ConfigEntryAuthFailed from err
        except MyLeonardoApiError as err:
            await self._async_handle_unavailable(err)
            raise UpdateFailed(str(err)) from err
        except MyLeonardoModbusError as err:
            await self._async_handle_unavailable(err)
            raise UpdateFailed(str(err)) from err

        await self._async_handle_available()

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


class MyLeonardoModbusCoordinator(
    MyLeonardoBaseCoordinator,
):
    def __init__(self, hass, api, update_interval):
        super().__init__(
            hass,
            api,
            f"{DOMAIN}_modbus",
            update_interval,
        )

    async def _async_fetch_data(self):
        return await self.api.async_get_data()
