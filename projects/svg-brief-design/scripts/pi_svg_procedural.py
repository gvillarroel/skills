#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Matched full-tool Pi adapter for original procedural skill bundles."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import tempfile

from harbor.agents.installed.pi import Pi


POLICY = """The loaded skill directory is a read-only resource. Its SKILL.md instructions
are included in this request. Read its relevant guides and run helpers when useful;
create deliverables and temporary working files in /app, never inside /harbor/skills.
The only available tools are read, write and bash. This environment already has
Python 3.12, resvg_py, Pillow and defusedxml installed: use python to run Python
helpers; uv is not installed. You may render and inspect local PNGs with read.
Do not read credentials, runtime logs, or system directories unrelated to the task.
Deliver the exact requested SVG path. Auxiliary work must not replace it.

"""


class PiSvgProcedural(Pi):
    @staticmethod
    def name():
        return "pi-svg-procedural"

    def get_version_command(self):
        return "pi --version"

    async def install(self, environment):
        await self.exec_as_agent(environment, command='test "$(pi --version)" = "0.84.2"')

    async def run(self, instruction, environment, context):
        if self.model_name != "openai-codex/gpt-6-luna" or not self.skills_dir:
            raise ValueError("Frozen exact model and one native skill are required")
        skill = Path(self.skills_dir) / "svg-brief-design"
        await self.exec_as_agent(environment, command="mkdir -p /root/.pi/agent /logs/agent /logs/artifacts")
        auth = json.loads(Path(os.environ["FOX_PI_AUTH"]).read_text(encoding="utf-8-sig"))
        settings = {"transport": "sse", "retry": {"enabled": False}, "compaction": {"enabled": False}, "enableSkillCommands": True}
        models = {"providers": {"openai-codex": {"api": "openai-codex-responses", "models": [{"id": "gpt-6-luna", "name": "GPT-6 Luna", "reasoning": True, "input": ["text", "image"], "contextWindow": 1050000, "maxTokens": 16384}]}}}
        with tempfile.TemporaryDirectory(prefix="procedural-pi-auth-") as temp:
            for name, value in [("auth.json", {"openai-codex": auth["openai-codex"]}), ("models.json", models), ("settings.json", settings)]:
                path = Path(temp) / name
                path.write_text(json.dumps(value))
                path.chmod(0o600)
                await environment.upload_file(path, "/root/.pi/agent/" + name)
        audit = """from pathlib import Path
import hashlib,json,re
root=Path(SKILL_ROOT)
files={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
assert 'SKILL.md' in files
assert all(Path(p).suffix in ['.md','.yaml','.py'] for p in files),files
for p in root.rglob('*'):
 if p.is_file():
  assert not p.is_symlink()
  assert not re.search(r'data:image|base64,|vector-\\d{3}|p\\d{2}-s\\d{3}|Fox Rockett',p.read_text(),re.I)
for forbidden in ['/tests','/solution','/curator','/app/datasets','/work']:
 assert not Path(forbidden).exists(),forbidden
for base in ['/app','/root']:
 assert not any(Path(base).rglob('*.svg')),base
Path('/logs/agent/skill-input-audit.json').write_text(json.dumps({'reference_absent':True,'verifier_absent':True,'ambient_skills_disabled':True,'loading_policy':'native-explicit-skill-command','allowed_tools':['read','write','bash'],'skill_files':files,'skill_root':str(root)},indent=2))
""".replace("SKILL_ROOT", repr(str(skill)))
        await self.exec_as_agent(environment, command="python -c " + shlex.quote(audit))
        (self.logs_dir / "loading-contract.json").write_text(json.dumps({
            "transport": "sse", "policy_sha256": hashlib.sha256(POLICY.encode()).hexdigest(),
            "task_instruction_sha256": hashlib.sha256(instruction.encode()).hexdigest(),
            "source_agent_image": environment.source_agent_image,
            "declared_agent_image": environment.declared_agent_image,
        }, indent=2))
        prompt = "/skill:svg-brief-design " + POLICY + instruction
        args = ["pi", "--print", "--mode", "json", "--no-session", "--offline", "--no-extensions", "--no-skills", "--no-context-files", "--no-prompt-templates", "--no-themes", "--skill", str(skill), "--tools", "read,write,bash", "--provider", "openai-codex", "--model", "gpt-6-luna", "--thinking", "medium", prompt]
        await self.exec_as_agent(environment, command=shlex.join(args) + " > /logs/agent/pi.txt 2>&1", env={"PI_OFFLINE": "1", "PI_TELEMETRY": "0", "PYTHONDONTWRITEBYTECODE": "1"})
        integrity = """from pathlib import Path
import hashlib,json
before=json.loads(Path('/logs/agent/skill-input-audit.json').read_text())
root=Path(before['skill_root'])
after={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
assert before['skill_files']==after,'Skill payload was modified'
Path('/logs/agent/skill-integrity.json').write_text(json.dumps({'unchanged':True,'files':after},indent=2))
"""
        await self.exec_as_agent(environment, command="python -c " + shlex.quote(integrity))

    def populate_context_post_run(self, context):
        super().populate_context_post_run(context)
        messages = []
        for line in (self.logs_dir / "pi.txt").read_text().splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue  # Pi may print a startup notice before its event stream.
            if event.get("type") == "tool_execution_end" and event.get("isError"):
                raise RuntimeError("Pi tool error")
            if event.get("type") == "tool_execution_start" and event.get("toolName") not in {"read", "write", "bash"}:
                raise RuntimeError("Undeclared tool")
            if event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant":
                messages.append(event["message"])
        if not messages or any(m.get("model") != "gpt-6-luna" for m in messages):
            raise RuntimeError("Missing or wrong model")
        if messages[-1].get("stopReason") in {"error", "aborted"}:
            raise RuntimeError("Pi provider failure")
        context.cost_usd = None
