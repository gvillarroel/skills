#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the semantic contract for the isolated editorial review-queue case."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


EXPECTED_NODES = {
    "web",
    "mobile",
    "partner",
    "batch",
    "gateway",
    "queue",
    "reviewers",
    "approved",
    "deferred",
}
EXPECTED_NODE_LABELS = {
    "web": "Web",
    "mobile": "Mobile",
    "partner": "Partner API",
    "batch": "Batch import",
    "gateway": "Gateway",
    "queue": "Review queue",
    "reviewers": "Reviewers",
    "approved": "Approved",
    "deferred": "Deferred",
}
EXPECTED_EDGES = {
    ("web", "gateway"),
    ("mobile", "gateway"),
    ("partner", "gateway"),
    ("batch", "gateway"),
    ("gateway", "queue"),
    ("queue", "reviewers"),
    ("queue", "deferred"),
    ("reviewers", "approved"),
}
EXPECTED_LEDGER = {
    "Producer: Web": ("Kept", "web"),
    "Producer: Mobile": ("Kept", "mobile"),
    "Producer: Partner API": ("Kept", "partner"),
    "Producer: Batch import": ("Kept", "batch"),
    "Gateway fan-in": ("Kept", "gateway"),
    "Review queue capacity: 2 items": ("Kept", "queue"),
    "Reviewer A": ("Merged", "reviewers"),
    "Reviewer B": ("Merged", "reviewers"),
    "Approved outcome": ("Kept", "approved"),
    "Deferred overflow outcome": ("Kept", "deferred"),
    "Metrics hook": ("Moved to detail", "operations-detail.mmd"),
    "Audit archive": ("Moved to detail", "operations-detail.mmd"),
}
NODE_DECLARATION_RE = re.compile(
    r"(?<![A-Za-z0-9_-])(?P<id>[A-Za-z_][A-Za-z0-9_-]*)\s*"
    r"(?P<shape>\[\[.*?\]\]|\[\(.*?\)\]|\[.*?\]|\(.*?\)|\{.*?\})"
)
NODE_ID_RE = re.compile(r"(?<![A-Za-z0-9_-])([A-Za-z_][A-Za-z0-9_-]*)(?![A-Za-z0-9_-])")
RELATION_RE = re.compile(
    r"<-\.\->|<-->|<==>|o--o|x--x|-\.\->|<-\.-|<--|<==|-->|==>|---|-\.-|===|--[ox]|[ox]--|~~~"
)


def _visible_node_label(shape: str) -> str:
    """Return the plain label from the simple flowchart shapes allowed by this case."""
    label = shape.strip()
    pairs = {"[": "]", "(": ")", "{": "}"}
    while len(label) >= 2 and label[0] in pairs and label[-1] == pairs[label[0]]:
        label = label[1:-1].strip()
    if len(label) >= 2 and label[0] == label[-1] and label[0] in {'"', "'"}:
        label = label[1:-1]
    return re.sub(r"\s+", " ", label).strip()


