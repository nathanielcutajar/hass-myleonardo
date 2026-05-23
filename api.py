import asyncio
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
        self._rate_limit_locks = {}
        self._rate_limit_next_available = {}

    def _rate_limit_seconds(self, path):
        if "/api/external/realtime/" in path:
            return 5

        if (
            "/api/external/energy/" in path
            or "/api/external/advanced/" in path
        ):
            return 20

        return 0

    async def _async_wait_for_rate_limit(self, path):
        delay = self._rate_limit_seconds(path)

        if delay == 0:
            return

        lock = self._rate_limit_locks.setdefault(path, asyncio.Lock())

        async with lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            next_available = self._rate_limit_next_available.get(path, now)

            if next_available > now:
                await asyncio.sleep(next_available - now)
                now = loop.time()

            self._rate_limit_next_available[path] = now + delay

    async def _async_get(self, path, params):
        url = f"{BASE_URL}{path}"
        await self._async_wait_for_rate_limit(path)

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

    async def async_get_monthly_energy(self):
        today = dt_util.now()

        start = today.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        # Monthly energy uses the same endpoint as daily energy with type M.
        return await self._async_get(
            f"/api/external/energy/{self._plant_key}/",
            {
                "type": "M",
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

    async def async_get_advanced_complete(self):
        today = dt_util.now()

        yesterday = today - timedelta(days=1)

        # Complete advanced data is larger, so expose only selected fields.
        return await self._async_get(
            f"/api/external/advanced/{self._plant_key}/",
            {
                "type": "C",
                "date_from": int(yesterday.timestamp()),
                "date_to": int(today.timestamp()),
            },
        )
