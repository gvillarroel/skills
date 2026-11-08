#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib==7.6.0"]
# ///
"""Inspect a local ontology and verify an asserted graph's evidence bindings."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path, PureWindowsPath
import re
import sys

import rdflib
from rdflib import Graph, Literal, OWL, RDF, RDFS, SKOS, URIRef, XSD
from rdflib.exceptions import ParserError

FORMATS = {".ttl": "turtle", ".nt": "nt"}
PROPERTY_TYPES = {
    OWL.ObjectProperty: "object",
    OWL.DatatypeProperty: "datatype",
    OWL.AnnotationProperty: "annotation",
    RDF.Property: "generic",
}
ANNOTATIONS = {
    SKOS.prefLabel: "preferred_label", RDFS.label: "label", SKOS.altLabel: "alias",
    SKOS.definition: "definition",
    URIRef("http://purl.obolibrary.org/obo/IAO_0000115"): "definition",
}
IRI_PATTERN = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:[^\s<>"{}|^\x60\\]+$')


def digest(raw):
    return sha256(raw).hexdigest()


def parse_graph(path):
    if path.suffix.lower() not in FORMATS:
        raise ValueError("supported RDF file extensions are .ttl and .nt")
    raw = path.read_bytes()
    graph = Graph().parse(data=raw, publicID=path.resolve().as_uri(), format=FORMATS[path.suffix.lower()])
    return graph, digest(raw)


def named(values):
    return sorted({str(value) for value in values if isinstance(value, URIRef)})


def vocabulary(graph):
    classes = set(named((*graph.subjects(RDF.type, OWL.Class), *graph.subjects(RDF.type, RDFS.Class))))
    properties = {}
    for type_, kind in PROPERTY_TYPES.items():
        for term in named(graph.subjects(RDF.type, type_)):
            properties.setdefault(term, set()).add(kind)
    individuals = set(named(graph.subjects(RDF.type, OWL.NamedIndividual)))
    return classes, properties, individuals


def inventory(ontology, checksum):
    classes, properties, individuals = vocabulary(ontology)
    concepts = set(named(ontology.subjects(RDF.type, SKOS.Concept)))
    terms = []
    for iri in sorted(classes | set(properties) | individuals | concepts):
        term = URIRef(iri)
        kinds = properties.get(iri, set()) | ({"class"} if iri in classes else set())
        if iri in individuals:
            kinds.add("individual")
        if iri in concepts:
            kinds.add("concept")
        annotations = [
            {"kind": kind, "predicate": str(predicate), "value": str(value), "language": value.language}
            for predicate, kind in ANNOTATIONS.items()
            for value in ontology.objects(term, predicate) if isinstance(value, Literal)
        ]
        row = {
            "iri": iri, "kinds": sorted(kinds),
            "annotations": sorted(annotations, key=lambda a: (a["kind"], a["language"] or "", a["value"], a["predicate"])),
        }
        if iri in properties:
            for key, predicate in (("domain", RDFS.domain), ("range", RDFS.range)):
                values = list(ontology.objects(term, predicate))
                row[key] = named(values)
                row[f"unnamed_{key}_count"] = sum(not isinstance(value, URIRef) for value in values)
        terms.append(row)
    return {
        "ontology_sha256": checksum,
        "ontology_iris": named(ontology.subjects(RDF.type, OWL.Ontology)),
        "unresolved_imports": named(ontology.objects(None, OWL.imports)),
        "terms": terms,
    }


def unique_object(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key in evidence")
    return result


def iri(value):
    if not isinstance(value, str) or not IRI_PATTERN.fullmatch(value):
        raise ValueError("evidence requires an absolute IRI")
    return URIRef(value)


def canonical_object(term):
    if isinstance(term, Literal):
        if term.language and term.language != term.language.lower():
            return Literal(str(term), lang=term.language.lower(), normalize=False)
        if term.datatype == XSD.string:
            return Literal(str(term), normalize=False)
    return term


def object_term(raw):
    if set(raw) == {"iri"}:
        return iri(raw["iri"])
    if set(raw) not in ({"value"}, {"value", "datatype"}, {"value", "language"}):
        raise ValueError("evidence object must have one RDF term representation")
    if not isinstance(raw["value"], str):
        raise ValueError("literal value must be a string")
    language = raw.get("language")
    if "language" in raw and (not isinstance(language, str) or not language):
        raise ValueError("invalid language tag")
    datatype = iri(raw["datatype"]) if "datatype" in raw else None
    return canonical_object(Literal(raw["value"], lang=language, datatype=datatype, normalize=False))


def source_text(root, row):
    relative = Path(row["path"])
    if relative.is_absolute() or PureWindowsPath(row["path"]).drive or ".." in relative.parts:
        raise ValueError("source path must stay under the source root")
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("source path is outside the root or is unavailable")
    raw = path.read_bytes()
    if digest(raw) != row["sha256"]:
        raise ValueError("source SHA-256 mismatch")
    return raw.decode("utf-8")


def triple_text(triple):
    return " ".join(term.n3() for term in triple) + " ."


def graph_issues(data, ontology):
    classes, properties, individuals = vocabulary(ontology)
    schema_only = (classes | set(properties)) - individuals
    issues = []
    for subject, predicate, object_ in sorted(data, key=triple_text):
        triple = (subject, predicate, object_)
        issue = None
        if not isinstance(subject, URIRef) or not isinstance(object_, (URIRef, Literal)):
            issue = "unnamed RDF term"
        elif str(subject) in schema_only:
            issue = "schema term used as instance subject"
        elif predicate == RDF.type and (not isinstance(object_, URIRef) or str(object_) not in classes):
            issue = "type outside declared vocabulary"
        elif predicate != RDF.type:
            kinds = properties.get(str(predicate), set())
            if not kinds:
                issue = "property outside declared vocabulary"
            elif {"object", "datatype"} <= kinds:
                issue = "conflicting declared property kinds"
            elif ("object" in kinds and not isinstance(object_, URIRef)) or (
                "datatype" in kinds and not isinstance(object_, Literal)
            ):
                issue = "object term does not match declared property kind"
        if issue:
            issues.append({"issue": issue, "triple": triple_text(triple)})
    return issues


def check(ontology, checksum, data, ledger, root):
    if (not isinstance(ledger, dict) or not isinstance(ledger.get("sources"), list)
            or not ledger["sources"] or not isinstance(ledger.get("assertions"), list)):
        raise ValueError("evidence requires a nonempty sources array and an assertions array")
    if not root.is_dir():
        raise ValueError("source root must be an existing directory")
    canonical_data = Graph()
    for subject, predicate, object_ in data:
        canonical_data.add((subject, predicate, canonical_object(object_)))
    data = canonical_data
    issues = graph_issues(data, ontology)
    if ledger["ontology_sha256"] != checksum:
        issues.append({"issue": "ontology SHA-256 mismatch"})
    sources = {}
    for row in ledger["sources"]:
        source_id = row["id"]
        if not isinstance(source_id, str) or not source_id.strip() or source_id in sources:
            raise ValueError("source IDs must be nonempty and unique")
        sources[source_id] = None
        try:
            sources[source_id] = source_text(root, row)
        except (ValueError, OSError) as exc:
            issues.append({"issue": str(exc), "source_id": source_id})
    covered = set()
    for index, row in enumerate(ledger["assertions"], 1):
        triple = (iri(row["subject"]), iri(row["predicate"]), object_term(row["object"]))
        text = sources.get(row["source_id"])
        quote = row["quote"]
        valid_quote = (text is not None and isinstance(quote, str) and bool(quote.strip()) and quote in text
                       and isinstance(row["locator"], str) and bool(row["locator"].strip()))
        if valid_quote and ("start" in row or "end" in row):
            start, end = row.get("start"), row.get("end")
            valid_quote = type(start) is type(end) is int and 0 <= start < end <= len(text) and text[start:end] == quote
        if triple not in data:
            issues.append({"issue": "evidence cites an unasserted triple", "row": index})
        elif not valid_quote:
            issues.append({"issue": "unbound source quote or locator", "row": index})
        else:
            covered.add(triple)
    for missing in sorted(set(data) - covered, key=triple_text):
        issues.append({"issue": "asserted triple lacks valid evidence", "triple": triple_text(missing)})
    has_unnamed_terms = any(issue["issue"] == "unnamed RDF term" for issue in issues)
    canonical = None
    if not has_unnamed_terms:
        records = data.serialize(format="nt").split("\n")
        canonical = "".join(f"{row}\n" for row in sorted(filter(None, records)))
    return {
        "status": "violations" if issues else "passed",
        "ontology_sha256": checksum,
        "asserted_graph_sha256": digest(canonical.encode()) if canonical is not None else None,
        "asserted_triples": len(data),
        "evidence_covered_triples": len(covered),
        "checked_sources": sum(text is not None for text in sources.values()),
        "unresolved_imports": named(ontology.objects(None, OWL.imports)),
        "semantic_entailment_checked": False,
        "issues": issues,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inventory_command = commands.add_parser("inventory")
    check_command = commands.add_parser("check")
    for command in (inventory_command, check_command):
        command.add_argument("--ontology", type=Path, required=True)
        command.add_argument("--output", type=Path)
    check_command.add_argument("--data", type=Path, required=True)
    check_command.add_argument("--evidence", type=Path, required=True)
    check_command.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    rdflib.NORMALIZE_LITERALS = False
    try:
        ontology, checksum = parse_graph(args.ontology)
        if args.command == "inventory":
            result = inventory(ontology, checksum)
        else:
            data, _ = parse_graph(args.data)
            ledger = json.loads(args.evidence.read_bytes(), object_pairs_hook=unique_object)
            result = check(ontology, checksum, data, ledger, args.source_root.resolve())
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as output:
                output.write(text)
        else:
            print(text, end="")
    except (OSError, KeyError, AttributeError, TypeError, ValueError, SyntaxError, ParserError) as exc:
        print(f"Extraction check could not run: {exc}", file=sys.stderr)
        return 2
    return int(result.get("status") == "violations")


if __name__ == "__main__":
    raise SystemExit(main())