def _parse_relations(
    source_text: str,
) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Parse every relation and edge label, including chains and implicit nodes."""
    relations: list[tuple[str, str, str]] = []
    unsupported: list[str] = []
    for raw_line in source_text.splitlines():
        line = re.sub(
            r"--\s+([^-\n]+?)\s+-->",
            lambda match: f"-->|{match.group(1).strip()}|",
            raw_line,
        )
        line = re.sub(
            r"-\.\s+([^.\n]+?)\s+\.->",
            lambda match: f"-.->|{match.group(1).strip()}|",
            line,
        )
        line = re.sub(
            r"==\s+([^=\n]+?)\s+==>",
            lambda match: f"==>|{match.group(1).strip()}|",
            line,
        )
        masked_line = re.sub(
            r"\|[^|]*\|", lambda match: " " * len(match.group(0)), line
        )
        occurrences = list(NODE_ID_RE.finditer(masked_line))
        for source_match, target_match in zip(occurrences, occurrences[1:]):
            between = line[source_match.end() : target_match.start()]
            relation = RELATION_RE.search(between)
            if relation is None:
                continue
            source = source_match.group(1)
            target = target_match.group(1)
            label_match = re.search(r"\|([^|]*)\|", between)
            label = re.sub(r"\s+", " ", label_match.group(1)).strip() if label_match else ""
            relations.append((source, target, label))
            if relation.group(0) != "-->":
                unsupported.append(
                    f"{source} {relation.group(0)} {target}"
                )
    return relations, unsupported


def parse_ledger(markdown: str) -> tuple[dict[str, tuple[str, str, str]], list[str]]:
    rows: dict[str, tuple[str, str, str]] = {}
    errors: list[str] = []
    header_seen = False
    for line in markdown.splitlines():
        if "|" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells == ["Source item", "Decision", "Drawn as or target", "Reason"]:
            header_seen = True
            continue
        if not header_seen or len(cells) != 4 or set(cells[0]) <= {"-", ":", " "}:
            continue
        source_item, decision, destination, reason = cells
        if source_item in rows:
            errors.append(f"Duplicate fidelity-ledger row: {source_item}")
        rows[source_item] = (decision, destination, reason)
    if not header_seen:
        errors.append("Missing exact fidelity-ledger table header")
    return rows, errors


def verify(source_text: str, ledger_text: str) -> list[str]:
    errors: list[str] = []
    declarations = list(NODE_DECLARATION_RE.finditer(source_text))
    node_ids = {match.group("id") for match in declarations}
    node_labels: dict[str, set[str]] = {}
    for match in declarations:
        node_labels.setdefault(match.group("id"), set()).add(
            _visible_node_label(match.group("shape"))
        )
    source_without_inline_declarations = NODE_DECLARATION_RE.sub(
        lambda match: match.group("id"), source_text
    )
    relations, unsupported_relations = _parse_relations(
        source_without_inline_declarations
    )
    edges = [(source, target) for source, target, _ in relations]
    edge_set = set(edges)
    relation_node_ids = {endpoint for edge in edges for endpoint in edge}
    observed_node_ids = node_ids.union(relation_node_ids)
    if observed_node_ids != EXPECTED_NODES:
        errors.append(
            f"Node IDs differ: expected {sorted(EXPECTED_NODES)}, found {sorted(observed_node_ids)}"
        )
    for node_id, expected_label in EXPECTED_NODE_LABELS.items():
        actual_labels = node_labels.get(node_id)
        if actual_labels != {expected_label}:
            errors.append(
                f"Every visible label for node {node_id!r} must be {expected_label!r}, "
                f"found {sorted(actual_labels or set())!r}"
            )
    if unsupported_relations:
        errors.append(
            "All directed relations must use the required --> form; found: "
            + ", ".join(sorted(unsupported_relations))
        )
    duplicate_edges = sorted(edge for edge in set(edges) if edges.count(edge) > 1)
    if duplicate_edges:
        errors.append(
            "Directed relations must appear exactly once; duplicates: "
            + ", ".join(f"{source} --> {target}" for source, target in duplicate_edges)
        )
    if edge_set != EXPECTED_EDGES:
        errors.append(
            f"Directed relations differ: expected {sorted(EXPECTED_EDGES)}, found {sorted(edge_set)}"
        )
    if len(observed_node_ids) > 9:
        errors.append(f"Editorial overview exceeds 9 concept nodes: {len(observed_node_ids)}")
    if len(edges) > 12:
        errors.append(f"Editorial overview exceeds 12 relations: {len(edges)}")
    required_edge_facts = {
        ("gateway", "queue"): "capacity 2 items",
        ("queue", "reviewers"): "1 item per hour",
    }
    labels_by_edge: dict[tuple[str, str], list[str]] = {}
    for source, target, label in relations:
        labels_by_edge.setdefault((source, target), []).append(label)
    for edge, literal in required_edge_facts.items():
        labels = labels_by_edge.get(edge, [])
        if not any(literal.casefold() in label.casefold() for label in labels):
            errors.append(
                f"Visible fact {literal!r} must label relation {edge[0]} --> {edge[1]}"
            )
    for moved_item in ("metrics", "audit"):
        if re.search(rf"\b{moved_item}\b", source_text, re.IGNORECASE):
            errors.append(f"Moved detail appears in Mermaid source or accDescr: {moved_item}")

    rows, ledger_errors = parse_ledger(ledger_text)
    errors.extend(ledger_errors)
    if set(rows) != set(EXPECTED_LEDGER):
        errors.append(
            f"Ledger source items differ: expected {sorted(EXPECTED_LEDGER)}, found {sorted(rows)}"
        )
    for source_item, (expected_decision, expected_destination) in EXPECTED_LEDGER.items():
        row = rows.get(source_item)
        if row is None:
            continue
        decision, destination, reason = row
        if decision != expected_decision:
            errors.append(
                f"Ledger decision for {source_item!r} must be {expected_decision!r}, found {decision!r}"
            )
        if destination != expected_destination:
            errors.append(
                f"Ledger destination for {source_item!r} must be {expected_destination!r}, found {destination!r}"
            )
        if decision != "Kept" and not reason.strip():
            errors.append(f"Ledger reason is empty for non-kept item {source_item!r}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = verify(
        args.source.read_text(encoding="utf-8"),
        args.ledger.read_text(encoding="utf-8"),
    )
    result = {"ok": not errors, "errors": errors}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
