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
)
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_PLANT_KEY,
    CONF_ADVANCED_SCAN_INTERVAL,
    CONF_ENERGY_SCAN_INTERVAL,
    CONF_REALTIME_SCAN_INTERVAL,
    DEFAULT_ADVANCED_SCAN_INTERVAL,
    DEFAULT_ENERGY_SCAN_INTERVAL,
    DEFAULT_REALTIME_SCAN_INTERVAL,
)
from .runtime_data import MyLeonardoRuntimeData

PLATFORMS = [Platform.SENSOR]

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
