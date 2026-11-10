#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect and replay a bounded official GitHub Docs Markdown corpus."""

from argparse import ArgumentParser
from collections import deque
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from urllib.error import URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


REPOSITORY = "github/docs"
DOCS = "https://docs.github.com"
RAW = f"https://raw.githubusercontent.com/{REPOSITORY}"
BLOB = f"https://github.com/{REPOSITORY}/blob"
SOURCE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SOURCE_PATH = re.compile(r"content/(?:[a-z0-9_-]+/)*[a-z0-9_-]+\.md")
DIGEST = re.compile(r"[0-9a-f]{64}")
DEVICE_NAMES = {"con", "prn", "aux", "nul"} | {f"{prefix}{number}"
              for prefix in ("com", "lpt") for number in range(1, 10)}
FENCE = re.compile(r"^ {0,3}(?:>\s*)?(\x60{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(?<!\x60)(\x60+)(?!\x60).*?(?<!\x60)\1(?!\x60)")
INLINE_LINK = re.compile(
    r"(?<![\\!])\[[^\]\n]*\]\([ \t]*(?:<([^<>\s]+)>|([^()\s]+))"
    r"""(?:[ \t]+(?:"[^"\n]*"|'[^'\n]*'|\([^\n)]*\)))?[ \t]*\)"""
)
SPEC_KEYS = {"version", "repository", "revision", "max_depth", "max_sources",
             "max_source_bytes", "seeds", "allowlist"}


