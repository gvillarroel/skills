#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate an editable local HyperFrames starter without installing or building."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


def merge(base, supplied):
    result = dict(base)
    for key, value in supplied.items():
        if key not in base:
            raise ValueError(f"Unknown configuration key: {key}")
        if isinstance(base[key], dict):
            if not isinstance(value, dict):
                raise ValueError(f"{key} must be a JSON object")
            result[key] = merge(base[key], value)
        else:
            result[key] = value
    return result


def positive(value, name, minimum, maximum, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if not minimum <= value <= maximum or (integer and value != int(value)):
        raise ValueError(f"{name} must be between {minimum} and {maximum}" + (" and an integer" if integer else ""))


def validate(config):
    if config["colorset"] not in ("colorset1", "colorset2"):
        raise ValueError("colorset must be colorset1 or colorset2")
    for key, value in config["titles"].items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"titles.{key} must be nonempty text")
    for key, value in config["explanation"].items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"explanation.{key} must be nonempty text")
    cues = config["cueTimes"]
    if not isinstance(cues, list) or not cues:
        raise ValueError("cueTimes must be a nonempty array")
    for index, value in enumerate(cues):
        positive(value, f"cueTimes[{index}]", 0, 12)
    positive(config["exportTime"], "exportTime", 0, 12)
    positive(config["heroHeight"], "heroHeight", 255, 330)
    if config["composition"] != "hyperframes/starter.html" or config["compactComposition"] != "hyperframes/starter.html?compact=1":
        raise ValueError("The scaffold uses the local starter; integrate custom scenes in the generated adapter afterward")
    layout = config["compactLayout"]
    if layout["mode"] not in ("columns", "grid", "masonry-columns"):
        raise ValueError("compactLayout.mode must be columns, grid or masonry-columns")
    positive(layout["columns"], "compactLayout.columns", 1, 2, True)
    positive(layout["height"], "compactLayout.height", 288, 330)
    positive(layout["gap"], "compactLayout.gap", 0, 24)
    positive(layout["playerHeight"], "compactLayout.playerHeight", 152, 210)
    positive(layout["minItemWidth"], "compactLayout.minItemWidth", 275, 400)
    positive(layout["minItemHeight"], "compactLayout.minItemHeight", layout["playerHeight"] + 78, layout["height"])


def inside(path, workspace, label):
    resolved = path.resolve()
    if not resolved.is_relative_to(workspace):
        raise ValueError(f"{label} leaves the current workspace")
    return resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deck", required=True, type=Path, help="Deck directory inside the current workspace; identical existing files are preserved")
    parser.add_argument("--config", type=Path, help="Optional JSON overrides for titles, cues, colorset and compact layout")
    parser.add_argument("--review", type=Path, help="Review path; defaults to deliverables/hyperframes-review.md beside the deck")
    args = parser.parse_args()
    try:
        workspace = Path.cwd().resolve()
        skill = Path(__file__).resolve().parents[1]
        starter = skill / "assets/templates/slidev-hyperframes-starter"
        deck = inside(args.deck, workspace, "Deck path")
        if deck == workspace or deck.is_relative_to(skill):
            raise ValueError("Choose a separate deck directory outside the read-only skill bundle")
        if deck.exists() and not deck.is_dir():
            raise ValueError("The deck path must be a directory")
        review = inside(args.review or deck.parent / "deliverables/hyperframes-review.md", workspace, "Review path")
        if review.is_relative_to(skill) or review.is_relative_to(deck):
            raise ValueError("Choose a review file outside the deck and read-only skill bundle")
        config = json.loads((starter / "data/hyperframes-story.json").read_text(encoding="utf-8"))
        if args.config:
            supplied = json.loads(inside(args.config, workspace, "Configuration path").read_text(encoding="utf-8-sig"))
            if not isinstance(supplied, dict):
                raise ValueError("Configuration must be a JSON object")
            config = merge(config, supplied)
        validate(config)
        planned = {}
        for name in ("slidev-hyperframes", "slidev-layouts", "slidev-diagram-style"):
            folder = skill / "assets/templates" / name
            for source in sorted(folder.rglob("*")):
                if source.is_file():
                    planned[deck / source.relative_to(folder)] = source.read_bytes()
        for name in ("components", "setup", "styles"):
            for source in sorted((starter / name).rglob("*")):
                if source.is_file():
                    planned[deck / name / source.relative_to(starter / name)] = source.read_bytes()
        for name in ("package.json", "vite.config.ts"):
            planned[deck / name] = (starter / name).read_bytes()
        planned[deck / "data/hyperframes-story.json"] = (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        slides = (starter / "slides.md.tmpl").read_text(encoding="utf-8")
        slides = slides.replace("@CLICKS@", str(len(config["cueTimes"]) - 1))
        planned[deck / "slides.md"] = slides.encode("utf-8")
        planned[review] = (starter / "review.md.tmpl").read_bytes()
        # Check every planned target before creating directories or changing files.
        for target, data in planned.items():
            boundary = deck if target != review else workspace
            if not target.resolve().is_relative_to(boundary):
                raise ValueError(f"Generated path leaves its output boundary: {target}")
            for parent in target.parents:
                if parent == workspace:
                    break
                if parent.exists() and not parent.is_dir():
                    raise ValueError(f"A generated parent path is a file: {parent}")
            if target.exists() and (not target.is_file() or target.read_bytes() != data):
                raise ValueError(f"Preserve differing existing file: {target}; integrate existing decks manually")
        for target, data in planned.items():
            if target != review and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        checks = []
        for name, options in (("check_hyperframes_deck.py", ["--direct-open"]), ("check_layout_deck.py", [])):
            command = [sys.executable, str(skill / "scripts" / name), "--deck", str(deck), "--require-bundled-runtime", *options]
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
            if result.returncode:
                raise ValueError(f"Bundled static check failed: {name}\n{result.stdout}{result.stderr}")
            checks.append({"script": name, "accepted": True})
        review.parent.mkdir(parents=True, exist_ok=True)
        if not review.exists():
            review.write_bytes(planned[review])
        print(json.dumps({"accepted": True, "deck": str(deck), "review": str(review), "checks": checks,
                          "installed": False, "built": False, "browserQualified": False}, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"accepted": False, "error": str(error)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
