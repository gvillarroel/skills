#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the exact Pages deployment and compare public files with its CI artifact."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
BASE = "https://gvillarroel.github.io/skills/"
PATHS = ["index.html"] + [f"examples/{name}/index.html" for name in (
    "d3-animated-svg-cs1", "d3-animated-svg-colorset2", "d3-logo-design",
    "mermaid-max-complexity", "plantuml-colorset-renderer", "plantuml-colorset-renderer-cs1",
    "echarts-animated-svg", "procedural-svg-animation", "threejs-animated-3d",
    "vectorize-abstract-world-maps", "compose-synchronized-svg", "hierarchy-lens",
    "usefulcharts-style", "ai-concept-videos", "slidev-echarts", "slidev-animejs")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--build-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=ROOT / "evaluations/solid-colorset-style/publication-20261003.json")
    args = parser.parse_args()
    command = ["gh", "run", "view", args.run_id, "--json", "headSha,status,conclusion,url,workflowName,jobs"]
    workflow = json.loads(subprocess.check_output(command, cwd=ROOT, text=True, encoding="utf-8"))
    provenance_path = args.build_root.parent / "pages-provenance.json"
    if not provenance_path.is_file():
        raise SystemExit("Run download_publication.py first; Pages artifact provenance is required.")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    files = {path.relative_to(args.build_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(args.build_root.rglob("*")) if path.is_file()}
    deployed = any(step["name"] == "Deploy Pages" and step["conclusion"] == "success"
                   for job in workflow["jobs"] for step in job["steps"])
    artifact = json.loads(subprocess.check_output(["gh", "api",
        f"repos/{provenance['repository']}/actions/artifacts/{provenance['artifact']['id']}"],
        cwd=ROOT, text=True, encoding="utf-8"))
    artifact_valid = (artifact["name"] == "github-pages" and not artifact["expired"]
                      and artifact.get("digest") == provenance["artifact"].get("digest")
                      and artifact.get("workflow_run", {}).get("id") == int(args.run_id)
                      and artifact["workflow_run"].get("head_sha") == args.commit)
    bound = (provenance["runId"] == args.run_id and provenance["sourceCommit"] == args.commit
             and provenance["buildRoot"] == args.build_root.resolve().relative_to(ROOT).as_posix()
             and provenance["files"] == files and artifact_valid
             and provenance["tarSha256"] == hashlib.sha256((args.build_root.parent / "artifact.tar").read_bytes()).hexdigest())
    if not bound or workflow["workflowName"] != "Publish GitHub Pages" or not deployed:
        raise SystemExit("Build provenance or the successful Pages deployment does not match the requested run.")

    def compare(path):
        expected = (args.build_root / path).read_bytes()
        url = BASE + path.removesuffix("index.html")
        request = Request(url + "?source=" + args.commit,
                          headers={"Cache-Control": "no-cache", "User-Agent": "skills-presentation-publication-check"})
        try:
            with urlopen(request, timeout=30) as response:
                actual = response.read()
                return {"path": path, "url": url, "status": response.status,
                        "buildSha256": hashlib.sha256(expected).hexdigest(),
                        "publicSha256": hashlib.sha256(actual).hexdigest(),
                        "matches": actual == expected}
        except Exception as error:
            return {"path": path, "url": url, "matches": False, "error": str(error)}

    paths = list(PATHS)
    paths += ["examples/d3-animated-svg/gallery.js", "examples/d3-animated-svg/gallery-page.css",
              "examples/mermaid-max-complexity/gallery.js", "examples/mermaid-max-complexity/gallery.css",
              "examples/mermaid-max-complexity/gallery.json"]
    paths += [f"examples/mermaid-max-complexity/svg/{palette}/{name}"
              for palette in ("colorset1", "colorset2")
              for name in ("c4.static.svg", "c4.animated.svg", "treemap.static.svg")]
    for directory, suffix in (("examples/threejs-animated-3d/assets", ".js"),
                              ("examples/threejs-animated-3d/assets", ".css"),
                              ("examples/mermaid-max-complexity/svg", ".svg")):
        candidates = sorted(path for path in (args.build_root / directory).rglob("*")
                            if path.is_file() and path.suffix == suffix)
        if not candidates:
            raise SystemExit(f"No {suffix} publication resource in {directory}")
        paths.append(candidates[0].relative_to(args.build_root).as_posix())
    with ThreadPoolExecutor(max_workers=4) as pool:
        comparisons = list(pool.map(compare, paths))
    passed = workflow["headSha"] == args.commit and workflow["status"] == "completed" and workflow["conclusion"] == "success" and all(row["matches"] for row in comparisons)
    report = {"date": "2026-10-03", "verifiedAtUtc": datetime.now(timezone.utc).isoformat(),
              "passed": passed, "sourceCommit": args.commit, "workflow": workflow,
              "comparisons": comparisons, "buildFileCount": sum(path.is_file() for path in args.build_root.rglob("*")),
              "buildRoot": args.build_root.resolve().relative_to(ROOT).as_posix(),
              "artifactId": artifact["id"], "artifactDigest": artifact.get("digest"),
              "tarSha256": provenance["tarSha256"], "artifactProvenanceVerified": bound,
              "deployStepSucceeded": deployed}
    destination = args.report.resolve()
    if not destination.is_relative_to(ROOT):
        raise SystemExit("Publication evidence must stay inside this repository.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "sourceCommit": args.commit, "workflow": workflow["url"],
                      "comparisons": len(comparisons), "failures": [row for row in comparisons if not row["matches"]]}, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
