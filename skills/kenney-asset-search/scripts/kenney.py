#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search free Kenney packs, download exact ZIPs, and extract selected files."""
import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

sys.dont_write_bytecode = True
from asset_io import (Client, ResourceError, add_selector, checked_url, download_one, fetch_file,
                      safe_member, save_results, selection, summarize, write_json, zip_inventory)

PROVIDER = "Kenney"
BASE = "https://kenney.nl"
HOSTS = {"kenney.nl", "www.kenney.nl"}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.meta, self.covers, self.headers = [], {}, {}, []
        self.anchor, self.heading = None, None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a":
            self.anchor = {**a, "text": ""}
            self.links.append(self.anchor)
        if tag == "meta":
            self.meta[a.get("property", a.get("name"))] = a.get("content", "")
        if tag == "h1":
            self.heading = []
        if "cover" in a.get("class", "").split():
            match = re.search(r'url\([\"\']?([^\)\"\']+)', a.get("style", ""))
            if match:
                image = urljoin(BASE, match.group(1))
                slug = re.search(r"/media/pages/assets/([^/]+)/", image)
                if slug:
                    self.covers[slug.group(1)] = image

    def handle_data(self, data):
        if self.anchor is not None:
            self.anchor["text"] += data
        if self.heading is not None:
            self.heading.append(data)

    def handle_endtag(self, tag):
        if tag == "a":
            self.anchor = None
        if tag == "h1" and self.heading is not None:
            self.headers.append("".join(self.heading).strip())
            self.heading = None


def valid_id(value):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value or ""):
        raise ResourceError("Use the exact Kenney pack slug from a source page or saved result.")
    return value


def basic(asset_id, title, thumbnail=None):
    return {"id": valid_id(asset_id), "title": title, "type": "game asset pack", "page_url": BASE + "/assets/" + asset_id,
            "thumbnail": thumbnail, "author": "Kenney", "license": {"title": "CC0", "url": "https://kenney.nl/support"}}


def search_rows(text):
    page = Page(text)
    result, seen = [], set()
    for a in page.links:
        url = urljoin(BASE, a.get("href", ""))
        p = urlsplit(url)
        match = re.fullmatch(r"/assets/([a-z0-9]+(?:-[a-z0-9]+)*)", p.path)
        if p.hostname in HOSTS and match and a["text"].strip() and match.group(1) not in seen:
            asset_id = match.group(1)
            seen.add(asset_id)
            result.append(basic(asset_id, a["text"].strip(), page.covers.get(asset_id)))
    return result


def inspect(client, asset_id):
    asset_id = valid_id(asset_id)
    page = Page(client.data(BASE + "/assets/" + asset_id, text=True))
    canonical = page.meta.get("og:url")
    if canonical and canonical.rstrip("/") != BASE + "/assets/" + asset_id:
        raise ResourceError("The source page no longer identifies the chosen pack.")
    license_links = [a.get("href", "") for a in page.links if "creativecommons.org/publicdomain/zero/1.0" in a.get("href", "")]
    links = [urljoin(BASE, a["href"]) for a in page.links if a.get("id") == "donate-text" and urlsplit(a.get("href", "")).path.endswith(".zip")]
    if len(links) != 1 or not license_links:
        raise ResourceError("No unique free CC0 ZIP was found. Inspect the public pack page; do not use the paid bundle.")
    checked_url(links[0], HOSTS)
    if f"/media/pages/assets/{asset_id}/" not in urlsplit(links[0]).path:
        raise ResourceError("Download link does not belong to the selected pack.")
    asset = basic(asset_id, page.headers[0] if page.headers else asset_id, page.meta.get("og:image"))
    asset["license"]["url"] = license_links[0]
    asset["variants"] = [{"key": unquote(urlsplit(links[0]).path.rsplit("/", 1)[-1]), "url": links[0], "extension": "zip"}]
    return asset


