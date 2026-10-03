#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Run two prospective actual-creation routing cases without replacing planning evidence."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time

from validate_unforced_routing import PROGRAM, SOURCE, FILES, TARGET, REPO, write_json
from luna_text_call import IMAGE, IMAGE_ID

RUN = REPO / "evaluations/runs/svg-brief-design-creation-routing-20260926"
VERIFIER = Path("/mnt/c/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1/scripts/compare_svg_v1_1.py")
VERIFIER_IMAGE = "sha256:f82f3a08d40b954417f8040d05f71213824906e312f477ac7ba0370e6b6427f7"
CASES = [
    {"id": "rainwater-cycle-diagram", "output": "rainwater.svg",
     "prompt": "Crea /app/rainwater.svg: un diagrama circular sencillo del ciclo de recogida de agua de lluvia, con una nube, un tejado y un depósito conectados con flechas. Usa líneas negras, fondo transparente y formas editables; sin texto."},
    {"id": "fern-corner-ornament", "output": "fern-corner.svg",
     "prompt": "Crea /app/fern-corner.svg: un ornamento original para la esquina de una invitación, con dos hojas de helecho curvas. Que sea ligero, elegante y editable, en negro sobre fondo transparente, sin marco ni texto."},
]

# Reuse the unchanged, audited native-discovery setup. Only the tool allowlist
# and artifact collection differ from the separately retained planning class.
assert PROGRAM.count("'--tools','read'") == 1
CREATION_PROGRAM = PROGRAM.replace("'--tools','read'", "'--tools','read,write'")
marker = "sys.stderr.write(result.stderr)"
assert CREATION_PROGRAM.count(marker) == 1
CREATION_PROGRAM = CREATION_PROGRAM.replace(marker, """
output=Path('/app')/request['output']
print(json.dumps({'type':'creation_artifact','output':request['output'],'content':output.read_text() if output.is_file() else None,'workspace_files':[str(p.relative_to('/app')) for p in Path('/app').rglob('*') if p.is_file()]}))
""" + marker)

CHECK = """
import sys,json,importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('svg_technical','/verifier.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
data=Path('/outputs/'+sys.argv[1]).read_bytes()
_,metadata=module.render(data)
print(json.dumps({'artifact_valid':True,'verifier_version':module.VERSION,'metadata':metadata,'reference_accessed':False,'fitness_computed':False}))
"""


