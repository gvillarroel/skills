#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Seal current runtime evidence and retain superseded revision attempts."""
import hashlib,importlib.util,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('pi_harness',root/'scripts/run-pi-skill-eval.py')
harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
dest=root/'evaluations/composition-solid-style';dest.mkdir(parents=True,exist_ok=True)
skills=['compose-synchronized-svg','diagram-composition','hierarchy-lens','usefulcharts-style','hyperframes-explainer','video','manim-svg-video']
records=[]
for skill in skills:
    attempt={'compose-synchronized-svg':5,'diagram-composition':2,'usefulcharts-style':2,
             'video':2,'manim-svg-video':3}.get(skill,1)
    rid=f'solid-composition-{skill}-20261003-{attempt}';run=root/'evaluations/runs'/rid
    read=lambda name:json.loads((run/name).read_text(encoding='utf-8-sig'))
    manifest,result,artifacts,events,integrity=[read(name) for name in ['run-manifest.json','evaluation-result.json','artifact-check.json','event-check.json','skill-integrity-check.json']]
    snapshot={p:v for p,v in harness.snapshot_tree(root/'skills'/skill).items() if not any(part in harness.COPY_IGNORE for part in Path(p).parts) and not p.startswith('assets/examples/')}
    digest=harness.snapshot_digest(snapshot)
    assert digest==manifest['skill']['payloadSha256'],f'{skill}: stale runtime freeze'
    assert result['passed'] and artifacts['passed'] and events['passed'] and integrity['passed']
    old=[f'solid-composition-{skill}-20261003-{i}' for i in range(1,attempt)]
    outputs=artifacts['outputs']
    records.append({'skill':skill,'runId':rid,'model':manifest['pi']['model'],'strict':manifest['eventPolicy']['strict'],'passed':result['passed'],'gates':result['gates'],'runtimeSha256':digest,'fileCount':len(snapshot),'exactOutputs':outputs,'manifestPath':str((run/'run-manifest.json').relative_to(root)).replace('\\','/'),'supersededPassingFreezes':old,'harnessCommand':(run/'command.txt').read_text(encoding='utf-8-sig')})
owned=subprocess.run(['git','diff','--name-only','--',*[f'skills/{s}' for s in skills]],cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace').stdout.splitlines()
new=subprocess.run(['git','ls-files','--others','--exclude-standard','--',*[f'skills/{s}' for s in skills]],cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace').stdout.splitlines()
report={'date':'2026-10-03','purpose':'Supplementary solid-first revision, not a new full release cohort','records':records,'changedSkillPaths':sorted(set(owned+new)),'paletteMetadataOwner':'Root agent; palette allowed tokens unchanged','browser':{'styleStates':83,'styleReport':'projects/composition-solid-style/artifacts/browser/audit.json','compositionStrongReport':'projects/composition-solid-style/artifacts/heatwave-browser-navigation.json','navigationReport':'projects/composition-solid-style/artifacts/navigation-final.json','hierarchyStrongReport':'projects/composition-solid-style/artifacts/hierarchy-analytical-audit.json'},'deterministicCommands':'projects/composition-solid-style/artifacts/tests/commands.json','overflowCopiesReport':'projects/composition-solid-style/artifacts/overflow-helpers-final.json','fixtureRegenerationCommands':'projects/composition-solid-style/artifacts/regeneration/commands.json','retainedFailures':['projects/composition-solid-style/artifacts/compose-tests-revision-final.txt','projects/composition-solid-style/artifacts/heatwave-browser.json','projects/composition-solid-style/artifacts/heatwave-browser-repaired.json','projects/composition-solid-style/artifacts/heatwave-browser-final.json','projects/composition-solid-style/artifacts/navigation-before.json','projects/composition-solid-style/artifacts/svg-navigation-pairs.txt','projects/composition-solid-style/artifacts/manim-smoke/middle.png']}
(dest/'validation-20261003.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'currentStrictFreezes':len(records),'evidence':str((dest/'validation-20261003.json').relative_to(root))}))
