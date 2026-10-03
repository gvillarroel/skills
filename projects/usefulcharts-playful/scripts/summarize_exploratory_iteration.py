#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect immutable trial evidence and final artifact checks without changing verdicts."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OUT = ROOT / 'artifacts/revision-3'
CASES = ['instruments', 'bsd', 'mars', 'starships', 'civilizations']


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_run(run_id, cohort=None):
    folder = REPO / 'evaluations/runs' / run_id
    manifest = read(folder / 'run-manifest.json')
    events = read(folder / 'event-check.json')
    integrity = read(folder / 'skill-integrity-check.json')
    result = read(folder / 'evaluation-result.json')
    reads = sorted({c['path'] for c in events['calls'] if c.get('tool') == 'read' and c.get('path')})
    item = dict(run_id=run_id, cohort=cohort, command=(folder / 'command.txt').read_text(encoding='utf-8').strip(),
                model=manifest['pi']['model'], payload=manifest['skill'],
                prompt=manifest['prompt'], expected_outputs=manifest['expectedOutputs'],
                strict_pass=result['passed'], gates=result['gates'], findings=events['findings'],
                payload_unchanged=integrity['passed'], read_paths=reads)
    model_errors = []
    for line in (folder / 'events.jsonl').read_text(encoding='utf-8').splitlines():
        event = json.loads(line)
        message = event.get('message', {})
        if event.get('type') == 'message_end' and message.get('errorMessage'):
            model_errors.append(message['errorMessage'])
    item['model_errors'] = sorted(set(model_errors))
    item['failure_classification'] = 'external-provider-usage-limit' if any('usage limit' in e.lower() for e in model_errors) else ('strict-process-error' if not result['passed'] else None)
    if cohort:
        raw = read(folder / 'workspace/review.json')
        inputs = read(folder / 'workspace/input/manifest.json')
        pngs = [name for name in inputs['files'] if name.endswith('.png')]
        item.update(raw_verdicts=raw, input_hashes=inputs['files'],
                    all_input_hashes_match=all(sha(folder / 'workspace/input' / name) == digest for name, digest in inputs['files'].items()),
                    image_read_count=sum('input/' + name in reads for name in pngs),
                    expected_image_count=len(pngs),
                    reviewer_outputs={name: sha(folder / 'workspace' / name) for name in ['review.json', 'review.md']})
        if cohort == 'C':
            inventory = {candidate['id']: candidate for candidate in raw['candidate_inventory']}
            expected = dict(CEDAR='UNIXANDTHEBSDFAMILY', MAPLE='UNIXBSDONEHISTORYMANYBRANCHES')
            identity = set(inventory) == set(expected) and all(
                inventory[ident]['visible_id'] == ident
                and inventory[ident]['whole_path'] == 'input/bsd-' + ident.lower() + '-whole.png'
                and inventory[ident]['detail_path'] == 'input/bsd-' + ident.lower() + '-detail.png'
                and re.sub('[^A-Z]', '', inventory[ident]['main_title'].upper()) == title
                for ident, title in expected.items())
            item.update(mapping=dict(CEDAR='previous-illustrated', MAPLE='repaired-recomposition'),
                        identity_fields_pass=identity, identity_prose_manually_checked=True,
                        raw_source_hashes=inputs['raw_source_hashes'],
                        raw_sources_unchanged=all(sha(folder / 'workspace/input' / name) == digest for name, digest in inputs['raw_source_hashes'].items()),
                        independent_review_findings=[])
            if run_id.endswith('-3'):
                item['independent_review_findings'].append(dict(code='unsupported-comparative-density-wording',
                    detail='The prose says the focused selection cannot match the reference knowledge density, although no matched semantic census exists. Its explicit density status remains pending; the categorical prose is not adopted.'))
            return item
        item['mapping'] = {'instruments': {'A': 'first-recomposition', 'B': 'previous-illustrated'}, 'bsd': {'A': 'previous-illustrated', 'B': 'first-recomposition'}} if cohort == 'A' else {'instruments': {'A': 'previous-illustrated', 'B': 'repaired-recomposition'}, 'bsd': {'A': 'repaired-recomposition', 'B': 'previous-illustrated'}}
        item['independent_review_findings'] = []
        if cohort == 'B' and run_id.endswith(('-1', '-2')):
            item['independent_review_findings'].append(dict(code='candidate-identity-mismatch', subject='bsd',
                detail='The JSON selects B, but describes the continuous connected graph, which is candidate A. Do not silently relabel or count this as a valid preference.'))
        if cohort == 'B' and run_id.endswith('-1'):
            item['independent_review_findings'].append(dict(code='relationship-type-misread', subject='bsd',
                detail='The review describes the FreeBSD 2.0 connection from 4.4BSD Lite as dashed; the source and rendered lineage route are solid.'))
    return item


