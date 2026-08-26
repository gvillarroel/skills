#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "gepa==0.1.2"]
# ///
"""Run harbor-evolve-skill while routing GEPA reflection through local Pi."""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import os
from pathlib import Path
import sys
from threading import Thread
from typing import Any

from pi_reflection_lm import PiReflectionLM


def load_evolution_module() -> Any:
    configured = os.environ.get("HARBOR_EVOLVE_SCRIPT")
    source = (
        Path(configured).expanduser().resolve()
        if configured
        else Path.home()
        / ".codex"
        / "skills"
        / "harbor-evolve-skill"
        / "scripts"
        / "evolve_skill_with_harbor.py"
    )
    if not source.is_file():
        raise SystemExit(
            "harbor-evolve-skill is unavailable; set HARBOR_EVOLVE_SCRIPT to its runner"
        )
    spec = importlib.util.spec_from_file_location("harbor_evolve_skill_runner", source)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Unable to load harbor evolution runner: {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")
    repository_root = Path(__file__).resolve().parents[2]
    repository_text = str(repository_root)
    if repository_text not in sys.path:
        sys.path.insert(0, repository_text)
    evolution = load_evolution_module()
    original_optimize = evolution.optimize_anything
    original_environment_config = evolution.EnvironmentConfig
    reflection_lm: PiReflectionLM | None = None

    def compatible_environment_config(*, type: str | None = None, **kwargs: Any) -> Any:
        if type and ":" in type:
            return original_environment_config(
                import_path=type,
                cpu_enforcement_policy="ignore",
                memory_enforcement_policy="ignore",
                env={},
                kwargs={},
                **kwargs,
            )
        return original_environment_config(type=type, **kwargs)

    evolution.EnvironmentConfig = compatible_environment_config

    def optimize_with_pi_reflection(
        seed_candidate: Any = None,
        *,
        evaluator: Any,
        dataset: Any = None,
        valset: Any = None,
        objective: str | None = None,
        background: str | None = None,
        config: Any = None,
    ) -> Any:
        nonlocal reflection_lm
        if config is None:
            raise RuntimeError("GEPA configuration is missing")
        # harbor-evolve-skill 0.1 supplies both objective/background and its
        # leakage-resistant custom reflection template. GEPA 0.1.2 correctly
        # treats those modes as mutually exclusive. Preserve all information by
        # folding the objective fields into the custom template before calling
        # GEPA, then remove the conflicting top-level arguments.
        objective_text = str(objective or "").strip()
        background_text = str(background or "").strip()
        template = str(config.reflection.reflection_prompt_template or "").strip()
        config.reflection.reflection_prompt_template = (
            "Evolution objective:\n"
            f"{objective_text}\n\n"
            "Evolution background and guardrails:\n"
            f"{background_text}\n\n"
            f"{template}"
        )
        if reflection_lm is None:
            run_directory = Path(config.engine.run_dir).resolve()
            reflection_lm = PiReflectionLM(run_directory.parent / "reflection-calls")
        config.reflection.reflection_lm = reflection_lm
        loop: asyncio.AbstractEventLoop | None = None
        thread: Thread | None = None
        if inspect.iscoroutinefunction(evaluator):
            async_evaluator = evaluator
            loop = asyncio.new_event_loop()
            thread = Thread(target=loop.run_forever, name="gepa-pricing-loop", daemon=True)
            thread.start()

            def sync_evaluator(candidate: Any, example: Any) -> Any:
                assert loop is not None
                future = asyncio.run_coroutine_threadsafe(
                    async_evaluator(candidate, example), loop
                )
                return future.result()

            evaluator = sync_evaluator
        try:
            return original_optimize(
                seed_candidate,
                evaluator=evaluator,
                dataset=dataset,
                valset=valset,
                objective=None,
                background=None,
                config=config,
            )
        finally:
            if loop is not None and thread is not None:
                loop.call_soon_threadsafe(loop.stop)
                thread.join(timeout=10)
                loop.close()

    evolution.optimize_anything = optimize_with_pi_reflection
    evolution.main()


if __name__ == "__main__":
    main()
