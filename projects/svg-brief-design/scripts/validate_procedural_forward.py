#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Seven prospective unforced Luna controls for the final standalone bundle."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import posixpath
import subprocess
import sys
import time

from validate_unforced_routing import PROGRAM as DISCOVERY, TARGET, write_json

REPO = Path(__file__).resolve().parents[3]
STUDY = REPO / "evaluations/runs/svp3"
RUN = STUDY / "forward"
SOURCE = STUDY / "inputs" / (sys.argv[1] if len(sys.argv) > 1 else "p") / "svg-brief-design"
VERIFIER = Path("/mnt/c/Users/villa/OneDrive/Documentos/ChatGPT/personal/output/fox-vector-benchmark-v1/scripts/compare_svg_v1_1.py")
CASES = [
    {"id": "service-flow", "kind": "naturalistic-forward", "output": "service.svg", "repetitions": 3,
     "text": {"Pedido": 1, "Preparación": 1, "Entrega": 1, "Retorno": 1},
     "prompt": "Crea /app/service.svg: un flujo sencillo para un servicio de café con Pedido, Preparación, Entrega y Retorno, de izquierda a derecha y unidos con flechas. Negro sobre fondo transparente, con esos nombres editables, sin texto extra ni adornos."},
    {"id": "astronomical-mark", "kind": "generalization", "output": "mark.svg", "repetitions": 3, "text": {},
     "prompt": "Crea /app/mark.svg: un emblema vertical original con una esfera de alambre de líneas finas arriba y una pequeña figura radial negra y sólida debajo. Que las dos partes se distingan, con aire entre ellas, sin texto ni marco, en SVG editable con fondo transparente."},
    {"id": "unrelated-python", "kind": "negative-routing", "output": None, "repetitions": 1,
     "prompt": "Explica en dos frases la diferencia entre una lista y una tupla en Python. No crees archivos."},
]
PREFIX = "Runtime context: Python 3.12, resvg_py, Pillow and defusedxml are already installed; use python, not uv, for helpers. Work only in /app and keep skill resources read-only. Do not read credentials or unrelated system files.\n\n"
PROGRAM = DISCOVERY.replace("'--tools','read'", "'--tools',('read,write,bash' if request['output'] else 'read')").replace("timeout=90", "timeout=240")
PROGRAM = PROGRAM.replace("sys.stderr.write(result.stderr)", """
expected=Path('/app')/request['output'] if request['output'] else None
print(json.dumps({'type':'forward_artifact','output':request['output'],'content':expected.read_text() if expected and expected.is_file() else None,'workspace_files':[str(p.relative_to('/app')) for p in Path('/app').rglob('*') if p.is_file()]}))
sys.stderr.write(result.stderr)
""")
CHECK = r'''
import importlib.util,json,sys,io
from pathlib import Path
from collections import Counter
from defusedxml import ElementTree as ET
from PIL import Image
import resvg_py
spec=importlib.util.spec_from_file_location('technical','/verifier.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
source=Path('/outputs')/sys.argv[1]
data=source.read_bytes();_,metadata=module.render(data)
root=ET.fromstring(data)
texts=dict(Counter(''.join(e.itertext()).strip() for e in root.iter() if e.tag.rsplit('}',1)[-1]=='text'))
expected=json.loads(sys.argv[2])
png=resvg_py.svg_to_bytes(svg_string=data.decode(),width=800,skip_system_fonts=True,font_dirs=['/usr/share/fonts/truetype/dejavu'],font_family='DejaVu Sans',sans_serif_family='DejaVu Sans')
im=Image.open(io.BytesIO(png)).convert('RGBA');bounds=im.getchannel('A').getbbox()
Image.alpha_composite(Image.new('RGBA',im.size,'white'),im).convert('RGB').save(source.with_suffix('.png'))
print(json.dumps({'artifact_valid':True,'text_contract':texts==expected,'observed_text':texts,'ink_bounds':bounds,'size':im.size,'touches_edge':bool(bounds and (bounds[0]==0 or bounds[1]==0 or bounds[2]==im.width or bounds[3]==im.height)),'metadata':metadata,'semantic_review_required':True}))
'''


