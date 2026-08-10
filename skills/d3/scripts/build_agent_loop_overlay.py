#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Build the standalone d3-agent-loop-overlay HTML pattern."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_IMAGE = SKILL_ROOT / "assets" / "reference" / "agent-loop-reference.png"
REGIONS = (
    ("main-loop", 38, 82, 272, 488, 0.34, "#e77204", "#994a00", 0.10),
    ("prompt-builder", 354, 68, 586, 98, 0.62, "#652f6c", "#431f47", 0.48),
    ("tool-system", 354, 220, 382, 236, 0.50, "#45842a", "#294d19", 0.86),
    ("sub-agents", 752, 220, 192, 232, 0.55, "#007298", "#004d66", 1.24),
    ("compaction", 354, 512, 590, 94, 0.58, "#f1c319", "#98700c", 1.62),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Exact standalone HTML output path")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output")
    return parser.parse_args()


def region_markup() -> str:
    image_x, image_y, image_width, image_height = 16, 34, 528, 333
    scale_x = image_width / 980
    scale_y = image_height / 618
    groups: list[str] = []
    for region_id, x, y, width, height, cover, fill, stroke, delay in REGIONS:
        mapped_x = image_x + x * scale_x
        mapped_y = image_y + y * scale_y
        mapped_width = width * scale_x
        mapped_height = height * scale_y
        target_width = mapped_width * cover
        groups.append(
            f'''<g id="{region_id}" class="region" data-region="{region_id}" data-cover-ratio="{cover}">
  <rect class="cover" x="{mapped_x:.3f}" y="{mapped_y:.3f}" width="{target_width:.3f}" height="{mapped_height:.3f}" rx="7" fill="{fill}" fill-opacity="0.19" stroke="{stroke}" stroke-width="1.4" stroke-dasharray="6 5">
    <animate attributeName="width" from="0" to="{target_width:.3f}" dur="0.58s" begin="{delay:.2f}s" calcMode="spline" keySplines=".2 .7 .2 1" fill="freeze" />
    <animate attributeName="fill-opacity" values="0.08;0.24;0.19" dur="0.9s" begin="{delay:.2f}s" fill="freeze" />
  </rect>
  <line class="sweep" x1="{mapped_x:.3f}" x2="{mapped_x:.3f}" y1="{mapped_y + 4:.3f}" y2="{mapped_y + mapped_height - 4:.3f}" stroke="{stroke}" stroke-width="2.2" stroke-opacity="0">
    <animate attributeName="x1" from="{mapped_x:.3f}" to="{mapped_x + target_width:.3f}" dur="0.58s" begin="{delay:.2f}s" fill="freeze" />
    <animate attributeName="x2" from="{mapped_x:.3f}" to="{mapped_x + target_width:.3f}" dur="0.58s" begin="{delay:.2f}s" fill="freeze" />
    <animate attributeName="stroke-opacity" values="0;0.85;0" dur="0.7s" begin="{delay:.2f}s" fill="freeze" />
  </line>
</g>'''
        )
    return "\n".join(groups)


def build_html() -> str:
    if not REFERENCE_IMAGE.is_file():
        raise SystemExit(f"Bundled reference image is missing: {REFERENCE_IMAGE}")
    image_uri = "data:image/png;base64," + base64.b64encode(REFERENCE_IMAGE.read_bytes()).decode("ascii")
    regions = region_markup()
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Agent loop partial covers</title>
  <style>
    :root {{ color-scheme: light; --ink: #333e48; --muted: #696969; --line: #cfcfcf; --paper: #f7f7f7; --surface: #ffffff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; padding: 24px; background: var(--paper); color: var(--ink); font-family: Arial, sans-serif; }}
    main {{ width: min(1024px, 100%); margin: 0 auto; }}
    h1 {{ margin: 0 0 6px; font-size: clamp(22px, 4vw, 30px); }}
    p {{ margin: 0 0 14px; color: var(--muted); }}
    svg {{ display: block; width: 100%; height: auto; background: var(--surface); border: 1px solid var(--line); }}
    button {{ margin-top: 12px; padding: 8px 14px; border: 1px solid var(--ink); background: var(--surface); color: var(--ink); font: inherit; cursor: pointer; }}
    button:focus-visible {{ outline: 3px solid #ffccd5; outline-offset: 2px; }}
  </style>
</head>
<body>
  <main>
    <h1>Agent loop overlay</h1>
    <p>Five partial covers reveal the main loop, prompt builder, tool system, sub-agents, and compaction regions.</p>
    <svg id="agent-loop-overlay" data-pattern-id="d3-agent-loop-overlay" role="img" aria-labelledby="overlay-title overlay-desc" viewBox="0 0 560 400">
      <title id="overlay-title">Agent loop partial covers</title>
      <desc id="overlay-desc">An embedded agent-loop diagram with five deterministic semantic cover reveals.</desc>
      <defs><clipPath id="image-clip"><rect x="16" y="34" width="528" height="333" /></clipPath></defs>
      <rect x="8" y="26" width="544" height="349" fill="#ffffff" stroke="#cfcfcf" />
      <g clip-path="url(#image-clip)"><image href="{image_uri}" x="16" y="34" width="528" height="333" preserveAspectRatio="xMidYMid meet" opacity="0.76" /></g>
      <g id="cover-layers" clip-path="url(#image-clip)">{regions}</g>
    </svg>
    <button id="replay" type="button">Replay reveal</button>
  </main>
  <script>
    const replay = document.querySelector('#replay');
    replay.addEventListener('click', () => {{
      const current = document.querySelector('#agent-loop-overlay');
      const replacement = current.cloneNode(true);
      current.replaceWith(replacement);
    }});
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {{
      const svg = document.querySelector('#agent-loop-overlay');
      if (svg.pauseAnimations) {{ svg.pauseAnimations(); svg.setCurrentTime(5); }}
    }}
  </script>
</body>
</html>
'''


def main() -> int:
    args = parse_args()
    output = args.output.expanduser().resolve()
    if output.exists() and not args.force:
        raise SystemExit(f"Output already exists: {output}. Pass --force to overwrite it.")
    output.parent.mkdir(parents=True, exist_ok=True)
    html = build_html()
    forbidden = ("http://", "https://", "skills", "skills/d3", "assets/examples")
    leftovers = [value for value in forbidden if value in html]
    if leftovers:
        raise SystemExit(f"Standalone output contains forbidden dependencies: {', '.join(leftovers)}")
    output.write_text(html, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "ok": True,
                "output": str(output),
                "bytes": output.stat().st_size,
                "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "patternId": "d3-agent-loop-overlay",
                "regionIds": [region[0] for region in REGIONS],
                "regionCount": len(REGIONS),
                "embeddedImage": True,
                "forbiddenDependencies": [],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
