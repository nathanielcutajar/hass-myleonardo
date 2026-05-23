import asyncio
import importlib
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def install_homeassistant_stubs():
    voluptuous = types.ModuleType("voluptuous")
    homeassistant = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")
    helpers = types.ModuleType("homeassistant.helpers")
    aiohttp_client = types.ModuleType("homeassistant.helpers.aiohttp_client")
    selector = types.ModuleType("homeassistant.helpers.selector")

    class ConfigFlow:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__()

        def __init__(self):
            self.hass = None
            self.context = {}
            self.unique_id = None
            self.current_entries = []

        async def async_set_unique_id(self, unique_id):
            self.unique_id = unique_id

        def _abort_if_unique_id_configured(self):
            for entry in self._async_current_entries():
                if entry.unique_id == self.unique_id:
                    return self.async_abort(reason="already_configured")

        def _async_current_entries(self):
            return self.current_entries

        def async_show_form(self, **kwargs):
            return {
                "type": "form",
                **kwargs,
            }

        def async_create_entry(self, **kwargs):
            return {
                "type": "create_entry",
                **kwargs,
            }

        def async_abort(self, **kwargs):
            return {
                "type": "abort",
                **kwargs,
            }

    class OptionsFlow:
        def async_show_form(self, **kwargs):
            return {
                "type": "form",
                **kwargs,
            }

        def async_create_entry(self, **kwargs):
            return {
                "type": "create_entry",
                **kwargs,
            }

    class Selector:
        def __init__(self, config=None):
            self.config = config

    class SelectorMode:
        BOX = "box"
        DROPDOWN = "dropdown"

    class TextSelectorType:
        PASSWORD = "password"

    class Required:
        def __init__(self, key, default=None):
            self.key = key
            self.default = default

        def __hash__(self):
            return hash((self.key, self.default))

        def __eq__(self, other):
            return (
                isinstance(other, Required)
                and self.key == other.key
                and self.default == other.default
            )

    voluptuous.Required = Required
    voluptuous.Schema = lambda schema: schema
    config_entries.ConfigFlow = ConfigFlow
    config_entries.OptionsFlow = OptionsFlow
    aiohttp_client.async_get_clientsession = lambda hass: hass.session
    selector.BooleanSelector = Selector
    selector.NumberSelector = Selector
    selector.NumberSelectorConfig = lambda **kwargs: kwargs
    selector.NumberSelectorMode = SelectorMode
    selector.SelectSelector = Selector
    selector.SelectSelectorConfig = lambda **kwargs: kwargs
    selector.SelectSelectorMode = SelectorMode
    selector.TextSelector = Selector
    selector.TextSelectorConfig = lambda **kwargs: kwargs
    selector.TextSelectorType = TextSelectorType

    sys.modules["voluptuous"] = voluptuous
    sys.modules["homeassistant"] = homeassistant
    sys.modules["homeassistant.config_entries"] = config_entries
    sys.modules["homeassistant.helpers"] = helpers
    sys.modules["homeassistant.helpers.aiohttp_client"] = aiohttp_client
    sys.modules["homeassistant.helpers.selector"] = selector


def load_config_flow_module():
    install_homeassistant_stubs()

    package = types.ModuleType("myleonardo")
    package.__path__ = [str(ROOT)]
    sys.modules["myleonardo"] = package

    sys.modules.pop("myleonardo.config_flow", None)
    return importlib.import_module("myleonardo.config_flow")


config_flow = load_config_flow_module()


class FakeConfigEntry:
    def __init__(
        self,
        entry_id="entry",
        unique_id="plant",
        data=None,
        options=None,
    ):
        self.entry_id = entry_id
        self.unique_id = unique_id
        self.data = data or {}
        self.options = options or {}


class FakeConfigEntries:
    def __init__(self, entries=None):
        self.entries = {
            entry.entry_id: entry
            for entry in entries or []
        }
        self.updated = []
        self.reloaded = []

    def async_get_entry(self, entry_id):
        return self.entries[entry_id]

    def async_update_entry(self, entry, **kwargs):
        self.updated.append((entry, kwargs))
        if "data" in kwargs:
            entry.data = kwargs["data"]
        if "unique_id" in kwargs:
            entry.unique_id = kwargs["unique_id"]

    async def async_reload(self, entry_id):
        self.reloaded.append(entry_id)


class FakeHass:
    def __init__(self, entries=None):
        self.session = object()
        self.config_entries = FakeConfigEntries(entries)


def build_flow(entries=None):
    flow = config_flow.MyLeonardoConfigFlow()
    flow.hass = FakeHass(entries)
    flow.current_entries = entries or []
    return flow


