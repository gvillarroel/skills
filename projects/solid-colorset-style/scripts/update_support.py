#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply the solid-fill preference to authored support chrome and instructions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROVIDERS = ("ambientcg-material-search", "iconify-icon-search", "kenney-asset-search", "pexels-media-search", "polyhaven-asset-search", "destockd-video-search")
SUPPORT = (*PROVIDERS, "animated-svg-to-gif", "asciinema-real-command-video", "one-bit-dither-svg", "pixel-art-image-video", "technical-logo-assets", "harbor-author-evaluation-datasets")
GUIDE = """## Solid-fill presentation

For authored filled marks and preview chrome, start with one opaque colorset fill and no decorative border. Prefer saturated/base colors, then dark, bright and neutral solids, with soft fills late. Assign unique usable fills before introducing border variants; exclude the actual canvas color. Choose exact black or white text on each fill by maximum relative-luminance contrast. Keep semantic mappings stable across previews, legends and exports. Only after the usable solid colors are exhausted, expand with contrasting palette border colors, dash patterns and widths. Preserve meaningful line art, connectors, keyboard focus indicators, original source media and explicitly requested conversion aesthetics. Apply this preference to newly authored visuals and framing; preserve required source identity and fidelity.

"""


def replace(path, before, after):
    text = path.read_text(encoding="utf-8")
    if before in text:
        path.write_text(text.replace(before, after), encoding="utf-8")


def main():
    for skill in SUPPORT:
        path = ROOT / "skills" / skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        if "## Solid-fill presentation" not in text:
            index = text.index("\n## ")
            text = text[:index] + "\n\n" + GUIDE.rstrip() + "\n" + text[index:]
        text = text.replace("`#333e48` text, `#cfcfcf` borders", "black text and borderless cards")
        text = text.replace("with light neutral panels and dark labels", "with borderless neutral panels and black labels")
        path.write_text(text, encoding="utf-8")
    for skill in PROVIDERS:
        script = "destockd.py" if skill == "destockd-video-search" else "asset_io.py"
        path = ROOT / "skills" / skill / "scripts" / script
        replace(path, "border:1px solid #cfcfcf", "border:0")
        replace(path, "color:#333e48", "color:#000000")
    pulse = ROOT / "skills/animated-svg-to-gif/assets/templates/pulse.animated.svg"
    replace(pulse, 'stroke="#333e48" stroke-width="4"', 'stroke="none"')
    replace(pulse, 'fill="#333e48"', 'fill="#000000"')
    replace(pulse, 'role="img"', 'role="img" data-colorset="colorset1" data-style-policy="solid-fill-no-outline"')
    logo = ROOT / "skills/technical-logo-assets/assets/logo-audit.html"
    replace(logo, "border:1px solid #cfcfcf", "border:0")
    replace(logo, "color:#333e48", "color:#000000")
    # Keep adaptive SVG ink independent from the visible label's text contrast.
    replace(logo, ".cell label{display:block", ".cell label{color:#000000;display:block")
    replace(logo, ".adaptive{color:", ".dark label{color:#ffffff}.adaptive{color:")
    print(f"Updated {len(SUPPORT)} support bundles; original media and recording bytes remain unchanged.")


if __name__ == "__main__":
    main()
