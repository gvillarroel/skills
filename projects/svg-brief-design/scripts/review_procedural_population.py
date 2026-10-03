#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "defusedxml==0.7.1"]
# ///
"""Audit native development traces and render every matched artifact, without rescoring."""
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from PIL import Image, ImageDraw, ImageFont
import resvg_py

REPO = Path(__file__).resolve().parents[3]
STUDY = REPO / "evaluations/runs/svp3"


def host_path(raw):
    if sys.platform == "win32" and raw.startswith("/mnt/"):
        return Path(raw[5].upper() + ":" + raw[6:])
    return Path(raw)


def preview(path, width=320, height=290):
    raster = resvg_py.svg_to_bytes(svg_string=path.read_text(encoding="utf-8-sig"), width=width)
    image = Image.open(io.BytesIO(raster)).convert("RGBA")
    image.thumbnail((width-20, height-20))
    canvas = Image.new("RGBA", (width, height), "white")
    canvas.alpha_composite(image, ((width-image.width)//2, (height-image.height)//2))
    return canvas.convert("RGB")


def main():
    generation = sys.argv[1] if len(sys.argv) > 1 else "generation-000"
    root = STUDY / generation
    out = STUDY / (generation + "-review")
    out.mkdir(exist_ok=False)
    protocol = json.loads((STUDY / "protocol.json").read_text())
    groups, records = {}, []
    if generation == "revision":
        inputs = [(name, path) for name, folder in (("b", STUDY / "generation-000/candidates/b/harbor-jobs/harbor-pop-g000-b"), ("q", STUDY / "jobs/q")) for path in sorted(folder.glob("*/result.json"))]
    else:
        inputs = [(path.parents[3].name, path) for path in sorted(root.glob("candidates/*/harbor-jobs/*/*/result.json"))]
    for candidate, path in inputs:
        result = json.loads(path.read_text())
        trial = path.parent
        task = host_path(result["config"]["task"]["path"])
        trace = trial / "agent/pi.txt"
        invalid = []
        events = []
        if trace.exists():
            for index, line in enumerate(trace.read_text().splitlines()):
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    invalid.append({"line": index+1, "text": line[:200]})
        starts = [e for e in events if e.get("type") == "tool_execution_start"]
        ends = {e.get("toolCallId"): e for e in events if e.get("type") == "tool_execution_end"}
        messages = [e["message"] for e in events if e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant"]
        reads = [e.get("args", {}).get("path", "") for e in starts if e.get("toolName") == "read"]
        commands = [e.get("args", {}).get("command", "") for e in starts if e.get("toolName") == "bash"]
        inputs_path, integrity_path = trial / "agent/skill-input-audit.json", trial / "agent/skill-integrity.json"
        inputs = json.loads(inputs_path.read_text()) if inputs_path.exists() else {}
        integrity = json.loads(integrity_path.read_text()) if integrity_path.exists() else {}
        expected = {p.relative_to(STUDY / "inputs" / candidate / "svg-brief-design").as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (STUDY / "inputs" / candidate / "svg-brief-design").rglob("*") if p.is_file()}
        exact_model = bool(messages) and all(m.get("model") == "gpt-6-luna" and m.get("provider") == "openai-codex" for m in messages)
        tools_ok = bool(starts) and len(starts) == len(ends) and all(not e.get("isError") for e in ends.values()) and all(e.get("toolName") in {"read", "write", "bash"} for e in starts)
        safe_reads = all(p.startswith(("/harbor/skills/svg-brief-design/", "/app/", "/logs/artifacts/")) for p in reads)
        safe_commands = not any(token in command for command in commands for token in ("/tests", "/solution", "/curator", "auth.json", "curl ", "wget "))
        payload = inputs.get("skill_files") == expected == integrity.get("files") and integrity.get("unchanged") is True
        valid = exact_model and tools_ok and safe_reads and safe_commands and payload and not invalid
        instruction = (task / "instruction.md").read_text()
        output_match = re.search(r"`(/logs/artifacts/[^`]+\.svg)`", instruction)
        artifact = trial / "artifacts" / output_match.group(1).lstrip("/") if output_match else None
        metrics_path = trial / "verifier/metrics.json"
        metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
        record = {"candidate": candidate, "task": result["task_name"], "trial": trial.name,
                  "native_result": str(path), "native_exception": result.get("exception_info"),
                  "reward": (result.get("verifier_result") or {}).get("rewards"), "metrics": metrics,
                  "exact_model": exact_model, "tools_ok": tools_ok, "safe_reads": safe_reads, "safe_commands": safe_commands,
                  "payload_unchanged": payload, "invalid_json_lines": invalid, "runtime_valid": valid,
                  "reads": reads, "commands": commands, "tool_counts": dict(Counter(e.get("toolName") for e in starts)),
                  "renderer_helper_used": any("render_svg.py" in command for command in commands),
                  "scaffold_helper_used": any("scaffold.py" in command for command in commands),
                  "preview_read": any(path.lower().endswith(".png") for path in reads),
                  "artifact": str(artifact) if artifact and artifact.exists() else None,
                  "total_tokens": sum(m.get("usage", {}).get("totalTokens", 0) for m in messages)}
        records.append(record)
        groups.setdefault(result["task_name"], {"task": task, "arms": {}})["arms"].setdefault(candidate, []).append(record)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    gallery = []
    for task_id, data in sorted(groups.items()):
        arms = sorted(data["arms"])
        sheet = Image.new("RGB", (1280, 325*len(arms)), "#eeeeee")
        draw = ImageDraw.Draw(sheet)
        for index, candidate in enumerate(arms):
            sheet.paste(preview(data["task"] / "tests/reference.svg"), (0, 325*index+30))
            draw.text((10, 325*index+8), "Reference / " + candidate, fill="black", font=font)
            for repeat, record in enumerate(data["arms"][candidate]):
                if record["artifact"]:
                    sheet.paste(preview(Path(record["artifact"])), ((repeat+1)*320, 325*index+30))
                reward = (record["reward"] or {}).get("visual_similarity")
                label = f"{candidate} / {repeat+1} / " + (f"{reward:.4f}" if reward is not None else "unavailable")
                draw.text(((repeat+1)*320+10, 325*index+8), label, fill="black", font=font)
        path = out / (task_id + ".jpg")
        sheet.save(path, quality=94)
        gallery.append(f'<h2>{task_id}</h2><img src="{path.name}" style="max-width:100%">')
    (out / "index.html").write_text('<!doctype html><meta charset="utf-8"><title>Procedural SVG comparison</title><body style="font-family:system-ui;max-width:1320px;margin:24px auto"><h1>All matched development outputs</h1><p>Private local review; purchased references are not part of the skill. b: original guide; p: first procedural candidate; q: documented renderer entrypoint.</p>' + "\n".join(gallery))
    summary = {"trials": len(records), "runtime_passes": sum(r["runtime_valid"] for r in records), "records": records,
               "all_outputs_review_required": True, "scores_recalculated": False}
    (out / "audit.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps({"trials": len(records), "runtime_passes": summary["runtime_passes"], "gallery": str(out / "index.html")}))


if __name__ == "__main__":
    main()
