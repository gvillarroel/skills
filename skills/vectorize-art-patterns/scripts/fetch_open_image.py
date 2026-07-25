#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0",
# ]
# ///
"""Download an openly licensed image and record machine-checkable provenance."""

from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
from io import BytesIO
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from PIL import Image


USER_AGENT = "vectorize-art-patterns/1.0 (open-image provenance fetcher)"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
AIC_API = "https://api.artic.edu/api/v1/artworks"
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
ASSET_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REJECTED_LICENSE_MARKERS = (
    "all rights reserved",
    "copyrighted",
    "editorial",
    "fair use",
    "noncommercial",
    "non-commercial",
    "no derivatives",
    "no-derivatives",
    "by-nd",
    "by-nc",
)


class FetchError(RuntimeError):
    """Raised when an image cannot be safely acquired."""


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        style = dict(attrs).get("style", "") or ""
        if self.hidden_depth or "display: none" in style.lower():
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth:
            self.parts.append(data)


def clean_html(value: Any) -> str:
    if value is None:
        return ""
    parser = _TextExtractor()
    parser.feed(str(value))
    text = html.unescape(" ".join(parser.parts))
    return re.sub(r"\s+", " ", text).strip()


def utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def request_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    target = url
    if params:
        target = f"{url}?{urlencode(params)}"
    request = Request(
        target,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    for attempt in range(4):
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code in {429, 502, 503, 504} and attempt < 3:
                retry_after = exc.headers.get("Retry-After", "")
                delay = float(retry_after) if retry_after.isdigit() else 1.5 * 2**attempt
                time.sleep(min(10.0, delay))
                continue
            raise FetchError(f"Metadata request failed for {target}: {exc}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise FetchError(f"Metadata request failed for {target}: {exc}") from exc
    raise FetchError(f"Metadata request exhausted retries for {target}")


def download(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "image/avif,image/webp,image/png,image/jpeg,*/*;q=0.5",
        },
    )
    for attempt in range(4):
        try:
            with urlopen(request, timeout=60) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code in {429, 502, 503, 504} and attempt < 3:
                retry_after = exc.headers.get("Retry-After", "")
                delay = float(retry_after) if retry_after.isdigit() else 1.5 * 2**attempt
                time.sleep(min(10.0, delay))
                continue
            raise FetchError(f"Image download failed for {url}: {exc}") from exc
        except (URLError, TimeoutError) as exc:
            raise FetchError(f"Image download failed for {url}: {exc}") from exc
    raise FetchError(f"Image download exhausted retries for {url}")


def canonical_license(
    short_name: str, license_url: str, usage_terms: str
) -> dict[str, Any]:
    evidence = " ".join((short_name, license_url, usage_terms)).lower()
    if any(marker in evidence for marker in REJECTED_LICENSE_MARKERS):
        raise FetchError(
            f"License does not allow unrestricted derivative work: {short_name or usage_terms}"
        )

    if "creativecommons.org/publicdomain/zero/" in evidence or re.search(
        r"\bcc[\s-]?0\b", evidence
    ):
        return {
            "license": "CC0-1.0",
            "license_url": license_url
            or "https://creativecommons.org/publicdomain/zero/1.0/",
            "attribution_required": False,
            "share_alike": False,
        }

    if (
        "public domain" in evidence
        or "publicdomain/mark/" in evidence
        or short_name.strip().lower() in {"pdm", "pd"}
    ):
        return {
            "license": "Public-Domain",
            "license_url": license_url
            or "https://creativecommons.org/publicdomain/mark/1.0/",
            "attribution_required": False,
            "share_alike": False,
        }

    by_sa_match = re.search(
        r"(?:cc[\s-]*by[\s-]*sa|licenses/by-sa/)(\d(?:\.\d)?)?", evidence
    )
    if by_sa_match:
        version = by_sa_match.group(1) or "4.0"
        return {
            "license": f"CC-BY-SA-{version}",
            "license_url": license_url
            or f"https://creativecommons.org/licenses/by-sa/{version}/",
            "attribution_required": True,
            "share_alike": True,
        }

    by_match = re.search(
        r"(?:cc[\s-]*by|licenses/by/)(?![\s-]*(?:nc|nd|sa))(\d(?:\.\d)?)?",
        evidence,
    )
    if by_match:
        version = by_match.group(1) or "4.0"
        return {
            "license": f"CC-BY-{version}",
            "license_url": license_url
            or f"https://creativecommons.org/licenses/by/{version}/",
            "attribution_required": True,
            "share_alike": False,
        }

    raise FetchError(
        "License is missing or outside the derivative-safe allowlist "
        f"(Public Domain, CC0, CC BY, CC BY-SA): {short_name or usage_terms or 'unknown'}"
    )


def ext_value(metadata: dict[str, Any], key: str) -> str:
    item = metadata.get(key, {})
    if isinstance(item, dict):
        return clean_html(item.get("value"))
    return clean_html(item)


def fetch_commons(title: str, max_width: int) -> dict[str, Any]:
    normalized_title = title if title.lower().startswith("file:") else f"File:{title}"
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "imageinfo",
        "titles": normalized_title,
        "iiprop": "url|extmetadata|sha1|mime|size",
        "iiurlwidth": str(max_width),
        "iiextmetadatalanguage": "en",
        "iiextmetadatafilter": (
            "LicenseShortName|LicenseUrl|UsageTerms|Artist|Credit|"
            "ImageDescription|DateTimeOriginal|Restrictions"
        ),
    }
    payload = request_json(COMMONS_API, params)
    pages = payload.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        raise FetchError(f"Wikimedia Commons file not found: {normalized_title}")
    page = pages[0]
    info_items = page.get("imageinfo", [])
    if not info_items:
        raise FetchError(f"No image metadata returned for {normalized_title}")
    info = info_items[0]
    metadata = info.get("extmetadata", {})
    restrictions = ext_value(metadata, "Restrictions")
    if restrictions:
        raise FetchError(
            f"The Commons record declares additional restrictions: {restrictions}"
        )

    short_name = ext_value(metadata, "LicenseShortName")
    license_url = ext_value(metadata, "LicenseUrl")
    usage_terms = ext_value(metadata, "UsageTerms")
    license_record = canonical_license(short_name, license_url, usage_terms)
    mime = str(info.get("thumbmime") or info.get("mime") or "")
    if mime not in ALLOWED_MIME:
        raise FetchError(f"Unsupported image MIME type: {mime or 'unknown'}")

    canonical_title = str(page.get("title") or normalized_title)
    source_page = "https://commons.wikimedia.org/wiki/" + quote(
        canonical_title.replace(" ", "_"), safe=":(),_-"
    )
    metadata_api_url = f"{COMMONS_API}?{urlencode(params)}"
    return {
        "provider": "wikimedia-commons",
        "provider_id": canonical_title,
        "title": ext_value(metadata, "ImageDescription")
        or canonical_title.removeprefix("File:"),
        "creator": ext_value(metadata, "Artist") or "Unknown",
        "date": ext_value(metadata, "DateTimeOriginal"),
        "source_page": source_page,
        "metadata_api_url": metadata_api_url,
        "original_url": str(info.get("url") or ""),
        "download_url": str(info.get("thumburl") or info.get("url") or ""),
        "source_file_sha1": str(info.get("sha1") or ""),
        "usage_terms": usage_terms or short_name,
        "credit": ext_value(metadata, "Credit"),
        "restrictions": restrictions,
        "mime": mime,
        **license_record,
    }


