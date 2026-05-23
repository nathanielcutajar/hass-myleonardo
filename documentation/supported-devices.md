# Supported Devices

This integration is built for Western Co. Leonardo solar and battery systems
that are available through the MyLeonardo cloud portal, a local Modbus TCP
device, or both.

## Tested

- Western Co. Leonardo systems using the MyLeonardo cloud API.
- Western Co. Leonardo Pro X with local Modbus TCP.
- Single-phase systems.

## Expected To Work

- Other Western Co. Leonardo systems exposed in the MyLeonardo portal, when
  using Cloud API mode.
- Three-phase systems, when local Modbus returns valid L1, L2, and L3 grid
  values.
- Hybrid setups where Home Assistant can reach the local Modbus TCP device and
  has valid MyLeonardo API credentials.

## Known Limitations

- Devices that do not expose local Modbus TCP cannot use Local Modbus TCP
  mode.
- Some systems return unsupported or `NaN` values for local grid energy totals.
- Batteryless installations are not yet confirmed.
- Wallbox entities depend on the MyLeonardo API returning `walc_*` fields.
- Multi-inverter and multi-plant setups are not yet confirmed.
- Local-only mode is limited to values exposed by the current Modbus register
  map.