def unique_fields(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("The spec contains a duplicate JSON field")
    return result


def valid_bound(value, lower, upper):
    return type(value) is int and lower <= value <= upper


def load_spec(path):
    raw = path.read_bytes()
    spec = json.loads(raw, object_pairs_hook=unique_fields)
    if not isinstance(spec, dict) or spec.keys() != SPEC_KEYS:
        raise ValueError("The spec does not match the expected fields")
    if type(spec["version"]) is not int or spec["version"] != 1 or spec["repository"] != REPOSITORY:
        raise ValueError("Expected spec version 1 for github/docs")
    revision = spec["revision"]
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("The revision must be a full lowercase commit SHA")
    if not (valid_bound(spec["max_depth"], 0, 12)
            and valid_bound(spec["max_sources"], 1, 64)
            and valid_bound(spec["max_source_bytes"], 1, 1_048_576)):
        raise ValueError("The crawl bounds are outside the supported range")
    rows = spec["allowlist"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= spec["max_sources"]:
        raise ValueError("The allowlist must fit within the source count bound")
    sources, paths = {}, set()
    for row in rows:
        if not isinstance(row, dict) or row.keys() != {"source_id", "source_path", "sha256"}:
            raise ValueError("Each allowed source needs source_id, source_path and sha256")
        name, source_path, digest = (row[k] for k in ("source_id", "source_path", "sha256"))
        if not (isinstance(name, str) and len(name) <= 80 and SOURCE_ID.fullmatch(name)
                and name not in DEVICE_NAMES
                and isinstance(source_path, str) and SOURCE_PATH.fullmatch(source_path)
                and isinstance(digest, str) and DIGEST.fullmatch(digest)):
            raise ValueError("Invalid allowed source ID, Markdown path or SHA-256")
        if name in sources or source_path in paths:
            raise ValueError("The allowlist repeats a source ID or path")
        sources[name] = row
        paths.add(source_path)
    seeds = spec["seeds"]
    if (not isinstance(seeds, list) or not seeds
            or any(not isinstance(seed, str) or seed not in sources for seed in seeds)
            or len(seeds) != len(set(seeds))):
        raise ValueError("The seeds must name distinct allowed sources")
    return spec, sources, sha256(raw).hexdigest()


def markdown_targets(text):
    """Read inline Markdown destinations outside comments and code."""
    text = re.sub(r"<!--.*?(?:-->|\Z)", "", text, flags=re.DOTALL)
    fence = ""
    for line in text.split("\n"):
        marker = FENCE.match(line)
        if fence:
            if marker and marker[1].startswith(fence) and not marker[2].strip():
                fence = ""
            continue
        if marker:
            fence = marker[1]
            continue
        if line.startswith(("    ", "\t")):
            continue
        for link in INLINE_LINK.finditer(INLINE_CODE.sub(" ", line)):
            yield link[1] or link[2]


def source_route(source_path):
    stem = source_path.removeprefix("content").removesuffix(".md")
    return stem.removesuffix("index") if stem.endswith("/index") else stem


def normalized_route(path):
    path = path.removeprefix("/en/").lstrip("/")
    path = "/" + path.removeprefix("content/").removesuffix(".md")
    path = path.removesuffix("/index").rstrip("/")
    return path or "/"


def linked_sources(text, base_route, route_ids):
    for href in markdown_targets(text):
        if href.startswith(("#", "?")) or "\\" in href or any(ord(c) < 32 for c in href):
            continue
        try:
            resolved = urlsplit(urljoin(DOCS + base_route, href))
            if resolved.scheme != "https" or resolved.netloc.lower() != "docs.github.com":
                continue
            target = normalized_route(unquote(resolved.path, errors="strict"))
        except ValueError:
            continue
        if target in route_ids:
            yield route_ids[target]


def canonical_manifest(spec, sources, spec_digest, fetch):
    """Walk the entire approved roster breadth first within the declared bounds."""
    route_ids = {normalized_route(source_route(row["source_path"])): name
                 for name, row in sources.items()}
    if len(route_ids) != len(sources):
        raise ValueError("The approved source paths collide as published routes")
    seeds = sorted(spec["seeds"])
    queue = deque((name, 0, None) for name in seeds)
    queued = set(seeds)
    collected, edges, contents = {}, set(), {}
    revision = spec["revision"]
    limit = spec["max_source_bytes"]
    while queue:
        name, depth, predecessor = queue.popleft()
        source = sources[name]
        path = source["source_path"]
        raw = fetch(name, f"{RAW}/{revision}/{path}", limit)
        digest = sha256(raw).hexdigest()
        if len(raw) > limit or digest != source["sha256"]:
            raise ValueError(f"Size or digest mismatch for {name}")
        text = raw.decode("utf-8-sig")
        if not text.strip() or "\x00" in text:
            raise ValueError(f"Expected a Markdown text source for {name}")
        contents[name] = raw
        route = source_route(path)
        collected[name] = {
            "source_id": name, "path": f"sources/{name}.md", "source_path": path,
            "url": f"{BLOB}/{revision}/{path}", "publisher_url": f"{DOCS}/en{route}",
            "revision": revision, "sha256": digest, "bytes": len(raw),
            "depth": depth, "discovered_from": predecessor,
        }
        for child in sorted(set(linked_sources(text, route, route_ids)) - {name}):
            edges.add((name, child))
            if child not in queued and depth < spec["max_depth"]:
                queue.append((child, depth + 1, name))
                queued.add(child)
    if missing := sorted(sources.keys() - collected.keys()):
        raise ValueError(f"Approved sources are unreachable within the bounds: {', '.join(missing)}")
    result = {
        "version": 1, "repository": REPOSITORY, "revision": revision,
        "spec_sha256": spec_digest, "seeds": seeds,
        "bounds": {key: spec[key] for key in ("max_depth", "max_sources", "max_source_bytes")},
        "sources": [collected[name] for name in sorted(collected)],
        "links": [{"from": left, "to": right} for left, right in sorted(edges)],
    }
    manifest = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return manifest, contents


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def online_fetch(name, url, limit):
    request = Request(url, headers={"User-Agent": "product-feature-inventory-crawl/1"})
    try:
        with build_opener(NoRedirect()).open(request, timeout=30) as response:
            return response.read(limit + 1)
    except (URLError, TimeoutError) as error:
        raise ValueError(f"Could not fetch pinned source {name}: {error}") from error


def crawl(output, spec, sources, spec_digest):
    if os.path.lexists(output):
        raise ValueError("The crawl output must be a new directory")
    manifest, contents = canonical_manifest(spec, sources, spec_digest, online_fetch)
    output.mkdir()
    with TemporaryDirectory(dir=output, prefix=".feature-crawl-") as stage:
        staging = Path(stage)
        raw_sources = staging / "sources"
        raw_sources.mkdir()
        for name, raw in sorted(contents.items()):
            (raw_sources / f"{name}.md").write_bytes(raw)
        manifest_file = staging / "manifest.json"
        manifest_file.write_bytes(manifest)
        raw_sources.rename(output / "sources")
        manifest_file.rename(output / "manifest.json")


def verify(output, spec, sources, spec_digest):
    raw_sources = output / "sources"
    manifest_file = output / "manifest.json"
    if (not output.is_dir() or output.is_symlink() or not raw_sources.is_dir()
            or raw_sources.resolve().parent != output.resolve()
            or not manifest_file.is_file() or manifest_file.is_symlink()):
        raise ValueError("Expected a retained corpus directory and regular manifest")
    if {path.name for path in raw_sources.iterdir()} != {f"{name}.md" for name in sources}:
        raise ValueError("The retained source filenames differ from the approved roster")

    def local_fetch(name, url, limit):
        file = raw_sources / f"{name}.md"
        if not file.is_file() or file.resolve().parent != raw_sources.resolve() or file.is_symlink():
            raise ValueError(f"Expected a regular retained source file for {name}")
        with file.open("rb") as handle:
            return handle.read(limit + 1)

    manifest, _ = canonical_manifest(spec, sources, spec_digest, local_fetch)
    if manifest_file.read_bytes() != manifest:
        raise ValueError("The retained manifest does not match the replayed crawl")


def main(argv=None):
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("crawl", "verify"))
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        spec, sources, digest = load_spec(args.spec)
        operation = crawl if args.action == "crawl" else verify
        operation(args.output, spec, sources, digest)
    except (OSError, ValueError) as error:
        parser.exit(2, f"{error}\n")
    print(f"{args.action}: {len(sources)} pinned Markdown sources at {spec['revision']}")


if __name__ == "__main__":
    main()
