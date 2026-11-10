#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compile independent, source-pinned glossary drafts from a framed batch."""

from argparse import ArgumentParser
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re

from compile_glossary_proposals import compile_ledger, unique_fields

DOCUMENT_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,99}")
SHA256 = re.compile(r"[0-9a-f]{64}")


def decode_json(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_fields)


def source_path(root, value):
    if (not isinstance(value, str) or not value
            or re.search(r"[\x00-\x1f\x7f:\\]", value)):
        raise ValueError("Source path must be portable and relative to the manifest")
    relative = PurePosixPath(value)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError("Source path must stay inside the manifest directory")
    resolved = root.joinpath(*relative.parts).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Source path must stay inside the manifest directory")
    return resolved


def read_manifest(raw, root):
    manifest = decode_json(raw)
    if not isinstance(manifest, dict) or manifest.keys() != {"documents"}:
        raise ValueError("Manifest needs a documents object")
    documents = manifest["documents"]
    if not isinstance(documents, dict) or not documents:
        raise ValueError("Manifest needs at least one expected document")
    expected = {}
    for name, item in documents.items():
        if not DOCUMENT_ID.fullmatch(name):
            raise ValueError(f"Invalid document ID: {name!r}")
        if not isinstance(item, dict) or item.keys() != {"path", "sha256"}:
            raise ValueError(f"Document {name} needs path and sha256")
        pin = item["sha256"]
        if not isinstance(pin, str) or not SHA256.fullmatch(pin):
            raise ValueError(f"Document {name} needs a lowercase SHA-256")
        expected[name] = source_path(root, item["path"]), pin
    return expected


def frame_records(raw, expected):
    rows, diagnostics = defaultdict(list), []
    lines = raw.removesuffix(b"\n").split(b"\n") if raw else []
    for index, line in enumerate(lines, 1):
        prefix, separator, body = line.removesuffix(b"\r").partition(b"\t")
        try:
            name = prefix.decode("ascii")
        except UnicodeDecodeError:
            name = ""
        if not separator or not DOCUMENT_ID.fullmatch(name):
            diagnostics.append({"line": index, "code": "unframed-record"})
        elif name not in expected:
            diagnostics.append({"line": index, "document": name, "code": "unexpected-document"})
        else:
            rows[name].append((index, body))
    return rows, diagnostics


def compile_document(name, line, body, path, pin, diagnostics):
    location = {"document": name, "line": line}
    try:
        draft = decode_json(body)
    except (ValueError, RecursionError) as error:
        diagnostics.append(location | {"code": "invalid-record", "message": str(error)})
        return None
    try:
        if not path.is_file():
            raise OSError("Source is not a regular file")
        source = path.read_bytes()
    except OSError:
        diagnostics.append(location | {"code": "unreadable-source"})
        return None
    if sha256(source).hexdigest() != pin:
        diagnostics.append(location | {"code": "stale-source"})
        return None
    try:
        return compile_ledger(source, draft) | {"draft_sha256": sha256(body).hexdigest()}
    except ValueError as error:
        diagnostics.append(location | {"code": "invalid-draft", "message": str(error)})
        return None


def compile_batch(manifest_bytes, records_bytes, root):
    expected = read_manifest(manifest_bytes, root)
    rows, diagnostics = frame_records(records_bytes, expected)
    documents = {}
    for name, (path, pin) in sorted(expected.items()):
        frames = rows[name]
        if not frames:
            diagnostics.append({"document": name, "code": "missing-document"})
        elif len(frames) > 1:
            diagnostics.append({"document": name, "lines": [line for line, _ in frames],
                                "code": "duplicate-document"})
        else:
            line, body = frames[0]
            result = compile_document(name, line, body, path, pin, diagnostics)
            if result is not None:
                documents[name] = result
    return {
        "status": "partial" if diagnostics else "compiled",
        "expected_documents": sorted(expected),
        "documents": documents,
        "diagnostics": diagnostics,
        "manifest_sha256": sha256(manifest_bytes).hexdigest(),
        "records_sha256": sha256(records_bytes).hexdigest(),
    }


def main(argv=None):
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = args.manifest.resolve()
        result = compile_batch(manifest.read_bytes(), args.records.read_bytes(), manifest.parent)
        raw_output = (json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
        with args.output.open("xb") as stream:
            stream.write(raw_output)
    except (OSError, RuntimeError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 2
    print(json.dumps({"status": result["status"], "documents": len(result["documents"]),
                      "diagnostics": len(result["diagnostics"])}))
    return 1 if result["diagnostics"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
