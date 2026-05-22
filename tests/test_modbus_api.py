import importlib
import math
import struct
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_modbus_module():
    package = types.ModuleType("myleonardo")
    package.__path__ = [str(ROOT)]
    sys.modules["myleonardo"] = package

    return importlib.import_module("myleonardo.modbus_api")


modbus_module = load_modbus_module()


def build_payload(values):
    payload = bytearray(
        modbus_module.MODBUS_REGISTER_COUNT * 2
    )

    for register, value in values.items():
        payload[register * 2:register * 2 + 4] = struct.pack(
            "<f",
            value,
        )

    return bytes(payload)


class MyLeonardoModbusApiTest(unittest.TestCase):
    def test_decode_modbus_float_uses_pdf_byte_order(self):
        payload = build_payload({
            0: 92.5,
        })

        self.assertEqual(
            modbus_module.decode_modbus_float(payload, 0),
            92.5,
        )

    def test_parse_modbus_registers_maps_realtime_values(self):
        payload = build_payload({
            0: 54,
            2: 50.18,
            4: 29.8,
            6: 2885.35,
            8: 3662,
            20: 452,
        })

        reading = modbus_module.parse_modbus_registers(payload)

        self.assertEqual(reading.battery_soc, 54)
        self.assertAlmostEqual(reading.battery_voltage, 50.18, places=2)
        self.assertAlmostEqual(reading.battery_temperature, 29.8, places=1)
        self.assertAlmostEqual(reading.battery_power, 2885.35, places=2)
        self.assertEqual(reading.pv_power, 3662)
        self.assertEqual(reading.home_power, 452)

    def test_parse_modbus_registers_uses_single_phase_grid_total(self):
        payload = build_payload({
            14: -3250,
            16: math.nan,
            18: math.nan,
        })

        reading = modbus_module.parse_modbus_registers(payload)

        self.assertEqual(reading.grid_power, -3250)

    def test_parse_modbus_registers_sums_three_phase_grid_total(self):
        payload = build_payload({
            14: 100,
            16: 200,
            18: -50,
        })

        reading = modbus_module.parse_modbus_registers(payload)

        self.assertEqual(reading.grid_power, 250)

    def test_parse_modbus_registers_returns_none_for_invalid_grid_total(self):
        payload = build_payload({
            14: math.nan,
            16: math.nan,
            18: math.nan,
        })

        reading = modbus_module.parse_modbus_registers(payload)

        self.assertIsNone(reading.grid_power)

    def test_parse_modbus_registers_scales_energy_meters_to_kwh(self):
        payload = build_payload({
            26: 549251,
            28: 2337029,
            30: 5061528,
        })

        reading = modbus_module.parse_modbus_registers(payload)

        self.assertAlmostEqual(reading.home_energy, 549.251)
        self.assertAlmostEqual(reading.pv_energy, 2337.029)
        self.assertAlmostEqual(reading.battery_charge_energy, 5061.528)

    def test_parse_modbus_registers_returns_none_for_unsupported_values(self):
        payload = build_payload({
            16: math.nan,
            18: math.inf,
        })

        reading = modbus_module.parse_modbus_registers(payload)

        self.assertIsNone(reading.grid_l2_power)
        self.assertIsNone(reading.grid_l3_power)

    def test_parse_modbus_registers_rejects_short_payload(self):
        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            modbus_module.parse_modbus_registers(b"\x00")

    def test_read_holding_response_rejects_modbus_exception(self):
        api = modbus_module.MyLeonardoModbusApi("192.0.2.1")

        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            api._parse_read_holding_response(b"\x83\x02")


if __name__ == "__main__":
    unittest.main()
