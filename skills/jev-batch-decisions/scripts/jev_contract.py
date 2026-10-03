#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the supported Jev job dialect and native decision responses."""
from __future__ import annotations

import hashlib
import json
import math

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
DEFAULT_LIMITS = dict(chunk_chars=3000, batch_items=4, max_questions=32,
                      max_request_bytes=24000, concurrency=4, max_requests=200,
                      attempts=3, timeout_seconds=30)
DEFAULT_REVIEW = dict(confidence_min=0.7, noul_low=0.2, noul_high=0.8)


class ContractError(ValueError):
    """A sanitized, non-retryable input or response error."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def strict_json(text):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "Duplicate JSON key.")
            out[key] = value
        return out
    def invalid(_):
        raise ContractError("Non-finite JSON number.")
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError("Invalid JSON encoding or syntax.") from exc


def number(value, low=0, high=1):
    return type(value) in (int, float) and math.isfinite(value) and low <= value <= high


def keys(value, allowed, required=()):
    require(isinstance(value, dict), "Expected an object.")
    require(set(value) <= set(allowed) and set(required) <= set(value), "Unexpected or missing contract field.")


def questions_valid(questions):
    require(isinstance(questions, dict) and 1 <= len(questions) <= 32, "Use 1 to 32 typed questions.")
    for name, question in questions.items():
        require(isinstance(name, str) and name and len(name) <= 80, "Invalid question name.")
        keys(question, ("type", "instructions", "criteria"), ("type", "instructions"))
        require(isinstance(question["instructions"], str) and question["instructions"].strip(), "Instructions must be a nonempty string.")
        kind, criteria = question["type"], question.get("criteria")
        require(kind in ("choice", "score", "noul"), "Jev supports choice, score and noul, not generated text.")
        if kind == "score":
            require(isinstance(criteria, list) and 2 <= len(criteria) <= 32 and
                    all(isinstance(x, str) and x.strip() for x in criteria), "Score needs 2 to 32 ordered descriptions.")
        elif kind == "choice":
            require(isinstance(criteria, dict) and 2 <= len(criteria) <= 32 and
                    all(isinstance(k, str) and k and (v is None or isinstance(v, str))
                        for k, v in criteria.items()), "Choice needs 2 to 32 named options.")
        elif criteria is not None:
            keys(criteria, ("true", "false"))
            require(all(isinstance(x, str) for x in criteria.values()), "Noul criteria must be text.")


def job_valid(raw):
    keys(raw, ("version", "model", "context", "questions", "limits", "review", "reducers", "reduce"),
         ("version", "questions"))
    require(type(raw["version"]) is int and raw["version"] == 1, "Unsupported job version.")
    job = dict(raw)
    job.setdefault("model", "typesafe/jev-1.13")
    require(isinstance(job["model"], str) and job["model"].startswith("typesafe/jev-"), "Use an explicit typesafe/jev model ID.")
    job.setdefault("context", "")
    require(isinstance(job["context"], str), "Context must be text.")
    questions_valid(job["questions"])
    keys(job.get("limits", {}), DEFAULT_LIMITS)
    job["limits"] = DEFAULT_LIMITS | job.get("limits", {})
    bounds = dict(chunk_chars=(32, 20000), batch_items=(1, 32), max_questions=(1, 64),
                  max_request_bytes=(1000, 28000), concurrency=(1, 16), max_requests=(1, 1000000),
                  attempts=(1, 5), timeout_seconds=(1, 120))
    for key, (low, high) in bounds.items():
        value = job["limits"][key]
        require(type(value) is int and low <= value <= high, "Invalid runner limit: " + key)
    require(len(job["questions"]) <= job["limits"]["max_questions"], "Question count exceeds request limit.")
    keys(job.get("review", {}), DEFAULT_REVIEW)
    job["review"] = DEFAULT_REVIEW | job.get("review", {})
    require(all(number(v) for v in job["review"].values()), "Review thresholds must be in [0,1].")
    require(job["review"]["noul_low"] < job["review"]["noul_high"], "Noul review interval must be nonempty.")
    job.setdefault("reducers", {})
    require(isinstance(job["reducers"], dict), "Reducers must be an object.")
    supported = {"choice": {"histogram"}, "score": {"max", "mean"}, "noul": {"any", "all"}}
    for name, op in job["reducers"].items():
        require(name in job["questions"] and op in supported[job["questions"][name]["type"]], "Reducer does not match its question type.")
    if "reduce" in job:
        spec = job["reduce"]
        keys(spec, ("questions", "context", "fan_in", "max_levels"), ("questions", "context"))
        questions_valid(spec["questions"])
        require(isinstance(spec["context"], str) and spec["context"].strip(), "Reduce needs its own aggregation instructions.")
        spec = dict(fan_in=4, max_levels=12) | spec
        require(type(spec["fan_in"]) is int and 2 <= spec["fan_in"] <= 32, "Reduce fan_in must be 2 to 32.")
        require(type(spec["max_levels"]) is int and 1 <= spec["max_levels"] <= 32, "Invalid reduce depth.")
        require(len(spec["questions"]) <= job["limits"]["max_questions"], "Reduce question count exceeds limit.")
        job["reduce"] = spec
    return job


def response_valid(body, questions, model):
    require(isinstance(body, dict), "Response must be an object.")
    actual = body.get("model")
    require(isinstance(actual, str) and (actual == model or actual.startswith(model + "-")), "Unexpected response model.")
    answers = body.get("answers")
    require(isinstance(answers, dict) and set(answers) == set(questions), "Missing or extra answer IDs.")
    for name, q in questions.items():
        a = answers[name]
        require(isinstance(a, dict) and a.get("type") == q["type"], "Answer type mismatch.")
        if q["type"] == "noul":
            require(number(a.get("noul")), "Invalid noul probability.")
            continue
        require(number(a.get("confidence")), "Invalid confidence.")
        expected = set(q["criteria"]) if q["type"] == "choice" else {str(i) for i in range(len(q["criteria"]))}
        p = a.get("probabilities")
        require(isinstance(p, dict) and set(p) == expected and all(number(v) for v in p.values()), "Invalid probability distribution keys or values.")
        require(abs(sum(p.values()) - 1) <= 0.011, "Probabilities do not sum to one.")
        if q["type"] == "choice":
            require(a.get("choice") in p and p[a["choice"]] >= max(p.values()) - 1e-6, "Choice is not a highest-probability option.")
        else:
            require(number(a.get("score"), 0, len(expected)-1), "Invalid score.")
            require(abs(a["score"] - sum(int(k)*v for k, v in p.items())) <= 0.06, "Score disagrees with its distribution.")
            require(a.get("legend") == {str(i): x for i, x in enumerate(q["criteria"])}, "Score legend mismatch.")
    usage = body.get("usage")
    require(isinstance(usage, dict), "Missing usage.")
    for field in ("input_tokens", "output_tokens"):
        require(type(usage.get(field)) is int and usage[field] >= 0, "Invalid token usage.")
    require("cost" not in usage or number(usage["cost"], 0, float("inf")), "Invalid reported cost.")
    return body


def decision(answer, review):
    kind = answer["type"]
    if kind == "noul":
        p = answer["noul"]
        value = True if p >= review["noul_high"] else False if p <= review["noul_low"] else None
    else:
        value = answer[kind] if answer["confidence"] >= review["confidence_min"] else None
        if kind == "choice" and value == "unknown":
            value = None
    return {"value": value, "needs_review": value is None, "raw": answer}
