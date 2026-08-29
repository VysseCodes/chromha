"""Number entities: corner radius and glass opacity."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_OPACITY, CONF_RADIUS, CONF_STYLE, STYLE_GLASS
from .entity import ChromHAEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(
        [
            ChromHANumber(entry, CONF_RADIUS, "Corner radius", 0, 32, 1,
                         "mdi:rounded-corner", "px"),
            ChromHAGlassOpacity(entry, CONF_OPACITY, "Card opacity", 0, 100, 1,
                               "mdi:opacity", "%"),
        ]
    )


class ChromHANumber(ChromHAEntity, NumberEntity):
    """A numeric setting rendered as a slider."""

    _attr_mode = NumberMode.SLIDER

    def __init__(self, entry, key, name, minimum, maximum, step, icon, unit) -> None:
        super().__init__(entry, key, name)
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float | None:
        try:
            return float(self._value())
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self._async_store(int(value))


class ChromHAGlassOpacity(ChromHANumber):
    """Only meaningful when the Glass style is selected."""

    @property
    def available(self) -> bool:
        return self._entry.options.get(
            CONF_STYLE, self._entry.data.get(CONF_STYLE)
        ) == STYLE_GLASS
