#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run pi forward-tests for gallery SVG recreation in style-checked batches."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path


def load_items(source_dir: Path, manifest_path: Path | None) -> list[dict]:
    if manifest_path:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        items = data.get("items", data if isinstance(data, list) else [])
        result = []
        for item in items:
            source = Path(item.get("file") or source_dir / item["relativeFile"])
            if not source.exists():
                source = source_dir / item["relativeFile"]
            result.append(
                {
                    "index": item.get("index", len(result) + 1),
                    "id": item.get("id") or source.stem,
                    "title": item.get("title") or item.get("id") or source.stem,
                    "file": source.resolve(),
                    "relativeFile": source.name,
                    "size": source.stat().st_size,
                }
            )
        return result

    return [
        {
            "index": index + 1,
            "id": path.stem,
            "title": path.stem,
            "file": path.resolve(),
            "relativeFile": path.name,
            "size": path.stat().st_size,
        }
        for index, path in enumerate(sorted(source_dir.glob("*.svg")))
    ]


def make_batches(items: list[dict], batch_size: int, max_source_bytes: int) -> list[list[dict]]:
    batches: list[list[dict]] = []
    current: list[dict] = []
    current_bytes = 0
    for item in items:
        item_size = int(item["size"])
        would_exceed_count = len(current) >= batch_size
        would_exceed_bytes = current and current_bytes + item_size > max_source_bytes
        if would_exceed_count or would_exceed_bytes:
            batches.append(current)
            current = []
            current_bytes = 0
        current.append(item)
        current_bytes += item_size
    if current:
        batches.append(current)
    return batches


def default_work_dir() -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(os.environ.get("TEMP", ".")) / f"pi-d3-svg-gallery-style-{stamp}"


def write_prompt(batch_dir: Path, batch: list[dict], attempt: int, retry_report: Path | None = None) -> Path:
    pairs = "\n".join(
        f"- `expected/{item['relativeFile']}` must remain equivalent to `source/{item['relativeFile']}`"
        for item in batch
    )
    templates = "\n".join(
        f"- `{item['relativeFile']}`: edit only `expected/{item['relativeFile']}`; constraints in `template/{Path(item['relativeFile']).stem}.inventory.md`; signature in `template/{Path(item['relativeFile']).stem}.signature.json`"
        for item in batch
    )
    compare_pairs = " `\n  ".join(
        f"--pair source\\{item['relativeFile']}=expected\\{item['relativeFile']}"
        for item in batch
    )
    retry_text = ""
    if retry_report:
        retry_text = f"""

This is retry attempt {attempt}. The previous style comparison report is attached as
`@{retry_report.as_posix()}`. Fix the candidate SVGs in `expected/` until the same
comparison command exits successfully. Treat every reported extra font size, missing
color, extra color, stroke-width drift, opacity drift, or animation-count drift as a
code defect.
"""

    prompt = f"""Use the d3-animated-svg skill already loaded for this run.

The final candidate SVGs are already preseeded in `expected/` from source-derived
templates. Do not recreate them from scratch. Your task is to make minimal data/text
edits while preserving the preseeded mark structure.

Required source/candidate pairs:

{pairs}

Source-derived templates have already been prepared for this batch:

{templates}

Requirements:

1. Use new labels and values for every candidate. Do not copy source domain labels,
   row names, exact numeric values, source-specific prose, or source titles.
2. Preserve each source SVG's `viewBox`, root font family, exact font-size bins,
   color set, stroke-width bins, opacity profile, dash patterns, label halo style,
   render tag count profile, animation node count, and animation style.
3. Do not invent title, caption, legend, or annotation font sizes. Reuse only the
   source font-size bins for that SVG.
4. Do not introduce colors outside each source SVG color set. Map new categories
   onto the same source color roles.
5. Create `output/index.html` as a browser-openable D3 implementation that renders
   all candidates in this batch. Base it on `template/*.template.html`.
6. Write each standalone candidate SVG to `expected/` using exactly the same file
   name as its source. The `expected/` files are preseeded from templates; leave the
   seeded SVG structure intact unless a text/data edit is clearly needed.
7. Create `output/NOTES.md` summarizing, per SVG, what data changed and which style
   signature was preserved.
8. Use only the loaded d3-animated-svg skill and the files attached in this batch.
   Do not search the filesystem, do not read unrelated project files, and do not use
   shell commands. Do not summarize dense mark fields, sketchy overlays, calendar
   cells, stippling, or per-mark animation into fewer marks; preserve the source's
   approximate number of rendered marks and animation nodes. The outer harness will
   run this exact comparison command after your response and will reject the batch if
   it fails:

Allowed SVG edits:

- You may edit text content in `title`, `desc`, `text`, and `tspan` nodes.
- You may update `output/index.html` and `output/NOTES.md`.
- Do not delete or add `path`, `rect`, `circle`, `line`, `polygon`, `polyline`,
  `image`, `use`, `animate`, `animateTransform`, `animateMotion`, or `set` nodes.
- Do not replace a dense seeded SVG with a simplified reconstruction. If unsure,
  preserve the seeded `expected/*.svg` structure byte-for-byte.

```powershell
uv run --script C:\\Users\\villa\\dev\\skills\\d3-animated-svg\\scripts\\compare_svg_style_signatures.py `
  {compare_pairs} `
  --report output\\style-compare.json
```

Do not say the work is ready unless that command exits successfully.
{retry_text}
"""
    path = batch_dir / ("retry-prompt.md" if attempt > 1 else "recreate-prompt.md")
    path.write_text(textwrap.dedent(prompt).strip() + "\n", encoding="utf-8")
    return path


