# MyLeonardo

Home Assistant custom integration for MyLeonardo solar and battery systems.
MyLeonardo is the cloud portal used by supported Western Co. Leonardo solar and
battery systems. This integration can read the external MyLeonardo API or a
local W-Hi-Stick Modbus TCP endpoint and exposes plant power, energy, battery,
wallbox, and diagnostic values in Home Assistant.

## Features

- Cloud polling through the MyLeonardo external API.
- Experimental local polling through W-Hi-Stick Modbus TCP.
- Hybrid mode with local realtime values and cloud energy/history values.
- Config flow setup with either API credentials or local Modbus host details.
- Realtime, energy, and advanced sensor groups.
- Redacted diagnostics support.
- Reauthentication flow when the API key is rejected.

## Installation

### HACS custom repository

1. In HACS, open **Custom repositories**.
2. Add this repository URL.
3. Select **Integration** as the category.
4. Install **MyLeonardo**.
5. Restart Home Assistant.

This repository stores the integration files at the repository root, so
`hacs.json` uses `content_in_root: true`.

### Manual

Copy the integration files into:

```text
custom_components/myleonardo/
```

Then restart Home Assistant.

## Configuration

Add the integration from **Settings > Devices & services > Add integration** and
search for **MyLeonardo**.

Choose one connection type during setup.

For **Cloud API**, you will need:

- MyLeonardo API key
- MyLeonardo plant key

The API key is stored in the Home Assistant config entry. It is redacted from
diagnostics.

For **Local Modbus TCP**, you will need:

- W-Hi-Stick or inverter IP address / hostname
- Modbus TCP port, usually `502`

Local Modbus TCP is experimental. It reads the inverter directly and does not
use the MyLeonardo cloud service.

For **Hybrid**, you will need both sets of details. Hybrid mode uses Local
Modbus TCP for fast realtime plant values and the MyLeonardo cloud API for
daily energy and advanced diagnostic values.

## Options

The integration options allow you to:

- Enable or disable realtime sensors
- Enable or disable energy sensors
- Enable or disable advanced diagnostic sensors
- Set the realtime polling interval in seconds
- Set the energy polling interval in seconds
- Set the advanced polling interval in seconds

Polling intervals are clamped by the setup form to the API rate limits:

- Realtime: minimum 5 seconds
- Energy: minimum 20 seconds
- Advanced: minimum 20 seconds
- Local Modbus TCP: minimum 1 second, defaults to 5 seconds

Hybrid mode uses the Local Modbus TCP interval for realtime sensors and the
cloud API intervals for energy and advanced sensors.

## Sensors

The integration exposes sensors grouped by the API endpoint they come from:

- Realtime sensors
- Energy sensors
- Advanced sensors
- Binary status sensors

Energy values are converted to kWh where the API returns Wh-style values.
Advanced sensors are diagnostic and disabled by default in the entity registry.

## Sensor Reference

