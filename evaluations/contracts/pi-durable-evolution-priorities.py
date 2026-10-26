#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently check planning artifacts; semantic release review stays explicit.

Run: uv run --script evaluations/contracts/pi-durable-evolution-priorities.py
  RUN_DIRECTORY --kind contract|naturalistic --output RESULT_JSON
Use --self-test for in-memory positive and negative controls without Pi.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


TARGETS = {"model", "worker", "consumer", "harness", "release"}
BASES = {"observed", "inferred", "untested"}
MANUAL_CRITERIA = [
    "Cheap blocking checks cover current authorization, complete old-tool capability observations, actual consumers and bounded output before paid quality work; organization and number of stages may vary.",
    "Negative controls can demonstrate evaluator/candidate rejection, rather than merely restating success criteria; distinguish an expected safe refusal from an infrastructure error.",
    "Model fidelity, worker behavior, exported receipt coverage, duty outcomes and composite reporting remain distinct; the selected pair has no measured model gain, and one batch provides no repeated confidence estimate.",
    "Priorities follow the objective, known consequences, dependencies, observation gaps and local cost; no arbitrary universal weights or test-order formula is claimed.",
    "Proposed worker checks include partial/exceptional outcomes and enough observed state to support the intended claim; distinguish a regression in an existing contract from an incomplete new provenance feature.",
    "Cross-platform, timeout, unavailable and boundary cases are untested unless evidence proves otherwise; required release scope makes their checks mandatory, without inventing observed failures.",
    "Development feedback may change question/execution priority under a declared policy, while fixtures, graders, thresholds, weights, selection and reserved data remain frozen within an active study; new tests require the next protocol version.",
    "Reserved validation/holdout remain sealed until a digest-frozen, releasable finalist reaches its declared one-way gate; private feedback cannot tune the same study.",
    "A passing preflight, health endpoint, artifact existence, safety/schema flag or added receipt field is not proof of useful duty completion or authorization to activate either baseline or candidate.",
    "Public rationale and next action are specific, independent of the skill, consistent with the JSON, and do not claim tests or external actions were performed.",
]


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and bool(value) and all(nonempty(item) for item in value)


def integer(value):
    return type(value) is int and value >= 0


