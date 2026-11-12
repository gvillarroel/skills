#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inspect isolated advisory artifacts; semantic review remains a separate gate."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL = re.compile(r"https://[^\s<>\"`'\[\]()]+")


def urls(text: str) -> set[str]:
    return {url.rstrip(".,;:)]") for url in URL.findall(text)}


def inspect(run: Path) -> dict:
    manifest = json.loads((run / "run-manifest.json").read_text(encoding="utf-8"))
    result = json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))
    workspace = run / "workspace"
    bundle = workspace / "skills/desktop-plugin-ui"
    source = "\n".join(p.read_text(encoding="utf-8") for p in bundle.rglob("*.md"))
    canonical = set(re.findall(r"^## (claude-ui-[a-z0-9-]+)$", source, re.M))
    allowed_urls = urls(source)
    findings = []
    output_ids = set()
    cited_urls = set()
    for relative in manifest["expectedOutputs"]:
        artifact = workspace / relative
        if not artifact.is_file():
            findings.append(f"{relative}: expected artifact missing")
            continue
        text = artifact.read_text(encoding="utf-8")
        cited_urls.update(urls(text))
        if artifact.suffix == ".json":
            data = json.loads(text)
            if data.get("host_acceptance_verified") is not False:
                findings.append(f"{relative}: host acceptance must remain false")
            patterns = data.get("patterns", [])
            for pattern in patterns:
                value = pattern if isinstance(pattern, str) else pattern.get("id")
                if value not in canonical:
                    findings.append(f"{relative}: unknown pattern {value!r}")
                output_ids.add(value)
            if "contract" in run.name:
                if len(output_ids) < 10:
                    findings.append("Contract must select at least ten canonical patterns")
                for pattern in patterns:
                    if not isinstance(pattern, dict) or not all(pattern.get(k) for k in ("id", "rule", "validation", "evidence")):
                        findings.append("Contract pattern lacks a required decision field")
            if "boundary" in run.name and data.get("product_confirmed") is not False:
                findings.append("Boundary must preserve product uncertainty")
    official = {url for url in cited_urls if any(name in url for name in ("claude", "anthropic", "modelcontextprotocol", "openai"))}
    unknown_urls = sorted(official - allowed_urls)
    if unknown_urls:
        findings.append("Primary-source URLs absent from copied bundle: " + ", ".join(unknown_urls))
    return {
        "run": run.name,
        "payloadSha256": manifest["skill"]["payloadSha256"],
        "fileCount": manifest["skill"]["fileCount"],
        "model": manifest["pi"]["model"],
        "strictPassed": result["passed"],
        "structuralEvidencePassed": not findings,
        "canonicalPatternCount": len(canonical),
        "selectedPatternCount": len(output_ids),
        "exactOfficialSourceCount": len(official & allowed_urls),
        "findings": findings,
        "semanticReviewRequired": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runs = sorted((ROOT / "evaluations/runs").glob(args.prefix + "*"))
    reports = [inspect(run) for run in runs if (run / "run-manifest.json").is_file() and (run / "evaluation-result.json").is_file()]
    payloads = sorted({row["payloadSha256"] for row in reports})
    report = {"runs": reports, "completedCount": len(reports), "payloads": payloads, "singleFrozenPayload": len(payloads) == 1}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"completed": len(reports), "strictPasses": sum(r["strictPassed"] for r in reports), "structuralEvidencePasses": sum(r["structuralEvidencePassed"] for r in reports), "payloads": payloads, "output": str(args.output)}))
    return 0 if reports and all(r["strictPassed"] and r["structuralEvidencePassed"] for r in reports) and len(payloads) == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
