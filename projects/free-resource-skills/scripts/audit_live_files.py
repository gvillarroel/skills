#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Independently verify live files, model dependencies and decoded previews."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree
from PIL import Image


def sha256(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def main():
    root = Path("projects/free-resource-skills/artifacts")
    checks = []
    for receipt_path in sorted((root / "downloads/utf8-check").glob("*.*.json")):
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        file = Path(str(receipt_path)[:-5])
        assert receipt["file"]["sha256"] == sha256(file)
        assert receipt["file"]["bytes"] == file.stat().st_size
        record = {"file": file.as_posix(), "provider": receipt["provider"], "id": receipt["asset_id"],
                  "variant": receipt["variant"], "sha256": sha256(file)}
        if file.suffix == ".jpg":
            with Image.open(file) as image:
                image.load()
                record["dimensions"] = list(image.size)
        elif file.suffix == ".svg":
            assert ElementTree.parse(file).getroot().tag.endswith("svg")
        elif file.suffix == ".zip":
            with zipfile.ZipFile(file) as archive:
                assert archive.testzip() is None
                record["members"] = len(archive.infolist())
                if receipt["provider"] == "ambientCG":
                    maps = [n for n in archive.namelist() if n.lower().endswith((".jpg", ".png"))]
                    for member in maps:
                        with Image.open(io.BytesIO(archive.read(member))) as image: image.load()
                    record["decoded_maps"] = len(maps)
        checks.append(record)
    bundle = root / "downloads/deck-gltf-bundle"
    gltf = json.loads((bundle / "wood_floor_deck_1k.gltf").read_text(encoding="utf-8"))
    dependencies = []
    for kind in ("buffers", "images"):
        for item in gltf[kind]:
            uri = item["uri"]
            file = (bundle / uri).resolve()
            assert file.is_relative_to(bundle.resolve()) and file.is_file()
            if kind == "buffers": assert file.stat().st_size == item["byteLength"]
            else:
                with Image.open(file) as image: image.load()
            dependencies.append({"uri": uri, "sha256": sha256(file), "bytes": file.stat().st_size})
    receipt = json.loads((bundle / "receipt.json").read_text(encoding="utf-8"))
    for row in receipt["files"]:
        file = bundle / row["path"]
        assert sha256(file) == row["sha256"]
    previews = []
    for file in sorted((root / "images").rglob("*.png")):
        with Image.open(file) as image:
            image.load()
            previews.append({"file": file.as_posix(), "dimensions": list(image.size)})
    report = {"passed": True, "download_checks": checks, "gltf_dependencies": dependencies,
              "gltf_scope": "Buffer lengths, URI resolution and texture decoding; not a 3D application import test.",
              "decoded_previews": previews}
    output = root / "reviews/live-files-audit.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "downloads": len(checks), "gltf_dependencies": len(dependencies),
                      "decoded_previews": len(previews), "report": output.as_posix()}))


if __name__ == "__main__": main()
