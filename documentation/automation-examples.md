# Automation Examples

These examples use the entity names Home Assistant commonly generates from the
integration names. Adjust entity IDs to match your installation.

## Notify When Exporting To Grid

```yaml
alias: MyLeonardo notify when exporting to grid
trigger:
  - platform: state
    entity_id: binary_sensor.myleonardo_solar_panels_grid_exporting
    to: "on"
    for:
      minutes: 5
action:
  - service: notify.mobile_app_phone
    data:
      title: Solar export active
      message: The system has been exporting to the grid for 5 minutes.
mode: single
```

## Start A Load During Excess Solar

```yaml
alias: MyLeonardo run load during grid export
trigger:
  - platform: numeric_state
    entity_id: sensor.myleonardo_solar_panels_grid_export_power
    above: 1500
    for:
      minutes: 3
condition:
  - condition: state
    entity_id: binary_sensor.myleonardo_solar_panels_producing
    state: "on"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.example_load
mode: single
```

## Warn When Battery Is Low

```yaml
alias: MyLeonardo low battery warning
trigger:
  - platform: numeric_state
    entity_id: sensor.myleonardo_solar_panels_battery_soc
    below: 20
    for:
      minutes: 10
action:
  - service: notify.mobile_app_phone
    data:
      title: Battery low
      message: Battery state of charge has been below 20% for 10 minutes.
mode: single
```

## Refresh Before A Critical Check

Use this only where a fresh reading matters. The integration rate-limits manual
refreshes based on each coordinator polling interval.

```yaml
alias: MyLeonardo refresh before evening check
trigger:
  - platform: time
    at: "18:00:00"
action:
  - service: button.press
    target:
      entity_id: button.myleonardo_solar_panels_refresh
  - delay:
      seconds: 5
  - condition: numeric_state
    entity_id: sensor.myleonardo_solar_panels_battery_soc
    below: 35
  - service: notify.mobile_app_phone
    data:
      title: Battery check
      message: Battery state of charge is below 35% this evening.
mode: single
```