def main():
    controls = [collect_run('20260913-usefulcharts-exploration-' + tail) for tail in ['control', 'control-b', 'control-final', 'control-identity-final']]
    trials = [collect_run('20260913-usefulcharts-exploration-' + middle + f'luna-{i}', cohort)
              for cohort, middle in [('A', ''), ('B', 'b-')] for i in range(1, 4)]
    identity_trials = [collect_run(f'20260913-usefulcharts-exploration-c-luna-{i}', 'C') for i in range(1, 4)]
    checks = [read(OUT / case / 'verification.json') for case in CASES]
    for check in checks:
        for name, digest in check['hashes'].items():
            assert sha(OUT / check['case'] / name) == digest, (check['case'], name, 'stale verification hash')
    (OUT / 'verification.json').write_text(json.dumps(checks, indent=2) + '\n', encoding='utf-8')
    summary = dict(schema_version=1, date='2026-09-13', skill='usefulcharts-style', status='validating',
        pattern_id='usefulcharts-visible-discovery', final_runtime=controls[-1]['payload'],
        deterministic_tests=dict(exploration=14, illustrated=12),
        controls=controls, review_trials=trials, identity_review_trials=identity_trials, application_checks=checks,
        authored_exploration_assessments=read(OUT / 'exploration-assessments.json'),
        totals=dict(records=sum(c['records'] for c in checks), illustrations=sum(c['illustrations'] for c in checks),
                    pdf_source_links=sum(c['pdf_source_links'] for c in checks), technical_passes=sum(c['status'] == 'pass' for c in checks)),
        evidence_limits=[
            'All visual reviews are development feedback, not a sealed holdout or blinded authorship experiment.',
            'Cohort B has two BSD candidate-identity errors; do not count those as valid preferences or silently repair the raw reviews.',
            'Cohort C resolves identifier binding for this pair in three development runs; it is not a general reliability benchmark. C3 retains overconfident comparative-density prose.',
            'The last default Spark command control stops at the provider usage limit after running fourteen exploration tests; its required output is missing. The prior Spark control passes on the preceding digest.',
            'Cohort B instruments images precede one small root-spine collision repair; they do not hash-match the final instrument PDF.',
            'Only the two supplied subject pairs were independently compared; all five final posters received authored pixel/PDF review.',
            'Record area is compared only to the previous project revision; it is not a matched semantic UsefulCharts density census.',
            'The Mars calendar and civilization matrix still fail the authored exploratory composition gate.',
            'Reference target, sufficient semantic density and indistinguishability are not established.'
        ])
    gallery = OUT / 'gallery-checks.json'
    if gallery.exists():
        summary['gallery_checks'] = read(gallery)
    package = OUT / 'package-checks.json'
    if package.exists():
        summary['package_checks'] = read(package)
    target = REPO / 'evaluations/usefulcharts-style/visible-exploration-20260913.json'
    target.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(totals=summary['totals'], final_runtime=summary['final_runtime'],
        controls=[dict(run=c['run_id'], strict=c['strict_pass']) for c in controls],
        trials=[dict(run=t['run_id'], strict=t['strict_pass'], images=t['image_read_count'],
                     inputs_unchanged=t['all_input_hashes_match'], preferred=[(s['subject'], s['preferred']) for s in t['raw_verdicts']['subjects']],
                     findings=t['independent_review_findings']) for t in trials],
        identity_trials=[dict(run=t['run_id'], strict=t['strict_pass'], identity=t['identity_fields_pass'], images=t['image_read_count'],
                              inputs_unchanged=t['all_input_hashes_match'] and t['raw_sources_unchanged'], preferred=t['raw_verdicts']['preferred_id'],
                              findings=t['independent_review_findings']) for t in identity_trials])))


if __name__ == '__main__':
    main()
