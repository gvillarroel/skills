#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently inspect generated model inventory and task-selection receipts.

Run: uv run --script evaluations/contracts/pi-durable-models.py WORKSPACE
This evaluator does not import the skill, contact a provider, inspect credentials,
run inference, or trust the candidate's check.json as verification evidence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath


LEVELS = ("off", "minimal", "low", "medium", "high", "xhigh", "max")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def finite_positive_integer(value):
    return type(value) is int and 0 < value <= 10**12


def inside(workspace: Path, relative: str) -> Path:
    require(isinstance(relative, str) and relative, "Expected a nonempty workspace-relative path.")
    posix, windows = PurePosixPath(relative), PureWindowsPath(relative)
    require(not posix.is_absolute() and not windows.anchor and "\\" not in relative and ":" not in relative,
            f"Nonportable artifact path: {relative}")
    require(all(part not in (".", "..") for part in relative.split("/")), f"Escaping artifact path: {relative}")
    current = workspace
    for part in posix.parts:
        current /= part
        require(not current.is_symlink() and not getattr(current, "is_junction", lambda: False)(),
                f"Linked authored artifact: {relative}")
    require(current.resolve().is_relative_to(workspace), f"Artifact escaped workspace: {relative}")
    require(current.is_file() and 0 < current.stat().st_size <= 4 * 1024 * 1024,
            f"Missing, empty or oversized artifact: {relative}")
    return current


def load(workspace, relative):
    value = json.loads(inside(workspace, relative).read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"Expected a JSON object: {relative}")
    return value


def supported_efforts(model):
    """Interpret the public Pi level map, independently of the generated resolver."""
    require(type(model.get("reasoning")) is bool, "A model must declare reasoning support.")
    if not model["reasoning"]:
        return {"off"}
    mapping = model.get("thinkingLevelMap", {})
    require(isinstance(mapping, dict), "Thinking-level metadata must be an object.")
    result = set()
    for level in LEVELS:
        if level in mapping and mapping[level] is None:
            continue
        if level in ("xhigh", "max") and level not in mapping:
            continue
        if level in mapping:
            require(isinstance(mapping[level], str) and mapping[level], "Invalid native thinking-level mapping.")
        result.add(level)
    return result


def stable_identity(model):
    """Compare numeric version components and real snapshot dates, not text order."""
    match = re.fullmatch(r"gpt-(\d+(?:\.\d+)*)-(sol|astra|luna)(?:-(\d{4}-\d{2}-\d{2}))?", model["id"])
    if not match:
        return None
    parts = tuple(int(part) for part in match[1].split("."))
    if any(part > 10**9 for part in parts):
        return None
    # Trailing zeroes are equivalent numerical versions (6 == 6.0).
    while len(parts) > 1 and parts[-1] == 0:
        parts = parts[:-1]
    try:
        date = dt.date.fromisoformat(match[3]).toordinal() if match[3] else 0
    except ValueError:
        return None
    return match[2], parts, date


def no_numeric_intelligence(value):
    if isinstance(value, list):
        return all(no_numeric_intelligence(item) for item in value)
    if not isinstance(value, dict):
        return True
    for key, item in value.items():
        if re.search(r"(?i)^(?:iq|intelligence[_ -]?(?:score|rating|level)?|capability[_ -]?score)$", key):
            if isinstance(item, (int, float)) or isinstance(item, str) and re.fullmatch(r"\s*\d+(?:\.\d+)?\s*", item):
                return False
        if not no_numeric_intelligence(item):
            return False
    return True


class Checks:
    def __init__(self):
        self.results = []

    def run(self, name, action):
        try:
            details = action()
            self.results.append({"name": name, "passed": True, "details": details})
        except (AssertionError, OSError, ValueError, KeyError, TypeError, OverflowError, AttributeError, IndexError) as error:
            self.results.append({"name": name, "passed": False, "error": str(error) or type(error).__name__})


