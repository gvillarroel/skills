#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["rapidocr", "onnxruntime", "pillow", "numpy"]
# ///
"""Measure text-density proxies; OCR is not an inventory of historical claims."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image
from rapidocr import RapidOCR


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    engine = RapidOCR(params={
        "Global.model_root_dir": str((args.output / "models").resolve()),
        "Global.log_level": "warning",
        "Global.max_side_len": 3200,
        "Det.limit_side_len": 1600,
        "Det.max_candidates": 5000,
        "EngineConfig.onnxruntime.intra_op_num_threads": 4,
        "EngineConfig.onnxruntime.inter_op_num_threads": 2,
    })
    records = []
    for path in args.image:
        original = Image.open(path).convert("RGB")
        width, height = original.size
        # Apply the same displayed width to both sources. This cannot restore
        # detail absent from a low-resolution reference and is not a fact census.
        normalized = original.resize((1600, round(height * 1600 / width)))
        lines = []
        for row in range(3):
            for column in range(2):
                x0 = max(0, round(column*normalized.width/2)-40)
                y0 = max(0, round(row*normalized.height/3)-40)
                x1 = min(normalized.width, round((column+1)*normalized.width/2)+40)
                y1 = min(normalized.height, round((row+1)*normalized.height/3)+40)
                crop = normalized.crop((x0,y0,x1,y1)).resize(((x1-x0)*2,(y1-y0)*2))
                result = engine(np.asarray(crop))
                if result.boxes is None:
                    continue
                for box, text, score in zip(result.boxes, result.txts, result.scores):
                    xs = [(x0+float(p[0])/2)/normalized.width for p in box]
                    ys = [(y0+float(p[1])/2)/normalized.height for p in box]
                    item = {"text": text, "score": float(score),
                            "box": [min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys)]}
                    duplicate = None
                    ax,ay,aw,ah = item["box"]
                    for previous in lines:
                        bx,by,bw,bh = previous["box"]
                        overlap = max(0,min(ax+aw,bx+bw)-max(ax,bx))*max(0,min(ay+ah,by+bh)-max(ay,by))
                        if overlap/max(min(aw*ah,bw*bh),1e-12) > .7:
                            duplicate = previous
                            break
                    if duplicate is None:
                        lines.append(item)
                    elif item["score"] > duplicate["score"]:
                        duplicate.update(item)
        body = [item for item in lines if .045 <= item["box"][1] < .985]
        bands = []
        for index in range(3):
            subset = [item for item in body
                      if int(min(2, (item["box"][1]-.045)/.94*3)) == index]
            bands.append({"band": index, "lines": len(subset),
                          "characters": sum(len(re.sub(r"\s", "", item["text"])) for item in subset)})
        record = {
            "id": path.stem, "path": str(path.resolve()),
            "image_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "source_size": [width, height], "normalized_width": 1600,
            "ocr_version": importlib.metadata.version("rapidocr"),
            "ocr_protocol": "2 columns x 3 rows, 40-pixel overlap, 2x recognition scale, overlap deduplication",
            "body_bounds": [0, .045, 1, .94],
            "ocr_line_count": len(body),
            "ocr_character_count": sum(len(re.sub(r"\s", "", item["text"])) for item in body),
            "text_box_area_fraction": sum(item["box"][2]*item["box"][3] for item in body)/.94,
            "bands": bands,
            "limitations": "OCR screening only; errors, missed tiny labels, logos and map text require manual review. Counts are not knowledge claims.",
        }
        (args.output / f"{path.stem}-ocr.json").write_text(
            json.dumps({"summary": record, "lines": lines}, indent=2)+"\n", encoding="utf-8")
        records.append(record)
        print(json.dumps(record), flush=True)
    (args.output / "summary.json").write_text(json.dumps(records, indent=2)+"\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
