#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Read-only checks for an independent agent lifecycle forward trial."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import os


def process_exists(pid: int) -> bool:
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() != 87
        try:
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                return True
            return code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def evaluate(workspace: Path) -> dict:
    workspace = workspace.resolve(strict=True)
    output = workspace / "outputs"
    project = output / "workspace with spaces/.pi/durable/lifecycle-eval"
    checks: list[dict] = []

    def check(name, function):
        try:
            checks.append({"name": name, "passed": True, "detail": function()})
        except Exception as error:
            checks.append({"name": name, "passed": False, "error": str(error)})

    def payload():
        manifest = json.loads((output / "console/scaffold-manifest.json").read_text(encoding="utf-8"))
        assert manifest["runtimeIndependent"] and manifest["agentCreationIncluded"]
        for name, digest in manifest["files"].items():
            path = (output / "console" / name).resolve(strict=True)
            assert path.is_relative_to((output / "console").resolve())
            if name == "durable-agents.json":
                continue  # This connection registry legitimately changes when creation registers an owner.
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
            source = workspace / "skills/pi-durable/assets/templates"
            original = source / "service" / name.removeprefix("service-template/") if name.startswith("service-template/") else source / "pi-extension" / name
            assert original.is_file() and original.read_bytes() == path.read_bytes(), name
        creation = json.loads((project / "creation-receipt.json").read_text(encoding="utf-8"))
        registry_path = Path(creation["connectionsFile"]).resolve(strict=True)
        assert registry_path.is_relative_to(workspace) and creation["registered"] is True
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        assert registry["version"] == 1 and len(registry["services"]) == 1
        connection = registry["services"][0]
        assert connection["id"] == "lifecycle-eval"
        assert (registry_path.parent / connection["configPath"]).resolve() == project.resolve() / "config.json"
        descriptor = json.loads((project / "managed-agent.json").read_text(encoding="utf-8"))
        assert descriptor["agentId"] == "lifecycle-eval" and descriptor["kind"] == "pi-durable-console-managed"
        assert hashlib.sha256((project / descriptor["hostFile"]).read_bytes()).hexdigest() == descriptor["hostSha256"]
        for name in ("dist/src/console/control-cli.js", "dist/src/console/agent-management.js", "dist/src/verify-cli.js", "verification-contract.json"):
            assert (project / name).is_file(), name
        return {"consoleFiles": len(manifest["files"]), "independentControlPresent": True}

    def lifecycle():
        result = json.loads((output / "lifecycle.json").read_text(encoding="utf-8"))
        assert result["agentId"] == "lifecycle-eval" and Path(result["projectDir"]).resolve() == project.resolve()
        assert result["pausedRefused"] is True and result["independentCliUsed"] is True
        assert result["conversationIdBefore"] == result["conversationIdAfter"] and result["conversationIdBefore"] > 0
        assert result["finalState"] == "stopped" and result["pidAlive"] is False
        assert isinstance(result["stoppedPid"], int) and result["stoppedPid"] > 0
        owner = json.loads((project / "state/last-owner.json").read_text(encoding="utf-8"))
        assert owner["pid"] == result["stoppedPid"] and Path(owner["configPath"]).resolve() == project.resolve() / "config.json"
        assert not process_exists(owner["pid"]), "The last owned process is still alive."
        assert {"running", "paused", "stopped"}.issubset(result["states"])
        assert not (project / "state/creation-owner.json").exists(), "Active owner receipt remains."
        config = json.loads((project / "config.json").read_text(encoding="utf-8"))
        assert config["provider"]["kind"] == "faux" and config["github"]["mode"] == "off"
        assert Path(config["agents"][0]["workspaceRoot"]).resolve() == (output / "workspace with spaces").resolve()
        db = sqlite3.connect((project / "state/owner.sqlite").as_uri() + "?mode=rw", uri=True, timeout=0)
        try:
            db.execute("BEGIN EXCLUSIVE")
            db.rollback()
        finally:
            db.close()
        return {"stateOwnerLockReleased": True, "conversation": result["conversationIdAfter"]}

    def verification():
        value = json.loads((output / "verification.json").read_text(encoding="utf-8"))
        positive, negative = value["positive"], value["negative"]
        assert positive["status"] == "passed" and negative["status"] == "failed"
        assert positive["agentId"] == negative["agentId"] == "lifecycle-eval"
        assert positive["conversationId"] == negative["conversationId"] and positive["submissionId"] == negative["submissionId"]
        assert positive["outputSha256"] == negative["outputSha256"]
        assert positive["contractSha256"] != negative["contractSha256"]
        db = sqlite3.connect((project / "state/evidence.sqlite").as_uri() + "?mode=ro", uri=True)
        try:
            for receipt in (positive, negative):
                row = db.execute("SELECT record FROM evidence WHERE id=? AND agentId=? AND kind='verification.completed'", (receipt["evidenceId"], "lifecycle-eval")).fetchone()
                assert row, "Verification was not persisted in the actual evidence ledger."
                record = json.loads(row[0])
                assert record["submissionId"] == receipt["submissionId"] and record["details"]["status"] == receipt["status"]
                for field in ("outputSha256", "contractSha256"):
                    assert record["details"][field] == receipt[field]
                assert receipt["evidenceIds"] and receipt["sourceVersion"]["conversationVersion"]["digest"]
        finally:
            db.close()
        receipts = [json.loads(path.read_text(encoding="utf-8")) for path in (project / "state/quality/lifecycle-eval").glob("*.json")]
        assert {positive["id"], negative["id"]}.issubset({receipt["id"] for receipt in receipts})
        return {"boundTask": positive["submissionId"], "positiveAndNegativePersisted": True}

    def handoff():
        text = (output / "report.md").read_text(encoding="utf-8")
        for name in ("/durable", "verify", "evolve", "rollback", "login", "macOS"):
            assert name.lower() in text.lower(), name
        assert len(text) > 700
        return {"characters": len(text)}

    check("Independent console and owned project", payload)
    check("Lifecycle observations and released real state owner", lifecycle)
    check("Actual positive/negative task receipts", verification)
    check("Operational and evolution handoff", handoff)
    return {"passed": all(item["passed"] for item in checks), "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(args.workspace)
    if args.output:
        target = args.output.resolve()
        if target.exists() or target.is_relative_to(args.workspace.resolve()):
            parser.error("Use a new receipt path outside the candidate workspace.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
