import argparse
import asyncio
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modbus_api import MyLeonardoModbusApi  # noqa: E402


async def async_main():
    parser = argparse.ArgumentParser(
        description="Probe a MyLeonardo W-Hi-Stick Modbus TCP endpoint."
    )
    parser.add_argument("host", help="W-Hi-Stick or inverter IP address")
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--unit-id", type=int, default=1)
    args = parser.parse_args()

    api = MyLeonardoModbusApi(
        args.host,
        port=args.port,
        unit_id=args.unit_id,
    )
    reading = (await api.async_get_data())["data"]

    for key, value in reading.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(async_main())
