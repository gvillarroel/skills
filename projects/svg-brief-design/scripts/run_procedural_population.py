#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Run the installed population skill with one stable native Harbor event loop."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types


def main():
    engine_path = Path("/mnt/c/Users/villa/.codex/skills/harbor-population-search/scripts/search_harbor_population.py")
    spec = importlib.util.spec_from_file_location("svg_population_engine", engine_path)
    engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = engine
    spec.loader.exec_module(engine)
    # Harbor's class-level Docker locks must not cross fresh asyncio.run loops.
    # Only the engine's local asyncio.run entry point changes, not its selection,
    # native job execution, scoring, validation or promotion behavior.
    with asyncio.Runner() as runner:
        proxy = types.SimpleNamespace(**vars(asyncio))
        proxy.run = runner.run
        engine.asyncio = proxy
        return engine.main()


if __name__ == "__main__":
    raise SystemExit(main())
