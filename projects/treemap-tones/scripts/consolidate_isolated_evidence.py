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
    ('d3-treemap-tones-contract-20261003-luna-3','contract-3','superseded',
     'The first deterministic-builder payload passes strict and seven independently rendered states. A later dense-overlap builder changes the complete runtime payload, so this retained pass cannot certify that later digest.'),
    ('d3-treemap-tones-naturalistic-20261003-luna-4','naturalistic-4','superseded',
     'The first deterministic-builder payload passes strict and seven independently rendered states; retained as part of its exactly three-run naturalistic cohort.'),
    ('d3-treemap-tones-naturalistic-20261003-luna-5','naturalistic-5','superseded',
     'Agent required d3-treemap-cs1 pattern metadata as the SVG DOM id, although the builder root id is treemap. Actual artifacts pass all seven independent states; the single failed guessed-ID check rejects strict acceptance.'),
    ('d3-treemap-tones-naturalistic-20261003-luna-6','naturalistic-6','superseded',
     'The first deterministic-builder payload passes strict and seven independently rendered states; its naturalistic cohort has exactly two joint passes from three fresh runs.'),
    ('d3-dense-overlap-contract-20261003-luna-1','overlap-contract-1','superseded',
     'Agent omitted --force when replacing an existing finalized HTML, causing a strict tool error. Native HTML passes four painted-radius states, but CSS/Web Animation radii leave the exported SVG at r=0 for nine regions and 100 dots; both portable SVG states fail. Originals remain untouched.'),
    ('d3-dense-overlap-contract-20261003-luna-2','overlap-contract-2','superseded',
     'Agent first omitted SVG desc, attempted a stale exact edit and again omitted --force on an existing final HTML. Actual geometry, semantic alpha, maximum BW and sampled pixels pass, but its inherited 16px footer overlaps T094, T095 and T100 in every HTML/SVG state. Strict and independently rendered acceptance both fail; no artifact repair is accepted.'),
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
    prompt_path=Path(manifest['prompt']['source']).relative_to(ROOT).as_posix() if manifest else None
    command=(f"uv run --script scripts/run-pi-skill-eval.py d3 --prompt-file {prompt_path} "
             f"--model {manifest['pi']['model']} --thinking {manifest['pi']['thinking']} --mode json --strict --profile runtime "
             f"--run-id {run_id} --timeout-seconds {manifest['pi']['timeoutSeconds']} "
             + ' '.join(f'--expect-output {path}' for path in manifest['expectedOutputs'])) if manifest else None
    review_dir=f'projects/treemap-tones/artifacts/isolated/{grade_directory}' if grade_directory else None
    validator_commands=[]
    if review_dir:
        if '-dense-overlap-' in run_id:
            validator_commands=[f'uv run --script projects/treemap-tones/scripts/inspect_overlap_isolated.py evaluations/runs/{run_id}/workspace --output {review_dir}']
        else:
            case='contract' if '-contract-' in run_id else 'naturalistic'
            basename='contract-treemap' if case=='contract' else 'portfolio-treemap'
            replay=' --replay' if grade and len(grade.get('states',[]))==7 else ''
            validator_commands=[
                f'uv run --script projects/treemap-tones/scripts/inspect_isolated_artifact.py evaluations/runs/{run_id}/workspace --output {review_dir} --basename {basename}{replay}',
                f'uv run --script projects/treemap-tones/scripts/grade_isolated_artifact.py {review_dir}/render-review.json --case {case} --output {review_dir}/independent-grade.json']
    states=grade.get('states',[]) if grade else []
    contrasts=[label['contrast'] for state in states for label in state.get('labels',[])]
    contrasts.extend(leaf['textContrast'] for state in states for branch in state.get('branches',{}).values() for leaf in branch.get('leaves',[]))
    samples=[sample for state in states for sample in state.get('samples',[])]
    return {'runId':run_id,'status':status,'classification': 'infrastructure' if status == 'unfinalized-infrastructure' else ('agent' if result and not result['passed'] else None),
            'note':note,'model':manifest['pi'] if manifest else None,'payload':manifest['skill'] if manifest else None,
            'harnessCommand':command,'prompt':manifest['prompt'] if manifest else None,
            'harnessPassed':result['passed'] if result else False,'evaluationFinalized':result is not None,
            'durationSeconds':result.get('durationSeconds') if result else None,'gates':result.get('gates') if result else None,
            'expectedArtifacts':artifacts.get('outputs',[]) if artifacts else [],
            'artifactsUnchanged':bool(artifacts) and all(digest(run/'workspace'/item['path'])==item['sha256'] for item in artifacts['outputs']),
            'eventFindings':events.get('findings',[]) if events else [],
            'failedCalls':[call for call in events.get('calls',[]) if call['isError']] if events else [],
            'readSurface':[call['path'] for call in events.get('calls',[]) if call['tool']=='read'] if events else [],
            'skillIntegrityPassed':integrity.get('passed') if integrity else None,
            'independentlyPassed':grade.get('passed') if grade else None,
            'independentGrade':grade_path.relative_to(ROOT).as_posix() if grade_path else None,
            'independentGradeSha256':digest(grade_path) if grade_path else None,
            'independentValidatorCommands':validator_commands,
            'independentFindings':(grade.get('findings') or sorted({finding for state in grade.get('states',[]) for finding in state.get('findings',[])})) if grade else None,
            'representativeCaptionCollisions':grade.get('states',[{}])[0].get('captionLabelCollisions',[]) if grade and grade.get('states') else [],
            'minimumMeasuredTextContrast':min(contrasts) if contrasts else None,
            'compositingPixelSampleCount':len(samples),
            'maximumCompositingChannelError':max(sample.get('maximumChannelError',0) for sample in samples) if samples else None,
            'captionLabelCollisionCount':sum(len(state.get('captionLabelCollisions',[])) for state in states),
            'independentStateCount':len(grade.get('states',[])) if grade else None,
            'independentStateFindingCounts':[len(state.get('findings',[])) for state in grade.get('states',[])] if grade else [],
            'evidenceSha256':{name:digest(run/name) for name in paths if (run/name).is_file()}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['builder-pending','final-cohort-running','complete'],default='builder-pending')
    parser.add_argument('--final-run',action='append',default=[],help='RUN_ID::GRADE_DIRECTORY')
    parser.add_argument('--final-payload')
    parser.add_argument('--manual-review',action='append',default=[],help='Run ID with completed direct screenshot review.')
    args=parser.parse_args()
    attempts=[collect(*row) for row in OLD]
    for record in attempts:
        record['manualRenderReviewed']=record['runId'] in args.manual_review
    final=[]
    for entry in args.final_run:
        run_id,grade_directory=entry.split('::',1)
        note=('Agent imposed an unrequested parent/children interleaving order with --ordered-text although the builder emits parent headers and then leaves. Required names, values, true geometry, tonal paint and all seven independent rendered states pass; the invented ordering assertion rejects strict acceptance.'
              if run_id=='d3-treemap-tones-contract-20261003-luna-4'
              else 'Agent imposed a guessed fixed viewBox of 0 0 960 540 on a responsive export. The task and builder do not promise those dimensions; all seven independent rendered states and direct narrow review pass, but the unnecessary fixed-size assertion rejects strict acceptance.'
              if run_id=='d3-treemap-tones-naturalistic-20261003-luna-7'
              else 'Agent imposed a rounded fixed viewBox of 0 0 880 490 on the portable export, then repeated the same false requirement with lower-case attribute spelling. Actual export is 0 0 880 489.85; all six independent rendered states and direct SVG review pass. Both unnecessary dimension assertions remain strict tool errors.'
              if run_id=='d3-dense-overlap-contract-20261003-luna-3'
              else 'Final deterministic-route cohort; generated outputs are not repaired outside the trace.')
        record=collect(run_id,grade_directory,'current',note)
        record['manualRenderReviewed']=run_id in args.manual_review
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
    joint=lambda row:row['harnessPassed'] and row['independentlyPassed'] and row['artifactsUnchanged'] and row['manualRenderReviewed']
    natural=[row for row in final if '-naturalistic-' in row['runId']]
    treemap_contract=[row for row in final if '-treemap-tones-contract-' in row['runId']]
    overlap_contract=[row for row in final if '-dense-overlap-contract-' in row['runId']]
    current_ok=(len(natural)==3 and sum(bool(joint(row)) for row in natural)>=2
                and any(joint(row) for row in treemap_contract) and any(joint(row) for row in overlap_contract)
                and all(row['payload']['payloadSha256']==args.final_payload for row in final))
    report={'schemaVersion':1,'date':'2026-10-03','skill':'d3','phase':args.phase,'passed':args.phase=='complete' and current_ok,
            'finalPayloadSha256':args.final_payload,'modelException':'openai-codex/gpt-5.6-luna, as recorded in the D3 backlog because Spark was unsupported.',
            'releaseSelection':{'naturalisticCohort':[row['runId'] for row in natural],
                                'jointNaturalisticPassCount':sum(bool(joint(row)) for row in natural),
                                'jointTreemapContractPasses':[row['runId'] for row in treemap_contract if joint(row)],
                                'jointOverlapContractPasses':[row['runId'] for row in overlap_contract if joint(row)],
                                'currentCohortPayloadsAgree':bool(final) and all(row['payload']['payloadSha256']==args.final_payload for row in final),
                                'retainedAttemptCount':len(attempts)},
            'settingsNote':'Retained pre-steering high cases are separate. The combined frozen paint revision uses Luna medium consistently; strict and artifact gates are unchanged, and no direct model-quality comparison is claimed.',
            'casePolicy':'A passing contract smoke for each changed form and exactly three fresh naturalistic repetitions on the final payload; require at least two joint strict/artifact naturalistic passes. Every failed/superseded attempt remains recorded.',
            'attempts':attempts,'diagnosticFinalizer':diagnostic,
            'evaluatorCorrections':['Separate adjacent text tspan lines when reading visible name/value tokens.',
                                    'Enforce responsive viewport overflow on HTML; portable SVG retains intrinsic export dimensions.',
                                    'Use viewport screenshots for native SVG after a full-page screenshot timeout; this is an evaluator capture correction.',
                                    'Measure actual painted circle radius with getBBox for CSS/SMIL animations rather than only the underlying r attribute; unmaterialized zero-radius exports still fail.',
                                    'Record rendered caption/task-label intersections after direct inspection found an oversized footer; preserve original artifacts.']}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'treemap-tones-isolated-20261003.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    selected_treemap=', '.join('`'+row['runId']+'`' for row in treemap_contract if joint(row)) or 'pending'
    selected_overlap=', '.join('`'+row['runId']+'`' for row in overlap_contract if joint(row)) or 'pending'
    selected_natural=', '.join('`'+row['runId']+'`' for row in natural) or 'pending'
    passing_states=sum(row['independentStateCount'] or 0 for row in final if row['independentlyPassed'])
    lines=['# D3 Treemap and Dense Overlap Isolated Validation','',
           'Date: 2026-10-03. Model exception: `openai-codex/gpt-5.6-luna`, recorded in the D3 backlog because Spark was unsupported. All finalized runs use JSON strict mode, the runtime profile, exact non-empty output expectations, prompt-first/observed-model/read-surface checks, zero tool-error acceptance, and unchanged copied skill payloads.','',
           (f'Current phase: **{args.phase}**. The final deterministic-builder cohort is pending until the source is frozen.' if args.phase=='builder-pending' else f'Current phase: **{args.phase}**. Final payload: `{args.final_payload}`. The serialized release cohort is in progress.') if args.phase!='complete' else f'Final payload: `{args.final_payload}`. Final cohort acceptance: **{"PASS" if report["passed"] else "FAIL"}**.','',
           'The initial treemap freeze used 288 runtime files with digest `fec0c61e4ff3ad2a4ffc4a0fec4444040f5be94d07767e45bc93bc24a253ca30`. Added dense-overlap steering produced the second 288-file digest `fd964189150e248e286954dc1b3019473980a2c47c2efe178a4d891241d39195`. Repeated agent omissions of mandatory finalization and incorrect exact black/white text motivated the compact deterministic standalone treemap route. These old-payload attempts are retained and cannot certify the later release payload.','',
           'The first deterministic treemap builder produced 289 runtime files with digest `869500828be9b356d53b9603c2aac23597f24562832e9fc77c758bdbf42de869`. Its treemap contract passed, all 28 rendered states passed, and exactly two of three fresh naturalistic runs passed jointly; the third had an invented SVG-ID check error. Two subsequent dense-overlap contracts failed strict and rendered acceptance. The complete payload is superseded by a deterministic dense-overlap builder; the earlier accepted treemap cohort remains evidence but is not counted toward a later digest.','',
           f'The final runtime contains 290 files. Its selected treemap contracts are {selected_treemap}; selected dense-overlap contracts are {selected_overlap}. The fresh naturalistic denominator is exactly {selected_natural}: {sum(bool(joint(row)) for row in natural)}/{len(natural)} pass jointly. Independent artifact grades pass in {passing_states} current rendered states. Invented ordering or rounded-dimension assertions remain strict failures and are not promoted by a passing artifact review.','',
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
                  'The standalone overlap evaluator measures each circle\'s actually painted local radius via `getBBox`, including CSS/SMIL animation. Comparing only the underlying `r` attribute falsely rejected the native HTML of overlap attempt 1. Corrected native review passes four states, while its exported SVG genuinely retains `r=0` and shows none of the nine regions or 100 task dots. That portable export remains a failure; the evaluator correction does not repair or waive it.','',
                  'Direct inspection of overlap attempt 2 found that its footer caption inherited a 16px font and covered task labels T094, T095 and T100. Rendered bounding-box measurements confirm three caption/task-label collisions in every one of the six states; these explicit readability findings reject the artifact gate even though the geometry, semantic alpha, BW and pixel audits pass. The inspector now retains the caption font and both intersecting bounds.','',
                  'Final runs use the original unmodified task prompts. Medium thinking is a scoped runtime choice for this narrow painting revision; model, isolation, strict trace and independent rendered acceptance requirements are unchanged.',''])
    (OUT/'treemap-tones-isolated-20261003.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print(json.dumps({'phase':report['phase'],'passed':report['passed'],'attempts':len(attempts),'originalDiagnosticInputsUnchanged':original_unchanged}))


if __name__=='__main__':
    main()