def validate(workspace: Path):
    workspace = workspace.resolve()
    checks = Checks()
    catalog = load(workspace, "outputs/catalog.json")

    def inventory():
        require(catalog.get("version") == 1 and catalog.get("source") == "pi-public", "Inventory must identify the actual public catalog source.")
        require(catalog.get("availability") == "catalog-only", "Public metadata must not claim account availability or an inference probe.")
        require(catalog.get("provider") == "openai-codex", "This contract requires the requested Codex provider.")
        require(catalog.get("inferencePerformed") is False or
                ("inferencePerformed" not in catalog and isinstance(catalog.get("entitlement"), str) and
                 "no model inference" in catalog["entitlement"].lower()), "Inventory must identify that no inference was performed.")
        observed = catalog.get("observedAt")
        require(isinstance(observed, str) and dt.datetime.fromisoformat(observed.replace("Z", "+00:00")).tzinfo is not None,
                "Inventory needs a timezone-qualified observation timestamp.")
        require(isinstance(catalog.get("digest"), str) and re.fullmatch(r"[a-f0-9]{64}", catalog["digest"]), "Inventory needs a bounded metadata digest.")
        models = catalog.get("models")
        require(isinstance(models, list) and 0 < len(models) <= 10000, "Inventory must contain a bounded nonempty model list.")
        seen = set()
        for model in models:
            require(isinstance(model, dict) and model.get("provider") == "openai-codex", "Inventory contains another provider or malformed model.")
            require(isinstance(model.get("id"), str) and 0 < len(model["id"]) <= 256, "Model identity is missing or oversized.")
            require(model["id"] not in seen, "Inventory contains duplicate model identities.")
            seen.add(model["id"])
            require(model.get("api") == "openai-codex-responses" and "text" in model.get("input", []), "Inventory includes an incompatible transport.")
            require(finite_positive_integer(model.get("contextWindow")) and finite_positive_integer(model.get("maxTokens")), "Context/output limits must be positive catalog metadata.")
            require(not any(key in model for key in ("headers", "baseUrl", "credentials", "apiKey", "authorization")), "Inventory persisted private connection fields.")
            allowed = supported_efforts(model)
            if "supportedThinkingLevels" in model:
                require(isinstance(model["supportedThinkingLevels"], list) and set(model["supportedThinkingLevels"]) == allowed,
                        "Listed reasoning levels contradict the model's public map.")
        require(no_numeric_intelligence(models), "Catalog metadata fabricates a numerical intelligence score.")
        return {"models": len(models), "source": catalog["source"], "availability": catalog["availability"],
                "freshness_scope": "Receipt metadata only; source command/event review is still required."}
    checks.run("public_inventory_and_supported_efforts", inventory)

    def initial_project():
        live = load(workspace, "outputs/team/config.codex.example.json")
        require(live.get("provider", {}).get("kind") == "openai-codex", "Live example must select Codex.")
        require(live["provider"].get("model") == "latest" and live["provider"].get("catalogMode") == "refresh",
                "Live example must demonstrate current task-aware discovery rather than a hardcoded model ID.")
        default = load(workspace, "outputs/team/config.json")
        require(default.get("provider", {}).get("kind") == "faux", "Preparation must preserve the offline default.")
        manifest = load(workspace, "outputs/team/scaffold-manifest.json")
        require(manifest.get("runtimeIndependent") is True, "Generated application lacks independent provenance.")
        files = manifest.get("files")
        require(isinstance(files, dict) and files, "Initial manifest has no authored files.")
        for relative, digest in files.items():
            require(isinstance(digest, str) and re.fullmatch(r"[a-f0-9]{64}", digest), "Malformed initial file digest.")
            source = inside(workspace, "outputs/team/" + relative)
            require(hashlib.sha256(source.read_bytes()).hexdigest() == digest, f"Generated authored bytes changed: {relative}")
        required = {"config.codex.example.json", "config.json", "src/model-discovery.ts", "src/model-runtime.ts", "src/model-selection.ts", "src/models-cli.ts", "package.json"}
        require(required.issubset(files), "Initial manifest omits a required model operation resource.")
        package = load(workspace, "outputs/team/package.json")
        require(package.get("scripts", {}).get("models") == "node dist/src/models-cli.js", "Generated project lacks its own model operations command.")
        return {"initial_files_verified": len(files), "policy": live["provider"]["model"], "default": "faux"}
    checks.run("independent_dynamic_example_and_unchanged_hashes", initial_project)

    def selection(path, family, effort):
        receipt = load(workspace, path)
        require(receipt.get("inferencePerformed") is False, "Resolution must not claim to invoke a model.")
        selected = receipt.get("selection")
        require(isinstance(selected, dict) and isinstance(selected.get("model"), dict), "Missing exact selection receipt.")
        reference = selected["model"]
        require(reference.get("provider") == "openai-codex", "Resolution silently changed providers.")
        candidates = catalog.get("models", [])
        matches = [model for model in candidates if model.get("id") == reference.get("modelId")]
        require(len(matches) == 1, "Resolved model is absent or ambiguous in the supplied current inventory.")
        model = matches[0]
        parsed = stable_identity(model)
        require(parsed is not None, "A latest-family selection must resolve a stable recognized numeric model.")
        preferred = [item for item in candidates if stable_identity(item) is not None and stable_identity(item)[0] == family]
        if preferred:
            require(parsed[0] == family, f"Task must prefer the {family} family when that family exists.")
            pool = preferred
        else:
            require(isinstance(selected.get("reason"), str) and "fallback" in selected["reason"].lower(), "Missing preferred family requires a disclosed fallback.")
            pool = [item for item in candidates if stable_identity(item) is not None and stable_identity(item)[0] == parsed[0]]
        best = max((stable_identity(item)[1], stable_identity(item)[2]) for item in pool)
        require((parsed[1], parsed[2]) == best, "Resolved model is not the numerically newest stable member of its selected family.")
        supported = supported_efforts(model)
        actual = selected.get("thinkingLevel")
        require(actual in supported, "Resolved reasoning effort is unsupported by the selected model.")
        require(selected.get("requestedThinkingLevel") == effort, "Task resolution used the wrong default reasoning effort.")
        if effort in supported:
            require(actual == effort, "Resolver changed a supported task-default effort.")
        else:
            require(isinstance(selected.get("reason"), str) and re.search(r"(?i)unavailable|clamp|unsupported", selected["reason"]), "A clamped default requires an explanation.")
        native = model.get("thinkingLevelMap", {}).get(actual)
        if isinstance(native, str):
            require(selected.get("effectiveThinkingLevel") == native, "Native effort mapping contradicts the catalog.")
        source = selected.get("sourceModel")
        if source is not None:
            require(isinstance(source, dict) and source.get("id") == model["id"] and source.get("provider") == model["provider"], "Selection's source metadata identifies another model.")
            require(source.get("thinkingLevelMap", {}) == model.get("thinkingLevelMap", {}), "Selection used another reasoning map than the listed inventory.")
        require(no_numeric_intelligence(selected), "Selection fabricates a numerical intelligence score.")
        context = receipt.get("catalog")
        require(isinstance(context, dict) and context.get("source") == "pi-public" and context.get("availability") == "catalog-only", "Resolution mislabels public metadata as a live entitlement check.")
        return {"model": reference, "preferred_family": family, "actual_family": parsed[0], "effort": actual,
                "supported_efforts": sorted(supported, key=LEVELS.index)}
    checks.run("coding_uses_latest_sol_and_medium_effort", lambda: selection("outputs/coding.json", "sol", "medium"))
    checks.run("review_uses_latest_astra_and_high_effort", lambda: selection("outputs/review.json", "astra", "high"))

    def report_artifacts():
        report = inside(workspace, "outputs/report.md").read_text(encoding="utf-8")
        require(len(report.strip()) >= 200, "Operational report is missing or too small for manual review.")
        claims = load(workspace, "outputs/check.json")
        require(claims, "Candidate check artifact must contain its observations.")
        return {"report_characters": len(report), "candidate_claim_keys": sorted(claims), "candidate_claims_are_not_verification": True,
                "manual_review": ["Task/family/effort explanation", "Catalog visibility versus server entitlement", "No-inference source commands", "Freshness and restart policy", "Pinned evolution and unsupported-level behavior"]}
    checks.run("report_and_candidate_claims_are_reviewable", report_artifacts)
    return {"passed": all(item["passed"] for item in checks.results), "workspace": str(workspace), "checks": checks.results,
            "scope": "Independent artifact, numeric ordering and public capability-map checks; no network, credential reads or inference.",
            "limitations": "Files alone cannot prove source execution, account entitlement, live inference quality, private isolation or native macOS operation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--output", type=Path, help="Optional new evaluator-owned JSON path outside the candidate workspace.")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    require(workspace.is_dir(), "Expected an existing candidate workspace.")
    if args.output:
        output = args.output.resolve()
        require(not output.is_relative_to(workspace), "Evaluator output must not overwrite or enter the candidate workspace.")
    try:
        result = validate(workspace)
    except (AssertionError, OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as error:
        result = {"passed": False, "checks": [], "error": str(error) or type(error).__name__}
    if args.output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
