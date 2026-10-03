#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Close the bounded research trial and install only an independently gated gain."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import statistics
import subprocess
import sys

from continue_technique_evolution import campaign_root, digest, put
from inspect_technique_evolution import collect, describe
from seal_technique_evolution import REPO, org, read, sha, wsl


def files(path):
    return {p.relative_to(path).as_posix():sha(p) for p in path.rglob('*') if p.is_file()}


def main():
    root=REPO/'evaluations/runs/svt4'
    decision=read(root/'decision-c.json')
    dev=decision['comparison']
    assert dev['complete_evaluable'], 'Do not close an unresolved external/evaluator failure as a semantic rejection'
    native=read(root/'run.json')
    audit=read(root/'model-and-behavior-audit.json')
    assert all(audit[a]['assistant_models']==['gpt-6-luna'] for a in ['b','c'])
    source, installed=REPO/'skills/svg-brief-design', REPO/'.agents/skills/svg-brief-design'
    assert files(source)==files(installed)==files(root/'inputs/b/svg-brief-design')
    selected=root/'inputs/c/svg-brief-design'
    assert files(selected)==files(root/'sealed-c/candidate/skills/svg-brief-design')
    private=None
    accepted=False
    study=root/'study'
    if dev['passed']:
        assert (root/'gate-started.json').exists()
        a,b=collect(root/'private-jobs/b',6),collect(root/'private-jobs/w',6)
        private_models=[]
        for directory in [root/'private-jobs/b',root/'private-jobs/w']:
            for path in directory.glob('*/agent/pi.txt'):
                for line in path.read_text(encoding='utf-8').splitlines():
                    try: event=json.loads(line)
                    except ValueError: continue
                    if event.get('type')=='message_end' and event.get('message',{}).get('role')=='assistant':
                        private_models.append(event['message'].get('model'))
        assert private_models and set(private_models)=={'gpt-6-luna'}
        assert all(r['input_isolated'] and r['skill_unchanged'] for r in a+b)
        put(root/'private-model-audit.json',{'trials':12,'observed_aliases':sorted(set(private_models)),
            'assistant_messages':len(private_models),'input_and_integrity_passed':True})
        private=describe(a,b)
        private['execution_counts']={role:{'attempts':len(rs),'errors':sum(bool(r['exception']) for r in rs),
            'valid_scored_artifacts':sum(r['reward'].get('artifact_valid')==1 for r in rs)} for role,rs in [('baseline',a),('candidate',b)]}
        accepted=private['passed'] and native['holdout'].get('promoted') is True
        put(root/'validation-decision.json',{'passed':accepted,'comparison':private,
            'native_gate':native['holdout'],'protocol_sha256':sha(root/'protocol.json'),
            'candidate_tree':digest(selected),'post_gate_mutations':0,'retired':True})
        for identifier,path,kind in [('native-private-b',root/'private-jobs/b','native-job'),
                                     ('native-private-w',root/'private-jobs/w','native-job'),
                                     ('private-decision',root/'validation-decision.json','decision')]:
            org('record-evidence',study,'--stage-id','validate','--evidence-id',identifier,
                '--kind',kind,'--role','validation','--visibility','private','--path',path)
        org('transition',study,'--stage-id','validate','--status','completed')
    else:
        assert not (root/'validation-release-ready.json').exists()
        for identifier,path,kind in [('native-b',root/'jobs/b','native-job'),
                                     ('native-c',root/'jobs/c','native-job'),
                                     ('selection',root/'run.json','evolution-report'),
                                     ('development-decision',root/'decision-c.json','decision')]:
            org('record-evidence',study,'--stage-id','evolve','--evidence-id',identifier,
                '--kind',kind,'--role','development','--visibility','private','--path',path)
        org('transition',study,'--stage-id','evolve','--status','completed','--note','One research candidate completed; no eligible changed winner.')
        org('transition',study,'--stage-id','validate','--status','stopped','--note','No development-qualified improvement; adopted private cohort remains untouched.')
    if accepted:
        for relative in files(selected):
            target=source/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(selected/relative,target)
        assert files(source)==files(selected)
        subprocess.run([sys.executable,str(REPO/'scripts/sync-local-skills.py'),
            '--source',str(source),'--destination',str(installed)],check=True)
        assert files(source)==files(installed)
        future=REPO/'projects/svg-brief-design/evaluation/runtime-v6.3/future-job.json'
        shutil.copy2(future,root/'future-job-before-promotion.json')
        config=read(future)
        config['agents'][0]['skills']=[wsl(selected)]
        future.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    rows=decision['trial_audit']
    assert all(r['input_isolated'] and r['skill_unchanged'] for a in ['b','c'] for r in rows[a])
    ranking={r['candidateId']:r for r in native['ranking']}
    summaries={}
    for arm in ['b','c']:
        scores=[r['reward']['technique_quality'] for r in rows[arm] if 'technique_quality' in r['reward']]
        effective=sum(scores)/len(rows[arm])
        paths=list((root/'generation-000/candidates'/arm).glob('candidate-result.json'))
        assert len(paths)==1
        native_summary=read(paths[0])['summary']
        assert abs(effective-native_summary['evaluableMeanReward'])<1e-10
        summaries[arm]={'attempts':len(rows[arm]),'scored_artifacts':len(scores),
            'agent_errors':sum(bool(r['exception']) for r in rows[arm]),
            'native_effective_mean':effective,'scored_only_mean':statistics.mean(scores) if scores else None,
            'strict_90_count':sum(s>=.9 for s in scores),
            'guide_read_trials':audit[arm]['guide_read_trials'],
            'proof_used_trials':audit[arm]['proof_used_trials'],'proof_read_trials':audit[arm]['proof_read_trials']}
    jobs=[root/f'jobs/{a}' for a in ['b','c']]
    if private is not None: jobs += [root/'private-jobs/b',root/'private-jobs/w']
    jev=[read(p) for j in jobs for p in j.glob('*/verifier/provider-response-*.json')]
    observers=[read(p) for j in jobs for p in j.glob('*/verifier/critic/receipt.json')]
    result={'status':'accepted-pilot' if accepted else 'development-gain-not-validated' if dev['passed'] else 'research-candidate-rejected',
        'finished_at':datetime.now(timezone.utc).isoformat(),'installed_changed':accepted,
        'installed_tree':digest(source),'candidate_tree':digest(selected),
        'development':dev,'validation':private,'validation_released':private is not None,
        'native_validation_gate':native.get('holdout'),
        'summaries':summaries,'native_ranking':native['ranking'],
        'calls':{'generation':sum(len(collect(j)) for j in jobs),'jev':len(jev),'visual_observer':len(observers),'new_curator':0,'semantic_retries':0},
        'cost':{'jev_usd':sum(r['usage']['cost'] for r in jev),'generator_usd':None,'observer_usd':None},
        'local_tests':{'scaffold':13,'proof':4,'passed':True},'source_audit':audit['source_audit'],
        'protocol_sha256':sha(root/'protocol.json'),'native_run_sha256':sha(root/'run.json'),
        'model_audit_sha256':sha(root/'model-and-behavior-audit.json'),
        'limitations':['Six public families and two repeats; descriptive pilot, not professional parity.',
            'Expected coded relative utility is not an absolute grade or pixel similarity.',
            'Instruction routing and proof helper are one treatment; no isolated causal attribution.',
            'Native explicit skill loading; unforced discovery not tested.',
            'Provider alias gpt-6-luna observed; immutable checkpoint unavailable.']}
    put(root/'research-decision.json',result)
    report_root=REPO/'evaluations/svg-brief-design'
    put(report_root/'information-editing-20260926.json',result)
    comparable=dev['unaffected_family_visual_guard']
    table='\n'.join(f"| {a} | {s['scored_artifacts']}/12 | {s['agent_errors']} | {100*s['native_effective_mean']:.2f} | {s['proof_used_trials']}/12 |" for a,s in summaries.items())
    families='\n'.join(f"| {task.split('--')[0]} | {100*v['baseline']:.2f} | {100*v['candidate']:.2f} | {100*v['delta']:+.2f} |" for task,v in dev['families'].items())
    disposition=('The candidate passed the independent pilot gate and was installed.' if accepted else
                 'The candidate did not meet the complete acceptance rule. The installed skill is unchanged; the tested research bundle remains available for inspection.')
    private_text='No development winner qualified, so private validation was not opened.'
    if private is not None:
        counts=private['execution_counts']
        private_text=(f"The private gate completed six attempts per version: baseline {counts['baseline']['valid_scored_artifacts']}/6 valid scored artifacts and {counts['baseline']['errors']} execution errors; candidate {counts['candidate']['valid_scored_artifacts']}/6 valid scored artifacts and {counts['candidate']['errors']} execution errors. ")
        if private['complete_evaluable']:
            private_text+=f"The paired mean changed by {100*private['mean_gain']:+.2f} points."
        else:
            private_text+='A complete error-free paired quality estimate is unavailable. This blocks promotion; it is not evidence that the candidate has worse artistic quality. No semantic retry is permitted by this protocol.'
    report=f'''# Information selection and vector editing experiment

{disposition}

## Research and candidate

The user asked whether techniques for selecting information, choosing its amount
and editing images could improve the skill. The experiment translated source
material from NN/g, IxDF, Adobe, Inkscape and W3C into a role-based content budget,
a symptom-to-operation guide and a reversible SVG proof helper. Required meaning,
supporting structure and optional accents have different jobs; minimum element
count alone is not an objective. Boolean openings, grouping, local curve edits,
hierarchy and scale review are selected according to the observed defect.

The helper renders a large view, a small view and a colored transparency view.
An optional second column removes specified SVG groups only in a diagnostic
copy. It does not decide artistic quality or rewrite the original. Four tests
verify true holes versus white patches, optional omission without source changes,
absent-group handling and rejection of active content. Thirteen existing scaffold
tests also pass. The candidate contains twelve source files, no purchased artwork.

## Complete live result

All 24 public generator executions used exact `openai-codex/gpt-6-luna`, observed
alias `gpt-6-luna`, through Pi at medium reasoning. Same six briefs, two attempts
per family and fixed Jev 6.3 scoring. Astra is only the separate visual evidence
observer; Jev remains the scorer. No semantic retry or brief/rubric change occurred.

| Arm | Valid scored artifacts | Agent errors | Native effective mean / 100 | Proof helper used |
| --- | ---: | ---: | ---: | ---: |
{table}

Native effective means retain attributable agent failures as zero. An errored
trial has no invented Jev score; the gallery marks it explicitly. The preregistered
additional comparison excludes every family affected by a baseline agent failure,
while retaining candidate failures as zero. This covers {len(comparable['families'])}
families and gives **{100*comparable['baseline_mean']:.2f} to
{100*comparable['candidate_mean']:.2f}, a change of {100*comparable['mean_gain']:+.2f}
points**. All candidate trials must additionally be error-free; mean gain must
reach two points and no family may lose over eight points. These conditions
prevent apparent improvement driven only by control failures.

| Public family | Baseline effective mean | Candidate effective mean | Delta, points |
| --- | ---: | ---: | ---: |
{families}

The new guide was read in {summaries['c']['guide_read_trials']}/12 candidate
executions. The proof helper was called in {summaries['c']['proof_used_trials']}/12,
and a proof-named PNG was opened in {summaries['c']['proof_read_trials']}/12.
These are behavior observations, not evidence that the helper alone caused a
score difference. The strict 90 screen was reached by
{summaries['b']['strict_90_count']}/12 baseline attempts and
{summaries['c']['strict_90_count']}/12 candidate attempts.
The score remains expected coded relative utility, not an absolute professional
grade. Inspect all families and both repeats before interpreting the average.

## Isolation and disposition

Private validation was {'released once after selection; the cohort is now retired' if private is not None else 'never released or run'}.
{private_text}

The reserve was explicitly adopted from the closed svt3 experiment, which never
opened it; it was not described as freshly authored. No new curator call was
needed. Private content did not enter research, mutation or development selection.
All public input-isolation and unchanged-skill audits passed. Host-level optimizer
read avoidance remains procedural, separate from container isolation.

Exact-text inspection found no match to 52 long paths from six public originals.
This is a bounded payload check, not proof against every transformed copy.
The proof demo is a new synthetic fixture, not a purchased SVG or Luna output.
Local preview import caches were archived before candidate inference, and the
candidate tree was rechecked against its immutable sealed realization.

The research hypothesis was tested as one bundle. A one-line exact-path link fix
was also included. This pilot cannot isolate each intervention, establish
statistical significance or demonstrate broad professional parity. The earlier
three-failure campaign remains closed; this is one new bounded investigation.

## Evidence

- [Research sources and decision matrix](../../projects/svg-brief-design/evaluation/information-editing-research-20260926.md)
- [Citation supplement](../runs/svt4/research-source-addendum.md)
- [Full machine-readable result](information-editing-20260926.json)
- [Native Harbor report](../runs/svt4/native-report/final-report.md)
- [All public outputs and failures](../runs/svt4/gallery-c/index.html)
- [Tested candidate skill](../runs/svt4/inputs/c/svg-brief-design/SKILL.md)
- [Proof demonstration](../runs/svt4/proof-demo.png)
- [Public visual review and limits](../runs/svt4/public-visual-review.md)
- [Frozen protocol](../runs/svt4/protocol.json)
- [Observed model and behavior audit](../runs/svt4/model-and-behavior-audit.json)

Known Jev cost: ${result['cost']['jev_usd']:.8f}. Reliable generator and observer
monetary costs are unavailable; zero placeholders must not be interpreted as free.
'''
    with (report_root/'information-editing-20260926.md').open('x',encoding='utf-8') as handle:
        handle.write(report)
    put(campaign_root(root)/'completion.json',{'stopped':True,'candidate_count':1,
        'installed_changed':accepted,'decision_sha256':sha(root/'research-decision.json')})
    print(json.dumps({'status':result['status'],'installed_changed':accepted,
        'summaries':summaries,'comparable_delta':comparable['mean_gain'],'validation':private},indent=2))


if __name__=='__main__':main()
