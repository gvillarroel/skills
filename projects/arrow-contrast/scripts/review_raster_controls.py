#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Check the native raster-only Ditaa arrow without restyling its source."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]


def main():
    rows = []
    for gallery in ("plantuml-colorset-renderer", "plantuml-colorset-renderer-cs1"):
        path = ROOT / "skills/plantuml-colorset-renderer/assets/examples" / gallery / "png/ditaa.png"
        image = Image.open(path).convert("RGBA")
        ink = [(170, 49), (195, 49), (213, 47), (213, 49), (213, 51)]
        backing = [(170, 44), (213, 40)]
        samples = [{"role": role, "xy": xy, "rgba": list(image.getpixel(xy))}
                   for role, points in (("shaft/head", ink), ("backing", backing)) for xy in points]
        passed = all(image.getpixel(xy) == (0, 0, 0, 255) for xy in ink) and all(image.getpixel(xy) == (255, 255, 255, 255) for xy in backing)
        rows.append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                     "size": list(image.size), "samples": samples, "contrast": 21 if passed else None, "passed": passed})
    report = {"date": "2026-10-03", "passed": all(row["passed"] for row in rows), "states": rows,
              "scope": "Two unchanged native raster-only Ditaa fixtures: opaque black shaft/head interior samples on white. The source arrow and its clear arrival gutter were manually inspected; ordinary unheaded dependencies are not reclassified as arrows. This finite control does not certify arbitrary imported raster artwork."}
    (ROOT / "evaluations/arrow-contrast/ditaa-raster-review-20261003.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "states": len(rows), "minimumContrast": min(row["contrast"] or 0 for row in rows)}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
