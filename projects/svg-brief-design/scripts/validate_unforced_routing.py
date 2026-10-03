#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Check native, unforced Luna skill discovery with four isolated planning cases."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time

from luna_text_call import IMAGE, IMAGE_ID

REPO = Path(__file__).resolve().parents[3]
RUN = REPO / "evaluations/runs/svg-brief-design-routing-20260926"
SOURCE = REPO / "skills/svg-brief-design"
FILES = {"SKILL.md", "references/svg-mechanics.md", "agents/openai.yaml"}
TARGET = "/root/.agents/skills/svg-brief-design/SKILL.md"
CASES = [
    {"id": "original-botanical-emblem", "expected_read": True,
     "prompt": "Quiero un emblema original en SVG editable: una rama de olivo que rodee una luna creciente, elegante y sencillo. Primero dame un plan breve de composición; todavía no escribas archivos."},
    {"id": "decorative-wind-diagram", "expected_read": True,
     "prompt": "Necesito diseñar un diagrama decorativo en SVG con líneas de viento alrededor de una pequeña turbina, limpio y técnico. Por ahora prepara solo un plan corto de diseño, sin crear archivos."},
    {"id": "unrelated-python-explanation", "expected_read": False,
     "prompt": "Explícame brevemente la diferencia entre una lista y una tupla en Python, con un ejemplo pequeño de cada una. No escribas archivos."},
    {"id": "raster-tracing-boundary", "expected_read": False,
     "prompt": "Tengo un logo en PNG y quiero convertirlo a vector mediante calco automático, sin rediseñarlo. Explica de forma general el proceso y sus limitaciones; no crees archivos ni busques en internet."},
]

PROGRAM = r'''
from pathlib import Path
import hashlib, json, os, subprocess, sys
request = json.load(sys.stdin)
root = Path('/root/.pi/agent')
for candidate in ['/root/.agents/skills','/root/.pi/agent/skills','/app/.agents/skills','/app/.pi','/.agents/skills','/.pi']:
    p = Path(candidate)
    if p.exists() and any(p.rglob('SKILL.md')):
        raise RuntimeError('Unexpected ambient skill surface')
if list(Path('/app').iterdir()):
    raise RuntimeError('The planning workspace must start empty')
root.mkdir(parents=True, exist_ok=True)
settings = {'transport':'sse','retry':{'enabled':False},'compaction':{'enabled':False},'enableSkillCommands':False}
models = {'providers':{'openai-codex':{'api':'openai-codex-responses','models':[{'id':'gpt-6-luna','name':'GPT-6 Luna','reasoning':True,'input':['text','image'],'contextWindow':1050000,'maxTokens':16384}]}}}
for filename, content in [('auth.json',request['auth']),('settings.json',settings),('models.json',models)]:
    p=root/filename
    p.write_text(json.dumps(content))
    p.chmod(0o600)
skill = Path('/root/.agents/skills/svg-brief-design')
for rel, data in request['bundle'].items():
    p=skill/rel
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(data,encoding='utf-8')
    p.chmod(0o444)
before={p.relative_to(skill).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in skill.rglob('*') if p.is_file()}
version=subprocess.check_output(['pi','--version'],text=True).strip()
assert version == '0.84.2',version
args=['pi','--print','--mode','json','--no-session','--offline','--no-extensions','--no-context-files','--no-prompt-templates','--no-themes','--tools','read','--provider','openai-codex','--model','gpt-6-luna','--thinking','medium',request['prompt']]
result=subprocess.run(args,cwd='/app',env={**os.environ,'PI_OFFLINE':'1','PI_TELEMETRY':'0'},capture_output=True,text=True,timeout=90)
after={p.relative_to(skill).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in skill.rglob('*') if p.is_file()}
sys.stdout.write(result.stdout)
if result.stdout and not result.stdout.endswith('\n'):
    sys.stdout.write('\n')
print(json.dumps({'type':'routing_environment','pi':version,'argv':args,'bundle_before':before,'bundle_after':after,'workspace_unchanged':not list(Path('/app').iterdir()),'discovery_root':str(skill.parent),'forced_skill':False,'ambient_skill_absent':True}))
sys.stderr.write(result.stderr)
sys.exit(result.returncode)
'''


