#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Prove that only CS1 allocation order changed across every palette copy."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = "0d4ff8be7b03d18e0a4e44dee5285ed6c3bff19b"
EXPECTED = ["#9e1b32", "#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c", "#b5b5b5", "#cfcfcf", "#e7e7e7", "#363636", "#f7f7f7", "#1c1c1c", "#000000", "#ffffff", "#6d1222", "#e8002a", "#ffccd5"]
GROUPS = ["primary-red", "grays", "black", "white", "remaining-colors"]


def main() -> int:
    findings, rows = [], []
    for path in [ROOT / "docs/colorsets.json", *sorted((ROOT / "skills").glob("*/assets/palettes/colorsets.json"))]:
        relative = path.relative_to(ROOT).as_posix()
        original_bytes = subprocess.run(["git", "show", f"{BASE}:{relative}"], cwd=ROOT, check=True, capture_output=True).stdout
        original = json.loads(original_bytes)
        current = json.loads(path.read_text(encoding="utf-8"))
        expected = json.loads(original_bytes)
        expected["colorsets"]["colorset1"].update(sequence=EXPECTED, solidSequence=EXPECTED, categoryPriority=GROUPS)
        if current != expected:
            findings.append(relative)
        encoded_cs2 = json.dumps(current["colorsets"]["colorset2"], sort_keys=True).encode()
        rows.append({"path": relative, "allowedTokensUnchanged": current["colorsets"]["colorset1"]["allowed"] == original["colorsets"]["colorset1"]["allowed"], "cs2Unchanged": current["colorsets"]["colorset2"] == original["colorsets"]["colorset2"], "cs2Sha256": hashlib.sha256(encoded_cs2).hexdigest()})
    result = {"ok": not findings, "baseline": BASE, "paletteCount": len(rows), "findings": findings, "palettes": rows}
    output = ROOT / "projects/colorset-priority/artifacts/manifests/palette-scope.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k != "palettes"}, indent=2))
    return bool(findings)


if __name__ == "__main__":
    raise SystemExit(main())
