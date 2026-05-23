import asyncio
import importlib
import sys
import types
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ClientError(Exception):
    pass


class ClientResponseError(ClientError):
    def __init__(self, request_info, history, status):
        super().__init__(status)
        self.status = status


def load_api_module():
    """Load api.py as a package module while stubbing external packages."""
    package = types.ModuleType("myleonardo")
    package.__path__ = [str(ROOT)]
    sys.modules["myleonardo"] = package

    aiohttp = types.ModuleType("aiohttp")
    aiohttp.ClientError = ClientError
    aiohttp.ClientResponseError = ClientResponseError
    sys.modules.setdefault("aiohttp", aiohttp)

    homeassistant = types.ModuleType("homeassistant")
    util = types.ModuleType("homeassistant.util")
    dt = types.ModuleType("homeassistant.util.dt")
    dt.now = lambda: datetime(2026, 5, 20, 12, 0, 0)
    dt.start_of_local_day = lambda value: value.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    sys.modules.setdefault("homeassistant", homeassistant)
    sys.modules.setdefault("homeassistant.util", util)
    sys.modules.setdefault("homeassistant.util.dt", dt)

    return importlib.import_module("myleonardo.api")


api_module = load_api_module()


class FakeResponse:
    def __init__(self, status, payload=None):
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        if self.status >= 400:
            raise ClientResponseError(
                None,
                (),
                status=self.status,
            )

    async def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response=None, exc=None):
        self.response = response
        self.exc = exc
        self.calls = []

    def get(self, url, headers=None, params=None):
        self.calls.append({
            "url": url,
            "headers": headers,
            "params": params,
        })

        if self.exc:
            raise self.exc

        return self.response


class MyLeonardoApiTest(unittest.TestCase):
    def test_realtime_request_uses_token_and_complete_type(self):
        session = FakeSession(
            FakeResponse(
                200,
                {
                    "data": {},
                },
            )
        )
        api = api_module.MyLeonardoApi(
            session,
            "token",
            "plant",
        )

        asyncio.run(api.async_get_realtime())

        call = session.calls[0]
        self.assertEqual(
            call["url"],
            "https://myleonardo.western.it/api/external/realtime/plant/",
        )
        self.assertEqual(call["headers"]["Authorization"], "Token token")
        self.assertEqual(call["params"], {"type": "C"})

    def test_monthly_energy_request_uses_monthly_type(self):
        session = FakeSession(FakeResponse(200, {"data": []}))
        api = api_module.MyLeonardoApi(session, "token", "plant")

        asyncio.run(api.async_get_monthly_energy())

        call = session.calls[0]
        self.assertEqual(
            call["url"],
            "https://myleonardo.western.it/api/external/energy/plant/",
        )
        self.assertEqual(call["params"]["type"], "M")
        self.assertIn("date_from", call["params"])
        self.assertIn("date_to", call["params"])

    def test_advanced_complete_request_uses_complete_type(self):
        session = FakeSession(FakeResponse(200, {"data": []}))
        api = api_module.MyLeonardoApi(session, "token", "plant")

        asyncio.run(api.async_get_advanced_complete())

        call = session.calls[0]
        self.assertEqual(
            call["url"],
            "https://myleonardo.western.it/api/external/advanced/plant/",
        )
        self.assertEqual(call["params"]["type"], "C")
        self.assertIn("date_from", call["params"])
        self.assertIn("date_to", call["params"])

    def test_shared_endpoint_calls_are_rate_limited(self):
        session = FakeSession(FakeResponse(200, {"data": []}))
        api = api_module.MyLeonardoApi(session, "token", "plant")
        sleeps = []
        original_sleep = api_module.asyncio.sleep

        async def fake_sleep(delay):
            sleeps.append(delay)

        async def run_calls():
            api_module.asyncio.sleep = fake_sleep
            try:
                await api.async_get_energy()
                await api.async_get_monthly_energy()
            finally:
                api_module.asyncio.sleep = original_sleep

        asyncio.run(run_calls())

        self.assertEqual(len(sleeps), 1)
        self.assertGreaterEqual(sleeps[0], 19)

    def test_auth_status_raises_auth_error(self):
        session = FakeSession(FakeResponse(401))
        api = api_module.MyLeonardoApi(session, "token", "plant")

        with self.assertRaises(api_module.MyLeonardoAuthError):
            asyncio.run(api.async_get_realtime())

    def test_forbidden_status_is_recoverable_api_error(self):
        session = FakeSession(FakeResponse(403))
        api = api_module.MyLeonardoApi(session, "token", "plant")

        with self.assertRaises(api_module.MyLeonardoApiError):
            asyncio.run(api.async_get_realtime())

    def test_plant_not_found_raises_plant_error(self):
        session = FakeSession(FakeResponse(404))
        api = api_module.MyLeonardoApi(session, "token", "plant")

        with self.assertRaises(api_module.MyLeonardoPlantError):
            asyncio.run(api.async_get_realtime())

    def test_connection_error_is_normalized(self):
        session = FakeSession(exc=ClientError())
        api = api_module.MyLeonardoApi(session, "token", "plant")

        with self.assertRaises(api_module.MyLeonardoConnectionError):
            asyncio.run(api.async_get_realtime())

    def test_unexpected_payload_raises_api_error(self):
        session = FakeSession(FakeResponse(200, {"unexpected": {}}))
        api = api_module.MyLeonardoApi(session, "token", "plant")

        with self.assertRaises(api_module.MyLeonardoApiError):
            asyncio.run(api.async_get_realtime())


if __name__ == "__main__":
    unittest.main()
