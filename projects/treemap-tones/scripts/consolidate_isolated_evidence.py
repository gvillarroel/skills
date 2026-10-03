#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain all isolated treemap/overlap attempts and diagnostic-only repairs."""

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'evaluations/d3'
OLD = [
    ('d3-treemap-tones-contract-20261003-luna-1','contract-1','superseded',
     'Agent omitted active palette metadata at its first check and attempted an exact SVG replacement with stale oldText. The final artifact passes independently; strict release acceptance fails.'),
    ('d3-treemap-tones-naturalistic-20261003-luna-1',None,'unfinalized-infrastructure',
     'The environment update interrupted the run and no evaluation-result.json or live runner remained. Its payload was superseded by added overlap steering. No pass is claimed.'),
    ('d3-treemap-tones-contract-20261003-luna-2','contract-2','superseded',
     'Agent omitted active palette metadata at its first check; actual labels violate exact maximum-contrast black/white, and Operations area fractions diverge by 0.0734. Both strict and artifact gates fail.'),
    ('d3-treemap-tones-naturalistic-20261003-luna-2','naturalistic-2','superseded',
     'Agent used #fff shorthand and omitted active metadata, guessed a missing ID, and issued unsuccessful edit/substring probes. Actual light-gray leaf labels violate maximum-contrast black/white; the portable SVG additionally gets Intake wrong.'),
    ('d3-treemap-tones-naturalistic-20261003-luna-3','naturalistic-3','superseded',
     'Agent used #fff shorthand and omitted active metadata. Its custom no-network assertion incorrectly rejects the required SVG xmlns URI as an external dependency. Actual light-gray labels violate maximum-contrast black/white.'),
]


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def collect(run_id, grade_directory, status, note):
    run = ROOT / 'evaluations/runs' / run_id
    manifest = read_json(run/'run-manifest.json')
    result = read_json(run/'evaluation-result.json')
    events = read_json(run/'event-check.json')
    artifacts = read_json(run/'artifact-check.json')
    integrity = read_json(run/'skill-integrity-check.json')
    grade_path = ROOT / 'projects/treemap-tones/artifacts/isolated' / grade_directory / 'independent-grade.json' if grade_directory else None
    grade = read_json(grade_path) if grade_path else None
    paths = ['run-manifest.json','evaluation-result.json','event-check.json','artifact-check.json','skill-integrity-check.json','events.jsonl']
    return {'runId':run_id,'status':status,'classification': 'infrastructure' if status == 'unfinalized-infrastructure' else ('agent' if result and not result['passed'] else None),
            'note':note,'model':manifest['pi'] if manifest else None,'payload':manifest['skill'] if manifest else None,
            'harnessPassed':result['passed'] if result else False,'evaluationFinalized':result is not None,
            'durationSeconds':result.get('durationSeconds') if result else None,'gates':result.get('gates') if result else None,
            'expectedArtifacts':artifacts.get('outputs',[]) if artifacts else [],
            'eventFindings':events.get('findings',[]) if events else [],
            'failedCalls':[call for call in events.get('calls',[]) if call['isError']] if events else [],
            'readSurface':[call['path'] for call in events.get('calls',[]) if call['tool']=='read'] if events else [],
            'skillIntegrityPassed':integrity.get('passed') if integrity else None,
            'independentlyPassed':grade.get('passed') if grade else None,
            'independentGrade':grade_path.relative_to(ROOT).as_posix() if grade_path else None,
            'independentGradeSha256':digest(grade_path) if grade_path else None,
            'independentFindings':grade.get('findings') if grade else None,
            'evidenceSha256':{name:digest(run/name) for name in paths if (run/name).is_file()}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['builder-pending','complete'],default='builder-pending')
    parser.add_argument('--final-run',action='append',default=[],help='RUN_ID::GRADE_DIRECTORY')
    parser.add_argument('--final-payload')
    args=parser.parse_args()
    attempts=[collect(*row) for row in OLD]
    final=[]
    for entry in args.final_run:
        run_id,grade_directory=entry.split('::',1)
        record=collect(run_id,grade_directory,'current','Final deterministic-route cohort; generated outputs are not repaired outside the trace.')
        attempts.append(record);final.append(record)
    diagnostic_path=ROOT/'projects/treemap-tones/artifacts/diagnostic/naturalistic-2/independent-grade.json'
    diagnostic_grade=read_json(diagnostic_path)
    original_artifacts=read_json(ROOT/'evaluations/runs/d3-treemap-tones-naturalistic-20261003-luna-2/artifact-check.json')
    original_workspace=ROOT/'evaluations/runs/d3-treemap-tones-naturalistic-20261003-luna-2/workspace'
    original_unchanged=all(digest(original_workspace/item['path'])==item['sha256'] for item in original_artifacts['outputs'])
    diagnostic={'acceptedAsRunPass':False,'purpose':'Determine whether the existing mandatory finalizer corrects the agent omission on a copied artifact.',
                'originalArtifactsUnchanged':original_unchanged,'gradePassed':diagnostic_grade.get('passed') if diagnostic_grade else None,
                'gradeSha256':digest(diagnostic_path),
                'commands':[
                    'uv run --script skills/d3/scripts/colorset_adapter.py evaluations/runs/d3-treemap-tones-naturalistic-20261003-luna-2/workspace/portfolio-treemap.html projects/treemap-tones/artifacts/diagnostic/naturalistic-2/portfolio-treemap.html --colorset colorset1',
                    'uv run --script skills/d3/scripts/render_d3_svg.py projects/treemap-tones/artifacts/diagnostic/naturalistic-2/portfolio-treemap.html --output projects/treemap-tones/artifacts/diagnostic/naturalistic-2/portfolio-treemap.svg --screenshot projects/treemap-tones/artifacts/diagnostic/naturalistic-2/normalized-960.png --viewport 960x720 --wait-ms 1200',
                    'python skills/d3/scripts/check_palette_contract.py projects/treemap-tones/artifacts/diagnostic/naturalistic-2/portfolio-treemap.html --colorset colorset1',
                    'uv run --script projects/treemap-tones/scripts/inspect_isolated_artifact.py projects/treemap-tones/artifacts/diagnostic/naturalistic-2 --output projects/treemap-tones/artifacts/diagnostic/naturalistic-2/review',
                    'uv run --script projects/treemap-tones/scripts/grade_isolated_artifact.py projects/treemap-tones/artifacts/diagnostic/naturalistic-2/review/render-review.json --case naturalistic --output projects/treemap-tones/artifacts/diagnostic/naturalistic-2/independent-grade.json'],
                'result':'The finalizer repairs active palette metadata, shorthand paint and maximum-contrast labels; a fresh export from that normalized HTML passes all four independent states. This proves the corrective operation, not the failed Pi run.'}
    joint=lambda row:row['harnessPassed'] and row['independentlyPassed']
    natural=[row for row in final if '-naturalistic-' in row['runId']]
    treemap_contract=[row for row in final if '-treemap-tones-contract-' in row['runId']]
    overlap_contract=[row for row in final if '-dense-overlap-contract-' in row['runId']]
    current_ok=(len(natural)==3 and sum(bool(joint(row)) for row in natural)>=2
                and any(joint(row) for row in treemap_contract) and any(joint(row) for row in overlap_contract)
                and all(row['payload']['payloadSha256']==args.final_payload for row in final))
    report={'schemaVersion':1,'date':'2026-10-03','skill':'d3','phase':args.phase,'passed':args.phase=='complete' and current_ok,
            'finalPayloadSha256':args.final_payload,'modelException':'openai-codex/gpt-5.6-luna, as recorded in the D3 backlog because Spark was unsupported.',
            'settingsNote':'Retained pre-steering high cases are separate. The combined frozen paint revision uses Luna medium consistently; strict and artifact gates are unchanged, and no direct model-quality comparison is claimed.',
            'casePolicy':'A passing contract smoke for each changed form and exactly three fresh naturalistic repetitions on the final payload; require at least two joint strict/artifact naturalistic passes. Every failed/superseded attempt remains recorded.',
            'attempts':attempts,'diagnosticFinalizer':diagnostic,
            'evaluatorCorrections':['Separate adjacent text tspan lines when reading visible name/value tokens.',
                                    'Enforce responsive viewport overflow on HTML; portable SVG retains intrinsic export dimensions.',
                                    'Use viewport screenshots for native SVG after a full-page screenshot timeout; this is an evaluator capture correction.']}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'treemap-tones-isolated-20261003.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# D3 Treemap and Dense Overlap Isolated Validation','',
           'Date: 2026-10-03. Model exception: `openai-codex/gpt-5.6-luna`, recorded in the D3 backlog because Spark was unsupported. All finalized runs use JSON strict mode, the runtime profile, exact non-empty output expectations, prompt-first/observed-model/read-surface checks, zero tool-error acceptance, and unchanged copied skill payloads.','',
           f'Current phase: **{args.phase}**. The final deterministic-builder cohort is pending until the source is frozen.' if args.phase!='complete' else f'Final payload: `{args.final_payload}`. Final cohort acceptance: **{"PASS" if report["passed"] else "FAIL"}**.','',
           'The initial treemap freeze used 288 runtime files with digest `fec0c61e4ff3ad2a4ffc4a0fec4444040f5be94d07767e45bc93bc24a253ca30`. Added dense-overlap steering produced the second 288-file digest `fd964189150e248e286954dc1b3019473980a2c47c2efe178a4d891241d39195`. Repeated agent omissions of mandatory finalization and incorrect exact black/white text motivated the compact deterministic standalone treemap route. These old-payload attempts are retained and cannot certify the later release payload.','',
           '| Attempt | Thinking | Strict | Independent artifacts | Status |',
           '| --- | --- | --- | --- | --- |']
    for row in attempts:
        strict='PASS' if row['harnessPassed'] else ('FAIL' if row['evaluationFinalized'] else 'Unfinalized')
        independent='PASS' if row['independentlyPassed'] else ('FAIL' if row['independentlyPassed'] is False else 'Not accepted')
        lines.append(f"| `{row['runId']}` | {row['model']['thinking'] if row['model'] else 'unknown'} | {strict} | {independent} | {row['status']} |")
    lines.extend(['','## Retained Failure Classification',''])
    for row in attempts:
        if not row['harnessPassed']:
            lines.append(f"- `{row['runId']}`: {row['note']}")
    lines.extend(['','## Diagnostic Finalization','',
                  'The existing colorset adapter was applied only to a separate diagnostic copy of naturalistic attempt 2, followed by a fresh SVG export. The original exact-output hashes remain unchanged. The diagnostic copy passes the active-palette check and independent HTML/SVG rendering at 960 and 420 pixels, including exact maximum-contrast black/white labels. **This diagnostic copy is not a Pi pass and does not repair the failed run.** The independent metadata/BW proof is retained under `projects/treemap-tones/artifacts/diagnostic/naturalistic-2/`. Incorrect quantitative geometry, such as contract attempt 2, still requires truthful D3 construction.','',
                  'The original input and normalized-copy commands, all manifest/event/artifact/grade hashes, complete tool errors, read lists and payload digests are in [the machine record](treemap-tones-isolated-20261003.json). Raw workspaces and JSONL traces remain under `evaluations/runs/`.','',
                  '## Independent Review','',
                  'The evaluator captures actual rendered fill, stroke, effective ancestor opacity, text and rectangles for HTML and portable SVG at 960/420 pixels. It checks exact branch/leaf names and values, three distinct opaque solid sibling tones, contained labels, proportional leaf areas, borderless cells, maximum-contrast black/white paint and HTML/SVG color parity. A local 1.15:1 minimum step between sorted sibling luminances is a distinguishability check, not a WCAG claim. Direct screenshot review remains part of acceptance.','',
                  'The capture initially treated adjacent tspan lines as concatenated tokens and incorrectly applied HTML responsive overflow to an intrinsic-width SVG export; those evaluator findings were corrected before judging artifacts. A native SVG full-page screenshot timeout was resolved with viewport capture without changing generated artifacts.','',
                  'Dense overlap uses the independent source-over inspector from `projects/task-overlap-transparency/scripts/verify_overlap.py`, bound to the retained original geometry manifest. Its standalone wrapper checks nine semantic-alpha regions, 100 task dots/labels/leaders, original positions and memberships, opaque borderless label faces, maximum BW text over actual composited backing, clear single/double/triple overlap pixel samples, two Replay states and reduced motion.','',
                  'Final runs use the original unmodified task prompts. Medium thinking is a scoped runtime choice for this narrow painting revision; model, isolation, strict trace and independent rendered acceptance requirements are unchanged.',''])
    (OUT/'treemap-tones-isolated-20261003.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'phase':report['phase'],'passed':report['passed'],'attempts':len(attempts),'originalDiagnosticInputsUnchanged':original_unchanged}))


if __name__=='__main__':
    main()
