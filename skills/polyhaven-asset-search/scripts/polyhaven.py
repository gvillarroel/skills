#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search free Poly Haven assets and download exact files and dependencies."""
import argparse
import json
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
from asset_io import (Client, ResourceError, add_selector, checked_url, download_one,
                      entry_for, fetch_file, now, safe_member, save_results,
                      selection, summarize, write_json, write_gallery)

PROVIDER = "Poly Haven"
API = "https://api.polyhaven.com"
HOSTS = {"api.polyhaven.com", "polyhaven.com", "dl.polyhaven.org", "cdn.polyhaven.com"}
TYPES = {0: "hdris", 1: "textures", 2: "models"}


def valid_id(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,150}", value or ""):
        raise ResourceError("Use an exact Poly Haven asset slug from a saved result or source page.")
    return value


def normalize(asset_id, row):
    if row.get("date_published", 0) > time.time():
        raise ResourceError("This asset has not reached its free public release date.")
    return {"id": valid_id(asset_id), "title": row.get("name", asset_id), "type": TYPES.get(row.get("type"), "unknown"),
            "page_url": "https://polyhaven.com/a/" + asset_id, "thumbnail": row.get("thumbnail_url"),
            "author": ", ".join(row.get("authors", {})), "license": {"title": "CC0", "url": "https://polyhaven.com/license"},
            "description": row.get("description"), "category": row.get("category"), "tags": row.get("tags", []),
            "max_resolution": row.get("max_resolution"), "attributes": row.get("attributes", {})}


def info(client, asset_id):
    return normalize(asset_id, client.data(API + "/info/" + valid_id(asset_id)))


def variants(data, path=()):
    found = []
    if isinstance(data, dict) and "url" in data:
        checked_url(data["url"], HOSTS)
        extension = Path(unquote(urlsplit(data["url"]).path)).suffix.lstrip(".")
        found.append({"key": "/".join(path), "url": data["url"], "bytes": data.get("size"), "md5": data.get("md5"),
                      "extension": extension, "include": data.get("include", {})})
    elif isinstance(data, dict):
        for key, value in data.items():
            found.extend(variants(value, path + (key,)))
    return found


def inspect(client, asset_id):
    asset = info(client, asset_id)
    asset["variants"] = variants(client.data(API + "/files/" + asset_id))
    return asset


def previews(client, manifest, output):
    doc = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if doc.get("provider") != PROVIDER or doc.get("schema_version") != 1:
        raise ResourceError("Use a Poly Haven selection manifest.")
    root = Path(output)
    if root.exists():
        raise ResourceError("Preview directory already exists; choose a new directory.")
    rows = doc.get("results", [])
    if len(rows) > 20:
        raise ResourceError("Preview at most 20 saved options at once.")
    plans = []
    for row in rows:
        asset = info(client, row["id"])
        url = asset.get("thumbnail")
        if url:
            ext = Path(urlsplit(url).path).suffix.lstrip(".")
            plans.append((row, {"url": url, "extension": ext}))
    root.mkdir(parents=True)
    downloaded = []
    for row, entry in plans:
        filename = f"{int(row['option'])}-{valid_id(row['id'])}.{entry['extension']}"
        file = fetch_file(client, entry, root / filename, 4)
        downloaded.append({"option": row["option"], "id": row["id"], **file})
    write_json(root / "previews.json", downloaded)
    return {"previews": downloaded}


