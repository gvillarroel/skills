#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent offline audit for the Pi context-rot simulation bundle.

The audit deliberately does not import either simulation implementation. It
reconstructs trajectories, context exposure, evidence survival, retry
economics, and paired Monte Carlo gates from exported data using only Python's
standard library. It never calls Pi, Copilot, a model API, or the network.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import random
import sys
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from itertools import pairwise
from pathlib import Path
from typing import Any

ABS_TOL = Decimal("0.000000001")
REL_TOL = Decimal("0.00000001")
FLOAT_TOL = 1e-9
AI_CREDIT_USD = Decimal("0.01")
EXPOSURE_UNIT_TOKENS = 100_000
PRIMARY_ASSUMPTION_ID = "primary-onset-200k-half-odds-f095-k3-uniform"
SOURCE_CONTRAST_ID = "long-cap-200k-uncached"
MODELS = ("luna", "terra", "sol")
COMPLETION_SLO = 0.95
TASK_STRATA: dict[str, tuple[float, float]] = {
    "easy": (0.25, 0.95),
    "typical": (0.50, 0.80),
    "hard": (0.25, 0.55),
}

REQUIRED_CONTEXT_FILES = (
    "trajectory-metrics.csv",
    "quality-stratum-results.csv.gz",
    "quality-aggregate-results.csv.gz",
    "quality-contrast-results.csv.gz",
    "break-even.csv.gz",
    "scale-results.csv.gz",
    "monte-carlo-summary.csv",
    "fidelity-boundaries.csv",
    "evidence-curves.csv",
    "evidence-onsets.csv",
    "study-results.json",
    "data-dictionary.json",
    "explore.sql",
    "summary.md",
    "manifest.json",
    "checksums.sha256",
)
GZIP_CONTEXT_FILES = (
    "quality-stratum-results.csv.gz",
    "quality-aggregate-results.csv.gz",
    "quality-contrast-results.csv.gz",
    "break-even.csv.gz",
    "scale-results.csv.gz",
)
LEGACY_RAW_CONTEXT_FILES = tuple(
    name.removesuffix(".gz") for name in GZIP_CONTEXT_FILES
)

REQUIRED_COST_FILES = (
    "scenario-results.csv",
    "call-ledger.csv",
    "manifest.json",
    "checksums.sha256",
    "independent-validation-report.json",
)

EXPECTED_SOURCE_COSTS: dict[tuple[str, str], Decimal] = {
    ("luna", "grow_to_800k"): Decimal("1.0204"),
    ("luna", "cap_200k_uncached"): Decimal("0.5952"),
    ("terra", "grow_to_800k"): Decimal("9.904"),
    ("terra", "cap_200k_uncached"): Decimal("5.952"),
    ("sol", "grow_to_800k"): Decimal("19.598"),
    ("sol", "cap_200k_uncached"): Decimal("11.428"),
}

GROW_PROMPTS = tuple(range(40_000, 800_001, 20_000))
CAP_PROMPTS = tuple(
    [value for _ in range(4) for value in range(40_000, 200_001, 20_000)]
    + [40_000, 60_000, 80_000]
)
COMPACTION_LOGICAL_POSITIONS = (9, 18, 27, 36)

SOURCE_STRATEGY_ORIGINS: dict[str, tuple[str, str]] = {
    "grow_to_800k": ("long-cap-200k-uncached", "baseline"),
    "cap_200k_uncached": ("long-cap-200k-uncached", "comparison"),
    "cap_200k_cache_read": (
        "compaction-input-cache-read-sensitivity",
        "comparison",
    ),
    "cap_200k_cache_write": (
        "compaction-input-cache-write-sensitivity",
        "comparison",
    ),
    "cap_pricing_threshold_uncached": (
        "long-cap-pricing-threshold-uncached",
        "comparison",
    ),
}


@dataclass
class Audit:
    checks: int = 0
    failures: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    def check(self, condition: bool, code: str, message: str, **context: Any) -> bool:
        self.checks += 1
        if not condition:
            finding: dict[str, Any] = {"code": code, "message": message}
            if context:
                finding["context"] = _json_safe(context)
            self.failures.append(finding)
        return condition

    def warn(self, code: str, message: str, **context: Any) -> None:
        finding: dict[str, Any] = {"code": code, "message": message}
        if context:
            finding["context"] = _json_safe(context)
        self.warnings.append(finding)

    def as_report(self, bundle: Path, cost_bundle: Path) -> dict[str, Any]:
        manifest_path = bundle / "manifest.json"
        checksums_path = bundle / "checksums.sha256"
        return {
            "schema_version": "1.0",
            "validator": "independent-pi-context-rot-audit",
            "mode": "offline-independent-validation",
            "bundle": str(bundle.resolve()),
            "cost_source_bundle": str(cost_bundle.resolve()),
            "bundle_manifest_sha256": (
                _sha256(manifest_path) if manifest_path.is_file() else None
            ),
            "bundle_checksums_sha256": (
                _sha256(checksums_path) if checksums_path.is_file() else None
            ),
            "status": "pass" if not self.failures else "fail",
            "checks": self.checks,
            "failure_count": len(self.failures),
            "warning_count": len(self.warnings),
            "failures": self.failures,
            "warnings": self.warnings,
            "no_external_calls": True,
        }


@dataclass(frozen=True)
class SourceScenario:
    model: str
    strategy: str
    scenario_id: str
    provider_cost_usd: Decimal
    main_prompts: tuple[int, ...]
    compaction_positions: tuple[int, ...]


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_csv(path: Path, audit: Audit) -> list[dict[str, str]]:
    try:
        with (
            gzip.open(path, "rt", encoding="utf-8-sig", newline="")
            if path.suffix == ".gz"
            else path.open("r", encoding="utf-8-sig", newline="")
        ) as handle:
            reader = csv.DictReader(handle)
            audit.check(
                bool(reader.fieldnames),
                "csv.header",
                "CSV requires a header.",
                path=path,
            )
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        audit.check(False, "csv.read", "Could not read CSV.", path=path, error=str(exc))
        return []
    audit.check(bool(rows), "csv.nonempty", "CSV requires at least one row.", path=path)
    return rows


def _read_json(path: Path, audit: Audit) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        audit.check(
            False, "json.read", "Could not read valid JSON.", path=path, error=str(exc)
        )
        return {}


def _text(row: Mapping[str, Any], *names: str, default: str = "") -> str:
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return default


def _dec(
    row: Mapping[str, Any], *names: str, default: Decimal | None = None
) -> Decimal | None:
    raw = _text(row, *names)
    if not raw:
        return default
    try:
        value = Decimal(raw)
    except InvalidOperation:
        return None
    return value if value.is_finite() else None


def _flt(
    row: Mapping[str, Any], *names: str, default: float | None = None
) -> float | None:
    value = _dec(row, *names)
    return float(value) if value is not None else default


def _int(row: Mapping[str, Any], *names: str, default: int | None = None) -> int | None:
    value = _dec(row, *names)
    if value is None:
        return default
    if value != value.to_integral_value():
        return None
    return int(value)


def _bool(row: Mapping[str, Any], *names: str) -> bool | None:
    raw = _text(row, *names).lower()
    if raw in {"true", "1", "yes"}:
        return True
    if raw in {"false", "0", "no"}:
        return False
    return None


def _close(left: Decimal | None, right: Decimal | None) -> bool:
    if left is None or right is None:
        return False
    return abs(left - right) <= max(ABS_TOL, REL_TOL * max(abs(left), abs(right)))


def _float_close(
    left: float | None, right: float | None, *, tol: float = FLOAT_TOL
) -> bool:
    if (
        left is None
        or right is None
        or not math.isfinite(left)
        or not math.isfinite(right)
    ):
        return False
    return math.isclose(left, right, rel_tol=1e-8, abs_tol=tol)


def _canonical_model(value: str) -> str | None:
    lowered = value.lower()
    return next((model for model in MODELS if model in lowered), None)


def _canonical_strategy(value: str, role: str = "") -> str | None:
    lowered = value.lower().replace("-", "_")
    if lowered in SOURCE_STRATEGY_ORIGINS:
        return lowered
    if "pricing_threshold" in lowered:
        return "cap_pricing_threshold_uncached"
    if "cache_read" in lowered:
        return "cap_200k_cache_read"
    if "cache_write" in lowered:
        return "cap_200k_cache_write"
    if "uncached" in lowered and ("cap" in lowered or "compact" in lowered):
        return "cap_200k_uncached"
    if "grow" in lowered or "800k" in lowered or role.lower() == "baseline":
        return "grow_to_800k"
    if "cap" in lowered or "compact" in lowered or role.lower() == "comparison":
        return "cap_200k_uncached"
    return None


def _stable_logistic(log_odds: float) -> float:
    if log_odds >= 0:
        return 1.0 / (1.0 + math.exp(-log_odds))
    exp_value = math.exp(log_odds)
    return exp_value / (1.0 + exp_value)


def _logit(probability: float) -> float:
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must be strictly between zero and one")
    return math.log(probability / (1.0 - probability))


def _context_exposure(
    prompts: Sequence[int], onset_tokens: float
) -> dict[str, float | int | None]:
    if not prompts or onset_tokens <= 0:
        raise ValueError("prompts must be non-empty and onset_tokens positive")
    excess = [max(prompt - onset_tokens, 0) for prompt in prompts]
    above = [index + 1 for index, amount in enumerate(excess) if amount > 0]
    area = sum(excess)
    # Keep the unit fixed across onset sensitivities. Otherwise the same beta
    # would silently change meaning when only the onset is varied.
    normalized = area / (EXPOSURE_UNIT_TOKENS * len(prompts))
    return {
        "first_call_above_onset": above[0] if above else None,
        "calls_above_onset": len(above),
        "fraction_calls_above_onset": len(above) / len(prompts),
        "peak_context_tokens": max(prompts),
        "peak_excess_tokens": max(excess),
        "excess_token_call_area": area,
        "normalized_excess_units": normalized,
    }


def _uniform_effective_fidelity(
    main_calls: int,
    compaction_positions: Sequence[int],
    fidelity: float,
) -> float:
    if main_calls <= 0 or not 0.0 <= fidelity <= 1.0:
        raise ValueError("invalid evidence-fidelity inputs")
    survival = 0.0
    for evidence_call in range(1, main_calls + 1):
        summaries_crossed = sum(
            1 for position in compaction_positions if position >= evidence_call
        )
        survival += fidelity**summaries_crossed
    return survival / main_calls


def _profile_weights(call_count: int, profile: str) -> list[float]:
    if profile == "uniform":
        return [1.0] * call_count
    if profile == "front_loaded":
        return [float(call_count - index + 1) for index in range(1, call_count + 1)]
    if profile == "back_loaded":
        return [float(index) for index in range(1, call_count + 1)]
    raise ValueError(f"unknown evidence profile: {profile}")


def _effective_fidelity(
    main_calls: int,
    compaction_positions: Sequence[int],
    fidelity: float,
    profile: str,
) -> float:
    if not 0.0 <= fidelity <= 1.0:
        raise ValueError("fidelity must be in [0,1]")
    weights = _profile_weights(main_calls, profile)
    weighted = 0.0
    for call_index, weight in enumerate(weights, start=1):
        losses = sum(position >= call_index for position in compaction_positions)
        weighted += weight * fidelity**losses
    return weighted / sum(weights)


def _single_attempt_probability(
    baseline_probability: float,
    beta: float,
    normalized_excess_auc: float,
    effective_fidelity: float,
) -> float:
    if beta < 0.0 or normalized_excess_auc < 0.0 or not 0.0 < effective_fidelity <= 1.0:
        raise ValueError("invalid quality-curve inputs")
    return _stable_logistic(
        _logit(baseline_probability)
        - beta * normalized_excess_auc
        + math.log(effective_fidelity)
    )


def _json_int_list(raw: str) -> tuple[int, ...] | None:
    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return None
    if not isinstance(value, list) or any(
        isinstance(item, bool) or not isinstance(item, int) for item in value
    ):
        return None
    return tuple(value)


def _retry_exact(
    probability: float, per_attempt_cost: float, max_attempts: int
) -> dict[str, float]:
    if not 0.0 <= probability <= 1.0 or per_attempt_cost < 0 or max_attempts < 1:
        raise ValueError("invalid retry inputs")
    failure = 1.0 - probability
    completion = 1.0 - failure**max_attempts
    expected_attempts = sum(failure**index for index in range(max_attempts))
    assigned_cost = per_attempt_cost * expected_attempts
    cost_per_success = assigned_cost / completion if completion > 0 else math.inf
    return {
        "completion_probability": completion,
        "unresolved_probability": 1.0 - completion,
        "expected_attempts": expected_attempts,
        "provider_cost_usd_per_assigned_task": assigned_cost,
        "provider_cost_usd_per_successful_task": cost_per_success,
    }


def _parse_checksums(path: Path, audit: Audit) -> dict[str, str]:
    entries: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        audit.check(
            False,
            "hash.read",
            "Could not read checksums file.",
            path=path,
            error=str(exc),
        )
        return entries
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        pieces = line.split(None, 1)
        valid = len(pieces) == 2 and len(pieces[0]) == 64
        audit.check(
            valid,
            "hash.format",
            "Checksum rows require a 64-character digest and relative filename.",
            path=path,
            line=line_number,
        )
        if not valid:
            continue
        digest, filename = pieces[0].lower(), pieces[1].strip().lstrip("*")
        audit.check(
            filename not in entries,
            "hash.duplicate",
            "Checksum filename must be unique.",
            filename=filename,
        )
        entries[filename] = digest
    return entries


