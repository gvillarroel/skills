#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Publish the exact authorized local preview commit through GitHub Git Data API.

One-off fallback for receive-pack server errors. No force updates or credentials.
Run from the repository root; requires the already authenticated gh CLI.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


REPO = "gvillarroel/skills"
BRANCH = "main"
COMMIT = "a52e2b58982fe72797e335d7840ce1d65e4f2f1a"
PREFIXES = ("skills/lucidchart-svg/", "evaluations/lucidchart-svg/",
            "evaluations/pi-prompts/lucidchart-svg-", "projects/lucid-svg-fidelity/reviews/")
FILES = {"SKILLS.md", "evaluations/colorset-audit/coverage.json"}


def run(args: list[str], data: bytes | None = None) -> bytes:
    result = subprocess.run(args, input=data, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(args[:5])}")
    return result.stdout


def git(*args: str) -> str:
    return run(["git", *args]).decode("utf-8").strip()


def api(endpoint: str, body: dict | None = None, method: str | None = None) -> dict:
    args = ["gh", "api", f"repos/{REPO}/{endpoint}"]
    if body is not None:
        args += ["--method", method or "POST", "--input", "-"]
    return json.loads(run(args, json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None))


def main() -> None:
    assert git("rev-parse", "HEAD") == COMMIT, "Local HEAD changed; reassess before publishing"
    parent = git("rev-parse", f"{COMMIT}^")
    expected_tree = git("rev-parse", f"{COMMIT}^{{tree}}")
    remote = api(f"git/ref/heads/{BRANCH}")["object"]["sha"]
    if remote == COMMIT:
        print(json.dumps({"published": True, "commit": COMMIT, "already_published": True}))
        return
    assert remote == parent, "Remote branch changed; reassess before publishing"
    base_tree = api(f"git/commits/{parent}")["tree"]["sha"]
    entries = []
    for line in git("diff-tree", "--no-commit-id", "--name-status", "-r", COMMIT).splitlines():
        status, path = line.split("\t", 1)
        assert status in ("A", "M"), "This preview may only add or modify reviewed files"
        assert path in FILES or path.startswith(PREFIXES), f"Unexpected publication path: {path}"
        record = git("ls-tree", COMMIT, "--", path).split("\t", 1)[0].split()
        assert record[0] == "100644" and record[1] == "blob"
        content = run(["git", "show", f"{COMMIT}:{path}"]).decode("utf-8")
        entries.append({"path": path, "mode": record[0], "type": "blob", "content": content})
    assert len(entries) == 26, "Reviewed publication inventory changed"
    tree = api("git/trees", {"base_tree": base_tree, "tree": entries})["sha"]
    assert tree == expected_tree, "Remote tree differs from the reviewed local tree"
    fields = run(["git", "show", "-s", "--format=%an%x00%ae%x00%aI%x00%cn%x00%ce%x00%cI", COMMIT]).decode("utf-8").strip().split("\0")
    assert len(fields) == 6
    message = run(["git", "cat-file", "commit", COMMIT]).split(b"\n\n", 1)[1].decode("utf-8")
    body = {"message": message, "tree": tree, "parents": [parent],
            "author": dict(zip(("name", "email", "date"), fields[:3])),
            "committer": dict(zip(("name", "email", "date"), fields[3:]))}
    created = api("git/commits", body)["sha"]
    assert created == COMMIT, "API commit differs from the reviewed local commit; reference unchanged"
    assert api(f"git/ref/heads/{BRANCH}")["object"]["sha"] == parent, "Remote changed during upload"
    updated = api(f"git/refs/heads/{BRANCH}", {"sha": created, "force": False}, "PATCH")
    assert updated["object"]["sha"] == COMMIT
    assert api(f"git/ref/heads/{BRANCH}")["object"]["sha"] == COMMIT
    record = {"published": True, "repository": REPO, "branch": BRANCH,
              "commit": COMMIT, "tree": tree, "files": len(entries), "force": False}
    output = Path("projects/lucid-svg-best-practices/artifacts/manifests/preview-publication.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
