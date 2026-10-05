#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a native-size measured connected Slidev flow from a small JSON contract."""
import argparse
import json
from pathlib import Path
import re

PALETTES = {
    "colorset1": {"fill": "#333e48", "text": "#ffffff", "ink": "#333e48", "accent": "#9e1b32"},
    "colorset2": {"fill": "#007298", "text": "#ffffff", "ink": "#333e48", "accent": "#9e1b32"},
}


def validate_config(raw):
    if not isinstance(raw, dict):
        raise ValueError("Flow configuration must be a JSON object.")
    allowed = {"id", "title", "labels", "branch", "return", "palette"}
    if set(raw) - allowed:
        raise ValueError(f"Unknown configuration keys: {sorted(set(raw) - allowed)}")
    labels = raw.get("labels")
    if not isinstance(labels, list) or not 2 <= len(labels) <= 6 or any(not isinstance(x, str) or not x.strip() or len(x) > 64 for x in labels):
        raise ValueError("Use two to six nonempty main-row labels, each at most 64 characters.")
    if len(set(labels)) != len(labels):
        raise ValueError("Main-row labels must identify distinct concepts.")
    config = {"id": raw.get("id", "connected-flow"), "title": raw.get("title", "Connected flow"), "labels": labels, "palette": raw.get("palette", "colorset1")}
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", config["id"]):
        raise ValueError("Use a lowercase hyphen-case flow ID.")
    if config["palette"] not in PALETTES:
        raise ValueError("Palette must be colorset1 or colorset2.")
    config.update(PALETTES[config["palette"]])
    branch = raw.get("branch")
    if branch:
        if set(branch) - {"at", "label", "outLabel", "backLabel"} or type(branch.get("at")) is not int or not 0 <= branch["at"] < len(labels):
            raise ValueError("Branch needs a valid main-row index in at and one reciprocal auxiliary label.")
        if not isinstance(branch.get("label"), str) or not branch["label"].strip():
            raise ValueError("Branch label must be nonempty.")
        config["branch"] = {**branch, "outLabel": branch.get("outLabel", "check"), "backLabel": branch.get("backLabel", "return")}
    back = raw.get("return")
    if back:
        if set(back) - {"source", "target", "label"} or any(type(back.get(k)) is not int for k in ("source", "target")) or not 0 <= back["target"] < back["source"] < len(labels):
            raise ValueError("Return source must be after its target in the main row.")
        config["return"] = {**back, "label": back.get("label", "return")}
    return config


def scaffold(raw, deck, component="ConnectedFlow", force=False):
    config = validate_config(raw)
    if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", component):
        raise ValueError("Component must be a PascalCase Vue identifier.")
    paths = [deck / "components" / f"{component}.vue", deck / "package.json", deck / "slides.md"]
    if not force and any(p.exists() for p in paths):
        raise ValueError("Output files already exist; use --force only for an intentional rebuild.")
    template = Path(__file__).resolve().parents[1] / "assets/templates/ConnectedFlow.vue"
    source = template.read_text(encoding="utf-8").replace("__FLOW_CONFIG__", json.dumps(config, ensure_ascii=True).replace("<", "\\u003c"))
    paths[0].parent.mkdir(parents=True, exist_ok=True)
    paths[0].write_text(source, encoding="utf-8")
    paths[1].write_text(json.dumps({"private": True, "type": "module", "scripts": {"dev": "slidev --port 4173", "build": "slidev build"}, "dependencies": {"@slidev/cli": "^53.0.0", "@slidev/theme-default": "^0.25.0", "animejs": "^4.0.0", "vue": "^3.5.0"}}, indent=2) + "\n", encoding="utf-8")
    clicks = 2 if config.get("branch") or config.get("return") else 1
    paths[2].write_text(f"---\ntheme: default\ntitle: {json.dumps(config['title'])}\nclicks: {clicks}\n---\n\n# {config['title']}\n\n<{component} :step=\"$clicks\" />\n", encoding="utf-8")
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--deck", type=Path, required=True)
    parser.add_argument("--component", default="ConnectedFlow")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        paths = scaffold(json.loads(args.config.read_text(encoding="utf-8")), args.deck, args.component, args.force)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({"written": [str(p) for p in paths], "next": f"npm --prefix {args.deck} install && npm --prefix {args.deck} run build"}))


if __name__ == "__main__":
    main()
