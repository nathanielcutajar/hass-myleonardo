from datetime import timedelta

import aiohttp
from homeassistant.util import dt as dt_util

from .const import BASE_URL


class MyLeonardoApiError(Exception):
    """Base error for MyLeonardo API failures."""


class MyLeonardoAuthError(MyLeonardoApiError):
    """Raised when MyLeonardo rejects the API token."""


class MyLeonardoPlantError(MyLeonardoApiError):
    """Raised when MyLeonardo rejects the plant key."""


class MyLeonardoConnectionError(MyLeonardoApiError):
    """Raised when MyLeonardo cannot be reached."""


class MyLeonardoApi:
    def __init__(
        self,
        session,
        api_key,
        plant_key,
    ):
        self._session = session
        self._plant_key = plant_key

        self._headers = {
            "Accept": "application/json",
            "Authorization": f"Token {api_key}",
        }

    async def _async_get(self, path, params):
        url = f"{BASE_URL}{path}"

        try:
            # Normalize HTTP/API failures into integration-specific exceptions.
            async with self._session.get(
                url,
                headers=self._headers,
                params=params,
            ) as response:
                if response.status == 401:
                    raise MyLeonardoAuthError(
                        "Invalid MyLeonardo API token"
                    )

                if response.status == 403:
                    raise MyLeonardoApiError(
                        "MyLeonardo API rejected the request"
                    )

                if response.status == 404:
                    raise MyLeonardoPlantError(
                        "Invalid MyLeonardo plant key"
                    )

                response.raise_for_status()
                data = await response.json()
        except aiohttp.ClientResponseError as err:
            raise MyLeonardoApiError(
                f"MyLeonardo API returned HTTP {err.status}"
            ) from err
        except aiohttp.ClientError as err:
            raise MyLeonardoConnectionError(
                "Unable to connect to MyLeonardo"
            ) from err

        if not isinstance(data, dict) or "data" not in data:
            raise MyLeonardoApiError(
                "Unexpected MyLeonardo API response"
            )

        return data

    async def async_get_realtime(self):
        return await self._async_get(
            f"/api/external/realtime/{self._plant_key}/",
            {
                "type": "C",
            },
        )

    async def async_get_energy(self):
        today = dt_util.now()

        start = dt_util.start_of_local_day(today)

        # Daily energy accepts a unix timestamp range and returns bucket rows.
        return await self._async_get(
            f"/api/external/energy/{self._plant_key}/",
            {
                "type": "D",
                "date_from": int(start.timestamp()),
                "date_to": int(today.timestamp()),
            },
        )

    async def async_get_advanced(self):
        today = dt_util.now()

        yesterday = today - timedelta(days=1)

        # Basic advanced data is enough for the currently exposed sensors.
        return await self._async_get(
            f"/api/external/advanced/{self._plant_key}/",
            {
                "type": "B",
                "date_from": int(yesterday.timestamp()),
                "date_to": int(today.timestamp()),
            },
        )
