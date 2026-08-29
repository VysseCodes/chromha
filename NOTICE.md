# Attribution

> Licensing note: `LICENSE` is plain MIT so automated licence detectors can
> identify it. The third-party terms below apply in addition to it and travel
> with any fork.

ChromHA stands on work by several other people.

## Weather icons

The animated SVG weather icons bundled in
`custom_components/chromha/icons/` come from
[Makin-Things/weather-icons](https://github.com/Makin-Things/weather-icons)
(MIT), used unmodified.

That set is in turn derived from the
[amCharts free animated SVG weather icons](https://www.amcharts.com/free-animated-svg-weather-icons/),
licensed **CC BY 4.0**. amCharts must be credited by anyone redistributing
these files, including anyone forking ChromHA.

## Design lineage

The idea of shipping animated weather icons with a Home Assistant theme, and
several of the accent colours offered as presets, come from the
[Caule Themes Pack 1](https://github.com/ricardoquecria/caule-themes-pack-1)
by Ricardo Correia (MIT).

ChromHA shares no code with that project. It is a separate implementation
built around a config flow and generated themes rather than static YAML, but
it would not exist without the Caule pack demonstrating the idea first.

## Home Assistant

Theme variable names are part of the Home Assistant frontend
(Apache-2.0). ChromHA only sets values for them.
