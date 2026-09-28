#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package the five independent skills and verify every archived source byte."""
import hashlib
import json
import zipfile
from pathlib import Path

NAMES = ["polyhaven-asset-search", "ambientcg-material-search", "pexels-media-search", "iconify-icon-search", "kenney-asset-search"]


def archive(path, files):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for file, name in files: output.write(file, name)
    with zipfile.ZipFile(path) as output:
        assert output.testzip() is None
        for file, name in files: assert output.read(name) == file.read_bytes()
    return {"path": path.as_posix(), "files": len(files), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    output = Path("projects/free-resource-skills/artifacts/archives")
    output.mkdir(parents=True, exist_ok=True)
    all_files, reports = [], []
    for name in NAMES:
        source = Path("skills") / name
        files = [(file, name + "/" + file.relative_to(source).as_posix()) for file in sorted(source.rglob("*"))
                 if file.is_file() and "__pycache__" not in file.parts and file.suffix != ".pyc"]
        assert len(files) == 7
        reports.append(archive(output / (name + ".zip"), files))
        all_files.extend(files)
    reports.append(archive(output / "free-resource-skills.zip", all_files))
    (output / "manifest.json").write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(reports, indent=2))


if __name__ == "__main__": main()
