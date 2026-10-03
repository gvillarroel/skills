#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regenerate controlled before/after text-pair cases from the same briefs."""

from __future__ import annotations

import colorsys
import copy
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "skills/compose-synchronized-svg/scripts"
ARTIFACTS = ROOT / "projects/svg-text-contrast/artifacts"
sys.path.insert(0, str(SCRIPTS))
import compile_synchronized_svg_plan as compiler
import compose_synchronized_svg as composer
import scaffold_synchronized_svg as scaffold


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_case(name: str, brief: dict) -> None:
    directory = ARTIFACTS / name
    directory.mkdir(parents=True, exist_ok=True)
    plan, _ = compiler.compile_brief(brief)
    (directory / "brief.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")
    spec = directory / "plan.json"
    spec.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    for variant, renderer in (("before", old_composer), ("after", composer)):
        renderer.compose(SimpleNamespace(spec=spec, output=directory / f"{variant}.svg", report=None, force=True))
    print(f"Generated {name}: identical brief, plan, and semantic values")


old_scaffold = load_module("contrast_before_scaffold", ARTIFACTS / "before/scaffold_synchronized_svg.py")
old_composer = load_module("contrast_before_composer", ARTIFACTS / "before/compose_synchronized_svg.py")
old_composer.scaffold = old_scaffold

template = json.loads((SCRIPTS.parent / "assets/templates/composition-brief.json").read_text(encoding="utf-8"))
template["timeline"] = None
near = copy.deepcopy(template)
near["theme"] = {"colors": {"canvas": "#ffffff", "surface": "#ffffff", "ink": "#767676", "muted": "#767676"}}
write_case("near-threshold", near)

world = json.loads((SCRIPTS.parent / "assets/templates/navigable-world-brief.json").read_text(encoding="utf-8"))
write_case("world-light", world)

dark = copy.deepcopy(template)
dark["theme"] = {"colors": {
    "canvas": "#101820", "surface": "#18242f", "ink": "#f1f5f9", "muted": "#b8c5d2",
    "line": "#425666", "accent": "#70dfc4", "focus": "#ffcf70", "warning": "#ffd582", "danger": "#ff9aaf",
}}
plan, _ = compiler.compile_brief(template)
roots = list(dict.fromkeys(scaffold.theme_token_map(plan).values()))
dark["theme"]["conceptColors"] = {}
for index, root in enumerate(roots):
    rgb = colorsys.hls_to_rgb((index * .618033988749895) % 1, .75, .68)
    dark["theme"]["conceptColors"][root] = "#{:02x}{:02x}{:02x}".format(*(round(c * 255) for c in rgb))
write_case("compact-dark", dark)

light = copy.deepcopy(template)
light["theme"] = {"conceptColors": {roots[0]: "#888888"}}
write_case("light-mark", light)
