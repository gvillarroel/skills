#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Find coherent Iconify icon choices and download identity-bound SVGs."""
import argparse
import json
import re
import sys
from urllib.parse import urlencode

sys.dont_write_bytecode = True
from asset_io import (Client, ResourceError, add_selector, download_one,
                      save_results, selection, summarize, write_json)

PROVIDER = "Iconify"
API = "https://api.iconify.design"
HOSTS = {"api.iconify.design", "api.simplesvg.com", "api.unisvg.com"}


def split_id(value):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*:[a-z0-9]+(?:-[a-z0-9]+)*", value or ""):
        raise ResourceError("Use an exact Iconify prefix:name identity from search.")
    return value.split(":", 1)


def normalize(asset_id, info):
    prefix, name = split_id(asset_id)
    return {"id": asset_id, "title": name.replace("-", " "), "type": "icon", "family": prefix,
            "page_url": f"https://icon-sets.iconify.design/{prefix}/{name}/", "thumbnail": f"{API}/{prefix}/{name}.svg?height=128&color=%2317222d",
            "author": info.get("author", {}).get("name"), "license": info.get("license", {"title": "Check collection source"}),
            "collection": info.get("name", prefix), "multicolor": info.get("palette"), "collection_tags": info.get("tags", [])}


def inspect(client, asset_id):
    prefix, name = split_id(asset_id)
    data = client.data(API + "/" + prefix + ".json", {"icons": name})
    if name not in data.get("icons", {}) and name not in data.get("aliases", {}):
        raise ResourceError("The selected icon is no longer present in its collection.")
    collection = client.data(API + "/collection", {"prefix": prefix, "info": 1})
    return normalize(asset_id, collection.get("info", {}))


def svg_entry(asset_id, color, size):
    prefix, name = split_id(asset_id)
    if not re.fullmatch(r"(?:#[0-9a-fA-F]{3,8}|[a-zA-Z]+)", color) or not 1 <= size <= 4096:
        raise ResourceError("Use a CSS color name or hex color and --size between 1 and 4096.")
    return {"key": "svg", "extension": "svg", "url": f"{API}/{prefix}/{name}.svg?" + urlencode({"color": color, "height": size})}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("collections")
    c.add_argument("--out", required=True)
    s = sub.add_parser("search")
    s.add_argument("--query", required=True)
    s.add_argument("--prefix", help="Limit to one family, such as lucide or mdi.")
    s.add_argument("--limit", type=int, default=6)
    s.add_argument("--start", type=int, default=0)
    s.add_argument("--out", required=True)
    s.add_argument("--html")
    for mode in ("inspect", "download"):
        s = sub.add_parser(mode)
        add_selector(s)
        if mode == "inspect":
            s.add_argument("--out", required=True)
        else:
            s.add_argument("--output", required=True)
            s.add_argument("--color", default="currentColor")
            s.add_argument("--size", type=int, default=24)
            s.add_argument("--max-mib", type=float, default=4)
    return p


def run(args, client=None):
    client = client or Client(HOSTS, "IconifyIconSkill")
    if args.command == "collections":
        data = client.data(API + "/collections")
        write_json(args.out, data)
        return {"collections": len(data), "out": args.out}
    if args.command == "search":
        if not args.query.strip() or not 1 <= args.limit <= 20 or args.start < 0:
            raise ResourceError("Use a nonempty query, --limit 1-20 and a nonnegative start.")
        if args.prefix and not re.fullmatch(r"[a-z0-9-]+", args.prefix):
            raise ResourceError("Invalid collection prefix.")
        data = client.data(API + "/search", {"query": args.query, "prefix": args.prefix, "limit": 32, "start": args.start})
        ids = [i for i in data.get("icons", []) if not args.prefix or i.split(":")[0] == args.prefix][:args.limit]
        rows = [normalize(i, data.get("collections", {}).get(i.split(":")[0], {})) for i in ids]
        return save_results(PROVIDER, rows, args.out, args.html, query=args.query, prefix=args.prefix, start=args.start,
                            next_start=args.start + len(rows), total=data.get("total"), fetched=len(data.get("icons", [])))
    asset = inspect(client, selection(args, PROVIDER))
    if args.command == "inspect":
        write_json(args.out, asset)
        return asset
    asset["export"] = {"color": args.color, "height": args.size}
    return download_one(client, PROVIDER, asset, "svg", svg_entry(asset["id"], args.color, args.size), args.output, args.max_mib)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        print(json.dumps(summarize(run(parser().parse_args())), ensure_ascii=False, indent=2))
    except (ResourceError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
