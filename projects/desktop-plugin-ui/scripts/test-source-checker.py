#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently test the citation checker without loading a model."""

from __future__ import annotations

import hashlib
import json
import runpy
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUNDLE_SOURCE = ROOT / "skills/desktop-plugin-ui"
ARTIFACTS = ROOT / "projects/desktop-plugin-ui/artifacts/source-checker-cross-assistant-tests"
ISOLATED_BUNDLE = ARTIFACTS / "bundle"
CHECKER = ISOLATED_BUNDLE / "scripts/check_sources.py"
BASE = "https://modelcontextprotocol.io/extensions/apps/overview"
ANCHOR = "https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html#downloadFile"
GITHUB = "https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md"
VERIFIED_EXTRA = "https://apps.extensions.modelcontextprotocol.io/api/documents/quickstart.html"
OPENAI_LEARN = "https://learn.chatgpt.com/docs/app-server"
VSCODE = "https://code.visualstudio.com/api/extension-guides/ai/mcp"
COPILOT = "https://docs.github.com/en/copilot/tutorials/create-an-extension"
CLAUDE_GITHUB = "https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts"
EXCALIDRAW = "https://github.com/excalidraw/excalidraw-mcp"
MICROSOFT_EXTRA = "https://learn.microsoft.com/en-us/visualstudio/extensibility/visual-studio-extensibility-overview"
NIELSEN = "https://www.nngroup.com/articles/ten-usability-heuristics/"
WCAG_CONTRAST = "https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html"
WCAG_NON_TEXT = "https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html"
WCAG_COLOR = "https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html"
PI_DOCS = "https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/extensions.md"
PI_RPC = "https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/rpc-extension-ui.md"
PI_PACKAGES = "https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/packages.md"
PI_COMMANDS = "https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/rpc-commands.md"
PI_TYPES = "https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/src/core/extensions/types.ts"
PI_RAW = "https://raw.githubusercontent.com/earendil-works/pi/v1.4.0/packages/coding-agent/docs/extensions.md"
PI_SPOOFED_HOST = PI_DOCS.replace("github.com", "github.com.attacker.invalid")
PI_SPOOFED_OWNER = PI_DOCS.replace("/earendil-works/", "/earendil-works-attacker/")
PI_SPOOFED_RAW = PI_RAW.replace("raw.githubusercontent.com", "raw.githubusercontent.com.attacker.invalid")
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
SCHEMA_EXTRA = "https://agent-plugins.org/schemas/verified-for-this-test.json"
SCHEMA_SPOOF = PLUGIN_SCHEMA.replace("agent-plugins.org", "agent-plugins.org.attacker.invalid")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    global ARTIFACTS, ISOLATED_BUNDLE, CHECKER
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="source-checker-poc-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f"))
    args = parser.parse_args()
    ARTIFACTS = ROOT / "projects/desktop-plugin-ui/artifacts" / args.run_id
    if not ARTIFACTS.resolve().is_relative_to(ROOT / "projects/desktop-plugin-ui/artifacts"):
        parser.error("The run ID must resolve inside the owning project's artifacts")
    if ARTIFACTS.exists():
        parser.error("Choose a fresh run ID; retained evidence is not overwritten")
    ISOLATED_BUNDLE = ARTIFACTS / "bundle"
    CHECKER = ISOLATED_BUNDLE / "scripts/check_sources.py"
    ARTIFACTS.mkdir(parents=True)
    # Snapshot only checker inputs so parallel authoring cannot look like a
    # checker mutation. The checker never reads the live repository catalog.
    for source in [BUNDLE_SOURCE / "scripts/check_sources.py", BUNDLE_SOURCE / "SKILL.md", *(BUNDLE_SOURCE / "references").glob("*.md")]:
        target = ISOLATED_BUNDLE / source.relative_to(BUNDLE_SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    checker_module = runpy.run_path(str(CHECKER))
    source_family = checker_module["source_family"]
    primary_family = checker_module["primary_family"]
    # Excalidraw is tested as an explicitly verified source until its new
    # canonical reference lands; neither branch allows arbitrary owner paths.
    excalidraw_bundled = EXCALIDRAW in checker_module["catalog"]()
    fixtures = {
        "correct.md": f"[Overview]({BASE}).\n`{ANCHOR}`,\n[{GITHUB}]({GITHUB});\n",
        "correct.json": json.dumps({"sources": [BASE, ANCHOR, GITHUB], "nested": {"url": BASE}}),
        "quoted-code.md": f"```python\nurl = '{BASE}'\n```\n```js\nconst link = \"{ANCHOR}\";\n```\n",
        "mutated-com.md": BASE.replace("modelcontextprotocol.io", "modelcontextprotocol.com"),
        "mutated-org.json": json.dumps({"url": BASE.replace("modelcontextprotocol.io", "modelcontextprotocol.org")}),
        "mutated-anchor.md": ANCHOR.replace("modelcontextprotocol.io", "modelcontextprotocol.org"),
        "github-primary.md": GITHUB,
        "github-unknown.md": "https://github.com/modelcontextprotocol/not-a-bundled-source",
        "extra.md": VERIFIED_EXTRA,
        "malformed.json": '{"sources": [}',
        "unrelated.md": "https://example.com/article and https://github.com/unrelated/project",
        "cross-assistant.md": "\n".join([OPENAI_LEARN, VSCODE, COPILOT, CLAUDE_GITHUB]),
        "cross-assistant.json": json.dumps({"sources": [OPENAI_LEARN, VSCODE, COPILOT, CLAUDE_GITHUB]}),
        "mutated-chatgpt.md": OPENAI_LEARN.replace("learn.chatgpt.com", "learn.chatgpt.org"),
        "mutated-vscode.md": VSCODE.replace("code.visualstudio.com", "code.visualstudio.org"),
        "mutated-copilot.md": COPILOT.replace("docs.github.com", "docs.github.org"),
        "spoofed-copilot.md": COPILOT.replace("docs.github.com", "docs.github.com.attacker.invalid"),
        "spoofed-openai.md": OPENAI_LEARN.replace("learn.chatgpt.com", "learn.chatgpt.com.attacker.invalid"),
        "credential-decorated.md": VSCODE.replace("code.visualstudio.com", "attacker@code.visualstudio.com"),
        "port-decorated.md": COPILOT.replace("docs.github.com", "docs.github.com:443"),
        "plain-http.md": OPENAI_LEARN.replace("https:", "http:"),
        "unknown-primary-path.md": "https://docs.github.com/en/copilot/not-a-bundled-page",
        "excalidraw.md": EXCALIDRAW,
        "mutated-excalidraw.md": EXCALIDRAW.replace("github.com", "github.org"),
        "mutated-raw-github.md": "https://raw.githubusercontent.org/excalidraw/excalidraw-mcp/main/README.md",
        "microsoft-extra.md": MICROSOFT_EXTRA,
        "mutated-microsoft.md": MICROSOFT_EXTRA.replace("learn.microsoft.com", "learn.microsoft.org"),
        "design-primary.md": "\n".join([NIELSEN, WCAG_CONTRAST, WCAG_NON_TEXT, WCAG_COLOR]),
        "design-primary.json": json.dumps({"sources": [NIELSEN, WCAG_CONTRAST, WCAG_NON_TEXT, WCAG_COLOR]}),
        "nielsen-unknown-path.md": "https://www.nngroup.com/articles/not-a-bundled-source/",
        "wcag-unknown-path.md": "https://www.w3.org/WAI/WCAG22/Understanding/not-a-bundled-source.html",
        "nielsen-alt-host.md": NIELSEN.replace("www.nngroup.com", "nngroup.com"),
        "wcag-alt-host.md": WCAG_CONTRAST.replace("www.w3.org", "w3.org"),
        "spoofed-nielsen.md": NIELSEN.replace("www.nngroup.com", "www.nngroup.com.attacker.invalid"),
        "spoofed-wcag.md": WCAG_CONTRAST.replace("www.w3.org", "www.w3.org.attacker.invalid"),
        "mutated-nielsen.md": NIELSEN.replace("www.nngroup.com", "www.nngroup.org"),
        "mutated-wcag.md": WCAG_CONTRAST.replace("www.w3.org", "www.w3.com"),
        "pi-primary.md": "\n".join([PI_DOCS, PI_RPC, PI_PACKAGES, PI_COMMANDS, PI_TYPES]),
        "pi-primary.json": json.dumps({"sources": [PI_DOCS, PI_RPC, PI_PACKAGES, PI_COMMANDS, PI_TYPES]}),
        "pi-unknown-path.md": "https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/not-a-bundled-page.md",
        "pi-unbundled-ref.md": PI_DOCS.replace("/v1.4.0/", "/unverified-ref/"),
        "pi-spoofed-host.md": PI_SPOOFED_HOST,
        "pi-spoofed-owner.md": PI_SPOOFED_OWNER,
        "pi-decorated-host.md": "https://docs.earendil-works.attacker.invalid/packages/coding-agent/docs/extensions.md",
        "pi-raw.md": PI_RAW,
        "pi-raw-unknown.md": PI_RAW.replace("extensions.md", "not-a-bundled-page.md"),
        "pi-raw-spoofed.md": PI_SPOOFED_RAW,
        "portable-primary.md": "\n".join([PLUGIN_SCHEMA, MCP_SCHEMA]),
        "portable-primary.json": json.dumps({"sources": [PLUGIN_SCHEMA, MCP_SCHEMA]}),
        "portable-unknown-path.md": SCHEMA_EXTRA,
        "portable-spoof.md": SCHEMA_SPOOF,
        "portable-credential.md": PLUGIN_SCHEMA.replace("agent-plugins.org", "attacker@agent-plugins.org"),
        "portable-http.md": PLUGIN_SCHEMA.replace("https:", "http:"),
        "json-quoted-command.json": json.dumps({"command": f'validate --schema "{PLUGIN_SCHEMA}"'}),
        "json-url-key.json": json.dumps({PLUGIN_SCHEMA: {"reference": MCP_SCHEMA}}),
        "json-escaped-slashes.json": json.dumps({"url": PLUGIN_SCHEMA}).replace("/", "\\/"),
        "json-escaped-spoof.json": json.dumps({"url": SCHEMA_SPOOF}).replace("/", "\\/"),
        "json-literal-backslash.json": json.dumps({"url": PLUGIN_SCHEMA + "\\"}),
        "json-duplicate-source-keys.json": '{"source":' + json.dumps(SCHEMA_SPOOF) + ',"source":' + json.dumps(PLUGIN_SCHEMA) + '}',
    }
    for name, body in fixtures.items():
        (ARTIFACTS / name).write_text(body, encoding="utf-8")
    (ARTIFACTS / "invalid-utf8.md").write_bytes(b"\xff")
    before = {str(p): digest(p) for p in ARTIFACTS.iterdir() if p.is_file() and p.name in {*fixtures, "invalid-utf8.md"}}
    catalog_before = {str(p): digest(p) for p in [CHECKER, ISOLATED_BUNDLE / "SKILL.md", *(ISOLATED_BUNDLE / "references").glob("*.md")]}
    cases = []

    def run(name: str, files: list[str], *, strict: bool = False, allowed: str | None = None,
            clean: bool = True, count: int | None = None, candidate: str | None = None,
            argument_error: str | None = None) -> None:
        command = [sys.executable, str(CHECKER), *(str(ARTIFACTS / f) for f in files)]
        if strict:
            command.append("--fail-on-findings")
        if allowed:
            command.extend(["--allow-url", allowed])
        result = subprocess.run(command, capture_output=True, text=True, timeout=20)
        try:
            decoded = json.loads(result.stdout)
        except ValueError:
            decoded = {}
        errors = []
        expected_exit = 2 if argument_error else 1 if strict and not clean else 0
        if result.returncode != expected_exit:
            errors.append(f"Expected exit {expected_exit}, found {result.returncode}")
        if not argument_error and decoded.get("passed") is not clean:
            errors.append(f"Expected passed={clean}")
        if argument_error and argument_error not in result.stderr:
            errors.append("Expected argument validation error was missing")
        if count is not None and decoded.get("checked_official_urls") != count:
            errors.append(f"Expected {count} official URLs")
        if candidate and not any(candidate in f.get("exact_candidates", []) for f in decoded.get("findings", [])):
            errors.append("Missing exact canonical candidate")
        cases.append({"name": name, "passed": not errors, "errors": errors, "command": command,
                      "exitCode": result.returncode, "output": decoded, "stderr": result.stderr})

    run("correct-markdown", ["correct.md"], strict=True, count=3)
    run("correct-json", ["correct.json"], strict=True, count=3)
    run("quoted-code-and-anchor", ["quoted-code.md"], strict=True, count=2)
    run("mutated-com-diagnostic", ["mutated-com.md"], clean=False, count=1, candidate=BASE)
    run("mutated-com-strict", ["mutated-com.md"], strict=True, clean=False, count=1, candidate=BASE)
    run("mutated-org-json", ["mutated-org.json"], strict=True, clean=False, count=1, candidate=BASE)
    run("mutated-anchor", ["mutated-anchor.md"], strict=True, clean=False, count=1, candidate=ANCHOR)
    run("github-primary", ["github-primary.md"], strict=True, count=1)
    run("github-unknown-primary", ["github-unknown.md"], strict=True, clean=False, count=1)
    run("verified-extra-rejected-without-allow", ["extra.md"], strict=True, clean=False, count=1)
    run("verified-extra-allowed", ["extra.md"], strict=True, allowed=VERIFIED_EXTRA, count=1)
    run("malformed-json-diagnostic", ["malformed.json"], clean=False, count=0)
    run("malformed-json-strict", ["malformed.json"], strict=True, clean=False, count=0)
    run("missing-path-diagnostic", ["missing-report.json"], clean=False, count=0)
    run("missing-path-strict", ["missing-report.json"], strict=True, clean=False, count=0)
    run("invalid-utf8", ["invalid-utf8.md"], strict=True, clean=False, count=0)
    run("unrelated-sources-ignored", ["unrelated.md"], strict=True, count=0)
    run("cross-assistant-markdown", ["cross-assistant.md"], strict=True, count=4)
    run("cross-assistant-json", ["cross-assistant.json"], strict=True, count=4)
    run("mutated-chatgpt-source", ["mutated-chatgpt.md"], strict=True, clean=False, count=1, candidate=OPENAI_LEARN)
    run("mutated-vscode-source", ["mutated-vscode.md"], strict=True, clean=False, count=1, candidate=VSCODE)
    run("mutated-copilot-source", ["mutated-copilot.md"], strict=True, clean=False, count=1, candidate=COPILOT)
    run("spoofed-copilot-host", ["spoofed-copilot.md"], strict=True, clean=False, count=1, candidate=COPILOT)
    run("spoofed-openai-host", ["spoofed-openai.md"], strict=True, clean=False, count=1, candidate=OPENAI_LEARN)
    run("credential-decorated-official-host", ["credential-decorated.md"], strict=True, clean=False, count=1, candidate=VSCODE)
    run("port-decorated-official-host", ["port-decorated.md"], strict=True, clean=False, count=1, candidate=COPILOT)
    run("plain-http-official-host", ["plain-http.md"], strict=True, clean=False, count=1, candidate=OPENAI_LEARN)
    run("unknown-path-on-primary-host", ["unknown-primary-path.md"], strict=True, clean=False, count=1)
    run("exact-excalidraw-source", ["excalidraw.md"], strict=True, count=1, allowed=None if excalidraw_bundled else EXCALIDRAW)
    run("mutated-excalidraw-source", ["mutated-excalidraw.md"], strict=True, clean=False, count=1, candidate=EXCALIDRAW if excalidraw_bundled else None)
    run("mutated-raw-github-source", ["mutated-raw-github.md"], strict=True, clean=False, count=1)
    run("microsoft-needs-exact-allow", ["microsoft-extra.md"], strict=True, clean=False, count=1)
    run("microsoft-exact-allow", ["microsoft-extra.md"], strict=True, allowed=MICROSOFT_EXTRA, count=1)
    run("mutated-microsoft-source", ["mutated-microsoft.md"], strict=True, clean=False, count=1)
    run("spoofed-host-cannot-be-allowed", ["spoofed-openai.md"], allowed=OPENAI_LEARN.replace("learn.chatgpt.com", "learn.chatgpt.com.attacker.invalid"), argument_error="recognized exact primary host")
    run("unrelated-github-owner-cannot-be-allowed", ["unrelated.md"], allowed="https://github.com/unrelated/project", argument_error="recognized exact primary host")
    run("design-exact-catalog-markdown", ["design-primary.md"], strict=True, count=4)
    run("design-exact-catalog-json", ["design-primary.json"], strict=True, count=4)
    run("nielsen-unknown-path-rejected", ["nielsen-unknown-path.md"], strict=True, clean=False, count=1)
    run("wcag-unknown-path-rejected", ["wcag-unknown-path.md"], strict=True, clean=False, count=1)
    run("nielsen-alt-host-still-needs-exact-catalog", ["nielsen-alt-host.md"], strict=True, clean=False, count=1, candidate=NIELSEN)
    run("wcag-alt-host-still-needs-exact-catalog", ["wcag-alt-host.md"], strict=True, clean=False, count=1, candidate=WCAG_CONTRAST)
    run("nielsen-alt-host-exact-allow", ["nielsen-alt-host.md"], strict=True, allowed=NIELSEN.replace("www.nngroup.com", "nngroup.com"), count=1)
    run("wcag-alt-host-exact-allow", ["wcag-alt-host.md"], strict=True, allowed=WCAG_CONTRAST.replace("www.w3.org", "w3.org"), count=1)
    run("spoofed-nielsen-host", ["spoofed-nielsen.md"], strict=True, clean=False, count=1, candidate=NIELSEN)
    run("spoofed-wcag-host", ["spoofed-wcag.md"], strict=True, clean=False, count=1, candidate=WCAG_CONTRAST)
    run("mutated-nielsen-host", ["mutated-nielsen.md"], strict=True, clean=False, count=1, candidate=NIELSEN)
    run("mutated-wcag-host", ["mutated-wcag.md"], strict=True, clean=False, count=1, candidate=WCAG_CONTRAST)
    run("spoofed-nielsen-cannot-be-allowed", ["spoofed-nielsen.md"], allowed=NIELSEN.replace("www.nngroup.com", "www.nngroup.com.attacker.invalid"), argument_error="recognized exact primary host")
    run("spoofed-wcag-cannot-be-allowed", ["spoofed-wcag.md"], allowed=WCAG_CONTRAST.replace("www.w3.org", "www.w3.org.attacker.invalid"), argument_error="recognized exact primary host")
    run("pi-exact-pinned-catalog-markdown", ["pi-primary.md"], strict=True, count=5)
    run("pi-exact-pinned-catalog-json", ["pi-primary.json"], strict=True, count=5)
    run("pi-unknown-path-rejected", ["pi-unknown-path.md"], strict=True, clean=False, count=1)
    run("pi-unbundled-ref-rejected", ["pi-unbundled-ref.md"], strict=True, clean=False, count=1)
    run("pi-spoofed-host-rejected", ["pi-spoofed-host.md"], strict=True, clean=False, count=1, candidate=PI_DOCS)
    run("pi-spoofed-owner-rejected", ["pi-spoofed-owner.md"], strict=True, clean=False, count=1)
    run("pi-decorated-owner-host-rejected", ["pi-decorated-host.md"], strict=True, clean=False, count=1)
    run("pi-spoofed-host-cannot-be-allowed", ["pi-spoofed-host.md"], allowed=PI_SPOOFED_HOST, argument_error="recognized exact primary host")
    run("pi-spoofed-owner-cannot-be-allowed", ["pi-spoofed-owner.md"], allowed=PI_SPOOFED_OWNER, argument_error="recognized exact primary host")
    run("pi-raw-needs-exact-allow", ["pi-raw.md"], strict=True, clean=False, count=1)
    run("pi-raw-exact-allow", ["pi-raw.md"], strict=True, allowed=PI_RAW, count=1)
    run("pi-raw-unknown-path-rejected", ["pi-raw-unknown.md"], strict=True, clean=False, count=1)
    run("pi-raw-spoofed-host-rejected", ["pi-raw-spoofed.md"], strict=True, clean=False, count=1)
    run("pi-raw-spoofed-cannot-be-allowed", ["pi-raw-spoofed.md"], allowed=PI_SPOOFED_RAW, argument_error="recognized exact primary host")
    run("portable-exact-schemas-markdown", ["portable-primary.md"], strict=True, count=2)
    run("portable-exact-schemas-json", ["portable-primary.json"], strict=True, count=2)
    run("portable-unknown-path-rejected", ["portable-unknown-path.md"], strict=True, clean=False, count=1)
    run("portable-exact-verified-allowance", ["portable-unknown-path.md"], strict=True, allowed=SCHEMA_EXTRA, count=1)
    run("portable-spoof-rejected", ["portable-spoof.md"], strict=True, clean=False, count=1, candidate=PLUGIN_SCHEMA)
    run("portable-spoof-cannot-be-allowed", ["portable-spoof.md"], allowed=SCHEMA_SPOOF, argument_error="recognized exact primary host")
    run("portable-credential-rejected", ["portable-credential.md"], strict=True, clean=False, count=1, candidate=PLUGIN_SCHEMA)
    run("portable-http-rejected", ["portable-http.md"], strict=True, clean=False, count=1, candidate=PLUGIN_SCHEMA)
    run("json-command-quotes-are-not-url-characters", ["json-quoted-command.json"], strict=True, count=1)
    run("json-url-keys-and-values", ["json-url-key.json"], strict=True, count=2)
    run("json-escaped-slashes-decode-to-canonical-url", ["json-escaped-slashes.json"], strict=True, count=1)
    run("json-escaped-spoof-still-rejected", ["json-escaped-spoof.json"], strict=True, clean=False, count=1, candidate=PLUGIN_SCHEMA)
    run("json-literal-backslash-still-rejected", ["json-literal-backslash.json"], strict=True, clean=False, count=1)
    run("json-duplicate-key-does-not-hide-spoof", ["json-duplicate-source-keys.json"], strict=True, clean=False, count=2, candidate=PLUGIN_SCHEMA)
    family_cases = [
        (OPENAI_LEARN, "openai"), (VSCODE, "vscode"), (COPILOT, "github"),
        (CLAUDE_GITHUB, "anthropic"), (EXCALIDRAW, "excalidraw"),
        (MICROSOFT_EXTRA, "microsoft"),
        ("https://github.com/microsoft/vscode", "microsoft"),
        ("https://raw.githubusercontent.com/excalidraw/excalidraw-mcp/main/README.md", "excalidraw"),
        (NIELSEN, "nngroup"), ("https://nngroup.com/articles/ten-usability-heuristics/", "nngroup"),
        (WCAG_CONTRAST, "w3c"), ("https://w3.org/WAI/WCAG22/Understanding/contrast-minimum.html", "w3c"),
        (PI_DOCS, "pi"), (PI_RAW, "pi"),
        (PLUGIN_SCHEMA, "agent-plugins"), (MCP_SCHEMA, "agent-plugins"),
    ]
    ownership_errors = [url for url, expected in family_cases if primary_family(url) != expected]
    misleading = ["https://myopenai-news.com/page", "https://code.visualstudio.com.attacker.invalid/api", "https://learn.microsoft.org/en-us/", "https://attacker@learn.chatgpt.com/docs/app-server", "https://github.com/excalidraw-unrelated/project", "https://github.com/unrelated/project", "http://docs.github.com/en/copilot", "https://docs.github.com:443/en/copilot"]
    ownership_errors.extend(url for url in misleading if primary_family(url) is not None)
    design_misleading = ["https://www.nngroup.com.attacker.invalid/articles/", "https://www.w3.org.attacker.invalid/WAI/", "https://docs.nngroup.com/articles/", "https://docs.w3.org/WAI/", "https://attacker@www.nngroup.com/articles/", "https://www.w3.org:443/WAI/", "http://www.nngroup.com/articles/", "https://github.com/nngroup/unverified", "https://github.com/w3/unverified"]
    ownership_errors.extend(url for url in design_misleading if primary_family(url) is not None)
    pi_misleading = [PI_SPOOFED_HOST, PI_SPOOFED_OWNER, PI_SPOOFED_RAW,
                     PI_DOCS.replace("github.com", "attacker@github.com"),
                     PI_DOCS.replace("github.com", "github.com:443"),
                     PI_RAW.replace("/earendil-works/", "/earendil-works.attacker/"),
                     "https://earendil-works.dev/unverified", "https://pi.dev/unverified"]
    ownership_errors.extend(url for url in pi_misleading if primary_family(url) is not None)
    ownership_errors.extend(url for url in [SCHEMA_SPOOF, PLUGIN_SCHEMA.replace("agent-plugins.org", "attacker@agent-plugins.org"),
                                          PLUGIN_SCHEMA.replace("https:", "http:")] if primary_family(url) is not None)
    cases.append({"name": "exact-primary-ownership-classification", "passed": not ownership_errors, "errors": ownership_errors, "checked": len(family_cases) + len(misleading) + len(design_misleading) + len(pi_misleading)})
    suspicious = [OPENAI_LEARN.replace("learn.chatgpt.com", "learn.chatgpt.com.attacker.invalid"), VSCODE.replace("code.visualstudio.com", "code.visualstudio.org"), EXCALIDRAW.replace("github.com", "github.org")]
    suspicious_errors = [url for url in suspicious if primary_family(url) or not source_family(url)]
    design_suspicious = [NIELSEN.replace("www.nngroup.com", "www.nngroup.com.attacker.invalid"), WCAG_CONTRAST.replace("www.w3.org", "www.w3.org.attacker.invalid"), NIELSEN.replace("www.nngroup.com", "www.nngroup.org"), WCAG_CONTRAST.replace("www.w3.org", "www.w3.com")]
    suspicious_errors.extend(url for url in design_suspicious if primary_family(url) or not source_family(url))
    pi_suspicious = [PI_SPOOFED_HOST, PI_SPOOFED_OWNER, PI_SPOOFED_RAW,
                     "https://docs.earendil-works.attacker.invalid/packages/coding-agent/docs/extensions.md"]
    suspicious_errors.extend(url for url in pi_suspicious if primary_family(url) or source_family(url) != "pi")
    suspicious_errors.extend(url for url in [SCHEMA_SPOOF, PLUGIN_SCHEMA.replace("agent-plugins.org", "agent-plugins.com")]
                             if primary_family(url) or source_family(url) != "agent-plugins")
    cases.append({"name": "lookalikes-are-inspected-never-trusted", "passed": not suspicious_errors, "errors": suspicious_errors})
    after = {path: digest(Path(path)) for path in before}
    catalog_after = {path: digest(Path(path)) for path in catalog_before}
    cases.append({"name": "no-report-or-catalog-mutation", "passed": before == after and catalog_before == catalog_after,
                  "reportSha256": before, "catalogSha256": catalog_before})
    report = {"passed": all(c["passed"] for c in cases), "passedCount": sum(c["passed"] for c in cases),
              "caseCount": len(cases), "checkerSha256": digest(CHECKER), "cases": cases}
    (ARTIFACTS / "result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))
    for case in cases:
        if not case["passed"]:
            print(json.dumps(case, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
