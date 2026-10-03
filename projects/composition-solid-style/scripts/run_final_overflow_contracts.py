#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Freeze strict current payload contracts for the five changed overflow helpers."""
import concurrent.futures,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
CASES={
'compose-synchronized-svg':(5,['output/diagram.svg','output/plan.json','output/composition.json','output/brief.json','output/static.json']),
'diagram-composition':(2,['output/brief.json','output/plan.json','output/panels.json','output/diagram.svg','output/composition.json']),
'usefulcharts-style':(2,['output/source.json','output/poster.svg','output/poster.html','output/render.json','output/palette.md']),
'video':(2,['output/scene-contract.json','output/validation.json','output/palette.md']),
'manim-svg-video':(3,['output/source.svg','output/composition/composition-manifest.json','output/composition/manim_svg_video_scene.py'])}
OUT=ROOT/'projects/composition-solid-style/artifacts/pi';OUT.mkdir(parents=True,exist_ok=True)
def run(item):
    skill,(attempt,outputs)=item;rid=f'solid-composition-{skill}-20261003-{attempt}';model='gpt-5.6-luna'
    cmd=['uv','run','--script','scripts/run-pi-skill-eval.py',skill,'--prompt-file',f'evaluations/composition-solid-style/prompts/{skill}.md','--model',f'openai-codex/{model}','--mode','json','--strict','--run-id',rid]
    for output in outputs:cmd+=['--expect-output',output]
    result=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace')
    (OUT/f'{skill}-overflow-final.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    trace_cmd=['uv','run','--script','scripts/summarize-pi-json-events.py',f'evaluations/runs/{rid}/events.jsonl','--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str((OUT/f'{skill}-overflow-trace.json').relative_to(ROOT))]
    trace=subprocess.run(trace_cmd,cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace')
    (OUT/f'{skill}-overflow-trace.txt').write_text(trace.stdout+trace.stderr,encoding='utf-8')
    record={'skill':skill,'runId':rid,'model':model,'command':cmd,'exitCode':result.returncode,'traceCommand':trace_cmd,'traceExitCode':trace.returncode}
    print(json.dumps(record),flush=True);return record
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    for result in pool.map(run,CASES.items()):
        results.append(result)
        (ROOT/'evaluations/composition-solid-style/final-overflow-contracts-20261003.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
if any(r['exitCode'] or r['traceExitCode'] for r in results):raise SystemExit(1)
