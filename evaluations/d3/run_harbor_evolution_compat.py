#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "gepa==0.1.2"]
# ///
"""Run harbor-evolve-skill with its GEPA 0.1.2 prompt-mode conflict repaired."""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
from pathlib import Path
import sys
from threading import Thread
from types import ModuleType
from typing import Any


def load_runner(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("harbor_evolve_skill_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load evolution runner: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) < 4 or sys.argv[1] != "--runner":
        raise SystemExit(
            "Usage: run_harbor_evolution_compat.py --runner RUNNER CONFIG [runner options]"
        )
    runner_path = Path(sys.argv[2]).resolve()
    if not runner_path.is_file():
        raise SystemExit(f"Evolution runner does not exist: {runner_path}")
    runner_args = sys.argv[3:]
    module = load_runner(runner_path)
    original = module.optimize_anything
    original_environment_config = module.EnvironmentConfig
    original_agent_config = module.AgentConfig

    def compatible_environment_config(*, type: str | None = None, **kwargs: Any) -> Any:
        if type and ":" in type:
            workspace_root = Path.cwd().resolve()
            return original_environment_config(
                import_path=type,
                cpu_enforcement_policy="ignore",
                memory_enforcement_policy="ignore",
                env={"CODEX_FORCE_AUTH_JSON": "true"},
                kwargs={
                    "shared_cache_dir": str(
                        workspace_root / "evaluations" / "runs" / "harbor-shared-cache"
                    )
                },
                **kwargs,
            )
        return original_environment_config(type=type, **kwargs)

    def compatible_agent_config(**kwargs: Any) -> Any:
        env = dict(kwargs.pop("env", {}))
        env.setdefault("CODEX_FORCE_AUTH_JSON", "true")
        return original_agent_config(env=env, **kwargs)

    module.EnvironmentConfig = compatible_environment_config
    module.AgentConfig = compatible_agent_config

    def compatible_optimize_anything(
        seed_candidate: Any = None,
        *,
        evaluator: Any,
        dataset: Any = None,
        valset: Any = None,
        objective: str | None = None,
        background: str | None = None,
        config: Any = None,
    ) -> Any:
        template = config.reflection.reflection_prompt_template
        if template:
            context = (
                "Evolution objective:\n"
                + (objective or "Improve the candidate.")
                + "\n\nBackground and constraints:\n"
                + (background or "No additional background.")
                + "\n\n"
            )
            config.reflection.reflection_prompt_template = context + template
            objective = None
            background = None
        loop: asyncio.AbstractEventLoop | None = None
        thread: Thread | None = None
        if inspect.iscoroutinefunction(evaluator):
            async_evaluator = evaluator
            loop = asyncio.new_event_loop()
            thread = Thread(target=loop.run_forever, name="gepa-harbor-loop", daemon=True)
            thread.start()

            def sync_evaluator(candidate: Any, example: Any) -> Any:
                assert loop is not None
                future = asyncio.run_coroutine_threadsafe(
                    async_evaluator(candidate, example), loop
                )
                return future.result()

            evaluator = sync_evaluator
        try:
            return original(
                seed_candidate,
                evaluator=evaluator,
                dataset=dataset,
                valset=valset,
                objective=objective,
                background=background,
                config=config,
            )
        finally:
            if loop is not None and thread is not None:
                loop.call_soon_threadsafe(loop.stop)
                thread.join(timeout=10)
                loop.close()

    module.optimize_anything = compatible_optimize_anything
    sys.argv = [str(runner_path), *runner_args]
    return int(module.main() or 0)


if __name__ == "__main__":
    sys.exit(main())
