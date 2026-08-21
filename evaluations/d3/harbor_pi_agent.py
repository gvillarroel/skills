#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Harbor adapter for the installed Windows Pi runtime used by D3 trials."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import shlex
from typing import override

from harbor.agents.installed.base import with_prompt_template
from harbor.agents.installed.pi import Pi
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


PROVIDER_ENV_KEYS = {
    "anthropic": ("ANTHROPIC_API_KEY", "ANTHROPIC_OAUTH_TOKEN"),
    "google": (
        "GEMINI_API_KEY",
        "GOOGLE_GENERATIVE_AI_API_KEY",
        "GOOGLE_API_KEY",
    ),
    "openai": ("OPENAI_API_KEY",),
    "openrouter": ("OPENROUTER_API_KEY",),
}


class WorkspaceWindowsPi(Pi):
    """Run Pi on Windows while Harbor keeps task files in isolated WSL roots."""

    def __init__(
        self,
        wrapper_path: str,
        skill_path: str = ".agents/skills/d3",
        expected_version: str = "0.84.2",
        **kwargs,
    ) -> None:
        self._wrapper_path = Path(wrapper_path).resolve()
        self._skill_path = skill_path
        self._expected_version = expected_version
        if not self._wrapper_path.is_file():
            raise FileNotFoundError(f"Pi wrapper is missing: {self._wrapper_path}")
        super().__init__(**kwargs)

    def _wrapper_command(self, *arguments: str) -> str:
        return shlex.join(["python.exe", self._wrapper_path.as_posix(), *arguments])

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

        skills_command = self._build_register_skills_command()
        if skills_command:
            await self.exec_as_agent(environment, command=skills_command)

        env = {
            key: value
            for key in PROVIDER_ENV_KEYS.get(provider, ())
            if (value := os.environ.get(key))
        }
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
                self._skill_path,
                "--output",
                output_path,
            ),
            env=env,
        )

    @override
    def populate_context_post_run(self, context: AgentContext) -> None:
        """Read Pi's UTF-8 JSONL deterministically on Windows."""

        output_file = self.logs_dir / self._OUTPUT_FILENAME
        if not output_file.exists():
            return

        total_input_tokens = 0
        total_output_tokens = 0
        total_cache_read_tokens = 0
        total_cache_write_tokens = 0
        total_cost = 0.0
        for line in output_file.read_text(
            encoding="utf-8", errors="replace"
        ).splitlines():
            try:
                event = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                continue
            if event.get("type") != "message_end":
                continue
            message = event.get("message") or {}
            if message.get("role") != "assistant":
                continue
            usage = message.get("usage") or {}
            total_input_tokens += usage.get("input", 0)
            total_output_tokens += usage.get("output", 0)
            total_cache_read_tokens += usage.get("cacheRead", 0)
            total_cache_write_tokens += usage.get("cacheWrite", 0)
            total_cost += (usage.get("cost") or {}).get("total", 0.0)

        context.n_input_tokens = total_input_tokens + total_cache_read_tokens
        context.n_output_tokens = total_output_tokens
        context.n_cache_tokens = total_cache_read_tokens
        context.cost_usd = total_cost if total_cost > 0 else None
