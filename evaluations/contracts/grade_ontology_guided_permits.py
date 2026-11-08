#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib==7.6.0"]
# ///
"""Verify the permit extraction and its glossary independently of the agent."""

from argparse import ArgumentParser
import csv
import json
from pathlib import Path
import re
import sys

from rdflib import RDF, URIRef

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/extract-with-ontology/scripts"))
import check_extraction as checker

MODEL = "urn:permit-model:"
RECORD = "urn:permit-record:"
EXPECTED_REGISTER = {
    "P17": "P17,Submitted",
    "P18": "P18,Escalated",
    "P19": "P19,",
    "P20": "P20,Granted",
}
EXPECTED_GLOSSARY = {
    "Archived": ("", "missing", []),
    "Filed": ("Recorded as received and awaiting a decision.", "source-backed", ["Submitted"]),
    "Granted": ("Approved by the issuing authority.", "source-backed", []),
}
HEADER = ["id", "term", "kind", "language", "definition", "definition_status", "aliases", "source_locator"]
CONCEPT_KINDS = {"concept", "skos:concept", "skos concept", str(checker.SKOS.Concept).lower()}


def grade(workspace):
    issues = []
    prompt = (ROOT / "evaluations/pi-prompts/ontology-guided-permits.md").read_text(encoding="utf-8")
    for name in ("permit-model.ttl", "permit-register.csv", "terminology.txt"):
        block = re.search(rf"`{re.escape(name)}`\n\n```\w+\n(.*?)\n```", prompt, re.DOTALL)
        if (workspace / name).read_text(encoding="utf-8").rstrip("\n") != block[1]:
            issues.append(f"supplied input changed: {name}")

    data, _ = checker.parse_graph(workspace / "data.ttl")
    expected = {(URIRef(RECORD + key), RDF.type, URIRef(MODEL + "Permit")) for key in EXPECTED_REGISTER}
    expected.update(
        (URIRef(RECORD + key), URIRef(MODEL + "status"), URIRef(MODEL + value))
        for key, value in (("P17", "Filed"), ("P20", "Granted"))
    )
    if set(data) != expected:
        issues.append("asserted graph differs from the six reference triples")
    ontology, checksum = checker.parse_graph(workspace / "permit-model.ttl")
    ledger = json.loads((workspace / "evidence.json").read_text(encoding="utf-8"))
    verified = checker.check(ontology, checksum, data, ledger, workspace)
    if verified["status"] != "passed":
        issues.append(f"independent evidence check failed: {verified['issues']}")
    submitted_check = json.loads((workspace / "checks.json").read_text(encoding="utf-8"))
    if submitted_check != verified:
        issues.append("submitted checker report differs from the independently reproduced report")
    sources = {row["id"]: row["path"] for row in ledger["sources"]}
    cited = set()
    for row in ledger["assertions"]:
        record = row["subject"].removeprefix(RECORD)
        if (sources.get(row["source_id"]) == "permit-register.csv"
                and EXPECTED_REGISTER.get(record) in row["quote"].splitlines()):
            cited.add((checker.iri(row["subject"]), checker.iri(row["predicate"]), checker.object_term(row["object"])))
    if cited != expected:
        issues.append("each accepted assertion must cite its own register row")

    with (workspace / "glossary.csv").open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if reader.fieldnames != HEADER:
            issues.append("glossary CSV header differs from the contract")
    if [row["id"] for row in rows] != [MODEL + key for key in EXPECTED_GLOSSARY]:
        issues.append("glossary concept coverage or order differs from the contract")
    for row in rows:
        key = row["id"].removeprefix(MODEL)
        if key not in EXPECTED_GLOSSARY:
            continue
        if row["term"] != key or row["kind"].lower() not in CONCEPT_KINDS or row["language"].lower() != "en":
            issues.append(f"{key}: wrong preferred label, kind or language")
        if (row["definition"], row["definition_status"], json.loads(row["aliases"])) != EXPECTED_GLOSSARY[key]:
            issues.append(f"{key}: wrong definition, status or aliases")
        if row["definition"] and "permit-model.ttl" not in row["source_locator"]:
            issues.append(f"{key}: canonical definition lacks ontology provenance")

    markdown = (workspace / "glossary.md").read_text(encoding="utf-8")
    for key, (definition, _, _) in EXPECTED_GLOSSARY.items():
        if key not in markdown or definition not in markdown:
            issues.append(f"{key}: Markdown glossary entry or definition missing")
    review = (workspace / "review.md").read_text(encoding="utf-8")
    if not all(token in review for token in ("P18", "Escalated", "P19")):
        issues.append("review must include the unmatched value and blank status")
    if not any("terminology.txt" in text and "scanned" in text for text in (markdown, review)):
        issues.append("historical usage and its provenance are missing")
    return {"issues": issues, "assertions": len(data), "register_supported_assertions": len(cited),
            "asserted_graph_sha256": verified["asserted_graph_sha256"], "glossary_entries": len(rows)}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    result = grade(parser.parse_args().workspace.resolve())
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["issues"]))
