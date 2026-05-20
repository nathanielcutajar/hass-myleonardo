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

    def test_sample_responses_are_covered_except_identifiers(self):
        exposed = {
            item["key"]
            for item in load_descriptions()
        }

        for name in ("realtime", "energy", "advanced"):
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

    def test_unique_id_template_includes_source(self):
        sensor = (ROOT / "sensor.py").read_text(encoding="utf-8")

        self.assertRegex(
            sensor,
            re.escape("{plant_key}_{description.source}_{description.key}"),
        )


if __name__ == "__main__":
    unittest.main()