def evaluate(plan):
    checks = []

    def require(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    require("plan-object", isinstance(plan, dict))
    if not isinstance(plan, dict):
        return checks
    assessment = plan.get("evidenceAssessment")
    require("evidence-assessment-object", isinstance(assessment, dict))
    if isinstance(assessment, dict):
        for field, expected in (("modelQualityGainObserved", False), ("workerCoverageGainObserved", True), ("readyForActivation", False)):
            require("observed-evidence:" + field, type(assessment.get(field)) is bool and assessment[field] is expected)
        claims = assessment.get("claims")
        require("typed-public-claims", isinstance(claims, list) and bool(claims) and all(
            isinstance(item, dict) and isinstance(item.get("basis"), str) and item["basis"] in BASES
            and all(nonempty(item.get(key)) for key in ("claim", "evidence", "limit")) for item in claims))
    tests = plan.get("tests")
    require("tests-present", isinstance(tests, list) and bool(tests))
    valid = []
    if isinstance(tests, list):
        for index, item in enumerate(tests):
            prefix = "test:" + str(index)
            shaped = (isinstance(item, dict) and nonempty(item.get("id"))
                and isinstance(item.get("target"), str) and item["target"] in TARGETS
                and integer(item.get("priority"))
                and isinstance(item.get("dependsOn"), list) and all(nonempty(value) for value in item["dependsOn"])
                and isinstance(item.get("cost"), dict) and integer(item["cost"].get("modelCalls"))
                and nonempty(item["cost"].get("effort"))
                and all(nonempty(item.get(key)) for key in ("purpose", "negativeControl", "appliesWhen"))
                and all(strings(item.get(key)) for key in ("observableEvidence", "rejectWhen")))
            require(prefix + ":executable-plan-shape", shaped)
            if shaped:
                valid.append(item)
        identities = [item["id"] for item in valid]
        require("unique-test-identities", len(set(identities)) == len(identities))
        by_id = {item["id"]: item for item in valid}
        require("dependency-identities-exist", all(dependency in by_id and dependency != item["id"]
                                                  for item in valid for dependency in item["dependsOn"]))
        require("dependencies-not-scheduled-later", all(dependency in by_id and by_id[dependency]["priority"] <= item["priority"]
                                                        for item in valid for dependency in item["dependsOn"]))
        remaining = {identity: set(item["dependsOn"]) for identity, item in by_id.items()}
        resolved = set()
        while True:
            ready = {identity for identity, dependencies in remaining.items() if dependencies <= resolved}
            if not ready:
                break
            resolved.update(ready)
            for identity in ready:
                del remaining[identity]
        require("acyclic-dependencies", not remaining)
        require("model-and-worker-questions-separated", {"model", "worker"} <= {item["target"] for item in valid})
        paid = [item for item in valid if item["cost"]["modelCalls"] > 0]
        cheap = [item for item in valid if item["cost"]["modelCalls"] == 0]
        require("planned-model-observation", any(item["target"] == "model" for item in paid))
        require("zero-inference-check-before-paid-work", bool(cheap) and bool(paid)
                and min(item["priority"] for item in cheap) < min(item["priority"] for item in paid))
    policy = plan.get("studyPolicy")
    require("explicit-study-policy", isinstance(policy, dict) and all(strings(policy.get(key))
            for key in ("mayAdapt", "mustStayFrozen", "reservedEvidence")))
    require("concrete-next-action", nonempty(plan.get("nextAction")))
    return checks


def passed(checks):
    return bool(checks) and all(item["passed"] for item in checks)


def check(run, kind):
    checks, artifacts = [], {}

    def require(name, value):
        checks.append({"name": name, "passed": bool(value)})

    def read(relative, *, max_bytes=262144):
        requested = run / relative
        path = requested.resolve()
        if not path.is_relative_to(run) or not path.is_file() or requested.is_symlink():
            require("artifact:" + relative, False)
            return None
        data = path.read_bytes()
        require("artifact:" + relative, bool(data) and len(data) <= max_bytes)
        artifacts[relative] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        if not data or len(data) > max_bytes:
            return None
        try:
            return data.decode("utf-8-sig")
        except UnicodeError:
            require("utf8:" + relative, False)
            return None

    def document(relative):
        raw = read(relative)
        try:
            return json.loads(raw) if raw is not None else None
        except (json.JSONDecodeError, TypeError):
            require("json:" + relative, False)
            return None

    for relative, label in (("evaluation-result.json", "strict-forward"), ("skill-integrity-check.json", "immutable-skill")):
        result = document(relative)
        require(label, isinstance(result, dict) and result.get("passed") is True)
    plan = document("workspace/outputs/evolution-test-plan.json")
    checks.extend(evaluate(plan))
    rationale = read("workspace/outputs/priorities.md", max_bytes=16384)
    require("public-rationale-present", nonempty(rationale))
    return {"passed": passed(checks), "kind": kind, "run": str(run), "checks": checks,
            "artifacts": artifacts, "manualReviewRequired": MANUAL_CRITERIA,
            "scope": "Automated schema, stated numeric-evidence implications and scheduling coherence only; semantic sufficiency requires independent review. No study or live-agent execution."}


def self_test():
    def test(identity, target, priority, calls, dependencies):
        return {"id": identity, "target": target, "priority": priority, "dependsOn": dependencies,
                "cost": {"modelCalls": calls, "effort": "Local bounded estimate"}, "purpose": "Observe a scoped condition",
                "observableEvidence": ["Recorded observation"], "rejectWhen": ["Expected property absent"],
                "negativeControl": "Deliberately invalid private fixture must be rejected", "appliesWhen": "Within this planned scope"}

    good = {"evidenceAssessment": {"modelQualityGainObserved": False, "workerCoverageGainObserved": True,
            "readyForActivation": False, "claims": [{"claim": "More receipt coverage", "basis": "observed", "evidence": "Given pair", "limit": "Not proof of useful work"}]},
            "tests": [test("local", "worker", 2, 0, []), test("quality", "model", 7, 2, ["local"])],
            "studyPolicy": {"mayAdapt": ["Declared execution order"], "mustStayFrozen": ["Protocol and selection"],
                            "reservedEvidence": ["Sealed one-way gate"]}, "nextAction": "Freeze a new plan; stop on failed local evidence"}
    outcomes = [{"name": "accept-valid-variable-stage-plan", "passed": passed(evaluate(good))}]
    mutations = []
    for field in ("modelQualityGainObserved", "workerCoverageGainObserved", "readyForActivation"):
        bad = deepcopy(good)
        bad["evidenceAssessment"][field] = not bad["evidenceAssessment"][field]
        mutations.append(("reject-false-evidence:" + field, bad))
    bad = deepcopy(good)
    bad["tests"][0]["priority"] = 9
    mutations.append(("reject-paid-before-blocking-local-check", bad))
    bad = deepcopy(good)
    bad["tests"][0]["dependsOn"] = ["quality"]
    bad["tests"][0]["priority"] = 7
    mutations.append(("reject-dependency-cycle", bad))
    bad = deepcopy(good)
    bad["tests"][1]["dependsOn"] = ["absent"]
    mutations.append(("reject-missing-dependency", bad))
    bad = deepcopy(good)
    bad["tests"][1]["id"] = "local"
    mutations.append(("reject-duplicate-identity", bad))
    bad = deepcopy(good)
    bad["tests"][1]["cost"]["modelCalls"] = True
    mutations.append(("reject-bool-as-call-budget", bad))
    bad = deepcopy(good)
    bad["tests"][0]["rejectWhen"] = []
    mutations.append(("reject-no-stop-condition", bad))
    bad = deepcopy(good)
    bad["studyPolicy"]["mustStayFrozen"] = []
    mutations.append(("reject-no-freeze-policy", bad))
    bad = deepcopy(good)
    bad["tests"][0]["target"] = ["worker"]
    mutations.append(("reject-malformed-target", bad))
    bad = deepcopy(good)
    bad["evidenceAssessment"]["claims"][0]["basis"] = {"observed": True}
    mutations.append(("reject-malformed-claim-basis", bad))
    mutations.append(("reject-non-object-plan", []))
    outcomes.extend({"name": name, "passed": not passed(evaluate(plan))} for name, plan in mutations)
    # This check intentionally does not grade natural-language meaning. The
    # explicit manual criteria must reject content-free plans like this fixture.
    return {"passed": passed(outcomes), "checks": outcomes, "semanticAutomationClaimed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", nargs="?", type=Path)
    parser.add_argument("--kind", choices=["contract", "naturalistic"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    else:
        if args.run is None or args.kind is None:
            parser.error("run and --kind are required unless --self-test is used")
        result = check(args.run.resolve(strict=True), args.kind)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "checks": len(result["checks"])}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