| Endpoint | Sensor | API field | Unit | Enabled by default |
| --- | --- | --- | --- | --- |
| Realtime | Production Power | `PacPV` | WATT | Yes |
| Realtime | Home Power | `PacHome` | WATT | Yes |
| Realtime | Grid Power | `PacGrid` | WATT | Yes |
| Realtime | Grid Import Power | `PacGrid` | WATT | No |
| Realtime | Grid Export Power | `PacGrid` | WATT | No |
| Realtime | Battery Power | `Pbat` | WATT | Yes |
| Realtime | Battery Charge Power | `Pbat` | WATT | No |
| Realtime | Battery Discharge Power | `Pbat` | WATT | No |
| Realtime | Load Power | `Pload` | WATT | Yes |
| Realtime | PWM Power | `Ppwm` | WATT | Yes |
| Realtime | Battery SOC | `SoC` | BATTERY | Yes |
| Realtime | Battery Temperature | `Tbat` | CELSIUS | Yes |
| Realtime | Wallbox Power | `walc_pread` | WATT | Yes |
| Realtime | Wallbox Energy | `walc_energy` | KILO_WATT_HOUR | Yes |
| Realtime | Updated | `Rtime` | TIMESTAMP | No |
| Energy | Solar Energy Today | `EacPV` | KILO_WATT_HOUR | Yes |
| Energy | Home Consumption Today | `EacHome` | KILO_WATT_HOUR | Yes |
| Energy | Grid Import Today | `EacGridIn` | KILO_WATT_HOUR | Yes |
| Energy | Grid Export Today | `EacGridOut` | KILO_WATT_HOUR | Yes |
| Energy | Battery Charged Today | `Einbat` | KILO_WATT_HOUR | Yes |
| Energy | Battery Discharged Today | `Eoutbat` | KILO_WATT_HOUR | Yes |
| Energy | PWM Today | `Epwm` | KILO_WATT_HOUR | No |
| Energy | Load Today | `Eload` | KILO_WATT_HOUR | Yes |
| Energy | Bucket Date | `Stime` | DATE | No |
| Advanced | Average Production | `avgPacPV` | WATT | Yes |
| Advanced | Average Home Consumption | `avgPacHome` | WATT | Yes |
| Advanced | Average Grid Power | `avgPacGrid` | WATT | Yes |
| Advanced | Average Battery Power | `avgPbat` | WATT | Yes |
| Advanced | Average Load Power | `avgPload` | WATT | Yes |
| Advanced | Average PWM Power | `avgPpwm` | WATT | Yes |
| Advanced | Battery Voltage | `Vbat` | V | Yes |
| Advanced | Battery Current | `Ibat` | A | Yes |
| Advanced | Load Current | `Iload` | A | Yes |
| Advanced | PWM Current | `Ipwm` | A | Yes |
| Advanced | Battery Cycles | `nCicli` | - | Yes |
| Advanced | Battery Temperature | `Tbat` | CELSIUS | Yes |
| Advanced | Internal Temperature | `Tint` | CELSIUS | Yes |
| Advanced | Battery SOC | `SoC` | BATTERY | Yes |
| Advanced | AC Input Voltage | `VacIn` | V | Yes |
| Advanced | AC Input Current | `IacIn` | A | Yes |
| Advanced | AC Output Voltage | `VacOut` | V | Yes |
| Advanced | AC Output Current | `IacOut` | A | Yes |
| Advanced | AC Input Frequency | `FacIn` | Hz | Yes |
| Advanced | AC Output Frequency | `FacOut` | Hz | Yes |
| Advanced | Bucket Time | `Stime` | TIMESTAMP | No |
| Local Modbus | Grid Power | `grid_power` | WATT | Yes |
| Local Modbus | Grid Import Power | `grid_power` | WATT | No |
| Local Modbus | Grid Export Power | `grid_power` | WATT | No |
| Local Modbus | Grid L1 Power | `grid_l1_power` | WATT | No |
| Local Modbus | Grid L2 Power | `grid_l2_power` | WATT | No |
| Local Modbus | Grid L3 Power | `grid_l3_power` | WATT | No |
| Local Modbus | Battery Charge Power | `battery_power` | WATT | No |
| Local Modbus | Battery Discharge Power | `battery_power` | WATT | No |

In Local Modbus TCP mode, `Grid Power` is derived from all valid phase values.
For grid power values, positive means importing from the grid and negative
means exporting / feed-in.

Derived split power sensors are disabled by default. They convert signed power
values into positive-only import/export and charge/discharge sensors for
dashboards and automations.

## Binary Status Sensors

The integration also creates binary sensors from realtime power values.

| Status | Cloud API field | Local Modbus field |
| --- | --- | --- |
| Producing | `PacPV > 0` | `pv_power > 0` |
| Grid importing | `PacGrid > 0` | `grid_power > 0` |
| Grid exporting | `PacGrid < 0` | `grid_power < 0` |
| Battery charging | `Pbat > 0` | `battery_power > 0` |
| Battery discharging | `Pbat < 0` | `battery_power < 0` |

Hybrid mode uses the local Modbus fields for these binary status sensors.

## Energy Dashboard

Use energy sensors, not realtime power sensors, when configuring Home
Assistant's Energy dashboard. Power sensors use W and show what is happening
right now; energy sensors use kWh and are suitable for long-term statistics.

### Cloud API

Cloud API mode exposes daily energy sensors from the MyLeonardo energy
endpoint. These sensors reset with the daily API bucket and are marked as
`total_increasing` so Home Assistant can handle the reset.

| Energy dashboard section | Recommended entity |
| --- | --- |
| Solar production | Solar Energy Today |
| Grid consumption | Grid Import Today |
| Return to grid | Grid Export Today |
| Battery charged from solar/grid | Battery Charged Today |
| Battery discharged to home/grid | Battery Discharged Today |

### Local Modbus TCP

Local Modbus TCP mode exposes cumulative total sensors where the inverter
returns supported values. These are preferred for the Energy dashboard because
they are lifetime-style meters rather than daily buckets.

