import asyncio
from dataclasses import asdict, dataclass
import math
import struct


MODBUS_PORT = 502
MODBUS_UNIT_ID = 1
MODBUS_REGISTER_START = 0
MODBUS_REGISTER_COUNT = 34
MODBUS_FUNCTION_READ_HOLDING = 3


class MyLeonardoModbusError(Exception):
    """Base error for local MyLeonardo Modbus failures."""


class MyLeonardoModbusConnectionError(MyLeonardoModbusError):
    """Raised when the local Modbus TCP device cannot be reached."""


class MyLeonardoModbusProtocolError(MyLeonardoModbusError):
    """Raised when the local Modbus TCP response is invalid."""


@dataclass(frozen=True)
class MyLeonardoModbusReading:
    battery_soc: float | None
    battery_voltage: float | None
    battery_temperature: float | None
    battery_power: float | None
    pv_power: float | None
    ac_input_voltage: float | None
    ac_output_voltage: float | None
    grid_power: float | None
    grid_l1_power: float | None
    grid_l2_power: float | None
    grid_l3_power: float | None
    home_power: float | None
    grid_import_energy: float | None
    grid_export_energy: float | None
    home_energy: float | None
    pv_energy: float | None
    battery_charge_energy: float | None
    battery_discharge_energy: float | None

    def as_dict(self):
        return asdict(self)


# Register numbers come from W-Hi-Stick_ModbusTCP_Protocol_1_0.pdf.
# Energy meters are scaled to kWh based on live validation against the inverter.
MODBUS_SENSOR_MAP = (
    (0, "battery_soc", 1),
    (2, "battery_voltage", 1),
    (4, "battery_temperature", 1),
    (6, "battery_power", 1),
    (8, "pv_power", 1),
    (10, "ac_input_voltage", 1),
    (12, "ac_output_voltage", 1),
    (14, "grid_l1_power", 1),
    (16, "grid_l2_power", 1),
    (18, "grid_l3_power", 1),
    (20, "home_power", 1),
    (22, "grid_import_energy", 0.001),
    (24, "grid_export_energy", 0.001),
    (26, "home_energy", 0.001),
    (28, "pv_energy", 0.001),
    (30, "battery_charge_energy", 0.001),
    (32, "battery_discharge_energy", 0.001),
)


def sum_grid_phases(values):
    """Return total net grid power from any valid phase values."""
    phases = [
        values["grid_l1_power"],
        values["grid_l2_power"],
        values["grid_l3_power"],
    ]
    valid_phases = [
        phase
        for phase in phases
        if phase is not None
    ]

    if not valid_phases:
        return None

    return sum(valid_phases)


def decode_modbus_float(payload, register):
    """Decode the W-Hi-Stick 32-bit float at a holding register address."""
    offset = register * 2
    raw = payload[offset:offset + 4]

    if len(raw) != 4:
        raise MyLeonardoModbusProtocolError(
            f"Register {register} is missing from Modbus response"
        )

    value = struct.unpack("<f", raw)[0]

    if math.isnan(value) or math.isinf(value) or abs(value) > 1e20:
        return None

    return value


def parse_modbus_registers(payload):
    """Parse holding register bytes into a MyLeonardo local reading."""
    expected_length = MODBUS_REGISTER_COUNT * 2

    if len(payload) < expected_length:
        raise MyLeonardoModbusProtocolError(
            "Modbus response did not include all requested registers"
        )

    values = {}

    for register, key, scale in MODBUS_SENSOR_MAP:
        value = decode_modbus_float(payload, register)
        values[key] = None if value is None else value * scale

    values["grid_power"] = sum_grid_phases(values)

    return MyLeonardoModbusReading(**values)


class MyLeonardoModbusApi:
    def __init__(
        self,
        host,
        port=MODBUS_PORT,
        unit_id=MODBUS_UNIT_ID,
        timeout=5,
    ):
        self._host = host
        self._port = port
        self._unit_id = unit_id
        self._timeout = timeout
        self._transaction_id = 0

    async def async_get_data(self):
        payload = await self.async_read_holding_registers(
            MODBUS_REGISTER_START,
            MODBUS_REGISTER_COUNT,
        )

        return {
            "data": parse_modbus_registers(payload).as_dict(),
        }

    async def async_read_holding_registers(self, start, count):
        self._transaction_id = (self._transaction_id + 1) % 65536
        transaction_id = self._transaction_id

        pdu = (
            bytes([MODBUS_FUNCTION_READ_HOLDING])
            + start.to_bytes(2, "big")
            + count.to_bytes(2, "big")
        )
        request = (
            transaction_id.to_bytes(2, "big")
            + b"\x00\x00"
            + (len(pdu) + 1).to_bytes(2, "big")
            + bytes([self._unit_id])
            + pdu
        )

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._timeout,
            )
        except OSError as err:
            raise MyLeonardoModbusConnectionError(
                "Unable to connect to local MyLeonardo Modbus TCP device"
            ) from err
        except asyncio.TimeoutError as err:
            raise MyLeonardoModbusConnectionError(
                "Timed out connecting to local MyLeonardo Modbus TCP device"
            ) from err

        try:
            writer.write(request)
            await writer.drain()

            header = await asyncio.wait_for(
                reader.readexactly(7),
                timeout=self._timeout,
            )
            response_transaction_id = int.from_bytes(header[0:2], "big")
            protocol_id = int.from_bytes(header[2:4], "big")
            length = int.from_bytes(header[4:6], "big")

            if response_transaction_id != transaction_id:
                raise MyLeonardoModbusProtocolError(
                    "Modbus response transaction id did not match request"
                )

            if protocol_id != 0:
                raise MyLeonardoModbusProtocolError(
                    "Modbus response used an unexpected protocol id"
                )

            body = await asyncio.wait_for(
                reader.readexactly(length - 1),
                timeout=self._timeout,
            )
        except asyncio.IncompleteReadError as err:
            raise MyLeonardoModbusProtocolError(
                "Local MyLeonardo Modbus TCP response was incomplete"
            ) from err
        except asyncio.TimeoutError as err:
            raise MyLeonardoModbusConnectionError(
                "Timed out reading from local MyLeonardo Modbus TCP device"
            ) from err
        finally:
            writer.close()
            await writer.wait_closed()

        return self._parse_read_holding_response(body)

    def _parse_read_holding_response(self, body):
        if len(body) < 2:
            raise MyLeonardoModbusProtocolError(
                "Local MyLeonardo Modbus TCP response was too short"
            )

        function_code = body[0]

        if function_code & 0x80:
            raise MyLeonardoModbusProtocolError(
                f"Modbus exception response code {body[1]}"
            )

        if function_code != MODBUS_FUNCTION_READ_HOLDING:
            raise MyLeonardoModbusProtocolError(
                f"Unexpected Modbus function code {function_code}"
            )

        byte_count = body[1]
        payload = body[2:2 + byte_count]

        if len(payload) != byte_count:
            raise MyLeonardoModbusProtocolError(
                "Local MyLeonardo Modbus TCP payload was incomplete"
            )

        return payload
