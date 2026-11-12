#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check finite line and label-based Sankey recipes for the connected adapter."""
import argparse
import json
import math
from pathlib import Path


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(spec):
    errors = []
    if not isinstance(spec, dict):
        return ["The request must be a JSON object."]
    if spec.get("colorset", "colorset1") not in {"colorset1", "colorset2"}:
        errors.append("Unknown colorset.")
    if spec.get("preset") == "sankey":
        allowed = {"preset", "title", "colorset", "width", "height", "data"}
        data = spec.get("data", {})
        nodes, links = data.get("nodes", []), data.get("links", [])
        if not nodes or not all(isinstance(n, str) and n for n in nodes) or len(set(map(str, nodes))) != len(nodes):
            errors.append("Sankey nodes must be unique nonempty label strings.")
        for link in links:
            if not isinstance(link, list) or len(link) != 3:
                errors.append("Each Sankey link needs source label, target label and value.")
            elif link[0] not in nodes or link[1] not in nodes or not isinstance(link[0], str) or not isinstance(link[1], str) or not finite(link[2]) or link[2] < 0:
                errors.append("Sankey link endpoints must resolve to exact labels with finite nonnegative weights.")
        if not links:
            errors.append("This focused flow recipe requires links.")
    elif spec.get("preset") == "line":
        allowed = {"preset", "title", "colorset", "width", "height", "data"}
        data = spec.get("data", {})
        x, y = data.get("x", []), data.get("y", [])
        if not x or len(x) != len(y) or not all(finite(v) for v in [*x, *y]):
            errors.append("Line x/y arrays must be paired, nonempty and finite.")
    elif spec.get("version") == 1 and spec.get("factory") == "chart":
        allowed = {"version", "factory", "title", "colorset", "width", "height", "marks", "components", "description", "args", "options"}
        marks = spec.get("marks", [])
        if not marks:
            errors.append("The finite Cartesian recipe requires marks.")
        for mark in marks:
            if not isinstance(mark, dict) or mark.get("kind") not in {"line", "scatter"}:
                errors.append("This focused checker accepts line/scatter marks with kind.")
                continue
            args = mark.get("args", [])
            if len(args) != 2 or not all(isinstance(a, list) for a in args) or not args[0] or len(args[0]) != len(args[1]) or not all(finite(v) for values in args for v in values):
                errors.append("Each mark requires paired finite x/y arrays.")
        for component in spec.get("components", []):
            if not isinstance(component, dict) or component.get("kind") not in {"x_axis", "y_axis", "legend"}:
                errors.append("Use kind for x_axis, y_axis or legend components in this focused profile.")
    else:
        return ["This checker covers preset line/Sankey and version:1 Cartesian line/scatter recipes only."]
    extra = sorted(set(spec) - allowed)
    if extra:
        errors.append("Unexpected fields for the selected recipe: " + ", ".join(extra))
    for key, minimum, maximum in [("width", 320, 2000), ("height", 240, 1400)]:
        if key in spec and (not finite(spec[key]) or not minimum <= spec[key] <= maximum):
            errors.append(f"{key} must be between {minimum} and {maximum} pixels.")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.spec.read_text(encoding="utf-8-sig")))
    except (ValueError, TypeError, AttributeError) as error:
        errors = ["Malformed focused recipe: " + str(error)]
    report = {"passed": not errors, "findings": errors, "scope": "Focused connected JSON recipe check; no renderer or host acceptance claim."}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
