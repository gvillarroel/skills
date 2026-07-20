#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Exercise adversarial contracts that ordinary happy-path builds cannot prove."""

from __future__ import annotations

import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from build_procedural_svg import Context, PALETTES, build_svg, load_catalog, resolve_parameters
from validate_procedural_svg import MOTION_TAGS, local_name, load_catalog as load_validation_catalog
from validate_procedural_svg import validate_one


PATTERN_ID = "procedural-svg-alpha-persistence"
SEED = 104729


def validate(path: Path, pattern_id: str = PATTERN_ID) -> dict[str, object]:
    return validate_one(
        path,
        load_validation_catalog(),
        require_motion=True,
        require_standalone=True,
        expect_pattern_id=pattern_id,
        expect_seed=SEED,
        expect_palette="colorset2",
        expect_motion="full",
        min_elements=12,
        max_bytes=None,
    )


def write_tree(path: Path, root: ET.Element) -> None:
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def require_failure(
    path: Path,
    root: ET.Element,
    expected_error_fragment: str,
    pattern_id: str = PATTERN_ID,
) -> dict[str, object]:
    write_tree(path, root)
    result = validate(path, pattern_id)
    errors = [str(value) for value in result.get("errors", [])]
    if bool(result.get("ok")) or not any(expected_error_fragment in value for value in errors):
        raise AssertionError(
            f"Adversarial artifact {path.name} did not fail with "
            f"{expected_error_fragment!r}: {errors!r}"
        )
    return {"case": path.stem, "matched": expected_error_fragment}


def canonical_source(
    patterns: dict[str, dict[str, object]], pattern_id: str, *, seed: int = SEED
) -> str:
    spec = patterns[pattern_id]
    context = Context(
        spec=spec,
        seed=seed,
        width=960,
        height=640,
        duration_ms=6000,
        palette_name="colorset2",
        palette=PALETTES["colorset2"],
        motion="full",
        parameters=resolve_parameters(spec, {}),
    )
    return build_svg(context)


def audit_transport_svg_evidence(source: str, tolerance: float = 1e-7) -> dict[str, object]:
    root = ET.fromstring(source)
    animated = next(
        element for element in root.iter() if element.get("data-motion-layer") == "animated"
    )
    checkpoint_groups = [
        element
        for element in animated.iter()
        if element.get("data-sinkhorn-iteration") is not None
    ]
    if not checkpoint_groups:
        raise AssertionError("Transport SVG has no serialized Sinkhorn checkpoints.")
    final_checkpoint = max(
        checkpoint_groups, key=lambda element: int(element.get("data-sinkhorn-iteration", "-1"))
    )
    scaling: dict[str, dict[int, float]] = {"u": {}, "v": {}}
    for element in final_checkpoint.iter():
        role = element.get("data-scaling-role")
        if role not in scaling:
            continue
        scaling[role][int(element.get("data-scaling-index", "-1"))] = float(
            element.get("data-scaling-value", "nan")
        )
    kernel = {
        (
            int(element.get("data-kernel-row", "-1")),
            int(element.get("data-kernel-column", "-1")),
        ): float(element.get("data-kernel-value", "nan"))
        for element in animated.iter()
        if element.get("data-kernel-value") is not None
    }
    plan = {
        (
            int(element.get("data-plan-source", "-1")),
            int(element.get("data-plan-target", "-1")),
        ): float(element.get("data-plan-mass", "nan"))
        for element in animated.iter()
        if element.get("data-plan-mass") is not None
    }
    if not scaling["u"] or not scaling["v"] or not kernel or set(kernel) != set(plan):
        raise AssertionError("Transport SVG factorization evidence is incomplete.")
    errors = {
        entry: abs(
            plan[entry]
            - scaling["u"][entry[0]] * kernel[entry] * scaling["v"][entry[1]]
        )
        for entry in plan
    }
    maximum_error = max(errors.values())
    if maximum_error > tolerance:
        worst_entry = max(errors, key=errors.get)  # type: ignore[arg-type]
        raise AssertionError(
            f"Serialized transport factorization error {maximum_error:.12g} exceeds "
            f"{tolerance:.12g} at plan entry {worst_entry}."
        )
    return {
        "case": "serialized-transport-factorization-seed-20260720",
        "entries": len(plan),
        "maximumError": maximum_error,
        "tolerance": tolerance,
    }


