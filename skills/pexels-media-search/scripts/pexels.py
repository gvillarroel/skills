#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search free Pexels photos/videos using an environment-held API key."""
import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.dont_write_bytecode = True
from asset_io import (Client, ResourceError, add_selector, download_one, entry_for,
                      save_results, selection, summarize, write_json)

PROVIDER = "Pexels"
API = "https://api.pexels.com/v1"
HOSTS = {"api.pexels.com", "www.pexels.com", "images.pexels.com", "videos.pexels.com", "static-videos.pexels.com", "player.vimeo.com"}


def credentials():
    value = os.environ.get("PEXELS_API_KEY", "").strip()
    if not value:
        raise ResourceError("PEXELS_API_KEY is not configured. Obtain a free key at https://www.pexels.com/api/ and set it privately in the environment, or use the browser workflow.")
    return {"Authorization": value}


def split_id(value):
    match = re.fullmatch(r"(photo|video):([1-9][0-9]*)", value or "")
    if not match:
        raise ResourceError("Use a typed ID such as photo:2014422 or video:2499611.")
    return match.groups()


def normalize(row, kind):
    if kind == "photo":
        variants = [{"key": key, "url": url, "extension": Path(urlsplit(url).path).suffix.lstrip(".") or "jpeg",
                     "transformed": key != "original"} for key, url in row["src"].items()]
        title, thumb, author = row.get("alt") or f"Photo {row['id']}", row["src"].get("medium"), row.get("photographer")
        author_url = row.get("photographer_url")
    else:
        variants = [{"key": str(f["id"]), "url": f["link"], "extension": "mp4", "width": f.get("width"), "height": f.get("height"),
                     "quality": f.get("quality"), "fps": f.get("fps")} for f in row.get("video_files", []) if f.get("file_type") == "video/mp4"]
        title, thumb, author = f"Video {row['id']}", row.get("image"), row.get("user", {}).get("name")
        author_url = row.get("user", {}).get("url")
    return {"id": f"{kind}:{row['id']}", "title": title, "type": kind, "page_url": row["url"], "thumbnail": thumb,
            "width": row.get("width"), "height": row.get("height"), "duration": row.get("duration"), "author": author,
            "author_url": author_url, "license": {"title": "Pexels License", "url": "https://www.pexels.com/license/"}, "variants": variants}


def inspect(client, asset_id, headers):
    kind, number = split_id(asset_id)
    path = "/photos/" if kind == "photo" else "/videos/videos/"
    row = client.data(API + path + number, headers=headers)
    if str(row.get("id")) != number:
        raise ResourceError("Refreshed metadata does not identify the selected asset.")
    return normalize(row, kind)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("status")
    s.add_argument("--out")
    s = sub.add_parser("search")
    s.add_argument("--query", required=True)
    s.add_argument("--type", choices=["photo", "video"], default="photo")
    s.add_argument("--orientation", choices=["landscape", "portrait", "square"])
    s.add_argument("--size", choices=["large", "medium", "small"])
    s.add_argument("--color")
    s.add_argument("--locale", default="en-US")
    s.add_argument("--page", type=int, default=1)
    s.add_argument("--limit", type=int, default=6)
    s.add_argument("--out", required=True)
    s.add_argument("--html")
    for mode in ("inspect", "download"):
        s = sub.add_parser(mode)
        add_selector(s)
        if mode == "inspect":
            s.add_argument("--out", required=True)
        else:
            s.add_argument("--variant", help="Photo src key or exact video_file ID. Photos default to original.")
            s.add_argument("--output", required=True)
            s.add_argument("--max-mib", type=float, default=512)
    return p


def run(args, client=None):
    if args.command == "status":
        result = {"provider": PROVIDER, "api_key_configured": bool(os.environ.get("PEXELS_API_KEY", "").strip()), "api_key_setup_url": "https://www.pexels.com/api/", "cost": "Free API; published rate limits apply", "browser_fallback": "https://www.pexels.com/"}
        if args.out:
            write_json(args.out, result)
        return result
    headers = credentials()
    client = client or Client(HOSTS, "PexelsMediaSkill")
    if args.command == "search":
        if not args.query.strip() or not 1 <= args.limit <= 20 or args.page < 1:
            raise ResourceError("Use a nonempty query, --limit 1-20 and a positive page.")
        if args.color and args.type != "photo":
            raise ResourceError("Pexels color filtering is available only for photos.")
        path = "/search" if args.type == "photo" else "/videos/search"
        params = {"query": args.query, "orientation": args.orientation, "size": args.size, "page": args.page, "per_page": args.limit, "locale": args.locale}
        if args.type == "photo":
            params["color"] = args.color
        data = client.data(API + path, params, headers)
        field = "photos" if args.type == "photo" else "videos"
        return save_results(PROVIDER, [normalize(r, args.type) for r in data[field]], args.out, args.html,
                            query=args.query, type=args.type, page=args.page, total=data.get("total_results"), has_more=bool(data.get("next_page")))
    asset = inspect(client, selection(args, PROVIDER), headers)
    if args.command == "inspect":
        write_json(args.out, asset)
        return asset
    key = args.variant or ("original" if asset["type"] == "photo" else None)
    if key is None:
        raise ResourceError("Select the exact video_file ID with --variant after inspecting available dimensions.")
    return download_one(client, PROVIDER, asset, key, entry_for(asset["variants"], key), args.output, args.max_mib)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        print(json.dumps(summarize(run(parser().parse_args())), ensure_ascii=False, indent=2))
    except (ResourceError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
