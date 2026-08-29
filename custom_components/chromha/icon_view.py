"""Sun-aware icon endpoint.

Theme files are static CSS: there is no way to write "if night, use this
icon". But the icons are fetched by URL, and this integration serves those
URLs, so the decision can move from write time to request time.

A theme that points at `/chromha_icons_auto/partlycloudy.svg` never has to be
rewritten. The browser asks for the same URL all day and this view answers
with day or night artwork depending on where the sun is.

The plain `/chromha_icons/` static route is still used for the fixed-artwork
options, where a long cache lifetime is free.
"""

from __future__ import annotations

import logging
from pathlib import Path

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import ICON_AUTO_URL_BASE, ICON_DIR, SUN_ENTITY, WEATHER_ICON_MAP, icon_map

_LOGGER = logging.getLogger(__name__)


class ChromHAIconView(HomeAssistantView):
    """Serve a weather icon chosen by the current sun state."""

    url = ICON_AUTO_URL_BASE + "/{condition}.svg"
    name = "chromha:icon_auto"

    # CSS url() requests carry no auth token, so this has to be open. It only
    # ever returns bundled SVGs from a fixed allowlist.
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._dir = Path(__file__).parent / ICON_DIR
        self._cache: dict[str, bytes] = {}

    def _is_night(self) -> bool:
        state = self._hass.states.get(SUN_ENTITY)
        return bool(state and state.state == "below_horizon")

    def _read(self, filename: str) -> bytes | None:
        if filename in self._cache:
            return self._cache[filename]
        path = self._dir / f"{filename}.svg"
        try:
            data = path.read_bytes()
        except OSError:
            _LOGGER.warning("Missing bundled icon: %s", path)
            return None
        self._cache[filename] = data
        return data

    async def get(self, request: web.Request, condition: str) -> web.Response:
        # Allowlist by condition name, so no part of the path comes from the
        # request unchecked.
        if condition not in WEATHER_ICON_MAP:
            return web.Response(status=404)

        night = self._is_night()
        filename = icon_map(night)[condition]

        data = await self._hass.async_add_executor_job(self._read, filename)
        if data is None:
            return web.Response(status=404)

        # The URL is stable but its content changes twice a day, so the
        # browser must revalidate. The ETag carries the resolved filename, so
        # revalidation is a cheap 304 for all but the two daily transitions.
        etag = f'"{filename}"'
        if request.headers.get("If-None-Match") == etag:
            return web.Response(status=304, headers={"ETag": etag})

        return web.Response(
            body=data,
            content_type="image/svg+xml",
            headers={"ETag": etag, "Cache-Control": "no-cache"},
        )