def fetch_artic(object_id: int, max_width: int) -> dict[str, Any]:
    fields = ",".join(
        (
            "id",
            "title",
            "artist_display",
            "date_display",
            "image_id",
            "is_public_domain",
            "copyright_notice",
            "api_link",
            "credit_line",
        )
    )
    metadata_api_url = f"{AIC_API}/{object_id}?{urlencode({'fields': fields})}"
    payload = request_json(f"{AIC_API}/{object_id}", {"fields": fields})
    data = payload.get("data", {})
    if not data:
        raise FetchError(f"Art Institute artwork not found: {object_id}")
    if data.get("is_public_domain") is not True:
        notice = clean_html(data.get("copyright_notice")) or "not marked public domain"
        raise FetchError(
            f"Art Institute artwork {object_id} is not Open Access: {notice}"
        )
    image_id = str(data.get("image_id") or "")
    if not image_id:
        raise FetchError(f"Art Institute artwork {object_id} has no public image")
    iiif_base = str(payload.get("config", {}).get("iiif_url") or "").rstrip("/")
    if not iiif_base.startswith("https://"):
        raise FetchError("Art Institute API did not return a secure IIIF endpoint")
    download_url = f"{iiif_base}/{image_id}/full/{max_width},/0/default.jpg"
    return {
        "provider": "art-institute-chicago",
        "provider_id": str(object_id),
        "title": clean_html(data.get("title")) or f"Artwork {object_id}",
        "creator": clean_html(data.get("artist_display")) or "Unknown",
        "date": clean_html(data.get("date_display")),
        "source_page": f"https://www.artic.edu/artworks/{object_id}",
        "metadata_api_url": metadata_api_url,
        "original_url": f"{iiif_base}/{image_id}/full/full/0/default.jpg",
        "download_url": download_url,
        "source_file_sha1": "",
        "usage_terms": "Art Institute of Chicago Open Access, CC0",
        "credit": clean_html(data.get("credit_line")),
        "restrictions": "",
        "mime": "image/jpeg",
        "license": "CC0-1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution_required": False,
        "share_alike": False,
    }


