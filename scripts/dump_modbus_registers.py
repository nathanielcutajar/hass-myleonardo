import argparse
import math
import socket
import struct


def read_registers(host, port, start, count, unit_id, timeout):
    pdu = (
        bytes([3])
        + start.to_bytes(2, "big")
        + count.to_bytes(2, "big")
    )
    request = (
        b"\x00\x01"
        + b"\x00\x00"
        + (len(pdu) + 1).to_bytes(2, "big")
        + bytes([unit_id])
        + pdu
    )

    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(request)
        header = sock.recv(7)
        length = int.from_bytes(header[4:6], "big")
        body = b""

        while len(body) < length - 1:
            body += sock.recv(length - 1 - len(body))

    return body[2:2 + body[1]]


def decode_float(raw, fmt):
    value = struct.unpack(fmt, raw)[0]

    if math.isnan(value) or math.isinf(value):
        return "NaN"

    if abs(value) > 1e12:
        return f"{value:.3e}"

    return f"{value:.6g}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--unit-id", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=5)
    args = parser.parse_args()

    payload = read_registers(
        args.host,
        args.port,
        args.start,
        args.count,
        args.unit_id,
        args.timeout,
    )

    print("Register raw words:")
    for register in range(args.start, args.start + args.count):
        offset = (register - args.start) * 2
        word = payload[offset:offset + 2]
        print(
            f"{register:02d}: {word.hex(' ')} "
            f"uint16={int.from_bytes(word, 'big')}"
        )

    print("\nFloat decode at each even register:")
    for register in range(args.start, args.start + args.count - 1, 2):
        offset = (register - args.start) * 2
        raw = payload[offset:offset + 4]
        swapped = raw[2:4] + raw[0:2]
        print(
            f"{register:02d} raw={raw.hex(' ')} "
            f"le={decode_float(raw, '<f')} "
            f"be={decode_float(raw, '>f')} "
            f"ws_be={decode_float(swapped, '>f')} "
            f"ws_le={decode_float(swapped, '<f')}"
        )


if __name__ == "__main__":
    main()
