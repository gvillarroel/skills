#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare a committed checkout with sealed local runtime bytes and Git blobs."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[3]


def snapshot(source, policy):
    result = {}
    for directory, children, files in os.walk(source):
        relative = Path(directory).relative_to(source)
        children[:] = [name for name in children if name not in policy["COPY_IGNORE"]
                       and (relative / name).as_posix() not in policy["RUNTIME_EXCLUDED_DIRS"]]
        for name in files:
            path = Path(directory) / name
            if name in policy["COPY_IGNORE"] or path.suffix.lower() in policy["SNAPSHOT_IGNORED_SUFFIXES"]:
                continue
            result[path.relative_to(source).as_posix()] = path.read_bytes()
    return result


def digest(files):
    rows = {name: {"sizeBytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for name, data in files.items()}
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluations/colorset-audit/committed-payload-20261002.json")
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    proof = json.loads((ROOT / "evaluations/colorset-audit/release-payload-20261002.json").read_text())
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip()
    tree = subprocess.check_output(["git", "ls-tree", "-r", "--format=%(objectname)%x09%(path)", "HEAD"], cwd=checkout, text=True)
    blobs = dict(line.split("\t", 1)[::-1] for line in tree.splitlines())
    rows, findings = [], []
    for evidence in proof["skills"]:
        skill = evidence["skill"]
        local = snapshot(ROOT / "skills" / skill, proof["filter"])
        stored = snapshot(checkout / "skills" / skill, proof["filter"])
        missing = sorted(local.keys() - stored.keys())
        extra = sorted(stored.keys() - local.keys())
        normalized, substantive, blob_errors = [], [], []
        for name in sorted(local.keys() & stored.keys()):
            a, b = local[name], stored[name]
            path = f"skills/{skill}/{name}"
            blob = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
            if blobs.get(path) != blob:
                blob_errors.append(path)
            if a != b:
                if a.replace(b"\r\n", b"\n") == b:
                    a.decode("utf-8")
                    normalized.append(path)
                else:
                    substantive.append(path)
        local_digest = digest(local)
        if missing or extra or substantive or blob_errors or local_digest != evidence["sourceRuntimeSha256"]:
            findings.append({"skill": skill, "missing": missing, "extra": extra, "substantive": substantive,
                             "gitBlobErrors": blob_errors, "localSealedDigestMatches": local_digest == evidence["sourceRuntimeSha256"]})
        rows.append({"skill": skill, "fileCount": len(stored), "localRuntimeSha256": local_digest,
                     "committedRuntimeSha256": digest(stored), "normalizedTextPaths": normalized,
                     "sealedLocalEvidence": evidence["acceptedCurrentEvidence"], "matchesGitBlobs": not blob_errors})
    report = {"schemaVersion": 1, "date": "2026-10-02", "sourceCommit": commit, "passed": not findings,
              "visualSkillCount": len(rows), "runtimeFileCount": sum(row["fileCount"] for row in rows),
              "normalizedTextCount": sum(len(row["normalizedTextPaths"]) for row in rows),
              "substantiveDifferenceCount": sum(len(row["substantive"]) for row in findings),
              "scope": "Sealed local Pi bundles compared with fresh committed LF checkout; every runtime file verified against its Git blob. This is not a new Pi trial.",
              "skills": rows, "findings": findings}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("sourceCommit", "passed", "visualSkillCount", "runtimeFileCount", "normalizedTextCount", "substantiveDifferenceCount", "findings")}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
