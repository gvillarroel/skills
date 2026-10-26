#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check official citation URLs in advisory Markdown/JSON against bundled sources."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

BUNDLE = Path(__file__).resolve().parents[1]
URL = re.compile(r"https?://[^\s<>\"'`\[\]]+")
# Exact hosts identify source ownership; they do not approve arbitrary paths.
# A citation must still equal an entry in the bundle or an explicit --allow-url.
PRIMARY_HOSTS = {
    "agent-plugins.org": "agent-plugins",
    "modelcontextprotocol.io": "modelcontextprotocol",
    "apps.extensions.modelcontextprotocol.io": "modelcontextprotocol",
    "claude.com": "claude",
    "code.claude.com": "claude",
    "support.claude.com": "claude",
    "anthropic.com": "anthropic",
    "www.anthropic.com": "anthropic",
    "docs.anthropic.com": "anthropic",
    "openai.com": "openai",
    "www.openai.com": "openai",
    "developers.openai.com": "openai",
    "platform.openai.com": "openai",
    "help.openai.com": "openai",
    "learn.chatgpt.com": "openai",
    "docs.github.com": "github",
    "github.blog": "github",
    "code.visualstudio.com": "vscode",
    "learn.microsoft.com": "microsoft",
    "support.microsoft.com": "microsoft",
    "www.microsoft.com": "microsoft",
    "excalidraw.com": "excalidraw",
    "docs.excalidraw.com": "excalidraw",
    "mcp.excalidraw.com": "excalidraw",
    "nngroup.com": "nngroup",
    "www.nngroup.com": "nngroup",
    "w3.org": "w3c",
    "www.w3.org": "w3c",
}
GITHUB_OWNERS = {
    "modelcontextprotocol": "modelcontextprotocol",
    "anthropics": "anthropic",
    "openai": "openai",
    "github": "github",
    "microsoft": "microsoft",
    "excalidraw": "excalidraw",
    "earendil-works": "pi",
}
CLAIMED_HOST_LABELS = {
    "modelcontextprotocol": "modelcontextprotocol",
    "claude": "claude",
    "anthropic": "anthropic",
    "openai": "openai",
    "chatgpt": "openai",
    "github": "github",
    "githubusercontent": "github",
    "visualstudio": "vscode",
    "microsoft": "microsoft",
    "excalidraw": "excalidraw",
    "nngroup": "nngroup",
    "w3": "w3c",
    # The URL-label tokenizer splits the distinctive owner name at its hyphen.
    "earendil": "pi",
}


def extract_urls(text: str) -> set[str]:
    return {url.rstrip(".,;:)]") for url in URL.findall(text)}


def extract_json_urls(text: str) -> set[str]:
    """Inspect decoded strings, retaining duplicate-key values for source checks."""
    pending = [json.loads(text.removeprefix("\ufeff"), object_pairs_hook=list)]
    urls: set[str] = set()
    while pending:
        value = pending.pop()
        if isinstance(value, str):
            urls.update(extract_urls(value))
        elif isinstance(value, (list, tuple)):
            pending.extend(value)
    return urls


def primary_family(url: str) -> str | None:
    """Recognize primary ownership without trusting lookalike or decorated hosts."""
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port is not None:
            return None
        hostname = (parsed.hostname or "").lower()
        if hostname in {"github.com", "raw.githubusercontent.com"}:
            owner = parsed.path.strip("/").split("/")[0].lower()
            return GITHUB_OWNERS.get(owner)
        return PRIMARY_HOSTS.get(hostname)
    except ValueError:
        return None


def source_family(url: str) -> str | None:
    """Classify sources to inspect, including suspicious claims, never to allow."""
    if family := primary_family(url):
        return family
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    if (parsed.hostname or "").lower() in {"github.com", "raw.githubusercontent.com"}:
        owner = parsed.path.strip("/").split("/")[0].lower()
        if family := GITHUB_OWNERS.get(owner):
            return family
        # Decorated owner names claim an existing source family but cannot
        # establish primary ownership or become explicitly allowed sources.
        return next((family for known, family in GITHUB_OWNERS.items()
                     if owner.startswith((known + "-", known + "."))), None)
    labels = re.split(r"[^a-z0-9]+", parsed.netloc.lower())
    # Inspect this distinctive two-token standard name without trusting a
    # lookalike or treating generic "agent" / "plugins" labels as ownership.
    if any(labels[index:index + 2] == ["agent", "plugins"] for index in range(len(labels) - 1)):
        return "agent-plugins"
    if "github" in labels or "githubusercontent" in labels:
        owner = parsed.path.strip("/").split("/")[0].lower()
        if family := GITHUB_OWNERS.get(owner):
            return family
    return next((CLAIMED_HOST_LABELS[label] for label in labels if label in CLAIMED_HOST_LABELS), None)


def catalog() -> set[str]:
    paths = [BUNDLE / "SKILL.md", *(BUNDLE / "references").glob("*.md")]
    return {url for path in paths for url in extract_urls(path.read_text(encoding="utf-8")) if primary_family(url)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", type=Path, nargs="*", help="Generated Markdown or JSON reports to inspect; files are never changed.")
    parser.add_argument("--list-sources", action="store_true", help="Print the exact bundled primary-source URLs.")
    parser.add_argument("--fail-on-findings", action="store_true", help="Exit 1 on findings for CI; default prints diagnostic JSON and exits 0.")
    parser.add_argument("--allow-url", action="append", default=[], help="An additional primary URL independently fetched and verified for this task.")
    args = parser.parse_args()
    for url in args.allow_url:
        if not primary_family(url):
            parser.error("--allow-url must be an HTTPS URL on a recognized exact primary host or GitHub owner")
    allowed = catalog() | set(args.allow_url)
    if args.list_sources:
        print(json.dumps({"sources": sorted(allowed)}, indent=2))
        if not args.reports:
            return 0
    if not args.reports:
        parser.error("Provide a report path or --list-sources")
    findings = []
    checked = 0
    for report in args.reports:
        if not report.is_file():
            findings.append({"path": str(report), "error": "Report does not exist"})
            continue
        try:
            text = report.read_text(encoding="utf-8")
            urls = extract_json_urls(text) if report.suffix.lower() == ".json" else extract_urls(text)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            findings.append({"path": str(report), "error": str(error)})
            continue
        for url in sorted(urls):
            if not source_family(url):
                continue
            checked += 1
            if url in allowed:
                continue
            parsed = urlsplit(url)
            matches = sorted(candidate for candidate in allowed
                             if source_family(candidate) == source_family(url)
                             and (urlsplit(candidate).path, urlsplit(candidate).query, urlsplit(candidate).fragment)
                             == (parsed.path, parsed.query, parsed.fragment))
            findings.append({"path": str(report), "url": url,
                             "error": "URL was not copied exactly from a bundled or explicitly verified source",
                             "exact_candidates": matches})
    print(json.dumps({"passed": not findings, "checked_official_urls": checked, "findings": findings}, indent=2))
    return 1 if findings and args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
