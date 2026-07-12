#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the pinned multi-source technical logo manifest from local source clones."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path


SCHEMA_VERSION = 2


@dataclass(frozen=True)
class Source:
    provider: str
    repository: str
    commit: str
    license_id: str
    license_url: str
    attribution: str
    artwork_glob: str


SOURCES = {
    "aws": Source(
        provider="AWS",
        repository="https://github.com/awslabs/aws-icons-for-plantuml",
        commit="50efda948226ff4e06937596201528b707ef3ef9",
        license_id="CC-BY-ND-2.0",
        license_url="https://creativecommons.org/licenses/by-nd/2.0/",
        attribution="Amazon Web Services (AWS); packaged by AWS Icons for PlantUML contributors",
        artwork_glob="dist/**/*.png",
    ),
    "gcp": Source(
        provider="GCP",
        repository="https://github.com/davidholsgrove/gcp-icons-for-plantuml",
        commit="f103741ffdca5793142103d7f5206814be92a405",
        license_id="CC-BY-ND-2.0",
        license_url="https://creativecommons.org/licenses/by-nd/2.0/",
        attribution="Google Cloud; packaged by GCP Icons for PlantUML contributors",
        artwork_glob="dist/**/*.png",
    ),
    "devicon": Source(
        provider="Devicon",
        repository="https://github.com/devicons/devicon",
        commit="7330accdbc47e2dc0c19789a48533c4a3c50fe58",
        license_id="MIT",
        license_url="https://spdx.org/licenses/MIT.html",
        attribution="Devicon contributors; product names and marks remain property of their owners",
        artwork_glob="icons/*/*.svg",
    ),
    "simpleicons": Source(
        provider="Simple Icons",
        repository="https://github.com/simple-icons/simple-icons",
        commit="0f9fa549da00e9aa6e3ef8d3d2171f481360e638",
        license_id="per-icon",
        license_url="https://github.com/simple-icons/simple-icons/blob/develop/DISCLAIMER.md",
        attribution="Simple Icons contributors; consult each icon's declared license and its mark owner",
        artwork_glob="icons/*.svg",
    ),
}

SIMPLE_ICON_ALLOWED_LICENSES = {
    "Apache-2.0": "https://spdx.org/licenses/Apache-2.0.html",
    "BSD-3-Clause": "https://spdx.org/licenses/BSD-3-Clause.html",
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "MIT": "https://spdx.org/licenses/MIT.html",
}