class MyLeonardoConfigFlowRuntimeTest(unittest.TestCase):
    def test_clean_input_trims_values_and_sets_connection_type(self):
        flow = build_flow()

        self.assertEqual(
            flow._clean_user_input({
                config_flow.CONF_API_KEY: " token ",
                config_flow.CONF_PLANT_KEY: " plant ",
            }),
            {
                config_flow.CONF_CONNECTION_TYPE:
                config_flow.CONNECTION_TYPE_CLOUD,
                config_flow.CONF_API_KEY: "token",
                config_flow.CONF_PLANT_KEY: "plant",
            },
        )
        self.assertEqual(
            flow._clean_modbus_input({
                config_flow.CONF_MODBUS_HOST: " 192.0.2.1 ",
                config_flow.CONF_MODBUS_PORT: 502,
            }),
            {
                config_flow.CONF_CONNECTION_TYPE:
                config_flow.CONNECTION_TYPE_MODBUS,
                config_flow.CONF_MODBUS_HOST: "192.0.2.1",
                config_flow.CONF_MODBUS_PORT: 502,
            },
        )

    def test_user_step_routes_to_selected_mode(self):
        async def run_case(connection_type, expected_step):
            flow = build_flow()
            called = []

            async def fake_step():
                called.append(expected_step)
                return {"step": expected_step}

            setattr(flow, f"async_step_{expected_step}", fake_step)

            result = await flow.async_step_user({
                config_flow.CONF_CONNECTION_TYPE: connection_type,
            })

            self.assertEqual(result, {"step": expected_step})
            self.assertEqual(called, [expected_step])

        asyncio.run(
            run_case(
                config_flow.CONNECTION_TYPE_CLOUD,
                "cloud",
            )
        )
        asyncio.run(
            run_case(
                config_flow.CONNECTION_TYPE_MODBUS,
                "modbus",
            )
        )
        asyncio.run(
            run_case(
                config_flow.CONNECTION_TYPE_HYBRID,
                "hybrid",
            )
        )

    def test_cloud_step_creates_entry_after_validation(self):
        flow = build_flow()

        async def fake_validate(user_input):
            return None

        flow._async_try_validate_input = fake_validate

        result = asyncio.run(
            flow.async_step_cloud({
                config_flow.CONF_API_KEY: " token ",
                config_flow.CONF_PLANT_KEY: " plant ",
            })
        )

        self.assertEqual(result["type"], "create_entry")
        self.assertEqual(result["title"], "MyLeonardo")
        self.assertEqual(result["data"][config_flow.CONF_API_KEY], "token")
        self.assertEqual(flow.unique_id, "plant")

    def test_cloud_step_shows_validation_error(self):
        flow = build_flow()

        async def fake_validate(user_input):
            return "invalid_auth"

        flow._async_try_validate_input = fake_validate

        result = asyncio.run(
            flow.async_step_cloud({
                config_flow.CONF_API_KEY: "bad",
                config_flow.CONF_PLANT_KEY: "plant",
            })
        )

        self.assertEqual(result["type"], "form")
        self.assertEqual(result["errors"], {"base": "invalid_auth"})

    def test_modbus_and_hybrid_steps_create_entries(self):
        async def run_modbus():
            flow = build_flow()
            flow._async_try_validate_modbus_input = (
                lambda user_input: asyncio.sleep(0, result=None)
            )

            return await flow.async_step_modbus({
                config_flow.CONF_MODBUS_HOST: " 192.0.2.1 ",
                config_flow.CONF_MODBUS_PORT: 502,
            })

        async def run_hybrid():
            flow = build_flow()
            flow._async_try_validate_hybrid_input = (
                lambda user_input: asyncio.sleep(0, result=None)
            )

            return await flow.async_step_hybrid({
                config_flow.CONF_API_KEY: " token ",
                config_flow.CONF_PLANT_KEY: " plant ",
                config_flow.CONF_MODBUS_HOST: " 192.0.2.1 ",
                config_flow.CONF_MODBUS_PORT: 502,
            })

        self.assertEqual(
            asyncio.run(run_modbus())["data"][
                config_flow.CONF_CONNECTION_TYPE
            ],
            config_flow.CONNECTION_TYPE_MODBUS,
        )
        self.assertEqual(
            asyncio.run(run_hybrid())["data"][
                config_flow.CONF_CONNECTION_TYPE
            ],
            config_flow.CONNECTION_TYPE_HYBRID,
        )

    def test_validation_error_mapping(self):
        async def run_case(error, expected):
            flow = build_flow()

            async def fake_validate(user_input):
                raise error

            flow._async_validate_input = fake_validate

            self.assertEqual(
                await flow._async_try_validate_input({}),
                expected,
            )

        asyncio.run(
            run_case(
                config_flow.MyLeonardoAuthError(),
                "invalid_auth",
            )
        )
        asyncio.run(
            run_case(
                config_flow.MyLeonardoPlantError(),
                "invalid_plant",
            )
        )
        asyncio.run(
            run_case(
                config_flow.MyLeonardoConnectionError(),
                "cannot_connect",
            )
        )
        asyncio.run(
            run_case(
                config_flow.MyLeonardoApiError(),
                "unknown",
            )
        )

    def test_hybrid_validation_short_circuits_cloud_error(self):
        flow = build_flow()
        called_modbus = []

        async def fake_cloud(user_input):
            return "invalid_auth"

        async def fake_modbus(user_input):
            called_modbus.append(True)

        flow._async_try_validate_input = fake_cloud
        flow._async_try_validate_modbus_input = fake_modbus

        result = asyncio.run(flow._async_try_validate_hybrid_input({}))

        self.assertEqual(result, "invalid_auth")
        self.assertEqual(called_modbus, [])

    def test_reauth_success_updates_entry(self):
        entry = FakeConfigEntry(
            data={
                config_flow.CONF_API_KEY: "old",
                config_flow.CONF_PLANT_KEY: "plant",
            }
        )
        flow = build_flow([entry])
        flow.context = {"entry_id": entry.entry_id}

        async def fake_validate(user_input):
            return None

        flow._async_try_validate_input = fake_validate

        asyncio.run(flow.async_step_reauth({}))
        result = asyncio.run(
            flow.async_step_reauth_confirm({
                config_flow.CONF_API_KEY: " new ",
            })
        )

        self.assertEqual(result["reason"], "reauth_successful")
        self.assertEqual(entry.data[config_flow.CONF_API_KEY], "new")
        self.assertEqual(flow.hass.config_entries.reloaded, [entry.entry_id])

    def test_reconfigure_cloud_success_updates_entry(self):
        entry = FakeConfigEntry(
            data={
                config_flow.CONF_CONNECTION_TYPE:
                config_flow.CONNECTION_TYPE_CLOUD,
                config_flow.CONF_API_KEY: "old",
                config_flow.CONF_PLANT_KEY: "old-plant",
            }
        )
        flow = build_flow([entry])
        flow.context = {"entry_id": entry.entry_id}

        async def fake_validate(user_input):
            return None

        flow._async_try_validate_input = fake_validate

        asyncio.run(flow.async_step_reconfigure({}))
        result = asyncio.run(
            flow.async_step_reconfigure_confirm({
                config_flow.CONF_API_KEY: " new ",
                config_flow.CONF_PLANT_KEY: " new-plant ",
            })
        )

        self.assertEqual(result["reason"], "reconfigure_successful")
        self.assertEqual(entry.unique_id, "new-plant")
        self.assertEqual(entry.data[config_flow.CONF_API_KEY], "new")

    def test_options_flow_outputs_internal_option_keys(self):
        entry = FakeConfigEntry(
            data={
                config_flow.CONF_CONNECTION_TYPE:
                config_flow.CONNECTION_TYPE_CLOUD,
            }
        )
        options_flow = config_flow.MyLeonardoOptionsFlow()
        options_flow.config_entry = entry

        result = asyncio.run(
            options_flow.async_step_init({
                config_flow.OPTIONS_FIELDS[
                    config_flow.CONF_ENABLE_REALTIME_SENSORS
                ]: True,
                config_flow.OPTIONS_FIELDS[
                    config_flow.CONF_ENABLE_ENERGY_SENSORS
                ]: False,
                config_flow.OPTIONS_FIELDS[
                    config_flow.CONF_ENABLE_MONTHLY_ENERGY_SENSORS
                ]: False,
                config_flow.OPTIONS_FIELDS[
                    config_flow.CONF_ENABLE_ADVANCED_SENSORS
                ]: True,
                config_flow.OPTIONS_FIELDS[
                    config_flow.CONF_ENABLE_ADVANCED_COMPLETE_SENSORS
                ]: False,
                config_flow.OPTIONS_FIELDS[
                    config_flow.CONF_REALTIME_SCAN_INTERVAL
                ]: 30,
                config_flow.OPTIONS_FIELDS[
                    config_flow.CONF_ENERGY_SCAN_INTERVAL
                ]: 300,
                config_flow.OPTIONS_FIELDS[
                    config_flow.CONF_ADVANCED_SCAN_INTERVAL
                ]: 120,
            })
        )

        self.assertEqual(result["type"], "create_entry")
        self.assertEqual(
            result["data"][config_flow.CONF_ENABLE_ENERGY_SENSORS],
            False,
        )


if __name__ == "__main__":
    unittest.main()
