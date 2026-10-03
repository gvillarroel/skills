#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Version 6.1: purpose-specific Jev Score calibration with isolated native receipts."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import statistics
import sys

from svg_excellence import REPO, encode, read, sha, write
from svg_art_direction import DIMENSIONS
from art_direction_review import verified_decisions
import svg_technique_review as previous

ROOT = REPO / "evaluations/runs/svg-technique-v6.1"
CONFIG = REPO / "projects/svg-brief-design/evaluation/technique-v6.1"
LEVELS = ["B_clear", "B_slight", "parity", "A_slight", "A_clear"]


def make_job():
    job = previous.make_job()
    concrete = {
        "silhouette_intent": ("main proportions, expressive form and visual closure", "generic or disconnected main form"),
        "composition_space": ("shaped openings, coordinated ink masses and functional footprint", "passive or arbitrary gaps, slab-like masses or unjustified area"),
        "shape_rhythm": ("controlled repetitions, taper, continuations and integrated junctions", "unrelated repeated curves, unresolved crossings or inconsistent connections"),
        "craft_finish": ("purpose-appropriate stroke substance, coherent mark variation and finished junctions", "mismatched line character or visibly unresolved mark-making"),
        "information_hierarchy": ("only relevant information, clear emphasis and economical readable placement", "unrequested information burden, missing required information or wasteful hierarchy"),
        "style_coherence": ("consistent construction embodying the declared medium and editorial use", "generic technique that conflicts with the declared use or inconsistent graphic language"),
    }
    for dimension, (strength, weakness) in concrete.items():
        old = job["questions"][dimension]
        old["type"] = "score"
        old["instructions"] += " Rate the ordered comparison from B's advantage through parity to A's advantage. This is mastery for the declared purpose, not similarity or quantity of marks."
        old["criteria"] = [
            f"B resolves {strength}; A instead has a consequential {weakness} that changes how successfully the piece works.",
            f"Both establish {strength}, but localized weaknesses in A leave B more resolved without changing the basic construction.",
            f"A and B show comparable control of {strength}; neither has a consequential or consistent localized advantage. Comparable weakness is also parity.",
            f"Both establish {strength}, but localized weaknesses in B leave A more resolved without changing the basic construction.",
            f"A resolves {strength}; B instead has a consequential {weakness} that changes how successfully the piece works.",
        ]
    job["questions"]["overall"]["criteria"] = {
        "A": "A more fully masters the requested technique and purpose; a supported artistic advantage is present.",
        "parity": "Comparable purpose-specific mastery, with no supported overall advantage.",
        "B": "B more fully masters the requested technique and purpose; a supported artistic advantage is present.",
        "unknown": "Missing or contradictory evidence prevents an overall judgment.",
    }
    job["questions"]["evidence"] = {
        "type": "choice",
        "instructions": "Are the side-specific observations sufficient to compare all six artistic dimensions? Mere differences of style or fallible visual observation do not by themselves make evidence insufficient. Missing descriptions or mutually contradictory central facts do.",
        "criteria": {
            "sufficient": "Concrete observations support comparison across the six dimensions.",
            "insufficient": "At least one dimension lacks the facts needed for a meaningful comparison, or central facts contradict each other.",
        },
    }
    job["context"] = job["context"].replace("select it", "reflect it in the ordered score and overall preference")
    job["limits"].update(concurrency=1, max_requests=1)
    return job


def aggregate(decisions, candidate_side):
    required = set(DIMENSIONS) | {"overall", "brief_A", "brief_B", "evidence"}
    if set(decisions) != required or candidate_side not in {"A", "B"}:
        raise ValueError("Incomplete decisions or invalid candidate binding")
    choices = {k: v["raw"]["choice"] for k, v in decisions.items() if k not in DIMENSIONS}
    confidence = {k: v["raw"]["confidence"] for k, v in decisions.items()}
    points = [50, 75, 90, 95, 100]
    if candidate_side == "B":
        points = list(reversed(points))
    dimensions = {}
    margins = {}
    for name in DIMENSIONS:
        raw = decisions[name]["raw"]
        probabilities = raw["probabilities"]
        if raw["type"] != "score" or set(probabilities) != {str(i) for i in range(5)}:
            raise ValueError("Invalid ordered score")
        # Native rounded probability distributions may sum to 0.99 or 1.01.
        # Normalize that rounding explicitly; never replace a rejected answer.
        total = sum(probabilities.values())
        if not .989 <= total <= 1.011:
            raise ValueError("Invalid probability mass")
        dimensions[name] = sum(points[i] * probabilities[str(i)] / total for i in range(5))
        margins[name] = sum((i - 2) / 2 * probabilities[str(i)] / total for i in range(5)) * (1 if candidate_side == "A" else -1)
    fit = choices["brief_" + candidate_side]
    if fit == "wrong":
        score = 0.0
    elif fit == "unknown" or choices["evidence"] == "insufficient":
        score = None
    else:
        score = min({"fulfilled": 100, "minor_gap": 79, "major_missing": 49}[fit], sum(DIMENSIONS[k][0] * v / 100 for k, v in dimensions.items()))
    return {
        "technique_quality": None if score is None else score / 100,
        "score_100": score,
        "dimension_expected_points": dimensions,
        "signed_technique_margin": sum(DIMENSIONS[k][0] * v / 100 for k, v in margins.items()),
        "choices": choices, "confidence": confidence,
        "overall_preference_unresolved": choices["overall"] == "unknown",
        "review_recommended": score is None or choices["overall"] == "unknown" or min(confidence.values()) < .3,
        "score_meaning": "Expected anchor-relative coded utility, not an absolute aesthetic grade or confidence interval. Probability mass is normalized for provider rounding. Pure parity=90 by convention; uncertainty across categories can lower it. Signed margin separately measures direction (-1 worse, 0 parity, +1 better). Confidence never multiplies quality. Not numerically interchangeable with v5.2's conservative category bounds.",
    }


