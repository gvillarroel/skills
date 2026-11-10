#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect and replay a bounded Markdown corpus pinned to a GitHub commit."""

from argparse import ArgumentParser
from collections import deque
from hashlib import sha256
import json
import os
from pathlib import Path
import posixpath
import re
import stat
from tempfile import TemporaryDirectory
from urllib.error import URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


REPOSITORY = "github/docs"
DOCS = "https://docs.github.com"
SOURCE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
GITHUB_DOCS_PATH = re.compile(r"content/(?:[a-z0-9_-]+/)*[a-z0-9_-]+\.md")
REPO_PART = r"[A-Za-z0-9_][A-Za-z0-9_.-]*"
GITHUB_REPO = re.compile(rf"{REPO_PART}/{REPO_PART}")
MARKDOWN_SUFFIXES = (".md", ".markdown", ".mdx")
MARKDOWN_PATH = re.compile(rf"(?:{REPO_PART}/)*{REPO_PART}\.(?:md|markdown|mdx)")
HOST_LABEL = r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
HTTPS_ORIGIN = re.compile(rf"https://(?:{HOST_LABEL}\.)+[a-z](?:[a-z0-9-]*[a-z0-9])?")
PUBLISHER_PATH = re.compile(r"/(?:[A-Za-z0-9_.~-]+/)*[A-Za-z0-9_.~-]*")
LIQUID_DOCS_PREFIX = "{{site.url}}{{site.baseurl}}"
DIGEST = re.compile(r"[0-9a-f]{64}")
DEVICE_NAMES = {"con", "prn", "aux", "nul"} | {f"{prefix}{number}"
              for prefix in ("com", "lpt") for number in range(1, 10)}
FENCE = re.compile(r"^ {0,3}(?:>\s*)?(\x60{3,}|~{3,})(.*)$")
INLINE_IGNORABLE = re.compile(r"(?<!\x60)(\x60+)(?!\x60).*?(?<!\x60)\1(?!\x60)|<!--")
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


def route_key(path):
    return path.rstrip("/") or "/"


def publisher_routes(row):
    return [row["publisher_path"], *row.get("aliases", [])]


def valid_publisher_path(path):
    return (isinstance(path, str) and PUBLISHER_PATH.fullmatch(path)
            and all(part not in {".", ".."} for part in path.split("/")))


def check_publisher_routes(row, used_routes):
    if "publisher_path" not in row or not isinstance(row.get("aliases", []), list):
        raise ValueError("A version 2 source needs a publisher path and optional path aliases")
    for path in publisher_routes(row):
        if not valid_publisher_path(path):
            raise ValueError("Expected a plain absolute publisher path")
        key = route_key(path)
        if key in used_routes:
            raise ValueError(f"The approved publisher paths collide at {key}")
        used_routes.add(key)


