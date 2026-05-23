from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .binary_sensor_descriptions import MyLeonardoBinarySensorDescriptions
from .const import (
    CONF_ENABLE_REALTIME_SENSORS,
    DEFAULT_ENABLE_REALTIME_SENSORS,
)
from .helpers import (
    get_device_identifier,
    get_device_info,
    get_description_source_key,
    set_entity_description_metadata,
    set_entity_device_metadata,
    uses_modbus_realtime,
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

    device_identifier = get_device_identifier(entry)
    descriptions = (
        MyLeonardoBinarySensorDescriptions.MODBUS
        if uses_modbus_realtime(entry)
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
        set_entity_description_metadata(self, description)
        set_entity_device_metadata(
            self,
            device_identifier,
            description.source,
            description.key,
        )

    @property
    def device_info(self):
        return get_device_info(self._device_identifier)

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def is_on(self):
        return get_binary_sensor_value(
            self.coordinator.data,
            get_description_source_key(self.entity_description),
            self.entity_description.source,
            self.entity_description.value_type,
            self.entity_description.threshold,
        )
