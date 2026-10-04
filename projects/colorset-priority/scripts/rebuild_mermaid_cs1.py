#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Regenerate the CS1 Mermaid fixture without rebuilding or replacing CS2."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[3]
GALLERY = ROOT / "skills/mermaid/assets/examples/mermaid-max-complexity"
ARTIFACTS = ROOT / "projects/colorset-priority/artifacts"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cs2_snapshot() -> dict[str, str]:
    paths = [*GALLERY.glob("source/colorset2/*.mmd"), *GALLERY.glob("svg/colorset2/*.svg")]
    paths.extend(GALLERY.glob("reports/colorset2-*.json"))
    return {path.relative_to(GALLERY).as_posix(): digest(path) for path in sorted(paths)}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--staging-id", default="mermaid-cs1")
    args = parser.parse_args()
    if args.jobs < 1 or not args.staging_id.replace("-", "").isalnum():
        parser.error("Use a positive job count and an alphanumeric staging ID.")
    staging = (ARTIFACTS / args.staging_id).resolve()
    if not staging.is_relative_to(ARTIFACTS.resolve()):
        raise ValueError("Staging must remain within the project artifacts directory.")
    staging.mkdir(parents=True, exist_ok=True)
    temporary = ARTIFACTS / "temp"
    temporary.mkdir(parents=True, exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(temporary)
    original = json.loads((GALLERY / "gallery.json").read_text(encoding="utf-8"))
    before = cs2_snapshot()
    original_cs2_patterns = [p for p in original["patterns"] if p["colorset"] == "colorset2"]
    shutil.copytree(GALLERY / "source-overrides", staging / "source-overrides", dirs_exist_ok=True)
    spec = importlib.util.spec_from_file_location("priority_mermaid_builder", GALLERY / "scripts/build_gallery.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the Mermaid gallery builder.")
    builder = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = builder
    spec.loader.exec_module(builder)
    builder.GALLERY_DIR = staging
    builder.COLORSETS = (("colorset1", "cs1"),)
    builder.build(jobs=args.jobs)
    generated = json.loads((staging / "gallery.json").read_text(encoding="utf-8"))
    new_patterns = {p["id"]: p for p in generated["patterns"]}
    expected = {p["id"] for p in original["patterns"] if p["colorset"] == "colorset1"}
    if set(new_patterns) != expected or generated["families"] != original["families"]:
        raise ValueError("Regeneration changed the stable pattern or family contract.")
    for part, suffix in (("source", "*.mmd"), ("svg", "*.svg")):
        for path in sorted((staging / part / "colorset1").glob(suffix)):
            destination = GALLERY / path.relative_to(staging)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
    for path in staging.glob("reports/colorset1-*.json"):
        # Report paths refer to the published fixture, not disposable staging.
        content = path.read_text(encoding="utf-8").replace(str(staging), str(GALLERY))
        content = content.replace(str(staging).replace("\\", "\\\\"), str(GALLERY).replace("\\", "\\\\"))
        (GALLERY / "reports" / path.name).write_text(content, encoding="utf-8", newline="\n")
    original["patterns"] = [new_patterns.get(p["id"], p) for p in original["patterns"]]
    write_json(GALLERY / "gallery.json", original)
    report = json.loads((GALLERY / "reports/build-report.json").read_text(encoding="utf-8"))
    report["manifestSha256"] = digest(GALLERY / "gallery.json")
    report.pop("recovery", None)
    write_json(GALLERY / "reports/build-report.json", report)
    after = cs2_snapshot()
    if before != after or [p for p in original["patterns"] if p["colorset"] == "colorset2"] != original_cs2_patterns:
        raise RuntimeError("CS2 changed during a CS1-only build.")
    proof = {
        "ok": True,
        "rebuiltCs1Patterns": len(new_patterns),
        "preservedCs2Resources": len(before),
        "cs2Sha256Before": before,
        "cs2Sha256After": after,
        "manifestSha256": digest(GALLERY / "gallery.json"),
    }
    write_json(ARTIFACTS / "manifests/mermaid-cs1-rebuild.json", proof)
    print(json.dumps({k: v for k, v in proof.items() if not k.startswith("cs2Sha")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