def _audit_checksum_inventory(
    root: Path,
    checksum_name: str,
    audit: Audit,
    *,
    required_names: Iterable[str] = (),
) -> dict[str, str]:
    checksums = _parse_checksums(root / checksum_name, audit)
    for filename in required_names:
        if filename == checksum_name:
            continue
        audit.check(
            filename in checksums,
            "hash.missing_entry",
            "Checksums inventory is missing a required artifact.",
            root=root,
            filename=filename,
        )
    for filename, expected in checksums.items():
        target = root / filename
        if not audit.check(
            target.is_file(),
            "hash.missing_file",
            "Checksummed artifact is missing.",
            path=target,
        ):
            continue
        observed = _sha256(target)
        audit.check(
            observed == expected,
            "hash.mismatch",
            "Artifact SHA-256 differs from the checksum inventory.",
            path=target,
            expected=expected,
            observed=observed,
        )
    return checksums


def _audit_manifest_hashes(
    root: Path, manifest: Mapping[str, Any], audit: Audit
) -> None:
    hashes = manifest.get("sha256")
    if not audit.check(
        isinstance(hashes, Mapping),
        "manifest.hashes",
        "Manifest must contain a sha256 object.",
        root=root,
    ):
        return
    for filename, expected in hashes.items():
        target = root / str(filename)
        if not audit.check(
            target.is_file(),
            "manifest.hash_file",
            "Manifest-hashed file is missing.",
            path=target,
        ):
            continue
        observed = _sha256(target)
        audit.check(
            observed == str(expected),
            "manifest.hash_mismatch",
            "Manifest SHA-256 does not match artifact bytes.",
            path=target,
            expected=expected,
            observed=observed,
        )


