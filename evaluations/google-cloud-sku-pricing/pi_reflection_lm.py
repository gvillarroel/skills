#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Expose the authenticated local Pi/Codex runtime as a GEPA reflection LM."""

from __future__ import annotations

import itertools
import json
from pathlib import Path
import shutil
import subprocess
import threading
from typing import Any
from uuid import uuid4


def resolve_pi_command() -> list[str]:
    node = shutil.which("node.exe") or shutil.which("node")
    for shim_name in ("pi.cmd", "pi.ps1", "pi"):
        shim = shutil.which(shim_name)
        if not shim:
            continue
        npm_bin = Path(shim).resolve().parent
        for package_scope in ("@earendil-works", "@mariozechner"):
            cli = npm_bin / "node_modules" / package_scope / "pi-coding-agent" / "dist" / "cli.js"
            if node and cli.is_file():
                return [node, str(cli)]
    executable = shutil.which("pi.exe")
    if executable:
        return [executable]
    raise RuntimeError("The installed Pi JavaScript CLI was not found on Windows PATH")


class PiReflectionLM:
    """A plain-string GEPA LM backed by locally authenticated openai-codex."""

    def __init__(
        self,
        run_root: Path,
        provider: str = "openai-codex",
        model: str = "gpt-5.3-codex-spark",
        thinking: str = "high",
        timeout_seconds: int = 900,
    ) -> None:
        self.run_root = run_root.resolve()
        self.provider = provider
        self.model = model
        self.thinking = thinking
        self.timeout_seconds = timeout_seconds
        self._counter = itertools.count(1)
        self._lock = threading.Lock()
        self._total_cost = 0.0
        self._total_tokens_in = 0
        self._total_tokens_out = 0

    @property
    def total_cost(self) -> float:
        return self._total_cost

    @property
    def total_tokens_in(self) -> int:
        return self._total_tokens_in

    @property
    def total_tokens_out(self) -> int:
        return self._total_tokens_out

    def _prompt_text(self, prompt: str | list[dict[str, Any]]) -> str:
        if isinstance(prompt, str):
            return prompt
        sections: list[str] = []
        for message in prompt:
            role = str(message.get("role", "user")).upper()
            content = message.get("content", "")
            if isinstance(content, str):
                rendered = content
            else:
                rendered = json.dumps(content, ensure_ascii=False)
            sections.append(f"{role}:\n{rendered}")
        return "\n\n".join(sections)

    def __call__(self, prompt: str | list[dict[str, Any]]) -> str:
        prompt_text = self._prompt_text(prompt)
        with self._lock:
            sequence = next(self._counter)
        call_dir = self.run_root / f"call-{sequence:03d}-{uuid4().hex[:8]}"
        call_dir.mkdir(parents=True, exist_ok=False)
        (call_dir / ".git").mkdir()
        (call_dir / ".git" / "HEAD").write_text(
            "ref: refs/heads/gepa-reflection\n", encoding="utf-8", newline="\n"
        )
        (call_dir / "prompt.md").write_text(prompt_text, encoding="utf-8", newline="\n")
        command = [
            *resolve_pi_command(),
            "--print",
            "--mode",
            "json",
            "--no-tools",
            "--no-session",
            "--no-context-files",
            "--no-extensions",
            "--no-skills",
            "--no-prompt-templates",
            "--no-themes",
            "--provider",
            self.provider,
            "--model",
            self.model,
            "--thinking",
            self.thinking,
            "--system-prompt",
            "You are a pure offline text-transformation function. Use only the supplied prompt. "
            "Do not inspect files, paths, tools, credentials, or external context. Return only the requested text.",
            prompt_text,
        ]
        completed = subprocess.run(
            command,
            cwd=call_dir,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=self.timeout_seconds,
        )
        events_path = call_dir / "events.jsonl"
        events_path.write_text(completed.stdout, encoding="utf-8", newline="\n")
        if completed.stderr:
            (call_dir / "stderr.log").write_text(
                completed.stderr, encoding="utf-8", newline="\n"
            )
        final_text = ""
        call_cost = 0.0
        tokens_in = 0
        tokens_out = 0
        model_errors: list[str] = []
        for line in completed.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "message_end":
                continue
            message = event.get("message") or {}
            if message.get("role") != "assistant":
                continue
            if message.get("stopReason") == "error":
                model_errors.append(str(message.get("errorMessage", "model error")).splitlines()[0][:300])
            usage = message.get("usage") or {}
            tokens_in += int(usage.get("input", 0)) + int(usage.get("cacheRead", 0))
            tokens_out += int(usage.get("output", 0))
            call_cost += float((usage.get("cost") or {}).get("total", 0.0))
            texts = [
                str(block.get("text", ""))
                for block in message.get("content") or []
                if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
            ]
            if texts:
                final_text = "\n".join(texts).strip()
        with self._lock:
            self._total_cost += call_cost
            self._total_tokens_in += tokens_in
            self._total_tokens_out += tokens_out
        summary = {
            "exitCode": completed.returncode,
            "model": f"{self.provider}/{self.model}",
            "promptSha256": __import__("hashlib").sha256(prompt_text.encode("utf-8")).hexdigest(),
            "responseBytes": len(final_text.encode("utf-8")),
            "costUsd": call_cost,
            "tokensIn": tokens_in,
            "tokensOut": tokens_out,
            "errors": model_errors,
        }
        (call_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
        )
        if completed.returncode != 0 or model_errors or not final_text:
            reason = model_errors[0] if model_errors else f"exit {completed.returncode}"
            raise RuntimeError(f"Pi reflection failed: {reason}")
        (call_dir / "response.md").write_text(final_text, encoding="utf-8", newline="\n")
        return final_text

    def __repr__(self) -> str:
        return f"PiReflectionLM(model={self.provider}/{self.model})"
