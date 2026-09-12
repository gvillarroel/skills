#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record all caption cohorts without conflating image, provenance and model gates."""

import hashlib
import json
import runpy
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT/'projects/usefulcharts-style/artifacts/reviews/full-branches-v33'
OUTPUT = ROOT/'evaluations/usefulcharts-style/branch-captions-and-luna-summary-20260912.json'
GALLERY = ROOT/'skills/usefulcharts-style/assets/examples/usefulcharts-style'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def browser_summary(path):
    if not path.exists():
        return dict(status='error', explanation='Independent replay could not produce a report; retain its adjacent log.')
    data = load(path)
    return {key:data.get(key) for key in ('status','canvas','node_count','edge_count','findings','composition_warnings')}


def trials():
    names = []
    for version, models in [('v33',['gpt55','luna']),('v33b',['luna']),('v33c',['luna'])]:
        names.extend(f'usefulcharts-{version}-captions-{model}-{n}-20260912' for model in models for n in (1,2,3))
        names.append(f'usefulcharts-{version}-captions-contract-spark-20260912')
    records = []
    for name in names:
        run = ROOT/'evaluations/runs'/name
        manifest = load(run/'run-manifest.json');trace = load(run/'trace-summary.json')
        events = load(run/'event-check.json');completion = load(run/'evaluation-result.json')
        artifact = load(run/'independent-artifact-v2.json')
        browser = browser_summary(run/'independent-browser-v2.json')
        passed = completion['passed'] and trace['passed'] and artifact['status'] == 'pass' and browser['status'] == 'pass'
        record = dict(id=name,model=manifest['pi'],payload=manifest['skill'],prompt=manifest['prompt'],
                      expected_outputs=manifest['expectedOutputs'],strict_pass=completion['passed'],
                      trace_pass=trace['passed'],complete_pass=passed,duration_seconds=completion['durationSeconds'],
                      read_paths=[item['path'] for item in trace['readPaths']],event_findings=events['findings'],
                      skill_integrity=load(run/'skill-integrity-check.json'),artifact_v2=artifact,browser_v2=browser,
                      final_png_sha256=sha(run/'workspace/result/poster.png'))
        previous = run/'independent-artifact.json'
        if previous.exists():
            record['previous_content_only_contract_status'] = load(previous)['status']
        records.append(record)
    return records


