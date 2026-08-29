"""Switch entity for the higher-contrast text option."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CONTRAST
from .entity import ChromHAEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([ChromHAContrastSwitch(entry)])


class ChromHAContrastSwitch(ChromHAEntity, SwitchEntity):
    """Raises the text contrast target from WCAG AA to AAA."""

    _attr_icon = "mdi:contrast-circle"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, CONF_CONTRAST, "High contrast text")

    @property
    def is_on(self) -> bool:
        return bool(self._value())

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_store(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_store(False)
