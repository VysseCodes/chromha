"""Config flow for ChromHA."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .const import (
    ACCENT_CUSTOM,
    ACCENT_PRESETS,
    CONF_ACCENT,
    CONF_ACCENT_HEX,
    CONF_MODE,
    CONF_PROFILE_NAME,
    CONF_STYLE,
    DEFAULTS,
    DOMAIN,
    MODES,
    STYLES,
)
from .palette import hex_to_rgb


def _schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_PROFILE_NAME, default=defaults.get(CONF_PROFILE_NAME, "")):
                TextSelector(),
            vol.Required(CONF_ACCENT, default=defaults[CONF_ACCENT]): SelectSelector(
                SelectSelectorConfig(
                    options=[*ACCENT_PRESETS, ACCENT_CUSTOM],
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONF_ACCENT_HEX, default=defaults[CONF_ACCENT_HEX]):
                TextSelector(),
            vol.Required(CONF_STYLE, default=defaults[CONF_STYLE]): SelectSelector(
                SelectSelectorConfig(options=STYLES, mode=SelectSelectorMode.LIST)
            ),
            vol.Required(CONF_MODE, default=defaults[CONF_MODE]): SelectSelector(
                SelectSelectorConfig(options=MODES, mode=SelectSelectorMode.LIST)
            ),
        }
    )


class ChromHAConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create one theme profile per config entry.

    Multiple entries are expected - one per household member - so there is no
    single-instance guard.
    """

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_PROFILE_NAME].strip()

            if not name:
                errors[CONF_PROFILE_NAME] = "name_required"
            else:
                # Theme names are the key in the generated YAML, so they
                # have to be unique across entries.
                for entry in self._async_current_entries():
                    existing = entry.options.get(
                        CONF_PROFILE_NAME, entry.data.get(CONF_PROFILE_NAME)
                    )
                    if existing and existing.lower() == name.lower():
                        errors[CONF_PROFILE_NAME] = "name_exists"
                        break

            if user_input.get(CONF_ACCENT) == ACCENT_CUSTOM:
                try:
                    hex_to_rgb(user_input.get(CONF_ACCENT_HEX, ""))
                except ValueError:
                    errors[CONF_ACCENT_HEX] = "invalid_colour"

            if not errors:
                data = {**DEFAULTS, **user_input, CONF_PROFILE_NAME: name}
                return self.async_create_entry(title=name, data=data)

        defaults = {**DEFAULTS, **(user_input or {})}
        return self.async_show_form(
            step_id="user", data_schema=_schema(defaults), errors=errors
        )
