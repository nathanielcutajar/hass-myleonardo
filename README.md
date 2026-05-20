# MyLeonardo

Home Assistant custom integration for MyLeonardo solar and battery systems.
MyLeonardo is the cloud portal used by supported Western Co. Leonardo solar and
battery systems. This integration reads the external MyLeonardo API and exposes
plant power, energy, battery, wallbox, and diagnostic values in Home Assistant.

## Features

- Cloud polling through the MyLeonardo external API.
- Config flow setup with API key and plant key.
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

You will need:

- MyLeonardo API key
- MyLeonardo plant key

The API key is stored in the Home Assistant config entry. It is redacted from
diagnostics.

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

## Sensors

The integration exposes sensors grouped by the API endpoint they come from:

- Realtime sensors
- Energy sensors
- Advanced sensors

Energy values are converted to kWh where the API returns Wh-style values.
Advanced sensors are diagnostic and disabled by default in the entity registry.

## Sensor Reference

| Endpoint | Sensor | API field | Unit | Enabled by default |
| --- | --- | --- | --- | --- |
| Realtime | Realtime Production | `PacPV` | WATT | Yes |
| Realtime | Realtime Home Consumption | `PacHome` | WATT | Yes |
| Realtime | Realtime Grid Power | `PacGrid` | WATT | Yes |
| Realtime | Realtime Battery Power | `Pbat` | WATT | Yes |
| Realtime | Realtime Load Power | `Pload` | WATT | Yes |
| Realtime | Realtime PWM Power | `Ppwm` | WATT | Yes |
| Realtime | Realtime Battery SOC | `SoC` | BATTERY | Yes |
| Realtime | Realtime Battery Temperature | `Tbat` | CELSIUS | Yes |
| Realtime | Realtime Wallbox Power | `walc_pread` | WATT | Yes |
| Realtime | Realtime Wallbox Energy | `walc_energy` | KILO_WATT_HOUR | Yes |
| Realtime | Realtime Updated | `Rtime` | TIMESTAMP | No |
| Energy | Energy Solar Energy Today | `EacPV` | KILO_WATT_HOUR | Yes |
| Energy | Energy Home Consumption Today | `EacHome` | KILO_WATT_HOUR | Yes |
| Energy | Energy Grid Import Today | `EacGridIn` | KILO_WATT_HOUR | Yes |
| Energy | Energy Grid Export Today | `EacGridOut` | KILO_WATT_HOUR | Yes |
| Energy | Energy Battery Charged Today | `Einbat` | KILO_WATT_HOUR | Yes |
| Energy | Energy Battery Discharged Today | `Eoutbat` | KILO_WATT_HOUR | Yes |
| Energy | Energy PWM Today | `Epwm` | KILO_WATT_HOUR | No |
| Energy | Energy Load Today | `Eload` | KILO_WATT_HOUR | Yes |
| Energy | Energy Bucket Date | `Stime` | DATE | No |
| Advanced | Advanced Average Production | `avgPacPV` | WATT | Yes |
| Advanced | Advanced Average Home Consumption | `avgPacHome` | WATT | Yes |
| Advanced | Advanced Average Grid Power | `avgPacGrid` | WATT | Yes |
| Advanced | Advanced Average Battery Power | `avgPbat` | WATT | Yes |
| Advanced | Advanced Average Load Power | `avgPload` | WATT | Yes |
| Advanced | Advanced Average PWM Power | `avgPpwm` | WATT | Yes |
| Advanced | Advanced Battery Voltage | `Vbat` | V | Yes |
| Advanced | Advanced Battery Current | `Ibat` | A | Yes |
| Advanced | Advanced Load Current | `Iload` | A | Yes |
| Advanced | Advanced PWM Current | `Ipwm` | A | Yes |
| Advanced | Advanced Battery Cycles | `nCicli` | - | Yes |
| Advanced | Advanced Battery Temperature | `Tbat` | CELSIUS | Yes |
| Advanced | Advanced Internal Temperature | `Tint` | CELSIUS | Yes |
| Advanced | Advanced Battery SOC | `SoC` | BATTERY | Yes |
| Advanced | Advanced AC Input Voltage | `VacIn` | V | Yes |
| Advanced | Advanced AC Input Current | `IacIn` | A | Yes |
| Advanced | Advanced AC Output Voltage | `VacOut` | V | Yes |
| Advanced | Advanced AC Output Current | `IacOut` | A | Yes |
| Advanced | Advanced AC Input Frequency | `FacIn` | Hz | Yes |
| Advanced | Advanced AC Output Frequency | `FacOut` | Hz | Yes |
| Advanced | Advanced Bucket Time | `Stime` | TIMESTAMP | No |

## Data Updates

The integration uses Home Assistant data coordinators. Each endpoint has its own
coordinator and polling interval:

- Realtime: defaults to 30 seconds
- Energy: defaults to 300 seconds
- Advanced: defaults to 120 seconds

If MyLeonardo rejects the API key, Home Assistant starts a reauthentication
flow. If the service is temporarily unavailable, affected entities are marked
unavailable until polling succeeds again.

## Notes

The MyLeonardo API documentation lists these rate limits:

- Realtime: max one request every 5 seconds
- Energy: max one request every 20 seconds
- Advanced: max one request every 20 seconds

The integration polls within those limits.

## Known Limitations

- The integration depends on the MyLeonardo cloud service.
- The integration does not connect directly to the inverter or battery over the
  local network; battery values are read from the MyLeonardo cloud API.
- Energy semantics depend on the MyLeonardo daily energy endpoint. The
  integration queries from local midnight to now for today's energy sensors.
- Discovery is not implemented; setup requires manually entering an API key and
  plant key.

## Roadmap

Potential future additions:

- Monthly energy sensors using the MyLeonardo energy endpoint with `type: M`.
- Selected advanced-complete diagnostic sensors using the advanced endpoint with
  `type: C`.
- Full Home Assistant config flow and diagnostics test coverage.
- Optional repair issues for repeated API failures or malformed responses.
- A wider landscape logo asset for Home Assistant views that prefer a full logo
  instead of a square icon.

## Troubleshooting

- If setup fails with an authentication error, verify the API key.
- If setup fails with a plant error, verify the plant key.
- If entities become unavailable, check MyLeonardo service availability and the
  Home Assistant logs.
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
- Watch battery charge, discharge, state of charge, voltage, and current.
- Use wallbox power/energy sensors in EV charging automations.

## Development

Parser tests use the sample API responses included in this repository.

```bash
python -m unittest discover -s tests
```

## Support

Open an issue on GitHub with diagnostics from Home Assistant when possible.