def copy_sources(batch_dir: Path, batch: list[dict]) -> None:
    source_dir = batch_dir / "source"
    expected_dir = batch_dir / "expected"
    output_dir = batch_dir / "output"
    source_dir.mkdir(parents=True, exist_ok=True)
    expected_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in batch:
        shutil.copy2(item["file"], source_dir / item["relativeFile"])


def prepare_templates(args: argparse.Namespace, batch_dir: Path, batch: list[dict]) -> int:
    if not args.use_templates:
        return 0
    template_dir = batch_dir / "template"
    expected_dir = batch_dir / "expected"
    manifest = batch_dir / "output" / "template-manifest.json"
    command = [
        sys.executable,
        str(args.template_script),
        *[str(batch_dir / "source" / item["relativeFile"]) for item in batch],
        "--template-dir",
        str(template_dir),
        "--expected-dir",
        str(expected_dir),
        "--manifest",
        str(manifest),
    ]
    return run_command(command, batch_dir, batch_dir / "output" / "template-prepare.log", args.timeout_seconds)


def run_command(command: list[str], cwd: Path, log_path: Path, timeout_seconds: int) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        log_path.write_text(
            output + f"\n[TIMEOUT] Command exceeded {timeout_seconds} seconds.\n",
            encoding="utf-8",
        )
        return 124
    log_path.write_text(completed.stdout, encoding="utf-8")
    return completed.returncode


def run_pi(args: argparse.Namespace, batch_dir: Path, batch: list[dict], prompt: Path, attempt: int, retry_report: Path | None) -> int:
    command = [
        *args.pi_command_parts,
        "--no-session",
        "--no-context-files",
        "--no-extensions",
        "--no-skills",
        "--no-prompt-templates",
        "--no-themes",
        "--tools",
        args.pi_tools,
        "--approve",
        "--skill",
        str(args.skill_path),
        "--model",
        args.model,
        "--thinking",
        args.thinking,
        "-p",
        f"@{prompt.name}",
    ]
    if retry_report:
        command.append(f"@{retry_report}")
        if args.use_templates:
            for item in batch:
                stem = Path(item["relativeFile"]).stem
                command.append(f"@template\\{stem}.inventory.md")
        for item in batch:
            expected = batch_dir / "expected" / item["relativeFile"]
            if expected.exists():
                command.append(f"@expected\\{item['relativeFile']}")
    elif args.use_templates:
        for item in batch:
            stem = Path(item["relativeFile"]).stem
            command.append(f"@template\\{stem}.inventory.md")
            command.append(f"@expected\\{item['relativeFile']}")
    if not args.use_templates:
        for item in batch:
            command.append(f"@source\\{item['relativeFile']}")

    if args.dry_run:
        print("DRY RUN:", " ".join(command))
        return 0
    return run_command(command, batch_dir, batch_dir / "output" / f"pi-attempt-{attempt}.log", args.timeout_seconds)


