#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Workspace-scoped WSL environment for live terminal-video Harbor trials.

The adapter lets Harbor's Pi agent operate inside one isolated workspace while
the evaluated skill controls real Windows CLIs through WSL interoperability.
It is an evaluation boundary, not a security sandbox. Raw jobs and credentials
remain private local evidence.
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


class RecordingWorkspaceWSLEnvironment(BaseEnvironment):
    """Run one Pi/Harbor terminal-recording trial in a private WSL root."""

    def __init__(
        self,
        shared_cache_dir: str | None = None,
        skill_source_dir: str | None = None,
        recording_tools_dir: str | None = None,
        pi_auth_path: str | None = None,
        codex_auth_path: str | None = None,
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
        self._recording_tools = (
            Path(recording_tools_dir).resolve() if recording_tools_dir else None
        )
        self._pi_auth = Path(pi_auth_path).resolve() if pi_auth_path else None
        self._codex_auth = Path(codex_auth_path).resolve() if codex_auth_path else None
        self._started = False
        super().__init__(**kwargs)

    @staticmethod
    def type() -> str:
        return "recording-workspace-wsl"

    @classmethod
    def preflight(cls) -> None:
        executable = shutil.which("wsl.exe") or shutil.which("wsl")
        if not executable:
            raise SystemExit("RecordingWorkspaceWSLEnvironment requires WSL2.")
        completed = subprocess.run(
            [
                executable,
                "--",
                "bash",
                "-lc",
                "command -v bash >/dev/null && command -v uv >/dev/null "
                "&& command -v tmux >/dev/null && command -v script >/dev/null "
                "&& (command -v ffmpeg >/dev/null || command -v ffmpeg.exe >/dev/null) "
                "&& (command -v ffprobe >/dev/null || command -v ffprobe.exe >/dev/null)",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if completed.returncode != 0:
            raise SystemExit(
                "WSL must provide bash, uv, tmux, util-linux script, ffmpeg, and ffprobe."
            )

    @property
    def capabilities(self) -> EnvironmentCapabilities:
        return EnvironmentCapabilities(mounted=True)

    def _validate_definition(self) -> None:
        if not self.environment_dir.is_dir():
            raise FileNotFoundError(
                f"Task environment directory is missing: {self.environment_dir}"
            )
        self.preflight()
        if self._skill_source is None or not (self._skill_source / "SKILL.md").is_file():
            raise FileNotFoundError("A complete skill_source_dir is required.")
        if self._recording_tools is None or not self._recording_tools.is_dir():
            raise FileNotFoundError("A project-local recording_tools_dir is required.")
        for tool_name in ("asciinema", "agg"):
            if not (self._recording_tools / tool_name).is_file():
                raise FileNotFoundError(
                    f"Recording tool is missing: {self._recording_tools / tool_name}"
                )
        for label, path in (("Pi auth", self._pi_auth), ("Codex auth", self._codex_auth)):
            if path is not None and not path.is_file():
                raise FileNotFoundError(f"Configured {label} file is missing: {path}")

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
            ("/installed-agent", self._root / "installed-agent"),
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

    @staticmethod
    def _copy_private(source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        try:
            destination.chmod(0o600)
        except OSError:
            pass

    async def start(self, force_build: bool = False) -> None:
        del force_build
        self._validate_definition()
        self.trial_paths.mkdir()
        for directory in (
            self._root / "app",
            self._root / "tests",
            self._root / "solution",
            self._root / "harbor",
            self._root / "tmp",
            self._root / "home",
            self._root / "cache",
            self._root / "installed-agent" / "skills",
            self._shared_cache / "npm",
        ):
            directory.mkdir(parents=True, exist_ok=True)

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
            "Work only in this task workspace. Use only the evaluated "
            "`asciinema-real-command-video` skill. Do not inspect ancestor repositories, "
            "other installed skills, prior trials, or credentials. Never print environment "
            "variables or authentication files.\n",
            encoding="utf-8",
            newline="\n",
        )

        assert self._skill_source is not None
        for skill_parent in (
            self._root / "app" / ".agents" / "skills",
            self._root / "home" / ".agents" / "skills",
            self._root / "installed-agent" / "skills",
        ):
            destination = skill_parent / self._skill_source.name
            skill_parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(self._skill_source, destination, dirs_exist_ok=True)

        assert self._recording_tools is not None
        shutil.copytree(
            self._recording_tools,
            self._root / "app" / ".tools" / "asciinema",
            dirs_exist_ok=True,
        )
        if self._pi_auth is not None:
            self._copy_private(
                self._pi_auth, self._root / "home" / ".pi" / "agent" / "auth.json"
            )
        if self._codex_auth is not None:
            self._copy_private(
                self._codex_auth, self._root / "home" / ".codex" / "auth.json"
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
        if not self._started:
            await self.start(force_build=False)

        working_directory = self._host_path(cwd or "/app")
        working_directory.mkdir(parents=True, exist_ok=True)
        defaults = {
            "HOME": self._to_wsl(self._root / "home"),
            "CODEX_HOME": self._to_wsl(self._root / "home" / ".codex"),
            "XDG_CACHE_HOME": self._to_wsl(self._root / "cache"),
            "npm_config_cache": self._to_wsl(self._shared_cache / "npm"),
            "NPM_CONFIG_CACHE": self._to_wsl(self._shared_cache / "npm"),
            "HARBOR_APP_DIR": self._to_wsl(self._root / "app"),
            "HARBOR_VERIFIER_LOG_DIR": self._to_wsl(self.trial_paths.verifier_dir),
            "HARBOR_ARTIFACT_DIR": self._to_wsl(self.trial_paths.artifacts_dir),
            "ASCIINEMA_VIDEO_HARBOR": "1",
        }
        merged = {**defaults, **(self._merge_env(env) or {})}
        exports = "\n".join(
            f"export {key}={shlex.quote(self._translate(str(value)))}"
            for key, value in merged.items()
        )
        script = (
            "set -o pipefail\n"
            f"{exports}\n"
            f"cd {shlex.quote(self._to_wsl(working_directory))}\n"
            f"{self._translate(command)}"
        )
        executable = shutil.which("wsl.exe") or shutil.which("wsl") or "wsl.exe"
        arguments = [executable]
        if str(user).casefold() == "root":
            arguments.extend(["-u", "root"])
        arguments.extend(["--", "bash", "-s"])
        process = await asyncio.create_subprocess_exec(
            *arguments,
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


if __name__ == "__main__":
    RecordingWorkspaceWSLEnvironment.preflight()
    print("RecordingWorkspaceWSLEnvironment preflight passed.")
