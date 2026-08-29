<img src="assets/logo.png" alt="ChromHA" width="120" align="right">

# ChromHA

[![hacs][hacs-badge]][hacs-url]
[![release][release-badge]][release-url]
[![license][license-badge]](LICENSE)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=vyssecodes&repository=chromha&category=integration)

Home Assistant themes you configure with entities instead of YAML.

Pick one accent colour. ChromHA derives the whole palette from it in OKLab,
writes a theme file, and reloads the frontend. Every setting is an entity, so
you can change your theme from a dashboard, an automation, or a voice command.

Each household member gets their own profile. Themes are global in Home
Assistant but *selection* is per-user, so everyone picks their own ChromHA
theme once in their profile and tunes it independently after that.

## What you get per profile

| Entity | What it does |
|---|---|
| `select.*_accent` | 10 presets, or Custom |
| `text.*_custom_accent` | Hex value, when Accent is Custom |
| `select.*_style` | Solid or Glass |
| `select.*_mode` | Light, Dark, Auto (follows the client), or Sun |
| `number.*_corner_radius` | 0–32px |
| `number.*_card_opacity` | Glass only |
| `select.*_weather_icons` | Animated or None |
| `select.*_icon_daynight` | Day only, Follow theme, or Follow sun |
| `select.*_icon_intensity` | Light, Standard, or Heavy rain/snow artwork |
| `switch.*_high_contrast_text` | WCAG AA → AAA target |
| `sensor.*_palette` | Every resolved colour, as attributes |

## The palette sensor

This is the part worth knowing about. Themes are CSS, and CSS variables can be
awkward to reach from inside custom cards. The sensor publishes the same
colours as plain data:

```yaml
state: "#aa3151"
attributes:
  accent: "#aa3151"
  accent_soft: "#ca6176"
  background: "#151014"
  surface: "#231e23"
  text: "#e7e2e5"
  text_muted: "#807a7e"
  icon: "#807a7e"
  icon_active: "#bc415f"
  weather_icons:
    sunny: /chromha_icons/clear-day.svg
    ...
```

So a `custom:button-card` template can do this:

```yaml
styles:
  card:
    - background-color: |-
        [[[ return hass.states['sensor.chromha_ryan_palette'].attributes.background ]]]
  custom_fields:
    time:
      - color: |-
          [[[ return hass.states['sensor.chromha_ryan_palette'].attributes.text ]]]
```

No card-mod, no cascade guessing, no shadow DOM surprises. Useful for wall
tablets and kiosk dashboards where cards often sit outside the normal theme
inheritance.

## Colour derivation

All maths happens in OKLab so perceived lightness stays steady as hue changes.

- Neutrals are tinted slightly toward the accent, so the interface reads as
  one scheme rather than an accent floating on grey.
- Text is checked against the card background and darkened or lightened until
  it clears **4.5:1** (or **7:1** with high contrast on). Every built-in preset
  passes in both light and dark.
- Glass backgrounds are generated gradients derived from the accent. No image
  files, and the backdrop follows whatever colour you pick.

## Modes

`Light` and `Dark` pin the theme. `Auto` emits both variants and lets the
client choose, which is the normal Home Assistant behaviour.

`Sun` is different: it emits a single variant and swaps it at sunrise and
sunset. Wall tablets and kiosk browsers have no OS-level dark mode to inherit,
so `Auto` leaves them stuck on one variant forever — `Sun` is what makes them
actually change.

Sun mode is the only thing that rewrites the theme file on a schedule, and it
has to: theme YAML is static CSS, and the frontend's only conditional is
`modes: light`/`dark`, which follows the client's colour scheme rather than
the sun. Colours cannot be resolved per request the way icon URLs can.

## Weather icons

51 animated SVGs ship inside the integration, served at
`/chromha_icons/<name>.svg` for fixed artwork and `/chromha_icons_auto/<condition>.svg`
for the sun-aware variant. Nothing to download, nothing to put in `www/`,
and a HACS update keeps the files and the condition mapping in step.

All 19 Home Assistant weather conditions are mapped, including `exceptional`,
`tornado`, `hurricane`, `dust`, and `hazy`.

### Day and night artwork

Home Assistant's `weather-icon-*` theme variables are keyed by condition only,
and CSS cannot know where the sun is. `clear-night` is its own condition, but
`partlycloudy`, `fog`, `rainy`, `snowy` and `lightning-rainy` are not — so a
static theme can only ever ship one icon for each.

ChromHA regenerates its theme file, so it can. `select.*_icon_daynight`:

- **Day only** — day artwork always.
- **Follow theme** *(default)* — night icons in the dark variant, day icons in
  the light one. Free, since both variants already live in the same file and
  the client picks. Assumes dark mode means night, which is usually true.
- **Follow sun** — night icons whenever `sun.sun` is below the horizon, and
  **no rewrite required**. The theme points at `/chromha_icons_auto/<condition>.svg`
  instead of a specific file, and ChromHA picks the artwork when the browser
  asks for it. Those URLs are served with an ETag naming the resolved file, so
  revalidation is a cheap 304 except at the two daily transitions.

