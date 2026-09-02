#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently validate isolated vector-logo evaluation deliverables."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--skill", type=Path, default=Path("skills/plantuml-colorset-renderer"))
    parser.add_argument("--case", choices=("contract", "naturalistic"), required=True)
    args = parser.parse_args()
    workspace, skill = args.workspace.resolve(), args.skill.resolve()
    if not workspace.is_relative_to((Path.cwd() / "evaluations/runs").resolve()):
        parser.error("Workspace must belong to an isolated evaluation run")
    sys.path.insert(0, str(skill / "scripts"))
    from export_logo_asset import prepare_export
    from logo_svg import inspect_vector

    deliverable = workspace / "deliverable"
    failures = []
    requests = ([
        ("devicon-python", "adaptive", "#007298", "python-blue"),
    ] if args.case == "contract" else [
        ("devicon-python", "adaptive", "#9e1b32", "python-red"),
        ("devicon-kubernetes", "mono-white", None, "kubernetes-white"),
        ("aws-compute-lambda", "color", None, "lambda-color"),
    ])
    expected_files = set()
    for logo_id, variant, color, stem in requests:
        expected_svg, expected_metadata, expected_license = prepare_export(skill / "assets/logos", logo_id, variant, color)
        files = {"svg": deliverable / f"{stem}.svg", "provenance": deliverable / f"{stem}.provenance.json", "license": deliverable / f"{stem}.license.txt"}
        expected_files.update(path.name for path in files.values())
        for label, path in files.items():
            if not path.is_file():
                failures.append(f"missing {label}: {path.name}")
        if not all(path.is_file() for path in files.values()):
            continue
        actual_svg = files["svg"].read_bytes()
        try:
            inspect_vector(actual_svg)
            root = ET.fromstring(actual_svg)
        except (ValueError, ET.ParseError) as error:
            failures.append(f"invalid vector {files['svg'].name}: {error}")
            continue
        if actual_svg != expected_svg:
            failures.append(f"wrong exact SVG bytes: {files['svg'].name}")
        if json.loads(files["provenance"].read_text(encoding="utf-8")) != expected_metadata:
            failures.append(f"wrong provenance: {files['provenance'].name}")
        if files["license"].read_bytes() != expected_license:
            failures.append(f"wrong complete license: {files['license'].name}")
        expected_variant = "custom-color" if color else variant
        if root.get("data-logo-id") != logo_id or root.get("data-logo-variant") != expected_variant or root.get("data-vector-only") != "true":
            failures.append(f"wrong SVG markers: {files['svg'].name}")
    if args.case == "contract":
        choice = deliverable / "lambda-choice.json"
        expected_files.add(choice.name)
        try:
            payload = json.loads(choice.read_text(encoding="utf-8"))
            if len(payload) != 1 or payload[0]["id"] != "aws-compute-lambda" or payload[0]["available"] is not False or payload[0]["reason"] != "license-no-derivatives":
                failures.append("Lambda choice does not fail closed with the recorded license reason")
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
            failures.append(f"invalid lambda-choice.json: {error}")
    else:
        notes = deliverable / "selection-notes.md"
        expected_files.add(notes.name)
        try:
            content = notes.read_text(encoding="utf-8").casefold()
            for token in ("devicon-python", "devicon-kubernetes", "aws-compute-lambda", "adaptive"):
                if token not in content:
                    failures.append(f"selection-notes.md omits {token}")
            if "currentcolor" not in content and not all(token in content for token in ("inline", "inherit", "bake")):
                failures.append("selection-notes.md does not correctly explain adaptive inline inheritance or baking")
            if "cc-by-nd-2.0" not in content and not ({"derivative", "recolor"} & set(content.replace("-", " ").split())):
                failures.append("selection-notes.md omits the Lambda no-derivatives/recoloring restriction")
        except OSError as error:
            failures.append(f"missing selection-notes.md: {error}")
    if deliverable.is_dir():
        extras = sorted(path.name for path in deliverable.iterdir() if path.is_file() and path.name not in expected_files)
        if extras:
            failures.append("unexpected deliverables: " + ", ".join(extras))
    print(json.dumps({"ok": not failures, "case": args.case, "requestCount": len(requests), "expectedFiles": sorted(expected_files), "failures": failures}, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
