import importlib
import math
import struct
import sys
import types
import unittest
import asyncio
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
    def test_decode_modbus_float_uses_local_modbus_byte_order(self):
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

    def test_decode_modbus_float_rejects_missing_register(self):
        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            modbus_module.decode_modbus_float(b"\x00", 2)

    def test_decode_modbus_float_rejects_extreme_values(self):
        payload = build_payload({
            0: 1e30,
        })

        self.assertIsNone(
            modbus_module.decode_modbus_float(payload, 0)
        )

    def test_reading_as_dict(self):
        payload = build_payload({
            0: 54,
        })
        reading = modbus_module.parse_modbus_registers(payload)

        self.assertEqual(reading.as_dict()["battery_soc"], 54)

    def test_read_holding_response_rejects_short_body(self):
        api = modbus_module.MyLeonardoModbusApi("192.0.2.1")

        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            api._parse_read_holding_response(b"\x03")

    def test_read_holding_response_rejects_modbus_exception(self):
        api = modbus_module.MyLeonardoModbusApi("192.0.2.1")

        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            api._parse_read_holding_response(b"\x83\x02")

    def test_read_holding_response_rejects_wrong_function(self):
        api = modbus_module.MyLeonardoModbusApi("192.0.2.1")

        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            api._parse_read_holding_response(b"\x04\x00")

    def test_read_holding_response_rejects_incomplete_payload(self):
        api = modbus_module.MyLeonardoModbusApi("192.0.2.1")

        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            api._parse_read_holding_response(b"\x03\x04\x00")

    def test_read_holding_response_returns_payload(self):
        api = modbus_module.MyLeonardoModbusApi("192.0.2.1")

        self.assertEqual(
            api._parse_read_holding_response(b"\x03\x02\x01\x02"),
            b"\x01\x02",
        )

    def test_async_read_holding_registers_connection_errors(self):
        api = modbus_module.MyLeonardoModbusApi("192.0.2.1")
        original_open_connection = modbus_module.asyncio.open_connection

        async def raise_os_error(*args):
            raise OSError

        async def raise_timeout(*args):
            raise asyncio.TimeoutError

        async def run_case(side_effect):
            modbus_module.asyncio.open_connection = side_effect
            try:
                await api.async_read_holding_registers(0, 1)
            finally:
                modbus_module.asyncio.open_connection = (
                    original_open_connection
                )

        with self.assertRaises(
            modbus_module.MyLeonardoModbusConnectionError
        ):
            asyncio.run(run_case(raise_os_error))

        with self.assertRaises(
            modbus_module.MyLeonardoModbusConnectionError
        ):
            asyncio.run(run_case(raise_timeout))

    def test_async_get_data_wraps_parsed_registers(self):
        payload = build_payload({
            0: 54,
        })
        api = modbus_module.MyLeonardoModbusApi("192.0.2.1")

        async def fake_read_holding_registers(start, count):
            self.assertEqual(start, modbus_module.MODBUS_REGISTER_START)
            self.assertEqual(count, modbus_module.MODBUS_REGISTER_COUNT)
            return payload

        api.async_read_holding_registers = fake_read_holding_registers

        data = asyncio.run(api.async_get_data())

        self.assertEqual(data["data"]["battery_soc"], 54)

    def test_async_read_holding_registers_success(self):
        api = modbus_module.MyLeonardoModbusApi("192.0.2.1")
        original_open_connection = modbus_module.asyncio.open_connection

        class FakeReader:
            def __init__(self):
                self.responses = [
                    b"\x00\x01\x00\x00\x00\x05\x01",
                    b"\x03\x02\x01\x02",
                ]

            async def readexactly(self, count):
                return self.responses.pop(0)

        class FakeWriter:
            def __init__(self):
                self.closed = False
                self.request = None

            def write(self, request):
                self.request = request

            async def drain(self):
                return None

            def close(self):
                self.closed = True

            async def wait_closed(self):
                return None

        writer = FakeWriter()

        async def fake_open_connection(host, port):
            self.assertEqual(host, "192.0.2.1")
            self.assertEqual(port, modbus_module.MODBUS_PORT)
            return FakeReader(), writer

        async def run_case():
            modbus_module.asyncio.open_connection = fake_open_connection
            try:
                return await api.async_read_holding_registers(0, 1)
            finally:
                modbus_module.asyncio.open_connection = (
                    original_open_connection
                )

        payload = asyncio.run(run_case())

        self.assertEqual(payload, b"\x01\x02")
        self.assertTrue(writer.closed)
        self.assertEqual(writer.request[6], modbus_module.MODBUS_UNIT_ID)

    def test_async_read_holding_registers_rejects_bad_header(self):
        original_open_connection = modbus_module.asyncio.open_connection

        class FakeReader:
            def __init__(self, header):
                self.header = header

            async def readexactly(self, count):
                return self.header

        class FakeWriter:
            def write(self, request):
                return None

            async def drain(self):
                return None

            def close(self):
                return None

            async def wait_closed(self):
                return None

        async def run_case(header):
            api = modbus_module.MyLeonardoModbusApi("192.0.2.1")

            async def fake_open_connection(host, port):
                return FakeReader(header), FakeWriter()

            modbus_module.asyncio.open_connection = fake_open_connection
            try:
                await api.async_read_holding_registers(0, 1)
            finally:
                modbus_module.asyncio.open_connection = (
                    original_open_connection
                )

        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            asyncio.run(run_case(b"\x00\x02\x00\x00\x00\x05\x01"))

        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            asyncio.run(run_case(b"\x00\x01\x00\x01\x00\x05\x01"))

    def test_async_read_holding_registers_read_errors(self):
        original_open_connection = modbus_module.asyncio.open_connection

        class FakeWriter:
            def write(self, request):
                return None

            async def drain(self):
                return None

            def close(self):
                return None

            async def wait_closed(self):
                return None

        async def run_case(error):
            api = modbus_module.MyLeonardoModbusApi("192.0.2.1")

            class FakeReader:
                async def readexactly(self, count):
                    raise error

            async def fake_open_connection(host, port):
                return FakeReader(), FakeWriter()

            modbus_module.asyncio.open_connection = fake_open_connection
            try:
                await api.async_read_holding_registers(0, 1)
            finally:
                modbus_module.asyncio.open_connection = (
                    original_open_connection
                )

        with self.assertRaises(
            modbus_module.MyLeonardoModbusProtocolError
        ):
            asyncio.run(
                run_case(
                    asyncio.IncompleteReadError(
                        partial=b"",
                        expected=7,
                    )
                )
            )

        with self.assertRaises(
            modbus_module.MyLeonardoModbusConnectionError
        ):
            asyncio.run(run_case(asyncio.TimeoutError()))


if __name__ == "__main__":
    unittest.main()
