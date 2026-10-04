#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Compare published changed gallery resources with the exact release Git blobs."""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
BASE = "0d4ff8be7b03d18e0a4e44dee5285ed6c3bff19b"
PUBLIC = "https://gvillarroel.github.io/skills/"


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout


def load_builder(expected_ref: str) -> tuple[dict[str, object], dict[str, dict[str, str]], str]:
    """Load the exact committed builder without running its build entry point."""
    source = git("show", f"{expected_ref}:scripts/build-pages.py")
    filename = ROOT / "scripts/build-pages.py"
    namespace = {"__name__": "publication_builder", "__file__": str(filename)}
    exec(compile(source, str(filename), "exec"), namespace)
    tree = ast.parse(source)
    build = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build_docs")
    patches: dict[str, dict[str, str]] = {}
    for call in ast.walk(build):
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != "patch_file":
            continue
        target = eval(compile(ast.Expression(call.args[0]), str(filename), "eval"), namespace)
        replacements = ast.literal_eval(call.args[1])
        if not isinstance(replacements, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in replacements.items()):
            raise ValueError("Pages replacements are not literal text mappings.")
        patches[target.relative_to(namespace["PAGES_ROOT"]).as_posix()] = replacements
    return namespace, patches, hashlib.sha256(source).hexdigest()


def expected_resource(expected_ref: str, source: str, builder: dict[str, object], patches: dict[str, dict[str, str]]) -> bytes:
    """Replay committed CDN/metadata/normalization steps on committed source bytes."""
    if "/assets/examples/" not in source or source.startswith("/") or ".." in Path(source).parts:
        raise ValueError("Expected source must be an in-repository example resource.")
    tail = source.split("/assets/examples/", 1)[1]
    route = "examples/" + tail
    expected = git("show", f"{expected_ref}:{source}")
    suffix = Path(source).suffix.lower()
    if suffix not in builder["TEXT_SUFFIXES"]:
        return expected
    content = expected.decode("utf-8")
    for before, after in patches.get(route, {}).items():
        content = content.replace(before, after)
    card = next((card for card in builder["PUBLISHED_EXAMPLE_SETS"] if route == card["href"] + "index.html"), None)
    if card:
        content = builder["ensure_html_head_meta"](content, card["id"])
        content = builder["ensure_html_favicon"](content)
        for name, value in {"data-example-id": card["id"], "data-pattern-id": card["id"], "data-pattern-page": "true"}.items():
            content = builder["ensure_body_attribute"](content, name, value)
    scratch = ROOT / "projects/colorset-priority/artifacts/expected-pages"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        temporary = Path(directory) / Path(source).name
        temporary.write_text(content, encoding="utf-8", newline="\n")
        builder["normalize_text_file"](temporary)
        return temporary.read_bytes()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-ref", required=True)
    parser.add_argument("--emit-expected", metavar="SOURCE", help="Write one exact transformed Git resource to stdout without performing HTTP checks.")
    args = parser.parse_args()
    expected_ref = git("rev-parse", args.expected_ref).decode().strip()
    if git("rev-parse", "HEAD").decode().strip() != expected_ref:
        raise ValueError("The working checkout is not the requested release commit.")
    builder, patches, builder_sha = load_builder(expected_ref)
    if args.emit_expected:
        import sys
        sys.stdout.buffer.write(expected_resource(expected_ref, args.emit_expected, builder, patches))
        return 0
    names = git("diff", "--name-only", "-z", BASE, expected_ref).decode().split("\0")
    resources = []
    for name in names:
        if not name or "/assets/examples/" not in name:
            continue
        tail = name.split("/assets/examples/", 1)[1]
        target = ROOT / "dist/pages/examples" / tail
        if not target.is_file():
            continue
        expected = expected_resource(expected_ref, name, builder, patches)
        resources.append((name, "examples/" + tail, expected))
    if not resources:
        raise ValueError("No changed published resources found.")

    def verify(resource: tuple[str, str, bytes]) -> dict[str, object]:
        source, route, expected = resource
        url = PUBLIC + route
        request = urllib.request.Request(url + "?release=" + expected_ref, headers={"User-Agent": "CS1-priority-release-verifier"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                observed = response.read()
            return {"source": source, "url": url, "ok": observed == expected, "expectedSha256": hashlib.sha256(expected).hexdigest(), "publishedSha256": hashlib.sha256(observed).hexdigest(), "sizeBytes": len(observed)}
        except Exception as error:
            return {"source": source, "url": url, "ok": False, "error": str(error)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        rows = list(executor.map(verify, resources))
    findings = [row for row in rows if not row["ok"]]
    result = {"ok": not findings, "expectedRef": expected_ref, "baseline": BASE, "builderSha256": builder_sha, "method": "Exact Git source with exact committed Pages CDN, catalog metadata, favicon, body metadata and text normalization transformations; no working draft is used as expected output.", "checkedResources": len(rows), "findings": findings, "resources": rows}
    path = ROOT / "projects/colorset-priority/artifacts/manifests/publication.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k != "resources"}, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