def assert_lock():
    for path, expected in read(ROOT / "pre-inference-lock.json")["files"].items():
        if sha((REPO / path).read_bytes()) != expected:
            raise ValueError("Pre-inference drift: " + path)


def prepare():
    ROOT.mkdir(exist_ok=False)
    CONFIG.mkdir(exist_ok=False)
    write(CONFIG / "job.json", make_job())
    write(CONFIG / "use-profiles.json", previous.PROFILES)
    write(CONFIG / "generator-introductions.json", previous.INTROS)
    source = previous.ROOT / "records.jsonl"
    records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    write(ROOT / "coordinator-only.json", read(previous.ROOT / "coordinator-only.json"))
    (ROOT / "records.jsonl").write_bytes(source.read_bytes())
    for record in records:
        destination = ROOT / "inputs" / (record["id"] + ".jsonl")
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(encode(record) + b"\n")
    protocol = copy.deepcopy(read(previous.CONFIG / "protocol.json"))
    protocol.update(version="6.1.0", scoring="Six native ordered Score questions; probability-weighted category utilities [50,75,90,95,100], plus a signed directional margin. Normalize only native probability rounding. Same six weights. Subject caps retained; insufficient evidence produces no numeric reward. Categorical overall preference is separate. Confidence is separate.", new_jev_calls=36, native_probe_calls={"observer":1,"jev":1}, external_recovery="No retries in this version. Each of the 36 cases has a separate native job so an invalid envelope cannot prevent other first attempts. Report missing cases explicitly; no complete score or promotion unless all required cases are accepted.")
    protocol["reason_for_revision"] = "The six-way Choice version encountered two provider contract violations (selected option below maximum probability). Preserve it as incomplete. TypeSafe documents Score for ordered spectra. Use concrete five-level dimensional descriptions and simpler unordered overall categories, not a relaxed response validator."
    protocol["acceptance"] = {"focus_original_preferences_min":7,"focus_generated_preferences_max":0,"family_negative_margin_min":5,"mean_expected_gap_min":15,"crop_expected_below_80_min":5,"order_score_distance_max":10,"order_cases_passing_min":5,"textual_context_switch_controls_required":4,"wrong_subject_zero":True,"rough_below_75":True,"complete_coverage":36}
    protocol["documentation"] = ["https://docs.typesafe.ai/primitives/score", "https://docs.typesafe.ai/primitives/choice"]
    write(CONFIG / "protocol.json", protocol)
    # Offline planning must succeed before the inference lock is written.
    sys.path.insert(0, str(REPO / "skills/jev-batch-decisions/scripts"))
    from jev_batch import execute
    for record in records:
        execute(CONFIG / "job.json", [ROOT / "inputs" / (record["id"] + ".jsonl")], ROOT / "plans" / record["id"], dry_run=True)
    paths = [Path(__file__), Path(previous.__file__), ROOT / "records.jsonl", ROOT / "coordinator-only.json", *CONFIG.glob("*.json"), *sorted((ROOT / "inputs").glob("*.jsonl"))]
    write(ROOT / "pre-inference-lock.json", {"files":{p.relative_to(REPO).as_posix():sha(p.read_bytes()) for p in paths}})
    print("Prepared and planned 36 native one-record jobs with no retries.")


def score():
    assert_lock()
    if (ROOT / "inference-started.json").exists():
        raise ValueError("This bounded inference pass already started")
    write(ROOT / "inference-started.json", {"calls_max":36,"retries":0})
    sys.path.insert(0, str(REPO / "skills/jev-batch-decisions/scripts"))
    from jev_batch import execute
    from jev_contract import digest
    from jev_transport import http_post
    def one(source):
        destination = ROOT / "native" / source.stem
        raw = ROOT / "raw" / source.stem
        raw.mkdir(parents=True)
        def recorded(payload, key, timeout):
            status, headers, data = http_post(payload, key, timeout)
            if status == 200:
                (raw / (digest(payload) + ".json")).write_bytes(data)
            return status, headers, data
        try:
            execute(CONFIG / "job.json", [source], destination, post=recorded)
            return {"id":source.stem,"status":"complete"}
        except Exception:
            # Native reports already contain sanitized error descriptions.
            return {"id":source.stem,"status":"failed","report":str(destination / "report.json")}
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(one, sorted((ROOT / "inputs").glob("*.jsonl"))))
    write(ROOT / "execution.json", results)
    print(json.dumps({"complete":sum(r["status"]=="complete" for r in results),"failed":sum(r["status"]!="complete" for r in results)}))


