"""Aggregate exact decisions and run bounded carrier and identity replays."""

from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path

from follow_up import adapted_observations, unnamed_basis
from study import ROOT, digest, encode, load, normalize_review, output_object, score, store


def keyed_scores(run, batch, mode):
    return load(ROOT / run / f"{batch}-{mode}-scores.json")


def repair_closed_questions(reply):
    repaired = deepcopy(reply)
    changed = 0
    for row in repaired["decisions"]:
        if set(row) == {"id", "verdict", "basis", "reason"} and row["verdict"] in {"supported", "contradicted"}:
            row["question"] = ""
            changed += 1
    return repaired, changed


def metrics(scores):
    return {
        "total": len(scores),
        "exact": sum(row["complete"] for row in scores.values()),
        "verdict": sum(row["verdict_correct"] for row in scores.values()),
        "exact_by_expected": {
            label: [sum(row["complete"] for row in rows), len(rows)]
            for label in ("supported", "contradicted", "unresolved")
            if (rows := [row for row in scores.values() if row["expected"]["verdict"] == label])
        },
        "false_supports": sum(
            row["actual"]["verdict"] == "supported" and row["expected"]["verdict"] != "supported"
            for row in scores.values()
        ),
    }


def key(row):
    actual = row["actual"]
    return actual["verdict"], actual["witnesses"]


def agreement(left, right):
    if set(left) != set(right):
        raise ValueError("Repeat decision IDs differ")
    return [sum(key(left[i]) == key(right[i]) for i in left), len(left)]


def try_repair(run, batch):
    path = ROOT / run
    receipt = load(path / f"{batch}-restricted.receipt.json")
    reply, changes = repair_closed_questions(output_object(receipt["output"]))
    observations = load(path / f"{batch}-observe-compiled.json")["packets"]
    actor = load(path / f"{batch}-actor.json")
    result = normalize_review(reply, actor, observations, enforce_identity=True)
    scores = score(result, load(path / f"{batch}-oracle.json"))
    return {"closed_questions_defaulted": changes, "metrics": metrics(scores), "scores": scores}


def guard_results(run, batch, inject):
    path = ROOT / run
    actor = load(path / f"{batch}-actor.json")
    compiled = adapted_observations(path, batch, "observe", actor)["packets"]
    oracle = load(path / f"{batch}-oracle.json")
    existing = keyed_scores(run, batch, "direct")
    target_packets = {"power-automate-isolated", "python-context-manager-body"}
    revised, challenged, guarded = {}, [], []
    for packet in actor:
        observations = compiled[packet["id"]]["observations"]
        for claim in packet["claims"]:
            case_id = claim["id"]
            row = existing[case_id]
            actual = dict(row["actual"])
            if inject and row["packet"] in target_packets and row["expected"]["verdict"] == "unresolved":
                actual.update(verdict="supported", witnesses=[packet["windows"][0]["id"]], question="")
                challenged.append(case_id)
            if (claim["identity"] == "named" and actual["verdict"] in {"supported", "contradicted"}
                and unnamed_basis(actual["witnesses"], observations)):
                actual.update(
                    verdict="unresolved", witnesses=[], identity_downgrade=True,
                    reason="The selected source observations leave the subject unnamed.",
                    question="Which source passage establishes the identity of the named subject?",
                )
                guarded.append(case_id)
            revised[case_id] = actual
    return {
        "challenged": challenged, "guarded": guarded, "metrics": metrics(score(revised, oracle)),
        "before": metrics(existing),
    }


def main(output):
    initial = {
        mode: {batch: metrics(keyed_scores("run-01", batch, mode)) for batch in ("a", "b")}
        for mode in ("direct", "advisory", "restricted", "direct-repeat", "restricted-repeat")
    }
    variants = {}
    for name, run, batch, mode in (
        ("format-a-repeat", "run-02-format-a-repeat", "a", "restricted"),
        ("format-b-advisory", "run-02-format-b", "b", "advisory"),
        ("positions-direct", "run-02-positions", "b", "direct"),
        ("positions-restricted", "run-02-positions-adapted", "b", "restricted"),
    ):
        path = ROOT / run / f"{batch}-{mode}-scores.json"
        if path.exists():
            variants[name] = metrics(load(path))
    scores = {
        "initial": initial,
        "direct_agreement": {
            batch: agreement(keyed_scores("run-01", batch, "direct"), keyed_scores("run-01", batch, "direct-repeat"))
            for batch in ("a", "b")
        },
        "restricted_agreement": {
            batch: agreement(keyed_scores("run-01", batch, "restricted"), keyed_scores("run-01", batch, "restricted-repeat"))
            for batch in ("a", "b")
        },
        "variants": variants,
        "format_b_restricted_repair": try_repair("run-02-format-b", "b"),
        "identity_guard": {
            "original-a": guard_results("run-01", "a", False),
            "original-b": guard_results("run-01", "b", False),
            "positions-b": guard_results("run-02-positions", "b", False),
            "injected-a": guard_results("run-01", "a", True),
        },
        "history": load(ROOT / "run-02-history" / "replay-receipt.json"),
        "receipts": {
            path.relative_to(ROOT).as_posix(): digest(path.read_bytes())
            for path in sorted(ROOT.glob("run-*/*.receipt.json"))
        },
    }
    store(output, scores)
    small = {**scores, "format_b_restricted_repair": {
        key: value for key, value in scores["format_b_restricted_repair"].items() if key != "scores"
    }}
    del small["history"]
    del small["receipts"]
    print(encode(small))
    print(digest(output.read_bytes()))


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    main(parser.parse_args().output)
