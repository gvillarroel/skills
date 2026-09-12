#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize the emblem revision, both frozen cohorts and retained composition attempts."""

import hashlib
import json
import runpy
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
ART=ROOT/'projects/usefulcharts-style/artifacts/reviews/semantic-emblems-v32'
OUTPUT=ROOT/'evaluations/usefulcharts-style/context-and-emblems-summary-20260912.json'


def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def browser_summary(path):
    data=load(path)
    return {key:data[key] for key in ('status','canvas','node_count','edge_count','text_count','findings','composition_warnings')}


def trials():
    records=[]
    for version in ('v32','v32b'):
        names=[f'usefulcharts-{version}-context-{n}-20260912' for n in (1,2,3)]+[f'usefulcharts-{version}-contract-spark-20260912']
        for name in names:
            run=ROOT/'evaluations/runs'/name
            manifest=load(run/'run-manifest.json');trace=load(run/'trace-summary.json');events=load(run/'event-check.json')
            data=load(run/'workspace/result/source.json')
            checked=load(run/'independent-artifact.json');completion=load(run/'evaluation-result.json')
            commands=[call['command'] for call in events['calls'] if call['tool']=='bash']
            records.append(dict(id=name,model=manifest['pi'],payload=manifest['skill'],prompt=manifest['prompt'],
                                expected_outputs=manifest['expectedOutputs'],strict_pass=completion['passed'],
                                duration_seconds=completion['durationSeconds'],trace_pass=trace['passed'],
                                read_surface=trace['readPaths'],event_findings=events['findings'],
                                skill_integrity=load(run/'skill-integrity-check.json'),artifact_contract=checked,
                                browser=browser_summary(run/'independent-browser.json'),
                                inset_boxes=[dict(id=item['id'],kind=item['kind'],box=item['box'],columns=item.get('columns')) for item in data['insets']],
                                fit_pockets_used=any('--fit-pockets' in command for command in commands),
                                browser_detail_used=any('--detail-box' in command for command in commands),
                                final_png_sha256=sha(run/'workspace/result/poster.png'),
                                author_full_png_review=version=='v32b' and 'spark' not in name,
                                classification=('agent: assumed optional image tooling; skill: inset-placement workflow needed bounded fitting' if not completion['passed'] else None)))
    return records


def attempts():
    cases=[('publishing-context','complete','Custom project prototype of the contextual opening.',True),
           ('publishing-education','layout-failure','Textbooks and research lack a five-unit gutter.',False),
           ('publishing-education-gutter','layout-failure','The same neighboring records still lack a gutter after the first shift.',False),
           ('publishing-education-clear','layout-failure','Children and language records lack a gutter.',False),
           ('publishing-education-spacing','layout-failure','Scientific Index and Learning Media collide.',False),
           ('publishing-education-group','complete','Eleven education records repositioned as one local history; both mergers are clearer.',True),
           ('native-context','layout-failure','Native count layout requires 230.7 units of height; supplied box had 228.',False),
           ('native-context-sized','complete','Native contextual insets, enlarged count box; no separate final author image review.',False),
           ('native-context-frozen','complete','Native composer freezes routes around source-backed insets.',True),
           ('contract-check','complete','Fourteen independent fictional collections; a technical control, not an aesthetic target.',True)]
    result=[]
    for name,status,note,reviewed in cases:
        folder=ART/name
        item=dict(id=name,status=status,note=note,author_png_review=reviewed,
                  files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file() and p.suffix in ('.json','.py','.svg','.html','.png')})
        if (folder/'browser.json').exists():item['browser']=browser_summary(folder/'browser.json')
        result.append(item)
    return result