def load_spec(path):
    raw = path.read_bytes()
    spec = json.loads(raw, object_pairs_hook=unique_fields)
    if not isinstance(spec, dict) or type(spec.get("version")) is not int:
        raise ValueError("The spec needs an integer version")
    version = spec["version"]
    expected_keys = SPEC_KEYS | ({"docs_origin"} if version == 2 else set())
    optional_keys = {"docs_base_path"} if version == 2 else set()
    if not expected_keys <= spec.keys() or spec.keys() - expected_keys - optional_keys:
        raise ValueError("The spec does not match the expected fields")
    if version == 1:
        if spec["repository"] != REPOSITORY:
            raise ValueError("Expected github/docs for spec version 1")
        source_pattern = GITHUB_DOCS_PATH
    elif version == 2:
        repo, origin = spec["repository"], spec["docs_origin"]
        if not isinstance(repo, str) or not GITHUB_REPO.fullmatch(repo):
            raise ValueError("Expected a GitHub repository in owner/name form")
        if not isinstance(origin, str) or not HTTPS_ORIGIN.fullmatch(origin):
            raise ValueError("Expected a canonical HTTPS documentation origin")
        if "docs_base_path" in spec:
            base = spec["docs_base_path"]
            if not valid_publisher_path(base) or base.endswith("/"):
                raise ValueError("Expected an absolute documentation base path without a trailing slash")
        source_pattern = MARKDOWN_PATH
    else:
        raise ValueError("Expected spec version 1 or 2")
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
    sources, paths, used_routes = {}, set(), set()
    row_keys = {"source_id", "source_path", "sha256"}
    if version == 2:
        row_keys.add("publisher_path")
    for row in rows:
        if (not isinstance(row, dict) or not row_keys <= row.keys()
                or row.keys() - row_keys - ({"aliases"} if version == 2 else set())):
            raise ValueError("An allowed source has missing or unexpected fields")
        name, source_path, digest = (row[k] for k in ("source_id", "source_path", "sha256"))
        if not (isinstance(name, str) and len(name) <= 80 and SOURCE_ID.fullmatch(name)
                and name not in DEVICE_NAMES
                and isinstance(source_path, str) and source_pattern.fullmatch(source_path)
                and isinstance(digest, str) and DIGEST.fullmatch(digest)):
            raise ValueError("Invalid allowed source ID, Markdown path or SHA-256")
        if name in sources or source_path in paths:
            raise ValueError("The allowlist repeats a source ID or path")
        if version == 2:
            check_publisher_routes(row, used_routes)
        sources[name] = row
        paths.add(source_path)
    seeds = spec["seeds"]
    if (not isinstance(seeds, list) or not seeds
            or any(not isinstance(seed, str) or seed not in sources for seed in seeds)
            or len(seeds) != len(set(seeds))):
        raise ValueError("The seeds must name distinct allowed sources")
    return spec, sources, sha256(raw).hexdigest()


def visible_markdown(line, in_comment):
    visible = []
    start = 0
    while start < len(line):
        if in_comment:
            end = line.find("-->", start)
            if end < 0:
                break
            start = end + 3
            in_comment = False
            continue
        skipped = INLINE_IGNORABLE.search(line, start)
        if skipped is None:
            visible.append(line[start:])
            break
        visible.extend((line[start:skipped.start()], " "))
        in_comment = skipped[0] == "<!--"
        start = skipped.end()
    return "".join(visible), in_comment


def markdown_targets(text):
    """Read inline Markdown destinations outside comments and code."""
    fence = ""
    in_comment = False
    for line in text.split("\n"):
        marker = FENCE.match(line)
        if fence:
            if marker and marker[1].startswith(fence) and not marker[2].strip():
                fence = ""
            continue
        if not in_comment and marker:
            fence = marker[1]
            continue
        if not in_comment and line.startswith(("    ", "\t")):
            continue
        visible, in_comment = visible_markdown(line, in_comment)
        for link in INLINE_LINK.finditer(visible):
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


def linked_repository_sources(text, origin, docs_base_path, source, route_ids, path_ids):
    publisher_url = origin + source["publisher_path"]
    host = urlsplit(origin).netloc
    for href in markdown_targets(text):
        if href.startswith(("#", "?")) or "\\" in href or any(ord(c) < 32 for c in href):
            continue
        if docs_base_path is not None and href.startswith(LIQUID_DOCS_PREFIX + "/"):
            href = origin + docs_base_path + href.removeprefix(LIQUID_DOCS_PREFIX)
        try:
            link = urlsplit(href)
            resolved = urlsplit(urljoin(publisher_url, href))
            if resolved.scheme != "https" or resolved.netloc.lower() != host:
                continue
            route = route_key(unquote(resolved.path, errors="strict"))
            raw_path = unquote(link.path, errors="strict")
        except ValueError:
            continue
        route_id = route_ids.get(route)
        path_id = None
        if not link.scheme and not link.netloc and raw_path.endswith(MARKDOWN_SUFFIXES):
            base_dir = posixpath.dirname(source["source_path"])
            path = (raw_path.lstrip("/") if raw_path.startswith("/")
                    else posixpath.normpath(posixpath.join(base_dir, raw_path)))
            path_id = path_ids.get(path)
        if path_id and route_id and path_id != route_id:
            raise ValueError(f"An approved link from {source['source_id']} has two destinations")
        if target := path_id or route_id:
            yield target


