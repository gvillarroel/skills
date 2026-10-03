#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare and optionally stage explicit reviewed presentation-revision paths."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EXACT = {"SKILLS.md", "docs/colorsets.md"}
PREFIXES = ("skills/", "evaluations/arrow-contrast/", "evaluations/arrow-contrast-composition/",
            "evaluations/arrow-contrast-custom/", "evaluations/arrow-contrast-diagrams/",
            "evaluations/pi-prompts/arrow-contrast/", "evaluations/pi-prompts/arrow-contrast-custom/",
            "evaluations/pi-prompts/arrow-contrast-composition/", "projects/arrow-contrast/",
            "projects/arrow-contrast-composition/", "projects/arrow-contrast-custom/", "projects/arrow-contrast-diagrams/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", action="store_true")
    args = parser.parse_args()
    paths = set()
    for command in (["git", "-c", "core.safecrlf=false", "diff", "--name-only", "-z", "HEAD", "--"],
                    ["git", "ls-files", "--others", "--exclude-standard", "-z"]):
        paths.update(value.decode("utf-8") for value in subprocess.check_output(command, cwd=ROOT).split(b"\0") if value)
    unrelated = sorted(path for path in paths if path.startswith(".codex-remote-attachments/"))
    paths.difference_update(unrelated)
    unexpected = sorted(path for path in paths if (path not in EXACT and not path.startswith(PREFIXES)) or
                        "/artifacts/" in path or path.startswith("evaluations/runs/"))
    media = sorted(path for path in paths if Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".pdf", ".zip"})
    if unexpected or any(not path.startswith("skills/plantuml-colorset-renderer/assets/examples/") or not path.endswith(".png") for path in media):
        raise RuntimeError(json.dumps({"unexpectedPaths": unexpected, "mediaPaths": media}, indent=2))
    destination = ROOT / "projects/arrow-contrast/artifacts/manifests"
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {"pathCount": len(paths), "paths": sorted(paths), "intentionalStaticMedia": media,
                "unrelatedAppAttachmentsNotStaged": unrelated,
                "scope": "Initial worktree was clean. Stage explicit canonical bundles, owning fixtures, shared contract, project scripts and compact validation evidence."}
    (destination / "publication-paths.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    pathspec = destination / "publication.pathspec"
    pathspec.write_bytes(b"\0".join((":(literal)" + path).encode("utf-8") for path in sorted(paths)) + b"\0")
    if args.stage:
        subprocess.run(["git", "-c", "core.safecrlf=false", "add", "--pathspec-from-file", str(pathspec), "--pathspec-file-nul"], cwd=ROOT, check=True)
    print(json.dumps({"pathCount": len(paths), "media": media, "staged": args.stage}, indent=2))


if __name__ == "__main__":
    main()
