"""Base entity.

Every control stores its value in the config entry's options rather than in
entity state. That gives free persistence across restarts, and a single
update listener that triggers the theme rebuild.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import CONF_PROFILE_NAME, DEFAULTS, DOMAIN


class ChromHAEntity(Entity):
    """Common plumbing for ChromHA's control entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_entity_category = None

    def __init__(self, entry: ConfigEntry, key: str, name: str) -> None:
        self._entry = entry
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def _profile_name(self) -> str:
        return self._entry.options.get(
            CONF_PROFILE_NAME, self._entry.data.get(CONF_PROFILE_NAME, self._entry.title)
        )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"ChromHA {self._profile_name}",
            manufacturer="ChromHA",
            model="Theme profile",
            entry_type=None,
        )

    def _value(self, default: Any = None) -> Any:
        if self._key in self._entry.options:
            return self._entry.options[self._key]
        if self._key in self._entry.data:
            return self._entry.data[self._key]
        return DEFAULTS.get(self._key, default)

    async def _async_store(self, value: Any) -> None:
        """Persist a new value and let the update listener rebuild."""
        options = {**self._entry.options, self._key: value}
        self.hass.config_entries.async_update_entry(self._entry, options=options)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._entry.add_update_listener(self._async_entry_updated)
        )

    async def _async_entry_updated(
        self, hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        self.async_write_ha_state()
