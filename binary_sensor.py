from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .binary_sensor_descriptions import MyLeonardoBinarySensorDescriptions
from .const import (
    CONF_CONNECTION_TYPE,
    CONF_ENABLE_REALTIME_SENSORS,
    CONF_MODBUS_HOST,
    CONF_PLANT_KEY,
    DEFAULT_ENABLE_REALTIME_SENSORS,
    DOMAIN,
    CONNECTION_TYPE_CLOUD,
    CONNECTION_TYPE_HYBRID,
    CONNECTION_TYPE_MODBUS,
)
from .parser import get_binary_sensor_value

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    options = entry.options

    if not options.get(
        CONF_ENABLE_REALTIME_SENSORS,
        DEFAULT_ENABLE_REALTIME_SENSORS,
    ):
        async_add_entities([])
        return

    connection_type = entry.data.get(
        CONF_CONNECTION_TYPE,
        CONNECTION_TYPE_CLOUD,
    )
    device_identifier = entry.data.get(
        CONF_PLANT_KEY,
        entry.data.get(CONF_MODBUS_HOST),
    )
    descriptions = (
        MyLeonardoBinarySensorDescriptions.MODBUS
        if connection_type in (CONNECTION_TYPE_MODBUS, CONNECTION_TYPE_HYBRID)
        else MyLeonardoBinarySensorDescriptions.REALTIME
    )

    async_add_entities(
        MyLeonardoBinarySensor(
            entry.runtime_data.realtime,
            description,
            device_identifier,
        )
        for description in descriptions
    )


class MyLeonardoBinarySensor(
    CoordinatorEntity,
    BinarySensorEntity,
):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        description,
        device_identifier,
    ):
        super().__init__(coordinator)
        self.entity_description = description
        self._device_identifier = device_identifier
        self._attr_name = description.name
        self._attr_translation_key = description.translation_key
        self._attr_entity_registry_enabled_default = (
            description.enabled_default
        )
        self._attr_unique_id = (
            f"{device_identifier}_{description.source}_{description.key}"
        ).lower()

    @property
    def device_info(self):
        # Keep status entities grouped with the same physical plant/device.
        return {
            "identifiers": {
                (
                    DOMAIN,
                    self._device_identifier,
                )
            },
            "manufacturer": "Western Co.",
            "name": f"MyLeonardo Solar {self._device_identifier}",
            "model": "Leonardo",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def is_on(self):
        return get_binary_sensor_value(
            self.coordinator.data,
            self.entity_description.source_key,
            self.entity_description.source,
            self.entity_description.value_type,
            self.entity_description.threshold,
        )