Eight conditions get distinct night artwork: `sunny`, `partlycloudy`, `fog`,
`hazy`, `rainy`, `pouring`, `snowy` and `lightning-rainy`. The rest — `hail`,
`tornado`, `dust`, `hurricane`, `cloudy` — look the same either way and keep
one icon.

### Intensity

`select.*_icon_intensity` picks how heavy the rain and snow artwork looks:
`rainy-1/2/3` and `snowy-1/2/3`. Home Assistant reports `rainy` and `snowy`
without a severity, so this is a look preference rather than live data.
`pouring` always uses the heaviest tier regardless.

### The rest of the set

Home Assistant defines 19 weather conditions; the pack has 51 icons. The
surplus — `frost`, `rain-and-sleet-mix`, `snow-and-sleet-mix`,
`tropical-storm`, `isolated-thunderstorms`, the `cloudy-2`/`cloudy-3` tiers —
has no HA condition to attach to, so it is published on the palette sensor as
`icon_library`:

```yaml
icon_library:
  frost-night: /chromha_icons/frost-night.svg
  tropical-storm: /chromha_icons/tropical-storm.svg
  ...
```

A card can use any of them directly:

```yaml
[[[ return hass.states['sensor.chromha_ryan_palette']
      .attributes.icon_library['tropical-storm'] ]]]
```

## Install

### HACS (recommended)

Click the button above, or add this repository manually:

HACS → three-dot menu → **Custom repositories** → paste the repo URL →
category **Integration** → Add → install → restart Home Assistant.

### Manual

Copy `custom_components/chromha/` into your Home Assistant `config/` folder
and restart.

### Set up

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=chromha)

Or: Settings → Devices & Services → Add Integration → **ChromHA**. Add one
profile per person, then pick your theme in your user profile
(Settings → your name → Theme).

Adding a *new* profile needs one browser refresh before the theme shows up in
the dropdown. Changing settings on an existing profile applies on reload
without one.

## How it works

Home Assistant has no runtime API for registering themes, so ChromHA does the
only thing available: writes `config/themes/chromha.yaml` and calls
`frontend.reload_themes`.

Rebuilds are debounced 1.5s and skipped entirely when the rendered output is
unchanged, so dragging a slider doesn't hammer the disk. Writes go through the
executor and land atomically via a temp file.

Settings live in the config entry's options, which gives free persistence and
one update listener to trigger rebuilds.

Do not hand-edit the generated file. It is overwritten.

## Known gaps

- HA 2026.5 moved switches and checkboxes to a new component library and
  dropped several `switch-*` variables. The current names are set, but if
  toggles render wrong on your version, that is the first place to look.
- Nothing from the 2025.8 semantic colour scale (`--md-sys-color-*`) is set
  yet, so some newer components still fall back to HA defaults.
- `exceptional` maps to `severe-thunderstorm`, which is approximate.

## Credits

Weather icons from
[Makin-Things/weather-icons](https://github.com/Makin-Things/weather-icons)
(MIT), derived from the
[amCharts free animated SVG weather icons](https://www.amcharts.com/free-animated-svg-weather-icons/)
(CC BY 4.0).

The idea of pairing animated weather icons with a Home Assistant theme, and
several preset accents, come from the
[Caule Themes Pack 1](https://github.com/ricardoquecria/caule-themes-pack-1)
by Ricardo Correia (MIT). ChromHA shares no code with it but owes it the
concept. See [NOTICE.md](NOTICE.md).

MIT licensed. If you fork this, the amCharts attribution has to come with you.

## Contributing

Two checks run on every push: `hassfest` (Home Assistant manifest validation)
and the HACS action (repository structure). Both must pass.

When cutting a release, bump `version` in
`custom_components/chromha/manifest.json` to match the tag — a workflow fails
the release if they disagree, because HACS serves whatever the manifest says.

## Brand assets

`assets/logo.svg` is the source artwork — true vector, so every PNG is
regenerated from it rather than resampled. Stroke weights are tuned so the
circuit nodes stay readable as rings down to 32px.

`custom_components/chromha/brand/icon.png` is what HACS checks. For the icon
to also appear in the Home Assistant UI, submit `icon.png`, `icon@2x.png`,
`logo.png` and `logo@2x.png` to
[home-assistant/brands](https://github.com/home-assistant/brands) under
`custom_integrations/chromha/`. Generate them with:

```bash
python3 -c "import cairosvg; [cairosvg.svg2png(url='assets/logo.svg', \
  write_to=n, output_width=s, output_height=s) for n, s in \
  [('icon.png',256),('icon@2x.png',512),('logo.png',256),('logo@2x.png',512)]]"
```

## Weather icon set

All 51 icons from [Makin-Things/weather-icons](https://github.com/Makin-Things/weather-icons)
are bundled. 31 are reachable through the condition mapping across the
day/night and intensity combinations; the remaining 20 are available via
`icon_library` on the palette sensor.

<!-- badges -->
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square
[hacs-url]: https://github.com/hacs/integration
[release-badge]: https://img.shields.io/github/v/release/vyssecodes/chromha?style=flat-square
[release-url]: https://github.com/vyssecodes/chromha/releases
[license-badge]: https://img.shields.io/github/license/vyssecodes/chromha?style=flat-square