def main():
    runs=trials();final=[run for run in runs if run['id'].startswith('usefulcharts-v32b-')]
    assert all(run['strict_pass'] and run['trace_pass'] and run['artifact_contract']['status']=='pass' for run in final)
    harness=runpy.run_path(str(ROOT/'scripts/run-pi-skill-eval.py'))
    with tempfile.TemporaryDirectory(prefix='runtime-snapshot-',dir=ART) as folder:
        copied=Path(folder)/'skill';harness['copy_skill_only'](ROOT/'skills/usefulcharts-style',copied,'runtime')
        snapshot=harness['snapshot_tree'](copied)
        payload=dict(file_count=len(snapshot),sha256=harness['snapshot_digest'](snapshot))
    assert all(run['payload']['payloadSha256']==payload['sha256'] for run in final)
    old=load(ROOT/'projects/usefulcharts-style/artifacts/reviews/local-stories-v31/publishing-final/source.json')
    new=load(ART/'native-context-frozen/source.json')
    records=lambda data,omit:{n['id']:{k:v for k,v in n.items() if k not in omit} for n in data['nodes']}
    assert records(old,{'x','y'})==records(new,{'x','y'})
    old_nodes={n['id']:n for n in old['nodes']}
    moved=[n['id'] for n in new['nodes'] if (n['x'],n['y'])!=(old_nodes[n['id']]['x'],old_nodes[n['id']]['y'])]
    typed=lambda data:{e['id']:(e['source'],e['target'],e['kind']) for e in data['edges']}
    assert typed(old)==typed(new)
    assert old['groups']==new['groups']
    tests=load(ART/'tests/summary.json');assert all(test['exit_code']==0 for test in tests)
    comparison=load(ART/'comparison/comparison.json')
    for item in comparison['families']:
        path=ROOT/'skills/usefulcharts-style/assets/examples/usefulcharts-style'/(item['id']+'.svg')
        assert sha(path)==item['new_svg_sha256']
    mural=load(ART/'gallery-candidate/atlas-of-inquiry.json')
    changed={'star','sun','astrolabe','orbit','wheel','lens','anchor','tower'}
    changed_illustrations=[n['id'] for n in mural['nodes'] if n.get('icon') in changed]
    report=dict(date='2026-09-12',baseline_commit='3b524e6320914e52deb137347c8a02c8cc9306a5',
                goal_status='active; visual parity is not established',current_runtime=payload,
                decision='Promote distinct semantic emblems, source-backed context insets, bounded pocket fitting and browser detail capture. Publish the reviewed emblem change in the existing institutional mural.',
                scope='Development/refinement of a disclosed authored layout. Positions and typography are supplied to the agent. No new data-first generalization, blind judgment or sealed holdout claim.',
                emblem_comparison=load(ART/'emblems-first/comparison.json'),changed_mural_illustrations=changed_illustrations,
                original_composition=dict(node_count=70,typed_edges=97,moved_nodes=moved,node_fields_except_xy_unchanged=True,
                                          typed_relations_unchanged=True,category_colors_unchanged=True,source='native-context-frozen/source.json',
                                          final_png_sha256=sha(ART/'native-context-frozen/poster.png')),
                attempts=attempts(),forward_runs=runs,
                cohort_a=dict(naturalistic_strict_passes=0,naturalistic_total=3,command_control_passes=1,independent_artifact_passes=4),
                cohort_b=dict(naturalistic_strict_passes=3,naturalistic_total=3,command_control_passes=1,independent_artifact_passes=4),
                model_exception='GPT-5.5 for image-dependent naturalistic runs; Spark for command controls. Recorded before each cohort.',
                visual_review='All three distinct final cohort-B whole-page PNGs, the author-composed context poster, fourteen-symbol table, three candidate murals and official references were directly inspected.',
                development_failures=['First inset browser mutations serialized an XML prefix that HTML parsing did not treat as SVG; tests corrected before cohort A.',
                                      'First bounded fitting test exposed an obstructed connection attachment; fitter now reserves those regions, before cohort B.',
                                      'Auxiliary quick_validate initially lacked PyYAML; rerun with an explicit uv dependency passed.'],
                tests=dict(total=sum(test['tests'] for test in tests),suites=tests,new_emblem_tests=3,new_context_tests=14),
                mutation_tests=load(ART/'mutations/mutation-audit.json'),paint_controls=load(ART/'paint-controls/summary.json'),
                gallery=load(ART/'gallery/gallery-audit.json'),comparison=comparison,
                final_murals={name:browser_summary(ART/'gallery-audits'/(name+'.json')) for name in ('atlas-of-inquiry','aurelian-families','five-regional-histories')},
                remaining_gaps=['Persistent large institutional families and limited intermediate hierarchy in the 141-record mural.',
                                'Many long dotted influence paths remain in the 70-record case despite its improved opening and education group.',
                                'Genealogical repeated nameplate rhythm and chronologically regular regional treatments remain unchanged by this revision.'])
    OUTPUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runtime=payload,tests=report['tests']['total'],cohort_a=report['cohort_a'],cohort_b=report['cohort_b'],
                          changed_mural_illustrations=len(changed_illustrations),moved_nodes=moved,visual_parity=False)))


if __name__=='__main__':main()
