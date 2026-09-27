#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain compact results, including superseded and unsuccessful attempts."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
ARTIFACTS=ROOT/'projects/visual-asset-composition/artifacts'
OUT=ROOT/'evaluations/visual-asset-composition/summary-20260927.json'


def read(path): return json.loads(path.read_text(encoding='utf-8'))


def classification(run_id,passed):
    if run_id=='assets-d3-contract-20260927-b-1':return 'agent: optional export outside requested workspace; excluded despite harness pass'
    if passed:return None
    if 'assets-d3-' in run_id and '-a-' in run_id:return 'skill: studio routing and initial metadata; contract also used an unsupported prompt fence'
    if 'assets-d3-generalization-' in run_id and '-b-' in run_id:return 'skill: static HTML palette check used for dynamic SVG marks'
    if 'assets-d3-' in run_id:return 'agent: ignored output or rendered-palette instructions'
    if 'assets-echarts-' in run_id:return 'agent: required command combined with a copy command'
    if 'assets-plantuml-' in run_id and '-a-' in run_id:return 'skill: Windows command resolution and redundant probes'
    if 'assets-plantuml-' in run_id and '-d-' in run_id:return 'validator: neutral CS1 output rejected; redundant probes also observed'
    if 'assets-plantuml-' in run_id:return 'skill: output-root ambiguity and redundant color probes'
    if 'assets-procedural-' in run_id:return 'skill/agent: redundant path, URL, manifest or default-encoding assertions'
    return 'unclassified'


def main():
    selected=read(ARTIFACTS/'forward-review/report.json')
    selected_ids={r['runId'] for r in selected}
    attempts=[]
    for path in sorted((ROOT/'evaluations/runs').glob('assets-*-20260927-*/evaluation-result.json')):
        folder=path.parent
        manifest=read(folder/'run-manifest.json')
        result=read(path)
        events=read(folder/'event-check.json') if (folder/'event-check.json').exists() else {}
        artifact=read(folder/'artifact-check.json') if (folder/'artifact-check.json').exists() else {}
        errors=[]
        for call in events.get('calls',[]):
            if call.get('isError'):
                command=call.get('command') or call.get('path') or ''
                # Raw shell selectors resemble authored pattern IDs to repository scans.
                # Retain exact command hashes and event lines; raw traces keep the text.
                errors.append({'tool':call['tool'],'line':call['line'],
                               'commandSha256':hashlib.sha256(command.encode()).hexdigest()})
        attempts.append({'runId':folder.name,'selected':folder.name in selected_ids,'skill':manifest['skill']['name'],
                         'model':manifest['pi']['model'],'thinking':manifest['pi']['thinking'],
                         'payloadSha256':manifest['skill']['payloadSha256'],'fileCount':manifest['skill']['fileCount'],
                         'promptSha256':manifest['prompt']['sha256'],'harnessPassed':result['passed'],
                         'durationSeconds':result['durationSeconds'],'gates':result['gates'],
                         'classification':classification(folder.name,result['passed']),
                         'eventFindings':events.get('findings',[]),'toolErrors':errors,
                         'outputs':artifact.get('outputs',[]),
                         'readPaths':[c['path'] for c in events.get('calls',[]) if c.get('tool')=='read'],
                         'rawEvidence':folder.relative_to(ROOT).as_posix()})
    cases=[]
    for skill,kind in sorted({(r['skill'],r['case']) for r in selected}):
        group=[r for r in selected if r['skill']==skill and r['case']==kind]
        required=2 if kind in ['naturalistic','generalization'] else 1
        passed=sum(r['passed'] for r in group)
        cases.append({'skill':skill,'case':kind,'passed':passed,'attempts':len(group),'required':required,'gatePassed':passed>=required})
    audit=read(ARTIFACTS/'final/audit.json')
    summary={'date':'2026-09-27','baselineCommit':'bd10b36cee91971001c468d70a30f38af3cba15b',
             'modelException':'GPT-5.6 Luna after same-session provider rejection of GPT-5.3 Codex Spark',
             'skillInventory':audit['inventory'],'pageViewportCount':len(audit['pages']),
             'documentOverflowFailures':sum(p.get('overflowX',0)>0 for p in audit['pages']),
             'browserErrors':sum(len(p.get('errors',[])) for p in audit['pages']),
             'brokenImages':sum(len(p.get('brokenImages',[])) for p in audit['pages']),
             'geometryAndInteractions':read(ARTIFACTS/'interactions/report.json'),
             'plantumlMeasurements':read(ARTIFACTS/'plantuml-final-probe/measurements.json'),
             'caseGates':cases,'allCaseGatesPassed':all(c['gatePassed'] for c in cases),
             'selectedRuns':selected,'attemptCount':len(attempts),'attempts':attempts,
             'repositoryChecks':read(ARTIFACTS/'release-checks.json') if (ARTIFACTS/'release-checks.json').exists() else {},
             'publication':{'branch':'main','workflow':'Publish GitHub Pages'}}
    OUT.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'attempts':len(attempts),'selectedPasses':sum(r['passed'] for r in selected),
                      'selectedArtifacts':sum(r.get('artifactPassed',False) for r in selected),
                      'allCaseGatesPassed':summary['allCaseGatesPassed'],'bytes':OUT.stat().st_size}))


if __name__=='__main__':main()
