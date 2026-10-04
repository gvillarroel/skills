#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Update canonical and bundled CS1 allocation order without changing paints."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
ORDER = [
    "#9e1b32",
    "#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c",
    "#b5b5b5", "#cfcfcf", "#e7e7e7", "#363636", "#f7f7f7",
    "#1c1c1c", "#000000", "#ffffff",
    "#6d1222", "#e8002a", "#ffccd5",
]
PRIORITY = ["primary-red", "grays", "black", "white", "remaining-colors"]
records = []
paths = [ROOT / "docs/colorsets.json", *sorted((ROOT / "skills").glob("*/assets/palettes/colorsets.json"))]
for path in paths:
    before = path.read_bytes()
    payload = json.loads(before)
    old = json.loads(before)
    row = payload["colorsets"]["colorset1"]
    if set(ORDER) != set(row["allowed"]):
        raise ValueError(f"Unexpected CS1 membership: {path.relative_to(ROOT)}")
    row["sequence"] = ORDER.copy()
    row["solidSequence"] = ORDER.copy()
    row["categoryPriority"] = PRIORITY.copy()
    assert payload["colorsets"]["colorset2"] == old["colorsets"]["colorset2"]
    for key, value in old["colorsets"]["colorset1"].items():
        if key not in {"sequence", "solidSequence", "categoryPriority"}:
            assert row[key] == value, (path, key)
    after = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    path.write_bytes(after)
    records.append({"path": path.relative_to(ROOT).as_posix(), "beforeSha256": hashlib.sha256(before).hexdigest(), "afterSha256": hashlib.sha256(after).hexdigest(), "cs2Unchanged": True, "otherCs1ValuesUnchanged": True})
report = ROOT / "projects/colorset-priority/artifacts/manifests/palette-update.json"
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps({"order": ORDER, "priority": PRIORITY, "count": len(records), "records": records}, indent=2) + "\n", encoding="utf-8")
print(f"Updated canonical CS1 order and {len(records) - 1} self-contained copies; CS2 and named roles are unchanged.")
