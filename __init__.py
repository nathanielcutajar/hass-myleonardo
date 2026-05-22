from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import (
    async_get_clientsession,
)
from .api import MyLeonardoApi
from .coordinator import (
    MyLeonardoCoordinator,
    MyLeonardoEnergyCoordinator,
    MyLeonardoAdvancedCoordinator,
    MyLeonardoModbusCoordinator,
)
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_PLANT_KEY,
    CONF_CONNECTION_TYPE,
    CONF_MODBUS_HOST,
    CONF_MODBUS_PORT,
    CONF_ADVANCED_SCAN_INTERVAL,
    CONF_ENERGY_SCAN_INTERVAL,
    CONF_REALTIME_SCAN_INTERVAL,
    CONNECTION_TYPE_CLOUD,
    CONNECTION_TYPE_HYBRID,
    CONNECTION_TYPE_MODBUS,
    DEFAULT_MODBUS_PORT,
    DEFAULT_MODBUS_SCAN_INTERVAL,
    DEFAULT_ADVANCED_SCAN_INTERVAL,
    DEFAULT_ENERGY_SCAN_INTERVAL,
    DEFAULT_REALTIME_SCAN_INTERVAL,
)
from .modbus_api import MyLeonardoModbusApi
from .runtime_data import MyLeonardoRuntimeData

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SENSOR,
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    if entry.title != "MyLeonardo":
        hass.config_entries.async_update_entry(
            entry,
            title="MyLeonardo",
        )

    session = async_get_clientsession(hass)
    connection_type = entry.data.get(
        CONF_CONNECTION_TYPE,
        CONNECTION_TYPE_CLOUD,
    )

    if connection_type == CONNECTION_TYPE_MODBUS:
        api = MyLeonardoModbusApi(
            entry.data[CONF_MODBUS_HOST],
            entry.data.get(CONF_MODBUS_PORT, DEFAULT_MODBUS_PORT),
        )

        realtime_coordinator = MyLeonardoModbusCoordinator(
            hass,
            api,
            entry.options.get(
                CONF_REALTIME_SCAN_INTERVAL,
                DEFAULT_MODBUS_SCAN_INTERVAL,
            ),
        )

        await realtime_coordinator.async_config_entry_first_refresh()

        entry.runtime_data = MyLeonardoRuntimeData(
            realtime=realtime_coordinator,
        )

        entry.async_on_unload(
            entry.add_update_listener(async_reload_entry)
        )

        await hass.config_entries.async_forward_entry_setups(
            entry,
            PLATFORMS,
        )

        return True

    if connection_type == CONNECTION_TYPE_HYBRID:
        cloud_api = MyLeonardoApi(
            session,
            entry.data[CONF_API_KEY],
            entry.data[CONF_PLANT_KEY],
        )
        modbus_api = MyLeonardoModbusApi(
            entry.data[CONF_MODBUS_HOST],
            entry.data.get(CONF_MODBUS_PORT, DEFAULT_MODBUS_PORT),
        )

        realtime_coordinator = MyLeonardoModbusCoordinator(
            hass,
            modbus_api,
            entry.options.get(
                CONF_REALTIME_SCAN_INTERVAL,
                DEFAULT_MODBUS_SCAN_INTERVAL,
            ),
        )

        energy_coordinator = MyLeonardoEnergyCoordinator(
            hass,
            cloud_api,
            entry.options.get(
                CONF_ENERGY_SCAN_INTERVAL,
                DEFAULT_ENERGY_SCAN_INTERVAL,
            ),
        )

        advanced_coordinator = MyLeonardoAdvancedCoordinator(
            hass,
            cloud_api,
            entry.options.get(
                CONF_ADVANCED_SCAN_INTERVAL,
                DEFAULT_ADVANCED_SCAN_INTERVAL,
            ),
        )

        await realtime_coordinator.async_config_entry_first_refresh()
        await energy_coordinator.async_config_entry_first_refresh()
        await advanced_coordinator.async_config_entry_first_refresh()

        entry.runtime_data = MyLeonardoRuntimeData(
            realtime=realtime_coordinator,
            energy=energy_coordinator,
            advanced=advanced_coordinator,
        )

        entry.async_on_unload(
            entry.add_update_listener(async_reload_entry)
        )

        await hass.config_entries.async_forward_entry_setups(
            entry,
            PLATFORMS,
        )

        return True

    api = MyLeonardoApi(
        session,
        entry.data[CONF_API_KEY],
        entry.data[CONF_PLANT_KEY],
    )

    realtime_coordinator = (
        MyLeonardoCoordinator(
            hass,
            api,
            entry.options.get(
                CONF_REALTIME_SCAN_INTERVAL,
                DEFAULT_REALTIME_SCAN_INTERVAL,
            ),
        )
    )

    energy_coordinator = (
        MyLeonardoEnergyCoordinator(
            hass,
            api,
            entry.options.get(
                CONF_ENERGY_SCAN_INTERVAL,
                DEFAULT_ENERGY_SCAN_INTERVAL,
            ),
        )
    )

    advanced_coordinator = (
        MyLeonardoAdvancedCoordinator(
            hass,
            api,
            entry.options.get(
                CONF_ADVANCED_SCAN_INTERVAL,
                DEFAULT_ADVANCED_SCAN_INTERVAL,
            ),
        )
    )

    await realtime_coordinator.async_config_entry_first_refresh()
    await energy_coordinator.async_config_entry_first_refresh()
    await advanced_coordinator.async_config_entry_first_refresh()

    entry.runtime_data = MyLeonardoRuntimeData(
        realtime=realtime_coordinator,
        energy=energy_coordinator,
        advanced=advanced_coordinator,
    )

    entry.async_on_unload(
        entry.add_update_listener(async_reload_entry)
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        entry.runtime_data = None

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
