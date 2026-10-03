#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Declare a matched agent-image override without modifying source tasks."""
import re
from pathlib import Path

from harbor.environments.docker.docker import DockerEnvironment


class ProceduralEnvironment(DockerEnvironment):
    def __init__(self, *args, task_env_config, agent_image, source_agent_image, environment_dir, **kwargs):
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", agent_image):
            raise ValueError("The study requires an immutable local agent image ID")
        self.source_agent_image = task_env_config.docker_image
        self.declared_agent_image = agent_image
        # Only the agent runtime changes. The separate verifier and all task bytes
        # remain frozen; the native JobConfig records this explicit override.
        if task_env_config.docker_image == source_agent_image:
            effective = task_env_config.model_copy(update={"docker_image": agent_image})
        elif Path(environment_dir).name == "tests" and task_env_config.docker_image is None:
            effective = task_env_config  # Build the original separate verifier verbatim.
        else:
            raise ValueError("Unexpected source environment; refuse an undeclared image change")
        super().__init__(*args, environment_dir=environment_dir, task_env_config=effective, **kwargs)
