#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///
"""Run an isolated pi smoke test for user-owned D3 artifact creation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "data.js",
    "NOTES.md",
    "rendered.svg",
    "rendered.png",
]


def default_work_dir() -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(os.environ.get("TEMP", ".")) / f"pi-d3-user-artifact-smoke-{stamp}"


def resolve_pi_command(pi_command: str | None) -> list[str]:
    if pi_command:
        return [pi_command]

    pi_cmd = shutil.which("pi.cmd") or shutil.which("pi")
    if pi_cmd:
        base = Path(pi_cmd).resolve().parent
        cli_js = base / "node_modules" / "@earendil-works" / "pi-coding-agent" / "dist" / "cli.js"
        local_node = base / "node.exe"
        node = local_node if local_node.exists() else Path(shutil.which("node") or "")
        if cli_js.exists() and str(node):
            return [str(node), str(cli_js)]
        return [pi_cmd]

    return ["pi"]


def write_jsonl(path: Path, value: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def stream_lines(stream: Any, target: queue.Queue[str | None], log_path: Path | None = None) -> None:
    try:
        for line in iter(stream.readline, ""):
            if log_path is not None:
                with log_path.open("a", encoding="utf-8", errors="replace") as handle:
                    handle.write(line)
            target.put(line)
    finally:
        target.put(None)


def send(process: subprocess.Popen[str], payload: dict[str, Any]) -> None:
    if process.stdin is None:
        return
    process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
    process.stdin.flush()


def build_prompt(skill_dir: Path, output_dir: str) -> str:
    starter_script = skill_dir / "scripts" / "create_d3_svg_starter.py"
    render_script = skill_dir / "scripts" / "render_d3_svg.py"
    return f"""/skill:d3

You are running in an isolated temporary project. Only use the explicitly loaded d3 skill.

Create a user-owned D3 animated SVG artifact under {output_dir}.

Hard boundaries:
- Do not edit any file under the skill directory: {skill_dir}
- Do not edit or copy the gallery fixture in assets/examples.
- Do not read repository-level token files for this ordinary user deliverable; use the portable defaults from the skill's user artifact workflow.

Requirements:
- Use the starter-first workflow. Prefer running:
  uv run --script "{starter_script}" --pattern operational-dashboard --out {output_dir} --title "Incident Risk Overview" --force
- Then edit only data.js and NOTES.md under {output_dir}. Do not edit index.html or styles.css in this smoke test; if something does not fit, shorten data labels or notes.
- Keep the artifact self-contained and deterministic: index.html, styles.css, data.js, NOTES.md, and vendor/d3.min.js if the starter provides it.
- Produce a polished 960x560 D3 SVG dashboard for incident risk overview with bars, compact KPI/context labels, a small trend or threshold cue, clean typography, and operational-dashboard colors.
- Keep side-panel notes short enough to fit the seeded template: no more than five rendered note lines.
- Validate by rendering the SVG:
  uv run --script "{render_script}" {output_dir}/index.html --selector "svg" -o {output_dir}/rendered.svg --screenshot {output_dir}/rendered.png --wait-ms 1200
