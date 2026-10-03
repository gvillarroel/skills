#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Build a standalone no-network Three.js HTML file at an exact output path."""

from __future__ import annotations

import argparse
import base64
import json
from html import escape
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = SKILL_ROOT / "assets" / "templates" / "self-contained-token-orbit.html"
MODULE_PATH = SKILL_ROOT / "assets" / "vendor" / "three.module.min.js"
CORE_PATH = SKILL_ROOT / "assets" / "vendor" / "three.core.min.js"
RUNTIME_MARKER = "// __INLINE_THREE_RUNTIME__"
CORE_IMPORT_SPECIFIER = "./three.core.min.js"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Exact HTML output path.")
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1", help="Red and neutrals by default; extended hues require an explicit request.")
    parser.add_argument("--density", choices=("compact", "comfortable"), default="compact", help="Panel and control spacing; does not change object geometry.")
    parser.add_argument("--title", default=None, help="Visible scene heading; defaults to the selected scene name.")
    parser.add_argument("--token-count", type=int, default=5, help="Number of orbiting objects, 1–24; reuse role colors.")
    parser.add_argument("--scene", choices=("orbit", "vector-field"), default="orbit", help="Orbiting solids or directed cone/cylinder vectors.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output file.")
    return parser.parse_args()


def encoded_text(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Required bundled file is missing: {path}")
    return base64.b64encode(path.read_bytes()).decode("ascii")


def inline_runtime() -> str:
    core_base64 = encoded_text(CORE_PATH)
    module_base64 = encoded_text(MODULE_PATH)
    core_specifier = json.dumps(CORE_IMPORT_SPECIFIER)
    return f"""const __decodeThreeSource = (encoded) =>
        new TextDecoder().decode(Uint8Array.from(atob(encoded), (character) => character.charCodeAt(0)));
      const __threeCoreSource = __decodeThreeSource({json.dumps(core_base64)});
      const __threeCoreUrl = URL.createObjectURL(new Blob([__threeCoreSource], {{ type: "text/javascript" }}));
      const __threeModuleSource = __decodeThreeSource({json.dumps(module_base64)}).replaceAll(
        {core_specifier},
        __threeCoreUrl,
      );
      const __threeModuleUrl = URL.createObjectURL(new Blob([__threeModuleSource], {{ type: "text/javascript" }}));
      const THREE = await import(__threeModuleUrl);"""


def build(output: Path, *, force: bool, colorset: str = "colorset1", density: str = "compact", title: str | None = None, token_count: int = 5, scene: str = "orbit") -> Path:
    if colorset not in {"colorset1", "colorset2"} or density not in {"compact", "comfortable"}:
        raise ValueError("Invalid colorset or density")
    if not 1 <= token_count <= 24:
        raise ValueError("--token-count must be between 1 and 24")
    if scene not in {"orbit", "vector-field"}:
        raise ValueError("Invalid scene")
    if not TEMPLATE_PATH.is_file():
        raise SystemExit(f"Required template is missing: {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    marker_count = template.count(RUNTIME_MARKER)
    if marker_count != 1:
        raise SystemExit(f"Expected exactly one {RUNTIME_MARKER!r} marker in {TEMPLATE_PATH}; found {marker_count}.")

    output = output.expanduser().resolve()
    if output.exists() and not force:
        raise SystemExit(f"Output already exists: {output}. Pass --force to overwrite it.")
    output.parent.mkdir(parents=True, exist_ok=True)

    html = template.replace(RUNTIME_MARKER, inline_runtime())
    html = html.replace("__COLORSET__", colorset).replace("__DENSITY__", density).replace("__TITLE__", escape(title or ("Vector Field" if scene == "vector-field" else "Token Orbit")))
    if scene == "vector-field":
        html = html.replace("Animated token orbit scene", "Animated directional vector field")
    html = html.replace("__TOKEN_COUNT__", str(token_count))
    html = html.replace("__SCENE__", scene)
    palette_contract = json.loads((SKILL_ROOT / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))
    html = html.replace("__PALETTES__", json.dumps(palette_contract["colorsets"], separators=(",", ":")))
    if RUNTIME_MARKER in html or 'import * as THREE from "./skills/' in html:
        raise SystemExit("Standalone HTML still contains a filesystem-relative Three.js vendor import.")

    output.write_text(html, encoding="utf-8", newline="\n")
    print(f"Wrote standalone Three.js HTML: {output}")
    return output


def main() -> int:
    args = parse_args()
    build(args.output, force=args.force, colorset=args.colorset, density=args.density, title=args.title, token_count=args.token_count, scene=args.scene)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
