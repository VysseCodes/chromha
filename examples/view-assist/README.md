# Making every View Assist view pull from ChromHA

No entity ids, no palette sensor. Home Assistant themes are CSS custom
properties, and custom properties inherit through the shadow DOM - so a
button-card style can just say `var(--primary-text-color)` and the theme
resolves it. button-card passes style values straight through to CSS.

The palette sensor exists for the cases CSS cannot reach: building a URL,
doing maths on a colour, or anything else that happens in JavaScript. Colours
are not one of those cases.

**Requirement:** the display's user profile must have a ChromHA theme selected.

---

## The variables to use

| Use | CSS variable |
|---|---|
| Body and heading text | `var(--primary-text-color)` |
| Dimmer secondary text | `var(--secondary-text-color)` |
| Page background | `var(--lovelace-background, var(--primary-background-color))` |
| Card background | `var(--ha-card-background)` |
| Accent, active icons | `var(--primary-color)` |
| Inactive icons | `var(--state-icon-color)` |
| Dividers | `var(--divider-color)` |

Always give a fallback as the second argument - `var(--primary-text-color, white)` -
so the view still renders if no theme is applied.

---

## Step 0 - Turn off View Assist's background images

View Assist paints its own background image over every view, which wins over
anything the theme does. It has no "none" option, so point it at ChromHA's
transparent asset instead:

Master Config -> **Background Image Source** -> *Default background*
Master Config -> **Default Background** -> `/chromha_static/transparent.png`

`body_template` sets the background with the CSS `background:` shorthand,
which resets `background-color` to transparent - so a transparent image leaves
the button-card with no background at all, and the Lovelace background behind
it (your theme) shows through.

If the result is black rather than your theme colour, `lovelace-background` is
not set. ChromHA only sets it for the Glass style, so either switch the
profile to Glass or add this after the `background:` line in `body_template`,
where a later declaration wins:

```yaml
        - background-color: var(--primary-background-color)
```

---

## Step 1 - Body text

`button_card_templates` lives at the *dashboard root*, not in a view file:
View Assist dashboard, three-dot menu, **Raw configuration editor**. Back up
that block before editing; `load_view` will not touch it, but a View Assist
dashboard update can.

In `body_template` -> `styles` -> `card`, find:

```yaml
        - color: white
```

Replace with:

```yaml
        - color: var(--primary-text-color, white)
```

That is the default text colour for every view.

## Step 2 - Status icons

In `icon_template` -> `styles` -> `icon`:

```yaml
      icon:
        - display: grid
        - color: var(--primary-color, white)
```

Covers the status icons, the menu, and every `dynamic_*_item`.

## Step 3 - The background fallback

`body_template` already has a branch that paints `background_color` when no
image is set, but nothing ever defined that variable - so it emitted
`no-repeat undefined`, which the browser discards. Define it once in
`variable_template` -> `variables`:

```yaml
      background_color: var(--lovelace-background, var(--primary-background-color, black))
```

One line, and every view that has no background image starts using the theme.

---

## Step 4 - Per-view overrides

Steps 1-3 fix the defaults. These views set their own colours, which win.
Each is in the view's `styles:` block.

| View | Find | Replace with |
|---|---|---|
| Alarm | `background-color: '#24292c'` | `var(--primary-background-color)` |
| Intent | `background-color: '#000000'` | `var(--primary-background-color)` |
| Music | `background-color: black;` | `var(--primary-background-color)` |
| Sports | `background-color: '#1c1c1c'` | `var(--primary-background-color)` |
| Thermostat | `background-color: '#1c1c1c'` | `var(--primary-background-color)` |
| Webpage | `background-color: '#00000'` | `var(--primary-background-color)` |
| Locate | `background: black` | `var(--primary-background-color)` |

The Webpage view's `'#00000'` is five digits. It is not a valid colour and
never did anything.

### Views with a hardcoded background image

Info, Infopic and List each set:

```yaml
        variables:
          background: /view_assist/dashboard/infobackground.png
```

and re-apply it in `styles: card:`. **Delete both** - the variable line and
the `background:` / `background-size:` pair. The view then falls through to
`body_template`, which now paints the theme background from Step 3.

Calendar and Camera reference `url(${variables.background})` without ever
setting it, so they emit `url(undefined)`. Delete those `background:` lines
too.

### List view

The todo colour is inside a `card_mod` string:

```yaml
                    ha-check-list-item {
                      color: white;
```

card_mod cannot evaluate button-card `[[[ ]]]` templates - but it is plain CSS,
so the variable works directly:

```yaml
                    ha-check-list-item {
                      color: var(--primary-text-color);
```

The same applies to the Weather view's forecast rows and Locate's map markers.
This is the reason to prefer CSS variables over the palette sensor: they work
in both places, and button-card templates only work in one.

### Alert view

Hardcoded `#059bf1` with black text throughout. That is a deliberate high-
visibility style - it is meant to interrupt rather than blend in. Leaving it
alone is reasonable.

### Weather view

Uses `#059bf1` in `styles` and `#059bf9` again inside `card_mod`. Since it
wraps the stock `weather-forecast` card, the cleanest fix is to delete the
card_mod background lines entirely and let the theme style the card natively.

---

## After editing

Refresh the dashboard. Changes to `button_card_templates` apply on reload; no
`load_view` call is needed, since these are not view files.

If a view goes blank, a `[[[ ]]]` block is returning `undefined` for a CSS
value and the browser is discarding the whole declaration. Plain
`var(--...)` strings cannot fail that way, which is another reason to prefer
them.
