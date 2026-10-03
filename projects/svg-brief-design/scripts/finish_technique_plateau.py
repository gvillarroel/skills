#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Close a completed three-rejection plateau without installing a failed bundle."""
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import subprocess
import sys

from seal_technique_evolution import REPO, org, read, sha
from inspect_technique_evolution import collect
from continue_technique_evolution import digest, put


def files(root):
    return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file()}


def main():
    root = REPO / "evaluations/runs" / sys.argv[1]
    campaign = REPO / "evaluations/runs/svg-continuation-20260926"
    event_paths = sorted((campaign / "events").glob("*.json"))
    events = [read(p) for p in event_paths]
    assert events[-1]["failure_streak"]==3
    assert all(not e["accepted"] for e in events[-3:])
    assert not (root / "validation-release-ready.json").exists()
    for index,event in enumerate(events):
        assert event["evidence_sha256"] == sha(event["evidence"])
        assert event["previous_event_sha256"] == (sha(event_paths[index-1]) if index else None)
    baseline = root / "inputs/b/svg-brief-design"
    canonical = REPO / "skills/svg-brief-design"
    installed = REPO / ".agents/skills/svg-brief-design"
    assert files(baseline)==files(canonical)==files(installed)
    assert digest(canonical)==read(root / "protocol.json")["baseline_tree"]
    rows = {a:collect(root / f"jobs/{a}",12) for a in ["b","c","d","e"]}
    assert all(r["input_isolated"] and r["skill_unchanged"] for rs in rows.values() for r in rs)
    decisions = {a:read(root / f"decision-{a}.json")["comparison"] for a in ["c","d","e"]}
    assert all(d["complete_evaluable"] and not d["passed"] for d in decisions.values())
    native = read(root / "run.json")
    assert all(r["infrastructureFailureTrials"]==0 and r["providerFailureTrials"]==0 for r in native["ranking"])
    jev=[]; observers=[]; usage=[]
    for job in (root / "jobs").iterdir():
        jev.extend(read(p) for p in job.glob('*/verifier/provider-response-*.json'))
        observers.extend(read(p) for p in job.glob('*/verifier/critic/receipt.json'))
        for path in job.glob('*/agent/pi.txt'):
            for line in path.read_text(encoding='utf-8').splitlines():
                try: event=json.loads(line)
                except ValueError: continue
                if event.get('type')=='message_end' and event.get('message',{}).get('role')=='assistant':
                    message=event['message']
                    assert message.get('model')=='gpt-6-luna'
                    usage.append(message.get('usage',{}))
    summary = {a:{"trials":len(rs),"agent_errors":sum(bool(r["exception"]) for r in rs),
        "valid_scored_artifacts":sum(r["reward"].get("artifact_valid")==1 for r in rs),
        "reported_quality_mean":statistics.mean(r["reward"]["technique_quality"] for r in rs if "technique_quality" in r["reward"]),
        "strict_90_screen":sum(r["reward"].get("technique_quality",0)>=.9 for r in rs),
        "preview_reads":sum(r["preview_reads"]>0 for r in rs),
        "scaffold_calls":sum(r["scaffold_used"] for r in rs)} for a,rs in rows.items()}
    result={"status":"plateau-baseline-retained","finished_at":datetime.now(timezone.utc).isoformat(),
        "failure_streak":3,"accepted_improvements":events[-1]["accepted_improvements"],
        "installed_changed":False,"installed_tree":digest(canonical),"events":events,
        "summaries":summary,"comparisons":decisions,"native_ranking":native["ranking"],
        "calls":{"generation":48,"visual_observer":len(observers),"jev":len(jev),
                 "curator":2,"semantic_retries":0,"private_gate":0},
        "usage":{"generator_assistant_messages":len(usage),
                 "generator_reported_input_tokens":sum(u.get('input',0) for u in usage),
                 "generator_reported_cache_read_tokens":sum(u.get('cacheRead',0) for u in usage),
                 "generator_reported_cache_write_tokens":sum(u.get('cacheWrite',0) for u in usage),
                 "generator_reported_output_tokens":sum(u.get('output',0) for u in usage),
                 "generator_reported_total_tokens":sum(u.get('totalTokens',0) for u in usage),
                 "generator_cost_usd":None,"observer_cost_usd":None,
                 "observer_reported_total_tokens":sum(r.get('usage',{}).get('totalTokens',0) for r in observers),
                 "jev_cost_usd":sum(r['usage']['cost'] for r in jev),
                 "jev_input_tokens":sum(r['usage']['input_tokens'] for r in jev),
                 "jev_output_tokens":sum(r['usage']['output_tokens'] for r in jev)},
        "validation":{"released":False,"unused_cases":3,"curator_passed":True},
        "local_tests":{"c":13,"d":14,"e":15},
        "source_audit":read(root / "source-path-audit.json"),
        "method_notes":read(root / "protocol-interpretation.json"),
        "protocol_sha256":sha(root / "protocol.json"),"native_run_sha256":sha(root / "run.json")}
    put(root / "plateau-decision.json",result)
    report_root=REPO / "evaluations/svg-brief-design"
    put(report_root / "continuation-20260926.json",result)
    descriptions={"c":"Contour hierarchy and mass/void instructions",
                  "d":"Read-only helper description and precise file/attribute contract",
                  "e":"Original cubic ribbon generator, joint mass/opening construction and explicit thumbnail review"}
    table=[]
    for arm in ['c','d','e']:
        comparison=decisions[arm]
        guard=comparison['unaffected_family_visual_guard']
        table.append(f"| {arm} | {descriptions[arm]} | {summary[arm]['valid_scored_artifacts']}/12 | {summary[arm]['agent_errors']} | {guard['mean_gain']*100:+.2f} | Rejected |")
    text='''# SVG skill continuation: three consecutive rejected candidates

The requested stopping condition was reached. Three distinct, fully executed
candidate interventions failed acceptance. The canonical and locally installed
skill remain byte-identical to the incoming validated pilot. No experimental
candidate was installed and the fresh private cohort was never released.

## Complete attempt record

All arms used the same six public families, two executions per family, exact
GPT-6 Luna through Pi at medium reasoning, and frozen Jev 6.3 scoring. The quality
score is expected coded relative utility, not a percentage of professional
mastery or pixel similarity. All attempts are retained; no semantic failure was
rerun or replaced.

| Candidate | Intervention | Valid scored outputs | Agent errors | Change on comparable families, points | Decision |
| --- | --- | ---: | ---: | ---: | --- |
'''+ '\n'.join(table)+f'''

The baseline had {summary['b']['agent_errors']} agent failures in the printed-diagram
family: an unsupported recipe attribute and an invented reference filename.
Native Harbor treats attributable agent failures as effective zero outcomes;
their original errors and absent Jev scores remain intact. The table's additional
comparison excludes that entire affected baseline family, retains candidate
failures as native zeros, and therefore covers five equally weighted families.
It is an added conservative sensitivity guard, not a new visual scorer. A
candidate still needs complete error-free qualification, a two-point mean gain,
and no family loss beyond eight points before the independent gate can open.

The reported means over only successfully scored outputs are available in JSON
for diagnostics. They exclude failures and must not be used to select a winner.
The native full-qualification ranking and all raw failures are preserved.

## What was learned

The first contour intervention sometimes produced large, insufficiently
articulated black masses. Some labels retained unnecessary fields or intersected
their codes. The second intervention supplied a correct, tested helper API but
did not reliably prevent the model from making invalid tool calls. The third
introduced a mathematically original variable-width cubic band, with controls
for its centerline, breadth and taper; this local mechanism passed rendering and
boundary tests, but a working helper alone does not establish end-to-end quality.
Its final native results determine its disposition above.

Purchased references still demonstrate stronger organization of voids, contour
rhythm, compact information and print-specific line treatment in the reviewed
public examples. This run provides no evidence of consistent professional parity.
The incumbent also showed execution and quality variance in this fresh repeat,
so its earlier pilot gain should not be interpreted as reliable excellence.

## Isolation, limits and verification

There were 48 native generator executions, {len(observers)} visual-observer calls,
{len(jev)} Jev calls, and two source-curation calls. The first curation attempt
could not establish three independent suitable families; no candidate was run
against that rejected design. The enlarged source pool passed a separate blind
curation review before candidate inference. That three-case gate remains unused.
All 48 executor input and unchanged-skill audits passed. The main optimizer's
private-data restriction is procedural; generator containers have separately
audited input isolation.

No scoring byte, purpose profile, judge model, or public task changed. An inherited
sentence in the sealed protocol still says one revision; the same sealed file's
explicit max_candidates=3 budget and three-rejection stopping rule governed the
run, as requested by the user. The stale helper wording is corrected only for
future studies. The conservative baseline-failure sensitivity guard was added
after that issue was observed, is disclosed separately, and only restricts
acceptance. Neither issue is hidden by rewriting the sealed protocol.

The candidate realizations passed 13, 14 and 15 deterministic tests respectively.
The first two bundles contain nine source files; the third contains ten. No SVG,
raster image or encoded artwork is packaged. An exact-text audit found no match
to 52 long paths from the six public originals; this is a bounded copy check,
not proof against every transformed reconstruction. All purchased previews stay
in the owner's local evaluation gallery, outside the skill.

Observed Jev cost was ${result['usage']['jev_cost_usd']:.8f}. Reliable monetary
cost for generator and visual-observer calls is unavailable; their Pi zero cost
fields are not evidence that the calls were free. Token counts and complete
native provenance are in the JSON companion.

## Evidence

- [Compact machine-readable report](continuation-20260926.json)
- [Sealed protocol](../runs/{root.name}/protocol.json)
- [Explicit protocol interpretation](../runs/{root.name}/protocol-interpretation.json)
- [Native population result](../runs/{root.name}/run.json)
- [First candidate: every public output](../runs/{root.name}/gallery-c/index.html)
- [Second candidate: every public output](../runs/{root.name}/gallery-d/index.html)
- [Third candidate: every public output](../runs/{root.name}/gallery-e/index.html)
- [Original ribbon helper and guide, experimental only](../runs/{root.name}/inputs/e/svg-brief-design/SKILL.md)
- [Earlier accepted pilot](construction-20260926.md)
'''
    path=report_root / "continuation-20260926.md"
    with path.open('x',encoding='utf-8') as handle: handle.write(text)
    study=root / "study"
    for arm in ['b','c','d','e']:
        org('record-evidence',study,'--stage-id','evolve','--evidence-id','native-'+arm,
            '--kind','native-job','--role','development','--visibility','private','--path',root / f'jobs/{arm}')
    for identity,kind,path in [('native-selection','evolution-report',root / 'run.json'),
                               ('plateau-decision','decision',root / 'plateau-decision.json')]:
        org('record-evidence',study,'--stage-id','evolve','--evidence-id',identity,
            '--kind',kind,'--role','development','--visibility','private','--path',path)
    org('transition',study,'--stage-id','evolve','--status','completed','--note','Three complete candidate attempts rejected; preserve incumbent.')
    org('transition',study,'--stage-id','validate','--status','stopped','--note','No eligible changed winner; unused private cohort remains sealed.')
    put(campaign / 'completion.json',{'failure_streak':3,'stopped':True,'installed_changed':False,
        'decision':str(root / 'plateau-decision.json'),'sha256':sha(root / 'plateau-decision.json')})
    print(json.dumps({'status':result['status'],'failure_streak':3,'installed_changed':False,
                      'calls':result['calls'],'summary':summary},indent=2))


if __name__=='__main__':main()
