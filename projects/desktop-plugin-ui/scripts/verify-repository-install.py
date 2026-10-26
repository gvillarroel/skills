#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify GitHub installation and native Pi discovery in isolated directories."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import threading
import time


ROOT = Path(__file__).resolve().parents[3]
AREA = ROOT / "projects/desktop-plugin-ui/artifacts/repository-install"
SKILL = "desktop-plugin-ui"
REPO = "gvillarroel/skills"


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def inventory(directory: Path) -> dict[str, str]:
    return {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.rglob("*")) if path.is_file()}


def execute(argv: list[str], cwd: Path, env: dict[str, str], receipt: Path,
            timeout: int = 300) -> dict:
    started = time.monotonic()
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=timeout)
    record = {"argv": argv, "cwd": str(cwd), "exitCode": result.returncode,
              "seconds": round(time.monotonic() - started, 3),
              "stdout": result.stdout, "stderr": result.stderr}
    save(receipt, record)
    if result.returncode:
        raise RuntimeError(f"Command failed; inspect {receipt.name}")
    return record


def pi_discovery(node: str, cli: Path, cwd: Path, env: dict[str, str], receipt: Path) -> Path:
    argv = [node, str(cli), "--mode", "rpc", "--offline", "--no-session",
            "--no-approve", "--no-context-files", "--no-mcp", "--no-extensions",
            "--no-prompt-templates", "--no-themes", "--no-builtin-tools"]
    process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", errors="replace", bufsize=1)
    lines: queue.Queue = queue.Queue()
    events, errors = [], []
    skill_file = None

    def read_stdout():
        for line in process.stdout:
            lines.put(line)
        lines.put(None)

    def read_stderr():
        errors.extend(process.stderr.readlines())

    stdout_thread = threading.Thread(target=read_stdout, daemon=True)
    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    try:
        process.stdin.write(json.dumps({"id": "installation-proof", "type": "get_commands"}) + "\n")
        process.stdin.flush()
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            line = lines.get(timeout=max(.1, deadline - time.monotonic()))
            if line is None:
                raise RuntimeError("Pi exited before registered skill discovery")
            event = json.loads(line)
            events.append(event)
            if event.get("type") in {"agent_start", "turn_start"}:
                raise RuntimeError("Discovery unexpectedly started a model turn")
            if event.get("type") == "response" and event.get("id") == "installation-proof":
                if not event.get("success"):
                    raise RuntimeError("Pi rejected command discovery")
                matches = [item for item in event.get("data", {}).get("commands", [])
                           if item.get("source") == "skill" and item.get("name") == f"skill:{SKILL}"]
                if len(matches) != 1:
                    raise RuntimeError("Expected exactly one installed skill command")
                source = matches[0].get("sourceInfo", {})
                if source.get("origin") != "package":
                    raise RuntimeError("Skill was not discovered through the installed package")
                skill_file = Path(source["path"]).resolve()
                agent_root = Path(env["PI_CODING_AGENT_DIR"]).resolve()
                if not skill_file.is_relative_to(agent_root) or skill_file.name != "SKILL.md":
                    raise RuntimeError("Discovered skill is outside isolated package storage")
                break
        if skill_file is None:
            raise RuntimeError("No installed skill discovery response")
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)
        save(receipt, {"argv": argv, "events": events, "stderr": "".join(errors),
                       "processClosed": process.poll() is not None,
                       "discoveredSkill": str(skill_file) if skill_file else None,
                       "modelStartEvents": sum(e.get("type") in {"agent_start", "turn_start"} for e in events)})
    return skill_file.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--ref", required=True, help="Published branch, tag or commit to install")
    parser.add_argument("--installer", type=Path, required=True, help="Existing Codex GitHub skill installer")
    parser.add_argument("--pi-cli", type=Path, help="Existing Pi JavaScript CLI; omit to skip native package discovery")
    parser.add_argument("--skip-codex", action="store_true", help="Continue only Pi verification after retained Codex transport passes")
    parser.add_argument("--methods", nargs="+", choices=("download", "git"), default=["download", "git"])
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,95}", args.run_id):
        parser.error("Use a lowercase hyphen-case run ID")
    run = AREA / args.run_id
    if run.exists():
        parser.error("Choose a fresh run ID; retained evidence is not overwritten")
    if not args.installer.is_file() or (args.pi_cli and not args.pi_cli.is_file()):
        parser.error("The supplied installed CLI must exist")
    if args.skip_codex and not args.pi_cli:
        parser.error("--skip-codex requires --pi-cli")
    run.mkdir(parents=True)
    workspace, temporary = run / "workspace with spaces", run / "temporary"
    workspace.mkdir()
    temporary.mkdir()
    essentials = {"PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "HOME", "USERPROFILE",
                  "APPDATA", "LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)", "LANG", "LC_ALL",
                  "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"}
    env = {key: value for key, value in os.environ.items() if key.upper() in essentials}
    env.update(TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary),
               PYTHONDONTWRITEBYTECODE="1", GIT_TERMINAL_PROMPT="0", UV_CACHE_DIR=str(run / "uv-cache"))
    if os.name == "nt":
        # Artifact isolation adds a much longer prefix than a normal Pi install.
        # Supply Git's Windows support to this process only, without global config.
        env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.longpaths", GIT_CONFIG_VALUE_0="true")
    canonical = ROOT / "skills" / SKILL
    expected = inventory(canonical)
    checks = []

    def check(name: str, passed: bool, detail: object = None):
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            raise RuntimeError(name)

    summary = {"startedAtUtc": datetime.now(timezone.utc).isoformat(), "repository": REPO,
               "ref": args.ref, "skill": SKILL, "canonicalFiles": len(expected),
               "codexTransports": [] if args.skip_codex else list(dict.fromkeys(args.methods)),
               "processOnlyGitLongpaths": os.name == "nt",
               "checks": checks, "scope": "Repository installation, bundle integrity and native discovery only; no model task or plugin frontend acceptance."}
    save(run / "source-before.json", expected)
    try:
        for method in ([] if args.skip_codex else dict.fromkeys(args.methods)):
            destination = run / f"codex-{method}" / "skills"
            execute([shutil.which("python"), str(args.installer), "--url",
                     f"https://github.com/{REPO}/tree/{args.ref}/skills/{SKILL}",
                     "--method", method, "--dest", str(destination)], workspace, env, run / f"codex-{method}.json")
            installed = destination / SKILL
            check(f"codex-{method}-all-files-exact", inventory(installed) == expected,
                  {"files": len(inventory(installed))})
            execute([shutil.which("uv"), "run", "--script", str(ROOT / "scripts/validate-skills.py"),
                     "--skill", str(installed)], workspace, env, run / f"codex-{method}-validation.json")
            execute([shutil.which("python"), str(installed / "scripts/probe_runtime.py"), "--host", "pi"],
                    workspace, env, run / f"codex-{method}-probe.json")
            check(f"codex-{method}-read-only-execution", inventory(installed) == expected)

        if args.pi_cli:
            agent = run / "isolated pi"
            env["PI_CODING_AGENT_DIR"] = str(agent)
            source = f"git:github.com/{REPO}@{args.ref}"
            node = shutil.which("node")
            registered = False
            try:
                execute([node, str(args.pi_cli), "install", source], workspace, env, run / "pi-install.json")
                registered = True
                execute([node, str(args.pi_cli), "list"], workspace, env, run / "pi-list.json")
                installed = pi_discovery(node, args.pi_cli, workspace, env, run / "pi-discovery.json")
                check("pi-registered-package-discovery", inventory(installed) == expected,
                      {"skillRoot": str(installed), "files": len(inventory(installed))})
                settings = json.loads((agent / "settings.json").read_text(encoding="utf-8"))
                check("pi-isolated-registration", source in settings.get("packages", []))
            finally:
                if registered:
                    execute([node, str(args.pi_cli), "remove", source], workspace, env, run / "pi-remove.json")
                    settings = json.loads((agent / "settings.json").read_text(encoding="utf-8"))
                    check("pi-registration-cleanup", not settings.get("packages"))
        check("canonical-source-unchanged", inventory(canonical) == expected)
        summary["passed"] = True
    except Exception as error:
        summary.update(passed=False, error=f"{type(error).__name__}: {error}")
    summary["finishedAtUtc"] = datetime.now(timezone.utc).isoformat()
    save(run / "summary.json", summary)
    print(json.dumps({"passed": summary["passed"], "checks": len(checks), "report": str(run / "summary.json")}))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