- Finish with the created file list and validation result."""


def resolve_agent_path(raw_path: str, cwd: Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = cwd / path
    return path.resolve()


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def collect_rpc_events(
    command: list[str],
    cwd: Path,
    prompt: str,
    timeout_seconds: int,
    event_log: Path,
    text_log: Path,
    stderr_log: Path,
) -> dict[str, Any]:
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    stdout_queue: queue.Queue[str | None] = queue.Queue()
    stderr_queue: queue.Queue[str | None] = queue.Queue()
    threading.Thread(target=stream_lines, args=(process.stdout, stdout_queue), daemon=True).start()
    threading.Thread(target=stream_lines, args=(process.stderr, stderr_queue, stderr_log), daemon=True).start()

    send(process, {"id": "prompt-1", "type": "prompt", "message": prompt})

    started = time.monotonic()
    prompt_accepted = False
    agent_ended = False
    assistant_text: list[str] = []
    tool_starts: list[dict[str, Any]] = []
    tool_ends: list[dict[str, Any]] = []
    event_count = 0

    while True:
        if time.monotonic() - started > timeout_seconds:
            send(process, {"type": "abort"})
            process.terminate()
            raise TimeoutError(f"pi RPC smoke test timed out after {timeout_seconds} seconds")

        try:
            line = stdout_queue.get(timeout=0.25)
        except queue.Empty:
            if process.poll() is not None:
                break
            continue

        if line is None:
            if process.poll() is not None:
                break
            continue

        line = line.rstrip("\r\n")
        if not line:
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            write_jsonl(event_log, {"type": "parse_error", "line": line, "error": str(exc)})
            continue

        event_count += 1
        write_jsonl(event_log, event)

        if event.get("type") == "response" and event.get("command") == "prompt":
            prompt_accepted = bool(event.get("success"))

        if event.get("type") == "extension_ui_request":
            method = event.get("method")
            if method == "confirm":
                send(process, {"type": "extension_ui_response", "id": event["id"], "confirmed": True})
            elif method == "select":
                options = event.get("options") or []
                send(process, {"type": "extension_ui_response", "id": event["id"], "value": options[0] if options else ""})
            elif method in {"input", "editor"}:
                send(process, {"type": "extension_ui_response", "id": event["id"], "value": ""})

        if event.get("type") == "message_update":
            delta = event.get("assistantMessageEvent") or {}
            if delta.get("type") == "text_delta":
                text = delta.get("delta") or ""
                assistant_text.append(text)
                with text_log.open("a", encoding="utf-8") as handle:
                    handle.write(text)

        if event.get("type") == "tool_execution_start":
            tool_starts.append({"name": event.get("toolName"), "args": event.get("args") or {}})

        if event.get("type") == "tool_execution_end":
            tool_ends.append(
                {
                    "name": event.get("toolName"),
                    "isError": bool(event.get("isError")),
                    "result": event.get("result"),
                }
            )

        if event.get("type") == "agent_end":
            agent_ended = True
            if process.stdin:
                process.stdin.close()
            break

    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=10)

    while not stderr_queue.empty():
        stderr_queue.get_nowait()

    return {
        "exitCode": process.returncode,
        "promptAccepted": prompt_accepted,
        "agentEnded": agent_ended,
        "eventCount": event_count,
        "toolStarts": tool_starts,
        "toolEnds": tool_ends,
        "assistantTextTail": "".join(assistant_text)[-3000:],
    }


def inspect_svg(svg_path: Path) -> dict[str, Any]:
    text = svg_path.read_text(encoding="utf-8")
    root = ET.fromstring(text)
    view_box = root.attrib.get("viewBox", "")
    numbers = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", view_box)]
    elements = sum(1 for _ in root.iter())
    text_chars = 0
    for node in root.iter():
        if node.tag.endswith("text") and node.text:
            text_chars += len(node.text.strip())
    return {
        "bytes": svg_path.stat().st_size,
        "viewBox": view_box,
        "viewBoxWidth": numbers[2] if len(numbers) >= 4 else None,
        "viewBoxHeight": numbers[3] if len(numbers) >= 4 else None,
        "elements": elements,
        "textCharacters": text_chars,
        "animationNodes": text.count("<animate"),
    }


def audit_html_layout(html_path: Path, wait_ms: int = 1600) -> dict[str, Any]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 760})
        page.goto(html_path.resolve().as_uri(), wait_until="load", timeout=45000)
        page.wait_for_timeout(wait_ms)
        audit = page.evaluate(
            """() => {
                const svg = document.querySelector("svg");
                if (!svg) return { ok: false, error: "No SVG found" };
                const svgRect = svg.getBoundingClientRect();
                const all = Array.from(svg.querySelectorAll("*"));

                function effectiveOpacity(node) {
                    let opacity = 1;
                    let current = node;
                    while (current && current.nodeType === Node.ELEMENT_NODE) {
                        const style = getComputedStyle(current);
                        if (style.display === "none" || style.visibility === "hidden") return 0;
                        const styleOpacity = Number.parseFloat(style.opacity);
                        if (Number.isFinite(styleOpacity)) opacity *= styleOpacity;
                        if (current === svg) break;
                        current = current.parentNode;
                    }
                    return opacity;
                }

                function relativeRect(rect) {
                    return {
                        left: rect.left - svgRect.left,
                        top: rect.top - svgRect.top,
                        right: rect.right - svgRect.left,
                        bottom: rect.bottom - svgRect.top,
                        width: rect.width,
                        height: rect.height
                    };
                }

                function collisionRect(rect) {
                    const trimY = rect.height * 0.28;
                    return {
                        left: rect.left,
                        right: rect.right,
                        top: rect.top + trimY,
                        bottom: rect.bottom - trimY,
                        width: rect.width,
                        height: Math.max(0, rect.height - trimY * 2)
                    };
                }

                function intersects(a, b) {
                    const left = Math.max(a.left, b.left);
                    const top = Math.max(a.top, b.top);
                    const right = Math.min(a.right, b.right);
                    const bottom = Math.min(a.bottom, b.bottom);
                    if (right <= left || bottom <= top) return null;
                    return { left, top, right, bottom, area: (right - left) * (bottom - top) };
                }

                function fillIsOpaque(node) {
                    const style = getComputedStyle(node);
                    const fill = node.getAttribute("fill") || style.fill || "";
                    if (!fill || fill === "none" || fill === "transparent") return false;
                    const opacity = effectiveOpacity(node);
                    const fillOpacity = Number.parseFloat(node.getAttribute("fill-opacity") || style.fillOpacity);
                    const resolvedFillOpacity = Number.isFinite(fillOpacity) ? fillOpacity : 1;
                    return opacity * resolvedFillOpacity >= 0.92;
                }

                const textItems = Array.from(svg.querySelectorAll("text"))
                    .map((node, index) => {
                        const content = (node.textContent || "").trim().replace(/\\s+/g, " ");
                        const rect = node.getBoundingClientRect();
                        const fontSize = Number.parseFloat(getComputedStyle(node).fontSize);
                        return {
                            node,
                            index,
                            order: all.indexOf(node),
                            text: content.length > 70 ? `${content.slice(0, 67)}...` : content,
                            rect: relativeRect(rect),
                            collisionRect: collisionRect(relativeRect(rect)),
                            fontSize: Number.isFinite(fontSize) ? fontSize : null,
                            opacity: effectiveOpacity(node)
                        };
                    })
                    .filter(item => item.text && item.opacity > 0.05 && item.rect.width > 0 && item.rect.height > 0);

                const clippedTexts = textItems.filter(item =>
                    item.rect.left < -2 ||
                    item.rect.top < -2 ||
                    item.rect.right > svgRect.width + 2 ||
                    item.rect.bottom > svgRect.height + 2
                ).map(item => ({ text: item.text, rect: item.rect }));

                const textOverlaps = [];
                for (let i = 0; i < textItems.length; i += 1) {
                    for (let j = i + 1; j < textItems.length; j += 1) {
                        const hit = intersects(textItems[i].collisionRect, textItems[j].collisionRect);
                        if (!hit || hit.area < 10) continue;
                        const smaller = Math.min(
                            textItems[i].collisionRect.width * textItems[i].collisionRect.height,
                            textItems[j].collisionRect.width * textItems[j].collisionRect.height
                        );
                        if (hit.area / Math.max(smaller, 1) > 0.08) {
                            textOverlaps.push({
                                a: textItems[i].text,
                                b: textItems[j].text,
                                area: Number(hit.area.toFixed(2))
                            });
                        }
                    }
                }

                const coverItems = Array.from(svg.querySelectorAll("rect"))
                    .map(node => ({ node, order: all.indexOf(node), rect: relativeRect(node.getBoundingClientRect()) }))
                    .filter(item => item.rect.width > 4 && item.rect.height > 4 && fillIsOpaque(item.node));

                const coveredTexts = [];
                for (const text of textItems) {
                    const area = text.collisionRect.width * text.collisionRect.height;
                    for (const cover of coverItems) {
                        if (cover.order <= text.order) continue;
                        const hit = intersects(text.collisionRect, cover.rect);
                        if (!hit || hit.area < 12) continue;
                        if (hit.area / Math.max(area, 1) > 0.15) {
                            coveredTexts.push({
                                text: text.text,
                                coverOrder: cover.order,
                                overlapRatio: Number((hit.area / Math.max(area, 1)).toFixed(3))
                            });
                            break;
                        }
                    }
                }

                return {
                    ok: clippedTexts.length === 0 && textOverlaps.length === 0 && coveredTexts.length === 0,
                    svgSize: { width: svgRect.width, height: svgRect.height },
                    textCount: textItems.length,
                    clippedTexts,
                    textOverlaps,
                    coveredTexts
                };
            }""",
        )
        browser.close()
        return audit


def validate_result(
    work_dir: Path,
    output_dir: Path,
    skill_dir: Path,
    rpc_summary: dict[str, Any],
    fail_on_external_read: bool,
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    output_resolved = output_dir.resolve()
    if not output_resolved.exists():
        errors.append(f"Output directory was not created: {output_resolved}")
    if is_under(output_resolved, skill_dir):
        errors.append(f"Output directory is inside the skill directory: {output_resolved}")

    missing = [name for name in REQUIRED_FILES if not (output_resolved / name).exists()]
    if missing:
        errors.append("Missing expected files: " + ", ".join(missing))

    for file_name in ["rendered.svg", "rendered.png"]:
        path = output_resolved / file_name
        if path.exists() and path.stat().st_size < 1000:
            errors.append(f"{file_name} is too small to be a useful render: {path.stat().st_size} bytes")

    tool_errors = [item for item in rpc_summary["toolEnds"] if item.get("isError")]
    if tool_errors:
        errors.append(f"pi reported {len(tool_errors)} tool error(s)")

    write_tools = {"write", "edit"}
    skill_writes: list[str] = []
    protected_output_writes: list[str] = []
    external_reads: list[str] = []
    for item in rpc_summary["toolStarts"]:
        name = item.get("name")
        args = item.get("args") or {}
        raw_path = args.get("path")
        if not raw_path:
            continue
        path = resolve_agent_path(str(raw_path), work_dir)
        if name in write_tools and is_under(path, skill_dir):
            skill_writes.append(str(path))
        if name in write_tools and is_under(path, output_resolved) and path.name in {"index.html", "styles.css"}:
            protected_output_writes.append(str(path))
        if name == "read" and not is_under(path, skill_dir) and not is_under(path, output_resolved):
            external_reads.append(str(path))

    if skill_writes:
        errors.append("pi attempted to write inside the skill directory: " + ", ".join(skill_writes))
    if protected_output_writes:
        errors.append(
            "pi edited protected template files instead of data-only fields: "
            + ", ".join(protected_output_writes)
        )
    if fail_on_external_read and external_reads:
        errors.append("pi read files outside the explicit skill and output artifact: " + ", ".join(external_reads))

    metrics: dict[str, Any] = {}
    svg_path = output_resolved / "rendered.svg"
    if svg_path.exists():
        try:
            metrics = inspect_svg(svg_path)
            if metrics["elements"] < 20:
                errors.append(f"Rendered SVG has too few elements: {metrics['elements']}")
            if metrics["textCharacters"] < 80:
                errors.append(f"Rendered SVG has too little text: {metrics['textCharacters']} characters")
            if metrics["viewBoxWidth"] and metrics["viewBoxWidth"] < 700:
                errors.append(f"Rendered SVG viewBox width is unexpectedly small: {metrics['viewBoxWidth']}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Could not inspect rendered SVG: {exc}")

    layout_audit: dict[str, Any] = {}
    html_path = output_resolved / "index.html"
    if html_path.exists():
        try:
            layout_audit = audit_html_layout(html_path)
            if not layout_audit.get("ok"):
                if layout_audit.get("error"):
                    errors.append(f"Browser layout audit failed: {layout_audit['error']}")
                if layout_audit.get("clippedTexts"):
                    errors.append(f"Browser layout audit found clipped text: {len(layout_audit['clippedTexts'])}")
                if layout_audit.get("textOverlaps"):
                    errors.append(f"Browser layout audit found text overlaps: {len(layout_audit['textOverlaps'])}")
                if layout_audit.get("coveredTexts"):
                    errors.append(f"Browser layout audit found covered text: {len(layout_audit['coveredTexts'])}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Could not run browser layout audit: {exc}")

    details = {
        "outputDir": str(output_resolved),
        "requiredFiles": REQUIRED_FILES,
        "externalReads": external_reads,
        "skillWrites": skill_writes,
        "protectedOutputWrites": protected_output_writes,
        "svgMetrics": metrics,
        "layoutAudit": layout_audit,
    }
    return errors, details


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=default_work_dir(), help="Temporary isolated project directory.")
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-dir", default="./risk-dashboard", help="Artifact path relative to the isolated work directory.")
    parser.add_argument("--model", default="openai-codex/gpt-5.3-codex-spark")
    parser.add_argument("--thinking", default="medium")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--pi-command", help="Optional pi executable path. Defaults to the installed pi CLI.")
    parser.add_argument(
        "--allow-external-read",
        action="store_true",
        help="Do not fail if pi reads files outside the explicit skill directory and generated artifact.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    work_dir = args.work_dir.resolve()
    skill_dir = args.skill_dir.resolve()
    output_dir = (work_dir / args.output_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    command = resolve_pi_command(args.pi_command) + [
        "--mode",
        "rpc",
        "--no-session",
        "--no-context-files",
        "--no-extensions",
        "--no-prompt-templates",
        "--no-themes",
        "--no-skills",
        "--skill",
        str(skill_dir),
        "--tools",
        "read,edit,write,bash,ls,find,grep",
        "--approve",
        "--model",
        args.model,
        "--thinking",
        args.thinking,
    ]

    event_log = work_dir / "pi-rpc-events.jsonl"
    text_log = work_dir / "pi-rpc-text.log"
    stderr_log = work_dir / "pi-rpc-stderr.log"
    summary_path = work_dir / "pi-rpc-summary.json"
    prompt = build_prompt(skill_dir, args.output_dir.replace("\\", "/"))

    print(f"Work directory: {work_dir}")
    print("Running pi with context discovery disabled and only the explicit d3 skill loaded.")
    rpc_summary = collect_rpc_events(command, work_dir, prompt, args.timeout_seconds, event_log, text_log, stderr_log)
    errors, details = validate_result(work_dir, output_dir, skill_dir, rpc_summary, not args.allow_external_read)

    summary = {
        "ok": not errors,
        "workDir": str(work_dir),
        "command": command,
        "rpc": rpc_summary,
        "details": details,
        "errors": errors,
        "logs": {
            "events": str(event_log),
            "text": str(text_log),
            "stderr": str(stderr_log),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if errors:
        print("pi isolated user-artifact smoke test failed:")
        for error in errors:
            print(f"- {error}")
        print(f"Summary: {summary_path}")
        return 1

    metrics = details.get("svgMetrics", {})
    print("pi isolated user-artifact smoke test passed.")
    print(f"Output: {details['outputDir']}")
    print(
        "Rendered SVG: "
        f"{metrics.get('viewBox', 'unknown viewBox')}, "
        f"{metrics.get('elements', 0)} elements, "
        f"{metrics.get('textCharacters', 0)} text characters"
    )
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
