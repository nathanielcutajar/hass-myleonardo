import json
import sys
import unittest
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from parser import (  # noqa: E402
    as_date,
    as_datetime,
    as_float,
    get_binary_sensor_value,
    get_sensor_value,
)


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

    def test_monthly_energy_values_are_scaled_to_kwh(self):
        data = load_sample("energy_monthly.json")

        self.assertEqual(
            get_sensor_value(data, "EacPV", "energy_monthly", 0.001),
            487.24,
        )
        self.assertEqual(
            get_sensor_value(data, "EacGridOut", "energy_monthly", 0.001),
            71.48,
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

    def test_advanced_complete_values(self):
        data = load_sample("advanced_complete.json")

        self.assertEqual(
            get_sensor_value(data, "SoH", "advanced_complete"),
            99,
        )
        self.assertEqual(
            get_sensor_value(data, "VEoC", "advanced_complete"),
            53.2,
        )
        self.assertIsNone(
            get_sensor_value(data, "FlagWRM", "advanced_complete"),
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
        self.assertIsNone(
            get_binary_sensor_value(
                {"data": {"grid_power": 1}},
                "grid_power",
                "modbus",
                "unknown",
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

    def test_scalar_converters_reject_bad_values(self):
        self.assertIsNone(as_float("bad"))
        self.assertIsNone(as_float(None))
        self.assertIsNone(as_date(None))
        self.assertIsNone(as_date("not-a-date"))
        self.assertIsNone(as_datetime(None))
        self.assertIsNone(as_datetime("not-a-date"))

    def test_timestamp_converter_handles_dates_and_utc_suffix(self):
        parsed_date = as_datetime("2026-05-22")
        parsed_utc = as_datetime("2026-05-22T10:30:00Z")

        self.assertEqual(parsed_date.date(), date(2026, 5, 22))
        self.assertEqual(
            parsed_utc,
            datetime.fromisoformat("2026-05-22T10:30:00+00:00"),
        )

    def test_list_values_ignore_non_dict_buckets(self):
        data = {
            "data": [
                "bad",
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


if __name__ == "__main__":
    unittest.main()
