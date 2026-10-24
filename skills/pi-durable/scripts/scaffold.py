#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Copy the self-contained Pi Durable service template to an exact destination."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def scaffold(destination: Path, *, with_tests: bool = False) -> dict:
    skill = Path(__file__).resolve().parents[1]
    destination = destination.resolve()
    if destination == skill or skill in destination.parents:
        raise ValueError("Generate the service outside the read-only skill bundle.")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("The destination must be absent or an empty directory.")
    template = skill / "assets/templates/service"
    if not (template / "package.json").is_file():
        raise ValueError("The service template is missing from this bundle.")
    tests = skill / "assets/examples/service-acceptance"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, destination, dirs_exist_ok=True)
    included_tests = with_tests and tests.is_dir()
    if included_tests:
        shutil.copytree(tests, destination / "tests")
    package = json.loads((destination / "package.json").read_text(encoding="utf-8"))
    files = {
        path.relative_to(destination).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(destination.rglob("*"))
        if path.is_file()
    }
    manifest = {
        "schemaVersion": 1,
        "template": "pi-durable-service-1.3.0",
        "runtimeSource": {
            "package": "@earendil-works/pi-durable",
            "version": "1.3.0",
            "upstreamCommit": "71023aec1546d6d677a65669c5665c0927ce0dd0",
        },
        "runtimeIndependent": True,
        "tests_included": included_tests,
        "dependencies": package.get("dependencies", {}),
        "devDependencies": package.get("devDependencies", {}),
        "files": files,
    }
    (destination / "scaffold-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    result = {"destination": str(destination), "template": manifest["template"], "tests_included": included_tests}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--with-tests", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(scaffold(args.destination, with_tests=args.with_tests), indent=2))
    except (ValueError, OSError) as error:
        parser.exit(2, f"Scaffold failed: {error}\n")


if __name__ == "__main__":
    main()