def write_json(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    RUN.mkdir(parents=True, exist_ok=False)
    bundle = {p.relative_to(SOURCE).as_posix(): p.read_text(encoding="utf-8")
              for p in SOURCE.rglob("*") if p.is_file()}
    assert set(bundle) == FILES, "Unexpected bundle payload"
    hashes = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in bundle.items()}
    assert hashes["SKILL.md"] == "740953f66380e648093af346231429ddf755d0fd564f910241157ea3beb57d04"
    identity = json.loads(subprocess.check_output(["docker", "image", "inspect", IMAGE]))[0]["Id"]
    assert identity == IMAGE_ID, "Pinned image changed"
    protocol = {"schema_version": 1, "started_at": datetime.now(timezone.utc).isoformat(),
                "model": "openai-codex/gpt-6-luna", "thinking": "medium", "transport": "sse",
                "image_id": identity, "source_files": hashes, "cases": CASES,
                "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "max_calls": 4, "retries": 0, "concurrency": 1,
                "required_evidence": "Successful native read tool event for positive cases; no skill read for negative cases. Exact model, valid JSONL, no tool errors, unchanged three-file bundle, no ambient context, read-only tools.",
                "scope": "Planning-only routing control; does not score SVG quality or replace repeated artifact evaluations."}
    write_json(RUN / "protocol.json", protocol)
    credentials = json.loads(Path(os.environ["FOX_PI_AUTH"]).read_text(encoding="utf-8-sig"))
    rows = []
    for case in CASES:
        output = RUN / case["id"]
        output.mkdir()
        started = time.monotonic()
        request = {"auth": {"openai-codex": credentials["openai-codex"]}, "prompt": case["prompt"], "bundle": bundle}
        try:
            result = subprocess.run(["docker", "run", "--rm", "-i", "--cpus", "1", "--memory", "1g", "--network", "bridge", IMAGE, "python3", "-c", PROGRAM],
                                    input=json.dumps(request), capture_output=True, text=True, timeout=110)
            events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
            starts = [e for e in events if e.get("type") == "tool_execution_start"]
            assert all(e.get("toolName") == "read" for e in starts), "Unexpected tool"
            reads = [e.get("args", {}).get("path") for e in starts]
            assert all(p and p.startswith("/root/.agents/skills/svg-brief-design/") for p in reads), "Read outside the isolated skill"
            (output / "events.jsonl").write_text(result.stdout, encoding="utf-8")
            (output / "stderr.txt").write_text(result.stderr, encoding="utf-8")
            end_by_id = {e.get("toolCallId"): e for e in events if e.get("type") == "tool_execution_end"}
            completed_skill_reads = [e for e in starts if e.get("args", {}).get("path") == TARGET and
                                     e.get("toolCallId") in end_by_id and not end_by_id[e["toolCallId"]].get("isError")]
            messages = [e["message"] for e in events if e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant"]
            env = [e for e in events if e.get("type") == "routing_environment"]
            model_valid = bool(messages) and all(m.get("model") == "gpt-6-luna" and m.get("provider") == "openai-codex" for m in messages)
            healthy = bool(messages) and messages[-1].get("stopReason") not in {"error", "aborted"}
            tool_ok = all(not e.get("isError") for e in end_by_id.values()) and len(end_by_id) == len(starts)
            integrity = len(env) == 1 and env[0]["bundle_before"] == env[0]["bundle_after"] == hashes and env[0]["workspace_unchanged"]
            routing = bool(completed_skill_reads) if case["expected_read"] else not reads
            row = {"case": case["id"], "expected_skill_read": case["expected_read"], "reads": reads,
                   "completed_skill_reads": len(completed_skill_reads), "routing_passed": routing,
                   "model_valid": model_valid, "tool_checks_passed": tool_ok, "payload_unchanged": integrity,
                   "exit_code": result.returncode, "elapsed_seconds": round(time.monotonic() - started, 3),
                   "total_tokens": sum(m.get("usage", {}).get("totalTokens", 0) for m in messages),
                   "passed": result.returncode == 0 and healthy and model_valid and tool_ok and integrity and routing}
        except Exception as exc:
            row = {"case": case["id"], "passed": False, "error_type": type(exc).__name__,
                   "error": str(exc)[:300], "elapsed_seconds": round(time.monotonic() - started, 3)}
        write_json(output / "receipt.json", row)
        rows.append(row)
        print(json.dumps(row), flush=True)
    summary = {"schema_version": 1, "study": RUN.name, "model": protocol["model"], "pi": "0.84.2",
               "source_files": hashes, "calls": len(rows), "passed": all(r["passed"] for r in rows), "rows": rows,
               "cost_usd": None, "finished_at": datetime.now(timezone.utc).isoformat()}
    write_json(RUN / "summary.json", summary)
    assert {p.relative_to(SOURCE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.rglob("*") if p.is_file()} == hashes
    print(json.dumps({"complete": True, "passed": summary["passed"]}), flush=True)


if __name__ == "__main__":
    main()
