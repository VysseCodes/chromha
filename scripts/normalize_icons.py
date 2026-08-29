#!/usr/bin/env python3
"""Normalise the bundled weather SVGs so they scale instead of tiling.

Upstream ships them with fixed `width`/`height` on the root element and no
`viewBox`. As a CSS background that gives the image a fixed intrinsic size, so
Home Assistant's weather elements tile it inside any box larger than 56x48
rather than scaling it.

Removing the fixed dimensions and adding a `viewBox` leaves the image with an
intrinsic ratio but no intrinsic size, which makes the browser scale it to fit
the background area. Nothing else in the file is touched.

Idempotent - safe to re-run after pulling new icons from upstream.

    python3 scripts/normalize_icons.py
"""

from __future__ import annotations

import pathlib
import re
import sys

ICON_DIR = (
    pathlib.Path(__file__).resolve().parent.parent
    / "custom_components"
    / "chromha"
    / "icons"
)

ROOT_RE = re.compile(r"<svg\b[^>]*>", re.I)
WIDTH_RE = re.compile(r'\s+width="([\d.]+)"', re.I)
HEIGHT_RE = re.compile(r'\s+height="([\d.]+)"', re.I)


def normalize(text: str) -> tuple[str, str]:
    """Return (new_text, status)."""
    match = ROOT_RE.search(text)
    if not match:
        return text, "no <svg> root"

    root = match.group(0)
    if "viewBox" in root:
        return text, "skipped (already has viewBox)"

    width = WIDTH_RE.search(root)
    height = HEIGHT_RE.search(root)
    if not (width and height):
        return text, "skipped (no numeric width/height)"

    new_root = HEIGHT_RE.sub("", WIDTH_RE.sub("", root), count=1)
    new_root = new_root.replace(
        "<svg",
        f'<svg viewBox="0 0 {width.group(1)} {height.group(1)}" '
        f'preserveAspectRatio="xMidYMid meet"',
        1,
    )
    return text[: match.start()] + new_root + text[match.end() :], "normalised"


def main() -> int:
    if not ICON_DIR.is_dir():
        print(f"icon directory not found: {ICON_DIR}", file=sys.stderr)
        return 1

    counts: dict[str, int] = {}
    for path in sorted(ICON_DIR.glob("*.svg")):
        original = path.read_text(encoding="utf-8")
        updated, status = normalize(original)
        counts[status] = counts.get(status, 0) + 1
        if updated != original:
            path.write_text(updated, encoding="utf-8")

    for status, count in sorted(counts.items()):
        print(f"{count:3}  {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
