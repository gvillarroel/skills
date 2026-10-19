#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify retained test counts, dependency pins, local links, and source hashes."""
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    repository = project.parents[1]
    artifacts = project / "artifacts"
    manifest = json.loads((project / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((project / "package-lock.json").read_text(encoding="utf-8"))
    for name, version in (manifest["dependencies"] | manifest["devDependencies"]).items():
        actual = lock["packages"][f"node_modules/{name}"]["version"]
        assert actual == version, (name, version, actual)

    tap = (artifacts / "tests-final.tap").read_text(encoding="utf-8")
    totals = {name: int(re.search(rf"^# {name} (\d+)$", tap, re.M)[1]) for name in ("tests", "pass", "fail", "cancelled", "skipped")}
    assert totals == {"tests": 129, "pass": 128, "fail": 0, "cancelled": 0, "skipped": 1}, totals
    junit = ET.parse(artifacts / "tests-final.junit.xml").getroot()
    cases = list(junit.iter("testcase"))
    assert len(cases) == totals["tests"]
    assert len(list(junit.iter("failure"))) == 0
    skipped = [case for case in cases if case.find("skipped") is not None]
    assert len(skipped) == 1 and "Photon" in skipped[0].attrib["name"]

    files = sorted({*project.glob("*.md"), *project.glob("scripts/*.ts"), *project.glob("scripts/*.py"), *project.glob("diagrams/*.mmd"), *project.glob("diagrams/*.md"), project / "package.json", project / "package-lock.json", repository / "docs/pi-durable.md"})
    missing = []
    for path in files:
        if path.suffix != ".md":
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            destination = target.split("#", 1)[0].strip("<>")
            if destination and not (path.parent / destination).resolve().exists():
                missing.append((str(path.relative_to(repository)), target))
    assert not missing, missing

    output = {
        "version": "1.3.0",
        "test_totals": totals,
        "blocked_integration": skipped[0].attrib["name"],
        "local_markdown_links": "passed",
        "storage_timing": json.loads((artifacts / "storage-tasks/storage-timing-final.json").read_text(encoding="utf-8")),
        "authored_source_sha256": {str(path.relative_to(repository)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
    }
    destination = artifacts / "data/verification.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {totals['tests']} test receipts, {len(files)} source files, dependency pins, and local Markdown links.")
    print(f"Report: {destination.relative_to(repository)}")


if __name__ == "__main__":
    main()
