#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the authored design contract without running a model or host UI."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


VALUE = re.compile(r'^\s*value:\s*"(#[0-9a-fA-F]{6})"\s*$', re.M)
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEURISTIC_ROW = re.compile(r"^\|\s*(H[0-9]+)\s*\|", re.M)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045
              else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return sum(channel * weight for channel, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(foreground: str, background: str) -> float:
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def anchors(text: str) -> set[str]:
    result = set()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        heading = re.sub(r"[^\w\- ]", "", heading.lower())
        result.add(heading.replace(" ", "-"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output", type=Path, help="Optional JSON report; default is stdout only")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    bundle = root / "skills/desktop-plugin-ui"
    entry = bundle / "SKILL.md"
    reference = bundle / "references/usability-and-color.md"
    checks: list[dict] = []

    def record(name: str, passed: bool, **details) -> None:
        checks.append({"check": name, "passed": passed, **details})

    palettes: dict[str, set[str]] = {}
    for filename, expected in (("colorset1.yml", 17), ("colorset2.yaml", 37)):
        source = root / "design" / filename
        copied = bundle / "assets/palettes" / filename
        exists = source.is_file() and copied.is_file()
        if not exists:
            record(f"palette-copy:{filename}", False, error="Canonical source or bundled copy is missing")
            palettes[filename] = set()
            continue
        source_hash, copied_hash = sha256(source), sha256(copied)
        tokens = {value.lower() for value in VALUE.findall(copied.read_text(encoding="utf-8-sig"))}
        palettes[filename] = tokens
        record(f"palette-copy:{filename}", source_hash == copied_hash,
               canonical_sha256=source_hash, bundled_sha256=copied_hash)
        record(f"palette-token-count:{filename}", len(tokens) == expected,
               actual=len(tokens), expected=expected, tokens=sorted(tokens))

    if not entry.is_file() or not reference.is_file():
        record("design-documents", False, error="SKILL.md or usability-and-color.md is missing")
        entry_text = reference_text = ""
    else:
        entry_text = entry.read_text(encoding="utf-8-sig")
        reference_text = reference.read_text(encoding="utf-8-sig")
        record("design-documents", True, entry_sha256=sha256(entry), reference_sha256=sha256(reference))

    ids = HEURISTIC_ROW.findall(reference_text)
    counts = Counter(ids)
    expected_ids = {f"H{index}" for index in range(1, 11)}
    record("ten-unique-heuristic-rows", set(ids) == expected_ids and all(count == 1 for count in counts.values()),
           actual=ids, duplicates=sorted(key for key, count in counts.items() if count > 1))

    broken_links = []
    checked_links = 0
    for document, text in ((entry, entry_text), (reference, reference_text)):
        for target in LINK.findall(text):
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("//"):
                continue
            local = (document.parent / unquote(parsed.path)).resolve() if parsed.path else document
            checked_links += 1
            if not local.is_relative_to(bundle.resolve()) or not local.is_file():
                broken_links.append({"document": str(document.relative_to(root)), "target": target,
                                     "error": "Local link must resolve inside the skill bundle"})
            elif parsed.fragment and local.suffix.lower() == ".md":
                if unquote(parsed.fragment) not in anchors(local.read_text(encoding="utf-8-sig")):
                    broken_links.append({"document": str(document.relative_to(root)), "target": target,
                                         "error": "Markdown anchor is absent"})
    record("local-design-links", not broken_links, checked=checked_links, findings=broken_links)

    normalized = re.sub(r"\s+", " ", reference_text).lower()
    entry_normalized = re.sub(r"\s+", " ", entry_text).lower()
    required = {
        "entry-routes-to-design": "references/usability-and-color.md" in entry_text,
        "cs1-default": "default for each new deliverable" in normalized and "colorset1 by default" in entry_normalized,
        "cs2-explicit": "only when explicitly selected" in normalized and "only when explicitly selected" in entry_normalized,
        "runtime-palette-independence": "bundled copies, not repository or sibling files" in normalized,
        "native-theme-boundary": "never assume html/css or ansi truecolor" in normalized,
        "host-paint-boundary": "host owns paint" in normalized and "do not inject css or recolor consent controls" in normalized,
        "accessibility-override": "preserve the override" in normalized and "mandatory accessibility overrides take precedence" in normalized,
        "unrounded-contrast": "compare unrounded ratios" in normalized,
        "no-user-test-claim": "separate an inspection from a test with representative users" in normalized,
        "no-invented-failure": "never convert an unperformed check into `observed-failed`" in normalized,
    }
    for name, passed in required.items():
        record(name, passed)

    expected_sources = {
        "https://www.nngroup.com/articles/ten-usability-heuristics/",
        "https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/",
        "https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html",
        "https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html",
        "https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html",
    }
    missing_sources = sorted(expected_sources - set(LINK.findall(reference_text)))
    record("primary-design-links-present", not missing_sources, missing=missing_sources,
           scope="Exact link presence only; no network verification")

    role_findings = []
    role_count = 0
    for line in reference_text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3 or not HEX.search(line):
            continue
        role_count += 1
        for index, filename in ((1, "colorset1.yml"), (2, "colorset2.yaml")):
            for token in HEX.findall(cells[index]):
                if token.lower() not in palettes[filename]:
                    role_findings.append({"role": cells[0], "palette": filename, "token": token})
    record("role-table-exact-tokens", role_count >= 8 and not role_findings,
           checked_rows=role_count, findings=role_findings)

    pairs = [
        ("focus-trap", "#cfcfcf", "#ffffff", 3.0, False),
        ("required-border-trap", "#9c9c9c", "#ffffff", 3.0, False),
        ("ordinary-error-text-trap", "#e8002a", "#ffccd5", 4.5, False),
        ("body-on-white", "#333e48", "#ffffff", 4.5, True),
        ("helper-on-white", "#696969", "#ffffff", 4.5, True),
        ("primary-button-text", "#ffffff", "#9e1b32", 4.5, True),
        ("hover-button-text", "#ffffff", "#6d1222", 4.5, True),
        ("error-tint-ink-repair", "#333e48", "#ffccd5", 4.5, True),
        ("error-tint-red-repair", "#9e1b32", "#ffccd5", 4.5, True),
        ("cs2-blue-button-text", "#ffffff", "#007298", 4.5, True),
        ("cs2-green-button-text", "#ffffff", "#45842a", 4.5, True),
        ("cs1-focus-repair", "#9e1b32", "#ffffff", 3.0, True),
        ("cs2-focus-repair", "#007298", "#ffffff", 3.0, True),
    ]
    measured_pairs = []
    for name, foreground, background, threshold, expected_pass in pairs:
        ratio = contrast(foreground, background)
        reaches = ratio >= threshold
        measured_pairs.append({"pair": name, "foreground": foreground, "background": background,
                               "ratio": ratio, "threshold": threshold, "reaches_threshold": reaches,
                               "expected_reaches_threshold": expected_pass})
    record("computed-contrast-expectations",
           all(pair["reaches_threshold"] == pair["expected_reaches_threshold"] for pair in measured_pairs),
           pairs=measured_pairs,
           scope="Opaque sRGB authored color arithmetic; no host paint, compositing, or accessibility certification")

    report = {"passed": all(check["passed"] for check in checks), "check_count": len(checks),
              "host_ui_test_performed": False, "user_testing_performed": False, "checks": checks}
    output = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
