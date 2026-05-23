# Development

Parser tests use the sample API responses included in this repository.

```bash
python -m unittest discover -s tests
```

## Local Modbus TCP Development

The repository includes an experimental Modbus TCP data layer for local
Leonardo devices. It can be selected during config flow setup, while the
existing cloud API implementation remains available as a separate connection
mode.

To probe a local device:

```bash
python scripts/probe_modbus.py 192.0.2.10
```

The current decoder reads holding registers `0` through `33`, decodes the
32-bit float byte order used by the local Modbus TCP interface, and scales
cumulative energy meters to kWh.

## Example Use Cases

- Monitor live solar production and home consumption.
- Track grid import/export energy.
- Automate from positive-only grid import/export and battery charge/discharge
  power sensors.
- Trigger automations from binary status sensors such as grid exporting or
  battery discharging.
- Watch battery charge, discharge, state of charge, voltage, and current.
- Use wallbox power/energy sensors in EV charging automations.
