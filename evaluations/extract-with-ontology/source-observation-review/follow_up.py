"""Replay the public source-only evaluation with bounded format and provenance changes."""

from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path

from study import (
    ROOT, compile_observations, digest, encode, load, opaque, output_object,
    resolve_observation_windows, store, verify_freeze,
)


HISTORY = ROOT.parent / "product-catalog-evolution-20261110"
ORIGINAL = HISTORY / "development-pi-antecedent-microbenchmark"
CANDIDATE = HISTORY / "development-pi-antecedent-verification-candidate"
CANDIDATE_RECEIPT = "48a146d858f5c6f1ebfcdf0d0fba8fb9b12a71149cfffd7dd5746815287fbf86"
ORIGINAL_PROTOCOL = "adcde9f72ec3c52e369944c659da2c8889d0d5881f1908fa53a90cb8e214fadc"


def allow_empty_context(reply):
    amended = deepcopy(reply)
    for packet in amended["packets"]:
        for item in packet["observations"]:
            if isinstance(item, dict) and set(item) == {"identity", "subject", "assertion"}:
                item["context"] = []
    return amended


def adapted_observations(run, batch, stage, actor):
    receipt = load(run / f"{batch}-{stage}.receipt.json")
    return compile_observations(allow_empty_context(output_object(receipt["output"])), actor)


def with_positions(actor, fixture, batch):
    positions = {
        opaque("w", packet["key"], label): {
            "document": opaque("d", fixture["sources"][window["source"]]["url"]),
            "lines": [window["start"], window["end"]],
        }
        for packet in fixture["packets"] if packet["batch"] == batch
        for label, window in packet["windows"].items()
    }
    return [
        {**packet, "windows": [{**window, **positions[window["id"]]} for window in packet["windows"]]}
        for packet in actor
    ]


def freeze(run, files, description):
    run.mkdir(parents=True)
    for name, body in files.items():
        store(run / name, body)
    record = {
        "protocol": description,
        "attempts_per_mode": 1,
        "retries": 0,
        "freeze": {name: digest((ROOT / name).read_bytes()) for name in (
            "study.py", "run-model.mjs", "fixtures.json", "test_study.py", "follow_up.py", "test_follow_up.py",
        )},
        "input_sha256": {path.name: digest(path.read_bytes()) for path in sorted(run.glob("*.json"))},
    }
    store(run / "freeze.json", record)
    return digest((run / "freeze.json").read_bytes())


def format_trial(run, target, batch, stage):
    verify_freeze(run)
    actor = load(run / f"{batch}-actor.json")
    compiled = adapted_observations(run, batch, stage, actor)
    print(encode({
        "target": target.name, "admitted": sum(len(item["observations"]) for item in compiled["packets"].values()),
        "rejected": len(compiled["rejected"]),
        "freeze": freeze(target, {
            f"{batch}-actor.json": actor,
            f"{batch}-oracle.json": load(run / f"{batch}-oracle.json"),
            f"{batch}-observe-compiled.json": compiled,
        }, {
            "change": "Default an omitted context list to empty and enforce all original quote checks.",
            "original_observer": digest((run / f"{batch}-{stage}.receipt.json").read_bytes()),
            "comparison": "Review the same claims against the admitted observations.",
        }),
    }))


def pinned(path, expected):
    if digest(path.read_bytes()) != expected:
        raise ValueError(f"Historical input changed: {path.name}")
    return load(path)


def historical_inputs():
    protocol = pinned(ORIGINAL / "protocol.json", ORIGINAL_PROTOCOL)
    receipt = pinned(CANDIDATE / "strict-candidate-comparison-receipt.json", CANDIDATE_RECEIPT)
    expected = pinned(ORIGINAL / "oracle" / "gold.json", protocol["files_sha256"]["oracle/gold.json"])
    files = {}
    for batch, arm in (("a", "original"), ("b", "antecedent")):
        actor_name = f"actor/{arm}.json"
        source = pinned(ORIGINAL / actor_name, protocol["files_sha256"][actor_name])
        packets = []
        for claim in source["claims"]:
            windows = [{
                "id": window["id"], "text": window["quote"],
                "document": opaque("d", "power-automate", window["source_id"]),
                "lines": [window["start_line"], window["end_line"]],
            } for window in claim["passages"]]
            packets.append({
                "id": opaque("p", "historical", arm, claim["id"]),
                "windows": windows,
                "claims": [{"id": claim["id"], "text": claim["claim"], "identity": "named"}],
            })
        result_path = CANDIDATE / "harness" / "evaluations" / "runs" / (
            f"power-catalog-antecedent-verify-{arm}-luna-low"
        ) / "workspace" / "decisions.json"
        files.update({
            f"{batch}-actor.json": packets,
            f"{batch}-old-decisions.json": pinned(result_path, receipt["arms"][arm]["files_sha256"]["workspace/decisions.json"]),
            f"{batch}-expected.json": expected["expected"][arm],
        })
    return files


