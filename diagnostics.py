from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_API_KEY, CONF_PLANT_KEY

TO_REDACT = {
    CONF_API_KEY,
    CONF_PLANT_KEY,
    "Bkey",
    "Dkey",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    entry_data = async_redact_data(
        entry.as_dict(),
        TO_REDACT,
    )
    entry_data["title"] = "**REDACTED**"
    entry_data["unique_id"] = "**REDACTED**"

    return {
        "entry": entry_data,
        "coordinators": {
            "realtime": {
                "last_update_success": (
                    entry.runtime_data.realtime.last_update_success
                ),
                "update_interval": str(
                    entry.runtime_data.realtime.update_interval
                ),
            },
            "energy": {
                "last_update_success": (
                    entry.runtime_data.energy.last_update_success
                ),
                "update_interval": str(
                    entry.runtime_data.energy.update_interval
                ),
            },
            "advanced": {
                "last_update_success": (
                    entry.runtime_data.advanced.last_update_success
                ),
                "update_interval": str(
                    entry.runtime_data.advanced.update_interval
                ),
            },
        },
    }
