#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""Inspect exact cloud source mappings and embedded vector/raster content."""

from __future__ import annotations

import argparse
import base64
import collections
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


def semantic(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def inspect_svg(payload: bytes, depth: int = 0) -> list[str]:
    if depth > 8:
        return ["nested-depth"]
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        return ["not-svg"]
    issues = []
    if root.tag.rsplit("}", 1)[-1] != "svg":
        issues.append("not-svg")
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag in {"script", "foreignObject", "text", "tspan", "feImage"}:
            issues.append(tag)
        if tag == "image":
            href = node.get("href") or node.get("{http://www.w3.org/1999/xlink}href") or ""
            if href.startswith("data:image/svg+xml;base64,"):
                issues.extend(inspect_svg(base64.b64decode(href.split(",", 1)[1]), depth + 1))
            else:
                issues.append("raster-or-external-image")
    return sorted(set(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--skill", type=Path, required=True)
    args = parser.parse_args()
    assets = args.skill / "assets/logos"
    manifest = json.loads((assets / "logo_manifest.json").read_text(encoding="utf-8"))
    counts = collections.Counter()
    invalid = []
    for item in manifest["logos"]:
        issues = inspect_svg((assets / item["assetPath"]).read_bytes())
        counts.update(issues or ["vector"])
        if issues and item["sourceFormat"] == "svg":
            invalid.append({"id": item["id"], "issues": issues, "sourcePath": item["sourcePath"]})
    print(json.dumps({"embeddedAudit": dict(counts), "svgSourceIssues": invalid}, indent=2))
    aws = yaml.safe_load((args.sources / "aws/scripts/config.yml").read_text(encoding="utf-8"))
    aws_map = {(category, row["Target"]): row for category, data in aws["Categories"].items() for row in data.get("Icons", [])}
    aws_files = collections.defaultdict(list)
    for path in (args.sources / "aws-official").rglob("*.svg"):
        aws_files[path.name].append(path)
    gcp = yaml.safe_load((args.sources / "gcp/scripts/config.yml").read_text(encoding="utf-8"))
    gcp_map = {(category["Name"], row["Target"]): row for category in gcp["Categories"] for row in category.get("Services", [])}
    gcp_files = {semantic(path.stem): path for path in (args.sources / "gcp-legacy").rglob("*.svg")}
    for provider in ("AWS", "GCP"):
        missing = []
        found = 0
        for item in manifest["logos"]:
            if item["provider"] != provider:
                continue
            key = (item["category"], Path(item["sourcePath"]).stem)
            row = (aws_map if provider == "AWS" else gcp_map).get(key)
            name = row["Source"] if row else ""
            if provider == "AWS":
                matches = aws_files.get(Path(name).with_suffix(".svg").name, []) if name else []
            else:
                match = gcp_files.get(semantic(Path(name).stem))
                matches = [match] if match else []
            if len(matches) == 1:
                found += 1
            else:
                missing.append({"id": item["id"], "key": key, "source": name, "matches": len(matches)})
        print(json.dumps({"provider": provider, "exactFound": found, "missing": missing}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