def main():
    RUN.mkdir(exist_ok=False)
    study = json.loads((STUDY / "protocol.json").read_text())
    image = study["runtime"]["agent_image"]
    bundle = {p.relative_to(SOURCE).as_posix(): p.read_bytes().decode("utf-8") for p in SOURCE.rglob("*") if p.is_file()}
    hashes = {name: hashlib.sha256(value.encode()).hexdigest() for name, value in bundle.items()}
    write_json(RUN / "protocol.json", {"registered_at": datetime.now(timezone.utc).isoformat(), "cases": CASES,
               "model": "openai-codex/gpt-6-luna", "thinking": "medium", "transport": "sse", "max_calls": 7,
               "retries": 0, "source_files": hashes, "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "native_discovery": True, "image": image, "verifier_sha256": hashlib.sha256(VERIFIER.read_bytes()).hexdigest(),
               "scope": "Prospective naturalistic/generalization and negative-routing controls. No purchased references or reward optimization. Exact labels, technical validity and strict trace checks are automated; subject/layout review is independent and manual."})
    auth = json.loads(Path(os.environ["FOX_PI_AUTH"]).read_text(encoding="utf-8-sig"))
    rows = []
    for case in CASES:
        for repeat in range(1, case["repetitions"]+1):
            folder = RUN / f"{case['id']}-{repeat}"
            folder.mkdir()
            request = {"auth": {"openai-codex": auth["openai-codex"]}, "bundle": bundle,
                       "prompt": PREFIX + case["prompt"], "output": case["output"]}
            started = time.monotonic()
            result = subprocess.run(["docker", "run", "--rm", "-i", "--cpus", "2", "--memory", "2g", image, "python", "-c", PROGRAM], input=json.dumps(request), capture_output=True, text=True, timeout=260)
            (folder / "events.jsonl").write_text(result.stdout, encoding="utf-8")
            (folder / "stderr.txt").write_text(result.stderr, encoding="utf-8")
            events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
            starts = [e for e in events if e.get("type") == "tool_execution_start"]
            ends = {e.get("toolCallId"): e for e in events if e.get("type") == "tool_execution_end"}
            reads = [e.get("args", {}).get("path", "") for e in starts if e.get("toolName") == "read"]
            commands = [e.get("args", {}).get("command", "") for e in starts if e.get("toolName") == "bash"]
            write_paths = [e.get("args", {}).get("path", "") for e in starts if e.get("toolName") == "write"]
            def normalized(path):
                return posixpath.normpath(path if path.startswith("/") else "/app/" + path)
            valid_surface = all(normalized(p).startswith(("/app/", "/root/.agents/skills/svg-brief-design/")) for p in reads) and all(normalized(p).startswith("/app/") for p in write_paths)
            valid_surface = valid_surface and not any(token in cmd for cmd in commands for token in ("/tests", "/solution", "/curator", "auth.json", "curl ", "wget "))
            read_skill = any(e.get("toolName") == "read" and e.get("args", {}).get("path") == TARGET and e.get("toolCallId") in ends and not ends[e["toolCallId"]].get("isError") for e in starts)
            model = [e["message"] for e in events if e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant"]
            valid_model = bool(model) and all(m.get("model") == "gpt-6-luna" and m.get("provider") == "openai-codex" for m in model) and model[-1].get("stopReason") == "stop"
            integrity = next(e for e in events if e.get("type") == "routing_environment")
            artifact = next(e for e in events if e.get("type") == "forward_artifact")
            payload_ok = integrity["bundle_before"] == integrity["bundle_after"] == hashes
            tools_ok = len(starts) == len(ends) and all(not e.get("isError") for e in ends.values()) and all(e.get("toolName") in {"read", "write", "bash"} for e in starts)
            check = {"artifact_valid": False, "text_contract": False}
            if case["output"] and artifact["content"]:
                (folder / case["output"]).write_text(artifact["content"], encoding="utf-8")
                checked = subprocess.run(["docker", "run", "--rm", "--network", "none", "--mount", f"type=bind,source={folder},target=/outputs", "--mount", f"type=bind,source={VERIFIER},target=/verifier.py,readonly", study["runtime"]["verifier_image"], "python", "-c", CHECK, case["output"], json.dumps(case["text"])], capture_output=True, text=True, timeout=40)
                check = json.loads(checked.stdout) if checked.returncode == 0 else {"artifact_valid": False, "error": checked.stderr[-1000:]}
            routing = read_skill if case["output"] else not reads
            artifact_ok = check.get("artifact_valid") and check.get("text_contract") if case["output"] else not artifact["workspace_files"]
            row = {"case": case["id"], "repetition": repeat, "kind": case["kind"], "exact_model": valid_model,
                   "routing": routing, "payload_unchanged": payload_ok, "tools_ok": tools_ok, "read_surface": valid_surface,
                   "reads": reads, "commands": commands, "writes": write_paths, "artifact": check, "elapsed_seconds": time.monotonic()-started,
                   "passed": result.returncode == 0 and valid_model and routing and payload_ok and tools_ok and valid_surface and bool(artifact_ok)}
            write_json(folder / "receipt.json", row)
            rows.append(row)
            print(json.dumps({k: row[k] for k in ("case", "repetition", "passed", "elapsed_seconds")}), flush=True)
    write_json(RUN / "summary.json", {"rows": rows, "passed": all(r["passed"] for r in rows), "calls": len(rows), "semantic_review_required": True})


if __name__ == "__main__":
    main()
