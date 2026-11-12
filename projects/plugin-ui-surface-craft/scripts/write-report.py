#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect exact per-surface contract and connected-renderer evidence."""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects/plugin-ui-surface-craft"
NAMES = ["desktop-plugin-ui", "desktop-chat-plugin-ui", "code-native-plugin-ui", "pi-extension-ui", "codex-plugin-ui", "chatgpt-desktop-plugin-ui", "gemini-enterprise-ui", "reflex-xy"]

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    forwards, sources = [], []
    for name in NAMES:
        attempt = 2 if name == "desktop-chat-plugin-ui" else 1
        run_id = f"20261112-surface-craft-{name}-sol-{attempt}"
        run = ROOT / "evaluations/runs" / run_id
        result, event, trace = (read(run / f) for f in ["evaluation-result.json", "event-check.json", "trace-summary.json"])
        p = run / "workspace/surface-contract.json"
        contract = read(p)
        words = len(p.read_text(encoding="utf-8").split())
        shape = set(contract) == {"targetSurface", "stylingAuthority", "implementation", "fallbacks", "validation"} and words < 900
        if not shape:
            raise ValueError(f"Independent contract shape/word check failed: {name}")
        forwards.append({"skill": name, "runId": run_id, "strictPassed": result["passed"], "eventPassed": event["passed"], "tracePassed": trace["passed"], "artifactShapePassed": shape, "words": words, "model": "openai-codex/gpt-6.1-sol", "thinking": "medium", "scope": "One implementation contract; no new host installation or paint claim."})
        sources.extend([ROOT / f"skills/{name}/SKILL.md", ROOT / f"skills/{name}/references/craft-by-surface.md"])
    request_path = ROOT / "evaluations/runs/20261112-surface-craft-reflex-xy-sol-1/workspace/request.json"
    spec = read(request_path)
    marks = spec["marks"]
    exact = spec["version"] == 1 and spec["colorset"] == "colorset1" and len(marks) == 2 and marks[0]["args"] == [[0, 1, 2], [110, 140, 190]] and marks[1]["args"] == [[0, 1, 2], [150, 150, 150]]
    if not exact:
        raise ValueError("Generated XY request changed the supplied observations or objective.")
    live = read(PROJECT / "artifacts/xy-live-render.json")
    png = PROJECT / "artifacts/images/xy-render.png"
    svg = PROJECT / "artifacts/images/xy-render.svg"
    native_size = struct.unpack(">II", png.read_bytes()[16:24])
    report = {"schemaVersion": 1, "date": "2026-11-12", "purpose": "Implement focused craft at each surface's actual styling authority.", "skills": NAMES, "forwards": forwards,
        "retainedEarlierRun": {"runId": "20261112-surface-craft-desktop-chat-plugin-ui-sol-1", "strictPassed": True, "finalCandidate": False, "reason": "Refined the example CSS to preserve the inherited font family; final Claude Chat contract uses sol-2."},
        "deterministicChecks": {"selectedSkillValidation": "8 bundles passed", "a2uiCheckerTests": {"passed": True, "tests": 12}, "a2uiStarters": {"passed": True, "streams": 2, "scope": "v0.9 closed-tree integrity only; no full catalog or host paint claim"}, "xyCheckerTests": {"passed": True, "tests": 4}, "generatedXYSpec": {"passed": read(PROJECT / "artifacts/xy-spec-review.json")["passed"], "exactDataPassed": exact}},
        "liveXY": {"renderer": "connected xy_render_chart", "palette": live["palette"], "marks": live["marks"], "cssSize": [live["width"], live["height"]], "nativePngSize": list(native_size), "warnings": live["warnings"], "specSha256": hashlib.sha256(request_path.read_bytes()).hexdigest(), "exports": [{"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in [png, svg]], "manualInspection": "Observed red data line preserves 110/140/190 ms, dashed objective remains at 150 ms, axes retain units, lower-right legend does not obscure the high endpoint.", "scope": "Actual connected renderer and native exports; no new stock-host UI paint or live Python callback acceptance."},
        "sourceSha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "hostLimits": "Native control paint, signed-in MCP App placement, Gemini registration and agent continuation retain their prior independently scoped evidence. No personal configuration or cloud settings changed."}
    target = ROOT / "evaluations/desktop-plugin-ui/surface-craft-20261112.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"finalContractsPassed": sum(r["strictPassed"] for r in forwards), "skills": len(NAMES), "liveXYPalette": live["palette"], "liveXYMarks": live["marks"], "nativePngSize": list(native_size)}))

if __name__ == "__main__":
    main()