def main():
    runs = trials()
    final = [run for run in runs if run['id'].startswith('usefulcharts-v33c-')]
    assert all(run['complete_pass'] for run in final), 'Do not promote an incomplete final cohort.'
    harness = runpy.run_path(str(ROOT/'scripts/run-pi-skill-eval.py'))
    with tempfile.TemporaryDirectory(prefix='runtime-snapshot-',dir=ART) as folder:
        copied = Path(folder)/'skill'
        harness['copy_skill_only'](ROOT/'skills/usefulcharts-style',copied,'runtime')
        snapshot = harness['snapshot_tree'](copied)
        payload = dict(file_count=len(snapshot),sha256=harness['snapshot_digest'](snapshot))
    assert all(run['payload']['payloadSha256'] == payload['sha256'] for run in final)
    naturalistic = [run for run in runs if 'spark' not in run['id']]
    assert len({run['prompt']['sha256'] for run in naturalistic}) == 1
    initial = [run for run in naturalistic if run['id'].startswith('usefulcharts-v33-')]
    assert len({run['final_png_sha256'] for run in initial}) == 1
    assert all(run['final_png_sha256'] == initial[0]['final_png_sha256'] for run in final if 'spark' not in run['id'])
    groups = {}
    for prefix,model in [('v33','gpt55'),('v33','luna'),('v33b','luna'),('v33c','luna')]:
        members = [run for run in runs if run['id'].startswith(f'usefulcharts-{prefix}-captions-{model}-')]
        groups[prefix+'-'+model] = dict(total=len(members),strict_passes=sum(run['strict_pass'] for run in members),
                                       independent_artifact_passes=sum(run['artifact_v2']['status']=='pass' for run in members),
                                       complete_passes=sum(run['complete_pass'] for run in members))
    tests = load(ART/'tests/summary.json');assert all(item['exit_code'] == 0 for item in tests)
    regression = []
    for path in sorted((ART/'gallery-candidate').iterdir()):
        if path.is_file():
            equal = sha(path) == sha(GALLERY/path.name)
            assert equal, path
            regression.append(dict(file=path.name,sha256=sha(path),identical_to_published_source=equal))
    attempts = []
    notes = [
        ('founded','failed','The baseline does not reserve the optical-family caption.'),
        ('causal','failed','An influence route exceeds the routing budget.'),
        ('founded-reserved','rejected','Complete main graph, but no original insets; long vertical stretches and an unrelated shared run.'),
        ('causal-reserved','rejected','Complete main graph, but no original insets; a wide fan, long influences and an unrelated shared run.'),
        ('founded-geometry','diagnostic','Nodes only. Edges and insets omitted; never an accepted poster.'),
        ('causal-geometry','diagnostic','Nodes only. Edges and insets omitted; never an accepted poster.'),
    ]
    for name,status,note in notes:
        folder=ART/name
        record=dict(id=name,status=status,note=note,files={p.name:sha(p) for p in sorted(folder.iterdir()) if p.is_file()})
        if (folder/'browser.json').exists():record['browser']=browser_summary(folder/'browser.json')
        attempts.append(record)
    report = dict(date='2026-09-12',baseline_commit='08e6f1836a9860881a48f242f4c0d4a1dd6df4e6',
        current_runtime=payload,status='validating; full aesthetic parity is unproven',
        decision='Promote complete caption envelopes, source-field preservation checking and a coupled poster export. Reject both full mural reflows; all eleven published gallery files remain byte-identical.',
        scope='A disclosed 70-record, 97-relation development case with five mandatory captions. All naturalistic prompts are identical across A/B/C. No new-subject generalization, blind attribution, statistical model ranking or sealed holdout claim.',
        model_exception='GPT-5.5 and Luna high were registered for the exploratory image-dependent comparison. Default Spark supplies each exact-command control. Cohorts B/C test observed workflow repairs on Luna only.',
        cohorts=groups,forward_runs=runs,paired_png_sha256=initial[0]['final_png_sha256'],
        grading_revision='The retained v1 content-only reports failed to establish final source/SVG consistency. Version 2 explicitly requires a fresh evaluator browser replay of the delivered source and SVG. All A/B/C outputs were reevaluated; old v1 files and failed B artifacts remain untouched.',
        failures=dict(cohort_a_gpt55='One missing re import in a self-check.',
                      cohort_a_luna='Two runs compare entire source arrays against augmented layout arrays, then repair their checks.',
                      cohort_b_luna='One strict tool failure; two final sources differ from the source rendered. Only one complete pass.',
                      full_mural='Initial caption/routing failures followed by two completed but aesthetically rejected reflows.'),
        tests=dict(total=sum(item['tests'] for item in tests),suites=tests),
        baseline_replay=load(ART/'baseline-replay.json'),attempts=attempts,
        source_regression=regression,
        murals={name:browser_summary(ART/'gallery'/(name+'-browser.json')) for name in ('aurelian-families','atlas-of-inquiry','five-regional-histories')},
        mutation_tests=load(ART/'mutations/mutation-audit.json'),paint_controls=load(ART/'paint-controls/summary.json'),
        gallery=load(ART/'gallery/gallery-audit.json'),comparison=load(ART/'comparison/comparison.json'),
        visual_review='The shared final naturalistic PNG was directly inspected after byte equality across all six A and all three C runs was established. Each final Luna C trace reads its full PNG and a detail. The private comparison, original reference and both rejected full mural variants were inspected. No claim that nine identical PNGs were separately reviewed.',
        remaining_gaps=['Persistent broad families and long influence paths in the medium poster.',
                        'The dense left illustration cluster and repeated ordinary names weaken local hierarchy.',
                        'The full institutional mural, repeated genealogy panels and regional chronology still need composition review beyond this medium-case feature.'])
    receipt = ART/'publication-verification.json'
    if receipt.exists():report['publication']=load(receipt)
    OUTPUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runtime=payload,tests=report['tests']['total'],cohorts=groups,controls=sum('spark' in run['id'] and run['complete_pass'] for run in runs),visual_parity=False)))


if __name__ == '__main__':
    main()
