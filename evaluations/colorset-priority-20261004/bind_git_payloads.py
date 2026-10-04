#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind sampled raw bundles to final staged/committed Git blobs without edits."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("priority_harness", ROOT / "scripts/run-pi-skill-eval.py")
HARNESS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(HARNESS)


def normalize_lf(data):
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data if b"\0" in data else data.replace(b"\r\n", b"\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", default="INDEX", help="INDEX or an exact Git commit/tree reference")
    args = parser.parse_args()
    results = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    first = {}
    identities = {}
    findings = []
    for row in results["selectedFinalRuns"]:
        manifest = json.loads((ROOT / row["rawEvidencePath"] / "run-manifest.json").read_text(encoding="utf-8"))
        skill = manifest["skill"]["name"]
        identities.setdefault(skill, set()).add(manifest["skill"]["payloadSha256"])
        if manifest["skill"]["payloadSha256"] != row["payloadSha256"]:
            findings.append(f"Selected result/manifest identity differs: {row['runId']}")
        first.setdefault(skill, row)
    for skill, hashes in identities.items():
        if len(hashes) != 1:
            findings.append(f"Selected skill cohort has multiple payload identities: {skill}: {sorted(hashes)}")
    bindings = []
    for skill, row in sorted(first.items()):
        source = ROOT / row["rawEvidencePath"] / "workspace/skills" / skill
        raw = HARNESS.snapshot_tree(source)
        list_args = ["git", "ls-files", "-z", "--", f"skills/{skill}"] if args.ref == "INDEX" else ["git", "ls-tree", "-rz", "--name-only", args.ref, "--", f"skills/{skill}"]
        listing = subprocess.run(list_args, cwd=ROOT, capture_output=True, check=False)
        if listing.returncode:
            findings.append(f"Cannot inventory final Git runtime payload: {skill}: {listing.stderr.decode('utf-8', errors='replace')}")
        prefix = f"skills/{skill}/"
        git_paths = {name[len(prefix):] for name in listing.stdout.decode("utf-8").split("\0") if name.startswith(prefix)}
        git_paths = {path for path in git_paths if not any(part in HARNESS.COPY_IGNORE for part in Path(path).parts) and not path.startswith("assets/examples/")}
        if git_paths != set(raw):
            findings.append(f"Final Git runtime file inventory differs: {skill}: missing={sorted(set(raw) - git_paths)}, additional={sorted(git_paths - set(raw))}")
        requests = [f":skills/{skill}/{path}" if args.ref == "INDEX" else f"{args.ref}:skills/{skill}/{path}" for path in sorted(raw)]
        proc = subprocess.run(["git", "cat-file", "--batch"], input=("\n".join(requests) + "\n").encode("utf-8"), cwd=ROOT, capture_output=True, check=False)
        cursor, normalized_only = 0, []
        destination = ROOT / "evaluations/runs/20261004-colorset-git-binding" / args.ref.replace(":", "-").replace("/", "-") / row["payloadSha256"][:16] / skill
        for path, request in zip(sorted(raw), requests):
            end = proc.stdout.find(b"\n", cursor)
            header = proc.stdout[cursor:end].decode("utf-8", errors="replace")
            cursor = end + 1
            fields = header.split()
            if len(fields) != 3 or fields[1] != "blob":
                findings.append(f"Missing final Git blob: {request} ({header})")
                continue
            size = int(fields[2])
            data = proc.stdout[cursor:cursor + size]
            cursor += size + 1
            sampled = (source / path).read_bytes()
            if data != sampled:
                if data != normalize_lf(sampled):
                    findings.append(f"Meaningful sampled/Git payload difference: skills/{skill}/{path}")
                else:
                    normalized_only.append(path)
            target = destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        canonical = HARNESS.snapshot_tree(destination)
        working = {path: value for path, value in HARNESS.snapshot_tree(ROOT / "skills" / skill).items() if not any(part in HARNESS.COPY_IGNORE for part in Path(path).parts) and not path.startswith("assets/examples/")}
        if set(working) != set(raw):
            findings.append(f"Frozen working payload file set changed: {skill}")
        if set(canonical) != set(raw):
            findings.append(f"Final Git runtime payload file set differs: {skill}")
        if HARNESS.snapshot_digest(raw) != row["payloadSha256"]:
            findings.append(f"Sampled manifest/raw identity mismatch: {skill}")
        if working != raw:
            # Commit-time LF normalization can affect the working tree only when
            # all sampled bytes still normalize to the final blobs above.
            differing = [path for path in raw if not (ROOT / "skills" / skill / path).is_file() or (ROOT / "skills" / skill / path).read_bytes() not in ((source / path).read_bytes(), normalize_lf((source / path).read_bytes()))]
            if differing:
                findings.append(f"Frozen working payload changed: {skill}: {differing}")
        bindings.append({"skill": skill, "sampledRunId": row["runId"], "sampledRawPayloadSha256": HARNESS.snapshot_digest(raw), "gitCanonicalLfPayloadSha256": HARNESS.snapshot_digest(canonical), "runtimeFileCount": len(raw), "gitFileCount": len(canonical), "gitInventoryFileCount": len(git_paths), "lfNormalizationOnlyPaths": normalized_only, "gitReference": args.ref})
    result = {"schemaVersion": 1, "date": "2026-10-04", "gitReference": args.ref, "passed": not findings, "bindingCount": len(bindings), "bindings": bindings, "findings": findings}
    output = HERE / "git-payload-bindings.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "bindingCount": len(bindings), "findings": findings}))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
