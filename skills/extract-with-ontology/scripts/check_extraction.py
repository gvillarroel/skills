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
        raise ValueError("duplicate JSON key")
    return result


def iri(value):
    if (not isinstance(value, str) or not IRI_PATTERN.fullmatch(value)
            or re.search(r"[\x00-\x1f\x7f-\x9f]", value)):
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


def manifest_rows(manifest_path):
    manifest = json.loads(manifest_path.read_bytes(), object_pairs_hook=unique_object)
    rows = manifest.get("sources") if isinstance(manifest, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("source manifest requires a nonempty sources array")

    entries = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("source manifest entries require a path and SHA-256")
        path, checksum = row.get("path"), row.get("sha256")
        if (not isinstance(path, str) or not path.strip() or not isinstance(checksum, str)
                or not re.fullmatch(r"[0-9a-f]{64}", checksum)):
            raise ValueError("source manifest entries require a path and lowercase SHA-256")
        if path in entries:
            raise ValueError("duplicate source path in manifest")
        entries[path] = row
    return entries


def manifest_pin(manifest_path, source):
    entries = manifest_rows(manifest_path)
    if source not in entries:
        raise ValueError("source path is absent from manifest")
    return entries[source]["sha256"]


def manifest_sources(manifest_path):
    sources = []
    for path, row in manifest_rows(manifest_path).items():
        if "source_id" in row and "id" in row and row["source_id"] != row["id"]:
            raise ValueError("conflicting source IDs in manifest")
        source_id = row.get("source_id", row.get("id", path))
        sources.append({"id": source_id, "path": path, "sha256": row["sha256"]})
    return sources


def line_starts(text):
    starts = [0, *(match.end() for match in re.finditer("\n", text))]
    if not text or text.endswith("\n"):
        starts.pop()
    return starts


def line_span(text, starts, first, last):
    start = starts[first - 1]
    end = starts[last] if last < len(starts) else len(text)
    if text[end - 1:end] == "\n":
        end -= 1
        if text[end - 1:end] == "\r":
            end -= 1
    return start, end


def numbered_source(root, path, checksum, first, last):
    text = source_text(root, {"path": path, "sha256": checksum})
    starts = line_starts(text)
    lines = []
    if starts or first != 1 or last is not None:
        stop = len(starts) if last is None else last
        if not 1 <= first <= stop <= len(starts):
            raise ValueError("requested source lines are out of bounds")
        for number in range(first, stop + 1):
            start, end = line_span(text, starts, number, number)
            lines.append({"line": number, "text": text[start:end]})
    return {"source": path, "source_sha256": checksum,
            "line_count": len(starts), "lines": lines}


def triple_text(triple):
    return " ".join(term.n3() for term in triple) + " ."


def assertion_triple(row):
    return iri(row["subject"]), iri(row["predicate"]), object_term(row["object"])


def canonical_graph_text(graph):
    records = graph.serialize(format="nt").split("\n")
    return "".join(f"{row}\n" for row in sorted(filter(None, records)))


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
        triple = assertion_triple(row)
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
    canonical = None if has_unnamed_terms else canonical_graph_text(data)
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


def bind_evidence(checksum, selection, root):
    if (not isinstance(selection, dict) or set(selection) != {"sources", "assertions"}
            or not isinstance(selection["sources"], list) or not selection["sources"]
            or not isinstance(selection["assertions"], list)):
        raise ValueError("selection requires a nonempty sources array and an assertions array")
    sources = {}
    for item in selection["sources"]:
        source_id = item["id"]
        if not isinstance(source_id, str) or not source_id.strip() or source_id in sources:
            raise ValueError("source IDs must be nonempty and unique")
        text = source_text(root, item)
        sources[source_id] = (text, line_starts(text))

    assertions = []
    triple_fields = {"subject", "predicate", "object", "source_id"}
    for index, row in enumerate(selection["assertions"], 1):
        if not isinstance(row, dict) or set(row) != triple_fields | {"start_line", "end_line"}:
            raise ValueError(f"selection row {index} requires triple fields, source_id, start_line and end_line")
        source_id = row["source_id"]
        if source_id not in sources:
            raise ValueError(f"selection row {index} has an unknown source")
        text, starts = sources[source_id]
        first, last = row["start_line"], row["end_line"]
        if not (type(first) is type(last) is int and 1 <= first <= last <= len(starts)):
            raise ValueError(f"selection row {index} has an out-of-bounds line range")
        start, end = line_span(text, starts, first, last)
        quote = text[start:end]
        if not quote.strip():
            raise ValueError(f"selection row {index} has a blank citation")
        locator = f"line {first}" if first == last else f"lines {first}-{last}"
        assertions.append({key: row[key] for key in triple_fields} | {
            "locator": locator, "quote": quote, "start": start, "end": end,
        })
    assertions.sort(key=lambda row: (row["source_id"], row["start"], row["end"],
                                     row["subject"], row["predicate"], json.dumps(row["object"], sort_keys=True)))
    return {"ontology_sha256": checksum, "sources": sorted(selection["sources"], key=lambda item: item["id"]),
            "assertions": assertions}


def materialized_graph(ledger):
    graph = Graph()
    for row in ledger["assertions"]:
        graph.add(assertion_triple(row))
    turtle = canonical_graph_text(graph)
    parsed = Graph().parse(data=turtle, format="turtle")
    if set(parsed) != set(graph):
        raise ValueError("materialized RDF does not preserve the selected terms")
    return parsed, turtle


def write_claim_bundle(directory, turtle, ledger):
    evidence = json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    files = (("data.ttl", turtle.encode("utf-8")), ("evidence.json", evidence.encode("utf-8")))
    directory.mkdir()
    created = []
    try:
        for name, payload in files:
            path = directory / name
            with path.open("xb") as stream:
                created.append(path)
                stream.write(payload)
    except BaseException:
        for path in created:
            path.unlink(missing_ok=True)
        directory.rmdir()
        raise


def extraction_result(args):
    ontology, checksum = parse_graph(args.ontology)
    if args.command == "inventory":
        return inventory(ontology, checksum)
    root = args.source_root.resolve()
    if args.command == "check":
        data, _ = parse_graph(args.data)
        ledger = json.loads(args.evidence.read_bytes(), object_pairs_hook=unique_object)
        return check(ontology, checksum, data, ledger, root)

    selection = json.loads(args.selection.read_bytes(), object_pairs_hook=unique_object)
    if args.manifest is not None:
        if not isinstance(selection, dict) or set(selection) != {"assertions"}:
            raise ValueError("selection with a manifest requires only an assertions array")
        selection["sources"] = manifest_sources(args.manifest)
    ledger = bind_evidence(checksum, selection, root)
    if args.command == "materialize":
        data, turtle = materialized_graph(ledger)
    else:
        data, _ = parse_graph(args.data)
    validation = check(ontology, checksum, data, ledger, root)
    if validation["status"] != "passed":
        raise ValueError(f"bound evidence failed validation: {validation['issues'][0]['issue']}")
    if args.command == "materialize":
        write_claim_bundle(args.output_dir, turtle, ledger)
        return validation
    return ledger


def main():
    parser = ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inventory_command = commands.add_parser("inventory")
    check_command = commands.add_parser("check")
    bind_command = commands.add_parser("bind")
    materialize_command = commands.add_parser("materialize")
    lines_command = commands.add_parser("lines", help="show numbered lines from pinned UTF-8 text")
    for command in (inventory_command, check_command, bind_command, lines_command):
        command.add_argument("--output", type=Path)
    for command in (inventory_command, check_command, bind_command, materialize_command):
        command.add_argument("--ontology", type=Path, required=True)
    for command in (check_command, bind_command):
        command.add_argument("--data", type=Path, required=True)
    for command in (check_command, bind_command, materialize_command, lines_command):
        command.add_argument("--source-root", type=Path, required=True)
    lines_command.add_argument("--source", required=True, help="path relative to the source root")
    source_pin = lines_command.add_mutually_exclusive_group(required=True)
    source_pin.add_argument("--sha256")
    source_pin.add_argument("--manifest", type=Path, help="read the SHA-256 from this source manifest")
    lines_command.add_argument("--start-line", type=int, default=1)
    lines_command.add_argument("--end-line", type=int)
    check_command.add_argument("--evidence", type=Path, required=True)
    for command in (bind_command, materialize_command):
        command.add_argument("--selection", type=Path, required=True)
        command.add_argument("--manifest", type=Path, help="read the source roster and pins from this manifest")
    materialize_command.add_argument("--output-dir", type=Path, required=True)
    materialize_command.set_defaults(output=None)
    args = parser.parse_args()
    rdflib.NORMALIZE_LITERALS = False
    try:
        if args.command == "lines":
            checksum = args.sha256 if args.manifest is None else manifest_pin(args.manifest, args.source)
            result = numbered_source(
                args.source_root.resolve(), args.source, checksum, args.start_line, args.end_line
            )
        else:
            result = extraction_result(args)
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as output:
                output.write(text)
        elif args.command == "lines":
            sys.stdout.buffer.write(text.encode("utf-8"))
        else:
            print(text, end="")
    except (OSError, KeyError, AttributeError, TypeError, ValueError, SyntaxError, ParserError) as exc:
        print(f"Extraction check could not run: {exc}", file=sys.stderr)
        return 2
    return int(result.get("status") == "violations")


if __name__ == "__main__":
    raise SystemExit(main())
