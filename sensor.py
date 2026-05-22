from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.const import (
    EntityCategory,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    CONF_CONNECTION_TYPE,
    CONF_MODBUS_HOST,
    CONF_PLANT_KEY,
    CONNECTION_TYPE_CLOUD,
    CONNECTION_TYPE_HYBRID,
    CONNECTION_TYPE_MODBUS,
)
from .const import (
    CONF_ENABLE_ADVANCED_SENSORS,
    CONF_ENABLE_ENERGY_SENSORS,
    CONF_ENABLE_REALTIME_SENSORS,
    DEFAULT_ENABLE_ADVANCED_SENSORS,
    DEFAULT_ENABLE_ENERGY_SENSORS,
    DEFAULT_ENABLE_REALTIME_SENSORS,
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
    advanced_coordinator = data.advanced
    connection_type = entry.data.get(
        CONF_CONNECTION_TYPE,
        CONNECTION_TYPE_CLOUD,
    )
    device_identifier = entry.data.get(
        CONF_PLANT_KEY,
        entry.data.get(CONF_MODBUS_HOST),
    )
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
            if connection_type == CONNECTION_TYPE_HYBRID
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

    async_add_entities(entities)


class MyLeonardoBaseSensor(
    CoordinatorEntity,
    SensorEntity,
):
    _attr_has_entity_name = True

    def __init__(self, coordinator, plant_key):
        super().__init__(coordinator)
        self._plant_key = plant_key

    def _set_description_attrs(self, description):
        self.entity_description = description
        self._attr_name = description.name
        self._attr_translation_key = description.translation_key
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_entity_registry_enabled_default = (
            description.enabled_default
        )

    @property
    def device_info(self):
        # All sensors for a plant are grouped under one Home Assistant device.
        return {
            "identifiers": {
                (
                    DOMAIN,
                    self._plant_key,
                )
            },
            "manufacturer": "Western Co.",
            "name": f"MyLeonardo Solar {self._plant_key}",
            "model": "Leonardo",
        }
        
    @property
    def available(self):
        return self.coordinator.last_update_success


class MyLeonardoRealtimeSensor(
    MyLeonardoBaseSensor
):
    def __init__(self, coordinator, description, plant_key):
        super().__init__(coordinator, plant_key)
        self._set_description_attrs(description)
        self._attr_unique_id = (
            f"{plant_key}_{description.source}_{description.key}".lower()
        )

    @property
    def native_value(self):
        # Realtime endpoint uses a dict payload under "data".
        return get_sensor_value(
            self.coordinator.data,
            self.entity_description.source_key
            or self.entity_description.key,
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
        plant_key,
    ):
        super().__init__(coordinator, plant_key)
        self._set_description_attrs(description)
        self._attr_unique_id = (
            f"{plant_key}_{description.source}_{description.key}".lower()
        )

    @property
    def native_value(self):
        # Energy endpoint returns a list; the newest bucket is read by parser.py.
        return get_sensor_value(
            self.coordinator.data,
            self.entity_description.source_key
            or self.entity_description.key,
            self.entity_description.source,
            self.entity_description.scale,
            self.entity_description.value_type,
        )


class MyLeonardoAdvancedSensor(
    MyLeonardoBaseSensor
):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, description, plant_key):
        super().__init__(coordinator, plant_key)
        self._set_description_attrs(description)
        self._attr_entity_registry_enabled_default = False
        self._attr_unique_id = (
            f"{plant_key}_{description.source}_{description.key}".lower()
        )

    @property
    def native_value(self):
        # Advanced endpoint also returns a list; parser.py hides that shape.
        return get_sensor_value(
            self.coordinator.data,
            self.entity_description.source_key
            or self.entity_description.key,
            self.entity_description.source,
            self.entity_description.scale,
            self.entity_description.value_type,
        )
