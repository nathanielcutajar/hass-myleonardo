import json
import sys
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from parser import get_sensor_value  # noqa: E402


def load_sample(name):
    with open(
        ROOT / "tests" / "fixtures" / name,
        encoding="utf-8",
    ) as sample:
        return json.load(sample)


class MyLeonardoParserTest(unittest.TestCase):
    def test_realtime_values(self):
        data = load_sample("realtime.json")

        self.assertEqual(
            get_sensor_value(data, "PacPV", "realtime"),
            369,
        )
        self.assertEqual(
            get_sensor_value(data, "Pbat", "realtime"),
            -348.81,
        )
        self.assertIsNone(
            get_sensor_value(data, "Ppwm", "realtime"),
        )
        self.assertIsNotNone(
            get_sensor_value(
                data,
                "Rtime",
                "realtime",
                value_type="timestamp",
            ),
        )

    def test_energy_values_are_scaled_to_kwh(self):
        data = load_sample("energy.json")

        self.assertEqual(
            get_sensor_value(data, "EacPV", "energy", 0.001),
            412.35,
        )
        self.assertEqual(
            get_sensor_value(
                data,
                "Stime",
                "energy",
                value_type="date",
            ),
            date(2026, 5, 1),
        )

    def test_advanced_values(self):
        data = load_sample("advanced.json")

        self.assertEqual(
            get_sensor_value(data, "avgPacHome", "advanced"),
            706.333,
        )
        self.assertIsNone(
            get_sensor_value(data, "Tint", "advanced"),
        )

    def test_list_values_use_newest_bucket(self):
        data = {
            "data": [
                {
                    "Stime": "2026-05-16T10:00:00",
                    "EacPV": 1000,
                },
                {
                    "Stime": "2026-05-17T10:00:00",
                    "EacPV": 2000,
                },
            ]
        }

        self.assertEqual(
            get_sensor_value(data, "EacPV", "energy", 0.001),
            2,
        )

    def test_bad_shapes_return_none(self):
        self.assertIsNone(
            get_sensor_value({"data": []}, "PacPV", "realtime"),
        )
        self.assertIsNone(
            get_sensor_value({"data": {}}, "EacPV", "energy"),
        )


if __name__ == "__main__":
    unittest.main()
