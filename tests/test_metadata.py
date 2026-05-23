import ast
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SensorDescriptionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.descriptions = []

    def visit_Call(self, node):
        if getattr(node.func, "id", "") == "MyLeonardoSensorDescription":
            data = {}

            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Constant):
                    data[keyword.arg] = keyword.value.value
                elif isinstance(keyword.value, ast.Attribute):
                    data[keyword.arg] = keyword.value.attr

            self.descriptions.append(data)

        self.generic_visit(node)


class BinarySensorDescriptionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.descriptions = []

    def visit_Call(self, node):
        if getattr(node.func, "id", "") == "MyLeonardoBinarySensorDescription":
            data = {}

            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Constant):
                    data[keyword.arg] = keyword.value.value
                elif isinstance(keyword.value, ast.Attribute):
                    data[keyword.arg] = keyword.value.attr

            self.descriptions.append(data)

        self.generic_visit(node)


def load_descriptions():
    tree = ast.parse(
        (ROOT / "sensor_descriptions.py").read_text(
            encoding="utf-8",
        )
    )
    visitor = SensorDescriptionVisitor()
    visitor.visit(tree)

    return visitor.descriptions


def load_binary_descriptions():
    tree = ast.parse(
        (ROOT / "binary_sensor_descriptions.py").read_text(
            encoding="utf-8",
        )
    )
    visitor = BinarySensorDescriptionVisitor()
    visitor.visit(tree)

    return visitor.descriptions


class MyLeonardoMetadataTest(unittest.TestCase):
    def test_description_keys_are_unique_per_source(self):
        pairs = [
            (
                item["source"],
                item["key"],
            )
            for item in load_descriptions()
        ]

        self.assertEqual(len(pairs), len(set(pairs)))

    def test_all_descriptions_have_translation_keys(self):
        missing = [
            item["key"]
            for item in load_descriptions()
            if "translation_key" not in item
        ]

        self.assertEqual(missing, [])

    def test_entity_translations_cover_descriptions(self):
        descriptions = load_descriptions()
        translation_keys = {
            item["translation_key"]
            for item in descriptions
        }
        strings = json.loads(
            (ROOT / "strings.json").read_text(encoding="utf-8")
        )
        string_keys = set(strings["entity"]["sensor"])

        self.assertEqual(translation_keys - string_keys, set())

    def test_icon_translations_reference_existing_entities(self):
        strings = json.loads(
            (ROOT / "strings.json").read_text(encoding="utf-8")
        )
        icons = json.loads(
            (ROOT / "icons.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(icons["entity"]["sensor"]) - set(strings["entity"]["sensor"]),
            set(),
        )
        self.assertEqual(
            set(icons["entity"]["binary_sensor"])
            - set(strings["entity"]["binary_sensor"]),
            set(),
        )

    def test_sample_responses_are_covered_except_identifiers(self):
        exposed = {
            item["key"]
            for item in load_descriptions()
        }

        for name in ("realtime", "energy", "advanced", "energy_monthly"):
            data = json.loads(
                (
                    ROOT
                    / "tests"
                    / "fixtures"
                    / f"{name}.json"
                ).read_text(encoding="utf-8")
            )["data"]
            payload_keys = (
                set(data)
                if isinstance(data, dict)
                else set(data[0])
            )
            missing = payload_keys - exposed - {"Bkey", "Dkey"}

            self.assertEqual(missing, set(), name)

        advanced_complete = json.loads(
            (
                ROOT
                / "tests"
                / "fixtures"
                / "advanced_complete.json"
            ).read_text(encoding="utf-8")
        )["data"][0]
        selected = {
            item["key"]
            for item in load_descriptions()
            if item["source"] == "advanced_complete"
        }

        self.assertEqual(selected - set(advanced_complete), set())

    def test_unique_id_template_includes_source(self):
        helpers = (ROOT / "helpers.py").read_text(encoding="utf-8")

        self.assertIn("get_entity_unique_id", helpers)
        self.assertIn("{device_identifier}_{source}_{key}", helpers)

    def test_refresh_button_platform_is_registered(self):
        init = (ROOT / "__init__.py").read_text(encoding="utf-8")
        button = (ROOT / "button.py").read_text(encoding="utf-8")
        strings = json.loads(
            (ROOT / "strings.json").read_text(encoding="utf-8")
        )

        self.assertIn("Platform.BUTTON", init)
        self.assertIn("_attr_translation_key = \"refresh\"", button)
        self.assertIn("refresh", strings["entity"]["button"])

    def test_binary_sensor_platform_is_registered(self):
        init = (ROOT / "__init__.py").read_text(encoding="utf-8")
        binary_sensor = (ROOT / "binary_sensor.py").read_text(
            encoding="utf-8"
        )
        strings = json.loads(
            (ROOT / "strings.json").read_text(encoding="utf-8")
        )

        self.assertIn("Platform.BINARY_SENSOR", init)
        self.assertIn("BinarySensorEntity", binary_sensor)
        self.assertIn("binary_sensor", strings["entity"])

    def test_repair_issue_is_registered_and_translated(self):
        coordinator = (ROOT / "coordinator.py").read_text(encoding="utf-8")
        strings = json.loads(
            (ROOT / "strings.json").read_text(encoding="utf-8")
        )

        self.assertIn("async_create_issue", coordinator)
        self.assertIn("async_delete_issue", coordinator)
        self.assertIn("endpoint_unavailable", strings["issues"])

    def test_binary_sensor_translations_cover_descriptions(self):
        translation_keys = {
            item["translation_key"]
            for item in load_binary_descriptions()
        }
        strings = json.loads(
            (ROOT / "strings.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            translation_keys - set(strings["entity"]["binary_sensor"]),
            set(),
        )

    def test_energy_sensors_use_total_increasing_state(self):
        invalid = [
            item["key"]
            for item in load_descriptions()
            if item.get("source") in ("energy", "energy_monthly")
            and item.get("device_class") == "ENERGY"
            and item.get("state_class") != "TOTAL_INCREASING"
        ]

        self.assertEqual(invalid, [])

    def test_derived_split_power_sensors_are_disabled_by_default(self):
        derived = [
            item
            for item in load_descriptions()
            if item.get("value_type") in ("positive", "negative_abs")
        ]

        self.assertEqual(len(derived), 8)
        self.assertTrue(
            all(item.get("enabled_default") is False for item in derived)
        )
        self.assertTrue(
            all("source_key" in item for item in derived)
        )

    def test_diagnostics_cover_all_cloud_coordinators(self):
        diagnostics = (ROOT / "diagnostics.py").read_text(encoding="utf-8")

        self.assertIn("energy_monthly", diagnostics)
        self.assertIn("advanced_complete", diagnostics)

    def test_runtime_data_covers_extended_cloud_coordinators(self):
        runtime_data = (ROOT / "runtime_data.py").read_text(encoding="utf-8")

        self.assertIn("energy_monthly", runtime_data)
        self.assertIn("advanced_complete", runtime_data)


if __name__ == "__main__":
    unittest.main()
