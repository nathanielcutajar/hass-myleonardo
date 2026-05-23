# Sensors

The integration exposes sensors grouped by the API source they come from:

- Realtime sensors.
- Energy sensors.
- Monthly energy sensors.
- Advanced sensors.
- Advanced-complete diagnostic sensors.
- Local Modbus sensors.
- Binary status sensors.

Energy values are converted to kWh where the API returns Wh-style values.
Advanced sensors are diagnostic and disabled by default in the entity registry.

## Sensor Reference

`Energy daily` and `Energy monthly` use the same energy endpoint with different
`type` parameters. `Advanced basic` and `Advanced complete` use the same
advanced endpoint with different `type` parameters.

| API source | Sensor | API field | Unit | Enabled by default |
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
| Energy daily (`type: D`) | Solar Energy Today | `EacPV` | KILO_WATT_HOUR | Yes |
| Energy daily (`type: D`) | Home Consumption Today | `EacHome` | KILO_WATT_HOUR | Yes |
| Energy daily (`type: D`) | Grid Import Today | `EacGridIn` | KILO_WATT_HOUR | Yes |
| Energy daily (`type: D`) | Grid Export Today | `EacGridOut` | KILO_WATT_HOUR | Yes |
| Energy daily (`type: D`) | Battery Charged Today | `Einbat` | KILO_WATT_HOUR | Yes |
| Energy daily (`type: D`) | Battery Discharged Today | `Eoutbat` | KILO_WATT_HOUR | Yes |
| Energy daily (`type: D`) | PWM Today | `Epwm` | KILO_WATT_HOUR | No |
| Energy daily (`type: D`) | Load Today | `Eload` | KILO_WATT_HOUR | Yes |
| Energy daily (`type: D`) | Bucket Date | `Stime` | DATE | No |
| Energy monthly (`type: M`) | Solar Energy This Month | `EacPV` | KILO_WATT_HOUR | Yes |
| Energy monthly (`type: M`) | Home Consumption This Month | `EacHome` | KILO_WATT_HOUR | Yes |
| Energy monthly (`type: M`) | Grid Import This Month | `EacGridIn` | KILO_WATT_HOUR | Yes |
| Energy monthly (`type: M`) | Grid Export This Month | `EacGridOut` | KILO_WATT_HOUR | Yes |
| Energy monthly (`type: M`) | Battery Charged This Month | `Einbat` | KILO_WATT_HOUR | Yes |
| Energy monthly (`type: M`) | Battery Discharged This Month | `Eoutbat` | KILO_WATT_HOUR | Yes |
| Energy monthly (`type: M`) | PWM This Month | `Epwm` | KILO_WATT_HOUR | No |
| Energy monthly (`type: M`) | Load This Month | `Eload` | KILO_WATT_HOUR | Yes |
| Energy monthly (`type: M`) | Month Bucket Date | `Stime` | DATE | No |
| Advanced basic (`type: B`) | Average Production | `avgPacPV` | WATT | No |
| Advanced basic (`type: B`) | Average Home Consumption | `avgPacHome` | WATT | No |
| Advanced basic (`type: B`) | Average Grid Power | `avgPacGrid` | WATT | No |
| Advanced basic (`type: B`) | Average Battery Power | `avgPbat` | WATT | No |
| Advanced basic (`type: B`) | Average Load Power | `avgPload` | WATT | No |
| Advanced basic (`type: B`) | Average PWM Power | `avgPpwm` | WATT | No |
| Advanced basic (`type: B`) | Battery Voltage | `Vbat` | V | No |
| Advanced basic (`type: B`) | Battery Current | `Ibat` | A | No |
| Advanced basic (`type: B`) | Load Current | `Iload` | A | No |
| Advanced basic (`type: B`) | PWM Current | `Ipwm` | A | No |
| Advanced basic (`type: B`) | Battery Cycles | `nCicli` | - | No |
| Advanced basic (`type: B`) | Battery Temperature | `Tbat` | CELSIUS | No |
| Advanced basic (`type: B`) | Internal Temperature | `Tint` | CELSIUS | No |
| Advanced basic (`type: B`) | Battery SOC | `SoC` | BATTERY | No |
| Advanced basic (`type: B`) | AC Input Voltage | `VacIn` | V | No |
| Advanced basic (`type: B`) | AC Input Current | `IacIn` | A | No |
| Advanced basic (`type: B`) | AC Output Voltage | `VacOut` | V | No |
| Advanced basic (`type: B`) | AC Output Current | `IacOut` | A | No |
| Advanced basic (`type: B`) | AC Input Frequency | `FacIn` | Hz | No |
| Advanced basic (`type: B`) | AC Output Frequency | `FacOut` | Hz | No |
| Advanced basic (`type: B`) | Bucket Time | `Stime` | TIMESTAMP | No |
| Advanced complete (`type: C`) | Battery SOH | `SoH` | BATTERY | No |
| Advanced complete (`type: C`) | Battery End-of-Charge Voltage | `VEoC` | V | No |
| Advanced complete (`type: C`) | Inverter Power | `PacInv` | WATT | No |
| Advanced complete (`type: C`) | Inverter Battery Voltage | `VbatInv` | V | No |
| Advanced complete (`type: C`) | Inverter Battery Current | `IbatInv` | A | No |
| Advanced complete (`type: C`) | WRM Flag | `FlagWRM` | - | No |
| Advanced complete (`type: C`) | WBM Flag | `FlagWBM` | - | No |
| Advanced complete (`type: C`) | WRD Flag | `FlagWRD` | - | No |
| Advanced complete (`type: C`) | LK3 Flag | `FlagLK3` | - | No |
| Advanced complete (`type: C`) | WRD System Charge | `SystemChargeWRD` | BATTERY | No |
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

The integration creates binary sensors from realtime power values.

| Status | Cloud API field | Local Modbus field |
| --- | --- | --- |
| Producing | `PacPV > 0` | `pv_power > 0` |
| Grid importing | `PacGrid > 0` | `grid_power > 0` |
| Grid exporting | `PacGrid < 0` | `grid_power < 0` |
| Battery charging | `Pbat > 0` | `battery_power > 0` |
| Battery discharging | `Pbat < 0` | `battery_power < 0` |

Hybrid mode uses the local Modbus fields for these binary status sensors.
