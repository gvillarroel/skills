#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Emit deterministic token offsets for an exact, digest-bound source quote."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from semantic_model import EngineError, require, write_new


TOKEN = re.compile(r"\w+(?:[-’']\w+)*|[^\w\s]", re.UNICODE)


def index_quote(quote):
    indexed = []
    byte_offset = 0
    previous_end = 0
    for index, match in enumerate(TOKEN.finditer(quote), 1):
        byte_offset += len(quote[previous_end:match.start()].encode("utf-8"))
        byte_start = byte_offset
        byte_offset += len(match.group(0).encode("utf-8"))
        indexed.append({"index": index, "text": match.group(0), "start": match.start(), "end": match.end(),
                        "byte_start": byte_start, "byte_end": byte_offset})
        previous_end = match.end()
    return indexed


def compile_index(raw, filename, start_line, end_line):
    require(b"\x00" not in raw, "Source must be UTF-8 text without NUL", filename, "DOCUMENT_INPUT")
    try:
        text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError as exc:
        raise EngineError("DOCUMENT_INPUT", "Source is not valid UTF-8", filename) from exc
    lines = text.removesuffix("\n").split("\n") if text else []
    require(type(start_line) is int and type(end_line) is int
            and 1 <= start_line <= end_line <= len(lines) and end_line - start_line <= 10,
            "Select an inclusive in-bounds span of up to 11 lines", filename, "INVALID_RANGE")
    quote = "\n".join(lines[start_line - 1:end_line])
    require(bool(quote.strip()), "Selected source span must contain text", filename, "INVALID_RANGE")
    tokens = index_quote(quote)
    return {"source_sha256": sha256(raw).hexdigest(),
            "evidence": {"start_line": start_line, "end_line": end_line, "quote": quote},
            "tokens": tokens}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--start-line", required=True, type=int)
    parser.add_argument("--end-line", required=True, type=int)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        source = Path(args.source).resolve()
        require(source.is_file(), "Source must be a regular file", str(source), "DOCUMENT_INPUT")
        result = compile_index(source.read_bytes(), str(source), args.start_line, args.end_line)
        write_new(args.output, result, {source})
    except EngineError as exc:
        print(json.dumps({"engine_status": "error", "semantic_status": "not_run",
                          "error": {"code": exc.code, "path": exc.path, "message": str(exc)}}))
        return 2
    except OSError as exc:
        print(json.dumps({"engine_status": "error", "semantic_status": "not_run",
                          "error": {"code": "DOCUMENT_INPUT", "message": str(exc)}}))
        return 2
    print(json.dumps({"engine_status": "completed", "semantic_status": "not_run",
                      "token_count": len(result["tokens"]),
                      "source_sha256": result["source_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
