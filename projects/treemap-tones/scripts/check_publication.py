#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind the treemap and dense-overlap public renderer bytes to their Pages commit."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
BASE = "https://gvillarroel.github.io/skills/examples/"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    destination = args.report.resolve()
    if not destination.is_relative_to(ROOT):
        raise SystemExit("Keep publication evidence inside the repository.")
    workflow = json.loads(subprocess.check_output([
        "gh", "run", "view", args.run_id, "--json",
        "headSha,status,conclusion,url,workflowName,jobs"
    ], cwd=ROOT, text=True, encoding="utf-8"))
    deployed = any(step["name"] == "Deploy Pages" and step["conclusion"] == "success"
                   for job in workflow["jobs"] for step in job["steps"])
    if not (workflow["headSha"] == args.commit and workflow["status"] == "completed"
            and workflow["conclusion"] == "success" and deployed
            and workflow["workflowName"] == "Publish GitHub Pages"):
        raise SystemExit("The requested commit has not completed its Pages deployment.")

    comparisons = []
    for relative in ("d3-animated-svg/gallery.js", "d3-animated-svg/solid-style.js",
                     "d3-animated-svg-cs1/cs1-config.js"):
        expected = subprocess.check_output([
            "git", "show", args.commit + ":skills/d3/assets/examples/" + relative
        ], cwd=ROOT)
        url = BASE + relative + "?source=" + args.commit
        with urlopen(Request(url, headers={"Cache-Control": "no-cache"}), timeout=30) as response:
            actual = response.read()
            comparisons.append({"path": relative, "status": response.status,
                                "sourceSha256": hashlib.sha256(expected).hexdigest(),
                                "publicSha256": hashlib.sha256(actual).hexdigest(),
                                "matches": actual == expected})
    pages = []
    for name in ("d3-animated-svg-cs1", "d3-animated-svg-colorset2", "d3-animated-svg"):
        url = BASE + name + "/?source=" + args.commit
        with urlopen(Request(url, headers={"Cache-Control": "no-cache"}), timeout=30) as response:
            content = response.read()
            pages.append({"url": url, "status": response.status,
                          "sha256": hashlib.sha256(content).hexdigest(),
                          "loadsSharedRenderer": b"gallery.js" in content})
    passed = all(row["matches"] for row in comparisons) and all(row["loadsSharedRenderer"] for row in pages)
    report = {"passed": passed, "verifiedAtUtc": datetime.now(timezone.utc).isoformat(),
              "sourceCommit": args.commit, "workflow": workflow,
              "deployStepSucceeded": deployed, "comparisons": comparisons, "pages": pages,
              "scope": "Exact Git blob bytes, successful matching Pages deployment, and all three shared-renderer pages. Live visual acceptance is recorded separately."}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "commit": args.commit, "workflow": workflow["url"],
                      "comparisons": len(comparisons), "pages": len(pages)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
