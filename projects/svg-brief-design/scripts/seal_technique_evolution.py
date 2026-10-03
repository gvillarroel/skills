#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Register a bounded native Harbor comparison and its one-way pilot gate."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svt1"
PRIOR = REPO / "evaluations/runs/svg-technique-v6.3"
ORGANIZER = Path("C:/Users/villa/.codex/skills/harbor-organize-evaluations/scripts/manage_harbor_evaluations.py")
REALIZER = Path("C:/Users/villa/.codex/skills/harbor-realize-skill-candidate/scripts/realize_skill_candidate.py")
IMAGE = "sha256:1c1ac1dfdc903a9f3a64f4a3a75be7ab883a94647edac0045105d89674b4cbf8"


def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, v):
    p = Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def wsl(p): return "/mnt/c/" + Path(p).resolve().as_posix()[3:]
def org(*args):
    result = subprocess.run([sys.executable,str(ORGANIZER),*map(str,args)],capture_output=True,text=True,encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:])
    return result.stdout


def main(root=None, baseline_source=None, max_candidates=2, prepare_candidate=True, protocol_updates=None,
         attempts=2, evolution_owner="harbor-population-search"):
    global ROOT
    if root is not None:
        ROOT = Path(root)
    assert attempts >= 1
    assert evolution_owner in {"harbor-population-search", "harbor-reflective-pareto-search"}
    assert read(ROOT / "curation-status.json")["passed"]
    validation_cases = read(ROOT / "curation-status.json")["selected_count"]
    baseline = ROOT / "inputs/b/svg-brief-design"
    shutil.copytree(baseline_source or REPO / "evaluations/runs/svp3/inputs/q/svg-brief-design",baseline)
    for p in baseline.rglob("*"):
        if p.is_file(): assert sha(p)==sha(REPO / "skills/svg-brief-design" / p.relative_to(baseline))
    digest = json.loads(subprocess.check_output([sys.executable,str(REALIZER),"digest",str(baseline)]))["treeSha256"]
    environment = {"import_path":"procedural_environment:ProceduralEnvironment","delete":True,
                   "kwargs":{"agent_image":IMAGE,"source_agent_image":IMAGE}}
    template = read(PRIOR / "future-job.json")
    template.update(n_attempts=attempts,n_concurrent_trials=3,environment=environment,jobs_dir=wsl(ROOT / "jobs"))
    template["agents"][0]["skills"] = [wsl(baseline)]
    template["verifier"]["kwargs"] = {"evaluator_bundle":wsl(ROOT / "evaluator"),"evaluator_lock_sha256":sha(ROOT / "evaluator/lock.json")}
    template["datasets"][0]["path"] = wsl(ROOT / "development")
    write(ROOT / "templates/development.json",template)
    validation = json.loads(json.dumps(template))
    validation["job_name"] = "technique-private-pilot"
    validation["datasets"] = [{"path":wsl(ROOT / "private/validation")}]
    write(ROOT / "templates/validation.json",validation)
    probe = """from pathlib import Path
import json,os
blocked=['/tests','/solution','/curator','/app/datasets','/work','/mnt/c/Users/villa/dev/skills/evaluations/runs/svt1/private']
assert all(not Path(p).exists() for p in blocked)
assert not os.environ.get('OPENROUTER_API_KEY')
assert not list(Path('/app').rglob('*.svg'))
assert not list(Path('/root').rglob('*.svg'))
assert Path('/harbor/skills/svg-brief-design/SKILL.md').is_file()
print(json.dumps({'passed':True,'uid':os.getuid(),'hidden_paths_absent':blocked,'host_secret_absent':True,'model_calls':0}))
"""
    probe = probe.replace('/mnt/c/Users/villa/dev/skills/evaluations/runs/svt1/private', wsl(ROOT / 'private'))
    result = subprocess.run(["wsl","-e","docker","run","--rm","--network","none","--mount",f"type=bind,source={wsl(baseline)},target=/harbor/skills/svg-brief-design,readonly",IMAGE,"python","-c",probe],capture_output=True,text=True,encoding="utf-8")
    if result.returncode: raise RuntimeError(result.stderr)
    write(ROOT / "runtime-access-probe.json",json.loads(result.stdout))
    # A real live-container host bind check catches the earlier Windows/WSL
    # path failure without purchasing another model execution.
    target = ROOT / "probe/generation-000/candidates/c/harbor-jobs/harbor-pop-g000-c/vector-030--d3c57e0c21dbede0__probe000/artifacts/logs/artifacts"
    target.mkdir(parents=True)
    code = "from pathlib import Path; import time; Path('/logs/artifacts/probe.txt').write_text('ready'); print('ready',flush=True); time.sleep(2)"
    with subprocess.Popen(["wsl","-e","docker","run","--rm","--network","none","--mount",f"type=bind,source={wsl(target)},target=/logs/artifacts",IMAGE,"python","-c",code],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) as process:
        ready = process.stdout.readline().strip()
        passed = ready=="ready" and (target / "probe.txt").read_text()=="ready"
        _, error = process.communicate(timeout=15)
    assert passed and process.returncode==0, error
    write(ROOT / "mount-readiness.json",{"passed":True,"path_length":len(str(target)),"model_calls":0})
    evidence = REPO / "projects/svg-brief-design/evaluation/technique-design-contract.md"
    protocol = {
        "schemaVersion":2,"created_at":datetime.now(timezone.utc).isoformat(),
        "claim":"Pilot improvement over the currently installed procedural skill for short monochrome illustration briefs; not parity with curated professional originals or general vector-art superiority.",
        "baseline_tree":digest,"baseline":str(baseline),
        "development":{"dataset":"dev","cases":6,"families":6,"attempts":2,"weight":"equal family means"},
        "validation":{"dataset":"val","cases":3,"construction_families":3,"source_packs":3,"attempts":2,"release":"once after one development winner is frozen; no subsequent same-study tuning","scope":"new constructions, unseen source items and packs relative to this six-family development comparison; shared publisher and broad style capabilities"},
        "budget":{"max_development_generation_calls":12*(1+max_candidates),"max_validation_generation_calls":12,"baseline_calls":12,"max_candidates":max_candidates,"calls_per_candidate":12,"observer_calls_max":12*(2+max_candidates),"jev_calls_max":12*(2+max_candidates),"retries":0,"curator_calls":1},
        "selection":{"metric":"technique_quality","required_rewards":{"artifact_valid":1},"minimum_development_gain":0.02,"minimum_validation_gain":0.02,"maximum_family_regression":0.08,"rule":f"Rank complete error-free candidates using native Harbor population search. Baseline may be retained. Up to {max_candidates} content-changing development candidates allowed; retain all proposals/trials. Gate only a changed winner with at least two percentage points mean gain and no family loss over eight points. Validation must independently satisfy the same two checks, exact full coverage, no execution errors and all valid artifacts. Any unresolvable evaluator result makes the comparison inconclusive. No claims of statistical significance.","uncertainty":"Report all family deltas; descriptive range and family-level bootstrap interval, six and three independence groups. Replicates are not extra independent families. Low-confidence judge fields are disclosed; not silently converted into zeros.","primary_pass_threshold_for_ranking":0,"strict_excellence_screening_threshold":0.9},
        "runtime":{"model":"openai-codex/gpt-6-luna","thinking":"medium","transport":"sse","pi":"0.84.2","harbor":"0.18.0","agent_image":IMAGE,"tools":["read","write","bash"],"agent_timeout":240,"verifier_timeout":600,"concurrency":3,"task_resource":"2 CPU / 2048 MB","network":"bridge/public as existing paired tasks","loading":"native-explicit-skill-command; not unforced discovery","model_revision_limitation":"Provider reports gpt-6-luna alias; immutable checkpoint unavailable. Same session and runtime paired arms."},
        "environment_fix":"Use the existing ProceduralEnvironment with identical source and effective image, supplying the attributes required by PiSvgProcedural; no image or scoring change.",
        "evaluator":read(ROOT / "evaluator-extension.json"),
        "development_memory":{"allowed":[str(evidence)],"evidence_sha256":sha(evidence),"generator":"Only the locked skill, current brief, tools and renderer; no original SVG, previous outputs, scores or optimizer memory."},
        "privacy":"Private curator is a separate tool-free Astra context. Main optimizer does not inspect private tasks or curator outputs before final freeze. Host-level optimizer restriction is procedural, not an OS security boundary. Real generator container cannot access host references, other task files or optimizer history; probe and every trial input audit verify it.",
        "stopping":f"At most {max_candidates} sequential development candidates in this phase. A changed eligible candidate is frozen before the one-use validation gate. No same-study mutation after release. For the continuation campaign, each complete rejected candidate increments the failure streak; accepted independent improvement resets it. Stop the campaign at three consecutive rejected candidates. External failures are inconclusive, not failed improvement attempts. A consumed gate requires a new study and fresh cohort before continuation. No semantic retries.",
        "template_sha256":{p.name:sha(p) for p in (ROOT / "templates").glob("*.json")},
        "helper_sha256":{n:sha(Path(__file__).parent / n) for n in ["pi_svg_procedural.py","procedural_environment.py","run_procedural_population.py","harbor_svg_technique.py"]},
    }
    if protocol_updates:
        for key, value in protocol_updates.items():
            if isinstance(value, dict) and isinstance(protocol.get(key), dict):
                protocol[key].update(value)
            else:
                protocol[key] = value
    write(ROOT / "protocol.json",protocol)
    study = ROOT / "study"
    if baseline_source is not None:
        protocol["development_memory"]["imported_prior_exposure"] = ["Six public technique families and all prior public SVG development studies; previous private gate outcomes are excluded from mutation evidence. The inherited baseline was selected in a prior study."]
        write(ROOT / "protocol.json",protocol)
    org("init",study,"--study-id","svg-technique-"+ROOT.name,"--title","Constructive figure-ground skill evolution","--objective",protocol["claim"],"--comparison-profile",f"luna-medium-jev63-paired-{attempts}-attempts")
    org("add-dataset",study,"--dataset-id","dev","--split","development","--source",ROOT / "development")
    org("add-dataset",study,"--dataset-id","val","--split","validation","--source",ROOT / "private/validation")
    org("add-stage",study,"--stage-id","evolve","--kind","evolution","--owner-skill",evolution_owner,"--dataset-id","dev")
    org("add-stage",study,"--stage-id","validate","--kind","validation","--owner-skill",evolution_owner,"--dataset-id","val","--depends-on","evolve")
    review = ROOT / "review"; review.mkdir()
    for source in [ROOT / "private/curation.json",ROOT / "runtime-access-probe.json",ROOT / "mount-readiness.json",PRIOR / "validation-receipt.json",PRIOR / "integration-lock.json",ROOT / "curation-status.json"]:
        shutil.copy2(source,review / source.name)
    report = """# Private pre-execution review

The independent tool-free curator reviewed an image inventory and accepted three
source/construction families from three packs omitted from this development set.
The full source-fit, alternative-valid construction and non-clone findings are
in curation.json; its content is not delivered to the candidate optimizer.
All catalog preview sources, raster sources and active references were excluded.
Source archives remain licensed local evaluation anchors; no public artwork is
redistributed. Shared publisher/style and unmeasurable pretraining exposure limit
the claim. Entirely unseen publishers or all prior human exposure are not claimed.

Fixed 6.3 scoring semantics have prior blinded source/generated decisions,
reversed-side, text-purpose, degraded/cropped and identical-artifact controls.
The inherited validation receipt and integration lock bind those actual tests.
The extension adds anchors only; executable scoring bytes and profiles match.
Every selected original and development original passed deterministic rendering
and vector validity during curation. Curator-reviewed alternatives are semantic
coverage evidence, not newly observed model scores. No reference-is-identical
shortcut is used: quality is judged using six visual dimensions and a subject
gate, not path or pixel agreement.

The artifact contract is explicit in every request. Validation varies three
requested output paths; this is nuisance coverage, not independent semantic
evidence. Native verification reads exactly the declared path. Output-file
location does not determine a quality label. HTML, scripts, external images,
malformed and blank drawings remain rejected by the inherited verifier tests.

This is a descriptive small pilot: six development and three validation groups,
two independent executions each. All families are equally weighted; more
replicates do not increase family sample size. No significant population-wide
gain is promised. A two-point mean gain and maximum eight-point family loss
were chosen before inference; private release occurs once after frozen selection.

The actual image/container/user probe found no host source, tests, previous SVGs,
optimizer history or evaluator credential in the executor, and proved the live
host artifact mount works at the expected path depth. Each native Pi trial also
audits its exact input and unchanged skill tree. The main optimizer has host
privileges; private read avoidance is procedural, not a separate OS principal.
It receives only aggregate curator readiness before freeze and will not open
private tasks/results during candidate mutation. This limitation is explicit.
"""
    report = report.replace("two independent executions each", f"{attempts} independent executions each")
    if validation_cases != 3:
        report = report.replace("three", str(validation_cases)).replace("Three", str(validation_cases))
    (review / "review.md").write_text(report,encoding="utf-8")
    datasets = []
    for name in ["dev","val"]:
        lock = read(study / f"datasets/{name}.lock.json")
        # Use the actual locked tree and task names without disclosing private
        # identities to the optimizer's tool output.
        datasets.append({"datasetId":name,"datasetSha256":lock["sha256"],"tasks":[
            {"taskId":t["taskId"],"taskSha256":t["sha256"],"groupIds":[f"{name}-construction-{i}"]}
            for i,t in enumerate(lock["tasks"])]})
    write(review / "review.json",{"schemaVersion":1,"reviewer":"isolated-astra-curator-plus-native-6.3-controls-and-container-audit","checks":{
        key:{"status":"pass","evidenceFile":"review.md"} for key in ["provenanceAndContamination","groupIsolation","surfaceCues","verifierQuality","coverageAndPower","accessIsolation"]},"datasets":datasets})
    org("seal-design",study,"--protocol",ROOT / "protocol.json","--baseline",baseline,"--review",review)
    org("transition",study,"--stage-id","evolve","--status","running")
    config = {"schemaVersion":1,"realization":{
        "id":"constructive-space-v1","candidateId":"c","parentSkill":str(baseline),"expectedParentTreeSha256":digest,
        "workspaceDir":str(ROOT / "workspace-c"),"outputDir":str(ROOT / "sealed-c"),
        "operator":{"operatorId":"construct-mass-and-void","instruction":"Explain joint construction of masses, open channels and junctions before detail; distinguish purpose-specific information economy from omissions. Add a concise conditional technique guide and route to it. Preserve generic mathematical helper code and all original-only/no-tracing boundaries. Do not add task identifiers, scored examples, source paths or evaluator wording.","origin":"human-reviewed-development","parentOperatorIds":[]},
        "allowedChanges":["SKILL.md","references/construction-decisions.md"],
        "developmentEvidence":[{"id":"human-technique-feedback","role":"development","path":str(evidence),"sha256":"sha256:"+sha(evidence)}],
        "trustedValidationCommands":True,"validationCommands":[{"id":"scaffold-regressions","argv":[sys.executable,"-B","scripts/test_scaffold.py"],"timeoutSeconds":60}]}}
    write(ROOT / "realize-c.json",config)
    if prepare_candidate:
        subprocess.run([sys.executable,str(REALIZER),"prepare",str(ROOT / "realize-c.json")],check=True)
    print(json.dumps({"sealed":True,"baseline_files":sum(p.is_file() for p in baseline.rglob('*')),"development_cases":6,"validation_cases":validation_cases,"maximum_new_generation_calls":6*attempts*(1+max_candidates)+2*validation_cases*attempts,"private_gate":"closed"}))


if __name__ == "__main__": main()