def run_compare(args: argparse.Namespace, batch_dir: Path, batch: list[dict], attempt: int) -> tuple[int, Path]:
    report = batch_dir / "output" / f"style-compare-attempt-{attempt}.json"
    command = [
        sys.executable,
        str(args.compare_script),
    ]
    for item in batch:
        command.extend(["--pair", f"source\\{item['relativeFile']}=expected\\{item['relativeFile']}"])
    command.extend(["--report", str(report)])
    return run_command(command, batch_dir, batch_dir / "output" / f"compare-attempt-{attempt}.log", args.timeout_seconds), report


def expected_files_exist(batch_dir: Path, batch: list[dict]) -> list[str]:
    missing = []
    for item in batch:
        if not (batch_dir / "expected" / item["relativeFile"]).exists():
            missing.append(item["relativeFile"])
    return missing


def expected_files_modified_after(batch_dir: Path, batch: list[dict], timestamp: float) -> list[str]:
    stale = []
    for item in batch:
        expected = batch_dir / "expected" / item["relativeFile"]
        if not expected.exists() or expected.stat().st_mtime <= timestamp:
            stale.append(item["relativeFile"])
    return stale


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--work-dir", type=Path, default=default_work_dir())
    parser.add_argument("--skill-path", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--compare-script", type=Path, default=Path(__file__).resolve().with_name("compare_svg_style_signatures.py"))
    parser.add_argument("--template-script", type=Path, default=Path(__file__).resolve().with_name("prepare_svg_recreation_templates.py"))
    parser.add_argument("--no-templates", dest="use_templates", action="store_false")
    parser.set_defaults(use_templates=True)
    parser.add_argument("--require-pi-edits", dest="require_pi_edits", action="store_true")
    parser.add_argument("--no-require-pi-edits", dest="require_pi_edits", action="store_false")
    parser.set_defaults(require_pi_edits=False)
    parser.add_argument("--pi-command", default="pi")
    parser.add_argument("--pi-tools", default="read,write")
    parser.add_argument("--model", default="openai-codex/gpt-5.4")
    parser.add_argument("--thinking", default="medium")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-source-bytes", type=int, default=220_000)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--start-batch", type=int, default=1)
    parser.add_argument("--max-batches", type=int)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def resolve_pi_command(command: str) -> list[str]:
    command_path = Path(command)
    if command_path.exists():
        return [str(command_path.resolve())]
    candidates = []
    if os.name == "nt" and not command.lower().endswith((".cmd", ".exe", ".ps1")):
        candidates.extend([f"{command}.cmd", f"{command}.exe", f"{command}.ps1"])
    candidates.append(command)
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if not resolved:
            continue
        if resolved.lower().endswith(".ps1"):
            return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", resolved]
        return [resolved]
    raise SystemExit(f"Could not find pi command: {command}")


