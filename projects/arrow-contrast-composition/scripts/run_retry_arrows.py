#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run six sequential strict skill-only arrow tasks; retain every failure."""
import json,subprocess,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
CASES={
'compose-synchronized-svg':['output/brief.json','output/plan.json','output/diagram.svg','output/browser.json','output/preview.png','output/arrow-audit.json'],
'diagram-composition':['output/brief.json','output/diagram.svg','output/browser.json','output/preview.png','output/arrow-audit.json'],
'usefulcharts-style':['output/source.json','output/poster.svg','output/poster.html','output/render.json','output/browser.json','output/preview.png'],
'hyperframes-explainer':['output/brief.json','output/project/index.html','output/audit.json','output/preview.png'],
'video':['output/index.html','output/svg-arrows.js','output/video.mp4','output/arrow-audit.json','output/frame.png'],
'manim-svg-video':['output/source.svg','output/composition/composition-manifest.json','output/composition/manim_svg_video_scene.py','output/composition/media/videos/manim_svg_video_scene/360p12/arrow-check-exact-2s.mp4','output/frame.png']}
OUT=ROOT/'projects/arrow-contrast-composition/artifacts/pi';OUT.mkdir(parents=True,exist_ok=True)
ledger=ROOT/'evaluations/arrow-contrast-composition/isolated-retry-20261003.json'
results=json.loads(ledger.read_text()) if ledger.exists() and len(sys.argv)>1 else []
for skill,outputs in CASES.items():
 if len(sys.argv)>1 and skill not in sys.argv[1:]:continue
 model='gpt-6-luna' if skill=='hyperframes-explainer' else 'gpt-5.6-luna';attempt=int(json.loads(os.environ.get('ARROW_PI_ATTEMPTS','{}')).get(skill,os.environ.get('ARROW_PI_ATTEMPT',3 if skill in ['video','manim-svg-video'] else 2)));rid=f'arrow-composition-{skill}-20261003-{attempt}'
 cmd=['uv','run','--script','scripts/run-pi-skill-eval.py',skill,'--prompt-file',f'evaluations/arrow-contrast-composition/prompts/{skill}.md','--model',f'openai-codex/{model}','--mode','json','--strict','--run-id',rid]
 for artifact in outputs:cmd+=['--expect-output',artifact]
 r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace');(OUT/f'{skill}-{attempt}.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
 result={'skill':skill,'runId':rid,'model':model,'command':cmd,'exitCode':r.returncode,'expectedOutputs':outputs}
 events=ROOT/f'evaluations/runs/{rid}/events.jsonl'
 if events.is_file():
  tracecmd=['uv','run','--script','scripts/summarize-pi-json-events.py',str(events.relative_to(ROOT)),'--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str((OUT/f'{skill}-trace-{attempt}.json').relative_to(ROOT))]
  trace=subprocess.run(tracecmd,cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace');(OUT/f'{skill}-trace-{attempt}.txt').write_text(trace.stdout+trace.stderr,encoding='utf-8');result.update(traceCommand=tracecmd,traceExitCode=trace.returncode)
 results=[x for x in results if x['skill']!=skill];results.append(result);(ROOT/'evaluations/arrow-contrast-composition/isolated-retry-20261003.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8');print(json.dumps(result),flush=True)
raise SystemExit(any(x['exitCode'] or x.get('traceExitCode',0) for x in results))
