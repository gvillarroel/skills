#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Read-only static checks for a deck using the bundled Slidev layout templates."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

RUNTIME = ("components/SlidevLayout.vue", "lib/slidev-layouts.mjs", "components/SlidevCollection.vue")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def child(deck: Path, relative: str) -> Path:
    result = (deck / relative).resolve()
    if not result.is_relative_to(deck):
        raise ValueError(f"Path must stay within the deck: {relative}.")
    return result


def fence_errors(source: str) -> tuple[int, list[str]]:
    opened: tuple[str, int] | None = None
    count = 0
    for number, line in enumerate(source.splitlines(), 1):
        match = FENCE.match(line)
        if opened is None and match:
            opened = (match[1], number)
        elif opened and match and match[1][0] == opened[0][0] and len(match[1]) >= len(opened[0]) and not match[2].strip():
            opened = None
            count += 1
    return count, ([f"Unclosed Markdown fence opened on line {opened[1]}."] if opened else [])


def check(deck: Path, data: str | None, expect_items: int | None, require_bundled: bool) -> dict[str, object]:
    errors: list[str] = []
    hashes: dict[str, str] = {}
    bundle = Path(__file__).resolve().parents[1] / "assets/templates/slidev-layouts"
    for relative in ("slides.md", "package.json", *RUNTIME):
        try:
            contents = child(deck, relative).read_bytes()
            if not contents:
                errors.append(f"Required file is empty: {relative}.")
            hashes[relative] = hashlib.sha256(contents).hexdigest()
            if require_bundled and relative in RUNTIME and contents != (bundle / relative).read_bytes():
                errors.append(f"Runtime copy differs from the loaded bundle: {relative}.")
        except (OSError, ValueError) as error:
            errors.append(f"Cannot read {relative}: {error}.")
    dependencies: dict[str, str] = {}
    try:
        package = json.loads(child(deck, "package.json").read_text(encoding="utf-8-sig"))
        if not isinstance(package, dict):
            raise ValueError("package.json must be an object")
        for group in ("dependencies", "devDependencies"):
            declared = package.get(group, {})
            if isinstance(declared, dict):
                dependencies.update({name: version for name, version in declared.items() if isinstance(version, str) and version.strip()})
    except (OSError, ValueError) as error:
        errors.append(f"Cannot parse package.json: {error}.")
    for name in ("@slidev/cli", "vue"):
        if name not in dependencies:
            errors.append(f"Declare {name} in dependencies or devDependencies.")
    themes = sorted(name for name in dependencies if name.startswith("@slidev/theme-") or name.startswith("slidev-theme-") or "/slidev-theme-" in name)
    if not themes:
        errors.append("Declare the selected Slidev theme package, including @slidev/theme-default for the default theme.")
    fences = 0
    try:
        fences, problems = fence_errors(child(deck, "slides.md").read_text(encoding="utf-8-sig"))
        errors.extend(problems)
    except (OSError, ValueError) as error:
        errors.append(f"Cannot inspect slides.md: {error}.")
    item_count: int | None = None
    if data:
        try:
            payload = json.loads(child(deck, data).read_text(encoding="utf-8-sig"))
            items = payload.get("items", payload.get("cards")) if isinstance(payload, dict) else payload
            if not isinstance(items, list):
                raise ValueError("data must be an array, or an object with an items/cards array")
            item_count = len(items)
            ids: list[str] = []
            for index, item in enumerate(items):
                if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
                    raise ValueError(f"item {index + 1} needs a nonempty string id")
                ids.append(item["id"])
                for key in ("category", "title", "body"):
                    if key in item and not isinstance(item[key], str):
                        raise ValueError(f"item {item['id']} field {key} must be a string")
                if "width" in item and (isinstance(item["width"], bool) or not isinstance(item["width"], (float, int)) or not math.isfinite(item["width"]) or item["width"] <= 0):
                    raise ValueError(f"item {item['id']} width must be positive")
            if len(set(ids)) != len(ids):
                raise ValueError("item ids must be unique")
            if expect_items is not None and item_count != expect_items:
                errors.append(f"Expected {expect_items} data items; found {item_count}.")
        except (OSError, ValueError) as error:
            errors.append(f"Cannot inspect data: {error}.")
    return {"passed": not errors, "deck": str(deck), "itemCount": item_count, "balancedFences": not any("Unclosed Markdown" in error for error in errors), "completedFences": fences, "declaredThemePackages": themes, "runtimeCopyRequired": require_bundled, "sha256": hashes, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deck", required=True, type=Path)
    parser.add_argument("--data", help="Optional JSON data path relative to the deck.")
    parser.add_argument("--expect-items", type=int)
    parser.add_argument("--require-bundled-runtime", action="store_true")
    args = parser.parse_args()
    if args.expect_items is not None and (args.expect_items < 0 or not args.data):
        parser.error("--expect-items requires --data and a nonnegative count")
    result = check(args.deck.resolve(), args.data, args.expect_items, args.require_bundled_runtime)
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