def main() -> int:
    args = build_parser().parse_args()
    args.source_dir = args.source_dir.resolve()
    args.skill_path = args.skill_path.resolve()
    args.compare_script = args.compare_script.resolve()
    args.template_script = args.template_script.resolve()
    args.work_dir = args.work_dir.resolve()
    args.pi_command_parts = resolve_pi_command(args.pi_command)
    args.work_dir.mkdir(parents=True, exist_ok=True)

    items = load_items(args.source_dir, args.manifest)
    selected = items[args.offset :]
    if args.limit is not None:
        selected = selected[: args.limit]
    batches = make_batches(selected, args.batch_size, args.max_source_bytes)
    if args.start_batch > 1:
        batches = batches[args.start_batch - 1 :]
    if args.max_batches is not None:
        batches = batches[: args.max_batches]

    summary = {
        "sourceDir": str(args.source_dir),
        "workDir": str(args.work_dir),
        "model": args.model,
        "thinking": args.thinking,
        "selectedCount": len(selected),
        "batchCount": len(batches),
        "batches": [],
    }

    print(f"Selected SVGs: {len(selected)}")
    print(f"Batches to run: {len(batches)}")
    print(f"Work dir: {args.work_dir}")

    overall_ok = True
    for batch_index, batch in enumerate(batches, start=args.start_batch):
        batch_dir = args.work_dir / f"batch-{batch_index:03d}"
        batch_dir.mkdir(parents=True, exist_ok=True)
        copy_sources(batch_dir, batch)
        template_code = prepare_templates(args, batch_dir, batch)
        batch_record = {
            "batch": batch_index,
            "dir": str(batch_dir),
            "items": [{"id": item["id"], "file": item["relativeFile"], "size": item["size"]} for item in batch],
            "attempts": [],
            "ok": False,
        }
        if template_code != 0:
            overall_ok = False
            batch_record["error"] = "template preparation failed"
            summary["batches"].append(batch_record)
            print(f"  FAIL template preparation exit code {template_code}")
            continue

        print(f"\nBatch {batch_index}: {len(batch)} SVG(s)")
        retry_report = None
        for attempt in range(1, args.retries + 2):
            prompt = write_prompt(batch_dir, batch, attempt, retry_report)
            prompt_mtime = prompt.stat().st_mtime
            pi_code = run_pi(args, batch_dir, batch, prompt, attempt, retry_report)
            if args.dry_run:
                batch_record["attempts"].append(
                    {
                        "attempt": attempt,
                        "piExitCode": pi_code,
                        "compareExitCode": None,
                        "compareReport": None,
                        "missing": [],
                    }
                )
                batch_record["ok"] = True
                print(f"  DRY RUN attempt {attempt}")
                break
            missing = expected_files_exist(batch_dir, batch)
            stale = []
            if args.require_pi_edits:
                stale = expected_files_modified_after(batch_dir, batch, prompt_mtime)
            compare_code = 1
            compare_report = None
            if pi_code == 0 and not missing and not stale and not args.dry_run:
                compare_code, compare_report = run_compare(args, batch_dir, batch, attempt)
                retry_report = compare_report.relative_to(batch_dir)
            elif missing:
                (batch_dir / "output" / f"missing-attempt-{attempt}.json").write_text(
                    json.dumps({"missing": missing}, indent=2),
                    encoding="utf-8",
                )
            elif stale:
                (batch_dir / "output" / f"stale-attempt-{attempt}.json").write_text(
                    json.dumps({"notRewrittenAfterPrompt": stale}, indent=2),
                    encoding="utf-8",
                )

            attempt_record = {
                "attempt": attempt,
                "piExitCode": pi_code,
                "compareExitCode": compare_code,
                "compareReport": str(compare_report) if compare_report else None,
                "missing": missing,
                "stale": stale,
            }
            batch_record["attempts"].append(attempt_record)
            if pi_code == 0 and not missing and compare_code == 0:
                batch_record["ok"] = True
                print(f"  PASS attempt {attempt}")
                break
            print(f"  FAIL attempt {attempt}: pi={pi_code}, compare={compare_code}, missing={len(missing)}")

        if not batch_record["ok"]:
            overall_ok = False
        summary["batches"].append(batch_record)
        (args.work_dir / "run-manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    passed = sum(1 for batch in summary["batches"] if batch["ok"])
    print(f"\nPassed batches: {passed}/{len(summary['batches'])}")
    print(f"Run manifest: {(args.work_dir / 'run-manifest.json').resolve()}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
