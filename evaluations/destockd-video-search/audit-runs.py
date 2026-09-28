#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently audit exact selections and media from isolated Destockd runs."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit


def audit(run):
    workspace = run / "workspace"
    result = json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))
    checks = {"strict_harness": result["passed"]}
    name = run.name
    manifest = None
    if "naturalistic" in name or "generalization" in name:
        filename = "options" if "naturalistic" in name else "animation-options"
        manifest = json.loads((workspace / f"{filename}.json").read_text(encoding="utf-8"))
        rows = manifest["results"]
        count = 6 if "naturalistic" in name else 4
        checks["exact_candidate_count"] = len(rows) == count
        checks["unique_shots"] = len({(r["film"], r["shot"]) for r in rows}) == count
        checks["stable_options"] = [r["option"] for r in rows] == list(range(1, count + 1))
        checks["identity_urls"] = all([unquote(x) for x in urlsplit(r["page_url"]).fragment.strip("/").split("/")] == ["shot", r["film"], r["shot"]] for r in rows)
        page = (workspace / f"{filename}.html").read_text(encoding="utf-8")
        checks["gallery_identity_coverage"] = all(r["id"] in page for r in rows)
        checks["preview_separation"] = all(r["clip"] != r["preview"] for r in rows)
        if "naturalistic" in name:
            checks["no_full_video_download"] = not list(workspace.glob("*.mp4"))
    if "contract" in name or "generalization" in name:
        filename = "chosen.mp4" if "contract" in name else "animation.mp4"
        file = workspace / filename
        receipt = json.loads((workspace / (filename + ".json")).read_text(encoding="utf-8"))
        expected = {"film": "Women Astronauts Training", "shot": "shot_050"} if manifest is None else manifest["results"][2]
        checks["exact_selected_identity"] = all(receipt["shot"][key] == expected[key] for key in ("film", "shot"))
        checks["complete_bytes"] = receipt["bytes"] == file.stat().st_size
        checks["sha256_matches"] = receipt["sha256"] == hashlib.sha256(file.read_bytes()).hexdigest()
        checks["full_clip_url"] = receipt["download_url"] == receipt["shot"]["clip"] and receipt["download_url"] != receipt["shot"]["preview"]
        decoded = subprocess.run(["ffmpeg", "-v", "error", "-i", str(file), "-f", "null", "-"], capture_output=True, timeout=90)
        checks["full_media_decode"] = decoded.returncode == 0 and not decoded.stderr.strip()
    if "boundary" in name:
        decision = json.loads((workspace / "decision.json").read_text(encoding="utf-8"))
        checks["unresolved_selection"] = decision["needs_selection"] is True and decision["download_performed"] is False
        checks["no_video_download"] = not list(workspace.glob("*.mp4"))
    return {"run": name, "passed": all(checks.values()), "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    reports = []
    for value in args.runs:
        try:
            reports.append(audit(Path(value)))
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
            reports.append({"run": Path(value).name, "passed": False, "error": str(exc)})
    document = {"passed": all(r["passed"] for r in reports), "runs": reports}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(document, indent=2))
    return 0 if document["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
