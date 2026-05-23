# Energy Dashboard

Use energy sensors, not realtime power sensors, when configuring Home
Assistant's Energy dashboard. Power sensors use W and show what is happening
right now; energy sensors use kWh and are suitable for long-term statistics.

## Cloud API

Cloud API mode exposes daily energy sensors from the MyLeonardo energy
endpoint. These sensors reset with the daily API bucket and are marked as
`total_increasing` so Home Assistant can handle the reset.

Monthly energy sensors are also exposed for dashboards and reporting, but the
daily sensors remain the recommended entities for Home Assistant's Energy
dashboard.

| Energy dashboard section | Recommended entity |
| --- | --- |
| Solar production | Solar Energy Today |
| Grid consumption | Grid Import Today |
| Return to grid | Grid Export Today |
| Battery charged from solar/grid | Battery Charged Today |
| Battery discharged to home/grid | Battery Discharged Today |

## Local Modbus TCP

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

Some local Modbus TCP devices return unsupported or `NaN` values for local grid
energy totals. When that happens, use Hybrid mode or Cloud API mode for grid
energy values.

## Hybrid

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
