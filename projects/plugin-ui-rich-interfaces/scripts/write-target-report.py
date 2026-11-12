#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize retained live-host captures without promoting fixtures to product acceptance."""
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
REVIEWS = ROOT / "artifacts/reviews"
TARGET = REVIEWS / "target-hosts"
DESTINATION = REPO / "evaluations/desktop-plugin-ui/target-hosts-20261112"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    reports = {
        "pi": load(TARGET / "pi-final-1/review.json"),
        "codex": load(REVIEWS / "codex/portable-target-final/review.json"),
        "browser": load(REVIEWS / "browser/review.json"),
        "previews": load(REVIEWS / "previews/review.json"),
        "inAppBrowser": load(TARGET / "in-app-browser/review.json"),
        "claudeXY": load(TARGET / "claude-desktop-live-xy/review.json"),
        "contracts": load(TARGET / "contracts/review.json"),
        "geminiDiscovery": load(TARGET / "gemini-discovery/review.json"),
        "geminiSchema": load(ROOT / "artifacts/data/a2ui-catalog-target-host-final.json"),
    }
    reports["geminiDiscovery"].pop("project", None)
    reports["geminiDiscovery"]["projectScope"] = "Configured default project; exact identity stays in ignored local evidence."
    sources = ["web/app.js", "web/styles.css", "pi/observatory.ts", "host-tests/capture.mjs", "host-tests/terminal.html", "scripts/verify-codex.py"]
    source_hashes = {name: digest(ROOT / name) for name in sources}
    pictures = []
    for file in sorted(TARGET.rglob("*")):
        if file.suffix.lower() in {".png", ".jpg"}:
            pictures.append({"path": file.relative_to(REPO).as_posix(), "bytes": file.stat().st_size, "sha256": digest(file)})
    selected = {
        "Claude Desktop fresh XY plot": TARGET / "claude-desktop-live-xy/fullscreen.png",
        "Actual 542px in-app panel before repair": TARGET / "in-app-browser/before-542.jpg",
        "Actual in-app selection after repair": TARGET / "in-app-browser/after-selection-542.jpg",
        "Actual in-app linked chart and inspector": TARGET / "in-app-browser/metrics-orders-readable-542.jpg",
        "Actual in-app exact values": TARGET / "in-app-browser/exact-values-542.jpg",
        "Pi short terminal before paging": TARGET / "pi-short-baseline-1/values-60x16-page-1.png",
        "Pi short terminal corrected page two": TARGET / "pi-final-1/values-60x16-page-2.png",
        "Pi short terminal corrected final page": TARGET / "pi-final-1/values-60x16-page-3.png",
        "Claude Code CLI login gate": TARGET / "claude-after-theme-1/after-theme.png",
        "Claude Desktop Code onboarding gate": TARGET / "claude-desktop-code/onboarding-gate.png",
    }
    for file in selected.values():
        if not file.is_file() or file.stat().st_size < 1000:
            raise ValueError(f"Missing actual capture: {file}")
    data = {
        "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "Additional target-host observations, fixes and focused contracts; previous 91-run frozen cohorts remain separate.",
        "sourceHashes": source_hashes,
        "reports": reports,
        "screenshots": pictures,
        "packages": load(ROOT / "artifacts/packages/package-manifest.json"),
        "unperformed": ["New Service Observatory installation and paint in Claude Desktop Chat", "Authenticated native Claude Code pane paint", "New Service Observatory stock MCP App frontend paint in Codex/ChatGPT Desktop", "Gemini Enterprise hosted A2A transport, administrator registration and host painting"],
        "configurationBoundary": "All authored files and task-local installs remain in this repository. Personal Claude configuration authorization and Gemini app URL are pending.",
        "additionalObservedGates": {"claudeCliAuthStatus": {"loggedIn": False, "authMethod": "none"}, "desktopCode": "Get Claude Code onboarding gateway", "excalidrawReference": "Fresh read_me call returned MCP -32001 Unknown tool; connector availability, not an unsupported renderer result."},
    }
    DESTINATION.with_suffix(".json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    count = lambda name: sum(row["passed"] for row in reports[name]["checks"])
    lines = [
        "# Target-host UI verification", "", "Date: November 12, 2026.", "",
        "This follow-up tests actual available application/terminal surfaces, retains screenshots and fixes observed defects. It does not certify all six requested hosts. Prior frozen naturalistic cohorts and their failures remain in [the earlier report](rich-interfaces-20261112.md).", "",
        "## Observed surfaces", "",
        "| Target | Executed evidence | Remaining boundary |", "| --- | --- | --- |",
        "| Claude Desktop Chat 5.1231.2 | A fresh installed Reflex XY call rendered the supplied 24-hour Payments line plus objective; native fullscreen and inline were observed. One user prompt used Haiku 5.5 Medium on the signed-in Free account. | This installed connector is distinct from the new Service Observatory MCP package. The latter's personal configuration change is awaiting authorization. |",
        "| Claude Code CLI 2.1.302 | The real ConPTY process painted theme setup, then login selection. A separate sanitized current-profile auth status reported loggedIn=false. | Native pane painting requires authenticated access; engine acceptance is retained separately. |",
        "| Claude Desktop Code | The actual Code tab showed the Get Claude Code onboarding gateway. | No Mod pane was mounted; the gateway is not a renderer rejection. |",
        f"| Pi 1.4.0 | {count('pi')}/10 real-process TUI checks pass: directed relationships, metrics, 24 values, 60x16 pages, N/P, resize, selection, close/reopen and normal exit. | xterm.js renders real Windows ConPTY output; this does not certify a stock Windows Terminal or arbitrary RPC client. |",
        f"| Codex core 0.167.0-alpha.3.2 | {count('codex')}/10 checks pass through local marketplace addition, actual package installation, exact cache bytes, app-server discovery and the direct tool. No model turn starts. | This is the installed core with a task-local home, not a stock frontend component screenshot. No direct MCP configuration fallback was used. |",
        "| ChatGPT desktop 26.1103.7773.0, Codex mode | Service Observatory was exercised in its real in-app browser at 542x767 CSS px. Actual XY component controls and image paint were also inspected; a native app capture is retained. | The browser is an explicit alternative. The new MCP package's inline/frontend installation and a separate ChatGPT Chat surface remain untested. |",
        "| Gemini Enterprise | Both updated payload streams pass official envelope/catalog and bound Vega-Lite schemas. Read-only engine discovery in only the configured default project/global/default_collection returned HTTP 403, SERVICE_DISABLED. | An existing Enterprise app URL, reachable hosted agent and registration are still needed. This does not rule out an app in another project or location. |",
        "| Excalidraw reference connector | A fresh advertised read_me call returned Unknown tool (-32001). | No successful renderer call or screenshot is claimed; the connector needs to become callable. |", "",
        "## Observed defects and repairs", "",
        "1. The actual 542px panel allocated only 459px to an 840-unit SVG. Labels became too small despite earlier 320px/desktop checks. The web panel now queries its allocated inline size and uses a selected neighborhood with explicit scope/full-list access when the map is too dense. Wide primary map labels are enlarged and measured at at least 12 rendered CSS px. Intermediate 542/768/1024 widths are included in regression checks.",
        "2. Selecting a recreated compact-list button dropped focus to the document. The component restores scoped focus to the corresponding replacement; a disappearing relationship moves focus to the updated inspector heading. Actual IAB Enter selection retained focus on Orders, with 142 ms preserved in its chart and 24-row table. The empty-filter state retained selection and offered recovery.",
        "3. A real 60x16 Pi view hid exact records behind a hint that reopened the same truncated content. It now reserves context/navigation rows and pages actual content. N/P works in the tested ConPTY input path; the injected PageUp/PageDown sequences had no effect and that bounded failure is retained. All 24 observations remain reachable across the three pages, including the 23:00 value of 268 ms.", "",
        "The Pi source and its skill guidance promote the height/access rule. The comparison and Codex skills promote allocated-width measurements, container-query alternatives, focus restoration and unoccluded/current-resource captures. The Claude Chat host reference records the additional bounded live observation.", "",
        "## Captures", "",
        "Original PNG/JPEG bytes, terminal output, events and accessibility trees remain ignored under project artifacts. Captures can contain private application chrome; they are not copied into public Pages or runtime skill payloads. The machine-readable companion retains screenshot hashes and current source hashes.", "",
    ]
    for label, file in selected.items():
        lines.append(f"- [{label}](../../{file.relative_to(REPO).as_posix()})")
    lines += ["", "## Validation", "",
        f"Current MCP/browser fixture: {count('browser')}/{len(reports['browser']['checks'])}; previews: {count('previews')}/12. Real RPC/print and geometry checks remain 29/29. The current Pi actual-process capture is 10/10. Official Gemini schema checks pass. These layers supplement actual host screenshots and keep their boundaries explicit.", "",
        "Four focused isolated executions were retained. The first Pi contract failed strict equality because the prompt asked for a descriptive mode while the grader required the literal tui string; its artifact remains correct. The clarified second contract passes all strict gates. Current Codex and comparison-router allocated-panel contracts also pass strict gates and independent artifact review. These are one-pass instruction contracts, not replacement three-repetition naturalistic cohorts. Model: openai-codex/gpt-6.1-sol, medium thinking, under the previously recorded Spark account exception.", "",
        "The first compact-focus browser assertion selected the first row containing Orders, which became Public API after selection because its relationship text mentions Orders. The evaluator now inspects actual focused scope/text and selected identity; the source artifact was unchanged for that evaluator repair. Capturing immediately after a reload also observed the previous resource; the final host check waited for the corrected focus marker after a cache-bypassing reload. Native app capture initially included an occluding window; foregrounding the authorized target corrected it. None is recorded as a product renderer failure.", "",
        "The first two completed Pi capture drivers retained a node-pty Windows worker handle after the target itself exited normally. Those owned drivers were stopped; the final capture closes browser/socket/process resources and exits its Windows driver explicitly. The target exit receipt remains separate from recorder cleanup.", "",
        "```powershell",
        "node projects/plugin-ui-rich-interfaces/host-tests/capture.mjs --host pi --label <fresh-id>",
        "node projects/plugin-ui-rich-interfaces/scripts/verify-browser.mjs",
        "node projects/plugin-ui-rich-interfaces/scripts/verify-pi.mjs",
        "node projects/plugin-ui-rich-interfaces/scripts/review-host-contracts.mjs",
        'uv run --script projects/plugin-ui-rich-interfaces/scripts/verify-codex.py --codex "<installed-core>" --packaged --label <fresh-id>',
        "uv run --script projects/plugin-ui-rich-interfaces/scripts/validate-a2ui.py <native-stream> <canvas-stream> --label <fresh-id>",
        "uv run --script projects/plugin-ui-rich-interfaces/scripts/package.py",
        "uv run --script projects/plugin-ui-rich-interfaces/scripts/write-target-report.py",
        "uv run --script scripts/run-pi-skill-eval.py pi-extension-ui --prompt-file evaluations/pi-prompts/plugin-ui-short-terminal-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id <fresh-id> --expect-output short-terminal-review.json --expect-output pager.mjs --expect-output-json-field short-terminal-review.json::mode=tui",
        "uv run --script scripts/run-pi-skill-eval.py codex-plugin-ui --prompt-file evaluations/pi-prompts/plugin-ui-allocated-panel-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id <fresh-id> --expect-output panel-review.json --expect-output-json-field panel-review.json::presentation=neighborhood-list --expect-output-json-field panel-review.json::effectiveFontPx=7.65",
        "```", "",
        "Use desktop-plugin-ui with the same allocated-panel prompt for the comparison-router contract. Actual retained IDs are 20261112-ui-short-terminal-contract-sol-1, 20261112-ui-short-terminal-contract-sol-2, 20261112-ui-allocated-panel-codex-sol-1 and 20261112-ui-allocated-panel-router-sol-1. Summarize every corresponding events.jsonl with scripts/summarize-pi-json-events.py --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error. The companion JSON preserves their separate strict/artifact outcomes.", "",
        "Install the exact host-capture dependencies with npm install --prefix projects/plugin-ui-rich-interfaces/host-tests. The terminal harness uses installed executables, explicit extensions and task-local state. It launches no shell and sends only known command/key inputs. Do not turn a login gate, capture limitation, API enablement error or unavailable tool into a claimed UI pass.", "",
        "## Open gates", "",
        "The two requested inputs remain pending: authorization to add the exact test server to personal Claude Desktop configuration with a backup, and the Gemini Enterprise instance/agent URL. The repository's AGENTS.md limits writes outside this root. No personal configuration, cloud API enablement, IAM policy, paid service or administrator registration was changed. Claude Code also needs an authenticated usable session. All broad skills remain validating.", "",
    ]
    DESTINATION.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"report": str(DESTINATION.with_suffix('.md')), "screenshots": len(pictures), "browserChecks": count('browser'), "piTuiChecks": count('pi'), "codexPackageChecks": count('codex'), "scope": "Retained live-host observations; pending hosts remain unverified."}))


if __name__ == "__main__":
    main()
