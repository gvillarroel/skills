#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Workspace-scoped WSL environment adapter for native D3 Harbor evaluations.

This adapter exists for Windows workstations where Harbor's default Docker
environment is unavailable. Each trial receives a distinct root below its
native Harbor trial directory. The adapter maps Harbor's Linux paths into that
root and executes commands through the installed WSL distribution.

It is an evaluation isolation boundary, not a security sandbox. Evaluation
prompts and trace review must still forbid ambient repository discovery.
"""

from __future__ import annotations

import asyncio
import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path, PurePosixPath

from harbor.environments.base import BaseEnvironment, ExecResult
from harbor.environments.capabilities import EnvironmentCapabilities


CODEX_BIN_RELATIVE = Path("codex-0.147.0") / "node_modules" / ".bin"


class WorkspaceWSLEnvironment(BaseEnvironment):
    """Run one Harbor trial in a distinct workspace-backed WSL root."""

    def __init__(
        self,
        shared_cache_dir: str | None = None,
        skill_source_dir: str | None = None,
        playwright_core_path: str | None = None,
        **kwargs,
    ):
        trial_paths = kwargs["trial_paths"]
        self._root = (trial_paths.trial_dir / "_wsl-root").resolve()
        self._shared_cache = (
            Path(shared_cache_dir).resolve()
            if shared_cache_dir
            else (trial_paths.trial_dir.parent / "_wsl-cache").resolve()
        )
        self._skill_source = Path(skill_source_dir).resolve() if skill_source_dir else None
        self._playwright_core = self._resolve_playwright_core(playwright_core_path)
        self._started = False
        super().__init__(**kwargs)

    def _resolve_playwright_core(self, explicit: str | None) -> Path | None:
        candidates: list[Path] = []
        for value in (
            explicit,
            os.environ.get("HARBOR_PLAYWRIGHT_CORE_PATH"),
        ):
            if value:
                candidates.append(Path(value).expanduser())
        cache_roots = [
            self._shared_cache / "npm",
            Path(os.environ.get("LOCALAPPDATA", "")) / "npm-cache",
            Path(os.environ.get("USERPROFILE", "")) / ".npm",
        ]
        for cache_root in cache_roots:
            npx_root = cache_root / "_npx"
            if not npx_root.is_dir():
                continue
            candidates.extend(npx_root.glob("*/node_modules/playwright-core"))
        valid = [
            candidate.resolve()
            for candidate in candidates
            if (candidate / "package.json").is_file()
        ]
        if not valid:
            return None
        return max(valid, key=lambda path: (path / "package.json").stat().st_mtime_ns)

    @staticmethod
    def type() -> str:
        return "workspace-wsl"

    @classmethod
    def preflight(cls) -> None:
        executable = shutil.which("wsl.exe") or shutil.which("wsl")
        if not executable:
            raise SystemExit("WorkspaceWSLEnvironment requires WSL.")
        completed = subprocess.run(
            [executable, "bash", "-lc", "command -v bash >/dev/null && command -v codex >/dev/null"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if completed.returncode != 0:
            raise SystemExit("WSL must provide bash and codex before Harbor starts.")

    @property
    def capabilities(self) -> EnvironmentCapabilities:
        return EnvironmentCapabilities(mounted=True)

    def _validate_definition(self) -> None:
        if not self.environment_dir.is_dir():
            raise FileNotFoundError(f"Task environment directory is missing: {self.environment_dir}")
        self.preflight()

    @staticmethod
    def _to_wsl(path: Path) -> str:
        resolved = path.resolve()
        drive = resolved.drive
        if not drive or len(drive) < 2 or drive[1] != ":":
            raise ValueError(f"Only drive-letter Windows paths are supported: {resolved}")
        tail = resolved.as_posix().split(":", 1)[1]
        return f"/mnt/{drive[0].lower()}{tail}"

    def _virtual_roots(self) -> tuple[tuple[str, Path], ...]:
        return (
            ("/logs/artifacts", self.trial_paths.artifacts_dir),
            ("/logs/verifier", self.trial_paths.verifier_dir),
            ("/logs/agent", self.trial_paths.agent_dir),
            ("/harbor", self._root / "harbor"),
            ("/solution", self._root / "solution"),
            ("/tests", self._root / "tests"),
            ("/app", self._root / "app"),
            ("/logs", self.trial_paths.trial_dir),
            ("/tmp", self._root / "tmp"),
        )

    def _host_path(self, virtual_path: str) -> Path:
        normalized = str(PurePosixPath(virtual_path))
        if not normalized.startswith("/"):
            return (self._root / "app" / normalized).resolve()
        for prefix, target in self._virtual_roots():
            if normalized == prefix:
                return target.resolve()
            if normalized.startswith(prefix + "/"):
                relative = normalized[len(prefix) + 1 :]
                return (target / Path(*PurePosixPath(relative).parts)).resolve()
        if normalized == "/":
            return self._root
        raise ValueError(f"Unsupported environment path: {virtual_path}")

    def _translate(self, value: str) -> str:
        translated = value
        for prefix, target in self._virtual_roots():
            translated = re.sub(
                rf"(?<![A-Za-z0-9_.-]){re.escape(prefix)}(?=$|[/\s'\";:,)])",
                self._to_wsl(target),
                translated,
            )
        return translated

    async def start(self, force_build: bool = False) -> None:
        del force_build
        self.trial_paths.mkdir()
        for directory in (
            self._root / "app",
            self._root / "tests",
            self._root / "solution",
            self._root / "harbor",
            self._root / "tmp",
            self._root / "home",
            self._root / "cache",
            self._shared_cache / "npm",
            self._shared_cache / "puppeteer",
        ):
            directory.mkdir(parents=True, exist_ok=True)
        # Make the trial app a repository boundary. Without this sentinel,
        # Codex walks into the parent source repository and advertises ambient
        # AGENTS.md files and locally installed skills, invalidating isolation.
        git_dir = self._root / "app" / ".git"
        git_dir.mkdir(parents=True, exist_ok=True)
        (git_dir / "HEAD").write_text(
            "ref: refs/heads/harbor-isolated\n", encoding="utf-8", newline="\n"
        )
        (git_dir / "config").write_text(
            "[core]\n\trepositoryformatversion = 0\n\tbare = false\n",
            encoding="utf-8",
            newline="\n",
        )
        (self._root / "app" / "AGENTS.md").write_text(
            "# Isolated Harbor Task\n\n"
            "Work only in this task workspace. Read only the evaluated skill under "
            "`.agents/skills/d3/`; do not inspect ancestor repositories, prior trials, "
            "or other skill installations.\n",
            encoding="utf-8",
            newline="\n",
        )
        if self._skill_source is not None:
            if not (self._skill_source / "SKILL.md").is_file():
                raise FileNotFoundError(
                    f"Evaluated skill source is missing SKILL.md: {self._skill_source}"
                )
            for skill_parent in (
                self._root / "app" / ".agents" / "skills",
                self._root / "home" / ".agents" / "skills",
            ):
                destination = skill_parent / self._skill_source.name
                skill_parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(self._skill_source, destination, dirs_exist_ok=True)
        if self._playwright_core is None:
            raise FileNotFoundError(
                "playwright-core is required for the D3 browser verifier; "
                "set HARBOR_PLAYWRIGHT_CORE_PATH or populate an npm _npx cache"
            )
        self._started = True

    async def stop(self, delete: bool) -> None:
        self._started = False
        if not delete or not self._root.exists():
            return
        trial_root = self.trial_paths.trial_dir.resolve()
        resolved = self._root.resolve()
        if resolved.parent != trial_root or resolved.name != "_wsl-root":
            raise ValueError(f"Refusing to remove unexpected WSL root: {resolved}")
        shutil.rmtree(resolved)

    async def upload_file(self, source_path: Path | str, target_path: str) -> None:
        source = Path(source_path).resolve()
        target = self._host_path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    async def upload_dir(self, source_dir: Path | str, target_dir: str) -> None:
        source = Path(source_dir).resolve()
        target = self._host_path(target_dir)
        target.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, dirs_exist_ok=True)

    async def download_file(self, source_path: str, target_path: Path | str) -> None:
        source = self._host_path(source_path)
        target = Path(target_path).resolve()
        if source == target:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    async def download_dir(self, source_dir: str, target_dir: Path | str) -> None:
        source = self._host_path(source_dir)
        target = Path(target_dir).resolve()
        if source == target:
            return
        target.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, dirs_exist_ok=True)

    async def exec(
        self,
        command: str,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout_sec: int | None = None,
        user: str | int | None = None,
    ) -> ExecResult:
        del user
        if not self._started:
            await self.start(force_build=False)

        working_directory = self._host_path(cwd or "/app")
        working_directory.mkdir(parents=True, exist_ok=True)
        defaults = {
            "HOME": self._to_wsl(self._root / "home"),
            "XDG_CACHE_HOME": self._to_wsl(self._root / "cache"),
            "npm_config_cache": self._to_wsl(self._shared_cache / "npm"),
            "NPM_CONFIG_CACHE": self._to_wsl(self._shared_cache / "npm"),
            "PUPPETEER_CACHE_DIR": self._to_wsl(self._shared_cache / "puppeteer"),
            "HARBOR_APP_DIR": self._to_wsl(self._root / "app"),
            "HARBOR_VERIFIER_LOG_DIR": self._to_wsl(self.trial_paths.verifier_dir),
            "HARBOR_ARTIFACT_DIR": self._to_wsl(self.trial_paths.artifacts_dir),
            "HARBOR_PLAYWRIGHT_CORE_PATH": self._to_wsl(self._playwright_core),
        }
        merged = {**defaults, **(self._merge_env(env) or {})}
        exports = "\n".join(
            f"export {key}={shlex.quote(self._translate(str(value)))}"
            for key, value in merged.items()
        )
        script = (
            "set -o pipefail\n"
            f"{exports}\n"
            # Harbor registers the evaluated bundle under the isolated HOME.
            # Mirror it into the trial workspace before Codex starts so the
            # nearest project-local skill wins over any ambient repository
            # installation in an ancestor directory.
            'if [ -d "$HOME/.agents/skills" ]; then\n'
            '  if [ ! -f "$HARBOR_APP_DIR/.agents/skills/d3/SKILL.md" ]; then\n'
            '    mkdir -p "$HARBOR_APP_DIR/.agents/skills"\n'
            '    cp -a "$HOME/.agents/skills/." "$HARBOR_APP_DIR/.agents/skills/"\n'
            '  fi\n'
            # Codex 0.147 can advertise a registered Harbor skill under its
            # system-skill locator even though Harbor installed it in HOME.
            # Populate that advertised locator so agents never need to search
            # an ambient parent repository after a stale-path read fails.
            '  if [ -n "${CODEX_HOME:-}" ]; then\n'
            '    if [ ! -f "$CODEX_HOME/skills/.system/d3/SKILL.md" ]; then\n'
            '      mkdir -p "$CODEX_HOME/skills/.system"\n'
            '      cp -a "$HOME/.agents/skills/." "$CODEX_HOME/skills/.system/"\n'
            '    fi\n'
            "  fi\n"
            "fi\n"
            'if [ -z "${HARBOR_BROWSER_PATH:-}" ]; then\n'
            "  export HARBOR_BROWSER_PATH=\"$(find /home -path '*/.cache/ms-playwright/chromium-*/chrome-linux*/chrome' -type f -perm -111 2>/dev/null | sort | tail -n 1)\"\n"
            "fi\n"
            f"export PATH={shlex.quote(self._to_wsl(self._shared_cache / CODEX_BIN_RELATIVE))}:$PATH\n"
            f"cd {shlex.quote(self._to_wsl(working_directory))}\n"
            f"{self._translate(command)}"
        )
        executable = shutil.which("wsl.exe") or shutil.which("wsl") or "wsl.exe"
        process = await asyncio.create_subprocess_exec(
            executable,
            "bash",
            "-s",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(script.encode("utf-8")), timeout=timeout_sec
            )
        except TimeoutError:
            process.kill()
            stdout_bytes, stderr_bytes = await process.communicate()
            stderr_bytes += f"\nCommand timed out after {timeout_sec} seconds.".encode()
            return_code = 124
        else:
            return_code = process.returncode or 0

        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")
        callback = self._output_callback()
        if callback:
            if stdout:
                await callback(stdout, "stdout")
            if stderr:
                await callback(stderr, "stderr")
        return ExecResult(stdout=stdout, stderr=stderr, return_code=return_code)
