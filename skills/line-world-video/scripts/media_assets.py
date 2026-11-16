#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2"]
# ///
"""Acquire reviewed portraits/logos and export portable circular graph assets."""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import io
import json
import mimetypes
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

VERSION = "2"
MAX_BYTES = 24 * 1024 * 1024
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch(url):
    if urllib.parse.urlparse(url).scheme not in ("https", "http"):
        raise ValueError("Download URLs must use HTTP or HTTPS.")
    req = urllib.request.Request(url, headers={"User-Agent": "LineWorldMedia/0.10 (educational assets; attribution retained)"})
    with urllib.request.urlopen(req, timeout=35) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Source exceeds the 24 MiB asset limit.")
    return data


def search(query, limit):
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": query,
              "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo", "iiprop": "url|extmetadata"}
    result = json.loads(fetch("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)))
    candidates = []
    for page in result.get("query", {}).get("pages", {}).values():
        info = page.get("imageinfo", [{}])[0]
        if not re.search(r"\.(jpe?g|png|webp|svg)$", page["title"], re.I):
            continue
        meta = info.get("extmetadata", {})
        clean = lambda key: html.unescape(re.sub("<[^>]+>", "", meta.get(key, {}).get("value", "")))
        candidates.append({"title": page["title"], "sourcePage": info.get("descriptionurl"),
                           "downloadUrl": info.get("url"), "creator": clean("Artist"),
                           "license": clean("LicenseShortName"), "licenseUrl": clean("LicenseUrl"),
                           "description": clean("ImageDescription")[:500], "reviewed": False})
    return {"query": query, "candidates": candidates, "note": "Inspect the actual image and source identity before selection."}


def check_entry(entry):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry.get("id", "")):
        raise ValueError("Asset IDs must be stable lowercase hyphen-case.")
    if entry.get("kind") not in ("portrait", "logo") or entry.get("reviewed") is not True:
        raise ValueError("Select a reviewed portrait or logo.")
    for key in ("label", "sourcePage", "identityEvidence", "contributionEvidence"):
        if not entry.get(key):
            raise ValueError("Missing reviewed asset field: " + key)
    for key in ("creator", "license", "credit"):
        if not entry.get("rights", {}).get(key):
            raise ValueError("Missing rights field: " + key)
    if bool(entry.get("sourceFile")) == bool(entry.get("downloadUrl")):
        raise ValueError("Provide exactly one sourceFile or downloadUrl.")


def vector_source(data, depth=0):
    if depth > 8:
        raise ValueError("Embedded SVG nesting exceeds the asset limit.")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("SVG DTD/entity declarations are unsupported.")
    root = ET.fromstring(data)
    if root.tag.split("}")[-1] != "svg":
        raise ValueError("Expected an SVG root.")
    for element in root.iter():
        tag = element.tag.split("}")[-1].lower()
        if tag in ("script", "foreignobject", "animate", "set"):
            raise ValueError("Logo SVG must contain static vector artwork only.")
        embedded_vector = False
        if tag == "image":
            href = element.get("href", element.get("{http://www.w3.org/1999/xlink}href", ""))
            prefix = "data:image/svg+xml;base64,"
            if not href.startswith(prefix):
                raise ValueError("Logo image wrappers must embed vector SVG, without raster or remote images.")
            vector_source(base64.b64decode(href[len(prefix):], validate=True), depth + 1)
            embedded_vector = True
        for key, value in element.attrib.items():
            if key.split("}")[-1].lower().startswith("on"):
                raise ValueError("SVG event attributes are unsupported.")
            if key.split("}")[-1] == "href" and not value.startswith("#") and not embedded_vector:
                raise ValueError("External SVG dependencies are unsupported.")
            if any(not url.strip(" \t\r\n\"'").startswith("#") for url in re.findall(r"url\(([^)]+)\)", value, re.I)):
                raise ValueError("External SVG paint dependencies are unsupported.")
        css = element.text or ""
        if element.tag.split("}")[-1] == "style" and (re.search(r"@import", css, re.I) or any(not url.strip(" \t\r\n\"'").startswith("#") for url in re.findall(r"url\(([^)]+)\)", css, re.I))):
            raise ValueError("External CSS dependencies are unsupported.")
    if "viewBox" not in root.attrib:
        values = [re.fullmatch(r"([\d.]+)(?:px)?", root.get(key, "")) for key in ("width", "height")]
        if not all(values):
            raise ValueError("SVG needs a viewBox or numeric dimensions.")
        root.set("viewBox", "0 0 " + " ".join(v[1] for v in values))
    root.set("x", "44"); root.set("y", "44"); root.set("width", "168"); root.set("height", "168")
    root.set("preserveAspectRatio", "xMidYMid meet")
    return ET.tostring(root, encoding="unicode")


def circular(entry, data):
    label = html.escape(entry["label"])
    rights = entry["rights"]
    description = html.escape(rights["credit"] + "; " + rights["license"] + "; " + entry["sourcePage"])
    header = f'<svg xmlns="{NS}" width="256" height="256" viewBox="0 0 256 256" role="img"><title>{label}</title><desc>{description}</desc>'
    if data.lstrip().startswith(b"<") and entry["kind"] == "logo":
        return (header + '<circle cx="128" cy="128" r="126" fill="#ffffff" stroke="#cfcfcf" stroke-width="2"/>' + vector_source(data) + "</svg>").encode(), True
    with Image.open(io.BytesIO(data)) as picture:
        picture.verify()
    with Image.open(io.BytesIO(data)) as picture:
        width, height = picture.size
        mime = Image.MIME[picture.format]
    if width < 64 or height < 64:
        raise ValueError("Raster source is too small for a legible asset.")
    source = "data:" + mime + ";base64," + base64.b64encode(data).decode()
    if entry["kind"] == "logo":
        body = f'<circle cx="128" cy="128" r="126" fill="#ffffff" stroke="#cfcfcf" stroke-width="2"/><image x="44" y="44" width="168" height="168" href="{source}" preserveAspectRatio="xMidYMid meet"/>'
    else:
        focus = entry.get("focus", [.5, .3])
        if len(focus) != 2 or not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in focus):
            raise ValueError("Portrait focus must contain two normalized coordinates.")
        zoom = entry.get("zoom", 1)
        if not isinstance(zoom, (int, float)) or not 1 <= zoom <= 4:
            raise ValueError("Portrait zoom must be between 1 and 4.")
        side = min(width, height) / zoom
        x = max(0, min(width - side, focus[0] * width - side / 2))
        y = max(0, min(height - side, focus[1] * height - side / 2))
        scale = 252 / side
        body = f'<defs><clipPath id="portrait"><circle cx="128" cy="128" r="126"/></clipPath></defs><image x="{2-x*scale}" y="{2-y*scale}" width="{width*scale}" height="{height*scale}" href="{source}" clip-path="url(#portrait)"/><circle cx="128" cy="128" r="126" fill="none" stroke="#cfcfcf" stroke-width="2"/>'
    return (header + body + "</svg>").encode(), False


