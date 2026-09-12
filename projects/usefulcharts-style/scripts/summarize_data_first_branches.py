#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain data-first branch experiments and every frozen-payload forward run."""

import hashlib
import json
import re
import runpy
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / 'projects/usefulcharts-style/artifacts/reviews/local-stories-v31'
OUTPUT = ROOT / 'evaluations/usefulcharts-style/data-first-branches-summary-20260912.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prompt_data(folder):
    return json.loads(re.search(r'```json\s*(.*?)\s*```', (folder / 'prompt.md').read_text(encoding='utf-8'), re.S).group(1))


def browser_summary(path):
    data = load(path)
    return {key: data[key] for key in ('status', 'canvas', 'node_count', 'edge_count', 'text_count', 'findings', 'composition_warnings') if key in data}


def recover_early_sources():
    """Recover input content only when it matches the render's recorded digest."""
    source = prompt_data(ROOT / 'evaluations/runs/usefulcharts-v31-publishing-1-20260912')
    source.update(design='editorial', mode='lineage', layout='branches')
    next(node for node in source['nodes'] if node['id'] == 'rail')['label'] = 'Railway News Service'
    recovered = []
    for name in ('publishing-natural', 'publishing-dated', 'publishing-ordered'):
        expected = load(ART / name / 'layout.json')['data_sha256']
        actual = hashlib.sha256(json.dumps(source, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        record = dict(id=name, expected_data_sha256=expected, reconstructed_data_sha256=actual, matched=actual == expected)
        if actual == expected:
            path = ART / name / 'recovered-input.json'
            if path.exists():
                assert load(path) == source
            else:
                path.write_text(json.dumps(source, indent=2) + '\n', encoding='utf-8')
            record['path'] = path.relative_to(ROOT).as_posix()
        recovered.append(record)
    return recovered


def forward_runs():
    records = []
    names = [f'usefulcharts-v31-publishing-{number}-20260912' for number in (1, 2, 3)] + ['usefulcharts-v31-contract-spark-20260912']
    for name in names:
        folder = ROOT / 'evaluations/runs' / name
        manifest = load(folder / 'run-manifest.json')
        result = load(folder / 'evaluation-result.json')
        trace = load(folder / 'trace-summary.json')
        events = load(folder / 'event-check.json')
        independent = browser_summary(folder / 'independent-browser.json')
        if 'contract-spark' in name:
            exact = prompt_data(folder) == load(folder / 'workspace/draft.json')
            contract = dict(status='pass' if exact and independent['status'] == 'pass' and not independent['composition_warnings'] else 'fail',
                            exact_prompt_source=exact, scope='Exact captured JSON and evaluator browser replay; no agent image requirement.')
            (folder / 'independent-artifact.json').write_text(json.dumps(contract, indent=2) + '\n', encoding='utf-8')
        else:
            contract = load(folder / 'independent-artifact.json')
        png = folder / 'workspace/result/poster.png'
        records.append(dict(id=name, model=manifest['pi']['model'], payload=manifest['skill'], prompt=manifest['prompt'],
                            strict_pass=result['passed'], duration_seconds=result['durationSeconds'],
                            expected_outputs=manifest['expectedOutputs'], event_findings=events['findings'],
                            integrity=load(folder / 'skill-integrity-check.json'), trace_pass=trace['passed'],
                            read_surface=trace['readPaths'], artifact_contract=contract, evaluator_browser=independent,
                            final_png_sha256=digest(png), scope='contract-smoke' if 'spark' in name else 'naturalistic-forward; disclosed new-subject development'))
    return records


def attempts():
    descriptions = [
        ('local', 'complete', True, 'Local vertical compaction of the previous 59-record source; large common-origin pocket remains.'),
        ('alternating', 'complete', False, 'Four alternating-axis cycles return the same dimensions and positions as local; SVG retained, no separate PNG review.'),
        ('layered', 'complete', True, 'Measured structural stages reduce width but retain a tall common-origin area.'),
        ('active', 'complete', True, 'Local horizontal-overlap constraints compact 59 records; four crossings and broad quiet fields remain.'),
        ('publishing-natural', 'complete', True, 'Initial causal ordering of 70 records separates unrelated founding centuries too strongly.'),
        ('publishing-dated', 'complete', True, 'Ordinal date bands improve ordering; long spines remain.'),
        ('publishing-ordered', 'complete', True, 'Uses local vertical slack for chronology; painted-width audit exposes an unrelated shared run.'),
        ('publishing-clear', 'layout-failure', False, 'Four-unit run reservation cannot route review-to-pictures. The attempted follow-up audit has no SVG.'),
        ('publishing-protected', 'layout-failure', False, 'Ten-unit future-port stems do not repair the same corridor failure; experimental reservation reverted.'),
        ('publishing-ports', 'layout-failure', False, 'Eighteen-unit future-port stems also fail; experimental reservation reverted.'),
        ('publishing-composed', 'complete', False, 'Full port-pair search completes successfully and retains authored source/report. No separate PNG. It was not cancelled.'),
        ('publishing-local-first', 'complete', True, 'Final local-first composer retains all 70 records and 97 relationships with zero painted-run warnings.'),
        ('medium-final', 'complete', True, 'Final helper on the earlier complete 59-record source retains typography and facts; oversized common-origin area remains.'),
        ('published-separated', 'complete', True, 'Accepted only as a local corridor correction in the existing mural; all node geometry and information unchanged.'),
        ('publishing-final', 'complete', True, 'Post-cohort author correction from Five to Six Centuries; every node, edge and placement is unchanged.')]
    records = []
    for name, status, inspected, critique in descriptions:
        folder = ART / name
        record = dict(id=name, status=status, direct_png_review=inspected, critique=critique,
                      selected_as_gallery_recomposition=False, selected_as_corridor_repair=name == 'published-separated')
        files = [path for path in folder.glob('*') if path.is_file() and path.suffix in ('.py', '.json', '.svg', '.png', '.html')]
        record['files'] = {path.name: dict(bytes=path.stat().st_size, sha256=digest(path)) for path in sorted(files)}
        if (folder / 'layout.json').exists():
            record['layout'] = {key: value for key, value in load(folder / 'layout.json').items() if key != 'resolved_layout'}
        if (folder / 'browser.json').exists():
            record['browser'] = browser_summary(folder / 'browser.json')
        if status == 'layout-failure':
            record['observed_error'] = 'Cannot route relationship review-to-pictures: No clear connector corridor. Separate nodes or increase the page size.'
            record['evidence_limit'] = 'Observed terminal error. No accepted SVG; initial driver did not persist stderr or the transient algorithm version.'
        records.append(record)
    return records


def main():
    recovered = recover_early_sources()
    runs = forward_runs()
    assert all(run['strict_pass'] and run['trace_pass'] and run['artifact_contract']['status'] == 'pass' for run in runs)
    harness = runpy.run_path(str(ROOT / 'scripts/run-pi-skill-eval.py'))
    with tempfile.TemporaryDirectory(prefix='runtime-check-', dir=ART) as temporary:
        copied = Path(temporary) / 'skill'
        harness['copy_skill_only'](ROOT / 'skills/usefulcharts-style', copied, 'runtime')
        snapshot = harness['snapshot_tree'](copied)
        current_payload = dict(file_count=len(snapshot), sha256=harness['snapshot_digest'](snapshot))
    assert current_payload['file_count'] == 97
    assert all(run['payload']['payloadSha256'] == current_payload['sha256'] for run in runs)
    pngs = {run['final_png_sha256'] for run in runs if 'publishing' in run['id']}
    assert len(pngs) == 1
    earlier = load(ART / 'publishing-local-first/source.json')
    corrected = load(ART / 'publishing-final/source.json')
    assert {key: value for key, value in earlier.items() if key != 'title'} == {key: value for key, value in corrected.items() if key != 'title'}
    metrics = [{key: value for key, value in item.items() if key not in ('longest', 'edges', 'overlaps')}
               for item in load(ART / 'published-route-metrics.json')['candidates']]
    record = dict(date='2026-09-12', baseline='2ea5183bb71e6737a74cbac3554d82ea2a10aca0',
                  goal_status='active; visual parity is not established',
                  decision='Promote the data-first composition helper and the reviewed local corridor repair. Reject every new composition as a public gallery replacement.',
                  current_runtime=current_payload, attempts=attempts(), recovered_inputs=recovered, forward_runs=runs,
                  strict_passes=4, strict_total=4, independent_contract_passes=4,
                  naturalistic_passes=3, naturalistic_total=3,
                  image_review=dict(identical_naturalistic_pngs=True, sha256=next(iter(pngs)),
                                    author_review='One shared image was directly inspected after confirming identical SHA-256 values across all three outputs. Every agent read its own final PNG.'),
                  model_exception='GPT-5.5 for three image-dependent naturalistic cases, as recorded before execution. Default Spark for one exact-command control.',
                  case_scope='Original fictional publishing subject with 70 individually authored institutions, 97 typed relationships and all supplied notes. It drove development before the three forward repetitions; no blind, sealed validation or holdout claim.',
                  headline_correction=dict(before=earlier['title'], after=corrected['title'], reason='1428 through 2024 spans approximately six centuries.',
                                           timing='After the frozen cohort; captured prompts and raw Pi outputs retain the original supplied Five title. Current reusable prompts and author display use Six. No runtime change or extra agent repetition.',
                                           invariant='Every node and edge field, including placements, remains identical.'),
                  other_source_correction='Railway News Service became Roadside News Service before Pi, matching the coach illustration. Early natural/dated/ordered prototypes retain Railway.',
                  trace_limitation='All three agents removed temporary builders and data-first drafts despite the guide recommending their retention; complete authored source and captured inputs survive.',
                  comparison=load(ART / 'comparison/comparison.json'),
                  corridor_promotion=load(ART / 'promoted-corridors.json'),
                  before_browser=browser_summary(ART / 'published-institution-browser.json'),
                  final_murals={name: browser_summary(ART / ('final-' + name + '-browser.json')) for name in ('genealogy', 'institution', 'timeline')},
                  route_metrics=metrics, browser_controls=load(ART / 'paint-controls/summary.json'),
                  mutations=load(ART / 'mutations/mutation-audit.json'), gallery=load(ART / 'gallery/gallery-audit.json'),
                  unit_tests=dict(total=158, passed=158, new_branching=6, lineage_runs=6, pi_harness=14),
                  audit_scope='Straight visible institutional path segments and painted widths in the generated poster coordinate space. Shared endpoints are exempt; arbitrary transformed stroke widths and every curved coincidence are not comprehensively covered.',
                  remaining_gaps=['Upper-right whitespace and a long isolated education spine in the 70-record publishing case.',
                                  'A large common-origin pocket remains in the 59-record case despite dimensional compaction.',
                                  'The 141-record mural still uses persistent large regions and repeated captions with limited illustration variety.',
                                  'The previously documented genealogy and chronology composition gaps remain.'])
    OUTPUT.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(summary=str(OUTPUT), attempts=len(record['attempts']), strict_passes=4, independent_contracts=4,
                          runtime=current_payload, recovered_inputs=sum(item['matched'] for item in recovered), visual_parity=False)))


if __name__ == '__main__':
    main()