def main() -> int:
    _catalog, patterns = load_catalog()
    source = canonical_source(patterns, PATTERN_ID)
    findings: list[dict[str, object]] = []
    evidence_checks = [
        audit_transport_svg_evidence(
            canonical_source(
                patterns, "procedural-svg-optimal-transport", seed=20260720
            )
        )
    ]
    clean_patterns = [PATTERN_ID]
    with tempfile.TemporaryDirectory(prefix="procedural-svg-contract-") as directory:
        root_directory = Path(directory)
        clean_path = root_directory / "clean.svg"
        clean_path.write_text(source, encoding="utf-8", newline="\n")
        clean_result = validate(clean_path)
        if not bool(clean_result.get("ok")):
            raise AssertionError(f"Clean canonical artifact failed: {clean_result.get('errors')!r}")

        swapped_root = ET.fromstring(source)
        animated = next(
            element
            for element in swapped_root.iter()
            if element.get("data-motion-layer") == "animated"
        )
        strata = {
            str(element.get("data-stratum")): element
            for element in animated.iter()
            if element.get("data-stratum")
        }
        samples = strata["samples"]
        delaunay = strata["delaunay"]
        sample_children = list(samples)
        delaunay_children = list(delaunay)
        for child in sample_children:
            samples.remove(child)
        for child in delaunay_children:
            delaunay.remove(child)
        samples.extend(delaunay_children)
        delaunay.extend(sample_children)
        findings.append(
            require_failure(
                root_directory / "swapped-strata.svg",
                swapped_root,
                "differs from the canonical solver render",
            )
        )

        schedule_root = ET.fromstring(source)
        animations = [
            element
            for element in schedule_root.iter()
            if local_name(element.tag) in MOTION_TAGS
        ]
        first_values = animations[0].get("values", "")
        for animation in animations:
            animation.set("values", first_values)
        findings.append(
            require_failure(
                root_directory / "lockstep-snapshots.svg",
                schedule_root,
                "exact one-hot palindromic schedule",
            )
        )

        role_root = ET.fromstring(source)
        animated_layer = next(
            element
            for element in role_root.iter()
            if element.get("data-motion-layer") == "animated"
        )
        reduced_layer = next(
            element
            for element in role_root.iter()
            if element.get("data-motion-layer") == "reduced"
        )
        animated_layer.set("class", "psvg-reduced-layer")
        reduced_layer.set("class", "psvg-motion-layer")
        findings.append(
            require_failure(
                root_directory / "swapped-motion-roles.svg",
                role_root,
                "must use only the psvg-motion-layer role class",
            )
        )

        transport_id = "procedural-svg-optimal-transport"
        transport_source = canonical_source(patterns, transport_id)
        transport_path = root_directory / "clean-transport.svg"
        transport_path.write_text(transport_source, encoding="utf-8", newline="\n")
        transport_result = validate(transport_path, transport_id)
        if not bool(transport_result.get("ok")):
            raise AssertionError(
                f"Clean transport artifact failed: {transport_result.get('errors')!r}"
            )
        clean_patterns.append(transport_id)
        scaling_root = ET.fromstring(transport_source)
        scaling_bar = next(
            element
            for element in scaling_root.iter()
            if element.get("data-scaling-role") == "u"
        )
        scaling_bar.set("height", str(float(scaling_bar.get("height", "1")) + 0.75))
        findings.append(
            require_failure(
                root_directory / "tampered-sinkhorn-scaling.svg",
                scaling_root,
                "differs from the canonical solver render",
                transport_id,
            )
        )

        front_id = "procedural-svg-fast-marching-front"
        front_source = canonical_source(patterns, front_id)
        front_path = root_directory / "clean-front.svg"
        front_path.write_text(front_source, encoding="utf-8", newline="\n")
        front_result = validate(front_path, front_id)
        if not bool(front_result.get("ok")):
            raise AssertionError(
                f"Clean Fast Marching artifact failed: {front_result.get('errors')!r}"
            )
        clean_patterns.append(front_id)
        trial_root = ET.fromstring(front_source)
        trial_path = next(
            element
            for element in trial_root.iter()
            if element.get("data-trial-time-bucket") is not None
        )
        trial_path.set("d", f'{trial_path.get("d", "")} M 0 0 L 1 1')
        findings.append(
            require_failure(
                root_directory / "tampered-fast-marching-trial.svg",
                trial_root,
                "differs from the canonical solver render",
                front_id,
            )
        )

    print(
        json.dumps(
            {
                "ok": True,
                "cleanCanonicalStrata": clean_result["counts"]["canonicalStrataVerified"],
                "cleanPatterns": clean_patterns,
                "evidenceChecks": evidence_checks,
                "adversarialCases": findings,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
