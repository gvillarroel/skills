#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search the ambientCG v3 API and download a selected free package."""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
from asset_io import (Client, ResourceError, add_selector, download_one, entry_for, fetch_file,
                      save_results, selection, summarize, write_json)

PROVIDER = "ambientCG"
API = "https://ambientcg.com/api/v3/"
HOSTS = {"ambientcg.com", "www.ambientcg.com", "acg-download.struffelproductions.com", "acg-media.struffelproductions.com"}
INCLUDE = "type,title,url,tags,dimensions,maps,downloads,thumbnails,releaseDate"
TYPES = ["material", "hdri", "substance", "decal", "atlas", "3d-model", "plain-image", "brush", "terrain", "hdri-element"]


def valid_id(value):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,150}", value or ""):
        raise ResourceError("Use an exact ambientCG asset ID from the saved list or source page.")
    return value


def normalize(row):
    if row.get("releaseDate", "") > date.today().isoformat():
        raise ResourceError("Asset is still in early access; use a freely released asset.")
    variants = [{"key": d["attributes"] + "/" + d["extension"], "url": d["url"], "extension": d["extension"], "bytes": d.get("size")} for d in row.get("downloads", [])]
    return {"id": valid_id(row["id"]), "title": row.get("title", row["id"]), "type": row.get("type"),
            "page_url": row["url"], "thumbnail": row.get("thumbnails", {}).get("512-PNG"),
            "author": "ambientCG", "license": {"title": "CC0", "url": "https://docs.ambientcg.com/license/"},
            "tags": row.get("tags", []), "maps": row.get("maps", []), "dimensions": row.get("dimensions"), "variants": variants}


def inspect(client, asset_id):
    data = client.data(API + "assets", {"id": valid_id(asset_id), "include": INCLUDE, "limit": 1})
    rows = [r for r in data["assets"] if r["id"] == asset_id]
    if len(rows) != 1:
        raise ResourceError("Selected asset is no longer available.")
    return normalize(rows[0])


def previews(client, manifest, output):
    doc = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if doc.get("provider") != PROVIDER or doc.get("schema_version") != 1:
        raise ResourceError("Use an ambientCG selection manifest.")
    root = Path(output)
    if root.exists():
        raise ResourceError("Preview directory already exists; choose a new directory.")
    rows = doc.get("results", [])
    if len(rows) > 20:
        raise ResourceError("Preview at most 20 saved options at once.")
    plans = []
    for row in rows:
        asset = inspect(client, row["id"])
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


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("search")
    s.add_argument("--query", required=True)
    s.add_argument("--type", choices=TYPES, default="material")
    s.add_argument("--sort", choices=["popular", "latest", "downloads", "oldest", "alphabet"], default="popular")
    s.add_argument("--limit", type=int, default=6)
    s.add_argument("--offset", type=int, default=0)
    s.add_argument("--out", required=True)
    s.add_argument("--html")
    v = sub.add_parser("previews")
    v.add_argument("--manifest", required=True)
    v.add_argument("--output-dir", required=True)
    for mode in ("inspect", "download"):
        s = sub.add_parser(mode)
        add_selector(s)
        if mode == "inspect":
            s.add_argument("--out", required=True)
        else:
            s.add_argument("--variant", required=True, help="Exact key from inspect, such as 2K-JPG/zip.")
            s.add_argument("--output", required=True)
            s.add_argument("--max-mib", type=float, default=512)
    return p


def run(args, client=None):
    client = client or Client(HOSTS, "AmbientCGMaterialSkill")
    if args.command == "previews":
        return previews(client, args.manifest, args.output_dir)
    if args.command == "search":
        if not args.query.strip() or not 1 <= args.limit <= 20 or args.offset < 0:
            raise ResourceError("Use a nonempty query, --limit 1-20 and nonnegative --offset.")
        data = client.data(API + "assets", {"q": args.query.strip(), "type": args.type, "sort": args.sort, "limit": args.limit, "offset": args.offset, "include": INCLUDE})
        return save_results(PROVIDER, [normalize(r) for r in data["assets"]], args.out, args.html, query=args.query, type=args.type,
                            offset=args.offset, total=data.get("totalResults"), has_more=bool(data.get("nextPageHttp")))
    asset = inspect(client, selection(args, PROVIDER))
    if args.command == "inspect":
        write_json(args.out, asset)
        return asset
    entry = entry_for(asset["variants"], args.variant)
    return download_one(client, PROVIDER, asset, args.variant, entry, args.output, args.max_mib)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        print(json.dumps(summarize(run(parser().parse_args())), ensure_ascii=False, indent=2))
    except (ResourceError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
