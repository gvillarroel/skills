#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bounded OpenRouter decisions transport with resumable, validated checkpoints."""
from __future__ import annotations

import datetime as dt
import email.utils
import json
import os
from pathlib import Path
import random
import threading
import time
import urllib.error
import urllib.request

from jev_contract import ContractError, ENDPOINT, digest, encode, require, response_valid, strict_json


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encode(value) + b"\n")
    temporary.replace(path)


def json_lines(path):
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield strict_json(line)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http_post(payload, key, timeout):
    request = urllib.request.Request(ENDPOINT, data=encode(payload), method="POST",
              headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                       "X-OpenRouter-Title": "Jev Batch Decisions"})
    # Do not forward the authorization header through redirects.
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=timeout) as response:
            data = response.read(2_000_001)
            require(len(data) <= 2_000_000, "Provider response is unexpectedly large.")
            return response.status, dict(response.headers.items()), data
    except urllib.error.HTTPError as exc:
        # Error bodies can echo source text or credentials; discard them.
        status, headers = exc.code, dict(exc.headers.items())
        exc.close()
        return status, headers, b""
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ContractError("Transport failed; request charge is unknown. Resume explicitly after checking connectivity.") from exc


def retry_delay(headers, attempt):
    value = next((v for k, v in headers.items() if k.lower() == "retry-after"), None)
    if value is not None:
        try:
            delay = float(value)
        except ValueError:
            try:
                when = email.utils.parsedate_to_datetime(value)
                delay = (when - dt.datetime.now(dt.timezone.utc)).total_seconds()
            except (TypeError, ValueError, OverflowError):
                delay = 0
        require(delay <= 30, "Provider Retry-After exceeds the bounded wait; resume later.")
        return max(0, delay)
    return min(2 ** attempt + random.random() * 0.25, 15)


class Client:
    def __init__(self, out, job, post=http_post, sleep=time.sleep):
        self.out, self.job, self.post, self.sleep = Path(out), job, post, sleep
        self.key = os.environ.get("OPENROUTER_API_KEY", "")
        require(self.key, "Set OPENROUTER_API_KEY in the environment; do not put it in the job.")
        self.cache = self.out / "checkpoints"
        self.cache.mkdir(exist_ok=True)
        self.ledger = self.out / "attempts.jsonl"
        self.lock = threading.Lock()
        self.stopped = threading.Event()
        self.attempts = sum(1 for e in json_lines(self.ledger) if e["event"] == "start") if self.ledger.exists() else 0
        self.cache_hits = 0

    def log(self, event):
        with self.ledger.open("ab") as f:
            f.write(encode(event) + b"\n")
            f.flush()
            os.fsync(f.fileno())

    def begin(self, key, stage):
        with self.lock:
            require(not self.stopped.is_set(), "Run stopped after another request failed.")
            require(self.attempts < self.job["limits"]["max_requests"], "Total request-attempt cap reached; use a new reviewed job to increase it.")
            self.attempts += 1
            self.log(dict(event="start", attempt=self.attempts, request_hash=key, stage=stage))
            return self.attempts

    def call(self, payload, stage):
        key = digest(dict(endpoint=ENDPOINT, payload=payload))
        cache_path = self.cache / (key + ".json")
        if cache_path.exists():
            saved = strict_json(cache_path.read_bytes())
            require(saved.get("request_hash") == key and saved.get("response_hash") == digest(saved.get("response")), "Checkpoint integrity failed.")
            response_valid(saved["response"], payload["questions"], payload["model"])
            with self.lock:
                self.cache_hits += 1
            return saved["response"], key
        limits = self.job["limits"]
        for local_attempt in range(limits["attempts"]):
            attempt = self.begin(key, stage)
            started = time.perf_counter()
            usage = None
            status = None
            try:
                status, headers, data = self.post(payload, self.key, limits["timeout_seconds"])
                if status != 200:
                    retry = status in (429, 500, 502, 503, 504, 529) and local_attempt + 1 < limits["attempts"]
                    with self.lock:
                        self.log(dict(event="end", attempt=attempt, status=status, outcome="http_error",
                                      elapsed_ms=round((time.perf_counter()-started)*1000, 2)))
                    if retry:
                        self.sleep(retry_delay(headers, local_attempt))
                        continue
                    raise ContractError(f"OpenRouter returned HTTP {status}; no decision was accepted.")
                response = strict_json(data)
                if isinstance(response, dict) and isinstance(response.get("usage"), dict):
                    # Persist only validated numeric accounting fields, even for rejected answers.
                    from jev_contract import number
                    usage = {k: v for k, v in response["usage"].items()
                             if k in ("input_tokens", "output_tokens", "cost") and number(v, 0, float("inf"))}
                response_valid(response, payload["questions"], payload["model"])
                write_json(cache_path, dict(request_hash=key, response_hash=digest(response), response=response))
                with self.lock:
                    self.log(dict(event="end", attempt=attempt, status=status, outcome="accepted", usage=usage,
                                  elapsed_ms=round((time.perf_counter()-started)*1000, 2)))
                return response, key
            except Exception:
                self.stopped.set()
                # Non-200 HTTP outcomes were already recorded above.
                if status is None or status == 200:
                    with self.lock:
                        self.log(dict(event="end", attempt=attempt, status=status, outcome="rejected", usage=usage,
                                      elapsed_ms=round((time.perf_counter()-started)*1000, 2)))
                raise
        raise ContractError("Request attempts exhausted.")

    def metrics(self):
        starts, ends = {}, {}
        if self.ledger.exists():
            for e in json_lines(self.ledger):
                (starts if e["event"] == "start" else ends)[e["attempt"]] = e
        usages = [e.get("usage") or {} for e in ends.values()]
        return dict(http_attempts=len(starts), accepted_calls=sum(e["outcome"] == "accepted" for e in ends.values()),
                    cache_hits_this_invocation=self.cache_hits,
                    reported_input_tokens=sum(x.get("input_tokens", 0) for x in usages),
                    reported_output_tokens=sum(x.get("output_tokens", 0) for x in usages),
                    reported_cost_usd=sum(x.get("cost", 0) for x in usages),
                    cost_unreported_attempts=len(starts)-sum("cost" in x for x in usages),
                    interrupted_attempts=len(set(starts)-set(ends)),
                    call_elapsed_ms=[e["elapsed_ms"] for e in ends.values() if e["outcome"] == "accepted"])
