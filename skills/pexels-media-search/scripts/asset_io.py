#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Local selection manifests, bounded HTTP transfers, and verified downloads."""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from http.client import HTTPException
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree


class ResourceError(Exception):
    """A retrieval or selection error suitable for a concise user report."""


def now():
    return datetime.now(timezone.utc).isoformat()


def checked_url(url, hosts):
    p = urlsplit(str(url))
    if p.scheme != "https" or p.hostname not in hosts or p.username or p.password or p.port not in (None, 443):
        raise ResourceError("Unexpected resource origin; inspect the provider's current download contract.")
    return url


class Redirects(HTTPRedirectHandler):
    def __init__(self, hosts):
        self.hosts = hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        checked_url(newurl, self.hosts)
        if req.has_header("Authorization") and urlsplit(newurl).netloc != urlsplit(req.full_url).netloc:
            raise ResourceError("Refusing to forward credentials to another origin.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Client:
    def __init__(self, hosts, name):
        self.hosts = set(hosts)
        self.name = name
        self.opener = build_opener(Redirects(self.hosts))

    def open(self, url, headers=None):
        checked_url(url, self.hosts)
        request = Request(url, headers={"User-Agent": self.name + "/1.0", "Accept-Encoding": "identity", **(headers or {})})
        for attempt in range(3):
            try:
                response = self.opener.open(request, timeout=40)
                checked_url(response.url, self.hosts)
                return response
            except HTTPError as exc:
                status = exc.code
                retry_after = exc.headers.get("Retry-After", "")
                exc.close()
                if attempt == 2 or status not in (429, 500, 502, 503, 504) or (retry_after and (not retry_after.isdigit() or int(retry_after) > 5)):
                    raise ResourceError(f"Provider returned HTTP {status}; no replacement resource was selected.") from exc
                time.sleep(max(2 ** attempt, int(retry_after or 0)))
            except (URLError, TimeoutError) as exc:
                if attempt == 2:
                    raise ResourceError("Network request failed after three attempts.") from exc
                time.sleep(2 ** attempt)

    def data(self, url, params=None, headers=None, text=False):
        if params:
            url += ("&" if "?" in url else "?") + urlencode({k: v for k, v in params.items() if v is not None})
        with self.open(url, headers) as r:
            raw = r.read(16 * 1024 * 1024 + 1)
        if len(raw) > 16 * 1024 * 1024:
            raise ResourceError("Metadata exceeds the 16 MiB limit.")
        try:
            return raw.decode("utf-8") if text else json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise ResourceError("The provider response no longer matches the expected text or JSON contract.") from exc


def write_json(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_results(provider, rows, out, gallery=None, **retrieval):
    seen, results = set(), []
    for row in rows:
        if row["id"] in seen:
            continue
        seen.add(row["id"])
        results.append({**row, "option": len(results) + 1, "visual_verified": False})
    document = {"schema_version": 1, "provider": provider, "retrieved_at": now(), "retrieval": retrieval, "results": results}
    write_json(out, document)
    if gallery:
        write_gallery(document, gallery)
    return document


def write_gallery(doc, path):
    esc = lambda value: html.escape(str(value or ""), quote=True)
    cards = []
    for r in doc["results"]:
        thumb = r.get("thumbnail")
        image = f'<img src="{esc(thumb)}" alt="Preview of {esc(r.get("title"))}" loading="lazy">' if thumb else '<p>No image preview; open the source.</p>'
        license_value = r.get("license", {})
        license_name = license_value.get("title", "See source") if isinstance(license_value, dict) else license_value
        cards.append(f'<article data-resource-id="{esc(r["id"])}"><h2>Option {r["option"]}</h2>{image}<h3>{esc(r.get("title",r["id"]))}</h3><p><code>{esc(r["id"])}</code></p><p>{esc(r.get("type"))} · {esc(license_name)}</p><p>{esc(r.get("author"))}</p><a href="{esc(r["page_url"])}" target="_blank" rel="noopener noreferrer">View source and attribution</a></article>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Resource options</title><style>body{font:16px/1.5 system-ui;margin:0;padding:24px;background:#101923;color:#eef4f9}main{max-width:1200px;margin:auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:20px}article{padding:18px;border:1px solid #50687c;border-radius:12px;background:#1d2c3b;overflow-wrap:anywhere}img{width:100%;height:220px;object-fit:contain;background:#f1f4f7;border-radius:6px}a{color:#98dcff}h2{font-size:18px}h3{font-size:20px}code{font-size:13px}</style><main><h1>''' + esc(doc["provider"]) + ''' resource options</h1><p>Resources provided by ''' + esc(doc["provider"]) + '''. Select an option number to request its download.</p><p>Previews are candidates; visual matches have not been verified automatically.</p><section class="grid">''' + ("".join(cards) or "<p>No results in this search window.</p>") + "</section></main></html>"
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(page, encoding="utf-8")


def selection(args, provider):
    if args.manifest:
        if bool(args.id) == (args.option is not None):
            raise ResourceError("With --manifest, choose exactly one --id or --option.")
        doc = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        if doc.get("schema_version") != 1 or doc.get("provider") != provider:
            raise ResourceError("This selection manifest belongs to a different provider or schema.")
        rows = doc.get("results", [])
        matches = [r for r in rows if (r.get("id") == args.id if args.id else r.get("option") == args.option)]
        if len(matches) != 1:
            raise ResourceError("The selection is missing or ambiguous in the saved list.")
        return matches[0]["id"]
    if not args.id or args.option is not None:
        raise ResourceError("Provide an exact --id or a saved --manifest and --option.")
    return args.id


def add_selector(parser):
    parser.add_argument("--id")
    parser.add_argument("--manifest")
    parser.add_argument("--option", type=int)


def safe_member(name):
    if not name or any(c in name for c in '\\:*?"<>|') or any(ord(c) < 32 for c in name):
        raise ResourceError("Unsafe archive or dependency path.")
    p = PurePosixPath(name)
    if p.is_absolute() or any(x in ("", ".", "..") for x in name.split("/")):
        raise ResourceError("Unsafe archive or dependency path.")
    for part in p.parts:
        if re.match(r"^(?:CON|PRN|AUX|NUL|COM[1-9\u00b9\u00b2\u00b3]|LPT[1-9\u00b9\u00b2\u00b3])(?:\.|$)", part, re.I) or part.endswith((" ", ".")):
            raise ResourceError("Unsafe Windows filename in archive or dependency.")
    return p


def zip_inventory(path, verify=False, max_bytes=2 * 1024 ** 3):
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        if len(infos) > 20000 or sum(i.file_size for i in infos) > max_bytes:
            raise ResourceError("Archive exceeds the bounded extraction inventory.")
        names = set()
        for i in infos:
            name = i.filename.rstrip("/")
            safe_member(name)
            if name.casefold() in names or ((i.external_attr >> 16) & 0o170000) == 0o120000:
                raise ResourceError("Archive contains colliding paths or symbolic links.")
            names.add(name.casefold())
        if verify and z.testzip():
            raise ResourceError("Archive CRC validation failed.")
        return [{"path": i.filename, "bytes": i.file_size, "directory": i.is_dir()} for i in infos]


def verify_file(path, extension):
    with Path(path).open("rb") as f:
        head = f.read(512)
    if not head or head.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        raise ResourceError("The response is empty or is an HTML page instead of an asset.")
    ext = extension.lower().lstrip(".")
    signatures = {"jpg": b"\xff\xd8\xff", "jpeg": b"\xff\xd8\xff", "png": b"\x89PNG\r\n\x1a\n", "exr": b"v/1\x01", "hdr": b"#?", "glb": b"glTF"}
    if ext in signatures and not head.startswith(signatures[ext]):
        raise ResourceError(f"The downloaded bytes do not match the expected {ext} format.")
    if ext == "webp" and not (head[:4] == b"RIFF" and head[8:12] == b"WEBP"):
        raise ResourceError("Invalid WebP signature.")
    if ext == "mp4" and head[4:8] != b"ftyp":
        raise ResourceError("Invalid MP4 signature.")
    if ext == "zip":
        return {"format": "zip", "members": zip_inventory(path, verify=True)}
    if ext == "svg":
        root = ElementTree.parse(path).getroot()
        if root.tag.split("}")[-1] != "svg":
            raise ResourceError("Expected an SVG root element.")
        for e in root.iter():
            if e.tag.split("}")[-1] in ("script", "foreignObject", "image"):
                raise ResourceError("The icon contains unsupported executable or raster content.")
            for key, value in e.attrib.items():
                if key.lower().startswith("on") or (key.split("}")[-1] == "href" and not value.startswith("#")):
                    raise ResourceError("The icon contains external references or event handlers.")
        return {"format": "svg", "viewBox": root.get("viewBox")}
    if ext == "gltf":
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
        if "asset" not in doc:
            raise ResourceError("Invalid glTF JSON.")
    return {"format": ext, "validation": "signature where supported; length and checksum when supplied"}


def fetch_file(client, entry, output, max_mib=512):
    p = Path(output)
    if p.exists():
        raise ResourceError("Output already exists; choose a new path.")
    if max_mib <= 0:
        raise ResourceError("The download limit must be positive.")
    cap = int(max_mib * 1024 ** 2)
    if entry.get("bytes") and int(entry["bytes"]) > cap:
        raise ResourceError("Asset exceeds --max-mib; choose a smaller variant or raise the explicit limit.")
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with client.open(entry["url"]) as r:
            if "text/html" in r.headers.get("Content-Type", "").lower():
                raise ResourceError("Received an HTML page instead of the selected file.")
            declared = int(r.headers["Content-Length"]) if r.headers.get("Content-Length") else None
            if declared and declared > cap:
                raise ResourceError("Response exceeds --max-mib.")
            sha, md5, size = hashlib.sha256(), hashlib.md5(), 0
            with tempfile.NamedTemporaryFile(dir=p.parent, prefix=".asset-", suffix=".part", delete=False) as f:
                temp = Path(f.name)
                while block := r.read(1024 * 1024):
                    size += len(block)
                    if size > cap:
                        raise ResourceError("Download exceeded --max-mib.")
                    f.write(block)
                    sha.update(block)
                    md5.update(block)
            final_url = r.url
        if not size or (declared is not None and size != declared) or (entry.get("bytes") is not None and size != int(entry["bytes"])):
            raise ResourceError("Downloaded byte length does not match the selected file.")
        if entry.get("md5") and md5.hexdigest() != entry["md5"].lower():
            raise ResourceError("Provider checksum mismatch.")
        validation = verify_file(temp, entry.get("extension") or p.suffix)
        # Same-directory hard link publishes complete bytes without replacing a file.
        os.link(temp, p)
        return {"path": str(p), "url": entry["url"], "final_url": final_url, "bytes": size, "sha256": sha.hexdigest(), "provider_md5": entry.get("md5"), "validation": validation}
    except (HTTPException, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise ResourceError("The selected file is incomplete or has an invalid container.") from exc
    finally:
        if temp:
            temp.unlink(missing_ok=True)


def download_one(client, provider, asset, variant, entry, output, max_mib=512):
    receipt_path = Path(str(output) + ".json")
    if receipt_path.exists():
        raise ResourceError("Download receipt already exists; choose a new path.")
    expected = entry.get("extension", "").lower().lstrip(".")
    actual = Path(output).suffix.lower().lstrip(".")
    if expected and actual != expected and {actual, expected} != {"jpg", "jpeg"}:
        raise ResourceError(f"Use a .{expected} output filename for this variant.")
    receipt = {"schema_version": 1, "provider": provider, "asset_id": asset["id"], "variant": variant, "downloaded_at": now(), "source": asset, "file": fetch_file(client, entry, output, max_mib)}
    write_json(receipt_path, receipt)
    return receipt


def entry_for(variants, key):
    matches = [r for r in variants if r["key"] == key]
    if len(matches) != 1:
        raise ResourceError("Selected variant is missing or ambiguous; inspect the exact asset again.")
    return matches[0]


def summarize(doc):
    if "results" in doc:
        return {k: v for k, v in doc.items() if k != "results"} | {"results": [{k: v for k, v in r.items() if k not in ("variants", "raw")} for r in doc["results"]]}
    return doc
