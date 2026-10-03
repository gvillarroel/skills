#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Probe public authored-paint entry points with a valid and an invalid token."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
def module(skill, script):
    directory = ROOT / "skills" / skill / "scripts"
    sys.path.insert(0, str(directory))
    spec = importlib.util.spec_from_file_location(skill.replace("-", "_") + "_" + script, directory / f"{script}.py")
    value = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = value
    spec.loader.exec_module(value)
    return value

checks = []
def rejects(name, callback):
    try:
        callback()
    except ValueError as error:
        assert "colorset" in str(error), (name, str(error))
        checks.append({"skill": name, "invalidPaintRejected": True, "diagnostic": str(error)})
    else:
        raise AssertionError(f"{name}: arbitrary authored paint was accepted")

compose = module("compose-synchronized-svg", "theme_contract")
rejects("compose-synchronized-svg", lambda: compose.resolve_theme({"colors": {"accent": "#123456"}}, []))
diagram = module("diagram-composition", "compose_diagram")
assert diagram.semantic_colors({"concepts": [{"id": "test", "color": "#9e1b32"}]}) == {"test": "#9e1b32"}
rejects("diagram-composition", lambda: diagram.semantic_colors({"concepts": [{"id": "test", "color": "#123456"}]}))
poster = module("usefulcharts-style", "render_chart")
assert poster.color("#9e1b32") == "#9E1B32"
rejects("usefulcharts-style", lambda: poster.color("#123456"))
manim = module("manim-svg-video", "compose_svg_video")
args = argparse.Namespace(**manim.DEFAULTS, config=None)
args.background = "#123456"
rejects("manim-svg-video", lambda: manim.normalize_args(args))
video = module("video", "validate_scene_contract")
scene = json.loads((ROOT / "skills/video/assets/templates/scene-contract.json").read_text())
scene["canvas"]["background"] = "#123456"
report = video.validate_contract(scene, ROOT)
assert any("#123456" in item and "colorset" in item for item in report["failures"]), report
checks.append({"skill": "video", "invalidPaintRejected": True})
result = {"ok": True, "checks": checks, "fixedPaletteRoutes": ["hierarchy-lens", "hyperframes-explainer"]}
output = ROOT / "projects/compositions-colorset-audit/artifacts/reviews/palette-guards.json"
output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
