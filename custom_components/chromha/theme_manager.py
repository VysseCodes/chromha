"""Writes the generated theme file and asks the frontend to reload it."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer

from .const import (
    ACCENT_CUSTOM,
    ACCENT_PRESETS,
    CONF_ACCENT,
    CONF_ACCENT_HEX,
    CONF_PROFILE_NAME,
    DEFAULTS,
    DOMAIN,
    REBUILD_DEBOUNCE,
    SUN_ENTITY,
    THEME_DIR,
    THEME_FILE,
)
from .palette import hex_to_rgb, rgb_to_hex
from .renderer import render_file

_LOGGER = logging.getLogger(__name__)


def resolve_accent(options: dict) -> str:
    """Work out the accent hex from the preset/custom selection."""
    choice = options.get(CONF_ACCENT, DEFAULTS[CONF_ACCENT])
    if choice == ACCENT_CUSTOM:
        raw = options.get(CONF_ACCENT_HEX) or DEFAULTS[CONF_ACCENT_HEX]
    else:
        raw = ACCENT_PRESETS.get(choice, DEFAULTS[CONF_ACCENT_HEX])
    try:
        return rgb_to_hex(hex_to_rgb(raw))
    except ValueError:
        _LOGGER.warning("Invalid accent colour %r, falling back to default", raw)
        return DEFAULTS[CONF_ACCENT_HEX]


class ThemeManager:
    """Owns the generated theme file.

    All config entries share one file. Any entry change triggers a debounced
    rebuild of the whole thing, so profiles can never drift out of sync.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._path = Path(hass.config.path(THEME_DIR)) / THEME_FILE
        self._last_written: str | None = None
        self._debouncer = Debouncer(
            hass,
            _LOGGER,
            cooldown=REBUILD_DEBOUNCE,
            immediate=False,
            function=self._rebuild,
        )

    async def async_request_rebuild(self) -> None:
        await self._debouncer.async_call()

    def is_night(self) -> bool:
        """True when the sun is below the horizon.

        Falls back to daytime if the sun integration is unavailable, so a
        missing sun.sun degrades to day artwork rather than erroring.
        """
        state = self.hass.states.get(SUN_ENTITY)
        return bool(state and state.state == "below_horizon")

    def collect_profiles(self) -> dict[str, dict]:
        """Build the render input from every loaded config entry."""
        night = self.is_night()
        profiles: dict[str, dict] = {}
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            options = {**DEFAULTS, **entry.data, **entry.options}
            options["resolved_accent"] = resolve_accent(options)
            options["is_night"] = night
            name = options.get(CONF_PROFILE_NAME) or entry.title
            profiles[f"ChromHA {name}"] = options
        return profiles

    async def _rebuild(self) -> None:
        profiles = self.collect_profiles()

        if not profiles:
            await self.hass.async_add_executor_job(self._remove)
            self._last_written = None
            await self._reload_frontend()
            return

        text = render_file(profiles)

        # Skip the write and the reload if nothing actually changed. Sliders
        # generate a lot of no-op updates.
        if text == self._last_written:
            return

        try:
            await self.hass.async_add_executor_job(self._write, text)
        except OSError as err:
            _LOGGER.error("Could not write %s: %s", self._path, err)
            return

        self._last_written = text
        _LOGGER.debug("Wrote %d theme profile(s) to %s", len(profiles), self._path)
        await self._reload_frontend()

    def _write(self, text: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(self._path)

    def _remove(self) -> None:
        try:
            self._path.unlink()
        except FileNotFoundError:
            pass

    async def _reload_frontend(self) -> None:
        try:
            await self.hass.services.async_call(
                "frontend", "reload_themes", blocking=True
            )
        except Exception:  # noqa: BLE001 - frontend may not be ready at startup
            _LOGGER.debug("Could not reload themes yet", exc_info=True)
