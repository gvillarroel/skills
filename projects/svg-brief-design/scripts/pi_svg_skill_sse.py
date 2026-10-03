#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""SSE-only successor; preserve native loading and guidance-only isolation."""
from pathlib import Path
import hashlib,json,os,re,shlex,tempfile
from harbor.agents.installed.pi import Pi

class PiSvgSkill(Pi):
    @staticmethod
    def name():return 'pi-svg-skill-sse'
    def get_version_command(self):return 'pi --version'
    async def install(self,environment):
        await self.exec_as_agent(environment,command='test "$(pi --version)" = "0.84.2"')
    async def run(self,instruction,environment,context):
        if self.model_name!='openai-codex/gpt-6-luna':raise ValueError('Frozen model identity mismatch')
        if not self.skills_dir:raise ValueError('Exactly one Harbor-managed skill is required')
        skill=Path(self.skills_dir)/'svg-brief-design'
        await self.exec_as_agent(environment,command='mkdir -p /root/.pi/agent /logs/agent /logs/artifacts')
        auth=json.loads(Path(os.environ['FOX_PI_AUTH']).read_text(encoding='utf-8-sig'))
        settings={'transport':'sse','retry':{'enabled':False},'compaction':{'enabled':False},'enableSkillCommands':True}
        models={'providers':{'openai-codex':{'api':'openai-codex-responses','models':[{'id':'gpt-6-luna','name':'GPT-6 Luna','reasoning':True,'input':['text','image'],'contextWindow':1050000,'maxTokens':16384}]}}}
        with tempfile.TemporaryDirectory(prefix='svg-skill-auth-') as temp:
            for name,value in [('auth.json',{'openai-codex':auth['openai-codex']}),('models.json',models),('settings.json',settings)]:
                path=Path(temp)/name;path.write_text(json.dumps(value));path.chmod(0o600)
                await environment.upload_file(path,'/root/.pi/agent/'+name)
        audit_code="""from pathlib import Path
import hashlib,json,re
root=Path(SKILL_ROOT)
files={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
assert set(files)=={'SKILL.md','agents/openai.yaml','references/svg-mechanics.md'},files
for p in root.rglob('*'):
 if p.is_file():
  assert p.suffix in ['.md','.yaml']
  assert not re.search(r'<(?:svg|path|image)\\b|data:image|base64,|vector-\\d{3}|p\\d{2}-s\\d{3}|Fox Rockett',p.read_text(),re.I)
for forbidden in ['/tests','/solution','/curator','/app/datasets','/work']:
 assert not Path(forbidden).exists(),forbidden
for base in ['/app','/root']:
 assert not any(Path(base).rglob('*.svg')),base
out={'reference_absent':True,'verifier_absent':True,'ambient_skills_disabled':True,'loading_policy':'native-explicit-skill-command','skill_files':files,'skill_root':str(root)}
Path('/logs/agent/skill-input-audit.json').write_text(json.dumps(out,indent=2))
""".replace('SKILL_ROOT',repr(str(skill)))
        await self.exec_as_agent(environment,command='python3 -c '+shlex.quote(audit_code))
        policy='The loaded skill directory is a read-only reference. Its instructions are already included in this request. Do not create, edit, or clear files in /harbor/skills. Create only the requested deliverable outside that directory.\n\n'
        (self.logs_dir/'loading-contract.json').write_text(json.dumps({'transport':'sse','policy_sha256':hashlib.sha256(policy.encode()).hexdigest(),'task_instruction_sha256':hashlib.sha256(instruction.encode()).hexdigest()}))
        prompt='/skill:svg-brief-design '+policy+instruction
        args=['pi','--print','--mode','json','--no-session','--offline','--no-extensions','--no-skills','--no-context-files','--no-prompt-templates','--no-themes','--skill',str(skill),'--tools','write','--provider','openai-codex','--model','gpt-6-luna','--thinking','medium',prompt]
        await self.exec_as_agent(environment,command=shlex.join(args)+' > /logs/agent/pi.txt 2>&1',env={'PI_OFFLINE':'1','PI_TELEMETRY':'0'})
        integrity="""from pathlib import Path
import hashlib,json
before=json.loads(Path('/logs/agent/skill-input-audit.json').read_text())
root=Path(before['skill_root'])
after={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
assert before['skill_files']==after,'Skill payload was modified'
Path('/logs/agent/skill-integrity.json').write_text(json.dumps({'unchanged':True,'files':after},indent=2))
"""
        await self.exec_as_agent(environment,command='python3 -c '+shlex.quote(integrity))
    def populate_context_post_run(self,context):
        super().populate_context_post_run(context)
        events=[]
        for line in (self.logs_dir/'pi.txt').read_text().splitlines():
            try:event=json.loads(line)
            except json.JSONDecodeError:continue
            if event.get('type')=='tool_execution_end' and event.get('isError'):raise RuntimeError('Pi tool error')
            if event.get('type')=='tool_execution_start' and event.get('toolName')!='write':raise RuntimeError('Undeclared tool')
            if event.get('type')=='message_end' and event.get('message',{}).get('role')=='assistant':events.append(event['message'])
        if not events or any(m.get('model')!='gpt-6-luna' for m in events):raise RuntimeError('Missing or wrong model')
        if events[-1].get('stopReason') in ['error','aborted']:raise RuntimeError('Pi provider failure')
        context.cost_usd=None
