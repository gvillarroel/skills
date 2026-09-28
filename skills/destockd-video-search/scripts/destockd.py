#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search public Destockd endpoints and download one identity-bound video shot."""

from __future__ import annotations

import argparse
import hashlib
import html
from http.client import HTTPException
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE = "https://www.destockd.com"
SITE_HOSTS = {"www.destockd.com", "destockd.com"}
MEDIA_HOSTS = SITE_HOSTS | {"clips.destockd.com"}
RIGHTS_URL = BASE + "/#/legal"


class DestockdError(Exception):
    """A user-facing retrieval, selection or validation failure."""


def now():
    return datetime.now(timezone.utc).isoformat()


def public_url(value, media=False):
    if not isinstance(value, str) or not value:
        raise DestockdError("Missing public resource URL.")
    url = urljoin(BASE + "/", value)
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.hostname not in (MEDIA_HOSTS if media else SITE_HOSTS)
            or parts.username or parts.password or parts.port not in (None, 443)):
        raise DestockdError("Unexpected resource origin; inspect the current website contract.")
    return url


class PublicRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl, media=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Client:
    def __init__(self):
        self.opener = build_opener(PublicRedirects())

    def open(self, url, media=False):
        url = public_url(url, media=media)
        for attempt in range(3):
            try:
                response = self.opener.open(Request(url, headers={
                    "User-Agent": "DestockdSkill/1.0 (public footage discovery)",
                    "Accept": "*/*" if media else "application/json",
                    "Accept-Encoding": "identity",
                }), timeout=40)
                public_url(response.url, media=media)
                return response
            except HTTPError as exc:
                retry = exc.code == 429 or 500 <= exc.code < 600
                header = exc.headers.get("Retry-After", "")
                delay = min(2 ** attempt, 4)
                if header:
                    if not header.isdigit() or int(header) > 5:
                        retry = False
                    else:
                        delay = max(delay, int(header))
                exc.close()
                if not retry or attempt == 2:
                    raise DestockdError(f"HTTP {exc.code} retrieving {url}; no alternate shot was selected.") from exc
                time.sleep(delay)
            except (URLError, TimeoutError) as exc:
                if attempt == 2:
                    raise DestockdError(f"Could not retrieve {url}: {exc}") from exc
                time.sleep(2 ** attempt)

    def get(self, path, **params):
        url = BASE + "/api/" + path
        if params:
            url += "?" + urlencode(params)
        with self.open(url) as response:
            raw = response.read(8 * 1024 * 1024 + 1)
        if len(raw) > 8 * 1024 * 1024:
            raise DestockdError("Unexpectedly large metadata response.")
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise DestockdError("Expected JSON from Destockd; use the browser if the endpoint changed.") from exc
        if not isinstance(data, dict):
            raise DestockdError("Unexpected metadata shape.")
        return data


def rows(data, field):
    value = data.get(field)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise DestockdError(f"Response is missing a valid {field} array.")
    return value


def identity(film, shot):
    if not isinstance(film, str) or not film.strip() or not isinstance(shot, str) or not shot.strip():
        raise DestockdError("A non-empty film and shot identity is required.")
    return film, shot


def stable_id(film, shot):
    return "dsk-" + hashlib.sha256(json.dumps([film, shot], ensure_ascii=False).encode()).hexdigest()[:16]


def shot_path(film, shot):
    return quote(film, safe="") + "/" + quote(shot, safe="")


def normalize(row):
    film, shot = identity(row.get("film"), row.get("shot"))
    result = {
        "id": stable_id(film, shot), "film": film, "shot": shot,
        "page_url": BASE + "/#/shot/" + shot_path(film, shot),
        "color_type": row.get("color_type"), "visual_verified": False,
    }
    for key in ("keyframe", "preview", "clip"):
        result[key] = public_url(row[key], media=True) if row.get(key) else None
    for key in ("archive_url", "national_archives_url", "prev_shot", "next_shot"):
        if key in row:
            result[key] = row[key]
    return result


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gallery(document, path):
    def escape(value):
        return html.escape(str(value or ""), quote=True)

    cards = []
    for row in document["results"]:
        poster = escape(row.get("keyframe"))
        preview = escape(row.get("preview"))
        if preview:
            media = f'<video controls preload="none" poster="{poster}" src="{preview}"></video>'
        else:
            media = f'<img loading="lazy" src="{poster}" alt="Candidate keyframe">'
        cards.append(f'''<article id="{escape(row['id'])}" data-shot-id="{escape(row['id'])}">
<h2>Option {row['option']} · {escape(row['shot'])}</h2>{media}
<h3>{escape(row['film'])}</h3><p>{escape(row.get('color_type') or 'Color unknown')} · Visual match unverified</p>
<p><code>{escape(row['id'])}</code></p>
<a href="{escape(row['page_url'])}" target="_blank" rel="noopener noreferrer">Open shot and download</a>
</article>''')
    body = "\n".join(cards) or '<p>No candidates in the fetched result window.</p>'
    output = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Destockd video options</title><style>
