#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Install only desktop-plugin-ui from GitHub and verify automatic Pi discovery."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("repository_install", Path(__file__).with_name("verify-repository-install.py"))
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--skills-version", required=True, help="Explicit npm skills CLI version")
    parser.add_argument("--npm-cli", type=Path, required=True)
    parser.add_argument("--pi-cli", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,95}", args.run_id):
        parser.error("Use a lowercase hyphen-case run ID")
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.skills_version):
        parser.error("Supply an exact stable CLI version")
    run = ROOT / "projects/desktop-plugin-ui/artifacts/single-skill-install" / args.run_id
    if run.exists() or not args.npm_cli.is_file() or not args.pi_cli.is_file():
        parser.error("Use a new run ID and existing installed CLI paths")
    workspace, temporary = run / "project with spaces", run / "temporary"
    workspace.mkdir(parents=True)
    temporary.mkdir()
    npm_config = run / "empty.npmrc"
    npm_config.write_text("", encoding="utf-8")
    essentials = {"PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "HOME", "USERPROFILE",
                  "APPDATA", "LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)", "LANG", "LC_ALL",
                  "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"}
    env = {key: value for key, value in os.environ.items() if key.upper() in essentials}
    env.update(TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary),
               PI_CODING_AGENT_DIR=str(run / "isolated pi"), PYTHONDONTWRITEBYTECODE="1",
               npm_config_cache=str(run / "npm-cache"), npm_config_userconfig=str(npm_config),
               npm_config_update_notifier="false", DISABLE_TELEMETRY="1", DO_NOT_TRACK="1",
               GIT_TERMINAL_PROMPT="0", CI="1", UV_CACHE_DIR=str(run / "uv-cache"))
    if os.name == "nt":
        env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.longpaths", GIT_CONFIG_VALUE_0="true")
    node = shutil.which("node")
    canonical = ROOT / "skills/desktop-plugin-ui"
    before = HELPER.inventory(canonical)
    checks = []

    def check(name, passed, detail=None):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise RuntimeError(name)

    result = {"source": "gvillarroel/skills", "skill": "desktop-plugin-ui",
              "skillsCliVersion": args.skills_version, "checks": checks,
              "scope": "One selected project skill, exact files and actual Pi discovery; no model task or global installation."}
    try:
        HELPER.execute([shutil.which("git"), "init", "-q"], workspace, env, run / "git-init.json")
        HELPER.execute([node, str(args.npm_cli), "exec", "--yes", f"--package=skills@{args.skills_version}",
                        "--", "skills", "add", "gvillarroel/skills", "--skill", "desktop-plugin-ui",
                        "--agent", "pi", "--copy", "--yes"], workspace, env, run / "install.json")
        installed = workspace / ".agents/skills/desktop-plugin-ui"
        check("only-selected-skill-installed", sorted(p.name for p in installed.parent.iterdir()) == ["desktop-plugin-ui"])
        check("all-source-files-identical", HELPER.inventory(installed) == before, {"files": len(before)})
        check("real-copy-not-symlink", not installed.is_symlink())
        lock = json.loads((workspace / "skills-lock.json").read_text(encoding="utf-8"))
        check("lock-contains-only-selected-skill", set(lock.get("skills", {})) == {"desktop-plugin-ui"})
        HELPER.save(run / "lock.json", lock)
        found = HELPER.pi_discovery(node, args.pi_cli, workspace, env, run / "pi-discovery.json",
                                    expected_project_skill=installed)
        check("automatic-pi-project-discovery", found == installed)
        HELPER.execute([shutil.which("uv"), "run", "--script", str(ROOT / "scripts/validate-skills.py"),
                        "--skill", str(installed)], workspace, env, run / "standalone-validation.json")
        check("installed-source-remains-unchanged", HELPER.inventory(installed) == before)
        check("canonical-source-remains-unchanged", HELPER.inventory(canonical) == before)
        check("no-pi-package-collection-registration", not (run / "isolated pi/settings.json").exists() or
              not json.loads((run / "isolated pi/settings.json").read_text()).get("packages"))
        result["passed"] = True
    except Exception as error:
        result.update(passed=False, error=f"{type(error).__name__}: {error}")
    HELPER.save(run / "summary.json", result)
    print(json.dumps({"passed": result["passed"], "checks": len(checks), "report": str(run / "summary.json")}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