def _audit_json_finite(value: Any, audit: Audit, path: str = "$") -> None:
    if isinstance(value, float):
        audit.check(
            math.isfinite(value),
            "finite.json_number",
            "Generated JSON must not contain NaN or infinity.",
            json_path=path,
            value=value,
        )
    elif isinstance(value, Mapping):
        for key, child in value.items():
            _audit_json_finite(child, audit, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _audit_json_finite(child, audit, f"{path}[{index}]")


def _audit_context_manifest(
    bundle: Path,
    manifest: Mapping[str, Any],
    table_rows: Mapping[str, Sequence[Mapping[str, str]]],
    cost_bundle: Path,
    audit: Audit,
) -> None:
    artifacts = manifest.get("artifacts")
    if not audit.check(
        isinstance(artifacts, Mapping),
        "manifest.artifacts",
        "Context manifest must contain an artifacts object.",
    ):
        return
    expected_artifacts = set(REQUIRED_CONTEXT_FILES) - {
        "manifest.json",
        "checksums.sha256",
    }
    audit.check(
        set(map(str, artifacts)) == expected_artifacts,
        "manifest.artifact_inventory",
        "Manifest artifact inventory must exactly cover generated non-manifest artifacts.",
        expected=sorted(expected_artifacts),
        observed=sorted(map(str, artifacts)),
    )
    for filename, metadata in artifacts.items():
        target = bundle / str(filename)
        context = {"filename": filename}
        if not audit.check(
            isinstance(metadata, Mapping) and target.is_file(),
            "manifest.artifact",
            "Manifest artifact metadata and file are required.",
            **context,
        ):
            continue
        observed_hash = _sha256(target)
        audit.check(
            metadata.get("sha256") == observed_hash,
            "manifest.artifact_hash",
            "Manifest artifact hash differs from file bytes.",
            expected=metadata.get("sha256"),
            observed=observed_hash,
            **context,
        )
        audit.check(
            _int(metadata, "bytes") == target.stat().st_size,
            "manifest.artifact_bytes",
            "Manifest artifact byte count differs from the file.",
            expected=target.stat().st_size,
            observed=metadata.get("bytes"),
            **context,
        )
        if filename in table_rows:
            audit.check(
                _int(metadata, "rows") == len(table_rows[str(filename)]),
                "manifest.artifact_rows",
                "Manifest row count differs from the CSV.",
                expected=len(table_rows[str(filename)]),
                observed=metadata.get("rows"),
                **context,
            )
        if filename in GZIP_CONTEXT_FILES:
            try:
                stored_bytes = target.read_bytes()
                logical_bytes = gzip.decompress(stored_bytes)
            except (OSError, EOFError) as exc:
                audit.check(
                    False,
                    "manifest.gzip_read",
                    "Gzip artifact must have a valid stream, CRC, and length.",
                    error=str(exc),
                    **context,
                )
                continue
            audit.check(
                len(stored_bytes) >= 10 and stored_bytes[:3] == b"\x1f\x8b\x08",
                "manifest.gzip_magic",
                "Gzip artifact must use the standard deflate header.",
                **context,
            )
            if len(stored_bytes) >= 10:
                audit.check(
                    stored_bytes[3] == 0,
                    "manifest.gzip_flags",
                    "Deterministic gzip must omit optional header fields.",
                    observed=stored_bytes[3],
                    **context,
                )
                audit.check(
                    int.from_bytes(stored_bytes[4:8], "little") == 0,
                    "manifest.gzip_mtime",
                    "Deterministic gzip must use MTIME=0.",
                    observed=int.from_bytes(stored_bytes[4:8], "little"),
                    **context,
                )
                audit.check(
                    stored_bytes[8] == 2,
                    "manifest.gzip_xfl",
                    "Compression level 9 must set the maximum-compression XFL marker.",
                    observed=stored_bytes[8],
                    **context,
                )
                audit.check(
                    stored_bytes[9] == 255,
                    "manifest.gzip_os",
                    "Deterministic Python gzip must use the unknown-OS marker.",
                    observed=stored_bytes[9],
                    **context,
                )
            audit.check(
                metadata.get("uncompressed_sha256")
                == hashlib.sha256(logical_bytes).hexdigest(),
                "manifest.gzip_logical_hash",
                "Manifest uncompressed hash must match the logical CSV bytes.",
                **context,
            )
            audit.check(
                _int(metadata, "uncompressed_bytes") == len(logical_bytes),
                "manifest.gzip_logical_bytes",
                "Manifest uncompressed byte count must match the logical CSV bytes.",
                **context,
            )
            compression = metadata.get("compression")
            audit.check(
                isinstance(compression, Mapping)
                and compression.get("format") == "gzip"
                and _int(compression, "level") == 9
                and _int(compression, "mtime") == 0
                and compression.get("original_filename") == ""
                and bool(str(compression.get("python_version", "")).strip())
                and bool(str(compression.get("zlib_build_version", "")).strip())
                and bool(str(compression.get("zlib_runtime_version", "")).strip()),
                "manifest.gzip_provenance",
                "Manifest must record the frozen gzip settings and generation runtime.",
                **context,
            )

    input_files = manifest.get("input_files")
    if not audit.check(
        isinstance(input_files, Mapping),
        "manifest.input_files",
        "Manifest must identify immutable input files and hashes.",
    ):
        return
    for filename in ("scenario-results.csv", "call-ledger.csv"):
        metadata = input_files.get(filename)
        expected_hash = _sha256(cost_bundle / filename)
        audit.check(
            isinstance(metadata, Mapping) and metadata.get("sha256") == expected_hash,
            "manifest.cost_input_hash",
            "Manifest cost-source hash must match the supplied versioned bundle.",
            filename=filename,
            expected=expected_hash,
            observed=metadata.get("sha256") if isinstance(metadata, Mapping) else None,
        )
    for filename, metadata in input_files.items():
        if filename in {"scenario-results.csv", "call-ledger.csv"}:
            continue
        candidate = Path(__file__).resolve().parents[1] / "source" / str(filename)
        if candidate.is_file():
            audit.check(
                isinstance(metadata, Mapping)
                and metadata.get("sha256") == _sha256(candidate),
                "manifest.aux_input_hash",
                "Manifest auxiliary-input hash differs from the versioned source file.",
                filename=filename,
                source_path=candidate,
            )
        else:
            audit.warn(
                "manifest.aux_input_unavailable",
                "Auxiliary input could not be independently located; its recorded hash was retained.",
                filename=filename,
            )


def _audit_no_nonfinite(
    rows: Sequence[Mapping[str, str]], table: str, audit: Audit
) -> None:
    forbidden = {
        "nan",
        "+nan",
        "-nan",
        "inf",
        "+inf",
        "-inf",
        "infinity",
        "+infinity",
        "-infinity",
    }
    for row_number, row in enumerate(rows, start=2):
        for field_name, raw in row.items():
            audit.check(
                str(raw).strip().lower() not in forbidden,
                "finite.nonfinite",
                "Generated CSV must not encode NaN or infinity.",
                table=table,
                row=row_number,
                field=field_name,
                value=raw,
            )


def _load_source_cost_bundle(
    cost_bundle: Path, audit: Audit
) -> dict[tuple[str, str], SourceScenario]:
    audit.check(
        cost_bundle.is_dir(),
        "cost_source.directory",
        "Cost source bundle must be a directory.",
        path=cost_bundle,
    )
    for filename in REQUIRED_COST_FILES:
        audit.check(
            (cost_bundle / filename).is_file(),
            "cost_source.file",
            "Cost source file is missing.",
            path=cost_bundle / filename,
        )
    if audit.failures:
        return {}

    _audit_checksum_inventory(
        cost_bundle,
        "checksums.sha256",
        audit,
        required_names=REQUIRED_COST_FILES,
    )
    manifest_raw = _read_json(cost_bundle / "manifest.json", audit)
    manifest = manifest_raw if isinstance(manifest_raw, Mapping) else {}
    audit.check(
        manifest.get("execution_mode") == "deterministic-offline-simulation",
        "cost_source.execution_mode",
        "Cost source must be the deterministic offline simulation bundle.",
        observed=manifest.get("execution_mode"),
    )
    audit.check(
        manifest.get("real_pi_or_copilot_calls") is False,
        "cost_source.no_real_calls",
        "Cost source must explicitly report no real Pi or Copilot calls.",
        observed=manifest.get("real_pi_or_copilot_calls"),
    )
    _audit_manifest_hashes(cost_bundle, manifest, audit)
    independent = _read_json(cost_bundle / "independent-validation-report.json", audit)
    audit.check(
        isinstance(independent, Mapping) and independent.get("status") == "pass",
        "cost_source.independent_validation",
        "Cost source must have a passing independent validation report.",
        observed=independent.get("status")
        if isinstance(independent, Mapping)
        else None,
    )

    scenario_rows = _read_csv(cost_bundle / "scenario-results.csv", audit)
    ledger_rows = _read_csv(cost_bundle / "call-ledger.csv", audit)
    _audit_no_nonfinite(scenario_rows, "cost-source/scenario-results.csv", audit)
    _audit_no_nonfinite(ledger_rows, "cost-source/call-ledger.csv", audit)
    source: dict[tuple[str, str], SourceScenario] = {}
    for model in MODELS:
        pricing_cap_prompts = (
            CAP_PROMPTS
            if model == "luna"
            else tuple(
                [value for _ in range(3) for value in range(40_000, 260_001, 20_000)]
                + [40_000, 60_000, 80_000]
            )
        )
        pricing_cap_positions = (
            COMPACTION_LOGICAL_POSITIONS if model == "luna" else (12, 24, 36)
        )
        for strategy, (contrast_id, role) in SOURCE_STRATEGY_ORIGINS.items():
            if strategy == "grow_to_800k":
                expected_prompts, expected_compactions = GROW_PROMPTS, ()
            elif strategy == "cap_pricing_threshold_uncached":
                expected_prompts, expected_compactions = (
                    pricing_cap_prompts,
                    pricing_cap_positions,
                )
            else:
                expected_prompts, expected_compactions = (
                    CAP_PROMPTS,
                    COMPACTION_LOGICAL_POSITIONS,
                )
            candidates = [
                row
                for row in scenario_rows
                if _text(row, "contrast_id") == contrast_id
                and _canonical_model(_text(row, "model")) == model
                and _text(row, "role").lower() == role
            ]
            if not audit.check(
                len(candidates) == 1,
                "cost_source.scenario",
                "Expected source-cost scenario must occur exactly once.",
                model=model,
                role=role,
                matches=len(candidates),
            ):
                continue
            scenario = candidates[0]
            scenario_id = _text(scenario, "scenario_id")
            calls = sorted(
                [
                    row
                    for row in ledger_rows
                    if _text(row, "scenario_id") == scenario_id
                ],
                key=lambda row: _int(row, "call_index", default=0) or 0,
            )
            main_prompts = tuple(
                _int(row, "full_input_tokens", default=-1) or 0
                for row in calls
                if _bool(row, "compaction_event") is not True
            )
            compaction_positions = tuple(
                _int(row, "logical_step", default=-1) or 0
                for row in calls
                if _bool(row, "compaction_event") is True
            )
            audit.check(
                main_prompts == expected_prompts,
                "cost_source.trajectory",
                "Source-cost main prompts do not match the preregistered 39-call trajectory.",
                model=model,
                strategy=strategy,
                expected=expected_prompts,
                observed=main_prompts,
            )
            audit.check(
                compaction_positions == expected_compactions,
                "cost_source.compaction_positions",
                "Source-cost compaction positions must be exactly 9, 18, 27, and 36.",
                model=model,
                strategy=strategy,
                expected=expected_compactions,
                observed=compaction_positions,
            )
            ledger_cost = sum(
                (_dec(row, "provider_cost_usd") or Decimal(0) for row in calls),
                Decimal(0),
            )
            summary_cost = _dec(scenario, "provider_cost_usd")
            expected_cost = EXPECTED_SOURCE_COSTS.get((model, strategy), ledger_cost)
            audit.check(
                _close(ledger_cost, summary_cost),
                "cost_source.reconcile",
                "Source scenario cost must equal its call ledger sum.",
                model=model,
                strategy=strategy,
                ledger=ledger_cost,
                scenario=summary_cost,
            )
            if (model, strategy) in EXPECTED_SOURCE_COSTS:
                audit.check(
                    _close(summary_cost, expected_cost),
                    "cost_source.hand_cost",
                    "Source scenario cost differs from the frozen hand oracle.",
                    model=model,
                    strategy=strategy,
                    expected=expected_cost,
                    observed=summary_cost,
                )
            source[(model, strategy)] = SourceScenario(
                model=model,
                strategy=strategy,
                scenario_id=scenario_id,
                provider_cost_usd=expected_cost,
                main_prompts=expected_prompts,
                compaction_positions=expected_compactions,
            )
    return source


def _audit_trajectories(
    rows: Sequence[Mapping[str, str]],
    source: Mapping[tuple[str, str], SourceScenario],
    audit: Audit,
) -> dict[tuple[str, str, float], Mapping[str, str]]:
    lookup: dict[tuple[str, str, float], Mapping[str, str]] = {}
    ids: set[str] = set()
    onset_sets: dict[tuple[str, str], set[float]] = defaultdict(set)
    for row_number, row in enumerate(rows, start=2):
        model = _canonical_model(_text(row, "model"))
        strategy = _canonical_strategy(_text(row, "strategy_id"))
        onset = _flt(row, "onset_tokens")
        context = {
            "table": "trajectory-metrics.csv",
            "row": row_number,
            "model": model,
            "strategy": strategy,
            "onset_tokens": onset,
        }
        if not audit.check(
            model is not None
            and strategy is not None
            and onset is not None
            and onset > 0,
            "trajectory.identity",
            "Trajectory row must identify a known model, strategy, and positive onset.",
            **context,
        ):
            continue
        key = (model, strategy, onset)
        audit.check(
            key not in lookup,
            "trajectory.duplicate",
            "Trajectory key must be unique.",
            **context,
        )
        lookup[key] = row
        onset_sets[(model, strategy)].add(onset)
        trajectory_id = _text(row, "trajectory_id")
        audit.check(
            bool(trajectory_id) and trajectory_id not in ids,
            "trajectory.id",
            "trajectory_id must be non-empty and unique.",
            trajectory_id=trajectory_id,
            **context,
        )
        ids.add(trajectory_id)
        source_scenario = source.get((model, strategy))
        if not audit.check(
            source_scenario is not None,
            "trajectory.source",
            "Trajectory must resolve to one independently audited cost-source scenario.",
            **context,
        ):
            continue
        prompts = _json_int_list(_text(row, "prompt_sequence_tokens_json"))
        positions = _json_int_list(_text(row, "compaction_positions_json"))
        audit.check(
            prompts == source_scenario.main_prompts,
            "trajectory.prompt_sequence",
            "Exported prompt sequence differs from the source cost ledger.",
            expected=source_scenario.main_prompts,
            observed=prompts,
            **context,
        )
        audit.check(
            positions == source_scenario.compaction_positions,
            "trajectory.compaction_positions",
            "Exported compaction positions differ from the source cost ledger.",
            expected=source_scenario.compaction_positions,
            observed=positions,
            **context,
        )
        audit.check(
            _text(row, "source_scenario_id") == source_scenario.scenario_id,
            "trajectory.source_scenario_id",
            "Trajectory source_scenario_id differs from the independently selected source row.",
            expected=source_scenario.scenario_id,
            observed=_text(row, "source_scenario_id"),
            **context,
        )
        audit.check(
            _close(
                _dec(row, "provider_cost_per_attempt_usd"),
                source_scenario.provider_cost_usd,
            ),
            "trajectory.source_cost",
            "Per-attempt cost differs from the source cost scenario.",
            expected=source_scenario.provider_cost_usd,
            observed=_dec(row, "provider_cost_per_attempt_usd"),
            **context,
        )
        if prompts is None:
            continue
        # Evidence-derived onset sensitivities may be fractional.  Preserve the
        # exact exported threshold instead of silently truncating it to an
        # integer before reconstructing excess token-call area.
        expected_metrics = _context_exposure(prompts, onset)
        audit.check(
            _int(row, "main_call_count") == len(prompts) == 39,
            "trajectory.main_calls",
            "Every quality trajectory must contain exactly 39 main calls.",
            observed=_int(row, "main_call_count"),
            **context,
        )
        audit.check(
            _int(row, "compaction_count") == len(source_scenario.compaction_positions),
            "trajectory.compaction_count",
            "Compaction count must match the source trajectory.",
            expected=len(source_scenario.compaction_positions),
            observed=_int(row, "compaction_count"),
            **context,
        )
        audit.check(
            _int(row, "minimum_prompt_tokens") == min(prompts),
            "trajectory.minimum",
            "Minimum prompt size is incorrect.",
            **context,
        )
        audit.check(
            _float_close(_flt(row, "mean_prompt_tokens"), sum(prompts) / len(prompts)),
            "trajectory.mean",
            "Mean prompt size is incorrect.",
            **context,
        )
        audit.check(
            _int(row, "maximum_prompt_tokens") == max(prompts),
            "trajectory.maximum",
            "Maximum prompt size is incorrect.",
            **context,
        )
        audit.check(
            _float_close(
                _flt(row, "excess_token_call_area"),
                float(expected_metrics["excess_token_call_area"]),
            ),
            "trajectory.excess_area",
            "Excess token-call area is incorrect.",
            expected=expected_metrics["excess_token_call_area"],
            observed=_flt(row, "excess_token_call_area"),
            **context,
        )
        audit.check(
            _float_close(
                _flt(row, "normalized_excess_auc"),
                float(expected_metrics["normalized_excess_units"]),
            ),
            "trajectory.exposure",
            "Normalized excess AUC must use a fixed 100,000-token unit.",
            expected=expected_metrics["normalized_excess_units"],
            observed=_flt(row, "normalized_excess_auc"),
            **context,
        )
        formula = _text(row, "normalization_formula").replace(" ", "").lower()
        audit.check(
            "100000" in formula and "onset*" not in formula,
            "trajectory.formula_label",
            "Normalization formula must visibly use the fixed 100,000-token unit.",
            observed=_text(row, "normalization_formula"),
            **context,
        )
        audit.check(
            _text(row, "source_type") == "simulated",
            "trajectory.source_type",
            "Generated trajectory rows must be labeled source_type=simulated.",
            **context,
        )

    onset_cardinalities = {len(values) for values in onset_sets.values()}
    audit.check(
        len(onset_sets) == len(source)
        and len(onset_cardinalities) == 1
        and next(iter(onset_cardinalities), 0) > 0,
        "trajectory.coverage",
        "Every source model/strategy must have the same nonzero onset coverage.",
        source_pairs=len(source),
        observed_pairs=len(onset_sets),
        onset_counts=sorted(onset_cardinalities),
    )
    return lookup


def _quality_key(row: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        _text(row, "parameter_set_id"),
        _canonical_model(_text(row, "model")) or _text(row, "model"),
        _canonical_strategy(_text(row, "strategy_id")) or _text(row, "strategy_id"),
    )


def _audit_strata(
    rows: Sequence[Mapping[str, str]],
    trajectories: Mapping[tuple[str, str, float], Mapping[str, str]],
    source: Mapping[tuple[str, str], SourceScenario],
    audit: Audit,
) -> dict[tuple[str, str, str, str], Mapping[str, str]]:
    lookup: dict[tuple[str, str, str, str], Mapping[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        parameter_id, model, strategy = _quality_key(row)
        stratum_id = _text(row, "stratum_id")
        onset = _flt(row, "onset_tokens")
        key = (parameter_id, model, strategy, stratum_id)
        context = {
            "table": "quality-stratum-results.csv.gz",
            "row": row_number,
            "parameter_set_id": parameter_id,
            "model": model,
            "strategy": strategy,
            "stratum_id": stratum_id,
        }
        if not audit.check(
            parameter_id
            and model in MODELS
            and strategy in SOURCE_STRATEGY_ORIGINS
            and stratum_id in TASK_STRATA
            and onset is not None,
            "stratum.identity",
            "Stratum row must identify a valid parameter set, model, strategy, stratum, and onset.",
            **context,
        ):
            continue
        audit.check(
            key not in lookup,
            "stratum.duplicate",
            "Stratum result key must be unique.",
            **context,
        )
        lookup[key] = row
        trajectory = trajectories.get((model, strategy, onset))
        source_scenario = source.get((model, strategy))
        if not audit.check(
            trajectory is not None and source_scenario is not None,
            "stratum.trajectory",
            "Stratum row must resolve to a trajectory and source-cost scenario.",
            onset_tokens=onset,
            **context,
        ):
            continue
        beta = _flt(row, "beta")
        fidelity = _flt(row, "per_compaction_fidelity")
        profile = _text(row, "evidence_profile")
        max_attempts = _int(row, "max_attempts")
        weight, baseline_probability = TASK_STRATA[stratum_id]
        valid_inputs = (
            beta is not None
            and beta >= 0
            and fidelity is not None
            and 0 <= fidelity <= 1
            and profile in {"uniform", "front_loaded", "back_loaded"}
            and max_attempts is not None
            and max_attempts >= 1
        )
        if not audit.check(
            valid_inputs,
            "stratum.parameters",
            "Quality and retry inputs must be valid and finite.",
            beta=beta,
            fidelity=fidelity,
            profile=profile,
            max_attempts=max_attempts,
            **context,
        ):
            continue
        assert beta is not None and fidelity is not None and max_attempts is not None
        positions = source_scenario.compaction_positions
        expected_effective_fidelity = _effective_fidelity(
            39, positions, fidelity, profile
        )
        exposure = _flt(trajectory, "normalized_excess_auc")
        if exposure is None:
            continue
        expected_probability = _single_attempt_probability(
            baseline_probability,
            beta,
            exposure,
            expected_effective_fidelity,
        )
        retry = _retry_exact(
            expected_probability,
            float(source_scenario.provider_cost_usd),
            max_attempts,
        )
        numeric_checks: dict[str, float] = {
            "stratum_weight": weight,
            "baseline_success_probability": baseline_probability,
            "normalized_excess_auc": exposure,
            "effective_evidence_fidelity": expected_effective_fidelity,
            "single_attempt_success_probability": expected_probability,
            "completion_probability": retry["completion_probability"],
            "expected_attempts": retry["expected_attempts"],
            "provider_cost_per_attempt_usd": float(source_scenario.provider_cost_usd),
            "weighted_completion_contribution": weight
            * retry["completion_probability"],
            "weighted_attempts_contribution": weight * retry["expected_attempts"],
            "weighted_assigned_cost_contribution_usd": (
                weight * retry["provider_cost_usd_per_assigned_task"]
            ),
        }
        for field_name, expected in numeric_checks.items():
            observed = _flt(row, field_name)
            audit.check(
                _float_close(observed, expected),
                "stratum.formula",
                "Stratum field differs from the independent quality/retry formula.",
                field=field_name,
                expected=expected,
                observed=observed,
                **context,
            )
        audit.check(
            _text(row, "source_scenario_id") == source_scenario.scenario_id,
            "stratum.source_scenario",
            "Stratum source scenario differs from the independently audited cost source.",
            expected=source_scenario.scenario_id,
            observed=_text(row, "source_scenario_id"),
            **context,
        )
        audit.check(
            _text(row, "source_type") == "simulated",
            "stratum.source_type",
            "Generated quality rows must be labeled source_type=simulated.",
            **context,
        )
    return lookup


def _audit_aggregates(
    rows: Sequence[Mapping[str, str]],
    strata: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    source: Mapping[tuple[str, str], SourceScenario],
    audit: Audit,
) -> dict[tuple[str, str, str], Mapping[str, str]]:
    lookup: dict[tuple[str, str, str], Mapping[str, str]] = {}
    cost_sets: dict[tuple[str, str], set[Decimal]] = defaultdict(set)
    for row_number, row in enumerate(rows, start=2):
        key = _quality_key(row)
        parameter_id, model, strategy = key
        context = {
            "table": "quality-aggregate-results.csv.gz",
            "row": row_number,
            "parameter_set_id": parameter_id,
            "model": model,
            "strategy": strategy,
        }
        if not audit.check(
            parameter_id and model in MODELS and strategy in SOURCE_STRATEGY_ORIGINS,
            "aggregate.identity",
            "Aggregate row must identify a valid parameter set, model, and strategy.",
            **context,
        ):
            continue
        audit.check(
            key not in lookup,
            "aggregate.duplicate",
            "Aggregate result key must be unique.",
            **context,
        )
        lookup[key] = row
        members = [strata.get((*key, stratum_id)) for stratum_id in TASK_STRATA]
        if not audit.check(
            all(member is not None for member in members),
            "aggregate.strata",
            "Aggregate requires exactly the three declared task strata.",
            **context,
        ):
            continue
        typed_members = [member for member in members if member is not None]
        weighted_baseline = sum(
            (_flt(member, "stratum_weight") or 0.0)
            * (_flt(member, "baseline_success_probability") or 0.0)
            for member in typed_members
        )
        weighted_single = sum(
            (_flt(member, "stratum_weight") or 0.0)
            * (_flt(member, "single_attempt_success_probability") or 0.0)
            for member in typed_members
        )
        completion = sum(
            _flt(member, "weighted_completion_contribution") or 0.0
            for member in typed_members
        )
        attempts = sum(
            _flt(member, "weighted_attempts_contribution") or 0.0
            for member in typed_members
        )
        assigned_cost = sum(
            _flt(member, "weighted_assigned_cost_contribution_usd") or 0.0
            for member in typed_members
        )
        source_scenario = source.get((model, strategy))
        if source_scenario is None:
            continue
        cost_per_success = assigned_cost / completion if completion > 0 else math.inf
        numeric_checks = {
            "weighted_baseline_success_probability": weighted_baseline,
            "weighted_single_attempt_success_probability": weighted_single,
            "completion_probability": completion,
            "expected_attempts": attempts,
            "provider_cost_per_attempt_usd": float(source_scenario.provider_cost_usd),
            "provider_cost_per_assigned_session_usd": assigned_cost,
            "provider_cost_per_successful_session_usd": cost_per_success,
            "completion_slo_target": COMPLETION_SLO,
        }
        for field_name, expected in numeric_checks.items():
            observed = _flt(row, field_name)
            audit.check(
                _float_close(observed, expected),
                "aggregate.formula",
                "Aggregate field does not reconcile to its stratum results.",
                field=field_name,
                expected=expected,
                observed=observed,
                **context,
            )
        audit.check(
            _bool(row, "completion_slo_met") == (completion >= COMPLETION_SLO),
            "aggregate.slo",
            "completion_slo_met must be derived from completion probability.",
            **context,
        )
        cost = _dec(row, "provider_cost_per_attempt_usd")
        if cost is not None:
            cost_sets[(model, strategy)].add(cost)
        audit.check(
            _text(row, "source_type") == "simulated",
            "aggregate.source_type",
            "Generated aggregate rows must be labeled source_type=simulated.",
            **context,
        )

    for key, source_scenario in source.items():
        observed = cost_sets.get(key, set())
        audit.check(
            observed == {source_scenario.provider_cost_usd},
            "separation.cost_invariance",
            "Per-attempt provider cost must be invariant to every quality assumption.",
            model=key[0],
            strategy=key[1],
            expected=source_scenario.provider_cost_usd,
            observed=sorted(observed),
        )
    return lookup


def _dominance_status(
    baseline_completion: float,
    comparison_completion: float,
    baseline_cost: float,
    comparison_cost: float,
) -> str:
    if (
        comparison_completion >= baseline_completion
        and comparison_cost <= baseline_cost
    ):
        return "comparison_dominates_or_ties"
    if (
        comparison_completion <= baseline_completion
        and comparison_cost >= baseline_cost
    ):
        return "baseline_dominates_or_ties"
    return "cost_quality_tradeoff"


def _audit_contrasts(
    rows: Sequence[Mapping[str, str]],
    aggregates: Mapping[tuple[str, str, str], Mapping[str, str]],
    audit: Audit,
) -> dict[str, Mapping[str, str]]:
    lookup: dict[str, Mapping[str, str]] = {}
    coverage: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row_number, row in enumerate(rows, start=2):
        contrast_id = _text(row, "quality_contrast_id")
        parameter_id = _text(row, "parameter_set_id")
        model = _canonical_model(_text(row, "model"))
        baseline_strategy = _canonical_strategy(_text(row, "baseline_strategy_id"))
        comparison_strategy = _canonical_strategy(_text(row, "comparison_strategy_id"))
        context = {
            "table": "quality-contrast-results.csv.gz",
            "row": row_number,
            "quality_contrast_id": contrast_id,
            "parameter_set_id": parameter_id,
            "model": model,
            "comparison_strategy": comparison_strategy,
        }
        if not audit.check(
            contrast_id
            and model in MODELS
            and baseline_strategy == "grow_to_800k"
            and comparison_strategy in SOURCE_STRATEGY_ORIGINS
            and comparison_strategy != baseline_strategy,
            "contrast.identity",
            "Quality contrast must compare a known compact strategy against grow_to_800k.",
            **context,
        ):
            continue
        audit.check(
            contrast_id not in lookup,
            "contrast.duplicate",
            "quality_contrast_id must be unique.",
            **context,
        )
        lookup[contrast_id] = row
        coverage[(parameter_id, model)].add(comparison_strategy)
        baseline = aggregates.get((parameter_id, model, baseline_strategy))
        comparison = aggregates.get((parameter_id, model, comparison_strategy))
        if not audit.check(
            baseline is not None and comparison is not None,
            "contrast.aggregate_pair",
            "Contrast must resolve to matched aggregate strategy rows.",
            **context,
        ):
            continue
        base_completion = _flt(baseline, "completion_probability")
        comp_completion = _flt(comparison, "completion_probability")
        base_attempts = _flt(baseline, "expected_attempts")
        comp_attempts = _flt(comparison, "expected_attempts")
        base_assigned = _flt(baseline, "provider_cost_per_assigned_session_usd")
        comp_assigned = _flt(comparison, "provider_cost_per_assigned_session_usd")
        base_success = _flt(baseline, "provider_cost_per_successful_session_usd")
        comp_success = _flt(comparison, "provider_cost_per_successful_session_usd")
        if None in {
            base_completion,
            comp_completion,
            base_attempts,
            comp_attempts,
            base_assigned,
            comp_assigned,
            base_success,
            comp_success,
        }:
            audit.check(
                False,
                "contrast.numeric_inputs",
                "Matched aggregates require finite contrast inputs.",
                **context,
            )
            continue
        assert base_completion is not None and comp_completion is not None
        assert base_attempts is not None and comp_attempts is not None
        assert base_assigned is not None and comp_assigned is not None
        assert base_success is not None and comp_success is not None
        expected_fields = {
            "baseline_completion_probability": base_completion,
            "comparison_completion_probability": comp_completion,
            "delta_completion_probability_comparison_minus_baseline": comp_completion
            - base_completion,
            "baseline_expected_attempts": base_attempts,
            "comparison_expected_attempts": comp_attempts,
            "delta_expected_attempts_comparison_minus_baseline": comp_attempts
            - base_attempts,
            "baseline_provider_cost_per_assigned_session_usd": base_assigned,
            "comparison_provider_cost_per_assigned_session_usd": comp_assigned,
            "provider_cost_savings_per_assigned_session_usd": base_assigned
            - comp_assigned,
            "baseline_provider_cost_per_successful_session_usd": base_success,
            "comparison_provider_cost_per_successful_session_usd": comp_success,
            "delta_provider_cost_per_successful_session_usd": comp_success
            - base_success,
        }
        for field_name, expected in expected_fields.items():
            observed = _flt(row, field_name)
            audit.check(
                _float_close(observed, expected),
                "contrast.formula",
                "Contrast field differs from the independently matched aggregate difference.",
                field=field_name,
                expected=expected,
                observed=observed,
                **context,
            )
        audit.check(
            _bool(row, "baseline_completion_slo_met")
            == _bool(baseline, "completion_slo_met")
            and _bool(row, "comparison_completion_slo_met")
            == _bool(comparison, "completion_slo_met"),
            "contrast.slo",
            "Contrast SLO flags must match aggregate rows.",
            **context,
        )
        expected_dominance = _dominance_status(
            base_completion,
            comp_completion,
            base_assigned,
            comp_assigned,
        )
        audit.check(
            _text(row, "dominance_status") == expected_dominance,
            "contrast.dominance",
            "Dominance status is inconsistent with completion and assigned cost.",
            expected=expected_dominance,
            observed=_text(row, "dominance_status"),
            **context,
        )
        audit.check(
            _text(row, "source_type") == "simulated",
            "contrast.source_type",
            "Generated contrast rows must be labeled source_type=simulated.",
            **context,
        )
    expected_comparisons = set(SOURCE_STRATEGY_ORIGINS) - {"grow_to_800k"}
    for parameter_model in {(key[0], key[1]) for key in aggregates}:
        audit.check(
            coverage.get(parameter_model, set()) == expected_comparisons,
            "contrast.coverage",
            "Every parameter/model cell must compare all four compact strategies with grow.",
            parameter_set_id=parameter_model[0],
            model=parameter_model[1],
            expected=sorted(expected_comparisons),
            observed=sorted(coverage.get(parameter_model, set())),
        )
    return lookup


def _audit_break_even(
    rows: Sequence[Mapping[str, str]],
    contrasts: Mapping[str, Mapping[str, str]],
    audit: Audit,
) -> None:
    seen: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        contrast_id = _text(row, "quality_contrast_id")
        break_id = _text(row, "break_even_id")
        context = {
            "table": "break-even.csv.gz",
            "row": row_number,
            "quality_contrast_id": contrast_id,
        }
        contrast = contrasts.get(contrast_id)
        if not audit.check(
            contrast is not None,
            "break_even.contrast",
            "Break-even row must resolve to one quality contrast.",
            **context,
        ):
            continue
        audit.check(
            break_id and break_id not in seen,
            "break_even.id",
            "break_even_id must be non-empty and unique.",
            break_even_id=break_id,
            **context,
        )
        seen.add(break_id)
        savings = _flt(contrast, "provider_cost_savings_per_assigned_session_usd")
        completion_delta = _flt(
            contrast, "delta_completion_probability_comparison_minus_baseline"
        )
        if savings is None or completion_delta is None:
            continue
        completion_loss = max(-completion_delta, 0.0)
        if savings > 0 and completion_loss > 0:
            expected_value: float | None = savings / completion_loss
            expected_status = "identified_tradeoff"
        elif savings >= 0 and completion_delta >= 0:
            expected_value = None
            expected_status = "comparison_weakly_dominates"
        elif savings <= 0 and completion_delta <= 0:
            expected_value = None
            expected_status = "baseline_weakly_dominates"
        else:
            expected_value = None
            expected_status = "comparison_costs_more_for_quality_gain"
        audit.check(
            _float_close(
                _flt(row, "provider_cost_savings_per_assigned_session_usd"), savings
            ),
            "break_even.savings",
            "Break-even savings must match its contrast.",
            expected=savings,
            observed=_flt(row, "provider_cost_savings_per_assigned_session_usd"),
            **context,
        )
        audit.check(
            _float_close(_flt(row, "completion_probability_loss"), completion_loss),
            "break_even.completion_loss",
            "Break-even completion loss must equal max(-completion delta, 0).",
            expected=completion_loss,
            observed=_flt(row, "completion_probability_loss"),
            **context,
        )
        observed_value = _flt(
            row, "break_even_failure_loss_usd_per_incremental_unresolved_session"
        )
        audit.check(
            (
                expected_value is None
                and _text(
                    row,
                    "break_even_failure_loss_usd_per_incremental_unresolved_session",
                )
                == ""
            )
            or _float_close(observed_value, expected_value),
            "break_even.value",
            "Break-even loss must equal savings divided by incremental unresolved probability when identified.",
            expected=expected_value,
            observed=observed_value,
            **context,
        )
        audit.check(
            _text(row, "break_even_status") == expected_status,
            "break_even.status",
            "Break-even status does not match cost/completion signs.",
            expected=expected_status,
            observed=_text(row, "break_even_status"),
            **context,
        )
        audit.check(
            _text(row, "source_type") == "simulated",
            "break_even.source_type",
            "Generated break-even rows must be labeled simulated.",
            **context,
        )
    audit.check(
        len(rows) == len(contrasts),
        "break_even.coverage",
        "There must be exactly one break-even row per quality contrast.",
        expected=len(contrasts),
        observed=len(rows),
    )


def _audit_scale(
    rows: Sequence[Mapping[str, str]],
    aggregates: Mapping[tuple[str, str, str], Mapping[str, str]],
    audit: Audit,
) -> None:
    volumes: dict[tuple[str, str, str], set[int]] = defaultdict(set)
    ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        key = _quality_key(row)
        context = {
            "table": "scale-results.csv.gz",
            "row": row_number,
            "parameter_set_id": key[0],
            "model": key[1],
            "strategy": key[2],
        }
        aggregate = aggregates.get(key)
        if not audit.check(
            aggregate is not None,
            "scale.aggregate",
            "Scale row must resolve to one aggregate result.",
            **context,
        ):
            continue
        volume = _int(row, "assigned_sessions")
        if not audit.check(
            volume in {1_000, 1_000_000},
            "scale.volume",
            "Scale row volume must be 1,000 or 1,000,000.",
            observed=volume,
            **context,
        ):
            continue
        volumes[key].add(volume)
        result_id = _text(row, "scale_result_id")
        audit.check(
            result_id and result_id not in ids,
            "scale.id",
            "scale_result_id must be non-empty and unique.",
            scale_result_id=result_id,
            **context,
        )
        ids.add(result_id)
        completion = _flt(aggregate, "completion_probability")
        assigned_cost = _flt(aggregate, "provider_cost_per_assigned_session_usd")
        cost_success = _flt(aggregate, "provider_cost_per_successful_session_usd")
        if completion is None or assigned_cost is None or cost_success is None:
            continue
        expected_fields = {
            "expected_completed_sessions": volume * completion,
            "expected_unresolved_sessions": volume * (1.0 - completion),
            "expected_provider_spend_usd": volume * assigned_cost,
            "provider_cost_per_successful_session_usd": cost_success,
            "completion_probability": completion,
        }
        for field_name, expected in expected_fields.items():
            observed = _flt(row, field_name)
            audit.check(
                _float_close(observed, expected, tol=1e-7),
                "scale.formula",
                "Scaled field must be an algebraic projection of its aggregate row.",
                field=field_name,
                expected=expected,
                observed=observed,
                **context,
            )
        audit.check(
            _text(row, "source_type") == "simulated",
            "scale.source_type",
            "Generated scale rows must be labeled simulated.",
            **context,
        )
    for key in aggregates:
        audit.check(
            volumes.get(key, set()) == {1_000, 1_000_000},
            "scale.coverage",
            "Every aggregate requires exactly both algebraic scale volumes.",
            key=key,
            observed=sorted(volumes.get(key, set())),
        )


def _audit_evidence(
    curve_rows: Sequence[Mapping[str, str]],
    onset_rows: Sequence[Mapping[str, str]],
    audit: Audit,
) -> None:
    grouped: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    evidence_ids: set[str] = set()
    for row_number, row in enumerate(curve_rows, start=2):
        series_id = _text(row, "series_id")
        evidence_id = _text(row, "evidence_id")
        context_tokens = _flt(row, "context_tokens")
        score = _flt(row, "score")
        context = {
            "table": "evidence-curves.csv",
            "row": row_number,
            "series_id": series_id,
            "evidence_id": evidence_id,
        }
        if not audit.check(
            bool(series_id) and bool(evidence_id) and score is not None,
            "evidence.identity",
            "Evidence inventory rows require non-empty IDs and a finite score; tokenless non-anchor rows are retained by design.",
            **context,
        ):
            continue
        audit.check(
            evidence_id not in evidence_ids,
            "evidence.id",
            "evidence_id must be unique.",
            **context,
        )
        evidence_ids.add(evidence_id)
        grouped[series_id].append(row)
        metadata_eligible = _text(row, "score_unit") == "proportion" and (
            (
                _text(row, "evidence_status") == "source-reported"
                and _text(row, "numeric_precision") in {"exact", "rounded"}
            )
            or (
                _text(row, "evidence_status") == "independently-derived"
                and _text(row, "numeric_precision") == "exact"
                and _text(row, "source_location").lower().startswith("frozen ")
                and "commit" in _text(row, "source_location").lower()
            )
        )
        expected_eligible = (
            metadata_eligible
            and context_tokens is not None
            and context_tokens > 0.0
            and 0.0 <= score <= 1.0
        )
        audit.check(
            _bool(row, "anchor_eligible") == expected_eligible,
            "evidence.anchor_eligibility",
            "Anchor eligibility must follow source-status and precision rules.",
            expected=expected_eligible,
            observed=_bool(row, "anchor_eligible"),
            **context,
        )
        if _bool(row, "anchor_eligible") is True:
            audit.check(
                context_tokens is not None and context_tokens > 0.0,
                "evidence.anchor_context",
                "Every eligible interpolation anchor must have a finite positive context size.",
                context_tokens=context_tokens,
                **context,
            )
        scope = _text(row, "target_model_scope").lower()
        audit.check(
            "gpt-5.6" not in scope or "not" in scope,
            "evidence.scope",
            "Historical evidence must not be labeled as direct GPT-5.6 calibration.",
            observed=scope,
            **context,
        )

    expected_onsets: dict[str, dict[float, dict[str, Any]]] = {}
    for series_id, members in grouped.items():
        ordered = sorted(
            members,
            key=lambda row: (
                _flt(row, "context_tokens") is None
                or float(_flt(row, "context_tokens") or 0.0) <= 0.0,
                (
                    float(_flt(row, "context_tokens") or 0.0)
                    if _flt(row, "context_tokens") is not None
                    and float(_flt(row, "context_tokens") or 0.0) > 0.0
                    else math.inf
                ),
                _text(row, "evidence_id"),
            ),
        )
        eligible = [row for row in ordered if _bool(row, "anchor_eligible") is True]
        reference = eligible[0] if eligible else None
        reference_score = _flt(reference, "score") if reference is not None else None
        anchors: list[tuple[float, float, Mapping[str, str]]] = []
        for order, row in enumerate(ordered, start=1):
            context = {"series_id": series_id, "evidence_id": _text(row, "evidence_id")}
            audit.check(
                _int(row, "curve_order") == order,
                "evidence.curve_order",
                "curve_order must follow context and evidence ID sorting.",
                expected=order,
                observed=_int(row, "curve_order"),
                **context,
            )
            row_context = _flt(row, "context_tokens")
            can_retain = (
                reference is not None
                and reference_score not in {None, 0.0}
                and row_context is not None
                and row_context > 0.0
                and _text(row, "score_unit") == "proportion"
            )
            if not can_retain:
                audit.check(
                    _text(row, "retention") == "",
                    "evidence.no_reference",
                    "Retention must be empty when no eligible reference exists.",
                    **context,
                )
                if row_context is None or row_context <= 0.0:
                    for field_name in (
                        "reference_evidence_id",
                        "reference_context_tokens",
                        "reference_score",
                    ):
                        audit.check(
                            _text(row, field_name) == "",
                            "evidence.tokenless_reference",
                            "Tokenless inventory rows must not inherit curve-reference fields.",
                            field=field_name,
                            **context,
                        )
                continue
            expected_retention = (_flt(row, "score") or 0.0) / reference_score
            audit.check(
                _text(row, "reference_evidence_id") == _text(reference, "evidence_id"),
                "evidence.reference_id",
                "Evidence reference must be the first eligible context anchor.",
                **context,
            )
            audit.check(
                _float_close(
                    _flt(row, "reference_context_tokens"),
                    _flt(reference, "context_tokens"),
                ),
                "evidence.reference_context",
                "Reference context is incorrect.",
                **context,
            )
            audit.check(
                _float_close(_flt(row, "reference_score"), reference_score),
                "evidence.reference_score",
                "Reference score is incorrect.",
                **context,
            )
            audit.check(
                _float_close(_flt(row, "retention"), expected_retention),
                "evidence.retention",
                "Retention must equal score divided by reference score.",
                expected=expected_retention,
                observed=_flt(row, "retention"),
                **context,
            )
            if _bool(row, "anchor_eligible") is True:
                anchors.append(
                    (float(_flt(row, "context_tokens") or 0.0), expected_retention, row)
                )

        series_expectations: dict[float, dict[str, Any]] = {}
        for threshold in (0.95, 0.90, 0.85, 0.80, 0.70, 0.50):
            bracket: (
                tuple[
                    tuple[float, float, Mapping[str, str]],
                    tuple[float, float, Mapping[str, str]],
                ]
                | None
            ) = None
            for lower, upper in pairwise(anchors):
                if lower[1] >= threshold and upper[1] < threshold:
                    bracket = (lower, upper)
                    break
            if bracket is None:
                series_expectations[threshold] = {"status": "unidentifiable"}
            else:
                lower, upper = bracket
                fraction = (threshold - lower[1]) / (upper[1] - lower[1])
                interpolated = 2.0 ** (
                    math.log2(lower[0])
                    + fraction * (math.log2(upper[0]) - math.log2(lower[0]))
                )
                series_expectations[threshold] = {
                    "status": "interpolated",
                    "interpolated": interpolated,
                    "lower": lower,
                    "upper": upper,
                    "anchor_count": len(anchors),
                }
        expected_onsets[series_id] = series_expectations

    seen_onsets: set[tuple[str, float]] = set()
    for row_number, row in enumerate(onset_rows, start=2):
        series_id = _text(row, "series_id")
        threshold = _flt(row, "retention_threshold")
        context = {
            "table": "evidence-onsets.csv",
            "row": row_number,
            "series_id": series_id,
            "threshold": threshold,
        }
        expected = expected_onsets.get(series_id, {}).get(
            threshold if threshold is not None else -1.0
        )
        if not audit.check(
            expected is not None,
            "evidence_onset.identity",
            "Evidence-onset row must resolve to one series and declared threshold.",
            **context,
        ):
            continue
        key = (series_id, float(threshold))
        audit.check(
            key not in seen_onsets,
            "evidence_onset.duplicate",
            "Series/threshold onset key must be unique.",
            **context,
        )
        seen_onsets.add(key)
        audit.check(
            _text(row, "threshold_status") == expected["status"],
            "evidence_onset.status",
            "Threshold status differs from independent bracket search.",
            expected=expected["status"],
            observed=_text(row, "threshold_status"),
            **context,
        )
        audit.check(
            _text(row, "interpolation_scale") == "log2(context_tokens)",
            "evidence_onset.scale",
            "Identified and unidentified onsets must declare the log2 context scale.",
            **context,
        )
        if expected["status"] == "unidentifiable":
            for field_name in (
                "interpolated_context_tokens",
                "lower_evidence_id",
                "upper_evidence_id",
                "lower_context_tokens",
                "upper_context_tokens",
                "lower_retention",
                "upper_retention",
            ):
                audit.check(
                    _text(row, field_name) == "",
                    "evidence_onset.no_extrapolation",
                    "Unbracketed onset fields must remain empty; extrapolation is forbidden.",
                    field=field_name,
                    **context,
                )
        else:
            lower = expected["lower"]
            upper = expected["upper"]
            expected_fields: dict[str, Any] = {
                "interpolated_context_tokens": expected["interpolated"],
                "lower_context_tokens": lower[0],
                "upper_context_tokens": upper[0],
                "lower_retention": lower[1],
                "upper_retention": upper[1],
            }
            for field_name, value in expected_fields.items():
                audit.check(
                    _float_close(_flt(row, field_name), float(value)),
                    "evidence_onset.interpolation",
                    "Bracketed log2 interpolation field is incorrect.",
                    field=field_name,
                    expected=value,
                    observed=_flt(row, field_name),
                    **context,
                )
            audit.check(
                _text(row, "lower_evidence_id") == _text(lower[2], "evidence_id")
                and _text(row, "upper_evidence_id") == _text(upper[2], "evidence_id"),
                "evidence_onset.bracket_ids",
                "Onset bracket evidence IDs are incorrect.",
                **context,
            )
            audit.check(
                _int(row, "anchor_count") == expected["anchor_count"],
                "evidence_onset.anchor_count",
                "Onset anchor count is incorrect.",
                expected=expected["anchor_count"],
                observed=_int(row, "anchor_count"),
                **context,
            )
    audit.check(
        len(seen_onsets) == sum(len(values) for values in expected_onsets.values()),
        "evidence_onset.coverage",
        "There must be one onset row for every series and declared retention threshold.",
        expected=sum(len(values) for values in expected_onsets.values()),
        observed=len(seen_onsets),
    )


def _analytic_strategy(
    source_scenario: SourceScenario,
    *,
    onset: int,
    beta: float,
    fidelity: float,
    profile: str,
    max_attempts: int,
) -> dict[str, float]:
    exposure = float(
        _context_exposure(source_scenario.main_prompts, onset)[
            "normalized_excess_units"
        ]
    )
    effective = _effective_fidelity(
        39,
        source_scenario.compaction_positions,
        fidelity,
        profile,
    )
    completion = attempts = assigned = weighted_single = 0.0
    for weight, baseline_probability in TASK_STRATA.values():
        probability = _single_attempt_probability(
            baseline_probability,
            beta,
            exposure,
            effective,
        )
        retry = _retry_exact(
            probability,
            float(source_scenario.provider_cost_usd),
            max_attempts,
        )
        weighted_single += weight * probability
        completion += weight * retry["completion_probability"]
        attempts += weight * retry["expected_attempts"]
        assigned += weight * retry["provider_cost_usd_per_assigned_task"]
    return {
        "normalized_excess_auc": exposure,
        "effective_evidence_fidelity": effective,
        "weighted_single_attempt_success_probability": weighted_single,
        "completion_probability": completion,
        "expected_attempts": attempts,
        "provider_cost_per_assigned_session_usd": assigned,
        "provider_cost_per_successful_session_usd": assigned / completion,
    }


def _minimum_threshold(
    predicate: Any,
    lower: float,
    upper: float,
    tolerance: float,
    max_iterations: int,
) -> tuple[float | None, str]:
    if predicate(lower):
        return lower, "already_satisfied_at_lower_bound"
    if not predicate(upper):
        return None, "not_reached_within_bounds"
    lo, hi = lower, upper
    for _ in range(max_iterations):
        if hi - lo <= tolerance:
            break
        midpoint = (lo + hi) / 2.0
        if predicate(midpoint):
            hi = midpoint
        else:
            lo = midpoint
    return hi, "identified_by_bisection"


def _audit_fidelity_boundaries(
    rows: Sequence[Mapping[str, str]],
    source: Mapping[tuple[str, str], SourceScenario],
    audit: Audit,
) -> None:
    expected_pairs = {
        (model, strategy)
        for model in MODELS
        for strategy in ("cap_200k_uncached", "cap_200k_cache_read")
    }
    observed_pairs: set[tuple[str, str]] = set()
    ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        model = _canonical_model(_text(row, "model"))
        strategy = _canonical_strategy(_text(row, "comparison_strategy_id"))
        context = {
            "table": "fidelity-boundaries.csv",
            "row": row_number,
            "model": model,
            "strategy": strategy,
        }
        if not audit.check(
            (model, strategy) in expected_pairs,
            "boundary.identity",
            "Boundary row must be one of the six primary model/strategy pairs.",
            **context,
        ):
            continue
        assert model is not None and strategy is not None
        observed_pairs.add((model, strategy))
        boundary_id = _text(row, "boundary_id")
        audit.check(
            boundary_id and boundary_id not in ids,
            "boundary.id",
            "boundary_id must be non-empty and unique.",
            boundary_id=boundary_id,
            **context,
        )
        ids.add(boundary_id)
        onset = _int(row, "onset_tokens")
        max_attempts = _int(row, "max_attempts")
        base_beta = _flt(row, "baseline_beta_for_fidelity_search")
        fixed_fidelity = _flt(row, "fixed_fidelity_for_beta_search")
        f_lower = _flt(row, "fidelity_search_lower_bound")
        f_upper = _flt(row, "fidelity_search_upper_bound")
        b_lower = _flt(row, "beta_search_lower_bound")
        b_upper = _flt(row, "beta_search_upper_bound")
        tolerance = _flt(row, "bisection_tolerance")
        iterations = _int(row, "bisection_max_iterations")
        valid = None not in {
            onset,
            max_attempts,
            base_beta,
            fixed_fidelity,
            f_lower,
            f_upper,
            b_lower,
            b_upper,
            tolerance,
            iterations,
        }
        if not audit.check(
            valid,
            "boundary.parameters",
            "Boundary-search parameters must be finite.",
            **context,
        ):
            continue
        assert onset is not None and max_attempts is not None and base_beta is not None
        assert (
            fixed_fidelity is not None and f_lower is not None and f_upper is not None
        )
        assert (
            b_lower is not None
            and b_upper is not None
            and tolerance is not None
            and iterations is not None
        )
        grow = source[(model, "grow_to_800k")]
        compact = source[(model, strategy)]

        def cost_at_fidelity(
            value: float,
            *,
            grow_scenario: SourceScenario = grow,
            compact_scenario: SourceScenario = compact,
            onset_value: float = onset,
            beta_value: float = base_beta,
            attempt_limit: int = max_attempts,
        ) -> bool:
            base = _analytic_strategy(
                grow_scenario,
                onset=onset_value,
                beta=beta_value,
                fidelity=value,
                profile="uniform",
                max_attempts=attempt_limit,
            )
            comp = _analytic_strategy(
                compact_scenario,
                onset=onset_value,
                beta=beta_value,
                fidelity=value,
                profile="uniform",
                max_attempts=attempt_limit,
            )
            return (
                comp["provider_cost_per_successful_session_usd"]
                <= base["provider_cost_per_successful_session_usd"]
            )

        def slo_at_fidelity(
            value: float,
            *,
            compact_scenario: SourceScenario = compact,
            onset_value: float = onset,
            beta_value: float = base_beta,
            attempt_limit: int = max_attempts,
        ) -> bool:
            comp = _analytic_strategy(
                compact_scenario,
                onset=onset_value,
                beta=beta_value,
                fidelity=value,
                profile="uniform",
                max_attempts=attempt_limit,
            )
            return comp["completion_probability"] >= COMPLETION_SLO

        def cost_at_beta(
            value: float,
            *,
            grow_scenario: SourceScenario = grow,
            compact_scenario: SourceScenario = compact,
            onset_value: float = onset,
            fidelity_value: float = fixed_fidelity,
            attempt_limit: int = max_attempts,
        ) -> bool:
            base = _analytic_strategy(
                grow_scenario,
                onset=onset_value,
                beta=value,
                fidelity=fidelity_value,
                profile="uniform",
                max_attempts=attempt_limit,
            )
            comp = _analytic_strategy(
                compact_scenario,
                onset=onset_value,
                beta=value,
                fidelity=fidelity_value,
                profile="uniform",
                max_attempts=attempt_limit,
            )
            return (
                comp["provider_cost_per_successful_session_usd"]
                <= base["provider_cost_per_successful_session_usd"]
            )

        expected_f_cost, expected_f_cost_status = _minimum_threshold(
            cost_at_fidelity, f_lower, f_upper, tolerance, iterations
        )
        expected_f_slo, expected_f_slo_status = _minimum_threshold(
            slo_at_fidelity, f_lower, f_upper, tolerance, iterations
        )
        expected_beta, expected_beta_status = _minimum_threshold(
            cost_at_beta, b_lower, b_upper, tolerance, iterations
        )
        checks = (
            ("minimum_fidelity_cost_per_success_not_above_grow", expected_f_cost),
            ("minimum_fidelity_completion_slo", expected_f_slo),
            ("minimum_beta_at_f095_cost_per_success_not_above_grow", expected_beta),
            ("grow_cost_per_attempt_usd", float(grow.provider_cost_usd)),
            ("comparison_cost_per_attempt_usd", float(compact.provider_cost_usd)),
        )
        for field_name, expected in checks:
            observed = _flt(row, field_name)
            audit.check(
                (expected is None and _text(row, field_name) == "")
                or _float_close(observed, expected, tol=max(tolerance * 2, 1e-9)),
                "boundary.value",
                "Decision-boundary value differs from independent bisection.",
                field=field_name,
                expected=expected,
                observed=observed,
                **context,
            )
        status_checks = {
            "minimum_fidelity_cost_status": expected_f_cost_status,
            "minimum_fidelity_completion_slo_status": expected_f_slo_status,
            "minimum_beta_cost_status": expected_beta_status,
        }
        for field_name, expected in status_checks.items():
            audit.check(
                _text(row, field_name) == expected,
                "boundary.status",
                "Boundary status differs from independent endpoint/bisection logic.",
                field=field_name,
                expected=expected,
                observed=_text(row, field_name),
                **context,
            )
        audit.check(
            _text(row, "parameter_set_id") == PRIMARY_ASSUMPTION_ID
            and _text(row, "evidence_profile") == "uniform",
            "boundary.primary_scope",
            "Decision boundaries must use the declared primary assumptions.",
            **context,
        )
        audit.check(
            _text(row, "source_type") == "simulated",
            "boundary.source_type",
            "Generated boundary rows must be labeled simulated.",
            **context,
        )
    audit.check(
        observed_pairs == expected_pairs and len(rows) == 6,
        "boundary.coverage",
        "Boundary table must contain exactly six primary pairs.",
        expected=sorted(expected_pairs),
        observed=sorted(observed_pairs),
        row_count=len(rows),
    )


def _draw_stratum(uniform: float) -> str:
    if uniform < 0.25:
        return "easy"
    if uniform < 0.75:
        return "typical"
    return "hard"


def _simulate_capped(probability: float, uniforms: Sequence[float]) -> tuple[int, int]:
    for attempt, value in enumerate(uniforms, start=1):
        if value < probability:
            return 1, attempt
    return 0, len(uniforms)


def _paired_mc_oracle(
    *,
    probabilities_baseline: Mapping[str, float],
    probabilities_comparison: Mapping[str, float],
    cost_baseline: float,
    cost_comparison: float,
    max_attempts: int,
    task_count: int,
    seed: int,
) -> dict[str, float]:
    rng = random.Random(seed)
    success_baseline = success_comparison = 0
    cost_sum_baseline = cost_sum_comparison = 0.0
    delta_sum = delta_square_sum = 0.0
    for _ in range(task_count):
        stratum = _draw_stratum(rng.random())
        uniforms = [rng.random() for _attempt in range(max_attempts)]
        completed_b, attempts_b = _simulate_capped(
            probabilities_baseline[stratum], uniforms
        )
        completed_c, attempts_c = _simulate_capped(
            probabilities_comparison[stratum], uniforms
        )
        success_baseline += completed_b
        success_comparison += completed_c
        cost_sum_baseline += attempts_b * cost_baseline
        cost_sum_comparison += attempts_c * cost_comparison
        delta = completed_c - completed_b
        delta_sum += delta
        delta_square_sum += delta * delta
    mean_b = success_baseline / task_count
    mean_c = success_comparison / task_count
    delta_completion = delta_sum / task_count
    variance_delta = (
        (delta_square_sum - task_count * delta_completion**2) / (task_count - 1)
        if task_count > 1
        else 0.0
    )
    se_completion = math.sqrt(max(variance_delta, 0.0) / task_count)
    ratio_b = cost_sum_baseline / success_baseline
    ratio_c = cost_sum_comparison / success_comparison

    rng = random.Random(seed)
    influence_sum = influence_square_sum = 0.0
    for _ in range(task_count):
        stratum = _draw_stratum(rng.random())
        uniforms = [rng.random() for _attempt in range(max_attempts)]
        completed_b, attempts_b = _simulate_capped(
            probabilities_baseline[stratum], uniforms
        )
        completed_c, attempts_c = _simulate_capped(
            probabilities_comparison[stratum], uniforms
        )
        item_cost_b = attempts_b * cost_baseline
        item_cost_c = attempts_c * cost_comparison
        influence_b = (item_cost_b - ratio_b * completed_b) / mean_b
        influence_c = (item_cost_c - ratio_c * completed_c) / mean_c
        influence = influence_c - influence_b
        influence_sum += influence
        influence_square_sum += influence * influence
    influence_mean = influence_sum / task_count
    influence_variance = (
        (influence_square_sum - task_count * influence_mean**2) / (task_count - 1)
        if task_count > 1
        else 0.0
    )
    se_cost = math.sqrt(max(influence_variance, 0.0) / task_count)
    delta_cost = ratio_c - ratio_b
    normal_95 = 1.959963984540054
    return {
        "mc_baseline_completion_probability": mean_b,
        "mc_comparison_completion_probability": mean_c,
        "mc_delta_completion_probability": delta_completion,
        "mcse_delta_completion_probability": se_completion,
        "ci95_low_delta_completion_probability": delta_completion
        - normal_95 * se_completion,
        "ci95_high_delta_completion_probability": delta_completion
        + normal_95 * se_completion,
        "mc_baseline_cost_per_successful_session_usd": ratio_b,
        "mc_comparison_cost_per_successful_session_usd": ratio_c,
        "mc_delta_cost_per_successful_session_usd": delta_cost,
        "mcse_delta_cost_per_successful_session_usd": se_cost,
        "ci95_low_delta_cost_per_successful_session_usd": delta_cost
        - normal_95 * se_cost,
        "ci95_high_delta_cost_per_successful_session_usd": delta_cost
        + normal_95 * se_cost,
    }


def _audit_monte_carlo(
    rows: Sequence[Mapping[str, str]],
    aggregates: Mapping[tuple[str, str, str], Mapping[str, str]],
    strata: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    audit: Audit,
) -> None:
    ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        parameter_id = _text(row, "parameter_set_id")
        model = _canonical_model(_text(row, "model"))
        baseline_strategy = _canonical_strategy(_text(row, "baseline_strategy_id"))
        comparison_strategy = _canonical_strategy(_text(row, "comparison_strategy_id"))
        context = {
            "table": "monte-carlo-summary.csv",
            "row": row_number,
            "model": model,
            "comparison_strategy": comparison_strategy,
        }
        if not audit.check(
            parameter_id == PRIMARY_ASSUMPTION_ID
            and model in MODELS
            and baseline_strategy == "grow_to_800k"
            and comparison_strategy in SOURCE_STRATEGY_ORIGINS,
            "mc.identity",
            "Monte Carlo sentinel must use the primary parameter set and a valid paired strategy contrast.",
            **context,
        ):
            continue
        assert model is not None and comparison_strategy is not None
        mc_id = _text(row, "monte_carlo_id")
        audit.check(
            mc_id and mc_id not in ids,
            "mc.id",
            "monte_carlo_id must be non-empty and unique.",
            monte_carlo_id=mc_id,
            **context,
        )
        ids.add(mc_id)
        task_count = _int(row, "task_count")
        seed = _int(row, "seed")
        max_attempts = _int(row, "max_attempts")
        audit.check(
            task_count == 200_000 and seed == 20_260_904,
            "mc.design",
            "MC sentinels must use 200,000 paired tasks and seed 20260904.",
            task_count=task_count,
            seed=seed,
            **context,
        )
        audit.check(
            _text(row, "coupling") == "paired-common-task-stratum-and-attempt-uniforms",
            "mc.coupling",
            "MC sentinel must declare paired common random numbers.",
            observed=_text(row, "coupling"),
            **context,
        )
        audit.check(
            "random" in _text(row, "rng").lower(),
            "mc.rng",
            "MC row must identify the standard-library RNG.",
            observed=_text(row, "rng"),
            **context,
        )
        if task_count is None or seed is None or max_attempts is None:
            continue
        baseline = aggregates.get((parameter_id, model, baseline_strategy))
        comparison = aggregates.get((parameter_id, model, comparison_strategy))
        if not audit.check(
            baseline is not None and comparison is not None,
            "mc.aggregate_pair",
            "MC sentinel must resolve to analytic aggregate results.",
            **context,
        ):
            continue
        analytic_fields = {
            "analytic_baseline_completion_probability": _flt(
                baseline, "completion_probability"
            ),
            "analytic_comparison_completion_probability": _flt(
                comparison, "completion_probability"
            ),
            "analytic_delta_completion_probability": (
                _flt(comparison, "completion_probability") or 0.0
            )
            - (_flt(baseline, "completion_probability") or 0.0),
            "analytic_baseline_cost_per_successful_session_usd": _flt(
                baseline, "provider_cost_per_successful_session_usd"
            ),
            "analytic_comparison_cost_per_successful_session_usd": _flt(
                comparison, "provider_cost_per_successful_session_usd"
            ),
            "analytic_delta_cost_per_successful_session_usd": (
                _flt(comparison, "provider_cost_per_successful_session_usd") or 0.0
            )
            - (_flt(baseline, "provider_cost_per_successful_session_usd") or 0.0),
        }
        for field_name, expected in analytic_fields.items():
            audit.check(
                _float_close(_flt(row, field_name), expected),
                "mc.analytic_reconciliation",
                "MC analytic field must match the deterministic aggregate results.",
                field=field_name,
                expected=expected,
                observed=_flt(row, field_name),
                **context,
            )
        probabilities_baseline = {
            stratum_id: float(
                _flt(
                    strata[(parameter_id, model, baseline_strategy, stratum_id)],
                    "single_attempt_success_probability",
                )
                or 0.0
            )
            for stratum_id in TASK_STRATA
        }
        probabilities_comparison = {
            stratum_id: float(
                _flt(
                    strata[(parameter_id, model, comparison_strategy, stratum_id)],
                    "single_attempt_success_probability",
                )
                or 0.0
            )
            for stratum_id in TASK_STRATA
        }
        oracle = _paired_mc_oracle(
            probabilities_baseline=probabilities_baseline,
            probabilities_comparison=probabilities_comparison,
            cost_baseline=float(_flt(baseline, "provider_cost_per_attempt_usd") or 0.0),
            cost_comparison=float(
                _flt(comparison, "provider_cost_per_attempt_usd") or 0.0
            ),
            max_attempts=max_attempts,
            task_count=task_count,
            seed=seed,
        )
        for field_name, expected in oracle.items():
            observed = _flt(row, field_name)
            audit.check(
                _float_close(observed, expected, tol=1e-10),
                "mc.exact_replay",
                "MC summary differs from the independent paired-CRN replay.",
                field=field_name,
                expected=expected,
                observed=observed,
                **context,
            )
        analytic_completion_delta = float(
            analytic_fields["analytic_delta_completion_probability"] or 0.0
        )
        analytic_cost_delta = float(
            analytic_fields["analytic_delta_cost_per_successful_session_usd"] or 0.0
        )
        observed_completion_delta = _flt(row, "mc_delta_completion_probability") or 0.0
        observed_cost_delta = (
            _flt(row, "mc_delta_cost_per_successful_session_usd") or 0.0
        )
        se_completion = _flt(row, "mcse_delta_completion_probability") or 0.0
        se_cost = _flt(row, "mcse_delta_cost_per_successful_session_usd") or 0.0
        audit.check(
            abs(observed_completion_delta - analytic_completion_delta)
            <= max(5.0 * se_completion, 1e-5),
            "mc.five_se_completion",
            "Analytic completion delta must be within max(5 MCSE, tolerance) of the paired estimate.",
            analytic=analytic_completion_delta,
            mc=observed_completion_delta,
            mcse=se_completion,
            **context,
        )
        audit.check(
            abs(observed_cost_delta - analytic_cost_delta) <= max(5.0 * se_cost, 1e-5),
            "mc.five_se_cost",
            "Analytic cost-per-success delta must be within max(5 MCSE, tolerance) of the paired estimate.",
            analytic=analytic_cost_delta,
            mc=observed_cost_delta,
            mcse=se_cost,
            **context,
        )
        completion_inside = (
            (_flt(row, "ci95_low_delta_completion_probability") or 0.0)
            <= analytic_completion_delta
            <= (_flt(row, "ci95_high_delta_completion_probability") or 0.0)
        )
        cost_inside = (
            (_flt(row, "ci95_low_delta_cost_per_successful_session_usd") or 0.0)
            <= analytic_cost_delta
            <= (_flt(row, "ci95_high_delta_cost_per_successful_session_usd") or 0.0)
        )
        audit.check(
            _bool(row, "completion_delta_analytic_inside_ci95") == completion_inside
            and _bool(row, "cost_delta_analytic_inside_ci95") == cost_inside,
            "mc.ci_flags",
            "Analytic-inside-CI flags must match the exported interval endpoints.",
            **context,
        )
        audit.check(
            _text(row, "source_type") == "simulated",
            "mc.source_type",
            "MC rows must be labeled simulated.",
            **context,
        )
    audit.check(
        len(rows) == 6,
        "mc.coverage",
        "Monte Carlo validation must contain exactly six preregistered sentinel pairs.",
        expected=6,
        observed=len(rows),
    )


def _nondecreasing(values: Sequence[float], tolerance: float = 1e-12) -> bool:
    return all(right + tolerance >= left for left, right in pairwise(values))


def _nonincreasing(values: Sequence[float], tolerance: float = 1e-12) -> bool:
    return all(right <= left + tolerance for left, right in pairwise(values))


def _audit_metamorphic_properties(
    rows: Sequence[Mapping[str, str]],
    audit: Audit,
) -> None:
    generic = [
        row for row in rows if _text(row, "calibration_id") == "generic-elasticity-grid"
    ]

    beta_groups: dict[tuple[Any, ...], list[tuple[float, float]]] = defaultdict(list)
    fidelity_groups: dict[tuple[Any, ...], list[tuple[float, float]]] = defaultdict(
        list
    )
    onset_groups: dict[tuple[Any, ...], list[tuple[float, float]]] = defaultdict(list)
    retry_groups: dict[tuple[Any, ...], list[tuple[int, float, float]]] = defaultdict(
        list
    )
    grow_fidelity_groups: dict[tuple[Any, ...], list[float]] = defaultdict(list)
    null_groups: dict[tuple[Any, ...], list[float]] = defaultdict(list)
    cache_mode_groups: dict[tuple[Any, ...], list[float]] = defaultdict(list)

    for row in generic:
        _, model, strategy = _quality_key(row)
        onset = _flt(row, "onset_tokens")
        beta = _flt(row, "beta")
        fidelity = _flt(row, "per_compaction_fidelity")
        max_attempts = _int(row, "max_attempts")
        profile = _text(row, "evidence_profile")
        completion = _flt(row, "completion_probability")
        assigned = _flt(row, "provider_cost_per_assigned_session_usd")
        if None in {onset, beta, fidelity, max_attempts, completion, assigned}:
            continue
        assert onset is not None and beta is not None and fidelity is not None
        assert (
            max_attempts is not None and completion is not None and assigned is not None
        )
        beta_groups[(model, strategy, onset, fidelity, max_attempts, profile)].append(
            (beta, completion)
        )
        fidelity_groups[(model, strategy, onset, beta, max_attempts, profile)].append(
            (fidelity, completion)
        )
        onset_groups[(model, strategy, beta, fidelity, max_attempts, profile)].append(
            (onset, completion)
        )
        retry_groups[(model, strategy, onset, beta, fidelity, profile)].append(
            (max_attempts, completion, assigned)
        )
        if strategy == "grow_to_800k":
            grow_fidelity_groups[(model, onset, beta, max_attempts, profile)].append(
                completion
            )
        if beta == 0.0 and fidelity == 1.0:
            null_groups[(model, onset, max_attempts, profile)].append(completion)
        if strategy in {
            "cap_200k_uncached",
            "cap_200k_cache_read",
            "cap_200k_cache_write",
        }:
            cache_mode_groups[
                (model, onset, beta, fidelity, max_attempts, profile)
            ].append(completion)

    for key, points in beta_groups.items():
        ordered = [value for _x, value in sorted(points)]
        audit.check(
            _nonincreasing(ordered),
            "metamorphic.beta",
            "Increasing context-rot beta must not improve completion probability.",
            group=key,
            values=ordered,
        )
    for key, points in fidelity_groups.items():
        ordered = [value for _x, value in sorted(points)]
        audit.check(
            _nondecreasing(ordered),
            "metamorphic.fidelity",
            "Increasing summary fidelity must not reduce completion probability.",
            group=key,
            values=ordered,
        )
    for key, points in onset_groups.items():
        ordered = [value for _x, value in sorted(points)]
        audit.check(
            _nondecreasing(ordered),
            "metamorphic.onset",
            "With a fixed 100K exposure unit, increasing onset must not reduce completion probability.",
            group=key,
            values=ordered,
        )
    for key, points in retry_groups.items():
        ordered = sorted(points)
        completions = [item[1] for item in ordered]
        assigned_costs = [item[2] for item in ordered]
        audit.check(
            _nondecreasing(completions),
            "metamorphic.retry_completion",
            "Increasing the retry cap must not reduce completion probability.",
            group=key,
            values=completions,
        )
        audit.check(
            _nondecreasing(assigned_costs),
            "metamorphic.retry_cost",
            "Increasing the retry cap must not reduce expected assigned provider spend.",
            group=key,
            values=assigned_costs,
        )
    for key, values in grow_fidelity_groups.items():
        audit.check(
            max(values) - min(values) <= 1e-12,
            "metamorphic.no_compaction_fidelity",
            "Fidelity must not affect an uncompacted trajectory.",
            group=key,
            min=min(values),
            max=max(values),
        )
    for key, values in null_groups.items():
        audit.check(
            len(values) == len(SOURCE_STRATEGY_ORIGINS)
            and max(values) - min(values) <= 1e-12,
            "metamorphic.null_equivalence",
            "At beta=0 and fidelity=1 all strategies must have exactly equal modeled quality.",
            group=key,
            count=len(values),
            min=min(values),
            max=max(values),
        )
    for key, values in cache_mode_groups.items():
        audit.check(
            len(values) == 3 and max(values) - min(values) <= 1e-12,
            "separation.cache_price_quality",
            "Changing only the compaction billing bucket must not change modeled quality.",
            group=key,
            count=len(values),
            min=min(values),
            max=max(values),
        )


def _audit_primary_case(
    trajectories: Mapping[tuple[str, str, float], Mapping[str, str]],
    strata: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    aggregates: Mapping[tuple[str, str, str], Mapping[str, str]],
    source: Mapping[tuple[str, str], SourceScenario],
    audit: Audit,
) -> None:
    expected_beta = math.log(2.0) * 13.0 / 31.0
    expected_grow_exposure = 31.0 / 13.0
    expected_cap_fidelity = (
        9 * 0.95**4 + 9 * 0.95**3 + 9 * 0.95**2 + 9 * 0.95 + 3
    ) / 39
    for model in MODELS:
        for strategy in SOURCE_STRATEGY_ORIGINS:
            trajectory = trajectories.get((model, strategy, 200_000.0))
            audit.check(
                trajectory is not None,
                "primary.trajectory",
                "Primary onset trajectory is missing.",
                model=model,
                strategy=strategy,
            )
            if trajectory is None:
                continue
            expected_exposure = float(
                _context_exposure(source[(model, strategy)].main_prompts, 200_000)[
                    "normalized_excess_units"
                ]
            )
            audit.check(
                _float_close(
                    _flt(trajectory, "normalized_excess_auc"), expected_exposure
                ),
                "primary.exposure",
                "Primary exposure differs from the hand calculation.",
                model=model,
                strategy=strategy,
                expected=expected_exposure,
                observed=_flt(trajectory, "normalized_excess_auc"),
            )
        grow = trajectories.get((model, "grow_to_800k", 200_000.0))
        if grow is not None:
            audit.check(
                _float_close(
                    _flt(grow, "normalized_excess_auc"), expected_grow_exposure
                ),
                "primary.grow_31_over_13",
                "Grow trajectory at 200K onset must have exposure 31/13.",
                model=model,
                expected=expected_grow_exposure,
                observed=_flt(grow, "normalized_excess_auc"),
            )

        for strategy in SOURCE_STRATEGY_ORIGINS:
            aggregate = aggregates.get((PRIMARY_ASSUMPTION_ID, model, strategy))
            if not audit.check(
                aggregate is not None,
                "primary.aggregate",
                "Primary aggregate row is missing.",
                model=model,
                strategy=strategy,
            ):
                continue
            audit.check(
                _float_close(_flt(aggregate, "beta"), expected_beta),
                "primary.beta",
                "Primary beta must be ln(2)*13/31.",
                model=model,
                strategy=strategy,
                expected=expected_beta,
                observed=_flt(aggregate, "beta"),
            )
            expected_fidelity = _effective_fidelity(
                39, source[(model, strategy)].compaction_positions, 0.95, "uniform"
            )
            audit.check(
                _float_close(
                    _flt(aggregate, "effective_evidence_fidelity"), expected_fidelity
                ),
                "primary.effective_fidelity",
                "Primary effective evidence fidelity differs from the hand oracle.",
                model=model,
                strategy=strategy,
                expected=expected_fidelity,
                observed=_flt(aggregate, "effective_evidence_fidelity"),
            )
            if strategy in {
                "cap_200k_uncached",
                "cap_200k_cache_read",
                "cap_200k_cache_write",
            }:
                audit.check(
                    _float_close(expected_fidelity, expected_cap_fidelity),
                    "primary.uniform_fidelity_oracle",
                    "Four-compaction uniform fidelity must equal (9f^4+9f^3+9f^2+9f+3)/39.",
                    model=model,
                    strategy=strategy,
                    expected=expected_cap_fidelity,
                    observed=expected_fidelity,
                )
            for stratum_id, (_weight, p0) in TASK_STRATA.items():
                stratum = strata.get(
                    (PRIMARY_ASSUMPTION_ID, model, strategy, stratum_id)
                )
                if stratum is None:
                    continue
                exposure = float(_flt(aggregate, "normalized_excess_auc") or 0.0)
                probability = _single_attempt_probability(
                    p0, expected_beta, exposure, expected_fidelity
                )
                retry = _retry_exact(
                    probability, float(source[(model, strategy)].provider_cost_usd), 3
                )
                audit.check(
                    _float_close(
                        _flt(stratum, "single_attempt_success_probability"), probability
                    ),
                    "primary.single_probability",
                    "Primary stratum probability differs from its hand formula.",
                    model=model,
                    strategy=strategy,
                    stratum=stratum_id,
                    expected=probability,
                    observed=_flt(stratum, "single_attempt_success_probability"),
                )
                audit.check(
                    _float_close(
                        _flt(stratum, "completion_probability"),
                        retry["completion_probability"],
                    ),
                    "primary.retry_completion",
                    "Primary K=3 completion differs from 1-(1-p)^3.",
                    model=model,
                    strategy=strategy,
                    stratum=stratum_id,
                )
                audit.check(
                    _float_close(
                        _flt(stratum, "expected_attempts"), retry["expected_attempts"]
                    ),
                    "primary.retry_attempts",
                    "Primary K=3 expected attempts differ from 1+(1-p)+(1-p)^2.",
                    model=model,
                    strategy=strategy,
                    stratum=stratum_id,
                )
    audit.check(
        _float_close(expected_cap_fidelity, 0.890241826923077),
        "primary.fidelity_numeric",
        "Independent primary fidelity hand constant must remain stable.",
        expected=0.890241826923077,
        observed=expected_cap_fidelity,
    )


def _audit_study_and_dictionary(
    study: Mapping[str, Any],
    dictionary: Mapping[str, Any],
    manifest: Mapping[str, Any],
    table_rows: Mapping[str, Sequence[Mapping[str, str]]],
    aggregates: Mapping[tuple[str, str, str], Mapping[str, str]],
    contrasts: Mapping[str, Mapping[str, str]],
    audit: Audit,
) -> None:
    audit.check(
        study.get("execution_mode") == "offline-statistical-simulation",
        "study.execution_mode",
        "Study must explicitly identify offline statistical simulation mode.",
        observed=study.get("execution_mode"),
    )
    audit.check(
        study.get("real_pi_or_copilot_or_model_calls") is False,
        "study.no_real_calls",
        "Study must explicitly state that no Pi, Copilot, or model calls occurred.",
        observed=study.get("real_pi_or_copilot_or_model_calls"),
    )
    audit.check(
        manifest.get("execution_mode") == "offline-statistical-simulation",
        "manifest.execution_mode",
        "Manifest must explicitly identify offline statistical simulation mode.",
        observed=manifest.get("execution_mode"),
    )
    audit.check(
        manifest.get("real_pi_or_copilot_or_model_calls") is False,
        "manifest.no_real_calls",
        "Manifest must explicitly state that no Pi, Copilot, or model calls occurred.",
        observed=manifest.get("real_pi_or_copilot_or_model_calls"),
    )
    uncertainty_scope = _text(manifest, "monte_carlo_uncertainty_scope").lower()
    audit.check(
        "conditional" in uncertainty_scope and "assumption" in uncertainty_scope,
        "manifest.mc_scope",
        "Monte Carlo uncertainty must be explicitly conditional on declared assumptions.",
        observed=uncertainty_scope,
    )
    audit.check(
        study.get("source_type") == "simulated"
        and manifest.get("source_type") == "simulated",
        "study.source_type",
        "Study and manifest must classify generated results as simulated.",
    )
    formulas = study.get("formulas")
    normalization = (
        str(formulas.get("normalized_excess_auc", ""))
        if isinstance(formulas, Mapping)
        else ""
    )
    audit.check(
        "100000" in normalization.replace(" ", "")
        and "2*" not in normalization.replace(" ", ""),
        "study.exposure_formula",
        "Study must declare the fixed 100,000-token exposure unit.",
        observed=normalization,
    )
    dictionary_text = json.dumps(dictionary, sort_keys=True).replace(" ", "").lower()
    audit.check(
        "100000" in dictionary_text
        and "2*sum(max(prompt-onset,0))/(onset" not in dictionary_text,
        "dictionary.exposure_formula",
        "Data dictionary must document the fixed 100,000-token exposure unit without the superseded onset-scaled formula.",
    )
    row_counts = study.get("row_counts")
    audit.check(
        isinstance(row_counts, Mapping),
        "study.row_counts",
        "Study must contain table row counts.",
    )
    if isinstance(row_counts, Mapping):
        for filename, rows in table_rows.items():
            audit.check(
                _int(row_counts, filename) == len(rows),
                "study.row_count",
                "Study row count differs from generated CSV.",
                filename=filename,
                expected=len(rows),
                observed=row_counts.get(filename),
            )
    manifest_inputs = manifest.get("input_files")
    study_inputs = study.get("input_hashes")
    if isinstance(manifest_inputs, Mapping) and isinstance(study_inputs, Mapping):
        normalized_manifest_inputs = {
            str(filename): metadata.get("sha256")
            for filename, metadata in manifest_inputs.items()
            if isinstance(metadata, Mapping)
        }
        audit.check(
            normalized_manifest_inputs == dict(study_inputs),
            "study.input_hashes",
            "Study and manifest must bind the same input hashes.",
            manifest=normalized_manifest_inputs,
            study=study_inputs,
        )

    primary = study.get("primary_case")
    audit.check(
        isinstance(primary, Mapping),
        "study.primary_case",
        "Study must expose the primary case in machine-readable form.",
    )
    if isinstance(primary, Mapping):
        audit.check(
            primary.get("parameter_set_id") == PRIMARY_ASSUMPTION_ID,
            "study.primary_id",
            "Primary parameter-set ID is incorrect.",
            observed=primary.get("parameter_set_id"),
        )
        audit.check(
            _float_close(_flt(primary, "onset_tokens"), 200_000.0),
            "study.primary_onset",
            "Primary onset must be 200,000 tokens.",
            observed=primary.get("onset_tokens"),
        )
        audit.check(
            _float_close(_flt(primary, "grow_normalized_excess_auc"), 31.0 / 13.0),
            "study.primary_exposure",
            "Primary grow exposure must be 31/13.",
            observed=primary.get("grow_normalized_excess_auc"),
        )
        audit.check(
            _float_close(_flt(primary, "beta"), math.log(2.0) * 13.0 / 31.0),
            "study.primary_beta",
            "Primary beta must be ln(2)*13/31.",
            observed=primary.get("beta"),
        )
        primary_aggregates = primary.get("aggregates")
        if isinstance(primary_aggregates, list):
            audit.check(
                len(primary_aggregates) == len(MODELS) * len(SOURCE_STRATEGY_ORIGINS),
                "study.primary_aggregate_count",
                "Primary case must contain all 15 model/strategy aggregates.",
                observed=len(primary_aggregates),
            )
            for item in primary_aggregates:
                if not isinstance(item, Mapping):
                    continue
                key = _quality_key(item)
                csv_row = aggregates.get(key)
                audit.check(
                    csv_row is not None,
                    "study.primary_aggregate_key",
                    "Embedded primary aggregate must resolve to the CSV.",
                    key=key,
                )
                if csv_row is not None:
                    for field_name in (
                        "completion_probability",
                        "provider_cost_per_assigned_session_usd",
                        "provider_cost_per_successful_session_usd",
                    ):
                        audit.check(
                            _float_close(
                                _flt(item, field_name), _flt(csv_row, field_name)
                            ),
                            "study.primary_aggregate_value",
                            "Embedded primary aggregate differs from CSV.",
                            key=key,
                            field=field_name,
                        )
        primary_contrasts = primary.get("contrasts")
        if isinstance(primary_contrasts, list):
            audit.check(
                len(primary_contrasts)
                == len(MODELS) * (len(SOURCE_STRATEGY_ORIGINS) - 1),
                "study.primary_contrast_count",
                "Primary case must contain all 12 compact-vs-grow contrasts.",
                observed=len(primary_contrasts),
            )
            for item in primary_contrasts:
                if not isinstance(item, Mapping):
                    continue
                contrast_id = str(item.get("quality_contrast_id", ""))
                csv_row = contrasts.get(contrast_id)
                audit.check(
                    csv_row is not None,
                    "study.primary_contrast_key",
                    "Embedded primary contrast must resolve to the CSV.",
                    quality_contrast_id=contrast_id,
                )
                if csv_row is not None:
                    for field_name in (
                        "delta_completion_probability_comparison_minus_baseline",
                        "delta_provider_cost_per_successful_session_usd",
                    ):
                        audit.check(
                            _float_close(
                                _flt(item, field_name), _flt(csv_row, field_name)
                            ),
                            "study.primary_contrast_value",
                            "Embedded primary contrast differs from CSV.",
                            quality_contrast_id=contrast_id,
                            field=field_name,
                        )

    mc_design = study.get("monte_carlo_design")
    audit.check(
        isinstance(mc_design, Mapping),
        "study.mc_design",
        "Study must expose the paired Monte Carlo design.",
    )
    if isinstance(mc_design, Mapping):
        audit.check(
            _int(mc_design, "task_count_per_sentinel") == 200_000
            and _int(mc_design, "seed") == 20_260_904,
            "study.mc_budget",
            "MC design must use 200,000 tasks per sentinel and seed 20260904.",
            observed=mc_design,
        )
        audit.check(
            mc_design.get("raw_task_rows_retained") is False,
            "study.mc_no_raw_rows",
            "MC design must state that raw task rows were not materialized.",
            observed=mc_design.get("raw_task_rows_retained"),
        )

    limitations = " ".join(map(str, study.get("limitations", []))).lower()
    audit.check(
        "hypothetical" in limitations and "cannot prove" in limitations,
        "study.inference_boundary",
        "Limitations must state that quality is hypothetical and simulation cannot prove real-world context rot.",
    )


def validate_bundle(
    bundle: Path,
    cost_bundle: Path,
) -> tuple[Audit, dict[str, Any]]:
    audit = Audit()
    audit.check(
        bundle.is_dir(),
        "bundle.directory",
        "Context-rot bundle must be a directory.",
        path=bundle,
    )
    for filename in REQUIRED_CONTEXT_FILES:
        audit.check(
            (bundle / filename).is_file(),
            "bundle.file",
            "Required context-rot artifact is missing.",
            path=bundle / filename,
        )
    observed_files = {path.name for path in bundle.iterdir() if path.is_file()}
    allowed_files = set(REQUIRED_CONTEXT_FILES) | {
        "README.md",
        "independent-validation-report.json",
    }
    audit.check(
        not (observed_files - allowed_files),
        "bundle.unexpected_files",
        "Context-rot bundle may contain only generated artifacts and allowlisted audit documentation.",
        unexpected=sorted(observed_files - allowed_files),
    )
    audit.check(
        not (set(LEGACY_RAW_CONTEXT_FILES) & observed_files),
        "bundle.legacy_raw_csv",
        "Superseded uncompressed large CSV artifacts must not remain beside gzip outputs.",
        observed=sorted(set(LEGACY_RAW_CONTEXT_FILES) & observed_files),
    )
    if audit.failures:
        return audit, audit.as_report(bundle, cost_bundle)

    source = _load_source_cost_bundle(cost_bundle, audit)
    tables: dict[str, list[dict[str, str]]] = {}
    for filename in REQUIRED_CONTEXT_FILES:
        if filename.endswith((".csv", ".csv.gz")):
            rows = _read_csv(bundle / filename, audit)
            _audit_no_nonfinite(rows, filename, audit)
            tables[filename] = rows
    study_raw = _read_json(bundle / "study-results.json", audit)
    dictionary_raw = _read_json(bundle / "data-dictionary.json", audit)
    manifest_raw = _read_json(bundle / "manifest.json", audit)
    study = study_raw if isinstance(study_raw, Mapping) else {}
    dictionary = dictionary_raw if isinstance(dictionary_raw, Mapping) else {}
    manifest = manifest_raw if isinstance(manifest_raw, Mapping) else {}
    audit.check(
        isinstance(study_raw, Mapping),
        "study.root",
        "study-results.json must contain a JSON object.",
    )
    audit.check(
        isinstance(dictionary_raw, Mapping),
        "dictionary.root",
        "data-dictionary.json must contain a JSON object.",
    )
    audit.check(
        isinstance(manifest_raw, Mapping),
        "manifest.root",
        "manifest.json must contain a JSON object.",
    )
    _audit_json_finite(study_raw, audit)
    _audit_json_finite(dictionary_raw, audit)
    _audit_json_finite(manifest_raw, audit)

    checksum_entries = _audit_checksum_inventory(
        bundle,
        "checksums.sha256",
        audit,
        required_names=REQUIRED_CONTEXT_FILES,
    )
    expected_checksum_names = set(REQUIRED_CONTEXT_FILES) - {"checksums.sha256"}
    audit.check(
        set(checksum_entries) == expected_checksum_names,
        "hash.inventory",
        "Context checksum inventory must exactly cover every generated artifact except itself.",
        expected=sorted(expected_checksum_names),
        observed=sorted(checksum_entries),
    )
    _audit_context_manifest(bundle, manifest, tables, cost_bundle, audit)

    trajectory_lookup = _audit_trajectories(
        tables["trajectory-metrics.csv"], source, audit
    )
    stratum_lookup = _audit_strata(
        tables["quality-stratum-results.csv.gz"],
        trajectory_lookup,
        source,
        audit,
    )
    aggregate_lookup = _audit_aggregates(
        tables["quality-aggregate-results.csv.gz"],
        stratum_lookup,
        source,
        audit,
    )
    contrast_lookup = _audit_contrasts(
        tables["quality-contrast-results.csv.gz"],
        aggregate_lookup,
        audit,
    )
    _audit_break_even(tables["break-even.csv.gz"], contrast_lookup, audit)
    _audit_scale(tables["scale-results.csv.gz"], aggregate_lookup, audit)
    _audit_evidence(
        tables["evidence-curves.csv"],
        tables["evidence-onsets.csv"],
        audit,
    )
    _audit_fidelity_boundaries(tables["fidelity-boundaries.csv"], source, audit)
    _audit_monte_carlo(
        tables["monte-carlo-summary.csv"],
        aggregate_lookup,
        stratum_lookup,
        audit,
    )
    _audit_metamorphic_properties(tables["quality-aggregate-results.csv.gz"], audit)
    _audit_primary_case(
        trajectory_lookup,
        stratum_lookup,
        aggregate_lookup,
        source,
        audit,
    )
    _audit_study_and_dictionary(
        study,
        dictionary,
        manifest,
        tables,
        aggregate_lookup,
        contrast_lookup,
        audit,
    )
    return audit, audit.as_report(bundle, cost_bundle)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Independently audit an offline Pi context-rot simulation bundle "
            "against its versioned Pi cost source. Uses only Python's standard "
            "library and performs no Pi, Copilot, model, API, or network calls."
        )
    )
    parser.add_argument(
        "bundle",
        type=Path,
        help="Generated context-rot bundle directory",
    )
    parser.add_argument(
        "--cost-bundle",
        type=Path,
        required=True,
        help="Versioned pi-cost-elasticity source bundle directory",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional JSON report path; the report is always printed to stdout",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    _, report = validate_bundle(args.bundle, args.cost_bundle)
    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.report is not None:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(rendered, encoding="utf-8", newline="\n")
        except OSError as exc:
            print(
                json.dumps(
                    {
                        "status": "fail",
                        "failure_count": 1,
                        "failures": [
                            {
                                "code": "report.write",
                                "message": "Could not write JSON validation report.",
                                "context": {
                                    "path": str(args.report),
                                    "error": str(exc),
                                },
                            }
                        ],
                    },
                    indent=2,
                ),
                file=sys.stderr,
            )
            return 2
    print(rendered, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