body{font:16px/1.5 system-ui,sans-serif;background:#101923;color:#eff4f8;margin:0;padding:24px}
main{max-width:1200px;margin:auto}header{margin-bottom:28px}h1{font-size:32px;margin:0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:20px}
article{background:#1d2a38;border:1px solid #4a6175;padding:18px;border-radius:12px;overflow-wrap:anywhere}
video,img{display:block;width:100%;aspect-ratio:4/3;object-fit:contain;background:#080c10}
h2{font-size:19px}h3{font-size:17px}a{color:#8cdaff}code{font-size:13px}p{color:#d3e0eb}
</style><main><header><h1>Destockd video options</h1>
<p>Preview candidates, then use the saved option number to request a download.
Each number identifies one film and shot. Playback loads a preview; the downloader saves the full clip.</p>
<p>''' + escape(document["retrieved_at"]) + '</p></header><section class="grid">' + body + '</section></main></html>'
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")


def save_results(args, items, retrieval, **extra):
    selected = []
    seen = set()
    for row in items:
        if args.color and row.get("color_type") != args.color:
            continue
        if args.film_contains and args.film_contains.casefold() not in row["film"].casefold():
            continue
        if row["id"] in seen:
            continue
        seen.add(row["id"])
        selected.append({**row, "option": len(selected) + 1})
        if len(selected) == args.limit:
            break
    document = {
        "schema_version": 1, "retrieved_at": now(), "mode": args.command,
        "retrieval": {**retrieval, "filters_applied_locally": {
            "color": args.color, "film_contains": args.film_contains}, "returned": len(selected)},
        "rights_information": RIGHTS_URL, "results": selected, **extra,
    }
    write_json(args.out, document)
    if args.html:
        gallery(document, args.html)
    return {"manifest": str(Path(args.out).resolve()),
            "gallery": str(Path(args.html).resolve()) if args.html else None,
            "results": [{k: row[k] for k in ("option", "id", "film", "shot", "page_url", "color_type")}
                        for row in selected], "retrieval": document["retrieval"]}


def discover(args, client):
    if args.command == "search":
        queries = list(dict.fromkeys(q.strip() for q in args.query if q.strip()))
        if not 1 <= len(queries) <= 3:
            raise DestockdError("Provide one to three non-empty visual queries.")
        records, pages = {}, []
        for query in queries:
            rank = 0
            query_seen = set()
            for page in range(1, args.pages + 1):
                data = client.get("search", q=query, page=page)
                found = rows(data, "results")
                pages.append({"query": query, "page": page, "total": data.get("total"),
                              "fetched": len(found), "has_more": data.get("has_more")})
                for raw in found:
                    rank += 1
                    row = normalize(raw)
                    key = row["id"]
                    if key in query_seen:
                        continue
                    query_seen.add(key)
                    if key not in records:
                        records[key] = {**row, "query_matches": [], "rank_fusion": 0.0}
                    records[key]["query_matches"].append({"query": query, "rank": rank, "score": raw.get("score")})
                    records[key]["rank_fusion"] += 1 / (60 + rank)
                if not data.get("has_more") or not found:
                    break
        items = sorted(records.values(), key=lambda r: -r["rank_fusion"])
        return save_results(args, items, {"queries": queries, "pages": pages,
                                        "unique_candidates": len(items), "ranking": "reciprocal_rank_fusion_k60"})
    if args.command == "collection":
        found, pages = [], []
        for page in range(1, args.pages + 1):
            data = client.get("collections/" + quote(args.slug, safe=""), page=page)
            batch = rows(data, "results")
            found.extend(batch)
            pages.append({"page": page, "fetched": len(batch), "has_more": data.get("has_more")})
            if not data.get("has_more") or not batch:
                break
        return save_results(args, [normalize(r) for r in found], {"slug": args.slug, "pages": pages})
    if args.command == "film":
        data = client.get("film/" + quote(args.film, safe=""))
        if data.get("film") != args.film:
            raise DestockdError("Film response identity did not match the requested film.")
        return save_results(args, [normalize(r) for r in rows(data, "shots")],
                            {"film": args.film, "shot_count": data.get("shot_count")},
                            archive_url=data.get("archive_url"), national_archives_url=data.get("national_archives_url"))
    if args.command == "similar":
        film, shot = identity(args.film, args.shot)
        data = client.get("similar/" + shot_path(film, shot))
        return save_results(args, [normalize(r) for r in rows(data, "results")], {"seed": {"film": film, "shot": shot}})
    if args.command == "collections":
        data = client.get("collections")
        entries = [{k: row.get(k) for k in ("name", "slug", "description", "shot_count")}
                   for row in rows(data, "collections")]
        value = {"retrieved_at": now(), "collections": entries}
    else:
        entries, pages = [], []
        for page in range(1, 21):
            data = client.get("films", page=page, per_page=1000)
            batch = rows(data, "films")
            entries.extend(batch)
            pages.append({"page": page, "fetched": len(batch), "has_more": data.get("has_more")})
            if not data.get("has_more") or not batch:
                break
        matches = [{"film": row["film"], "shot_count": row.get("shot_count"),
                    "page_url": BASE + "/#/film/" + quote(row["film"], safe="")}
                   for row in entries if args.query.casefold() in row.get("film", "").casefold()]
        value = {"retrieved_at": now(), "query": args.query, "fetched": len(entries),
                 "pages": pages, "films": matches}
    write_json(args.out, value)
    return value


def resolve_selection(args):
    if args.url:
        if args.manifest or args.id or args.option is not None:
            raise DestockdError("Use a shot URL or a manifest selector, not both.")
        parts = urlsplit(public_url(args.url))
        components = parts.fragment.strip("/").split("/")
        if len(components) != 3 or components[0] != "shot":
            raise DestockdError("Expected a Destockd #/shot/<film>/<shot> URL.")
        return identity(unquote(components[1]), unquote(components[2]))
    if not args.manifest or (bool(args.id) + (args.option is not None)) != 1:
        raise DestockdError("Provide --manifest and exactly one --id or --option, or a shot --url.")
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8-sig"))
    if data.get("schema_version") != 1:
        raise DestockdError("Unsupported selection manifest version.")
    found = [row for row in rows(data, "results") if
             (row.get("id") == args.id if args.id else row.get("option") == args.option)]
    if len(found) != 1:
        raise DestockdError("Selection is missing or ambiguous in the saved list.")
    film, shot = identity(found[0].get("film"), found[0].get("shot"))
    if found[0].get("id") != stable_id(film, shot):
        raise DestockdError("Saved identity does not match its stable ID.")
    return film, shot


def refresh(client, film, shot):
    data = client.get("shot/" + shot_path(film, shot))
    if identity(data.get("film"), data.get("shot")) != (film, shot):
        raise DestockdError("Refreshed shot identity changed; refusing to substitute footage.")
    return normalize(data)


def probe(path):
    executable = shutil.which("ffprobe")
    if not executable:
        return {"verification": "mp4_signature_and_transfer_only", "duration_seconds": None,
                "width": None, "height": None, "has_audio_stream": None}
    result = subprocess.run([executable, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                            capture_output=True, text=True, timeout=60, check=False)
    if result.returncode:
        raise DestockdError("Downloaded media failed ffprobe validation.")
    data = json.loads(result.stdout)
    videos = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    if not videos or not videos[0].get("width") or not videos[0].get("height"):
        raise DestockdError("Downloaded MP4 has no readable video stream.")
    video = videos[0]
    duration = data.get("format", {}).get("duration")
    return {"verification": "ffprobe_video_stream", "duration_seconds": float(duration) if duration else None,
            "width": video.get("width"), "height": video.get("height"),
            "codec": video.get("codec_name"), "frame_rate": video.get("avg_frame_rate"),
            "has_audio_stream": any(s.get("codec_type") == "audio" for s in data.get("streams", []))}


def download(client, row, output, max_mib):
    output = Path(output).resolve()
    receipt_path = Path(str(output) + ".json")
    if output.suffix.lower() != ".mp4":
        raise DestockdError("Use an .mp4 output path.")
    if output.exists() or receipt_path.exists():
        raise DestockdError("Output or receipt already exists; choose a new path.")
    if not row.get("clip") or row["clip"] == row.get("preview"):
        raise DestockdError("Selected shot has no distinct full clip URL.")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    receipt_temp = None
    promoted = False
    try:
        with client.open(row["clip"], media=True) as response:
            if getattr(response, "status", 200) != 200:
                raise DestockdError("Expected a complete HTTP 200 video response.")
            content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
            if content_type not in ("video/mp4", "application/mp4", "application/octet-stream"):
                raise DestockdError("The download did not return MP4 media.")
            declared = response.headers.get("Content-Length")
            expected = int(declared) if declared else None
            maximum = max_mib * 1024 * 1024
            if expected is not None and (expected <= 0 or expected > maximum):
                raise DestockdError("Download length is empty or exceeds the configured size cap.")
            count, digest, prefix = 0, hashlib.sha256(), b""
            with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".destockd-", suffix=".part", delete=False) as file:
                temporary = Path(file.name)
                while chunk := response.read(1024 * 1024):
                    count += len(chunk)
                    if count > maximum:
                        raise DestockdError("Download exceeded the configured size cap.")
                    if len(prefix) < 32:
                        prefix = (prefix + chunk)[:32]
                    digest.update(chunk)
                    file.write(chunk)
                file.flush()
                os.fsync(file.fileno())
            if count < 16 or prefix[4:8] != b"ftyp":
                raise DestockdError("Downloaded bytes are not a supported MP4 container.")
            if expected is not None and count != expected:
                raise DestockdError("Incomplete download: byte count differs from Content-Length.")
            metadata = probe(temporary)
            receipt = {"schema_version": 1, "downloaded_at": now(), "output": str(output),
                       "bytes": count, "sha256": digest.hexdigest(), "download_url": response.url,
                       "shot": row, "media": metadata, "rights_information": RIGHTS_URL}
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".destockd-", suffix=".json.part", delete=False) as file:
            receipt_temp = Path(file.name)
            file.write((json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        # Hard links atomically create new names without replacing existing files.
        os.link(temporary, output)
        promoted = True
        os.link(receipt_temp, receipt_path)
        return {**receipt, "receipt": str(receipt_path)}
    except BaseException:
        if promoted:
            output.unlink(missing_ok=True)
        raise
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)
        if receipt_temp:
            receipt_temp.unlink(missing_ok=True)


def bounded(low, high):
    def parse(value):
        number = int(value)
        if not low <= number <= high:
            raise argparse.ArgumentTypeError(f"Value must be between {low} and {high}.")
        return number
    return parse


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("collections", "films", "search", "collection", "film", "similar"):
        p = commands.add_parser(name)
        p.add_argument("--out", required=True, help="Output JSON path in the active workspace.")
        if name in ("search", "collection", "film", "similar"):
            p.add_argument("--html", help="Optional HTML preview gallery path.")
            p.add_argument("--limit", type=bounded(1, 48), default=6)
            p.add_argument("--color", choices=("color", "bw"))
            p.add_argument("--film-contains", help="Local substring filter on fetched film titles.")
        if name in ("search", "collection"):
            p.add_argument("--pages", type=bounded(1, 3), default=1)
        if name == "search":
            p.add_argument("--query", action="append", required=True)
        if name == "films":
            p.add_argument("--query", default="")
        if name == "collection":
            p.add_argument("slug")
        if name in ("film", "similar"):
            p.add_argument("--film", required=True)
        if name == "similar":
            p.add_argument("--shot", required=True)
    for name in ("inspect", "download"):
        p = commands.add_parser(name)
        p.add_argument("--url", help="Actual Destockd shot page URL.")
        p.add_argument("--manifest")
        p.add_argument("--id")
        p.add_argument("--option", type=bounded(1, 48))
        if name == "inspect":
            p.add_argument("--out", required=True)
        else:
            p.add_argument("--output", required=True, help="Exact destination .mp4 path.")
            p.add_argument("--max-mib", type=bounded(1, 4096), default=512)
    return root


def main():
    args = parser().parse_args()
    try:
        if getattr(args, "html", None) and Path(args.html).resolve() == Path(args.out).resolve():
            raise DestockdError("JSON and HTML outputs must have different paths.")
        client = Client()
        if args.command in ("inspect", "download"):
            film, shot = resolve_selection(args)
            selected = refresh(client, film, shot)
            if args.command == "inspect":
                result = {"retrieved_at": now(), "shot": selected, "rights_information": RIGHTS_URL}
                write_json(args.out, result)
            else:
                result = download(client, selected, args.output, args.max_mib)
        else:
            result = discover(args, client)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (DestockdError, OSError, ValueError, KeyError, TypeError, HTTPException, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc), "command": args.command}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
