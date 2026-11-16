#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently grade the final orchestrator cohort and materialized producer runs."""
import importlib.util
import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edition',choices=('v041','v050'),default='v041')
    edition=parser.parse_args().edition
    spec=importlib.util.spec_from_file_location('line_world_release_harness',ROOT/'scripts/run-pi-skill-eval.py')
    harness=importlib.util.module_from_spec(spec);sys.modules[spec.name]=harness;spec.loader.exec_module(harness)
    version=read(ROOT/'projects/line-world-video/package-spec.json')['version']
    package=ROOT/'projects/line-world-video/artifacts/packages'/('line-world-video-'+version)/'plugin/skills'
    subjects=[('orchestrator',case,n,ROOT/'evaluations/runs'/f'20261114-line-world-{edition}-{case}-sol-{n}','line-world-video',ROOT/'skills/line-world-video') for case,n in [('contract',1),('boundary',1),*[(c,n) for c in ('naturalistic','generalization') for n in (1,2,3)]]]
    probes=[('d3',n,'line-world-profiles-v041') for n in (1,2,3)]+[('mermaid',1,'line-world-profiles-v040'),('icons',1,'line-world-plugin-profiles')]+[('hyperframes',n,'line-world-plugin-profiles') for n in (1,2,3)]
    if edition=='v050':probes=[(name,1,'line-world-profiles-v050') for name in ('d3','icons')]+[(name,n,'line-world-profiles-v050') for name in ('mermaid','hyperframes') for n in (1,2,3)]
    subjects += [('producer',name,n,ROOT/'evaluations/runs'/cohort/'evaluations/runs'/f'20261114-line-world-{name}-contract-sol-{n}','line-world-'+name,package/('line-world-'+name)) for name,n,cohort in probes]
    if edition=='v050':subjects.append(('producer','hyperframes-attention',1,ROOT/'evaluations/runs/line-world-profiles-v050/evaluations/runs/20261114-line-world-hyperframes-attention-sol-1','line-world-hyperframes',package/'line-world-hyperframes'))
    results=[]
    for scope,case,n,run,name,source in subjects:
        if not (run/'evaluation-result.json').is_file():
            results.append({'scope':scope,'case':case,'repeat':n,'ok':False,'checks':{'complete':False}});continue
        work=run/'workspace';evaluation=read(run/'evaluation-result.json')
        trace=subprocess.run(['uv','run','--script',str(ROOT/'scripts/summarize-pi-json-events.py'),str(run/'events.jsonl'),'--output',str(run/'read-surface.json'),'--require-model','gpt-6.1-sol','--fail-on-invalid-json','--fail-on-tool-error','--require-tool-call','--require-read','../prompt.md','--forbid-read-regex',r'(?i)(?:^|[\\/])assets[\\/]examples(?:[\\/]|$)'],capture_output=True,text=True)
        checks={'strictHarness':evaluation['passed'],'trace':trace.returncode==0,'currentPayloadMatches':harness.snapshot_tree(source)==harness.snapshot_tree(work/'skills'/name)}
        if scope=='orchestrator':
            directory='lab-film' if case=='generalization' else 'boundary-film' if case=='boundary' else 'film'
            story,timing=read(work/directory/'story.json'),read(work/directory/'timing.json')
            checks['noAutomaticTitles']=story.get('presentation',{}).get('contextLabels',{})=={}
            beats=timing['beats'];checks['contiguousClock']=beats[0]['start']==0 and all(a['end']==b['start'] for a,b in zip(beats,beats[1:])) and beats[-1]['end']==timing['duration']
            if case in ('contract','naturalistic','boundary'):
                expected_palette='colorset2' if edition=='v050' and case=='naturalistic' else 'colorset1'
                checks['atlas']=story['mode']=='atlas' and len(story['scenePlan'])==16 and story['palette']==expected_palette
                coverage=read(work/directory/'coverage.json')
                checks['inventory']=len(coverage['mermaidFamilies'])==20 and len(coverage['d3Forms'])==26 and coverage['panels']==46
                checks['duration']=timing['duration']==(189 if case=='naturalistic' else 185)
                sys.path.insert(0,str(ROOT/'skills/line-world-video/scripts'))
                from atlas_story import partition_check,DEFAULT_ATLAS
                checks['fullFramePartitions']=all(abs(partition_check(s['panels'])['coveredArea']-1)<1e-8 for s in story['scenePlan'])
                checks['sameFacts']=all(story[k]==DEFAULT_ATLAS[k] for k in ('rows','flows','schedule','sites'))
                if case=='naturalistic':checks['requestedRetime']=[s['seconds'] for s in story['scenePlan']]==[18 if s['id']=='records' else s['seconds'] for s in DEFAULT_ATLAS['scenePlan']]
            if case in ('naturalistic','generalization'):
                audit=read(work/('lab-review' if case=='generalization' else 'review')/'audit.json')
                checks['actualBrowserAudit']=audit['ok'] and not audit['findings'] and len(audit['samples'])>=16 and all(Path(s['path']).is_file() for s in audit['samples'])
                if edition=='v050':
                    checks['primaryRed']=all(s['state']['guideColor']=='#9e1b32' for s in audit['samples'])
                    if case=='naturalistic':
                        checks['semanticPointMap']=story['attention']['categoryColors']=={'intake':'#007298','review':'#45842a','build':'#652f6c','release':'#e77204'}
                        checks['visibleSizeVariation']=audit['attention']['minimumSampleRadius']<=6 and audit['attention']['maximumSampleRadius']>=31.99
                        checks['quantityReceivers']=audit['attention']['quantityViews']==['circle-pack','donut','network']
            if case=='generalization':
                checks['newFacts']=[(r['id'],r['before'],r['after'],r['trend']) for r in story['rows']]==[('alpha',9,6,[9,8,7,6]),('beta',7,4,[7,6,5,4]),('gamma',12,8,[12,11,9,8])]
                checks['newTiming']=timing['duration']==35 and [b['duration'] for b in timing['beats']]==[3,3,2,11,7,5,4]
                checks['newUnitsAndColor']=story['unit']=='hours' and story['palette']=='colorset2' and bool(story['paletteReason'])
            if case=='boundary':
                report=read(work/'boundary-report.json')
                checks['rejections']=len(report['cases'])==(8 if edition=='v050' else 4) and all(c['rejected'] and c['timingManifestUnchanged'] for c in report['cases']) and report['validStoryRestored'] and report['pass']
        elif case=='mermaid':
            root=ET.parse(work/'diagram/asset.svg').getroot();ns='{http://www.w3.org/2000/svg}'
            texts=[''.join(e.itertext()).strip() for e in root.iter(ns+'text')]
            checks['realVideoFinish']=root.get('data-video-style')=='line-world'
            checks['noVisibleDraftTitle']=not any('Draft heading' in text for text in texts)
            checks['metadata']=all(root.find(ns+tag) is not None and ''.join(root.find(ns+tag).itertext()).strip() for tag in ('title','desc'))
            checks['tasks']=all(any(label in text for text in texts) for label in ('Intake','Review','Release'))
            backgrounds=[e for e in root.iter() if 'node-bkg' in e.get('class','')]
            checks['neutralNativeEventSurfaces']=bool(backgrounds) and all('#ffffff!important' in e.get('style','') for e in backgrounds)
        elif case=='d3':
            svg=(work/'film/asset.svg').read_text(encoding='utf-8')
            receipt=(work/'review/receipt.json').read_text(encoding='utf-8')
            checks['sourceLabels']=all(value in svg for value in ('Alpha','Beta','Gamma'))
            checks['realD3Version']='7.9.0' in receipt
            exported=read(work/'review/receipt.json')
            checks['actualExporterPass']=exported.get('ok') is True and all(exported['checks'].values())
        elif case=='icons':
            checks['realProviderReceipts']=all('lucide' in (work/'icons'/(name+'.svg.json')).read_text(encoding='utf-8') for name in ('database','workflow'))
            license_text=(work/'icons/LICENSE.txt').read_text(encoding='utf-8')
            checks['license']=('MIT' in license_text or 'ISC' in license_text) and 'Copyright' in license_text
            checks['svgRoots']=all(ET.parse(work/'icons'/(name+'.svg')).getroot().tag.endswith('svg') for name in ('database','workflow'))
        elif case.startswith('hyperframes'):
            html=(work/'film/index.html').read_text(encoding='utf-8')
            code=html+'\n'+'\n'.join(p.read_text(encoding='utf-8') for p in (work/'film').rglob('*') if p.suffix in ('.js','.mjs') and 'assets' not in p.parts)
            checks['nativeClockContract']='data-composition-id' in html and all(value in code for value in ('__timelines','renderAt','snapshot'))
            seek=read(work/'review/seek-check.json')
            checks['actualSeekEvidence']=bool(seek.get('checks')) and all(seek['checks'].values()) and len(seek.get('states',seek.get('sequence',[])))>=3 and not seek.get('errors',[])
        result={'scope':scope,'case':case,'repeat':n,'ok':all(checks.values()),'checks':checks,'run':run.relative_to(ROOT).as_posix()}
        results.append(result);(run/'independent-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    gates={'orchestrator':all(r['ok'] for r in results if r['scope']=='orchestrator')}
    primary_counts={case:{'passed':sum(r['ok'] for r in results if r['scope']=='orchestrator' and r['case']==case),'total':sum(r['scope']=='orchestrator' and r['case']==case for r in results)} for case in ('contract','boundary','naturalistic','generalization')}
    if edition=='v050':
        # Apply the repository's pre-existing repetition policy: at least 2/3
        # fresh naturalistic/generalization runs; every contract/boundary run.
        gates['orchestrator']=all(v['total']==(3 if case in ('naturalistic','generalization') else 1) and v['passed']>=(2 if case in ('naturalistic','generalization') else 1) for case,v in primary_counts.items())
    for name in ('d3','mermaid','icons','hyperframes'):
        rows=[r for r in results if r['scope']=='producer' and (r['case']==name or name=='hyperframes' and r['case']=='hyperframes-attention')]
        if edition=='v050':
            # These are deterministic producer contract smokes, whose repository
            # minimum is one passing run. Preserve every diagnostic attempt.
            gates[name]=any(r['ok'] for r in rows)
        else:gates[name]=all(r['ok'] for r in rows if r['repeat']>=2) if name=='hyperframes' else all(r['ok'] for r in rows)
    report={'ok':all(gates.values()),'allStrict':all(r['ok'] for r in results),'passed':sum(r['ok'] for r in results),'total':len(results),'releaseGates':gates,'model':'openai-codex/gpt-6.1-sol','results':results,'policy':'Primary formal release cohort: 8/8. Final D3 verification: 3/3. Single current Mermaid/Iconify smokes. HyperFrames: two fresh verification runs after a retained diagnostic failure. Producer smokes are separate integration evidence.'}
    if edition=='v050':
        report['primaryCaseCounts']=primary_counts
        report['producerCaseCounts']={name:{'passed':sum(r['ok'] for r in results if r['scope']=='producer' and r['case']==name),'total':sum(r['scope']=='producer' and r['case']==name for r in results)} for name in ('d3','mermaid','icons','hyperframes','hyperframes-attention')}
        report['policy']='Apply evaluations/README.md: one passing deterministic contract/boundary or producer smoke; at least two of three fresh naturalistic/generalization runs. Preserve every strict failure and independently inspect artifacts. Producer integration probes are separate from the formal primary cohort.'
    (ROOT/'evaluations/line-world-video'/('plugin-'+edition+'-results.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
    return 0 if report['ok'] else 1


if __name__=='__main__':
    raise SystemExit(main())
