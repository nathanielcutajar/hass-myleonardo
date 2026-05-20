import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    MyLeonardoApi,
    MyLeonardoApiError,
    MyLeonardoAuthError,
    MyLeonardoConnectionError,
    MyLeonardoPlantError,
)
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_PLANT_KEY,
    CONF_ADVANCED_SCAN_INTERVAL,
    CONF_ENABLE_ADVANCED_SENSORS,
    CONF_ENABLE_ENERGY_SENSORS,
    CONF_ENABLE_REALTIME_SENSORS,
    CONF_ENERGY_SCAN_INTERVAL,
    CONF_REALTIME_SCAN_INTERVAL,
    DEFAULT_ADVANCED_SCAN_INTERVAL,
    DEFAULT_ENABLE_ADVANCED_SENSORS,
    DEFAULT_ENABLE_ENERGY_SENSORS,
    DEFAULT_ENABLE_REALTIME_SENSORS,
    DEFAULT_ENERGY_SCAN_INTERVAL,
    DEFAULT_REALTIME_SCAN_INTERVAL,
    MIN_ADVANCED_SCAN_INTERVAL,
    MIN_ENERGY_SCAN_INTERVAL,
    MIN_REALTIME_SCAN_INTERVAL,
)

API_KEY_SELECTOR = TextSelector(
    TextSelectorConfig(
        type=TextSelectorType.PASSWORD,
    )
)

OPTIONS_FIELDS = {
    CONF_ENABLE_REALTIME_SENSORS: "Enable realtime sensors",
    CONF_ENABLE_ENERGY_SENSORS: "Enable energy sensors",
    CONF_ENABLE_ADVANCED_SENSORS: "Enable advanced sensors",
    CONF_REALTIME_SCAN_INTERVAL: "Realtime scan interval in seconds",
    CONF_ENERGY_SCAN_INTERVAL: "Energy scan interval in seconds",
    CONF_ADVANCED_SCAN_INTERVAL: "Advanced scan interval in seconds",
}


class MyLeonardoConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    VERSION = 1
    _reauth_entry = None
    _reconfigure_entry = None

    @staticmethod
    def async_get_options_flow(config_entry):
        return MyLeonardoOptionsFlow()

    def _clean_user_input(self, user_input):
        return {
            CONF_API_KEY: user_input[CONF_API_KEY].strip(),
            CONF_PLANT_KEY: user_input[CONF_PLANT_KEY].strip(),
        }

    async def _async_validate_input(self, user_input):
        api = MyLeonardoApi(
            async_get_clientsession(self.hass),
            user_input[CONF_API_KEY],
            user_input[CONF_PLANT_KEY],
        )

        await api.async_get_realtime()

    async def _async_try_validate_input(self, user_input):
        try:
            await self._async_validate_input(user_input)
        except MyLeonardoAuthError:
            return "invalid_auth"
        except MyLeonardoPlantError:
            return "invalid_plant"
        except MyLeonardoConnectionError:
            return "cannot_connect"
        except MyLeonardoApiError:
            return "unknown"

        return None

    async def async_step_user(
        self,
        user_input=None,
    ):
        errors = {}

        if user_input is not None:
            user_input = self._clean_user_input(user_input)
            plant_key = user_input[CONF_PLANT_KEY]
            await self.async_set_unique_id(plant_key)
            self._abort_if_unique_id_configured()

            error = await self._async_try_validate_input(user_input)

            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title="MyLeonardo",
                    data=user_input,
                )

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): API_KEY_SELECTOR,
            vol.Required(CONF_PLANT_KEY): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data):
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input=None,
    ):
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            data = {
                **self._reauth_entry.data,
                CONF_API_KEY: api_key,
            }

            error = await self._async_try_validate_input(data)

            if error:
                errors["base"] = error
            else:
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry,
                    data=data,
                )
                await self.hass.config_entries.async_reload(
                    self._reauth_entry.entry_id
                )

                return self.async_abort(reason="reauth_successful")

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): API_KEY_SELECTOR,
        })

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reconfigure(self, entry_data):
        self._reconfigure_entry = (
            self.hass.config_entries.async_get_entry(
                self.context["entry_id"]
            )
        )

        return await self.async_step_reconfigure_confirm()

    async def async_step_reconfigure_confirm(
        self,
        user_input=None,
    ):
        errors = {}

        current_data = self._reconfigure_entry.data

        if user_input is not None:
            user_input = self._clean_user_input(user_input)
            plant_key = user_input[CONF_PLANT_KEY]

            for entry in self._async_current_entries():
                if (
                    entry.entry_id
                    != self._reconfigure_entry.entry_id
                    and entry.unique_id == plant_key
                ):
                    return self.async_abort(
                        reason="already_configured"
                    )

            error = await self._async_try_validate_input(user_input)

            if error:
                errors["base"] = error
            else:
                self.hass.config_entries.async_update_entry(
                    self._reconfigure_entry,
                    unique_id=plant_key,
                    data=user_input,
                )
                await self.hass.config_entries.async_reload(
                    self._reconfigure_entry.entry_id
                )

                return self.async_abort(
                    reason="reconfigure_successful"
                )

        schema = vol.Schema({
            vol.Required(
                CONF_API_KEY,
                default=current_data.get(CONF_API_KEY, ""),
            ): API_KEY_SELECTOR,
            vol.Required(
                CONF_PLANT_KEY,
                default=current_data.get(CONF_PLANT_KEY, ""),
            ): str,
        })

        return self.async_show_form(
            step_id="reconfigure_confirm",
            data_schema=schema,
            errors=errors,
        )


class MyLeonardoOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    key: user_input[label]
                    for key, label in OPTIONS_FIELDS.items()
                },
            )

        options = self.config_entry.options

        schema = vol.Schema({
            vol.Required(
                OPTIONS_FIELDS[CONF_ENABLE_REALTIME_SENSORS],
                default=options.get(
                    CONF_ENABLE_REALTIME_SENSORS,
                    DEFAULT_ENABLE_REALTIME_SENSORS,
                ),
            ): BooleanSelector(),
            vol.Required(
                OPTIONS_FIELDS[CONF_ENABLE_ENERGY_SENSORS],
                default=options.get(
                    CONF_ENABLE_ENERGY_SENSORS,
                    DEFAULT_ENABLE_ENERGY_SENSORS,
                ),
            ): BooleanSelector(),
            vol.Required(
                OPTIONS_FIELDS[CONF_ENABLE_ADVANCED_SENSORS],
                default=options.get(
                    CONF_ENABLE_ADVANCED_SENSORS,
                    DEFAULT_ENABLE_ADVANCED_SENSORS,
                ),
            ): BooleanSelector(),
            vol.Required(
                OPTIONS_FIELDS[CONF_REALTIME_SCAN_INTERVAL],
                default=options.get(
                    CONF_REALTIME_SCAN_INTERVAL,
                    DEFAULT_REALTIME_SCAN_INTERVAL,
                ),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_REALTIME_SCAN_INTERVAL,
                    mode=NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                OPTIONS_FIELDS[CONF_ENERGY_SCAN_INTERVAL],
                default=options.get(
                    CONF_ENERGY_SCAN_INTERVAL,
                    DEFAULT_ENERGY_SCAN_INTERVAL,
                ),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_ENERGY_SCAN_INTERVAL,
                    mode=NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                OPTIONS_FIELDS[CONF_ADVANCED_SCAN_INTERVAL],
                default=options.get(
                    CONF_ADVANCED_SCAN_INTERVAL,
                    DEFAULT_ADVANCED_SCAN_INTERVAL,
                ),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_ADVANCED_SCAN_INTERVAL,
                    mode=NumberSelectorMode.BOX,
                )
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
