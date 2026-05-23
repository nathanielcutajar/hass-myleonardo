import importlib
import sys
import types
import unittest
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_helpers_module():
    package = types.ModuleType("myleonardo")
    package.__path__ = [str(ROOT)]
    sys.modules["myleonardo"] = package

    return importlib.import_module("myleonardo.helpers")


helpers = load_helpers_module()


class FakeEntry:
    def __init__(self, data):
        self.data = data


@dataclass
class Description:
    key: str = "power"
    name: str = "Power"
    translation_key: str = "power"
    source: str = "realtime"
    source_key: str | None = None
    enabled_default: bool = True
    unit: str = "W"
    device_class: str = "power"
    state_class: str = "measurement"


@dataclass
class MinimalDescription:
    key: str = "status"
    name: str = "Status"
    translation_key: str = "status"
    source: str = "realtime"
    source_key: str | None = None
    enabled_default: bool = False


class MyLeonardoHelpersTest(unittest.TestCase):
    def test_get_connection_type_defaults_to_cloud(self):
        self.assertEqual(
            helpers.get_connection_type(FakeEntry({})),
            helpers.CONNECTION_TYPE_CLOUD,
        )

    def test_uses_modbus_realtime_for_modbus_and_hybrid(self):
        self.assertTrue(
            helpers.uses_modbus_realtime(
                FakeEntry({
                    helpers.CONF_CONNECTION_TYPE:
                    helpers.CONNECTION_TYPE_MODBUS,
                })
            )
        )
        self.assertTrue(
            helpers.uses_modbus_realtime(
                FakeEntry({
                    helpers.CONF_CONNECTION_TYPE:
                    helpers.CONNECTION_TYPE_HYBRID,
                })
            )
        )
        self.assertFalse(
            helpers.uses_modbus_realtime(FakeEntry({}))
        )

    def test_get_device_identifier_prefers_plant_key(self):
        self.assertEqual(
            helpers.get_device_identifier(
                FakeEntry({
                    helpers.CONF_PLANT_KEY: "plant",
                    helpers.CONF_MODBUS_HOST: "192.0.2.10",
                })
            ),
            "plant",
        )
        self.assertEqual(
            helpers.get_device_identifier(
                FakeEntry({
                    helpers.CONF_MODBUS_HOST: "192.0.2.10",
                })
            ),
            "192.0.2.10",
        )

    def test_device_info_and_unique_id(self):
        self.assertEqual(
            helpers.get_entity_unique_id("Plant", "Realtime", "Power"),
            "plant_realtime_power",
        )

        device_info = helpers.get_device_info("plant")

        self.assertEqual(device_info["manufacturer"], "Western Co.")
        self.assertEqual(device_info["name"], "MyLeonardo Solar plant")
        self.assertIn(
            (helpers.DOMAIN, "plant"),
            device_info["identifiers"],
        )

    def test_description_source_key_uses_override_or_key(self):
        self.assertEqual(
            helpers.get_description_source_key(
                Description(key="derived", source_key="raw")
            ),
            "raw",
        )
        self.assertEqual(
            helpers.get_description_source_key(Description(key="raw")),
            "raw",
        )

    def test_set_entity_metadata(self):
        entity = types.SimpleNamespace()
        description = Description()

        helpers.set_entity_description_metadata(entity, description)
        helpers.set_entity_device_metadata(
            entity,
            "plant",
            description.source,
            description.key,
        )

        self.assertIs(entity.entity_description, description)
        self.assertEqual(entity._attr_name, "Power")
        self.assertEqual(entity._attr_translation_key, "power")
        self.assertEqual(entity._attr_entity_registry_enabled_default, True)
        self.assertEqual(entity._attr_native_unit_of_measurement, "W")
        self.assertEqual(entity._attr_device_class, "power")
        self.assertEqual(entity._attr_state_class, "measurement")
        self.assertEqual(entity._device_identifier, "plant")
        self.assertEqual(entity._attr_unique_id, "plant_realtime_power")

    def test_set_entity_metadata_handles_minimal_description(self):
        entity = types.SimpleNamespace()

        helpers.set_entity_description_metadata(
            entity,
            MinimalDescription(),
        )

        self.assertEqual(entity._attr_name, "Status")
        self.assertFalse(entity._attr_entity_registry_enabled_default)
        self.assertFalse(hasattr(entity, "_attr_native_unit_of_measurement"))


if __name__ == "__main__":
    unittest.main()
