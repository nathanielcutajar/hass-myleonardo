import json
import sys
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from parser import get_binary_sensor_value, get_sensor_value  # noqa: E402


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

    def test_modbus_values_use_dict_payload(self):
        data = {
            "data": {
                "pv_power": 3662,
            }
        }

        self.assertEqual(
            get_sensor_value(data, "pv_power", "modbus"),
            3662,
        )

    def test_positive_value_type_returns_positive_side(self):
        data = {
            "data": {
                "grid_power": 3184,
            }
        }

        self.assertEqual(
            get_sensor_value(data, "grid_power", "modbus", value_type="positive"),
            3184,
        )

        data["data"]["grid_power"] = -1200

        self.assertEqual(
            get_sensor_value(data, "grid_power", "modbus", value_type="positive"),
            0,
        )

    def test_negative_abs_value_type_returns_export_or_discharge_side(self):
        data = {
            "data": {
                "grid_power": -1200,
            }
        }

        self.assertEqual(
            get_sensor_value(
                data,
                "grid_power",
                "modbus",
                value_type="negative_abs",
            ),
            1200,
        )

        data["data"]["grid_power"] = 3184

        self.assertEqual(
            get_sensor_value(
                data,
                "grid_power",
                "modbus",
                value_type="negative_abs",
            ),
            0,
        )

    def test_binary_sensor_value_uses_signed_threshold(self):
        data = {
            "data": {
                "grid_power": -1200,
                "pv_power": 3662,
            }
        }

        self.assertTrue(
            get_binary_sensor_value(
                data,
                "pv_power",
                "modbus",
                "above",
            )
        )
        self.assertTrue(
            get_binary_sensor_value(
                data,
                "grid_power",
                "modbus",
                "below",
            )
        )
        self.assertFalse(
            get_binary_sensor_value(
                data,
                "grid_power",
                "modbus",
                "above",
            )
        )

    def test_binary_sensor_value_returns_none_for_bad_values(self):
        self.assertIsNone(
            get_binary_sensor_value(
                {"data": {"grid_power": None}},
                "grid_power",
                "modbus",
                "below",
            )
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
