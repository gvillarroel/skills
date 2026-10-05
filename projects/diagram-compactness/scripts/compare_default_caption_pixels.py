#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11"]
# ///
"""Compare immutable authored/default and disabled native caption screenshots."""
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
output = ROOT / "projects/diagram-compactness/artifacts/reviews/caption-default-diagnosis"
output.mkdir(parents=True, exist_ok=True)
report = {"runs": [], "originalsUnchanged": True}
for case, bounds in [(2, (495, 413, 671, 493)), (3, (495, 468, 671, 548))]:
    run = f"compact-slidev-echarts-20261004-sol-first-probe-final-natural-{case}"
    workspace = ROOT / "evaluations/runs" / run / "workspace"
    independent = ROOT / "projects/diagram-compactness/artifacts/reviews" / run / "independent-deck"
    sources = {
        "default-resized": workspace / "deliverables/independent-default-capture/resized.png",
        "default-reduced": workspace / "deliverables/independent-default-capture/reduced.png",
        "disabled-resized": independent / "resized.png",
        "disabled-reduced": independent / "reduced-motion.png",
    }
    if case == 3:
        sources.update({"authored-resized": workspace / "deliverables/deck-capture/resized.png", "authored-reduced": workspace / "deliverables/deck-capture/reduced.png"})
    row = {"run": run, "captionBounds": bounds, "patches": {}}
    payloads = {}
    for state, path in sources.items():
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as native:
            patch = native.convert("RGB").crop(bounds)
            size = list(native.size)
        payloads[state] = patch.tobytes()
        patch.resize((patch.width * 4, patch.height * 4), Image.Resampling.NEAREST).save(output / f"natural-{case}-{state}-4x.png")
        row["patches"][state] = {"source": path.relative_to(ROOT).as_posix(), "sourceSize": size, "sourceSha256": before, "patchSha256": hashlib.sha256(payloads[state]).hexdigest()}
        report["originalsUnchanged"] &= before == hashlib.sha256(path.read_bytes()).hexdigest()
    pairs = [("default-resized", "default-reduced"), ("disabled-reduced", "default-reduced")]
    if case == 3:
        pairs += [("authored-resized", "authored-reduced"), ("authored-reduced", "default-reduced")]
    row["comparisons"] = [{"states": pair, "pixelIdentical": payloads[pair[0]] == payloads[pair[1]], "differentChannelValues": sum(a != b for a, b in zip(payloads[pair[0]], payloads[pair[1]], strict=True))} for pair in pairs]
    report["runs"].append(row)
target = output / "comparison.json"
target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
