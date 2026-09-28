#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise source scripts with real metadata and bounded selected downloads."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
ART = ROOT / "projects/free-resource-skills/artifacts"
DATA = ART / "data"
FILES = ART / "downloads" / "utf8-check"
REVIEW = ART / "reviews"


def call(skill, script, *args):
    argv = ["uv", "run", "--script", str(ROOT / "skills" / skill / "scripts" / script), *map(str, args)]
    r = subprocess.run(argv, capture_output=True, text=True, encoding="utf8")
    REVIEW.mkdir(parents=True, exist_ok=True)
    label = skill + "-" + args[0]
    (REVIEW / (label + ".stdout.txt")).write_text(r.stdout, encoding="utf8")
    (REVIEW / (label + ".stderr.txt")).write_text(r.stderr, encoding="utf8")
    if r.returncode:
        print(json.dumps({"command": argv, "exit_code": r.returncode, "error": r.stderr}), flush=True)
        raise SystemExit(r.returncode)
    return json.loads(r.stdout)


def main():
    for skill, script, source, option, variant in [
        ("polyhaven-asset-search", "polyhaven.py", "polyhaven", 2, "Diffuse/1k/jpg"),
        ("ambientcg-material-search", "ambientcg.py", "ambientcg", 2, "1K-JPG/zip"),
        ("iconify-icon-search", "iconify.py", "iconify", 2, None),
        ("kenney-asset-search", "kenney.py", "kenney", 2, None),
    ]:
        asset = call(skill, script, "inspect", "--manifest", DATA / f"{source}-options.json", "--option", option, "--out", DATA / f"{source}-selected.json")
        if variant:
            matches = [v for v in asset["variants"] if v["key"] == variant]
            if len(matches) != 1:
                raise RuntimeError(f"Required validation variant is unavailable for {source}")
            ext = matches[0]["extension"]
        else:
            ext = "svg" if source == "iconify" else "zip"
        args = ["download", "--manifest", DATA / f"{source}-options.json", "--option", option, "--output", FILES / f"{source}-option-2.{ext}", "--max-mib", "40"]
        if variant: args += ["--variant", variant]
        result = call(skill, script, *args)
        print(json.dumps({"provider": source, "asset_id": result["asset_id"], "variant": result["variant"], "bytes": result["file"]["bytes"], "sha256": result["file"]["sha256"]}), flush=True)
    inv = call("kenney-asset-search", "kenney.py", "archive", "--zip", FILES / "kenney-option-2.zip", "--out", DATA / "kenney-members.json")
    member = next(r["path"] for r in inv["members"] if r["path"].lower().endswith(".png"))
    result = call("kenney-asset-search", "kenney.py", "extract", "--zip", FILES / "kenney-option-2.zip", "--member", member, "--output-dir", FILES / "kenney-selected-files")
    print(json.dumps({"extracted": [r["path"] for r in result["files"]]}))


if __name__ == "__main__": main()
