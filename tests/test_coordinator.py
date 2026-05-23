import asyncio
import importlib
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_coordinator_module():
    package = types.ModuleType("myleonardo")
    package.__path__ = [str(ROOT)]
    sys.modules["myleonardo"] = package

    exceptions = types.ModuleType("homeassistant.exceptions")
    update_coordinator = types.ModuleType(
        "homeassistant.helpers.update_coordinator"
    )
    issue_registry = types.ModuleType(
        "homeassistant.helpers.issue_registry"
    )

    class ConfigEntryAuthFailed(Exception):
        pass

    class UpdateFailed(Exception):
        pass

    class DataUpdateCoordinator:
        def __init__(self, hass, logger, name, update_interval):
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval

    class IssueSeverity:
        WARNING = "warning"

    exceptions.ConfigEntryAuthFailed = ConfigEntryAuthFailed
    update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
    update_coordinator.UpdateFailed = UpdateFailed
    issue_registry.IssueSeverity = IssueSeverity
    issue_registry.created = []
    issue_registry.deleted = []

    def async_create_issue(*args, **kwargs):
        issue_registry.created.append((args, kwargs))

    def async_delete_issue(*args, **kwargs):
        issue_registry.deleted.append((args, kwargs))

    issue_registry.async_create_issue = async_create_issue
    issue_registry.async_delete_issue = async_delete_issue

    sys.modules["homeassistant"] = types.ModuleType("homeassistant")
    sys.modules["homeassistant.exceptions"] = exceptions
    sys.modules["homeassistant.helpers"] = types.ModuleType(
        "homeassistant.helpers"
    )
    sys.modules[
        "homeassistant.helpers.update_coordinator"
    ] = update_coordinator
    sys.modules[
        "homeassistant.helpers.issue_registry"
    ] = issue_registry

    sys.modules.pop("myleonardo.coordinator", None)
    return importlib.import_module("myleonardo.coordinator")


coordinator = load_coordinator_module()


class FakeApi:
    async def async_get_realtime(self):
        raise coordinator.MyLeonardoAuthError("auth failed")

    async def async_get_energy(self):
        raise coordinator.MyLeonardoAuthError("energy unavailable")

    async def async_get_advanced(self):
        raise coordinator.MyLeonardoAuthError("advanced unavailable")

    async def async_get_monthly_energy(self):
        raise coordinator.MyLeonardoAuthError("monthly unavailable")

    async def async_get_advanced_complete(self):
        raise coordinator.MyLeonardoAuthError("complete unavailable")

class SuccessfulApi:
    async def async_get_energy(self):
        return {"data": []}


class MyLeonardoCoordinatorTest(unittest.TestCase):
    def test_core_auth_failure_triggers_reauth(self):
        item = coordinator.MyLeonardoCoordinator(
            object(),
            FakeApi(),
            30,
        )

        with self.assertRaises(coordinator.ConfigEntryAuthFailed):
            asyncio.run(item._async_update_data())

    def test_optional_monthly_auth_failure_is_recoverable(self):
        item = coordinator.MyLeonardoMonthlyEnergyCoordinator(
            object(),
            FakeApi(),
            300,
        )

        with self.assertRaises(coordinator.UpdateFailed):
            asyncio.run(item._async_update_data())

        self.assertTrue(item._was_unavailable)
        self.assertEqual(item._failure_count, 1)

    def test_energy_auth_failure_is_recoverable(self):
        item = coordinator.MyLeonardoEnergyCoordinator(
            object(),
            FakeApi(),
            300,
        )

        with self.assertRaises(coordinator.UpdateFailed):
            asyncio.run(item._async_update_data())

        self.assertTrue(item._was_unavailable)
        self.assertEqual(item._failure_count, 1)

    def test_advanced_auth_failure_is_recoverable(self):
        item = coordinator.MyLeonardoAdvancedCoordinator(
            object(),
            FakeApi(),
            120,
        )

        with self.assertRaises(coordinator.UpdateFailed):
            asyncio.run(item._async_update_data())

        self.assertTrue(item._was_unavailable)
        self.assertEqual(item._failure_count, 1)

    def test_optional_advanced_complete_auth_failure_is_recoverable(self):
        item = coordinator.MyLeonardoAdvancedCompleteCoordinator(
            object(),
            FakeApi(),
            120,
        )

        with self.assertRaises(coordinator.UpdateFailed):
            asyncio.run(item._async_update_data())

        self.assertTrue(item._was_unavailable)
        self.assertEqual(item._failure_count, 1)

    def test_success_clears_unavailable_state(self):
        item = coordinator.MyLeonardoEnergyCoordinator(
            object(),
            SuccessfulApi(),
            300,
        )
        item._was_unavailable = True
        item._repair_issue_created = True

        result = asyncio.run(item._async_update_data())

        self.assertEqual(result, {"data": []})
        self.assertFalse(item._was_unavailable)
        self.assertFalse(item._repair_issue_created)


if __name__ == "__main__":
    unittest.main()