def png_outputs(records, output):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        roots = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
        paths = sorted(roots.glob("chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe"), reverse=True)
        browser = pw.chromium.launch(executable_path=str(paths[0]) if paths else None, headless=True)
        page = browser.new_page(viewport={"width": 256, "height": 256}, device_scale_factor=2)
        for record in records:
            svg = output / record["svg"]
            png = svg.with_suffix(".png")
            if record.get("pngSha256") and png.is_file() and digest(png.read_bytes()) == record["pngSha256"]:
                continue
            page.set_content('<style>html,body{margin:0;background:transparent}</style>' + svg.read_text(encoding="utf-8"))
            page.evaluate("async()=>{await Promise.all([...document.querySelectorAll('image')].map(e=>new Promise((ok,bad)=>{const i=new Image();i.onload=ok;i.onerror=bad;i.src=e.getAttribute('href')})))}")
            page.screenshot(path=str(png), omit_background=True)
            record["png"] = png.relative_to(output).as_posix(); record["pngSha256"] = digest(png.read_bytes())
        browser.close()


def build(request, output, png=False, refresh=False):
    entries = json.loads(request.read_text(encoding="utf-8"))["assets"]
    ids = [entry.get("id") for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate asset IDs.")
    output.mkdir(parents=True, exist_ok=True)
    previous = json.loads((output / "manifest.json").read_text(encoding="utf-8")) if (output / "manifest.json").is_file() else {"assets": []}
    old = {entry["id"]: entry for entry in previous["assets"]}; records = []; reused = []
    for entry in entries:
        check_entry(entry)
        prior = old.get(entry["id"], {})
        cached = output / prior.get("original", "missing")
        if entry.get("sourceFile"):
            data = (request.parent / entry["sourceFile"]).read_bytes()
        elif not refresh and prior.get("downloadUrl") == entry["downloadUrl"] and cached.is_file() and digest(cached.read_bytes()) == prior.get("sourceSha256"):
            data = cached.read_bytes()
        else:
            data = fetch(entry["downloadUrl"])
        sha = digest(data)
        if entry.get("sourceSha256") and sha != entry["sourceSha256"]:
            raise ValueError("Pinned source digest changed for " + entry["id"])
        key = digest(json.dumps({"version": VERSION, "entry": entry, "source": sha}, sort_keys=True).encode())
        svg = output / (entry["id"] + ".circle.svg")
        if prior.get("cacheKey") == key and svg.is_file() and digest(svg.read_bytes()) == prior.get("svgSha256"):
            records.append(prior); reused.append(entry["id"]); continue
        wrapped, vector = circular(entry, data)
        extension = ".svg" if vector else mimetypes.guess_extension(Image.MIME[Image.open(io.BytesIO(data)).format]) or ".bin"
        original = output / "originals" / (entry["id"] + extension)
        original.parent.mkdir(parents=True, exist_ok=True); original.write_bytes(data); svg.write_bytes(wrapped)
        records.append({**entry, "original": original.relative_to(output).as_posix(), "sourceSha256": sha,
                        "svg": svg.name, "svgSha256": digest(wrapped), "vectorArtwork": vector,
                        "cacheKey": key, "changes": "Circular viewport over original photograph" if entry["kind"] == "portrait" else "Unchanged artwork centered inside a separate circular support"})
    if png:
        png_outputs(records, output)
    save(output / "manifest.json", {"schemaVersion": 1, "assets": records})
    save(output / "graph-nodes.json", {"nodes": [{"id": e["id"], "label": e["label"], "kind": e["kind"], "role": e.get("role"), "stage": e.get("stage"), "image": e["svg"] if e["vectorArtwork"] or e["kind"] == "portrait" else e.get("png", e["svg"]), "width": 256, "height": 256, "shape": "circle", "sourcePage": e["sourcePage"]} for e in records], "edges": []})
    credits = ["# Media credits", "", "Keep this file with the film and derived graph assets.", ""]
    for entry in records:
        rights = entry["rights"]
        credits.extend(["## " + entry["label"], "", rights["credit"], "", "Source: " + entry["sourcePage"], "License: " + rights["license"] + (" — " + rights["licenseUrl"] if rights.get("licenseUrl") else ""), "Changes: " + entry["changes"], ""])
    (output / "credits.md").write_text("\n".join(credits), encoding="utf-8")
    return {"ok": True, "assets": len(records), "reused": reused, "output": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    find = sub.add_parser("search"); find.add_argument("--query", required=True); find.add_argument("--limit", type=int, default=5); find.add_argument("--output", type=Path, required=True)
    make = sub.add_parser("build"); make.add_argument("--request", type=Path, required=True); make.add_argument("--output", type=Path, required=True); make.add_argument("--png", action="store_true"); make.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "search":
            if not 1 <= args.limit <= 12: raise ValueError("Search limit must be between 1 and 12.")
            result = search(args.query, args.limit); save(args.output, result)
            print(json.dumps({"ok": True, "candidates": len(result["candidates"]), "output": str(args.output)}))
        else:
            print(json.dumps(build(args.request.resolve(), args.output.resolve(), args.png, args.refresh)))
        return 0
    except (ValueError, OSError, ET.ParseError) as error:
        print(json.dumps({"ok": False, "error": str(error)})); return 2


if __name__ == "__main__":
    sys.exit(main())
