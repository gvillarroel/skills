#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Download pinned catalog source archives into a caller-owned audit directory."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
import tarfile
import urllib.request
import urllib.error
import zipfile
from pathlib import Path, PurePosixPath


SOURCES = {
    "aws-archive": ("DataDog/pathfinding.cloud", "a81659da620b83399f98025f8de001816d9adec6"),
    "aws": ("awslabs/aws-icons-for-plantuml", "50efda948226ff4e06937596201528b707ef3ef9"),
    "gcp": ("davidholsgrove/gcp-icons-for-plantuml", "f103741ffdca5793142103d7f5206814be92a405"),
    "devicon": ("devicons/devicon", "7330accdbc47e2dc0c19789a48533c4a3c50fe58"),
    "lobe-icons": ("lobehub/lobe-icons", "32f4083f7a20b67ecdc7b29c0af031ada5a29c52"),
    "simpleicons": ("simple-icons/simple-icons", "0f9fa549da00e9aa6e3ef8d3d2171f481360e638"),
}

ZIP_SOURCES = {
    "aws-official": "https://d1.awsstatic.com/onedam/marketing-channels/website/public/shared/architecture-icon-release/Icon-package_07312026.5846e92413caa21490223536cc97f1269e44fa92.zip",
    "gcp-legacy": "https://services.google.com/fh/files/misc/google-cloud-legacy-icons.zip",
}

FILES = {
    "opencode-fixed": "https://raw.githubusercontent.com/anomalyco/opencode/cf7503687a2485621a690d18c4b0d1ff2060bc3e/packages/ui/src/assets/favicon/favicon-v3.svg",
}

AWS_ARCHIVE_PROBES = [
    "https://d1.awsstatic.com/onedam/marketing-channels/website/public/shared/architecture-icon-release/Asset-Package_01302026.zip",
    "https://d1.awsstatic.com/onedam/marketing-channels/website/public/shared/architecture-icon-release/Icon-package_01302026.zip",
    "https://d1.awsstatic.com/webteam/architecture-icons/q1-2026/Asset-Package_01302026.zip",
    "https://d1.awsstatic.com/webteam/architecture-icons/Asset-Package_01302026.zip",
    "https://d1.awsstatic.com/webteam/architecture-icons/q3-2025/Asset-Package_07312025.zip",
]


def fetch_file(name: str, root: Path) -> dict:
    url = FILES[name]
    target = root / name / url.rsplit("/", 1)[1]
    if not target.is_file():
        request = urllib.request.Request(url, headers={"User-Agent": "vector-logo-audit"})
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    return {"name": name, "url": url, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "files": 1}


def fetch_zip(name: str, root: Path) -> dict:
    url = ZIP_SOURCES[name]
    archive = root / f"{name}.zip"
    root.mkdir(parents=True, exist_ok=True)
    if not archive.is_file():
        request = urllib.request.Request(url, headers={"User-Agent": "vector-logo-audit"})
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read()
        archive.write_bytes(payload)
    payload = archive.read_bytes()
    destination = (root / name).resolve()
    extracted = 0
    with zipfile.ZipFile(io.BytesIO(payload)) as bundle:
        for member in bundle.infolist():
            relative = PurePosixPath(member.filename)
            if relative.is_absolute() or ".." in relative.parts or "\\" in member.filename:
                raise ValueError(f"Unsafe archive path: {member.filename}")
            if relative.suffix.lower() not in {".svg", ".md", ".txt", ".json", ".pdf"} or "__MACOSX" in relative.parts:
                continue
            target = destination.joinpath(*relative.parts).resolve()
            if not target.is_relative_to(destination):
                raise ValueError(f"Unsafe archive destination: {member.filename}")
            content = bundle.read(member)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.is_file() or target.read_bytes() != content:
                target.write_bytes(content)
            extracted += 1
    return {"name": name, "url": url, "sha256": hashlib.sha256(payload).hexdigest(), "files": extracted}


def fetch(name: str, root: Path) -> dict:
    repository, commit = SOURCES[name]
    url = f"https://codeload.github.com/{repository}/tar.gz/{commit}"
    archive = root / f"{name}-{commit}.tar.gz"
    root.mkdir(parents=True, exist_ok=True)
    if not archive.is_file():
        request = urllib.request.Request(url, headers={"User-Agent": "vector-logo-audit"})
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read()
        archive.write_bytes(payload)
    payload = archive.read_bytes()
    destination = (root / name).resolve()
    extracted = 0
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as bundle:
        for member in bundle:
            if not member.isfile():
                continue
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"Unsafe archive path: {member.name}")
            relative = PurePosixPath(*relative.parts[1:])
            if not relative.parts:
                continue
            if relative.suffix.lower() not in {".svg", ".json", ".yml", ".yaml", ".md", ".txt", ".tsx"} and not relative.name.startswith("LICENSE"):
                continue
            target = destination.joinpath(*relative.parts).resolve()
            if not target.is_relative_to(destination):
                raise ValueError(f"Unsafe archive destination: {member.name}")
            data = bundle.extractfile(member)
            assert data is not None
            target.parent.mkdir(parents=True, exist_ok=True)
            content = data.read()
            if not target.is_file() or target.read_bytes() != content:
                target.write_bytes(content)
            extracted += 1
    return {"name": name, "url": url, "sha256": hashlib.sha256(payload).hexdigest(), "files": extracted}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", action="append", choices=sorted(SOURCES | ZIP_SOURCES | FILES))
    parser.add_argument("--probe-aws-archives", action="store_true")
    args = parser.parse_args()
    root = args.output.resolve()
    if args.probe_aws_archives:
        for url in AWS_ARCHIVE_PROBES:
            try:
                with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=15) as response:
                    print(json.dumps({"url": url, "status": response.status}), flush=True)
            except (urllib.error.URLError, TimeoutError) as error:
                print(json.dumps({"url": url, "error": str(error)}), flush=True)
        return 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fetch_file if name in FILES else fetch_zip if name in ZIP_SOURCES else fetch, name, root): name for name in (args.source or (SOURCES | ZIP_SOURCES | FILES))}
        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(json.dumps(result), flush=True)
            results.append(result)
    record = root / "downloads.json"
    prior = {item["name"]: item for item in json.loads(record.read_text(encoding="utf-8"))} if record.is_file() else {}
    prior.update({item["name"]: item for item in results})
    record.write_text(json.dumps(sorted(prior.values(), key=lambda row: row["name"]), indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
