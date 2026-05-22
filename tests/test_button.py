import asyncio
from datetime import datetime, timedelta
import importlib
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_button_module(now):
    package = types.ModuleType("myleonardo")
    package.__path__ = [str(ROOT)]
    sys.modules["myleonardo"] = package

    components = types.ModuleType("homeassistant.components")
    button_component = types.ModuleType("homeassistant.components.button")
    button_component.ButtonEntity = object

    const = types.ModuleType("homeassistant.const")
    const.EntityCategory = types.SimpleNamespace(CONFIG="config")

    util = types.ModuleType("homeassistant.util")
    dt = types.ModuleType("homeassistant.util.dt")
    dt.utcnow = lambda: now[0]

    sys.modules["homeassistant"] = types.ModuleType("homeassistant")
    sys.modules["homeassistant.components"] = components
    sys.modules["homeassistant.components.button"] = button_component
    sys.modules["homeassistant.const"] = const
    sys.modules["homeassistant.util"] = util
    sys.modules["homeassistant.util.dt"] = dt

    sys.modules.pop("myleonardo.button", None)
    return importlib.import_module("myleonardo.button")


class FakeCoordinator:
    def __init__(self, name, seconds):
        self.name = name
        self.update_interval = timedelta(seconds=seconds)
        self.refresh_count = 0

    async def async_request_refresh(self):
        self.refresh_count += 1


class FakeEntry:
    def __init__(self, realtime, energy=None, advanced=None):
        self.runtime_data = types.SimpleNamespace(
            realtime=realtime,
            energy=energy,
            advanced=advanced,
        )


class MyLeonardoRefreshButtonTest(unittest.TestCase):
    def test_press_refreshes_active_coordinators(self):
        now = [datetime(2026, 5, 22, 12, 0, 0)]
        button_module = load_button_module(now)
        realtime = FakeCoordinator("realtime", 30)
        energy = FakeCoordinator("energy", 300)
        advanced = FakeCoordinator("advanced", 120)
        button = button_module.MyLeonardoRefreshButton(
            FakeEntry(realtime, energy, advanced),
            "plant",
        )

        asyncio.run(button.async_press())

        self.assertEqual(realtime.refresh_count, 1)
        self.assertEqual(energy.refresh_count, 1)
        self.assertEqual(advanced.refresh_count, 1)

    def test_press_skips_repeated_refresh_inside_interval(self):
        now = [datetime(2026, 5, 22, 12, 0, 0)]
        button_module = load_button_module(now)
        realtime = FakeCoordinator("realtime", 30)
        button = button_module.MyLeonardoRefreshButton(
            FakeEntry(realtime),
            "plant",
        )

        asyncio.run(button.async_press())
        now[0] = datetime(2026, 5, 22, 12, 0, 10)
        asyncio.run(button.async_press())

        self.assertEqual(realtime.refresh_count, 1)

    def test_press_allows_refresh_after_interval(self):
        now = [datetime(2026, 5, 22, 12, 0, 0)]
        button_module = load_button_module(now)
        realtime = FakeCoordinator("realtime", 30)
        button = button_module.MyLeonardoRefreshButton(
            FakeEntry(realtime),
            "plant",
        )

        asyncio.run(button.async_press())
        now[0] = datetime(2026, 5, 22, 12, 0, 30)
        asyncio.run(button.async_press())

        self.assertEqual(realtime.refresh_count, 2)

    def test_press_ignores_missing_cloud_coordinators_for_modbus(self):
        now = [datetime(2026, 5, 22, 12, 0, 0)]
        button_module = load_button_module(now)
        realtime = FakeCoordinator("modbus", 5)
        button = button_module.MyLeonardoRefreshButton(
            FakeEntry(realtime),
            "192.0.2.10",
        )

        asyncio.run(button.async_press())

        self.assertEqual(realtime.refresh_count, 1)


if __name__ == "__main__":
    unittest.main()
