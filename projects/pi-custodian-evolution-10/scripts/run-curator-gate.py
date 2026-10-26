#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Freeze a ten-attempt selection and open authorized one-way native gates."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import sys

AREA = Path(__file__).resolve().parents[1]
ARTIFACTS = AREA / "artifacts"
DRIVER_PATH = Path(__file__).with_name("run-development.py")
SPEC = importlib.util.spec_from_file_location("curator_development_driver", DRIVER_PATH)
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)
ALLOWED = set(driver.ALLOWED)


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seal(value):
    payload = {key: item for key, item in value.items() if key != "digest"}
    return {**payload, "digest": digest(payload)}


def sealed(path):
    value = read(path)
    if not isinstance(value, dict) or value.get("digest") != digest({key: item for key, item in value.items() if key != "digest"}):
        raise ValueError("Sealed curator/native artifact changed.")
    return value


def write(path, value, exclusive=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def scoped_output(path):
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(ARTIFACTS.resolve()) or resolved == ARTIFACTS.resolve():
        raise ValueError("Curator output must remain inside this study's private artifacts.")
    return resolved


def local(project, path):
    name = Path(path)
    if name.is_absolute() or ".." in name.parts or "\\" in str(path) or ":" in str(path):
        raise ValueError("Native study paths must be project-relative.")
    target = project / name
    if target.is_symlink() or not target.resolve().is_relative_to(project):
        raise ValueError("Native study path escaped the owned project.")
    return target


def finite_score(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def checked_context(args):
    project = args.project.resolve(strict=True)
    output = scoped_output(args.output_dir)
    request = sealed(args.request_file)
    if request.get("id") != "custodian-evo10-development-20261025" or set(request.get("allowedPaths", [])) != ALLOWED:
        raise ValueError("Unexpected immutable development request/scope.")
    config = local(project, args.config)
    driver.source_guard(project, request, config)
    cfg = read(config)
    if cfg.get("provider", {}).get("model") != driver.MODEL or cfg["provider"].get("thinkingLevel") != "medium" or not cfg["provider"].get("catalogFile"):
        raise ValueError("Use the frozen exact Sol 6.1/medium configuration.")
    commitments = read(args.commitments)
    if commitments.get("selection") != {"decisionWeight": 0.5, "workerReceiptWeight": 0.5,
                                       "minimumPairedImprovement": 0.01,
                                       "tieBreak": ["candidate-score-descending", "patch-digest-lexicographic"]}:
        raise ValueError("Frozen selection protocol changed.")
    if request.get("minimumImprovement") != 0.01:
        raise ValueError("Native threshold differs from the preregistered threshold.")
    development_cases = [name for name in request["fixturePaths"] if Path(name).name == "decision-cases.json"]
    if len(development_cases) != 1:
        raise ValueError("Expected one exact semantic development case file.")
    case_path = development_cases[0]
    if sha(local(project, case_path)) != commitments["development"]["sha256"]:
        raise ValueError("Frozen development case bytes changed.")
    protocol = args.commitments.resolve().parent / "protocol.md"
    if sha(protocol) != commitments["evaluatorFiles"]["protocol.md"]:
        raise ValueError("Frozen public protocol changed.")
    driver_freeze = read(args.commitments.resolve().parents[1] / "artifacts/driver-freeze.json")
    if sha(DRIVER_PATH) != driver_freeze["driverSha256"]:
        raise ValueError("Development driver differs from its preregistered bytes.")
    return project, output, request, config, commitments, case_path


def check_native_evaluation(evaluation, proposal, request, patch):
    if evaluation.get("proposalId") != proposal.get("id") or evaluation.get("proposalDigest") != proposal.get("digest") or evaluation.get("requestDigest") != request.get("digest"):
        raise ValueError("Native evaluation/proposal/request identity mismatch.")
    if proposal.get("requestId") != request["id"] or proposal.get("requestDigest") != request["digest"] or driver.patch_digest(proposal.get("changes", [])) != patch:
        raise ValueError("Native proposal differs from the frozen patch.")
    if evaluation.get("source") != request["source"] or evaluation.get("frozenVerifier") != request["frozenVerifier"]:
        raise ValueError("Native evaluation provenance differs from its exact request.")
    baseline = evaluation.get("baseline", {}).get("verification")
    candidate = evaluation.get("candidate", {}).get("verification")
    passed = bool(baseline and candidate and baseline.get("passed") is True and candidate.get("passed") is True)
    if baseline and candidate:
        for side in (baseline, candidate):
            if not finite_score(side.get("score")) or not isinstance(side.get("cases"), list) or not side["cases"]:
                raise ValueError("Native score/case evidence is invalid.")
            if len({case.get("id") for case in side["cases"]}) != len(side["cases"]):
                raise ValueError("Native evaluation contains duplicate cases.")
            passed = passed and all(case.get("passed") is True for case in side["cases"])
        passed = passed and sorted(case["id"] for case in baseline["cases"]) == sorted(case["id"] for case in candidate["cases"])
        passed = passed and candidate["score"] - baseline["score"] + sys.float_info.epsilon >= request["minimumImprovement"]
    if evaluation.get("passed") is not passed:
        raise ValueError("Native measured pass disagrees with frozen hard/threshold checks.")
    return passed


def candidate_artifacts(folder, record, request):
    proposal = sealed(folder / "proposal.json")
    evaluation = sealed(folder / "evaluation.json")
    candidate_path = Path(record["candidatePath"]).resolve(strict=True)
    if candidate_path != (folder / "candidate.json").resolve():
        raise ValueError("A selected candidate path leaves its exact iteration folder.")
    candidate = read(candidate_path)
    patch = driver.patch_digest(candidate["changes"])
    if patch != record.get("patchDigest") or patch != driver.patch_digest(proposal["changes"]):
        raise ValueError("Candidate/native patch digests differ.")
    if record.get("proposalId") != proposal.get("id") or record.get("evaluationDigest") != evaluation.get("digest"):
        raise ValueError("Development ledger native identity drift.")
    if not check_native_evaluation(evaluation, proposal, request, patch):
        raise ValueError("A purported qualified development evaluation did not pass.")
    if evaluation["candidate"]["verification"]["score"] != record.get("candidateScore"):
        raise ValueError("Selected score differs from its sealed native evaluation.")
    return candidate_path, candidate, proposal, evaluation


def completed_attempts(args, request):
    directory = args.development_dir.resolve(strict=True)
    if (directory / "development-driver.lock").exists():
        raise ValueError("Development driver is still active; gates are closed.")
    ledger_path = directory / "development-ledger.jsonl"
    events = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(event.get("event") not in {"started", "finished"} for event in events):
        raise ValueError("Unexpected development ledger event.")
    starts = [event for event in events if event["event"] == "started"]
    finished = [event for event in events if event["event"] == "finished"]
    if len(starts) != 10 or len(finished) != 10 or {event.get("slot") for event in starts} != set(range(1, 11)) or {event.get("slot") for event in finished} != set(range(1, 11)):
        raise ValueError("Exactly ten unique started and completed slots are required.")
    for event in starts:
        if event.get("baselineRequestDigest") != request["digest"] or event.get("maximumStartedSlots") != 10:
            raise ValueError("A development slot used a different request or budget.")
        start_index = events.index(event)
        end_event = next(item for item in finished if item["slot"] == event["slot"])
        if events.index(end_event) <= start_index:
            raise ValueError("A completion predates its started attempt.")
    summary_path = directory / "development-summary.json"
    summary = read(summary_path)
    if summary.get("startedSlots") != 10 or summary.get("finishedSlots") != 10 or summary.get("completedRequestedSlots") is not True or summary.get("iterations") != finished:
        raise ValueError("Completed ledger and final development summary disagree.")
    qualified = [event for event in finished if event.get("qualified") is True]
    if any(not finite_score(event.get("candidateScore")) or not isinstance(event.get("patchDigest"), str) for event in qualified):
        raise ValueError("A qualified development score is invalid.")
    for event in qualified:
        candidate_artifacts(directory / "iterations" / f"i{event['slot']:02}", event, request)
    ordered = sorted(qualified, key=lambda event: (-event["candidateScore"], event["patchDigest"]))
    winner = ordered[0] if ordered else None
    if bool(winner) != bool(summary.get("best")) or winner and any(summary["best"].get(key) != winner.get(key) for key in ("slot", "candidateScore", "patchDigest", "proposalId", "evaluationDigest")):
        raise ValueError("Development selection disagrees with the frozen scalar/digest rule.")
    return directory, ledger_path, summary_path, finished, winner


def freeze_selection(args):
    project, output, request, config, commitments, case_path = checked_context(args)
    directory, ledger, summary, finished, winner = completed_attempts(args, request)
    selected = None
    if winner:
        candidate_path, candidate, proposal, evaluation = candidate_artifacts(directory / "iterations" / f"i{winner['slot']:02}", winner, request)
        source = {item["path"]: item["sha256"] for item in request["source"]}
        for change in candidate["changes"]:
            if change["path"] not in ALLOWED or change.get("beforeHash") != source[change["path"]]:
                raise ValueError("Selected patch path/preimage is outside the frozen request.")
        baseline = {name: (project / name).read_bytes().decode("utf-8") for name in driver.ALLOWED}
        changed = {**baseline, **{change["path"]: change["content"] for change in candidate["changes"]}}
        driver.scope_guard(baseline, changed)
        selected = {"slot": winner["slot"], "candidatePath": str(candidate_path), "candidateSha256": sha(candidate_path),
                    "patchDigest": winner["patchDigest"], "proposalId": proposal["id"],
                    "evaluationDigest": evaluation["digest"], "candidateScore": winner["candidateScore"]}
    selection = seal({"version": 1, "kind": "curator-selection", "at": now(), "project": str(project),
                      "configPath": str(config), "requestId": request["id"], "requestDigest": request["digest"],
                      "requestFileSha256": sha(args.request_file), "ledgerSha256": sha(ledger),
                      "summarySha256": sha(summary), "commitmentsSha256": sha(args.commitments),
                      "sourceDigest": digest(request["source"]), "commonAssetsDigest": digest(request["frozenVerifier"]),
                      "driverSha256": sha(DRIVER_PATH), "curatorRunnerSha256": sha(Path(__file__)),
                      "startedSlots": 10, "completedSlots": 10, "winner": selected,
                      "retainedBaseline": selected is None, "selectionRule": "highest qualified candidate score then patch digest",
                      "reservedCaseCounts": {"validation": 4, "holdout": 4}, "automaticActivation": False})
    write(output / "selection.json", selection)
    return {"phase": "baseline-retained" if not selected else "finalist-frozen", "selectionDigest": selection["digest"],
            "patchDigest": selected["patchDigest"] if selected else None, "automaticActivation": False}


def checked_selection(args, context):
    project, output, request, config, commitments, case_path = context
    selection = sealed(output / "selection.json")
    expected = {"project": str(project), "configPath": str(config), "requestId": request["id"],
                "requestDigest": request["digest"], "requestFileSha256": sha(args.request_file),
                "commitmentsSha256": sha(args.commitments), "sourceDigest": digest(request["source"]),
                "commonAssetsDigest": digest(request["frozenVerifier"]), "driverSha256": sha(DRIVER_PATH),
                "curatorRunnerSha256": sha(Path(__file__))}
    if any(selection.get(key) != value for key, value in expected.items()):
        raise ValueError("Frozen selection provenance changed.")
    directory, ledger, summary, finished, winner = completed_attempts(args, request)
    if sha(ledger) != selection["ledgerSha256"] or sha(summary) != selection["summarySha256"] or not winner or not selection.get("winner"):
        raise ValueError("Development changed after selection or no qualified finalist exists.")
    selected = selection["winner"]
    candidate_path, candidate, proposal, evaluation = candidate_artifacts(directory / "iterations" / f"i{winner['slot']:02}", winner, request)
    if sha(candidate_path) != selected["candidateSha256"] or driver.patch_digest(candidate["changes"]) != selected["patchDigest"]:
        raise ValueError("Finalist bytes changed after freeze.")
    return selection, candidate


def native(args, project, config, directory, action, *extra):
    node = shutil.which("node") or "node"
    argv = [node, str(project / "dist/src/evolve-cli.js"), action, "--config", str(config), *map(str, extra)]
    process = driver.run_command(argv, project, 800 if action == "evaluate" else 90, max_bytes=8 * 1024 * 1024)
    write(directory / (action + ".process.json"), {key: process[key] for key in ("returnCode", "timedOut", "overflow", "durationSeconds")})
    if process["returnCode"] or process["timedOut"] or process["overflow"]:
        (directory / (action + ".stderr.redacted.txt")).write_text(driver.redact(process["stderr"])[:10000], encoding="utf-8")
        raise RuntimeError("Native curator stage failed; release is consumed and cannot be retried.")
    value = json.loads(process["stdout"])
    write(directory / (action + ".json"), value)
    if value.get("digest") != digest({key: item for key, item in value.items() if key != "digest"}):
        raise ValueError("Native gate artifact seal is invalid.")
    return value


def open_gate(args):
    context = checked_context(args)
    project, output, request, config, commitments, case_path = context
    selection, candidate = checked_selection(args, context)
    stage = args.command
    directory = output / stage
    if not args.authorize_open:
        return {"phase": "awaiting-explicit-root-authorization", "stage": stage, "released": False, "automaticActivation": False}
    if stage == "holdout":
        previous = sealed(output / "validation" / "result.json")
        if previous.get("passed") is not True or previous.get("selectionDigest") != selection["digest"] or previous.get("patchDigest") != selection["winner"]["patchDigest"]:
            raise ValueError("Holdout requires this exact finalist's passed one-way validation.")
    stage_case = str(Path(case_path).parent.parent / stage / Path(case_path).name).replace("\\", "/")
    stage_hash = sha(local(project, stage_case))
    expected_hash = commitments[stage + "Commitment"]["sha256"]
    if stage_hash != expected_hash or stage_hash == commitments["development"]["sha256"]:
        raise ValueError("Reserved semantic case bytes do not match their disjoint commitment.")
    if commitments["validationCommitment"]["sha256"] == commitments["holdoutCommitment"]["sha256"]:
        raise ValueError("Validation and holdout semantic cases must be distinct.")
    fixtures = [name for name in request["fixturePaths"] if name != case_path] + [stage_case]
    release = seal({"version": 1, "stage": stage, "at": now(), "selectionDigest": selection["digest"],
                    "patchDigest": selection["winner"]["patchDigest"], "reservedCasesSha256": stage_hash,
                    "sharedCommonHelpers": True, "automaticActivation": False})
    # Exclusive marker is persisted before ANY gate-native/model call. Failure,
    # interruption, or a previously successful release cannot be rerun.
    write(directory / "released.json", release)
    try:
        request_input = {key: request[key] for key in ("agentId", "goal", "allowedPaths", "minimumImprovement", "timeoutMs")}
        request_input.update(id=request["id"].replace("-development-", "-" + stage + "-"),
                             verifierPath=request["verifierPath"], fixturePaths=fixtures)
        input_path = directory / "request-input.json"
        write(input_path, request_input)
        gate_request = native(args, project, config, directory, "request", "--input", input_path)
        if gate_request["source"] != request["source"] or gate_request["configDigest"] != request["configDigest"] or set(gate_request["allowedPaths"]) != ALLOWED:
            raise ValueError("Gate request does not retain the immutable baseline/config/scope.")
        hashes = {item["path"]: item["sha256"] for item in request["frozenVerifier"] if item["path"] != case_path}
        hashes[stage_case] = stage_hash
        if {item["path"]: item["sha256"] for item in gate_request["frozenVerifier"]} != hashes:
            raise ValueError("Native gate common assets/cases differ from frozen inputs.")
        adapted = {**candidate, "requestId": gate_request["id"], "evidenceIds": [item["id"] for item in gate_request["evidence"]]}
        if driver.patch_digest(adapted["changes"]) != selection["winner"]["patchDigest"]:
            raise ValueError("Adapted gate proposal changed finalist bytes.")
        candidate_path = directory / "candidate.json"
        write(candidate_path, adapted)
        proposal = native(args, project, config, directory, "propose", "--request", gate_request["id"], "--input", candidate_path)
        if driver.patch_digest(proposal["changes"]) != selection["winner"]["patchDigest"]:
            raise ValueError("Imported native gate proposal changed finalist bytes.")
        evaluation = native(args, project, config, directory, "evaluate", "--proposal", proposal["id"])
        passed = check_native_evaluation(evaluation, proposal, gate_request, selection["winner"]["patchDigest"])
        baseline = evaluation.get("baseline", {}).get("verification") or {}
        changed = evaluation.get("candidate", {}).get("verification") or {}
        result = seal({"version": 1, "stage": stage, "at": now(), "selectionDigest": selection["digest"],
                       "patchDigest": selection["winner"]["patchDigest"], "requestId": gate_request["id"],
                       "requestDigest": gate_request["digest"], "proposalId": proposal["id"],
                       "proposalDigest": proposal["digest"], "evaluationDigest": evaluation["digest"],
                       "passed": passed, "baselineScore": baseline.get("score"), "candidateScore": changed.get("score"),
                       "baselineComponents": {key: baseline.get(key) for key in ("decisionScore", "workerScore")},
                       "candidateComponents": {key: changed.get(key) for key in ("decisionScore", "workerScore")},
                       "threshold": request["minimumImprovement"], "oneFreshNoToolBatchPerArm": True,
                       "sharedBatchContext": True, "workerFixturesReusedNotReserved": True,
                       "reservedSemanticCaseCount": 4, "automaticActivation": False,
                       "qualifiedForSeparatePromotionReview": stage == "holdout" and passed})
        write(directory / "result.json", result)
        return result
    except BaseException as error:
        failure = seal({"version": 1, "stage": stage, "at": now(), "selectionDigest": selection["digest"],
                        "patchDigest": selection["winner"]["patchDigest"], "passed": False,
                        "errorCategory": type(error).__name__, "message": driver.redact(str(error))[:1500],
                        "releaseConsumed": True, "baselineRetained": True, "automaticActivation": False})
        write(directory / "failure.json", failure)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["freeze", "validation", "holdout"])
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--config", default="config.evo10.json")
    parser.add_argument("--request-file", type=Path, default=ARTIFACTS / "development-request.json")
    parser.add_argument("--development-dir", type=Path, default=ARTIFACTS / "development-run")
    parser.add_argument("--commitments", type=Path, default=AREA / "evaluation-controls/benchmark-commitments.json")
    parser.add_argument("--output-dir", type=Path, default=ARTIFACTS / "curator-gates")
    parser.add_argument("--authorize-open", action="store_true")
    args = parser.parse_args()
    result = freeze_selection(args) if args.command == "freeze" else open_gate(args)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"opened": False, "errorCategory": type(error).__name__,
                          "error": driver.redact(str(error))[:1500], "automaticActivation": False}), file=sys.stderr)
        raise SystemExit(1)
