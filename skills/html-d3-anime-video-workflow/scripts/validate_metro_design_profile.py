#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from compile_metro_design_profile import DEFAULT_PROFILE, compile_profile, load_design_profile, profile_prompt_contract


SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the bundled Metro design profile and its tonal-audit enforcement without a browser."
    )
    parser.add_argument("--design-profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--style", type=Path)
    parser.add_argument("--colorset1", type=Path)
    parser.add_argument("--colorset2", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def canonical_digest(profile: dict[str, Any]) -> str:
    payload = dict(profile)
    payload.pop("profileSha256", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def fixture_html(color: str) -> str:
    return f"""<!doctype html>
<html><head><style>
html, body {{ font-family: 'Open Sans', Arial, sans-serif; background: #ffffff; }}
</style></head><body>
<svg width="320" height="240"><rect width="320" height="240" fill="{color}"></rect></svg>
</body></html>
"""


def run_case(
    *,
    name: str,
    html: Path,
    manifest: Path,
    profile: Path,
    extra_args: list[str],
    expected_pass: bool,
    expected_code: str | None,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "audit_metro_tonal_style.py"),
        "--html",
        str(html),
        "--design-profile",
        str(profile),
        "--output",
        str(manifest),
        *extra_args,
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    data = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {}
    codes = sorted(
        str(item.get("code"))
        for item in data.get("findings", [])
        if isinstance(item, dict) and item.get("code")
    )
    actual_pass = result.returncode == 0 and data.get("passed") is True
    case_passed = actual_pass is expected_pass and (expected_code is None or expected_code in codes)
    return {
        "name": name,
        "passed": case_passed,
        "expectedPass": expected_pass,
        "actualPass": actual_pass,
        "expectedCode": expected_code,
        "codes": codes,
        "returnCode": result.returncode,
    }


def main() -> int:
    args = parse_args()
    profile = load_design_profile(args.design_profile)
    findings: list[dict[str, Any]] = []

    def require(condition: bool, code: str, **evidence: Any) -> None:
        if not condition:
            findings.append({"code": code, **evidence})

    require(profile.get("profileSha256") == canonical_digest(profile), "profile-digest-mismatch")
    require(all(profile.get("style", {}).get("rules", {}).values()), "profile-style-rules-incomplete")
    geometry = profile.get("geometry", {})
    require(geometry.get("cornerRadiusPx") == 0, "profile-nonzero-corner-radius")
    require(geometry.get("internalPaddingPx") == 0, "profile-nonzero-internal-padding")
    require(geometry.get("gridPx") == 4, "profile-wrong-grid-size")
    colors1 = set(profile.get("colorsets", {}).get("colorset1", {}).get("colors", []))
    colors2 = set(profile.get("colorsets", {}).get("colorset2", {}).get("colors", []))
    require("#ccd6e3" not in colors1, "profile-admits-undeclared-gray")
    require("#007298" in colors2 and "#007298" not in colors1, "profile-colorset2-distinction-missing")
    policy = profile.get("policy", {})
    require(policy.get("colorset2RequiresRecordedReason") is True, "profile-colorset2-reason-policy-missing")
    prompt_contract = profile_prompt_contract(profile)
    require(str(profile.get("profileSha256")) in prompt_contract, "prompt-contract-missing-profile-digest")
    require("0 px internal box padding" in prompt_contract, "prompt-contract-missing-zero-padding")
    source_paths = [args.style, args.colorset1, args.colorset2]
    source_verification: dict[str, Any] | None = None
    if any(source_paths):
        if not args.style or not args.colorset1:
            raise ValueError("--style and --colorset1 are both required for source-drift verification.")
        source_profile = compile_profile(args.style, args.colorset1, args.colorset2)
        source_verification = {
            "profileSha256": source_profile.get("profileSha256"),
            "matchesBundledProfile": source_profile.get("profileSha256") == profile.get("profileSha256"),
        }
        require(source_verification["matchesBundledProfile"], "profile-source-drift")

    with tempfile.TemporaryDirectory(prefix="metro-design-profile-") as temp:
        temp_dir = Path(temp)
        valid_html = temp_dir / "valid.html"
        invalid_html = temp_dir / "invalid.html"
        invalid_rgb_html = temp_dir / "invalid-rgb.html"
        invalid_hsl_html = temp_dir / "invalid-hsl.html"
        colorset2_html = temp_dir / "colorset2.html"
        valid_html.write_text(fixture_html("#9e1b32"), encoding="utf-8")
        invalid_html.write_text(fixture_html("#ccd6e3"), encoding="utf-8")
        invalid_rgb_html.write_text(fixture_html("rgb(0, 255, 0)"), encoding="utf-8")
        invalid_hsl_html.write_text(fixture_html("hsl(120, 100%, 50%)"), encoding="utf-8")
        colorset2_html.write_text(fixture_html("#007298"), encoding="utf-8")
        cases = [
            run_case(
                name="colorset1-valid-passes",
                html=valid_html,
                manifest=temp_dir / "valid.json",
                profile=args.design_profile,
                extra_args=[],
                expected_pass=True,
                expected_code=None,
            ),
            run_case(
                name="undeclared-gray-fails",
                html=invalid_html,
                manifest=temp_dir / "invalid.json",
                profile=args.design_profile,
                extra_args=[],
                expected_pass=False,
                expected_code="non-selected-colorset-colors",
            ),
            run_case(
                name="undeclared-rgb-fails",
                html=invalid_rgb_html,
                manifest=temp_dir / "invalid-rgb.json",
                profile=args.design_profile,
                extra_args=[],
                expected_pass=False,
                expected_code="non-selected-colorset-colors",
            ),
            run_case(
                name="undeclared-hsl-fails",
                html=invalid_hsl_html,
                manifest=temp_dir / "invalid-hsl.json",
                profile=args.design_profile,
                extra_args=[],
                expected_pass=False,
                expected_code="non-selected-colorset-colors",
            ),
            run_case(
                name="colorset2-without-reason-fails",
                html=colorset2_html,
                manifest=temp_dir / "colorset2-no-reason.json",
                profile=args.design_profile,
                extra_args=["--allow-colorset2"],
                expected_pass=False,
                expected_code="missing-colorset2-reason",
            ),
            run_case(
                name="colorset2-with-reason-passes",
                html=colorset2_html,
                manifest=temp_dir / "colorset2-reason.json",
                profile=args.design_profile,
                extra_args=["--allow-colorset2", "--colorset2-reason", "Distinct semantic category"],
                expected_pass=True,
                expected_code=None,
            ),
        ]

    for case in cases:
        if not case["passed"]:
            findings.append({"code": "design-profile-fixture-failed", "case": case["name"]})
    report = {
        "passed": not findings,
        "designProfile": {
            "path": args.design_profile.as_posix(),
            "profileId": profile.get("profileId"),
            "profileVersion": profile.get("profileVersion"),
            "profileSha256": profile.get("profileSha256"),
            "sourceDigests": {
                key: value.get("sha256")
                for key, value in profile.get("sources", {}).items()
                if isinstance(value, dict)
            },
        },
        "cases": cases,
        "sourceVerification": source_verification,
        "findings": findings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output.as_posix(), "passed": report["passed"], "cases": len(cases)}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