def bundle(client, asset, keys, output, max_mib):
    dest = Path(output).resolve()
    if dest.exists():
        raise ResourceError("Bundle output directory already exists; choose a new directory.")
    files = {}
    for key in keys:
        entry = entry_for(asset["variants"], key)
        name = unquote(urlsplit(entry["url"]).path.rsplit("/", 1)[-1])
        plans = [(name, entry)]
        for relative, dep in entry.get("include", {}).items():
            plans.append((relative, {"url": dep["url"], "bytes": dep.get("size"), "md5": dep.get("md5"), "extension": Path(relative).suffix.lstrip(".")}))
        for relative, file in plans:
            safe_member(relative)
            checked_url(file["url"], HOSTS)
            if relative in files and files[relative]["url"] != file["url"]:
                raise ResourceError("Requested variants contain conflicting dependency paths.")
            files[relative] = file
    if "receipt.json" in files or len({k.casefold() for k in files}) != len(files):
        raise ResourceError("Bundle contains colliding paths.")
    if sum(f.get("bytes") or 0 for f in files.values()) > max_mib * 1024 ** 2:
        raise ResourceError("The complete bundle exceeds --max-mib.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(dir=dest.parent, prefix=".polyhaven-")).resolve()
    try:
        downloaded = []
        remaining = max_mib
        for relative, entry in files.items():
            file = fetch_file(client, entry, stage / relative, remaining)
            remaining -= file["bytes"] / 1024 ** 2
            downloaded.append({**file, "path": relative})
        receipt = {"schema_version": 1, "provider": PROVIDER, "asset_id": asset["id"], "variants": keys,
                   "downloaded_at": now(), "source": asset, "files": downloaded}
        write_json(stage / "receipt.json", receipt)
        if dest.exists():
            raise ResourceError("Output directory appeared during download.")
        stage.rename(dest)
        return {"output_dir": str(dest), **receipt}
    finally:
        if stage.exists() and stage.parent == dest.parent and stage.name.startswith(".polyhaven-"):
            shutil.rmtree(stage)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("search")
    s.add_argument("--query", required=True)
    s.add_argument("--type", choices=["all", "hdris", "textures", "models"], default="all")
    s.add_argument("--limit", type=int, default=6)
    s.add_argument("--out", required=True)
    s.add_argument("--html")
    t = sub.add_parser("taxonomy")
    t.add_argument("--type", choices=["hdris", "textures", "models"], required=True)
    t.add_argument("--out", required=True)
    v = sub.add_parser("previews")
    v.add_argument("--manifest", required=True)
    v.add_argument("--output-dir", required=True)
    g = sub.add_parser("gallery")
    g.add_argument("--manifest", required=True)
    g.add_argument("--html", required=True)
    for mode in ("inspect", "download"):
        s = sub.add_parser(mode)
        add_selector(s)
        if mode == "inspect":
            s.add_argument("--out", required=True)
        else:
            s.add_argument("--variant", action="append", required=True, help="Exact key from inspect; repeat for a bundle.")
            group = s.add_mutually_exclusive_group(required=True)
            group.add_argument("--output")
            group.add_argument("--output-dir")
            s.add_argument("--max-mib", type=float, default=512)
    return p


def run(args, client=None):
    if args.command == "gallery":
        doc = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        if doc.get("provider") != PROVIDER or doc.get("schema_version") != 1:
            raise ResourceError("Use a Poly Haven selection manifest.")
        write_gallery(doc, args.html)
        return {"gallery": Path(args.html).as_posix(), "options": len(doc["results"])}
    client = client or Client(HOSTS, "PolyHavenAssetSkill")
    if args.command == "previews":
        return previews(client, args.manifest, args.output_dir)
    if args.command == "taxonomy":
        data = client.data(API + "/taxonomy/" + args.type)
        write_json(args.out, data)
        return {"taxonomy": args.out}
    if args.command == "search":
        q = args.query.strip().lower()
        if not q or len(q) > 100 or not 1 <= args.limit <= 20:
            raise ResourceError("Use a query of 1-100 characters and --limit between 1 and 20.")
        data = client.data(API + "/search", {"q": q, "t": args.type, "limit": args.limit, "future": "false"})
        rows = [info(client, row["slug"]) | {"search_score": row.get("score")} for row in data["results"][:args.limit]]
        return save_results(PROVIDER, rows, args.out, args.html, query=q, type=args.type, total=data.get("total"), ranking="provider order; scores do not prove visual relevance")
    asset = inspect(client, valid_id(selection(args, PROVIDER)))
    if args.command == "inspect":
        write_json(args.out, asset)
        return asset
    if args.output_dir:
        return bundle(client, asset, args.variant, args.output_dir, args.max_mib)
    if len(args.variant) != 1:
        raise ResourceError("Use --output-dir for multiple variants.")
    entry = entry_for(asset["variants"], args.variant[0])
    if entry.get("include"):
        raise ResourceError("This file needs dependencies; use --output-dir to keep the package complete.")
    return download_one(client, PROVIDER, asset, args.variant[0], entry, args.output, args.max_mib)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        print(json.dumps(summarize(run(parser().parse_args())), ensure_ascii=False, indent=2))
    except (ResourceError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
