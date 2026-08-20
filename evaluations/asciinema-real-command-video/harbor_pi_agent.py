#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Harbor Pi adapter that uses the already-installed Windows Pi runtime."""

from __future__ import annotations

import base64
from pathlib import Path
import shlex
from typing import override

from harbor.agents.installed.base import with_prompt_template
from harbor.agents.installed.pi import Pi
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class WorkspaceWindowsPi(Pi):
    """Run Pi on Windows while Harbor keeps task commands in workspace WSL."""

    def __init__(
        self,
        wrapper_path: str,
        expected_version: str = "0.84.2",
        **kwargs,
    ) -> None:
        self._wrapper_path = Path(wrapper_path).resolve()
        self._expected_version = expected_version
        if not self._wrapper_path.is_file():
            raise FileNotFoundError(f"Pi wrapper is missing: {self._wrapper_path}")
        super().__init__(**kwargs)

    def _wrapper_command(self, *arguments: str) -> str:
        return shlex.join(
            ["python.exe", self._wrapper_path.as_posix(), *arguments]
        )

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        await self.exec_as_agent(
            environment,
            command=self._wrapper_command(
                "check", "--expected-version", self._expected_version
            ),
        )

    @override
    @with_prompt_template
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        del context
        if not self.model_name or "/" not in self.model_name:
            raise ValueError("model_name must use provider/model format")
        provider, model = self.model_name.split("/", 1)
        if provider != "openai-codex":
            raise ValueError("WorkspaceWindowsPi is fixed to the openai-codex provider")

        skills_command = self._build_register_skills_command()
        if skills_command:
            await self.exec_as_agent(environment, command=skills_command)

        prompt_base64 = base64.b64encode(instruction.encode("utf-8")).decode("ascii")
        thinking = str(self._resolved_flags.get("thinking", "high"))
        output_path = (self.logs_dir / self._OUTPUT_FILENAME).resolve().as_posix()
        await self.exec_as_agent(
            environment,
            command=self._wrapper_command(
                "run",
                "--expected-version",
                self._expected_version,
                "--prompt-base64",
                prompt_base64,
                "--provider",
                provider,
                "--model",
                model,
                "--thinking",
                thinking,
                "--skill-path",
                ".agents/skills/asciinema-real-command-video",
                "--output",
                output_path,
            ),
        )