def verify_image(data: bytes, expected_mime: str) -> dict[str, Any]:
    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
        with Image.open(BytesIO(data)) as image:
            width, height = image.size
            detected_format = str(image.format or "").upper()
    except Exception as exc:
        raise FetchError(f"Downloaded bytes are not a valid raster image: {exc}") from exc
    if width <= 0 or height <= 0 or width * height > 100_000_000:
        raise FetchError(f"Unsafe image dimensions: {width}x{height}")
    format_to_mime = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp",
    }
    detected_mime = format_to_mime.get(detected_format, "")
    if detected_mime not in ALLOWED_MIME:
        raise FetchError(f"Unsupported decoded image format: {detected_format}")
    if expected_mime and detected_mime != expected_mime:
        raise FetchError(
            f"Metadata MIME {expected_mime} does not match decoded {detected_mime}"
        )
    return {
        "width": width,
        "height": height,
        "mime": detected_mime,
    }


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": 1,
            "policy": {
                "allowed_licenses": [
                    "Public-Domain",
                    "CC0-1.0",
                    "CC-BY-*",
                    "CC-BY-SA-*",
                ],
                "generated_by": "scripts/fetch_open_image.py",
            },
            "assets": [],
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FetchError(f"Cannot read manifest {path}: {exc}") from exc
    if payload.get("schema_version") != 1 or not isinstance(
        payload.get("assets"), list
    ):
        raise FetchError(f"Unsupported or malformed asset manifest: {path}")
    return payload


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )
    atomic_write_bytes(path, encoded)


def store_asset(
    *,
    asset_id: str,
    output: Path,
    manifest_path: Path,
    metadata: dict[str, Any],
    replace: bool,
) -> dict[str, Any]:
    if not ASSET_ID_RE.fullmatch(asset_id):
        raise FetchError("Asset ID must be lowercase hyphen-case")
    manifest_path = manifest_path.resolve()
    output = output.resolve()
    manifest_dir = manifest_path.parent
    try:
        relative_output = output.relative_to(manifest_dir)
    except ValueError as exc:
        raise FetchError(
            "Downloaded assets must be stored inside the manifest directory"
        ) from exc

    data = download(metadata["download_url"])
    decoded = verify_image(data, metadata["mime"])
    digest = sha256_bytes(data)
    manifest = load_manifest(manifest_path)
    assets = manifest["assets"]
    existing = next((item for item in assets if item.get("id") == asset_id), None)
    if existing:
        if (
            existing.get("sha256") == digest
            and existing.get("source_page") == metadata["source_page"]
        ):
            retrieved_at = existing.get("retrieved_at") or utc_now()
        elif not replace:
            raise FetchError(
                f"Asset ID {asset_id} already exists with different source or bytes; "
                "pass --replace only after reviewing the new license evidence"
            )
        else:
            retrieved_at = utc_now()
    else:
        retrieved_at = utc_now()

    attribution = metadata["creator"]
    if metadata.get("credit"):
        attribution = f"{metadata['creator']}; {metadata['credit']}"
    entry = {
        "id": asset_id,
        "filename": relative_output.as_posix(),
        "provider": metadata["provider"],
        "provider_id": metadata["provider_id"],
        "title": metadata["title"],
        "creator": metadata["creator"],
        "date": metadata["date"],
        "source_page": metadata["source_page"],
        "metadata_api_url": metadata["metadata_api_url"],
        "original_url": metadata["original_url"],
        "download_url": metadata["download_url"],
        "retrieved_at": retrieved_at,
        "license": metadata["license"],
        "license_url": metadata["license_url"],
        "usage_terms": metadata["usage_terms"],
        "attribution_required": metadata["attribution_required"],
        "share_alike": metadata["share_alike"],
        "attribution": attribution,
        "restrictions": metadata["restrictions"],
        "transformation_allowed": True,
        "mime": decoded["mime"],
        "width": decoded["width"],
        "height": decoded["height"],
        "bytes": len(data),
        "sha256": digest,
        "source_file_sha1": metadata["source_file_sha1"],
    }

    atomic_write_bytes(output, data)
    manifest["assets"] = sorted(
        [item for item in assets if item.get("id") != asset_id] + [entry],
        key=lambda item: item["id"],
    )
    atomic_write_json(manifest_path, manifest)
    return entry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Download one derivative-safe open image and update a provenance manifest."
        )
    )
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--max-width", type=int, default=900)
    parser.add_argument("--replace", action="store_true")
    subparsers = parser.add_subparsers(dest="provider", required=True)

    commons = subparsers.add_parser("commons", help="Fetch from Wikimedia Commons")
    commons.add_argument("--title", required=True)

    artic = subparsers.add_parser(
        "artic", help="Fetch a public-domain Art Institute of Chicago image"
    )
    artic.add_argument("--object-id", required=True, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    if not 200 <= args.max_width <= 2400:
        raise FetchError("--max-width must be between 200 and 2400")
    if args.provider == "commons":
        metadata = fetch_commons(args.title, args.max_width)
    else:
        metadata = fetch_artic(args.object_id, args.max_width)
    entry = store_asset(
        asset_id=args.asset_id,
        output=args.output,
        manifest_path=args.manifest,
        metadata=metadata,
        replace=args.replace,
    )
    print(json.dumps({"ok": True, "asset": entry}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FetchError as exc:
        print(f"[vectorize-art-patterns] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
