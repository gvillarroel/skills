#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Stage one immutable runtime-profile copy of the consolidated D3 skill."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys


RUNTIME_TOP_LEVEL = ("SKILL.md", "agents", "references", "scripts", "assets")
EXCLUDED_DIRECTORY_NAMES = {"examples", "node_modules", "__pycache__", ".pytest_cache", ".git"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def selected_files(source: Path) -> list[Path]:
    files: list[Path] = []
    for name in RUNTIME_TOP_LEVEL:
        candidate = source / name
        if candidate.is_file():
            files.append(candidate)
            continue
        if not candidate.is_dir():
            continue
        for path in candidate.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(source)
            if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative.parts):
                continue
            if path.suffix.casefold() in EXCLUDED_SUFFIXES:
                continue
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(source).as_posix())


def digest_mapping(source: Path, files: list[Path]) -> tuple[str, int]:
    digest = hashlib.sha256()
    byte_count = 0
    for path in files:
        relative = path.relative_to(source).as_posix()
        payload = path.read_bytes()
        byte_count += len(payload)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(payload)).encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest(), byte_count


def parse_skill_name(skill_file: Path) -> str:
    text = skill_file.read_text(encoding="utf-8")
    match = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", text)
    if not match:
        raise ValueError(f"Unable to read skill name from {skill_file}")
    return match.group(1)


def stage(source: Path, output: Path, manifest_path: Path) -> dict[str, object]:
    source = source.resolve()
    output = output.resolve()
    manifest_path = manifest_path.resolve()
    if not (source / "SKILL.md").is_file():
        raise FileNotFoundError(f"Source skill is missing SKILL.md: {source}")
    skill_name = parse_skill_name(source / "SKILL.md")
    if source.name != skill_name:
        raise ValueError(f"Source directory {source.name!r} does not match skill name {skill_name!r}")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing non-empty output directory: {output}")
    if manifest_path.exists():
        raise FileExistsError(f"Refusing existing manifest: {manifest_path}")

    files = selected_files(source)
    if source / "SKILL.md" not in files:
        raise ValueError("Runtime payload selection omitted SKILL.md")
    source_digest, source_bytes = digest_mapping(source, files)
    output.mkdir(parents=True, exist_ok=True)
    for path in files:
        destination = output / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)

    copied = selected_files(output)
    output_digest, output_bytes = digest_mapping(output, copied)
    if source_digest != output_digest or source_bytes != output_bytes or len(files) != len(copied):
        raise RuntimeError("Staged runtime payload differs from selected source bytes")
    forbidden = [
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if any(part in EXCLUDED_DIRECTORY_NAMES for part in path.relative_to(output).parts)
    ]
    if forbidden:
        raise RuntimeError(f"Excluded paths leaked into runtime payload: {forbidden[:5]}")

    manifest = {
        "schemaVersion": 1,
        "skillName": skill_name,
        "source": str(source),
        "output": str(output),
        "sha256": output_digest,
        "fileCount": len(copied),
        "byteCount": output_bytes,
        "profile": "runtime",
        "includedTopLevel": list(RUNTIME_TOP_LEVEL),
        "excludedDirectoryNames": sorted(EXCLUDED_DIRECTORY_NAMES),
        "sourceUnchanged": digest_mapping(source, selected_files(source))[0] == source_digest,
    }
    if not manifest["sourceUnchanged"]:
        raise RuntimeError("Source skill changed while staging runtime payload")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--manifest", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    manifest = args.manifest or output.with_name(f"{output.name}-runtime-manifest.json")
    print(json.dumps(stage(args.source, output, manifest), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
