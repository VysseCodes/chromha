"""The ChromHA theme integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import Event, EventStateChangedData, HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, ICON_DIR, ICON_URL_BASE, SUN_ENTITY
from .icon_view import ChromHAIconView
from .theme_manager import ThemeManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
]

_ICONS_KEY = f"{DOMAIN}_icons_registered"
_SUN_KEY = f"{DOMAIN}_sun_listener"


async def _async_register_icons(hass: HomeAssistant) -> None:
    """Serve the bundled weather SVGs.

    They ship inside the integration, so a HACS update keeps them in step with
    the mapping in const.py. Nothing to download, nothing to put in /www.
    """
    if hass.data.get(_ICONS_KEY):
        return

    icon_path = Path(__file__).parent / ICON_DIR
    if not icon_path.is_dir():
        _LOGGER.warning("Bundled icons missing at %s", icon_path)
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(ICON_URL_BASE, str(icon_path), cache_headers=True)]
    )
    # Sun-aware endpoint. Registered on a separate prefix so the static route
    # above cannot shadow it.
    hass.http.register_view(ChromHAIconView(hass))

    hass.data[_ICONS_KEY] = True
    _LOGGER.debug("Serving weather icons from %s at %s", icon_path, ICON_URL_BASE)


def _async_track_sun(hass: HomeAssistant, manager: ThemeManager) -> None:
    """Rebuild when the sun crosses the horizon.

    Only Sun mode needs this, and only for its palette: sun-aware weather
    icons are resolved per request by icon_view.py, so they never require a
    rewrite.

    Registered unconditionally anyway. The rebuild is debounced and skipped
    entirely when the rendered output is unchanged, so profiles that ignore
    the sun cost one string comparison twice a day.
    """
    if hass.data.get(_SUN_KEY):
        return

    async def _sun_changed(event: Event[EventStateChangedData]) -> None:
        old, new = event.data.get("old_state"), event.data.get("new_state")
        if old is None or new is None or old.state == new.state:
            return
        await manager.async_request_rebuild()

    hass.data[_SUN_KEY] = async_track_state_change_event(
        hass, [SUN_ENTITY], _sun_changed
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a ChromHA profile."""
    await _async_register_icons(hass)

    manager: ThemeManager | None = hass.data.get(DOMAIN, {}).get("manager")
    if manager is None:
        manager = ThemeManager(hass)
        hass.data.setdefault(DOMAIN, {})["manager"] = manager

    _async_track_sun(hass, manager)
    hass.data[DOMAIN].setdefault("entries", set()).add(entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    await manager.async_request_rebuild()
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Any entity change lands here as an options update."""
    manager: ThemeManager = hass.data[DOMAIN]["manager"]
    await manager.async_request_rebuild()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a profile and drop it from the theme file."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unloaded:
        return False

    hass.data[DOMAIN]["entries"].discard(entry.entry_id)
    manager: ThemeManager = hass.data[DOMAIN]["manager"]
    await manager.async_request_rebuild()
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Rebuild once more after removal so the profile disappears."""
    manager: ThemeManager | None = hass.data.get(DOMAIN, {}).get("manager")
    if manager:
        await manager.async_request_rebuild()
