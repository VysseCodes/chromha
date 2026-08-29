"""Text entity for a custom accent hex value."""

from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ACCENT_CUSTOM, CONF_ACCENT, CONF_ACCENT_HEX
from .entity import ChromHAEntity
from .palette import hex_to_rgb


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([ChromHAAccentHex(entry)])


class ChromHAAccentHex(ChromHAEntity, TextEntity):
    """Free-form hex entry, used when Accent is set to Custom."""

    _attr_mode = TextMode.TEXT
    _attr_native_min = 4
    _attr_native_max = 7
    _attr_pattern = r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"
    _attr_icon = "mdi:eyedropper-variant"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, CONF_ACCENT_HEX, "Custom accent")

    @property
    def available(self) -> bool:
        return self._entry.options.get(
            CONF_ACCENT, self._entry.data.get(CONF_ACCENT)
        ) == ACCENT_CUSTOM

    @property
    def native_value(self) -> str | None:
        return self._value()

    async def async_set_value(self, value: str) -> None:
        # Reject anything unparseable rather than writing a broken theme.
        hex_to_rgb(value)
        await self._async_store(value if value.startswith("#") else f"#{value}")
