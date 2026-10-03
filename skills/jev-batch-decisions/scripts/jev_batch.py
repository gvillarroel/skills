#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run typed Jev map decisions and optional recursive reduction over large inputs."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path
import sys
import time

from jev_contract import ContractError, decision, digest, encode, job_valid, require, strict_json
from jev_documents import batches, chunks, source_info
from jev_reduce import deterministic, semantic
from jev_transport import Client, json_lines, write_json


def runner_digest():
    return digest({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(Path(__file__).parent.glob("jev_*.py"))})


def plan(out, sources, job):
    counts = {s["source_id"]: 0 for s in sources}
    hard_splits, batch_count, max_bytes = 0, 0, 0
    with (out / "chunks.jsonl.tmp").open("wb") as chunk_file, (out / "map-jobs.jsonl.tmp").open("wb") as request_file:
        def items():
            nonlocal hard_splits
            for source in sources:
                for item in chunks(source, job["limits"]["chunk_chars"]):
                    counts[source["source_id"]] += 1
                    hard_splits += item["location"].get("boundary") == "hard"
                    chunk_file.write(encode(item) + b"\n")
                    yield item
        for batch, request, bindings in batches(items(), job):
            batch_count += 1
            max_bytes = max(max_bytes, len(encode(request)))
            request_file.write(encode(dict(request=request, bindings=bindings,
                                      items=[{k: v for k, v in x.items() if k != "text"} for x in batch])) + b"\n")
    require(source_info([s["path"] for s in sources]) == sources, "Input changed during planning; retry with stable source files.")
    for name in ("chunks.jsonl", "map-jobs.jsonl"):
        (out / (name + ".tmp")).replace(out / name)
    total = sum(counts.values())
    # With successful shrinking, each nonfinal level removes at least one node;
    # n(n+1)/2 is a safe loose bound even when byte packing reduces fan-in.
    reduce_upper = min(total * (total + 1) // 2, total * job.get("reduce", {}).get("max_levels", 0)) if "reduce" in job else 0
    planned = dict(sources=sources, units_by_source=counts, total_units=total, map_requests=batch_count,
                   max_map_request_bytes=max_bytes, request_byte_limit=job["limits"]["max_request_bytes"],
                   hard_text_boundaries=hard_splits, overlap_chars=0, reduce_call_upper_bound=reduce_upper,
                   request_attempt_cap=job["limits"]["max_requests"],
                   batching="Application-side synchronous decisions requests with bounded concurrency")
    require(batch_count <= job["limits"]["max_requests"], "Map requests alone exceed max_requests; revise the job before inference.")
    write_json(out / "plan.json", planned)
    return planned


def run_map(out, job, client):
    completed = reviewed = 0
    iterator = iter(json_lines(out / "map-jobs.jsonl"))
    workers = job["limits"]["concurrency"]
    with (out / "decisions.jsonl").open("wb") as result_file, ThreadPoolExecutor(max_workers=workers) as pool:
        while True:
            wave = []
            for _ in range(workers):
                item = next(iterator, None)
                if item is None:
                    break
                wave.append((item, pool.submit(client.call, item["request"], "map")))
            if not wave:
                break
            for item, future in wave:
                response, request_hash = future.result()
                by_id = {x["id"]: dict(x, decisions={}, request_hash=request_hash) for x in item["items"]}
                for key, (chunk_id, name) in item["bindings"].items():
                    by_id[chunk_id]["decisions"][name] = decision(response["answers"][key], job["review"])
                for row in by_id.values():
                    completed += 1
                    reviewed += any(d["needs_review"] for d in row["decisions"].values())
                    result_file.write(encode(row) + b"\n")
                result_file.flush()
    return completed, reviewed


def execute(job_path, input_paths, output, dry_run=False, resume=False, post=None, sleep=None):
    started = time.perf_counter()
    job = job_valid(strict_json(Path(job_path).read_bytes()))
    sources = source_info(input_paths)
    out = Path(output).resolve()
    bundle = Path(__file__).resolve().parent.parent
    require(not out.is_relative_to(bundle), "Keep outputs outside the read-only skill bundle.")
    require(not Path(job_path).resolve().is_relative_to(out) and
            all(not Path(s["path"]).is_relative_to(out) for s in sources), "Output directory must not contain the job or input files.")
    identity = digest(dict(job=job, sources=sources, runner_sha256=runner_digest()))
    out.mkdir(parents=True, exist_ok=True)
    lock_path = out / ".lock"
    try:
        lock = lock_path.open("x")
    except FileExistsError as exc:
        raise ContractError("Output is locked; verify its recorded process has ended before removing .lock.") from exc
    client, planned = None, None
    try:
        lock.write(str(os.getpid()))
        lock.close()
        existing = [p for p in out.iterdir() if p.name != ".lock"]
        require(not existing or resume, "Output is not empty; use a new directory or --resume.")
        if existing:
            manifest = strict_json((out / "run.json").read_bytes())
            require(manifest["identity"] == identity, "Resume identity differs: job, inputs or runner changed.")
        write_json(out / "run.json", dict(identity=identity, job=job, sources=sources, runner_sha256=runner_digest()))
        planned = plan(out, sources, job)
        write_json(out / "report.json", dict(status="planned" if dry_run else "running", identity=identity, total_units=planned["total_units"]))
        if dry_run:
            return strict_json((out / "report.json").read_bytes())
        options = {}
        if post is not None:
            options["post"] = post
        if sleep is not None:
            options["sleep"] = sleep
        client = Client(out, job, **options)
        completed, reviewed = run_map(out, job, client)
        require(completed == planned["total_units"], "Incomplete map coverage.")
        deterministic(out, job)
        final = semantic(out, job, client, completed) if "reduce" in job else None
        report = dict(status="complete", identity=identity, total_units=planned["total_units"], completed_units=completed,
                      review_units=reviewed, reduce_complete=final is not None,
                      metrics=client.metrics(), elapsed_seconds=round(time.perf_counter()-started, 3))
        write_json(out / "report.json", report)
        return report
    except Exception as exc:
        # Preserve prior successful output on a refused resume or nonempty-directory check.
        if planned is not None:
            completed = sum(1 for _ in json_lines(out / "decisions.jsonl")) if (out / "decisions.jsonl").exists() else 0
            safe_error = str(exc) if isinstance(exc, ContractError) else "Local processing failed; inspect the input format and filesystem."
            write_json(out / "report.json", dict(status="failed", identity=identity, error=safe_error,
                       total_units=planned["total_units"], completed_units=completed,
                       metrics=client.metrics() if client else {}, elapsed_seconds=round(time.perf_counter()-started, 3)))
        raise
    finally:
        lock.close()
        lock_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--input", required=True, nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Validate and materialize the plan without network access.")
    parser.add_argument("--resume", action="store_true", help="Reuse unchanged validated checkpoints; preserve the total attempt cap.")
    args = parser.parse_args()
    try:
        result = execute(args.job, args.input, args.out, args.dry_run, args.resume)
        print(encode(result).decode("utf-8"))
        return 0
    except (ContractError, OSError, UnicodeError, ValueError) as exc:
        message = str(exc) if isinstance(exc, ContractError) else "Local processing failed; check input encoding, file paths and filesystem access."
        print("Error: " + message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
