from .const import (
    CONF_CONNECTION_TYPE,
    CONF_MODBUS_HOST,
    CONF_PLANT_KEY,
    DOMAIN,
    CONNECTION_TYPE_CLOUD,
    CONNECTION_TYPE_HYBRID,
    CONNECTION_TYPE_MODBUS,
)


def get_connection_type(entry):
    return entry.data.get(
        CONF_CONNECTION_TYPE,
        CONNECTION_TYPE_CLOUD,
    )


def uses_modbus_realtime(entry):
    return get_connection_type(entry) in (
        CONNECTION_TYPE_MODBUS,
        CONNECTION_TYPE_HYBRID,
    )


def get_device_identifier(entry):
    return entry.data.get(
        CONF_PLANT_KEY,
        entry.data.get(CONF_MODBUS_HOST),
    )


def get_device_info(device_identifier):
    return {
        "identifiers": {
            (
                DOMAIN,
                device_identifier,
            )
        },
        "manufacturer": "Western Co.",
        "name": f"MyLeonardo Solar {device_identifier}",
        "model": "Leonardo",
    }


def get_entity_unique_id(device_identifier, source, key):
    return f"{device_identifier}_{source}_{key}".lower()


def get_description_source_key(description):
    return description.source_key or description.key


def set_entity_device_metadata(
    entity,
    device_identifier,
    source,
    key,
):
    entity._device_identifier = device_identifier
    entity._attr_unique_id = get_entity_unique_id(
        device_identifier,
        source,
        key,
    )


def set_entity_description_metadata(entity, description):
    entity.entity_description = description
    entity._attr_name = description.name
    entity._attr_translation_key = description.translation_key
    entity._attr_entity_registry_enabled_default = (
        description.enabled_default
    )

    if hasattr(description, "unit"):
        entity._attr_native_unit_of_measurement = description.unit

    if hasattr(description, "device_class"):
        entity._attr_device_class = description.device_class

    if hasattr(description, "state_class"):
        entity._attr_state_class = description.state_class
