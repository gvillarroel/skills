#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent release compatibility check; not part of frozen study scoring."""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
STUDY = Path(__file__).resolve().parents[1]
FIELDS = ("repo", "head", "status", "ownedMerge", "excluded")
FORBIDDEN_PARTS = {"evaluator-private", "validation", "holdout"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git(cwd, *args):
    result = subprocess.run(["git", "-c", "core.longpaths=true", "-c", "core.autocrlf=false", *args],
                            cwd=cwd, capture_output=True, timeout=20, check=False,
                            env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never"})
    if result.returncode:
        raise RuntimeError("Isolated Git compatibility fixture failed; diagnostics suppressed.")
    return result.stdout.decode("utf-8", "strict").strip()


def load_worker(source, resource_root):
    name = "compatibility_worker_" + uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.PROJECT = resource_root
    return module


def equivalent_commands(result):
    """Recognize exact old argv observation or a losslessly structured policy."""
    value = result.get("validationCommands")
    if isinstance(value, list):
        return value, "validationCommands"
    policy = result.get("validationPolicy")
    if isinstance(policy, dict) and isinstance(policy.get("commands"), list):
        commands = policy["commands"]
        if all(isinstance(item, list) for item in commands):
            return commands, "validationPolicy.commands"
        if all(isinstance(item, dict) and isinstance(item.get("argv"), list) for item in commands):
            return [item["argv"] for item in commands], "validationPolicy.commands[].argv"
    return None, None


def inspect_source(source_bytes, baseline_bytes, temporary_root):
    temporary_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="c-", dir=temporary_root, ignore_cleanup_errors=True) as temporary:
        base = Path(temporary).resolve()
        if not base.is_relative_to(temporary_root.resolve()):
            raise ValueError("Compatibility fixture escaped its explicit private artifact root.")
        root = base / "dev"
        repo = root / "project"
        repo.mkdir(parents=True)
        git(repo, "init")
        git(repo, "config", "user.name", "Local Compatibility Fixture")
        git(repo, "config", "user.email", "fixture@example.invalid")
        git(repo, "config", "core.longpaths", "true")
        (repo / "notes with spaces.md").write_text("Initial harmless fixture\n", encoding="utf-8")
        git(repo, "add", "notes with spaces.md")
        git(repo, "commit", "-m", "Initial compatibility fixture")
        head = git(repo, "rev-parse", "HEAD")
        branch = git(repo, "symbolic-ref", "--short", "HEAD")
        remote = base / "private-remote.git"
        git(base, "init", "--bare", str(remote))
        git(repo, "remote", "add", "origin", str(remote))
        git(repo, "config", f"branch.{branch}.remote", "origin")
        git(repo, "config", f"branch.{branch}.merge", "refs/heads/" + branch)
        (repo / "notes with spaces.md").write_text("Modified harmless fixture\n", encoding="utf-8")
        (repo / "extra documentation.md").write_text("Untracked harmless fixture\n", encoding="utf-8")
        resources = base / "host"
        resources.mkdir()
        unexpected_execution = base / "CONFIGURED_COMMAND_WAS_EXECUTED"
        # The command is safe and fixture-local, but must never run in inspect.
        commands = [[sys.executable, "-c", "from pathlib import Path;Path(" + repr(str(unexpected_execution)) + ").write_text('unexpected')"],
                    ["node", "tools/validate-prompts.mjs"], ["node", "--test"]]
        (resources / "validation.json").write_text(json.dumps({"project": commands}), encoding="utf-8")
        exclusion = "Owner-defined fixture exclusion; inspect must expose it without acting."
        (resources / "excluded-repositories.json").write_text(json.dumps({"project": exclusion}), encoding="utf-8")
        source = base / "candidate.py"
        baseline_source = base / "baseline.py"
        source.write_bytes(source_bytes)
        baseline_source.write_bytes(baseline_bytes)
        captured_out, captured_err = io.StringIO(), io.StringIO()
        with redirect_stdout(captured_out), redirect_stderr(captured_err):
            baseline = load_worker(baseline_source, resources)
            original = baseline.Custodian(root, base / "baseline-state", test_mode=True)
            saved = {"head": head, "mergeHead": "b" * 40, "resolved": [], "startedAt": 1}
            original.marker(repo).write_text(json.dumps(saved), encoding="utf-8")
            expected = original.inspect("project")
            candidate = load_worker(source, resources)
            worker = candidate.Custodian(root, base / "candidate-state", test_mode=True)
            worker.marker(repo).write_text(json.dumps(saved), encoding="utf-8")
            result = worker.inspect("project")
        if not isinstance(result, dict):
            raise ValueError("Candidate inspect returned no structured observation.")
        observed_commands, location = equivalent_commands(result)
        checks = [{"name": "original-field:" + field, "passed": field in result and result[field] == expected[field]}
                  for field in FIELDS]
        checks.extend([
            {"name": "validation-policy-capability-preserved", "passed": observed_commands == commands,
             "equivalentLocation": location},
            {"name": "configured-commands-not-executed", "passed": not unexpected_execution.exists()},
            {"name": "checks-not-claimed-passed", "passed": result.get("validationStatus") in (None, "not-run")
             and result.get("validationReceipts") in (None, [])},
            {"name": "no-inspection-stdout-stderr", "passed": not captured_out.getvalue() and not captured_err.getvalue()},
            {"name": "source-copy-unmodified", "passed": sha(source.read_bytes()) == sha(source_bytes)
             and sha(baseline_source.read_bytes()) == sha(baseline_bytes)},
        ])
        return {"passed": all(check["passed"] for check in checks), "checks": checks,
                "observedFieldNames": sorted(result), "configuredCommandCount": len(commands),
                "commandPolicySha256": sha(json.dumps(commands, separators=(",", ":")).encode()),
                "scope": "Exact legacy inspect observations and lossless policy equivalence; configured commands are never maintenance execution evidence."}


def candidate_source(path, baseline_bytes):
    if FORBIDDEN_PARTS.intersection(path.parts):
        raise ValueError("Reserved gate data are outside this compatibility review.")
    value = read_json(path)
    changed = [item for item in value.get("changes", []) if item.get("path") == "scripts/custodian.py"]
    if len(changed) > 1:
        raise ValueError("Duplicate worker source in candidate.")
    if changed:
        if changed[0].get("beforeHash") != sha(baseline_bytes):
            raise ValueError("Candidate worker preimage differs from the immutable baseline.")
        return changed[0]["content"].encode("utf-8")
    return baseline_bytes


def run(args):
    baseline_file = args.baseline_project.resolve(strict=True) / "scripts/custodian.py"
    baseline_bytes = baseline_file.read_bytes()
    temporary_root = args.temporary_root.resolve()
    if not temporary_root.is_relative_to((STUDY / "artifacts").resolve()):
        raise ValueError("Use the study's private artifact root for compatibility fixtures.")
    sources = []
    for path in args.candidate_file:
        sources.append((path.resolve(strict=True), None))
    if args.iterations_root:
        iterations = args.iterations_root.resolve(strict=True)
        if FORBIDDEN_PARTS.intersection(iterations.parts):
            raise ValueError("Reserved gate directories must not be read.")
        for folder in sorted(iterations.glob("i[0-9][0-9]")):
            result_file, source_file = folder / "iteration-result.json", folder / "candidate.json"
            if result_file.is_file() and source_file.is_file():
                finished = read_json(result_file)
                sources.append((source_file, {"slot": finished.get("slot"), "nativeQualified": finished.get("qualified"),
                                              "nativeOutcome": finished.get("outcome"), "patchDigest": finished.get("patchDigest")}))
    results = []
    baseline_check = inspect_source(baseline_bytes, baseline_bytes, temporary_root)
    for path, identity in sources:
        source = candidate_source(path, baseline_bytes)
        candidate_hash = sha(path.read_bytes())
        try:
            check = inspect_source(source, baseline_bytes, temporary_root)
        except Exception as error:
            check = {"passed": False, "errorCategory": type(error).__name__, "rawDiagnosticsSuppressed": True}
        if sha(path.read_bytes()) != candidate_hash:
            raise ValueError("Candidate artifact changed during independent review.")
        results.append({"candidateFile": str(path), "candidateSha256": candidate_hash,
                        **(identity or {}), "manualCompatibility": check})
    if sha(baseline_file.read_bytes()) != sha(baseline_bytes):
        raise ValueError("Live baseline source changed during inspection review.")
    return {"version": 1, "atUtc": datetime.now(timezone.utc).isoformat(),
            "passed": baseline_check["passed"] and all(item["manualCompatibility"]["passed"] for item in results),
            "baselineSourceSha256": sha(baseline_bytes), "baselineCompatibility": baseline_check,
            "candidates": results, "sourceUnmodified": True, "frozenStudyScoresModified": False,
            "limitations": "A separate compatibility release check, not an added development score or reserved-case gate. No scanner, provider, network, maintenance or user-repository operation runs."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-project", type=Path, required=True)
    parser.add_argument("--candidate-file", type=Path, action="append", default=[])
    parser.add_argument("--iterations-root", type=Path)
    parser.add_argument("--temporary-root", type=Path, default=STUDY / "artifacts/c")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "baselinePassed": result["baselineCompatibility"]["passed"],
                      "candidates": [{"slot": item.get("slot"), "nativeQualified": item.get("nativeQualified"),
                                      "manualCompatible": item["manualCompatibility"]["passed"]} for item in result["candidates"]]}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"passed": False, "errorCategory": type(error).__name__, "rawDiagnosticsSuppressed": True}))
        raise SystemExit(1)