def report():
    assert_lock()
    native = {}; models = set(); failed = []; metrics = []
    for source in sorted((ROOT / "inputs").glob("*.jsonl")):
        destination = ROOT / "native" / source.stem
        receipt = read(destination / "report.json")
        metrics.append(receipt["metrics"])
        if receipt["status"] != "complete":
            failed.append({"id":source.stem,"error":receipt.get("error")})
            continue
        decisions, versions = verified_decisions(destination, source)
        native.update(decisions); models.update(versions)
    coordinator = read(ROOT / "coordinator-only.json")
    rows = []
    for pair in coordinator["pairs"]:
        if pair["id"] not in native:
            continue
        row = pair | aggregate(native[pair["id"]]["decisions"], pair["candidate_side"])
        other = "B" if pair["candidate_side"] == "A" else "A"
        rows.append(row | {"reference_preferred":row["choices"]["overall"]==other,"candidate_preferred":row["choices"]["overall"]==pair["candidate_side"]})
    generated = [r for r in rows if r["kind"] == "generated"]
    scored = [r for r in generated if r["score_100"] is not None]
    by_candidate = {r["candidate_id"]:r for r in generated}
    focus = [r for r in generated if r["id"] in coordinator["focus_ids"]]
    families = [{"task":task,"n":sum(r["task"]==task for r in generated),"mean_expected_points":statistics.mean(r["score_100"] for r in scored if r["task"]==task) if any(r["task"]==task for r in scored) else None,"mean_signed_margin":statistics.mean(r["signed_technique_margin"] for r in generated if r["task"]==task)} for task in sorted({r["task"] for r in generated})]
    stability = [{"task":r["task"],"distance":abs(r["score_100"]-by_candidate[r["candidate_id"]]["score_100"]) if r["score_100"] is not None and by_candidate[r["candidate_id"]]["score_100"] is not None else None} for r in rows if r["kind"]=="order_control" and r["candidate_id"] in by_candidate]
    controls = [c | {"choice":native[c["id"]]["decisions"]["overall"]["raw"]["choice"],"passed":native[c["id"]]["decisions"]["overall"]["raw"]["choice"]==c["expected_side"]} for c in coordinator["controls"] if c["id"] in native]
    synthetic = {r["candidate_id"]:r for r in rows if r["kind"]=="synthetic"}
    registry = read(REPO / "evaluations/runs/svg-art-v4/prepared/coordinator-only.json")
    syn = {r["name"]:synthetic[r["id"]]["score_100"] for r in registry if r["id"] in synthetic}
    mean = statistics.mean(r["score_100"] for r in scored) if scored else None
    checks = {
        "complete_coverage":len(native)==36 and len(scored)==18,
        "focus_original_preferences":sum(r["reference_preferred"] for r in focus)>=7,
        "no_focus_generated_preference":len(focus)==8 and not any(r["candidate_preferred"] for r in focus),
        "five_families_negative_margin":sum(r["mean_signed_margin"]<0 for r in families)>=5,
        "mean_expected_gap":mean is not None and 90-mean>=15,
        "crop_sensitivity":sum(r["score_100"] is not None and r["score_100"]<80 for r in rows if r["kind"]=="crop_control")>=5,
        "order_stability":sum(r["distance"] is not None and r["distance"]<=10 for r in stability)>=5,
        "context_switch_controls":len(controls)==4 and all(c["passed"] for c in controls),
        "wrong_subject":syn.get("wrong-subject")==0,
        "rough":syn.get("minimal-rough") is not None and syn["minimal-rough"]<75,
    }
    accounting = {key:sum(m.get(key,0) for m in metrics) for key in ("http_attempts","accepted_calls","reported_input_tokens","reported_output_tokens","reported_cost_usd","cost_unreported_attempts")}
    # Retain exact native metric keys too; API cost is not an estimate.
    result = {"version":"6.1.0","passed":all(checks.values()),"checks":checks,"accepted_cases":len(native),"failed_cases":failed,"generated_scored":len(scored),"mean_expected_points_available_cases":mean,"reference_preferred_of_available":sum(r["reference_preferred"] for r in generated),"focus_reference_preferred":sum(r["reference_preferred"] for r in focus),"focus_available":len(focus),"families":families,"stability":stability,"textual_controls":controls,"synthetic_scores":syn,"observed_models":sorted(models),"accounting":accounting,"native_metrics":metrics,"records":rows}
    write(ROOT / "results.json", result)
    print(json.dumps({k:v for k,v in result.items() if k not in {"records","native_metrics"}}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare","score","report"])
    args = parser.parse_args()
    {"prepare":prepare,"score":score,"report":report}[args.mode]()
