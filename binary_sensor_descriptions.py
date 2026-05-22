from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntityDescription,
)


@dataclass
class MyLeonardoBinarySensorDescription(
    BinarySensorEntityDescription
):
    """Describes how one signed power field becomes an on/off status."""

    source: str = ""
    source_key: str = ""
    value_type: str = "above"
    threshold: float = 0
    enabled_default: bool = True


class MyLeonardoBinarySensorDescriptions:
    """Binary status definitions grouped by realtime data source."""

    REALTIME = [
        MyLeonardoBinarySensorDescription(
            key="producing",
            name="Producing",
            translation_key="realtime_producing",
            source="realtime",
            source_key="PacPV",
            value_type="above",
        ),
        MyLeonardoBinarySensorDescription(
            key="grid_importing",
            name="Grid Importing",
            translation_key="realtime_grid_importing",
            source="realtime",
            source_key="PacGrid",
            value_type="above",
        ),
        MyLeonardoBinarySensorDescription(
            key="grid_exporting",
            name="Grid Exporting",
            translation_key="realtime_grid_exporting",
            source="realtime",
            source_key="PacGrid",
            value_type="below",
        ),
        MyLeonardoBinarySensorDescription(
            key="battery_charging",
            name="Battery Charging",
            translation_key="realtime_battery_charging",
            source="realtime",
            source_key="Pbat",
            value_type="above",
        ),
        MyLeonardoBinarySensorDescription(
            key="battery_discharging",
            name="Battery Discharging",
            translation_key="realtime_battery_discharging",
            source="realtime",
            source_key="Pbat",
            value_type="below",
        ),
    ]

    MODBUS = [
        MyLeonardoBinarySensorDescription(
            key="producing",
            name="Producing",
            translation_key="modbus_producing",
            source="modbus",
            source_key="pv_power",
            value_type="above",
        ),
        MyLeonardoBinarySensorDescription(
            key="grid_importing",
            name="Grid Importing",
            translation_key="modbus_grid_importing",
            source="modbus",
            source_key="grid_power",
            value_type="above",
        ),
        MyLeonardoBinarySensorDescription(
            key="grid_exporting",
            name="Grid Exporting",
            translation_key="modbus_grid_exporting",
            source="modbus",
            source_key="grid_power",
            value_type="below",
        ),
        MyLeonardoBinarySensorDescription(
            key="battery_charging",
            name="Battery Charging",
            translation_key="modbus_battery_charging",
            source="modbus",
            source_key="battery_power",
            value_type="above",
        ),
        MyLeonardoBinarySensorDescription(
            key="battery_discharging",
            name="Battery Discharging",
            translation_key="modbus_battery_discharging",
            source="modbus",
            source_key="battery_power",
            value_type="below",
        ),
    ]
