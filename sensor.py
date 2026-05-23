from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.const import (
    EntityCategory,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import CONNECTION_TYPE_MODBUS
from .const import (
    CONF_ENABLE_ADVANCED_SENSORS,
    CONF_ENABLE_ADVANCED_COMPLETE_SENSORS,
    CONF_ENABLE_ENERGY_SENSORS,
    CONF_ENABLE_MONTHLY_ENERGY_SENSORS,
    CONF_ENABLE_REALTIME_SENSORS,
    DEFAULT_ENABLE_ADVANCED_COMPLETE_SENSORS,
    DEFAULT_ENABLE_ADVANCED_SENSORS,
    DEFAULT_ENABLE_ENERGY_SENSORS,
    DEFAULT_ENABLE_MONTHLY_ENERGY_SENSORS,
    DEFAULT_ENABLE_REALTIME_SENSORS,
)
from .helpers import (
    get_connection_type,
    get_description_source_key,
    get_device_identifier,
    get_device_info,
    set_entity_description_metadata,
    set_entity_device_metadata,
    uses_modbus_realtime,
)
from .parser import get_sensor_value
from .sensor_descriptions import MyLeonardoSensorDescriptions

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    data = entry.runtime_data
    realtime_coordinator = data.realtime
    energy_coordinator = data.energy
    energy_monthly_coordinator = data.energy_monthly
    advanced_coordinator = data.advanced
    advanced_complete_coordinator = data.advanced_complete
    connection_type = get_connection_type(entry)
    device_identifier = get_device_identifier(entry)
    options = entry.options

    # Build entities from endpoint-specific description groups.
    entities = []

    if connection_type == CONNECTION_TYPE_MODBUS:
        if options.get(
            CONF_ENABLE_REALTIME_SENSORS,
            DEFAULT_ENABLE_REALTIME_SENSORS,
        ):
            entities.extend(
                MyLeonardoRealtimeSensor(
                    realtime_coordinator,
                    description,
                    device_identifier,
                )
                for description in MyLeonardoSensorDescriptions.MODBUS
            )

        async_add_entities(entities)
        return

    if options.get(
        CONF_ENABLE_REALTIME_SENSORS,
        DEFAULT_ENABLE_REALTIME_SENSORS,
    ):
        realtime_descriptions = (
            MyLeonardoSensorDescriptions.MODBUS
            if uses_modbus_realtime(entry)
            else MyLeonardoSensorDescriptions.REALTIME
        )
        entities.extend(
            MyLeonardoRealtimeSensor(
                realtime_coordinator,
                description,
                device_identifier,
            )
            for description in realtime_descriptions
        )

    if options.get(
        CONF_ENABLE_ENERGY_SENSORS,
        DEFAULT_ENABLE_ENERGY_SENSORS,
    ):
        entities.extend(
            MyLeonardoEnergySensor(
                energy_coordinator,
                description,
                device_identifier,
            )
            for description in MyLeonardoSensorDescriptions.ENERGY
        )

        if options.get(
            CONF_ENABLE_MONTHLY_ENERGY_SENSORS,
            DEFAULT_ENABLE_MONTHLY_ENERGY_SENSORS,
        ):
            entities.extend(
                MyLeonardoEnergySensor(
                    energy_monthly_coordinator,
                    description,
                    device_identifier,
                )
                for description in MyLeonardoSensorDescriptions.ENERGY_MONTHLY
            )

    if options.get(
        CONF_ENABLE_ADVANCED_SENSORS,
        DEFAULT_ENABLE_ADVANCED_SENSORS,
    ):
        entities.extend(
            MyLeonardoAdvancedSensor(
                advanced_coordinator,
                description,
                device_identifier,
            )
            for description in MyLeonardoSensorDescriptions.ADVANCED
        )

        if options.get(
            CONF_ENABLE_ADVANCED_COMPLETE_SENSORS,
            DEFAULT_ENABLE_ADVANCED_COMPLETE_SENSORS,
        ):
            entities.extend(
                MyLeonardoAdvancedSensor(
                    advanced_complete_coordinator,
                    description,
                    device_identifier,
                )
                for description in (
                    MyLeonardoSensorDescriptions.ADVANCED_COMPLETE
                )
            )

    async_add_entities(entities)


class MyLeonardoBaseSensor(
    CoordinatorEntity,
    SensorEntity,
):
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_identifier, description):
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


class MyLeonardoRealtimeSensor(MyLeonardoBaseSensor):
    def __init__(self, coordinator, description, device_identifier):
        super().__init__(coordinator, device_identifier, description)

    @property
    def native_value(self):
        # Realtime endpoint uses a dict payload under "data".
        return get_sensor_value(
            self.coordinator.data,
            get_description_source_key(self.entity_description),
            self.entity_description.source,
            self.entity_description.scale,
            self.entity_description.value_type,
        )


class MyLeonardoEnergySensor(
    MyLeonardoBaseSensor,
):
    def __init__(
        self,
        coordinator,
        description,
        device_identifier,
    ):
        super().__init__(coordinator, device_identifier, description)

    @property
    def native_value(self):
        # Energy endpoint returns a list; the newest bucket is read by parser.py.
        return get_sensor_value(
            self.coordinator.data,
            get_description_source_key(self.entity_description),
            self.entity_description.source,
            self.entity_description.scale,
            self.entity_description.value_type,
        )


class MyLeonardoAdvancedSensor(MyLeonardoBaseSensor):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, description, device_identifier):
        super().__init__(coordinator, device_identifier, description)
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self):
        # Advanced endpoint also returns a list; parser.py hides that shape.
        return get_sensor_value(
            self.coordinator.data,
            get_description_source_key(self.entity_description),
            self.entity_description.source,
            self.entity_description.scale,
            self.entity_description.value_type,
        )
