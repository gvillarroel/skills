#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Native Harbor Pi adapter for one derived runtime skill in a Windows workspace."""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

from harbor.agents.installed.base import with_prompt_template
from harbor.agents.installed.pi import Pi
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class SemanticWindowsPi(Pi):
    def __init__(self, wrapper_path: str, expected_version: str = "1.4.0", skill_name: str = "curate-semantic-model", **kwargs):
        self._wrapper = Path(wrapper_path).resolve()
        self._expected_version = expected_version
        self._skill_name = skill_name
        if not self._wrapper.is_file():
            raise FileNotFoundError("The study's Windows Pi wrapper is missing")
        super().__init__(**kwargs)

    @staticmethod
    def _event_helpers():
        helper_path = Path(__file__).resolve().parents[3] / "scripts" / "run-pi-skill-eval.py"
        spec = importlib.util.spec_from_file_location("semantic_existing_pi_harness", helper_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module

    def _audit_trace(self, environment, instruction: str) -> dict:
        """Use the repository's existing strict Pi policy in its native layout."""
        source = self.logs_dir / self._OUTPUT_FILENAME
        copied = environment._root / "events.jsonl"
        shutil.copy2(source, copied)
        helpers = self._event_helpers()
        patterns = helpers.strict_forbidden_read_patterns(self._skill_name, "runtime")
        report = helpers.event_check_report(
            events_path=copied, prompt=instruction,
            require_prompt_read_first=True, require_exact_command_from_prompt=False,
            require_observed_model=True, requested_model=self.model_name,
            fail_on_invalid_json=True, fail_on_tool_error=True,
            forbid_read_regex=patterns, forbid_command_regex=[],
        )
        report["source_events_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        report["audited_copy_sha256"] = hashlib.sha256(copied.read_bytes()).hexdigest()
        report["boundary"] = "Trace-audited workspace isolation; no OS sandbox claim. Shell commands need supplementary evaluator review."
        (self.logs_dir / "trace-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        summary_path = self.logs_dir / "trace-summary.json"
        summarizer = Path(__file__).resolve().parents[3] / "scripts" / "summarize-pi-json-events.py"
        command = [sys.executable, str(summarizer), str(copied), "--output", str(summary_path), "--require-model", "gpt-6.1-sol", "--require-tool-call", "--require-read", "../prompt.md", "--fail-on-invalid-json", "--fail-on-tool-error"]
        for pattern in patterns:
            command.extend(["--forbid-read-regex", pattern])
        result = subprocess.run(command, capture_output=True, timeout=30)
        (self.logs_dir / "trace-summary-stdout.txt").write_bytes(result.stdout)
        (self.logs_dir / "trace-summary-stderr.txt").write_bytes(result.stderr)
        if result.returncode:
            report["passed"] = False
            report["findings"].append({"code": "existing-trace-summary-failed", "return_code": result.returncode})
            (self.logs_dir / "trace-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report

    def _command(self, *arguments: str) -> str:
        return shlex.join(["python.exe", self._wrapper.as_posix(), *arguments])

    async def install(self, environment: BaseEnvironment) -> None:
        result = await self.exec_as_agent(environment, command=self._command("check", "--expected-version", self._expected_version))
        if result.return_code:
            raise RuntimeError("Windows Pi preflight failed: " + result.stderr[-1000:])

    @with_prompt_template
    async def run(self, instruction: str, environment: BaseEnvironment, context: AgentContext) -> None:
        del context
        if self.model_name != "openai-codex/gpt-6.1-sol":
            raise ValueError("This study freezes openai-codex/gpt-6.1-sol")
        if not self.skills_dir:
            raise ValueError("Native Harbor must stage the one frozen candidate skill")
        skill_path = environment.prepare_runtime_skill(self.skills_dir, self._skill_name)
        environment.write_task_prompt(instruction)
        helpers = self._event_helpers()
        launcher = helpers.build_launcher_prompt(self._skill_name)
        (self.logs_dir / "prompt-provenance.json").write_text(json.dumps({"task_prompt_sha256": hashlib.sha256(instruction.encode("utf-8")).hexdigest(), "launcher_sha256": hashlib.sha256(launcher.encode("utf-8")).hexdigest(), "task_prompt_location": "../prompt.md", "launcher": launcher}, indent=2) + "\n", encoding="utf-8")
        try:
            result = await self.exec_as_agent(environment, command=self._command(
                "run", "--expected-version", self._expected_version,
                "--prompt-base64", base64.b64encode(launcher.encode("utf-8")).decode("ascii"),
                "--model", self.model_name, "--thinking", "medium", "--skill-path", skill_path,
                "--output", (self.logs_dir / self._OUTPUT_FILENAME).resolve().as_posix(),
            ))
            trace = self._audit_trace(environment, instruction)
            if result.return_code:
                raise RuntimeError("Pi execution failed; inspect agent/runtime-status.json and raw Pi events. " + result.stderr[-1000:])
            if not trace["passed"]:
                raise RuntimeError("Pi strict trace policy failed; inspect agent/trace-check.json")
        finally:
            environment.record_runtime_integrity()

    def populate_context_post_run(self, context: AgentContext) -> None:
        output = self.logs_dir / self._OUTPUT_FILENAME
        if not output.is_file():
            return
        totals = {"input": 0, "output": 0, "cacheRead": 0}
        total_cost = 0.0
        seen = set()
        for line in output.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = event.get("message") or {}
            if event.get("type") != "message_end" or message.get("role") != "assistant":
                continue
            identity = hashlib.sha256(json.dumps(message, sort_keys=True).encode()).hexdigest()
            if identity in seen:
                continue
            seen.add(identity)
            usage = message.get("usage") or {}
            for key in totals:
                totals[key] += usage.get(key, 0)
            total_cost += (usage.get("cost") or {}).get("total", 0.0)
        context.n_input_tokens = totals["input"] + totals["cacheRead"]
        context.n_output_tokens = totals["output"]
        context.n_cache_tokens = totals["cacheRead"]
        context.cost_usd = total_cost if total_cost > 0 else None
