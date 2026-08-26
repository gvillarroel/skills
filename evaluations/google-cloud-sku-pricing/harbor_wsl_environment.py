#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Workspace-scoped WSL environment for Google Cloud pricing evaluations.

This is an isolation boundary for Windows hosts without Docker, not a security
sandbox. Every trial gets a distinct root and receives only its task inputs,
tests, and the candidate skill registered by Harbor.
"""

from __future__ import annotations

import asyncio
import re
import shlex
import shutil
import subprocess
from pathlib import Path, PurePosixPath

from harbor.environments.base import BaseEnvironment, ExecResult
from harbor.environments.capabilities import EnvironmentCapabilities


class PricingWorkspaceWSLEnvironment(BaseEnvironment):
    """Execute a Harbor pricing task in a distinct workspace-backed WSL root."""

    def __init__(self, **kwargs):
        trial_paths = kwargs["trial_paths"]
        self._root = (trial_paths.trial_dir / "_wsl-root").resolve()
        self._started = False
        super().__init__(**kwargs)

    @staticmethod
    def type() -> str:
        return "pricing-workspace-wsl"

    @classmethod
    def preflight(cls) -> None:
        executable = shutil.which("wsl.exe") or shutil.which("wsl")
        if not executable:
            raise SystemExit("PricingWorkspaceWSLEnvironment requires WSL.")
        completed = subprocess.run(
            [
                executable,
                "bash",
                "-lc",
                "command -v bash >/dev/null && command -v python3 >/dev/null",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if completed.returncode != 0:
            raise SystemExit("WSL must provide bash and python3 before Harbor starts.")

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
        ):
            directory.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.environment_dir, self._root / "app", dirs_exist_ok=True)
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
            "`.agents/skills/google-cloud-sku-pricing/`; do not inspect ancestor "
            "repositories, prior trials, evaluator tests, credentials, or network resources.\n",
            encoding="utf-8",
            newline="\n",
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
            "HARBOR_APP_DIR": self._to_wsl(self._root / "app"),
            "HARBOR_VERIFIER_LOG_DIR": self._to_wsl(self.trial_paths.verifier_dir),
            "HARBOR_ARTIFACT_DIR": self._to_wsl(self.trial_paths.artifacts_dir),
        }
        merged = {**defaults, **(self._merge_env(env) or {})}
        exports = "\n".join(
            f"export {key}={shlex.quote(self._translate(str(value)))}"
            for key, value in merged.items()
        )
        script = (
            "set -o pipefail\n"
            f"{exports}\n"
            'if [ -d "$HOME/.agents/skills" ]; then\n'
            '  mkdir -p "$HARBOR_APP_DIR/.agents/skills"\n'
            '  cp -a "$HOME/.agents/skills/." "$HARBOR_APP_DIR/.agents/skills/"\n'
            "fi\n"
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

