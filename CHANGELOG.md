# Changelog

All notable changes to ChromHA are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-08-29

### Fixed

- **Weather icons tiled instead of scaling.** The upstream SVGs ship with a
  fixed `width`/`height` and no `viewBox`, which gives them an intrinsic size
  as a CSS background - so Home Assistant repeated them across any element
  larger than 56x48. All bundled icons are now normalised by
  `scripts/normalize_icons.py`: fixed dimensions removed, `viewBox` and
  `preserveAspectRatio` added, nothing else touched. The script is idempotent
  and should be re-run after pulling new icons from upstream.

### Changed

- **Precipitation intensity now follows the condition** rather than being a
  user-selectable option, and `select.*_icon_intensity` has been removed. The
  `-1`/`-2`/`-3` suffixes encode rainfall intensity, so choosing one as a
  style preference showed a drizzle icon during a downpour. Home Assistant
  already makes the distinction it can: `rainy` uses `rainy-2`, `pouring` uses
  `rainy-3`.

  Live intensity cannot be driven from the theme. A theme supplies one URL per
  condition and the weather card reuses it for forecast rows, so an icon
  tracking current rainfall would put today's rate on next week's forecast.
  For live intensity, read `icon_library` from the palette sensor in a card
  template - that is per-element and does not affect forecasts.

### Upgrading from 0.1.0

`select.<profile>_icon_intensity` no longer exists. Home Assistant keeps
showing removed entities as unavailable rather than deleting them, so after
updating, remove it from any dashboard that references it and delete it from
Settings > Devices & Services > Entities. Nothing else carries over.

- The sun-aware endpoint drops its tier path segment: it is now
  `/chromha_icons_auto/<condition>.svg`.

### Added

- `examples/view-assist/` - a View Assist clock view wired to ChromHA, plus a
  guide to making the remaining View Assist views follow the theme. Both use
  plain CSS variables and need no entity ids.
- `CHANGELOG.md` and `RELEASE.md`.

## [0.1.0] - 2026-08-29

First public release.

### Added

- **Entity-driven themes.** One config entry per profile, each generating its
  own Home Assistant theme. Add one per household member; themes are global
  but selection is per-user, so everyone tunes their own independently.
- **OKLab palette derivation.** The entire palette is computed from a single
  accent colour. Neutrals are tinted toward the accent so the interface reads
  as one scheme rather than an accent floating on grey.
- **Contrast enforcement.** Text is checked against the card background and
  adjusted until it clears 4.5:1, or 7:1 with the high-contrast switch.
- **Four modes.** Light and Dark pin the theme; Auto emits both variants and
  lets the client choose; Sun follows sunrise and sunset, which is what makes
  a wall tablet with no OS-level dark mode actually change.
- **Glass style.** Backdrops are gradients generated from the accent colour,
  so there are no image files and the backdrop follows the selected colour.
- **Animated weather icons**, bundled and served from the integration.
- **Sun-aware icon endpoint**, resolving day or night artwork when the request
  arrives, so following the sun needs no theme rewrite and no frontend reload.
- **Palette sensor.** Publishes every resolved colour as an attribute, plus
  `icon_library` listing every bundled icon URL - for work that happens in
  JavaScript, where CSS variables cannot reach.

### Known gaps

- HA 2026.5 moved switches and checkboxes to a new component library and
  dropped several `switch-*` variables. Current names are set but not fully
  verified.
- Nothing from the 2025.8 semantic colour scale (`--md-sys-color-*`) is set,
  so some newer components fall back to Home Assistant defaults.
- `exceptional` maps to `severe-thunderstorm`, which is approximate.

[0.2.0]: https://github.com/vyssecodes/chromha/releases/tag/v0.2.0
[0.1.0]: https://github.com/vyssecodes/chromha/releases/tag/v0.1.0
