#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run isolated offline adapter evidence; native UI evidence is recorded separately."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'evaluations/line-world-google-vids';folder.mkdir(parents=True,exist_ok=True)
prompts=folder/'prompts';prompts.mkdir(exist_ok=True)
base='Use only the loaded line-world-google-vids skill and normal local tools. Keep the copied skill read-only. Do not browse, discover other skills, operate a real account, or claim native UI actions. This is an offline adapter test with supplied observations. Write all requested exact paths in the workspace. '
story={'projectTitle':'Pipeline walkthrough','fps':30,'scenes':[{'id':'prepare','script':'Prepare the data and split by entity.','visual':'grouped split','clipSeconds':30,'essentialAnimationSeconds':5},{'id':'compare','script':'Compare a baseline with cross validation.','visual':'linked table and error curve','clipSeconds':30,'essentialAnimationSeconds':6},{'id':'evaluate','script':'Freeze the model and evaluate the independent holdout.','visual':'frozen test','clipSeconds':30,'essentialAnimationSeconds':7}]}
obs={'voice':'Nyla','projectUrl':'https://docs.google.com/videos/d/offline-fixture/edit','measurementMethod':'supplied native scene observations, 0.1 second resolution','scenes':[{'id':'prepare','observed':True,'voiceoverSeconds':20.4,'sceneSeconds':20.4},{'id':'compare','observed':True,'voiceoverSeconds':22.6,'sceneSeconds':22.6},{'id':'evaluate','observed':True,'voiceoverSeconds':20.6,'sceneSeconds':20.6}]}
cases={
'contract':base+'Save the following input as inputs/story.json and inputs/observed.json. Use the bundled prepare and compile commands to produce handoff/scripts.txt, handoff/observed.json and release/timing.json. Keep the generated worksheet unmeasured; compile using the supplied inputs/observed.json. Story: '+json.dumps(story)+' Observations: '+json.dumps(obs),
'naturalistic':base+'Prepare a Google Vids handoff for a clean three-scene training video. Preserve the exact scripts, order and measured durations below. Deliver editable input files at inputs/story.json and inputs/observed.json, ordered scripts at handoff/scripts.txt, an unmeasured worksheet at handoff/observed.json, and a measured contiguous 30 fps timeline at release/timing.json. Explain that these supplied observations are not a live editor verification. Story: '+json.dumps(story)+' Observations: '+json.dumps(obs),
'generalization':base+'Adapt this handoff to 24 fps with two scenes. Create inputs/story.json, inputs/observed.json, handoff/scripts.txt, handoff/observed.json and release/timing.json. Scene IDs: inspect then decide. Their exact scripts are "Inspect the grouped error." and "Decide using reserved evidence." Their visual briefs are "table and scatter" and "pipeline". Each source clip lasts 10 seconds, with essential animation 3 seconds. Native voice Alba was observed with speech 5.0 and 6.5 seconds, scene durations 5.5 and 7.25 seconds, leading silence zero and tails 0.5 and 0.75 seconds respectively. Mark observations measured and retain fractional durations. The project name is "Reserved evidence". Do not invent a Vids URL.',
'boundary':base+'No native account or measured audio durations are available. Create a two-scene draft with IDs inspect and decide, English scripts of your choice, 20-second source clips and essential animation 5 seconds. Save inputs/story.json, draft/scripts.txt and draft/observed.json. Keep observations unmeasured. Demonstrate that compiling this worksheet fails without inventing measurements: capture the expected validation failure inside a local subprocess so it is not a tool error, and write boundary/check.json with ok=true, rejected=true and the returned error. Write boundary/status.md explaining the native voice/export steps that remain unverified.'}
for name,prompt in cases.items():(prompts/(name+'.md')).write_text(prompt+'\n',encoding='utf-8')
# Explicit account exception is recorded in SKILLS.md, matching earlier Line World tests.
results=[]
for name,count in [('contract',1),('naturalistic',3),('generalization',3),('boundary',1)]:
    for repeat in range(1,count+1):
        runid=f'20261115-line-world-vids-{name}-{repeat}'
        expected=['inputs/story.json','draft/scripts.txt','draft/observed.json','boundary/check.json','boundary/status.md'] if name=='boundary' else ['inputs/story.json','inputs/observed.json','handoff/scripts.txt','handoff/observed.json','release/timing.json']
        cmd=['uv','run','--script',str(ROOT/'scripts/run-pi-skill-eval.py'),'line-world-google-vids','--prompt-file',str(prompts/(name+'.md')),'--model','openai-codex/gpt-6.1-sol','--thinking','medium','--mode','json','--strict','--run-id',runid]
        for path in expected:cmd+=['--expect-output',path]
        target='boundary/check.json::rejected=true' if name=='boundary' else 'release/timing.json::frames='+('306' if name=='generalization' else '1908')
        cmd+=['--expect-output-json-field',target]
        result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        record={'case':name,'repeat':repeat,'runId':runid,'exitCode':result.returncode,'requiredOutputs':expected,'command':cmd}
        results.append(record);print(json.dumps(record),flush=True)
        (folder/'offline-results-20261115.json').write_text(json.dumps({'model':'openai-codex/gpt-6.1-sol','date':'2026-11-15','scope':'offline handoff and evidence gates; actual native UI is a separate manual test','results':results},indent=2)+'\n')
        if result.returncode:print(result.stdout[-4000:]+result.stderr[-2000:],flush=True)
raise SystemExit(0 if all(r['exitCode']==0 for r in results) else 1)