def canonical_manifest(spec, sources, spec_digest, fetch):
    """Walk the entire approved roster breadth first within the declared bounds."""
    github_docs = spec["version"] == 1
    if github_docs:
        route_ids = {normalized_route(source_route(row["source_path"])): name
                     for name, row in sources.items()}
        if len(route_ids) != len(sources):
            raise ValueError("The approved source paths collide as published routes")
    else:
        route_ids = {route_key(route): name for name, row in sources.items()
                     for route in publisher_routes(row)}
        path_ids = {row["source_path"]: name for name, row in sources.items()}
    seeds = sorted(spec["seeds"])
    queue = deque((name, 0, None) for name in seeds)
    queued = set(seeds)
    collected, edges, contents = {}, set(), {}
    revision = spec["revision"]
    repository = spec["repository"]
    raw_base = f"https://raw.githubusercontent.com/{repository}/{revision}"
    blob_base = f"https://github.com/{repository}/blob/{revision}"
    limit = spec["max_source_bytes"]
    while queue:
        name, depth, predecessor = queue.popleft()
        source = sources[name]
        path = source["source_path"]
        raw = fetch(name, f"{raw_base}/{path}", limit)
        digest = sha256(raw).hexdigest()
        if len(raw) > limit or digest != source["sha256"]:
            raise ValueError(f"Size or digest mismatch for {name}")
        text = raw.decode("utf-8-sig")
        if not text.strip() or "\x00" in text:
            raise ValueError(f"Expected a Markdown text source for {name}")
        contents[name] = raw
        if github_docs:
            route = source_route(path)
            publisher_url = f"{DOCS}/en{route}"
            children = linked_sources(text, route, route_ids)
        else:
            origin = spec["docs_origin"]
            publisher_url = origin + source["publisher_path"]
            children = linked_repository_sources(
                text, origin, spec.get("docs_base_path"), source, route_ids, path_ids
            )
        collected[name] = {
            "source_id": name, "path": f"sources/{name}.md", "source_path": path,
            "url": f"{blob_base}/{path}", "publisher_url": publisher_url,
            "revision": revision, "sha256": digest, "bytes": len(raw),
            "depth": depth, "discovered_from": predecessor,
        }
        for child in sorted(set(children) - {name}):
            edges.add((name, child))
            if child not in queued and depth < spec["max_depth"]:
                queue.append((child, depth + 1, name))
                queued.add(child)
    if missing := sorted(sources.keys() - collected.keys()):
        raise ValueError(f"Approved sources are unreachable within the bounds: {', '.join(missing)}")
    result = {
        "version": 1, "repository": repository, "revision": revision,
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
    with TemporaryDirectory(dir=output.parent, prefix=".feature-crawl-") as stage:
        staging = Path(stage)
        raw_sources = staging / "sources"
        raw_sources.mkdir()
        for name, raw in sorted(contents.items()):
            (raw_sources / f"{name}.md").write_bytes(raw)
        manifest_file = staging / "manifest.json"
        manifest_file.write_bytes(manifest)
        output.mkdir()
        destination = output / "sources"
        try:
            raw_sources.rename(destination)
            manifest_file.rename(output / "manifest.json")
        except OSError:
            if destination.exists():
                destination.rename(raw_sources)
            output.rmdir()
            raise


def is_link(path):
    return (path.is_symlink()
            or (os.name == "nt" and path.lstat().st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT))


def verify(output, spec, sources, spec_digest):
    raw_sources = output / "sources"
    manifest_file = output / "manifest.json"
    if (not output.is_dir() or is_link(output) or not raw_sources.is_dir() or is_link(raw_sources)
            or raw_sources.resolve().parent != output.resolve()
            or not manifest_file.is_file() or is_link(manifest_file)):
        raise ValueError("Expected a retained corpus directory and regular manifest")
    if {path.name for path in raw_sources.iterdir()} != {f"{name}.md" for name in sources}:
        raise ValueError("The retained source filenames differ from the approved roster")

    def local_fetch(name, url, limit):
        file = raw_sources / f"{name}.md"
        if not file.is_file() or file.resolve().parent != raw_sources.resolve() or is_link(file):
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