def slugify(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return value or "logo"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def raw_url(source: Source, relative_path: str) -> str:
    repo_path = source.repository.removeprefix("https://github.com/")
    return f"https://raw.githubusercontent.com/{repo_path}/{source.commit}/{relative_path}"


def cloud_entries(key: str, root: Path) -> list[dict[str, str]]:
    source = SOURCES[key]
    candidates = sorted(root.glob(source.artwork_glob))
    seen_hashes: set[str] = set()
    entries: list[dict[str, str]] = []
    for path in candidates:
        digest = sha256(path)
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        relative = path.relative_to(root).as_posix()
        category = path.parent.name
        name = path.stem
        logo_id = f"{key}-{slugify(category)}-{slugify(name)}"
        entries.append(
            {
                "id": logo_id,
                "title": f"{source.provider} {name}",
                "provider": source.provider,
                "category": category,
                "sourceFormat": "png",
                "sourcePath": relative,
                "sourceUrl": raw_url(source, relative),
                "sourceSha256": digest,
                "licenseId": source.license_id,
                "licenseUrl": source.license_url,
                "sourceRepository": source.repository,
                "sourceCommit": source.commit,
                "attribution": source.attribution,
            }
        )
    return entries


def choose_devicon(directory: Path) -> Path | None:
    slug = directory.name
    preferences = [
        f"{slug}-original.svg",
        f"{slug}-plain.svg",
        f"{slug}-line.svg",
        f"{slug}-original-wordmark.svg",
        f"{slug}-plain-wordmark.svg",
        f"{slug}-line-wordmark.svg",
    ]
    for name in preferences:
        path = directory / name
        if path.is_file():
            return path
    return next(iter(sorted(directory.glob("*.svg"))), None)


def devicon_entries(root: Path) -> list[dict[str, str]]:
    source = SOURCES["devicon"]
    entries: list[dict[str, str]] = []
    seen_hashes: set[str] = set()
    for directory in sorted((root / "icons").iterdir()):
        if not directory.is_dir():
            continue
        path = choose_devicon(directory)
        if path is None:
            continue
        digest = sha256(path)
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        relative = path.relative_to(root).as_posix()
        entries.append(
            {
                "id": f"devicon-{slugify(directory.name)}",
                "title": directory.name,
                "provider": source.provider,
                "category": "technology",
                "sourceFormat": "svg",
                "sourcePath": relative,
                "sourceUrl": raw_url(source, relative),
                "sourceSha256": digest,
                "licenseId": source.license_id,
                "licenseUrl": source.license_url,
                "sourceRepository": source.repository,
                "sourceCommit": source.commit,
                "attribution": source.attribution,
            }
        )
    return entries


def simple_icon_slug_map(root: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for line in (root / "slugs.md").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"\| `(.+)` \| `([a-z0-9]+)` \|", line)
        if match:
            mapping[match.group(1)] = match.group(2)
    return mapping


def simple_icon_entries(root: Path) -> list[dict[str, str]]:
    source = SOURCES["simpleicons"]
    data = json.loads((root / "data" / "simple-icons.json").read_text(encoding="utf-8"))
    slugs = simple_icon_slug_map(root)
    entries: list[dict[str, str]] = []
    for item in data:
        license_data = item.get("license") or {}
        license_id = license_data.get("type")
        if license_id not in SIMPLE_ICON_ALLOWED_LICENSES:
            continue
        title = item["title"]
        slug = slugs.get(title)
        if not slug:
            raise ValueError(f"No Simple Icons slug for {title!r}")
        path = root / "icons" / f"{slug}.svg"
        if not path.is_file():
            raise ValueError(f"Missing Simple Icons SVG {path}")
        relative = path.relative_to(root).as_posix()
        entries.append(
            {
                "id": f"simpleicons-{slug}",
                "title": title,
                "provider": source.provider,
                "category": "technology-brand",
                "sourceFormat": "svg",
                "sourcePath": relative,
                "sourceUrl": raw_url(source, relative),
                "sourceSha256": sha256(path),
                "licenseId": license_id,
                "licenseUrl": SIMPLE_ICON_ALLOWED_LICENSES[license_id],
                "sourceRepository": source.repository,
                "sourceCommit": source.commit,
                "attribution": source.attribution,
                "originalSource": item.get("source", ""),
                "guidelines": item.get("guidelines", ""),
            }
        )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aws-source", type=Path, required=True)
    parser.add_argument("--gcp-source", type=Path, required=True)
    parser.add_argument("--devicon-source", type=Path, required=True)
    parser.add_argument("--simpleicons-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    entries = (
        cloud_entries("aws", args.aws_source)
        + cloud_entries("gcp", args.gcp_source)
        + devicon_entries(args.devicon_source)
        + simple_icon_entries(args.simpleicons_source)
    )
    entries.sort(key=lambda item: item["id"])
    ids = [item["id"] for item in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("Generated logo IDs are not unique")
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "normalization": {
            "width": 256,
            "height": 256,
            "viewBox": "0 0 256 256",
            "preserveAspectRatio": "xMidYMid meet",
            "padding": 16,
        },
        "sources": {
            key: {
                "provider": value.provider,
                "repository": value.repository,
                "commit": value.commit,
                "licenseId": value.license_id,
                "licenseUrl": value.license_url,
                "attribution": value.attribution,
            }
            for key, value in SOURCES.items()
        },
        "logoCount": len(entries),
        "logos": entries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    counts = {provider: sum(e["provider"] == provider for e in entries) for provider in ("AWS", "GCP", "Devicon", "Simple Icons")}
    print(f"Wrote {len(entries)} unique logos to {args.output}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