| Energy dashboard section | Recommended entity |
| --- | --- |
| Solar production | PV Energy Total |
| Grid consumption | Grid Import Energy Total, if supported by the device |
| Return to grid | Grid Export Energy Total, if supported by the device |
| Battery charged from solar/grid | Battery Charge Energy Total |
| Battery discharged to home/grid | Battery Discharge Energy Total, if supported by the device |

Some W-Hi-Stick devices return unsupported or `NaN` values for local grid
energy totals. When that happens, use Hybrid mode or Cloud API mode for grid
energy values.

### Hybrid

Hybrid mode is usually the best fit when Home Assistant can reach the local
device and cloud credentials are available.

| Energy dashboard section | Recommended entity |
| --- | --- |
| Solar production | PV Energy Total from local Modbus, or Solar Energy Today from cloud if local totals are unavailable |
| Grid consumption | Grid Import Today from cloud |
| Return to grid | Grid Export Today from cloud |
| Battery charged from solar/grid | Battery Charge Energy Total from local Modbus, or Battery Charged Today from cloud |
| Battery discharged to home/grid | Battery Discharged Today from cloud if the local total is unavailable |

Do not use `Production Power`, `Grid Power`, `Home Power`, or `Battery Power`
as Energy dashboard energy sources.

## Data Updates

The integration uses Home Assistant data coordinators. Each endpoint has its own
coordinator and polling interval:

- Realtime: defaults to 30 seconds
- Energy: defaults to 300 seconds
- Advanced: defaults to 120 seconds
- Local Modbus TCP: defaults to 5 seconds

If MyLeonardo rejects the API key, Home Assistant starts a reauthentication
flow. If the service is temporarily unavailable, affected entities are marked
unavailable until polling succeeds again.

After repeated update failures, the integration creates a Home Assistant repair
issue for the affected endpoint. The repair issue is cleared automatically once
that endpoint updates successfully again.

## Notes

The MyLeonardo API documentation lists these rate limits:

- Realtime: max one request every 5 seconds
- Energy: max one request every 20 seconds
- Advanced: max one request every 20 seconds

The integration polls within those limits.

## Known Limitations

- Cloud API mode depends on the MyLeonardo cloud service.
- Hybrid mode depends on both the local Modbus device and the MyLeonardo cloud
  service; realtime values can be local while history values still come from
  the cloud.
- Local Modbus TCP mode requires Home Assistant to reach the W-Hi-Stick or
  inverter on the local network.
- Energy semantics depend on the MyLeonardo daily energy endpoint. The
  cloud API mode queries from local midnight to now for today's energy sensors.
- Discovery is not implemented; setup requires manually entering an API key and
  plant key or local Modbus host.

## Roadmap

Potential future additions:

- Monthly energy sensors using the MyLeonardo energy endpoint with `type: M`.
- Selected advanced-complete diagnostic sensors using the advanced endpoint with
  `type: C`.
- Full Home Assistant config flow and diagnostics test coverage.
- A wider landscape logo asset for Home Assistant views that prefer a full logo
  instead of a square icon.

## Troubleshooting

- If setup fails with an authentication error, verify the API key.
- If setup fails with a plant error, verify the plant key.
- If entities become unavailable, check MyLeonardo service availability and the
  Home Assistant logs.
- If Home Assistant shows a MyLeonardo repair issue, follow the repair text and
  check cloud availability, local network access, or connection details.
- Use Home Assistant diagnostics when opening issues. API key, plant key, and
  device identifiers are redacted.

## Removal

Remove the integration from **Settings > Devices & services**, then restart
Home Assistant if requested. Manual installations can also remove the
`custom_components/myleonardo/` directory after the integration entry has been
deleted.

## Example Use Cases

- Monitor live solar production and home consumption.
- Track grid import/export energy.
- Automate from positive-only grid import/export and battery charge/discharge
  power sensors.
- Trigger automations from binary status sensors such as grid exporting or
  battery discharging.
- Watch battery charge, discharge, state of charge, voltage, and current.
- Use wallbox power/energy sensors in EV charging automations.

## Development

Parser tests use the sample API responses included in this repository.

```bash
python -m unittest discover -s tests
```

### Local Modbus TCP development

The repository includes an experimental Modbus TCP data layer for W-Hi-Stick
devices. It can be selected during config flow setup, while the existing cloud
API implementation remains available as a separate connection mode.

To probe a local device:

```bash
python scripts/probe_modbus.py 192.0.2.10
```

The current decoder reads holding registers `0` through `33`, decodes the
32-bit float byte order used by the W-Hi-Stick protocol, and scales cumulative
energy meters to kWh.

## Support

Open an issue on GitHub with diagnostics from Home Assistant when possible.
