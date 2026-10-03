#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Explicit read-only loading contract, applied equally to control and treatment."""
import hashlib,json
from pi_svg_skill import PiSvgSkill as OriginalAdapter

POLICY='The loaded skill directory is a read-only reference. Its instructions are already included in this request. Do not create, edit, or clear files in /harbor/skills. Create only the requested deliverable outside that directory.\n\n'

class PiSvgSkill(OriginalAdapter):
    async def run(self,instruction,environment,context):
        self.logs_dir.mkdir(parents=True,exist_ok=True)
        (self.logs_dir/'loading-contract.json').write_text(json.dumps({'policy':POLICY,'policy_sha256':hashlib.sha256(POLICY.encode()).hexdigest(),'task_instruction_sha256':hashlib.sha256(instruction.encode()).hexdigest()},indent=2))
        await super().run(POLICY+instruction,environment,context)
