#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Compare published changed gallery resources with the exact release Git blobs."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
BASE = "0d4ff8be7b03d18e0a4e44dee5285ed6c3bff19b"
PUBLIC = "https://gvillarroel.github.io/skills/"


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-ref", required=True)
    args = parser.parse_args()
    expected_ref = git("rev-parse", args.expected_ref).decode().strip()
    if git("rev-parse", "HEAD").decode().strip() != expected_ref:
        raise ValueError("The working checkout is not the requested release commit.")
    names = git("diff", "--name-only", "-z", BASE, expected_ref).decode().split("\0")
    resources = []
    for name in names:
        if not name or "/assets/examples/" not in name:
            continue
        tail = name.split("/assets/examples/", 1)[1]
        target = ROOT / "dist/pages/examples" / tail
        if not target.is_file():
            continue
        expected = git("show", f"{expected_ref}:{name}")
        # The builder canonicalizes authored textual Pages resources.
        if target.suffix.lower() in {".html", ".css", ".js", ".mjs", ".svg", ".json", ".mmd", ".puml", ".md", ".txt"}:
            lines = [line.rstrip() for line in expected.decode("utf-8").splitlines()]
            while lines and not lines[-1]:
                lines.pop()
            expected = ("\n".join(lines) + "\n").encode()
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
    result = {"ok": not findings, "expectedRef": expected_ref, "baseline": BASE, "checkedResources": len(rows), "findings": findings, "resources": rows}
    path = ROOT / "projects/colorset-priority/artifacts/manifests/publication.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k != "resources"}, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
