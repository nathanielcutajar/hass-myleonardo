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

    coordinators = {}

    for name in (
        "realtime",
        "energy",
        "energy_monthly",
        "advanced",
        "advanced_complete",
    ):
        coordinator = getattr(entry.runtime_data, name)

        if coordinator is None:
            continue

        coordinators[name] = {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
        }

    return {
        "entry": entry_data,
        "coordinators": coordinators,
    }
