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
    MyLeonardoMonthlyEnergyCoordinator,
    MyLeonardoAdvancedCoordinator,
    MyLeonardoAdvancedCompleteCoordinator,
    MyLeonardoModbusCoordinator,
)
from .const import (
    CONF_API_KEY,
    CONF_PLANT_KEY,
    CONF_MODBUS_HOST,
    CONF_MODBUS_PORT,
    CONF_ADVANCED_SCAN_INTERVAL,
    CONF_ENABLE_ADVANCED_COMPLETE_SENSORS,
    CONF_ENABLE_MONTHLY_ENERGY_SENSORS,
    CONF_ENERGY_SCAN_INTERVAL,
    CONF_REALTIME_SCAN_INTERVAL,
    CONNECTION_TYPE_HYBRID,
    CONNECTION_TYPE_MODBUS,
    DEFAULT_MODBUS_PORT,
    DEFAULT_MODBUS_SCAN_INTERVAL,
    DEFAULT_ADVANCED_SCAN_INTERVAL,
    DEFAULT_ENABLE_ADVANCED_COMPLETE_SENSORS,
    DEFAULT_ENABLE_MONTHLY_ENERGY_SENSORS,
    DEFAULT_ENERGY_SCAN_INTERVAL,
    DEFAULT_REALTIME_SCAN_INTERVAL,
)
from .helpers import get_connection_type
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
    connection_type = get_connection_type(entry)

    if connection_type == CONNECTION_TYPE_MODBUS:
        realtime_coordinator = _create_modbus_coordinator(hass, entry)
        await _first_refresh(realtime_coordinator)
        return await _finish_setup(
            hass,
            entry,
            MyLeonardoRuntimeData(realtime=realtime_coordinator),
        )

    if connection_type == CONNECTION_TYPE_HYBRID:
        realtime_coordinator = _create_modbus_coordinator(hass, entry)
        (
            energy_coordinator,
            energy_monthly_coordinator,
            advanced_coordinator,
            advanced_complete_coordinator,
        ) = _create_cloud_history_coordinators(hass, session, entry)
    else:
        realtime_coordinator = _create_cloud_realtime_coordinator(
            hass,
            session,
            entry,
        )
        (
            energy_coordinator,
            energy_monthly_coordinator,
            advanced_coordinator,
            advanced_complete_coordinator,
        ) = _create_cloud_history_coordinators(hass, session, entry)

    await _first_refresh(
        realtime_coordinator,
        energy_coordinator,
        advanced_coordinator,
    )
    return await _finish_setup(
        hass,
        entry,
        MyLeonardoRuntimeData(
            realtime=realtime_coordinator,
            energy=energy_coordinator,
            energy_monthly=energy_monthly_coordinator,
            advanced=advanced_coordinator,
            advanced_complete=advanced_complete_coordinator,
        ),
    )


def _create_cloud_api(session, entry):
    return MyLeonardoApi(
        session,
        entry.data[CONF_API_KEY],
        entry.data[CONF_PLANT_KEY],
    )


def _create_modbus_api(entry):
    return MyLeonardoModbusApi(
        entry.data[CONF_MODBUS_HOST],
        entry.data.get(CONF_MODBUS_PORT, DEFAULT_MODBUS_PORT),
    )


def _create_modbus_coordinator(hass, entry):
    return MyLeonardoModbusCoordinator(
        hass,
        _create_modbus_api(entry),
        entry.options.get(
            CONF_REALTIME_SCAN_INTERVAL,
            DEFAULT_MODBUS_SCAN_INTERVAL,
        ),
    )


def _create_cloud_realtime_coordinator(hass, session, entry):
    return MyLeonardoCoordinator(
        hass,
        _create_cloud_api(session, entry),
        entry.options.get(
            CONF_REALTIME_SCAN_INTERVAL,
            DEFAULT_REALTIME_SCAN_INTERVAL,
        ),
    )


def _create_cloud_history_coordinators(hass, session, entry):
    api = _create_cloud_api(session, entry)
    options = entry.options
    energy_monthly_coordinator = None
    advanced_complete_coordinator = None

    if options.get(
        CONF_ENABLE_MONTHLY_ENERGY_SENSORS,
        DEFAULT_ENABLE_MONTHLY_ENERGY_SENSORS,
    ):
        energy_monthly_coordinator = MyLeonardoMonthlyEnergyCoordinator(
            hass,
            api,
            options.get(
                CONF_ENERGY_SCAN_INTERVAL,
                DEFAULT_ENERGY_SCAN_INTERVAL,
            ),
        )

    if options.get(
        CONF_ENABLE_ADVANCED_COMPLETE_SENSORS,
        DEFAULT_ENABLE_ADVANCED_COMPLETE_SENSORS,
    ):
        advanced_complete_coordinator = MyLeonardoAdvancedCompleteCoordinator(
            hass,
            api,
            options.get(
                CONF_ADVANCED_SCAN_INTERVAL,
                DEFAULT_ADVANCED_SCAN_INTERVAL,
            ),
        )

    return (
        MyLeonardoEnergyCoordinator(
            hass,
            api,
            options.get(
                CONF_ENERGY_SCAN_INTERVAL,
                DEFAULT_ENERGY_SCAN_INTERVAL,
            ),
        ),
        energy_monthly_coordinator,
        MyLeonardoAdvancedCoordinator(
            hass,
            api,
            options.get(
                CONF_ADVANCED_SCAN_INTERVAL,
                DEFAULT_ADVANCED_SCAN_INTERVAL,
            ),
        ),
        advanced_complete_coordinator,
    )


async def _first_refresh(*coordinators):
    for coordinator in coordinators:
        if coordinator is None:
            continue

        await coordinator.async_config_entry_first_refresh()


async def _finish_setup(hass, entry, runtime_data):
    entry.runtime_data = runtime_data

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