def main():
    RUN.mkdir(parents=True, exist_ok=False)
    bundle = {p.relative_to(SOURCE).as_posix(): p.read_text(encoding="utf-8") for p in SOURCE.rglob("*") if p.is_file()}
    assert set(bundle) == FILES
    hashes = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in bundle.items()}
    assert hashes["SKILL.md"] == "740953f66380e648093af346231429ddf755d0fd564f910241157ea3beb57d04"
    assert json.loads(subprocess.check_output(["docker", "image", "inspect", IMAGE]))[0]["Id"] == IMAGE_ID
    protocol = {"schema_version": 1, "started_at": datetime.now(timezone.utc).isoformat(), "model": "openai-codex/gpt-6-luna",
                "pi": "0.84.2", "thinking": "medium", "transport": "sse", "max_calls": 2, "concurrency": 1, "retries": 0,
                "cases": CASES, "source_files": hashes, "image_id": IMAGE_ID, "verifier_image": VERIFIER_IMAGE,
                "verifier_sha256": hashlib.sha256(VERIFIER.read_bytes()).hexdigest(),
                "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "discovery_setup_sha256": hashlib.sha256(PROGRAM.encode()).hexdigest(),
                "expected": "Actual native successful SKILL.md read, exact output, unchanged bundle, valid self-contained static monochrome SVG through existing verifier render(), no reference or fitness.",
                "scope": "New actual-creation routing class. Original planning observations remain unchanged; no metadata mutation."}
    write_json(RUN / "protocol.json", protocol)
    credentials = json.loads(Path(os.environ["FOX_PI_AUTH"]).read_text(encoding="utf-8-sig"))
    rows = []
    for case in CASES:
        output = RUN / case["id"]
        output.mkdir()
        started = time.monotonic()
        request = {"auth": {"openai-codex": credentials["openai-codex"]}, "prompt": case["prompt"], "bundle": bundle, "output": case["output"]}
        result = subprocess.run(["docker", "run", "--rm", "-i", "--cpus", "1", "--memory", "1g", "--network", "bridge", IMAGE, "python3", "-c", CREATION_PROGRAM], input=json.dumps(request), capture_output=True, text=True, timeout=110)
        events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        starts = [e for e in events if e.get("type") == "tool_execution_start"]
        assert all(e.get("toolName") in {"read", "write"} for e in starts)
        reads = [e.get("args", {}).get("path") for e in starts if e.get("toolName") == "read"]
        writes = [e.get("args", {}).get("path") for e in starts if e.get("toolName") == "write"]
        assert all(p and p.startswith("/root/.agents/skills/svg-brief-design/") for p in reads), "Unexpected read"
        assert all(p == "/app/" + case["output"] for p in writes), "Unexpected write"
        (output / "events.jsonl").write_text(result.stdout, encoding="utf-8")
        (output / "stderr.txt").write_text(result.stderr, encoding="utf-8")
        ends = {e.get("toolCallId"): e for e in events if e.get("type") == "tool_execution_end"}
        routed = any(e.get("toolName") == "read" and e.get("args", {}).get("path") == TARGET and e.get("toolCallId") in ends and not ends[e["toolCallId"]].get("isError") for e in starts)
        messages = [e["message"] for e in events if e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant"]
        env = next(e for e in events if e.get("type") == "routing_environment")
        artifact = next(e for e in events if e.get("type") == "creation_artifact")
        artifact_ok = bool(artifact["content"]) and artifact["workspace_files"] == [case["output"]]
        technical = {"artifact_valid": False, "reason": "missing_or_extra_output"}
        if artifact_ok:
            (output / case["output"]).write_text(artifact["content"], encoding="utf-8")
            check = subprocess.run(["docker", "run", "--rm", "--network", "none", "--cpus", "1", "--memory", "1g", "--mount", f"type=bind,source={VERIFIER},target=/verifier.py,readonly", "--mount", f"type=bind,source={output},target=/outputs,readonly", VERIFIER_IMAGE, "python", "-c", CHECK, case["output"]], capture_output=True, text=True, timeout=30)
            technical = json.loads(check.stdout) if check.returncode == 0 else {"artifact_valid": False, "error": check.stderr[-1000:]}
        model_valid = bool(messages) and all(m.get("model") == "gpt-6-luna" and m.get("provider") == "openai-codex" for m in messages)
        healthy = bool(messages) and messages[-1].get("stopReason") not in {"error", "aborted"}
        tool_ok = len(starts) == len(ends) and all(not e.get("isError") for e in ends.values())
        integrity = env["bundle_before"] == env["bundle_after"] == hashes
        row = {"case": case["id"], "reads": reads, "writes": writes, "routing_passed": routed,
               "technical": technical, "model_valid": model_valid, "tool_checks_passed": tool_ok,
               "payload_unchanged": integrity, "exit_code": result.returncode,
               "elapsed_seconds": round(time.monotonic() - started, 3), "total_tokens": sum(m.get("usage", {}).get("totalTokens", 0) for m in messages),
               "passed": result.returncode == 0 and healthy and routed and model_valid and tool_ok and integrity and technical["artifact_valid"]}
        write_json(output / "receipt.json", row)
        rows.append(row)
        print(json.dumps(row), flush=True)
    write_json(RUN / "summary.json", {"schema_version": 1, "study": RUN.name, "model": protocol["model"], "source_files": hashes,
                                     "calls": len(rows), "passed": all(r["passed"] for r in rows), "rows": rows,
                                     "cost_usd": None, "finished_at": datetime.now(timezone.utc).isoformat()})
    assert {p.relative_to(SOURCE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.rglob("*") if p.is_file()} == hashes


if __name__ == "__main__":
    main()
