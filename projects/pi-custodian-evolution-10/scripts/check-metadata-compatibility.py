#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent release observations, outside frozen study scoring.

Run: uv run --script check-metadata-compatibility.py --candidate-project PATH
  --baseline-project PATH --output-dir PROJECT/artifacts/manual-audit/UNIQUE
Only import source already reviewed as trusted code. The imported definitions
are exercised with local fixtures, a private environment, and a scanner stub;
this metadata check does not verify the secret gate or authorize activation.
"""
from __future__ import annotations

import contextlib
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
AREA = Path(__file__).resolve().parents[1]
FILES = ["scripts/custodian.py", "src/tools/maintenance.ts", "prompts/repo-custodian.md"]


def hashes(roots):
    return {label: {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in FILES}
            for label, root in roots.items()}


def load(label, root):
    spec = importlib.util.spec_from_file_location("manual_audit_" + label, root / FILES[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_inspect(module, raw):
    old_git, old_text = module.git, module.text
    def observed_git(repo, *args, **kwargs):
        if args[0] == "status":
            value = raw
        elif args[0] == "symbolic-ref":
            value = "main\n"
        elif args[-1] == "branch.main.remote":
            value = "origin\n"
        elif args[-1] == "branch.main.merge":
            value = "refs/heads/main\n"
        else:
            raise AssertionError("Unexpected observation")
        return SimpleNamespace(stdout=value.encode(), returncode=0)
    module.git = observed_git
    module.text = lambda *args: "a" * 40
    worker = module.Custodian.__new__(module.Custodian)
    worker.repo = lambda name: Path("fixture")
    worker.saved = lambda repo: None
    worker.excluded = lambda: {}
    worker.commands = lambda repo: [["node", "--test"]]
    try:
        return worker.inspect("project")
    finally:
        module.git, module.text = old_git, old_text


def private_environment():
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never", GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull)
    return env


def git(cwd, *args):
    run = subprocess.run(["git", "-c", "core.longpaths=true", "-c", "core.autocrlf=false", *args],
                         cwd=cwd, capture_output=True, timeout=30,
                         env=private_environment())
    if run.returncode:
        raise RuntimeError("Private Git fixture failed; diagnostics suppressed")
    return run.stdout.decode().strip()


def failed_after_local_commit(module, fixture):
    # All repositories, state and policy are private. Scanner is a no-op only in
    # this metadata-path demonstration. This is not secret-gate verification.
    repo = fixture / "dev/project"
    repo.mkdir(parents=True)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Private Release Audit")
    git(repo, "config", "user.email", "audit@example.invalid")
    git(repo, "config", "core.longpaths", "true")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "config", "core.fsmonitor", "false")
    git(repo, "config", "commit.gpgsign", "false")
    git(repo, "config", "core.hooksPath", str(fixture / "no-hooks"))
    (repo / "notes.md").write_text("Initial harmless fixture\n", encoding="utf-8", newline="\n")
    git(repo, "add", "notes.md")
    git(repo, "commit", "-m", "Initial fixture")
    before = git(repo, "rev-parse", "HEAD")
    git(repo, "remote", "add", "origin", str(fixture / "absent-remote.git"))
    git(repo, "config", "branch.main.remote", "origin")
    git(repo, "config", "branch.main.merge", "refs/heads/main")
    (repo / "notes.md").write_text("Updated harmless fixture\n", encoding="utf-8", newline="\n")
    resources = fixture / "resources"
    resources.mkdir()
    (resources / "validation.json").write_text(json.dumps({"project": [[sys.executable, "-c", "pass"]]}))
    old_project, original_type, old_environment = module.PROJECT, module.Custodian, module.environment
    module.PROJECT = resources
    module.environment = private_environment
    worker = original_type(root=fixture / "dev", state=fixture / "state", test_mode=True)
    worker.scan = lambda blobs: None
    module.Custodian = lambda: worker
    old_stdin = sys.stdin
    out = io.StringIO()
    try:
        sys.stdin = io.StringIO(json.dumps({"action": "maintain", "repo": "project"}))
        with contextlib.redirect_stdout(out):
            module.main()
    finally:
        sys.stdin = old_stdin
        module.Custodian, module.PROJECT, module.environment = original_type, old_project, old_environment
    result = json.loads(out.getvalue())
    after = git(repo, "rev-parse", "HEAD")
    events = [json.loads(row) for row in (worker.state / "operations.jsonl").read_text().splitlines()]
    return {"realLocalHeadChanged": before != after, "beforeHeadObservedExternally": before,
            "afterHeadObservedExternally": after, "result": result, "events": events,
            "scope": "Real private Git commit then failed private fetch; scanner stubbed only in private instance; no remote push or user repository"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-project", type=Path, required=True)
    parser.add_argument("--baseline-project", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    artifacts = (AREA / "artifacts").resolve(strict=True)
    out = args.output_dir.resolve()
    roots = {"baseline": args.baseline_project.resolve(strict=True), "candidate": args.candidate_project.resolve(strict=True)}
    if not out.is_relative_to(artifacts) or any(out.is_relative_to(root) for root in roots.values()):
        raise ValueError("Output must be a separate private study artifact directory")
    for root in roots.values():
        if {"evaluator-private", "validation", "holdout"}.intersection(root.parts):
            raise ValueError("Reserved gate data are outside this release check")
    out.mkdir(parents=True, exist_ok=False)
    short_root = artifacts / "t"
    short_root.mkdir(exist_ok=True)
    if short_root.is_symlink() or short_root.resolve() != short_root:
        raise ValueError("Private fixture root must not be redirected")
    fixture = Path(tempfile.mkdtemp(prefix="m", dir=short_root))
    before = hashes(roots)
    base, candidate = load("baseline", roots["baseline"]), load("candidate", roots["candidate"])
    rename_raw = "R  destination/public.md\0source/restricted.md\0"
    rename = fake_inspect(candidate, rename_raw)
    long_path = "folder/" + "segment/" * 63 + "hidden-source.md"
    long = fake_inspect(candidate, " M " + long_path + "\0")
    rows = "".join(" M " + (f"{i:03d}/" + "a/" * 190 + "file.md") + "\0" for i in range(300))
    bulk_base, bulk_candidate = fake_inspect(base, rows), fake_inspect(candidate, rows)
    encode = lambda value: len((json.dumps(value, ensure_ascii=True) + "\n").encode())
    inspection = fake_inspect(candidate, " M docs.md\0")
    journal = candidate.operation_event({"action": "inspect", "repo": "project"}, inspection, 1, {})
    blocked = failed_after_local_commit(candidate, fixture)
    after = hashes(roots)
    structured_long = long.get("changes") or []
    observed_path = structured_long[0].get("path", "") if structured_long else ""
    result = {"kind": "independent-manual-release-observations", "version": 1,
        "reservedCasesRead": False, "modelCalls": 0, "lifecycleActions": 0,
        "roots": {key: str(value) for key, value in roots.items()}, "fixtureRoot": str(fixture),
        "sourceHashesBefore": before, "sourceHashesAfter": after, "sourcesUnchanged": before == after,
        "validationCapability": {"baselineField": "validationCommands", "expected": [["node", "--test"]],
                                 "candidateObservation": inspection.get("validationCommands")},
        "rename": {"input": rename_raw, "structuredChanges": rename.get("changes"),
                   "changesTruncated": rename.get("changesTruncated"), "legacyStatus": rename.get("status")},
        "pathTruncation": {"inputPathLength": len(long_path), "observedPathLength": len(observed_path),
                           "changesTruncated": long.get("changesTruncated"),
                           "pathSuffixLost": bool(observed_path) and not observed_path.endswith("hidden-source.md")},
        "boundedOutput": {"records": 300, "pathLength": len("000/" + "a/" * 190 + "file.md"),
                          "baselineJsonBytes": encode(bulk_base), "candidateJsonBytes": encode(bulk_candidate),
                          "toolByteLimit": 200000, "changesTruncated": bulk_candidate.get("changesTruncated")},
        "inspectJournal": {"returnedBranch": inspection.get("branch"), "returnedUpstream": inspection.get("upstream"),
                           "event": journal}, "blockedAfterMutation": blocked,
        "limits": ["Injected porcelain observations verify parser and serialized-byte semantics, not actual large filesystem creation",
                   "Short private Git fixture verifies real local commit and failed local fetch metadata; scanner stubbed in fixture instance only",
                   "No study case, grading criterion, candidate, live service, or model invocation is modified"]}
    (out / "observations.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sourcesUnchanged": result["sourcesUnchanged"], "report": str(out / "observations.json"),
                      "boundedOutput": result["boundedOutput"],
                      "realLocalHeadChanged": blocked["realLocalHeadChanged"], "blockedResultFields": sorted(blocked["result"])}))


if __name__ == "__main__":
    main()
