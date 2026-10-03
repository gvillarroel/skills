#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run supplementary strict runtime contracts for seven composition bundles."""
import concurrent.futures,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
CASES={
'compose-synchronized-svg':['output/diagram.svg','output/plan.json','output/composition.json','output/brief.json','output/static.json'],
'diagram-composition':['output/brief.json','output/plan.json','output/panels.json','output/diagram.svg','output/composition.json'],
'hierarchy-lens':['output/explorer.html','output/decision.html','output/source.json','output/commands.md'],
'usefulcharts-style':['output/source.json','output/poster.svg','output/poster.html','output/render.json','output/palette.md'],
'hyperframes-explainer':['output/brief.json','output/preflight.json','output/build.json','output/project/index.html'],
'video':['output/scene-contract.json','output/validation.json','output/palette.md'],
'manim-svg-video':['output/source.svg','output/composition/composition-manifest.json','output/composition/manim_svg_video_scene.py']}
OUT=ROOT/'projects/composition-solid-style/artifacts/pi';OUT.mkdir(parents=True,exist_ok=True)
def run(item):
    skill,outputs=item;model='gpt-6-luna' if skill=='hyperframes-explainer' else 'gpt-5.6-luna'
    rid=f'solid-composition-{skill}-20261003-1'
    cmd=['uv','run','--script','scripts/run-pi-skill-eval.py',skill,'--prompt-file',f'evaluations/composition-solid-style/prompts/{skill}.md','--model',f'openai-codex/{model}','--mode','json','--strict','--run-id',rid]
    for output in outputs:cmd+=['--expect-output',output]
    r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace')
    (OUT/f'{skill}.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
    result={'skill':skill,'runId':rid,'model':model,'command':cmd,'exitCode':r.returncode,'expectedOutputs':outputs}
    event=ROOT/f'evaluations/runs/{rid}/events.jsonl'
    if event.exists():
        summary=['uv','run','--script','scripts/summarize-pi-json-events.py',str(event.relative_to(ROOT)),'--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str((OUT/f'{skill}-trace.json').relative_to(ROOT))]
        trace=subprocess.run(summary,cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace')
        (OUT/f'{skill}-trace.txt').write_text(trace.stdout+trace.stderr,encoding='utf-8')
        result.update(traceCommand=summary,traceExitCode=trace.returncode)
    print(json.dumps(result),flush=True)
    return result
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    for result in pool.map(run,CASES.items()):
        results.append(result)
        (ROOT/'evaluations/composition-solid-style/isolated-contracts-20261003.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
if any(r['exitCode'] or r.get('traceExitCode',0) for r in results):raise SystemExit(1)
