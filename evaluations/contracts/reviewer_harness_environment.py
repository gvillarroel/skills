#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Keep pi temporary files and Git discovery inside its isolated workspace."""

from __future__ import annotations

import os
import shlex
from pathlib import Path


def install(harness) -> None:
    original_run = harness.subprocess.run

    def run(command, *args, **kwargs):
        if isinstance(command, list) and "--no-context-files" in command and "--no-skills" in command:
            workspace = Path(kwargs["cwd"]).resolve()
            temporary = workspace / ".runtime-temp"
            temporary.mkdir(exist_ok=True)
            bash_environment = workspace / ".runtime-env.bash"
            bash_environment.write_text(f"export TMPDIR={shlex.quote(temporary.as_posix())}\n", encoding="utf-8")
            environment = dict(kwargs.get("env") or os.environ)
            environment.update({"TMPDIR": temporary.as_posix(), "TEMP": str(temporary), "TMP": str(temporary), "BASH_ENV": bash_environment.as_posix(), "GIT_CEILING_DIRECTORIES": workspace.parent.as_posix()})
            kwargs["env"] = environment
        return original_run(command, *args, **kwargs)

    harness.subprocess.run = run
