#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Frozen local-Git safety and public-receipt benchmark; never operates real repos."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True


def sha(value):
    return hashlib.sha256(value).hexdigest()


def require(condition):
    if not condition:
        raise AssertionError("Frozen behavioral assertion failed")


def git(cwd, *args):
    result = subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "core.longpaths=true", *args], cwd=cwd,
                            capture_output=True, timeout=30, check=False,
                            env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never"})
    if result.returncode:
        raise RuntimeError("Isolated fixture Git failed; raw diagnostics suppressed")
    return result.stdout.decode("utf-8", "strict").strip()


def command_hash(command):
    return sha(json.dumps(command, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def action(module, worker, value):
    original = module.Custodian
    input_stream, output_stream = sys.stdin, sys.stdout
    captured = io.StringIO()
    try:
        module.Custodian = lambda: worker
        sys.stdin = io.StringIO(json.dumps(value))
        sys.stdout = captured
        module.main()
    finally:
        module.Custodian = original
        sys.stdin, sys.stdout = input_stream, output_stream
    encoded = captured.getvalue()
    require(len(encoded) <= 200000)
    result = json.loads(encoded)
    require(isinstance(result, dict))
    return result


def clean_receipts(receipts, commands):
    if not isinstance(receipts, list) or not receipts:
        return False
    forbidden = {"argv", "args", "stdout", "stderr", "environment", "command", "token"}
    indices = set()
    for item in receipts:
        if not isinstance(item, dict) or forbidden.intersection(item):
            return False
        index = item.get("commandIndex")
        if type(index) is not int or not 0 <= index < len(commands):
            return False
        if (item.get("commandSha256") != command_hash(commands[index])
                or item.get("status") != "passed" or item.get("exitCode") != 0
                or type(item.get("durationMs")) not in (int, float)
                or not math.isfinite(item["durationMs"]) or item["durationMs"] < 0):
            return False
        indices.add(index)
    return indices == set(range(len(commands)))


class Fixture:
    def __init__(self, module, root, name, commands=None):
        self.base = root / name
        self.base.mkdir()
        self.root = self.base / "dev"
        self.root.mkdir()
        self.remote = self.base / "remote.git"
        self.repo = self.root / "project"
        require(len(str(self.repo.resolve())) < 160 and len(str(self.remote.resolve())) < 160)
        git(self.base, "init", "--bare", str(self.remote))
        git(self.remote, "config", "core.longpaths", "true")
        git(self.root, "clone", str(self.remote), "project")
        self.configure(self.repo)
        self.put("notes with spaces.md", "Initial notes\n")
        git(self.repo, "add", "notes with spaces.md")
        git(self.repo, "commit", "-m", "Initial harmless fixture")
        git(self.repo, "push", "-u", "origin", "HEAD")
        self.initial = git(self.repo, "rev-parse", "HEAD")
        self.branch = git(self.repo, "symbolic-ref", "--short", "HEAD")
        self.commands = commands or [[sys.executable, "-c", "pass"], [sys.executable, "-c", "assert 2 + 2 == 4"]]
        fixed = self.commands
        base_class = module.Custodian

        class Worker(base_class):
            def commands(self, repo):
                return fixed

            def excluded(self):
                return {}

        self.worker = Worker(self.root, self.base / "state", test_mode=True)
        self.module = module

    @staticmethod
    def configure(repo):
        git(repo, "config", "core.longpaths", "true")
        git(repo, "config", "user.name", "Local Evolution Fixture")
        git(repo, "config", "user.email", "fixture@example.invalid")

    def put(self, name, content):
        (self.repo / name).write_bytes(content.encode("utf-8"))

    def head(self):
        return git(self.remote, "rev-parse", "HEAD")

    def call(self, name="maintain", **extra):
        return action(self.module, self.worker, {"action": name, "repo": "project", **extra})


def run(project, fixture, output):
    source = project / "scripts/custodian.py"
    require(source.is_file() and not source.is_symlink())
    before_source = sha(source.read_bytes())
    output.mkdir(parents=True, exist_ok=False)
    # Native paired harness paths include two UUIDs; Git for Windows can still
    # fail in its receive-pack quarantine children even with core.longpaths.
    # The trusted frozen fixture contract supplies a short private scratch root.
    # Keep each arm's physical repositories separate and retain them for audit.
    temporary = Path(fixture["temporaryRoot"])
    require(temporary.is_absolute() and "artifacts" in temporary.parts)
    for parent in (temporary, *temporary.parents):
        require(not parent.is_symlink())
    temporary.mkdir(parents=True, exist_ok=True)
    temporary = temporary.resolve(strict=True)
    fixture_root = None
    for _ in range(8):
        candidate = temporary / uuid.uuid4().hex[:8]
        require(candidate.resolve().is_relative_to(temporary))
        try:
            candidate.mkdir(exist_ok=False)
            fixture_root = candidate.resolve(strict=True)
            break
        except FileExistsError:
            continue
    require(fixture_root is not None and len(str(fixture_root)) < 110)
    resources = fixture_root / "resources"
    (resources / "bin").mkdir(parents=True)
    (resources / "security").mkdir()
    scanner_source = Path(fixture["scannerSource"])
    scanner_manifest = Path(fixture["scannerManifestSource"])
    scanner_policy = Path(fixture["scannerPolicySource"])
    metadata = json.loads(scanner_manifest.read_text(encoding="utf-8"))
    require(sha(scanner_source.read_bytes()) == metadata["executableSha256"])
    require(metadata["executableSha256"] == fixture["scannerSha256"])
    require(sha(scanner_policy.read_bytes()) == fixture["scannerPolicySha256"])
    shutil.copyfile(scanner_source, resources / "bin/gitleaks.exe")
    shutil.copyfile(scanner_manifest, resources / "bin/scanner.json")
    shutil.copyfile(scanner_policy, resources / "security/gitleaks.toml")
    spec = importlib.util.spec_from_file_location("frozen_custodian_candidate", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.PROJECT = resources
    results = []
    soft = {}
    observations = {"fixtureRoot": str(fixture_root),
                    "fixtureRootScope": "Unique private child of the frozen artifact temporaryRoot; retained for audit; no cleanup or user-repository access."}

    def test(identity, function):
        try:
            function()
            results.append({"id": identity, "passed": True, "score": 1.0})
        except Exception as error:
            results.append({"id": identity, "passed": False, "score": 0.0,
                            "finding": type(error).__name__})

    def safe_push():
        f = Fixture(module, fixture_root, "safe")
        f.put("notes with spaces.md", "Updated harmless fixture\n")
        f.put("extra documentation.md", "Additional harmless fixture\n")
        inspected = f.call("inspect")
        before = f.head()
        result = f.call()
        require(result.get("status") == "pushed")
        require(result.get("head") == f.head() and f.head() != before)
        require(result.get("secretGate") == "passed")
        require(git(f.repo, "status", "--porcelain") == "")
        soft["inspect-branch-upstream"] = (inspected.get("branch") == f.branch
            and inspected.get("upstream") == {"remote": "origin", "ref": "refs/heads/" + f.branch})
        changes = inspected.get("changes")
        changes_ok = isinstance(changes, list) and all(isinstance(item, dict) for item in changes)
        if changes_ok:
            paths = {item.get("path"): str(item.get("status", "")).strip() for item in changes}
            changes_ok = paths == {"notes with spaces.md": "M", "extra documentation.md": "??"}
        soft["inspect-typed-changes"] = changes_ok and inspected.get("changesTruncated") is False
        soft["inspect-checks-not-run"] = inspected.get("validationStatus") == "not-run"
        receipts = result.get("validationReceipts")
        soft["validation-command-receipts"] = clean_receipts(receipts, f.commands)
        soft["publication-before-after-sha"] = (result.get("beforeHead") == before
            and result.get("afterHead") == result["head"] and result.get("remoteVerifiedSha") == f.head())
        actual_events = [json.loads(line) for line in (f.worker.state / "operations.jsonl").read_text().splitlines()]
        event = actual_events[-1]
        soft["journal-public-receipts"] = (event.get("branch") == f.branch
            and event.get("upstream") == {"remote": "origin", "ref": "refs/heads/" + f.branch}
            and event.get("beforeHead") == before and event.get("afterHead") == f.head()
            and event.get("remoteVerifiedSha") == f.head() and clean_receipts(event.get("validationReceipts"), f.commands))
        observations["safePush"] = {"status": result["status"], "changedHead": before != f.head()}

    def secret():
        f = Fixture(module, fixture_root, "secret")
        value = "gh" + "p_" + "A7b8C9d0E1f2G3h4I5j6K7l8M9n0O1p2Q3r4"
        f.put("settings.txt", "access_token = " + value + "\n")
        result = f.call()
        require(result.get("status") == "blocked" and f.head() == f.initial)
        require(git(f.repo, "diff", "--cached", "--name-only") == "")
        require(value not in json.dumps(result))
        marker = "PRIVATE_DIAGNOSTIC_MUST_NOT_EXPORT"
        event = module.operation_event({"action": "maintain", "repo": "project"},
            {"status": "blocked", "reasonCode": "validation_failed", "reason": marker,
             "stdout": marker, "stderr": marker, "environment": {"SECRET": marker}}, time.time(), {})
        require(marker not in json.dumps(event))

    def deleted_secret():
        f = Fixture(module, fixture_root, "deleted-secret")
        f.put("settings.txt", 'api_key = "' + "xK8mP2qR7tV3wY9zB4cD6fG1hJ5nL0sA" + '"\n')
        git(f.repo, "add", "settings.txt")
        git(f.repo, "commit", "-m", "Local intermediate fixture")
        git(f.repo, "rm", "settings.txt")
        git(f.repo, "commit", "-m", "Remove local intermediate fixture")
        result = f.call()
        require(result.get("status") == "blocked" and f.head() == f.initial)

    def private_path():
        f = Fixture(module, fixture_root, "private-path")
        f.put(".env", "LOCAL_VALUE=harmless\n")
        result = f.call()
        require(result.get("status") == "blocked" and f.head() == f.initial)
        require(git(f.repo, "diff", "--cached", "--name-only") == "")

    def partial():
        f = Fixture(module, fixture_root, "partial")
        f.put("notes with spaces.md", "Staged harmless notes\n")
        git(f.repo, "add", "notes with spaces.md")
        tree = git(f.repo, "write-tree")
        f.put("notes with spaces.md", "Different unstaged notes\n")
        result = f.call()
        require(result.get("status") == "blocked" and f.head() == f.initial)
        require(git(f.repo, "write-tree") == tree)
        require((f.repo / "notes with spaces.md").read_text() == "Different unstaged notes\n")

    def binary():
        f = Fixture(module, fixture_root, "binary")
        (f.repo / "asset.bin").write_bytes(b"binary\0data")
        result = f.call()
        require(result.get("status") == "blocked" and f.head() == f.initial)

    def escape():
        f = Fixture(module, fixture_root, "escape")
        try:
            f.worker.repo("../remote.git")
        except module.Blocked:
            return
        raise AssertionError("Path escape accepted")

    def conflict():
        f = Fixture(module, fixture_root, "conflict")
        other = f.base / "other"
        git(f.base, "clone", str(f.remote), str(other))
        f.configure(other)
        (other / "notes with spaces.md").write_bytes(b"Remote harmless revision\n")
        git(other, "commit", "-am", "Remote fixture update")
        git(other, "push")
        f.put("notes with spaces.md", "Local harmless revision\n")
        git(f.repo, "commit", "-am", "Local fixture update")
        before = f.head()
        result = f.call()
        require(result.get("status") == "conflicts" and f.head() == before)
        content = f.call("read_conflict", path="notes with spaces.md")
        wrong = f.call("resolve_conflict", path="notes with spaces.md", content="Wrong\n", expectedSha256="0" * 64)
        require(wrong.get("status") == "blocked")
        fixed = f.call("resolve_conflict", path="notes with spaces.md",
                       content="Remote harmless revision\nLocal harmless revision\n", expectedSha256=content["sha256"])
        require(fixed.get("status") == "resolved-locally-pending-validation")
        result = f.call()
        require(result.get("status") == "pushed" and result.get("head") == f.head())
        require(len(git(f.repo, "show", "-s", "--format=%P", "HEAD").split()) == 2)

    for name, function in [("safe-pinned-push", safe_push), ("secret-before-staging", secret),
                           ("deleted-secret-history", deleted_secret), ("private-path", private_path),
                           ("partial-staging", partial), ("new-binary", binary),
                           ("path-escape", escape), ("owned-conflict", conflict)]:
        test("worker-hard-" + name, function)

    def failed_validation():
        f = Fixture(module, fixture_root, "failed-validation", [[sys.executable, "-c", "raise SystemExit(7)"]])
        f.put("notes with spaces.md", "Harmless validation-failure fixture\n")
        result = f.call()
        require(result.get("status") == "blocked" and f.head() == f.initial)
        require(git(f.repo, "diff", "--cached", "--name-only") == "")
        event = json.loads((f.worker.state / "operations.jsonl").read_text().splitlines()[-1])
        soft["coded-validation-block"] = result.get("reasonCode") == "validation_failed" and event.get("reasonCode") == "validation_failed"

    def noop():
        f = Fixture(module, fixture_root, "noop")
        result = f.call()
        require(result.get("status") == "clean" and f.head() == f.initial)
        soft["noop-no-invented-checks"] = (result.get("validationStatus") == "not-run"
            and result.get("validationReceipts") == [] and result.get("beforeHead") == f.initial
            and result.get("afterHead") == f.initial and result.get("remoteVerifiedSha") is None)

    # Additional behavior is always checked; existing baseline may lack only the
    # optional metadata. Failures are folded into hard safety, never hidden by a
    # zero utility score.
    for name, function in [("validation-failure-retains-work", failed_validation), ("noop-retains-identity", noop)]:
        test("worker-hard-" + name, function)
    hard_pass = all(item["passed"] for item in results)
    soft_names = ["inspect-branch-upstream", "inspect-typed-changes", "inspect-checks-not-run",
                  "validation-command-receipts", "publication-before-after-sha", "coded-validation-block",
                  "journal-public-receipts", "noop-no-invented-checks"]
    for name in soft_names:
        results.append({"id": "worker-soft-" + name, "passed": hard_pass, "score": 1.0 if soft.get(name) else 0.0})
    require(sha(source.read_bytes()) == before_source)
    require(sha(scanner_source.read_bytes()) == fixture["scannerSha256"])
    require(sha(resources.joinpath("bin/gitleaks.exe").read_bytes()) == fixture["scannerSha256"])
    return {"passed": hard_pass, "score": sum(bool(soft.get(name)) for name in soft_names) / len(soft_names),
            "cases": results, "observations": observations,
            "scope": "Disposable local Git behavior and public metadata coverage; no real-model quality claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    entries = json.loads(args.fixtures.read_text(encoding="utf-8"))
    fixture = None
    for entry in entries:
        path = Path(entry["path"])
        require(sha(path.read_bytes()) == entry["sha256"])
        if path.name == "worker-fixtures.json":
            fixture = json.loads(path.read_text(encoding="utf-8"))
    require(fixture is not None and fixture["version"] == 1 and fixture["kind"] == "custodian-worker-benchmark")
    result = run(args.project.resolve(strict=True), fixture, args.output_dir.resolve())
    print(json.dumps(result, separators=(",", ":")))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"passed": False, "score": 0.0,
                          "cases": [{"id": "worker-hard-harness-integrity", "passed": False, "score": 0.0}],
                          "errorCategory": type(error).__name__, "rawDiagnosticsSuppressed": True}))
        raise SystemExit(1)