def previews(client, manifest, output):
    doc = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if doc.get("provider") != PROVIDER or doc.get("schema_version") != 1:
        raise ResourceError("Use a Kenney selection manifest.")
    root = Path(output)
    if root.exists():
        raise ResourceError("Preview directory already exists; reuse its images or choose a new directory.")
    rows = doc.get("results", [])
    if len(rows) > 20:
        raise ResourceError("Preview at most 20 saved options at once.")
    plans = []
    for row in rows:
        asset_id = valid_id(row["id"])
        url = row.get("thumbnail")
        if not url:
            url = inspect(client, asset_id).get("thumbnail")
        if url:
            checked_url(url, HOSTS)
            if f"/media/pages/assets/{asset_id}/" not in urlsplit(url).path:
                raise ResourceError("Preview does not belong to the selected pack.")
            extension = Path(urlsplit(url).path).suffix.lstrip(".").lower()
            if extension not in ("png", "jpg", "jpeg", "webp"):
                raise ResourceError("Unsupported preview format.")
            plans.append((row, {"url": url, "extension": extension}))
    root.mkdir(parents=True)
    downloaded = []
    for row, entry in plans:
        target = root / f"{int(row['option'])}-{row['id']}.{entry['extension']}"
        file = fetch_file(client, entry, target, 4)
        file["path"] = target.as_posix()
        downloaded.append({"option": row["option"], "id": row["id"], **file})
    write_json(root / "previews.json", downloaded)
    return {"previews": downloaded}


def extract_selected(archive, members, output):
    inventory = zip_inventory(archive)
    available = {r["path"] for r in inventory if not r["directory"]}
    chosen = set(members)
    if not chosen or not chosen <= available:
        raise ResourceError("Choose exact file paths listed by the archive command.")
    chosen |= {name for name in available if re.search(r"(?:^|/)(?:licen[cs]e|copying)(?:\.[a-z]+)?$", name, re.I)}
    dest = Path(output).resolve()
    if dest.exists():
        raise ResourceError("Extraction directory already exists; choose a new directory.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(dir=dest.parent, prefix=".kenney-")).resolve()
    files = []
    try:
        with zipfile.ZipFile(archive) as z:
            for name in sorted(chosen):
                safe_member(name)
                target = stage / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(name) as source, target.open("xb") as out:
                    shutil.copyfileobj(source, out)
                with target.open("rb") as f:
                    digest = hashlib.file_digest(f, "sha256").hexdigest()
                files.append({"path": name, "bytes": target.stat().st_size, "sha256": digest})
        with Path(archive).open("rb") as f:
            digest = hashlib.file_digest(f, "sha256").hexdigest()
        receipt = {"provider": PROVIDER, "archive": str(archive), "archive_sha256": digest, "files": files}
        if (stage / "extraction.json").exists():
            raise ResourceError("Selected member conflicts with the extraction receipt.")
        write_json(stage / "extraction.json", receipt)
        stage.rename(dest)
        return {"output_dir": str(dest), **receipt}
    finally:
        if stage.exists() and stage.parent == dest.parent and stage.name.startswith(".kenney-"):
            shutil.rmtree(stage)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("search")
    s.add_argument("--query", required=True)
    s.add_argument("--category", choices=["2D", "3D", "UI", "Audio", "Pixel", "Textures"])
    s.add_argument("--page", type=int, default=1)
    s.add_argument("--limit", type=int, default=6)
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
            s.add_argument("--output", required=True)
            s.add_argument("--max-mib", type=float, default=512)
    s = sub.add_parser("archive")
    s.add_argument("--zip", required=True)
    s.add_argument("--out", required=True)
    s = sub.add_parser("extract")
    s.add_argument("--zip", required=True)
    s.add_argument("--member", action="append", required=True)
    s.add_argument("--output-dir", required=True)
    return p


def run(args, client=None):
    if args.command == "archive":
        result = {"archive": args.zip, "members": zip_inventory(args.zip)}
        write_json(args.out, result)
        return result
    if args.command == "extract":
        return extract_selected(args.zip, args.member, args.output_dir)
    client = client or Client(HOSTS, "KenneyAssetSkill")
    if args.command == "previews":
        return previews(client, args.manifest, args.output_dir)
    if args.command == "search":
        if not args.query.strip() or not 1 <= args.limit <= 20 or args.page < 1:
            raise ResourceError("Use a nonempty query, --limit 1-20 and positive page.")
        text = client.data(BASE + "/assets", {"search": args.query.strip(), "category": args.category, "page": args.page}, text=True)
        rows = search_rows(text)
        return save_results(PROVIDER, rows[:args.limit], args.out, args.html, query=args.query, category=args.category, page=args.page, fetched=len(rows), total="unknown; catalog page window")
    asset = inspect(client, selection(args, PROVIDER))
    if args.command == "inspect":
        write_json(args.out, asset)
        return asset
    entry = asset["variants"][0]
    return download_one(client, PROVIDER, asset, entry["key"], entry, args.output, args.max_mib)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        print(json.dumps(summarize(run(parser().parse_args())), ensure_ascii=False, indent=2))
    except (ResourceError, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
