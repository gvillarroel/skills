#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare sealed local runtime files with the committed Git blobs."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("pi_runner", ROOT / "scripts/run-pi-skill-eval.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def main():
    proof = json.loads((ROOT / "evaluations/solid-colorset-style/final-runtime-20261003.json").read_text())
    if not proof["passed"]:
        raise SystemExit("Seal final runtime evidence before comparing committed files.")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    tree = subprocess.check_output(["git", "ls-tree", "-r", "--format=%(objectname)%x09%(path)", "HEAD"], cwd=ROOT, text=True)
    blobs = dict(line.split("\t", 1)[::-1] for line in tree.splitlines())
    process = subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    results, findings = [], []
    try:
        for accepted in proof["selectedRuns"]:
            skill = accepted["skill"]
            source = ROOT / "skills" / skill
            local_snapshot, committed_snapshot, normalized, missing, substantive = {}, {}, [], [], []
            for directory, children, files in os.walk(source):
                relative = Path(directory).relative_to(source)
                children[:] = sorted(name for name in children if name not in RUNNER.COPY_IGNORE and relative / name not in RUNNER.RUNTIME_EXCLUDED_DIRS)
                for name in sorted(files):
                    path = Path(directory) / name
                    if name in RUNNER.COPY_IGNORE or path.suffix.lower() in RUNNER.SNAPSHOT_IGNORED_SUFFIXES:
                        continue
                    key = path.relative_to(source).as_posix()
                    full = f"skills/{skill}/{key}"
                    data = path.read_bytes()
                    local_snapshot[key] = {"sizeBytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                    if full not in blobs:
                        missing.append(full)
                        continue
                    process.stdin.write((blobs[full] + "\n").encode())
                    process.stdin.flush()
                    header = process.stdout.readline().decode().strip().split()
                    stored = process.stdout.read(int(header[2]))
                    if process.stdout.read(1) != b"\n":
                        raise RuntimeError("Invalid Git batch separator")
                    committed_snapshot[key] = {"sizeBytes": len(stored), "sha256": hashlib.sha256(stored).hexdigest()}
                    if data != stored:
                        if data.replace(b"\r\n", b"\n") == stored:
                            data.decode("utf-8")
                            normalized.append(full)
                        else:
                            substantive.append(full)
            extra = sorted(path for path in blobs if path.startswith(f"skills/{skill}/") and
                           path.removeprefix(f"skills/{skill}/") not in local_snapshot and
                           not path.startswith(f"skills/{skill}/assets/examples/"))
            local_digest = RUNNER.snapshot_digest(local_snapshot)
            sealed = local_digest == accepted["payloadSha256"]
            if missing or extra or substantive or not sealed:
                findings.append({"skill": skill, "missing": missing, "extra": extra,
                                 "substantive": substantive, "sealedLocalDigestMatches": sealed})
            results.append({"skill": skill, "fileCount": len(committed_snapshot),
                            "localRuntimeSha256": local_digest,
                            "committedRuntimeSha256": RUNNER.snapshot_digest(committed_snapshot),
                            "normalizedTextPaths": normalized, "sealedLocalRun": accepted["runId"]})
    finally:
        process.stdin.close()
        process.wait()
    report = {"date": "2026-10-03", "sourceCommit": commit, "passed": not findings,
              "visualSkillCount": len(results), "runtimeFileCount": sum(row["fileCount"] for row in results),
              "normalizedTextCount": sum(len(row["normalizedTextPaths"]) for row in results),
              "scope": "Sealed local Pi bytes compared directly with committed Git blobs. UTF-8 CRLF to LF normalization is disclosed; this is not a new Pi trial.",
              "skills": results, "findings": findings}
    destination = ROOT / "evaluations/solid-colorset-style/committed-runtime-20261003.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "skills"}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
