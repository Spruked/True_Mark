"""Generate the original SVG frame library from the governed registry."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path

from frame_catalog import FRAME_CATALOG


ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 816, 1056  # US Letter at 96 CSS pixels per inch


def _pattern(frame: dict) -> str:
    group = frame["group"]
    number = int(frame["number"])
    if group == "modern_tech":
        return f'<rect x="72" y="72" width="672" height="912" class="fine"/><path d="M72 {84 + number % 3 * 5} H744 M72 {972 - number % 3 * 5} H744" class="accent"/><path d="M84 72 V984 M732 72 V984" class="fine"/>'
    if group == "ornamental":
        return f'<rect x="72" y="72" width="672" height="912" class="accent"/><circle cx="72" cy="72" r="{14 + number % 5}" class="accent"/><circle cx="744" cy="72" r="{14 + number % 5}" class="accent"/><circle cx="72" cy="984" r="{14 + number % 5}" class="accent"/><circle cx="744" cy="984" r="{14 + number % 5}" class="accent"/>'
    if group == "heavy_elite":
        return '<rect x="52" y="52" width="712" height="952" class="heavy"/><rect x="70" y="70" width="676" height="916" class="accent"/>'
    if group == "ultra_minimal":
        return '<path d="M72 72 H744 V984 H72 Z" class="fine"/>'
    return '<rect x="58" y="58" width="700" height="940" class="accent"/><rect x="72" y="72" width="672" height="912" class="fine"/>'


def render(frame: dict) -> str:
    title = escape(str(frame["name"]))
    group = escape(str(frame["group_label"]))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" viewBox="0 0 {WIDTH} {HEIGHT}">
  <title>TrueMark {title}</title>
  <desc>Presentation-only 8.5 by 11 inch certificate frame. Group: {group}.</desc>
  <defs><pattern id="micro" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0 8 L8 0" stroke="#0f2e74" stroke-width="0.35" opacity="0.32"/></pattern></defs>
  <rect width="100%" height="100%" fill="none"/>
  <rect x="42" y="42" width="732" height="972" fill="url(#micro)" opacity="0.06"/>
  <g fill="none" stroke-linecap="round">{_pattern(frame)}</g>
  <text x="408" y="1032" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#52717e" letter-spacing="2">TRUEMARK FRAME {int(frame["number"]):02d}</text>
  <style>.heavy{{stroke:#0f2e74;stroke-width:10}}.accent{{stroke:#daa520;stroke-width:3}}.fine{{stroke:#0f2e74;stroke-width:1.2}}</style>
</svg>
'''


def main() -> None:
    directory = ROOT / "frames"
    directory.mkdir(parents=True, exist_ok=True)
    (ROOT / "FRAME_CATALOG.json").write_text(
        json.dumps(FRAME_CATALOG, indent=2) + "\n", encoding="utf-8"
    )
    for frame in FRAME_CATALOG:
        path = directory / Path(str(frame["asset"])).name
        path.write_text(render(frame), encoding="utf-8")
    print(f"Generated {len(FRAME_CATALOG)} SVG certificate frames in {directory}")


if __name__ == "__main__":
    main()