def unnamed_basis(witnesses, observations):
    selected = set(witnesses)
    contained = [item for item in observations if resolve_observation_windows(item) <= selected]
    return bool(contained) and all(item["identity"] == "unnamed" for item in contained)


def replay_historical(run):
    verify_freeze(run)
    results = {}
    for batch in ("a", "b"):
        actor = load(run / f"{batch}-actor.json")
        by_claim = {claim["id"]: packet["id"] for packet in actor for claim in packet["claims"]}
        observations = adapted_observations(run, batch, "observe", actor)
        old = load(run / f"{batch}-old-decisions.json")["decisions"]
        expected = {row["id"]: row for row in load(run / f"{batch}-expected.json")}
        comparisons = []
        for row in old:
            packet = observations["packets"][by_claim[row["id"]]]
            revised = dict(row)
            if row["status"] in {"keep", "replace"} and unnamed_basis(row["witness_ids"], packet["observations"]):
                revised.update(
                    status="needs-evidence", witness_ids=[],
                    reason="The selected source observations leave the subject unnamed.",
                    question="Which source passage identifies the capability referenced in the provider statement?",
                )
            gold = expected[row["id"]]
            comparisons.append({
                "id": row["id"],
                "original": row, "after_check": revised,
                "original_exact": row["status"] == gold["status"] and sorted(row["witness_ids"]) == sorted(gold["witness_ids"]),
                "after_check_exact": revised["status"] == gold["status"] and sorted(revised["witness_ids"]) == sorted(gold["witness_ids"]),
            })
        results[batch] = {"comparisons": comparisons, "admitted": sum(
            len(packet["observations"]) for packet in observations["packets"].values()
        ), "rejected": len(observations["rejected"])}
    store(run / "replay-receipt.json", results)
    print(encode({
        batch: {
            "before": sum(row["original_exact"] for row in result["comparisons"]),
            "after": sum(row["after_check_exact"] for row in result["comparisons"]),
            "total": len(result["comparisons"]), "admitted": result["admitted"], "rejected": result["rejected"],
        } for batch, result in results.items()
    }))


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    form = sub.add_parser("format")
    form.add_argument("original", type=Path)
    form.add_argument("target", type=Path)
    form.add_argument("batch", choices=("a", "b"))
    form.add_argument("reader", choices=("observe", "observe-repeat"))
    pos = sub.add_parser("positions")
    pos.add_argument("original", type=Path)
    pos.add_argument("target", type=Path)
    hist = sub.add_parser("history")
    hist.add_argument("target", type=Path)
    replay = sub.add_parser("replay-history")
    replay.add_argument("target", type=Path)
    args = parser.parse_args()
    if args.command == "format":
        format_trial(args.original, args.target, args.batch, args.reader)
    elif args.command == "positions":
        verify_freeze(args.original)
        fixture = load(ROOT / "fixtures.json")
        print(freeze(args.target, {
            "b-actor.json": with_positions(load(args.original / "b-actor.json"), fixture, "b"),
            "b-oracle.json": load(args.original / "b-oracle.json"),
        }, {
            "change": "Add opaque document identity and exact line ranges to the unchanged windows.",
            "comparison": "Compare direct review and restricted review in packet batch b.",
        }))
    elif args.command == "history":
        print(freeze(args.target, historical_inputs(), {
            "change": "Inspect the frozen public Pi source windows without access to the recorded verdicts.",
            "gate": "Withhold a positive citation when all admitted observations contained in it leave the subject unnamed.",
            "comparison": "Replay the fixed old decisions. Compare with the unchanged original oracle.",
            "receipt_sha256": CANDIDATE_RECEIPT,
        }))
    else:
        replay_historical(args.target)
