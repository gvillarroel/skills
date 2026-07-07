#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zlib
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_THEME = SKILL_DIR / "assets" / "themes" / "cs2.puml"
DEFAULT_SERVER_URL = "https://www.plantuml.com/plantuml"
DEFAULT_KROKI_URL = "https://kroki.io"
PLANTUML_SUFFIXES = {".puml", ".plantuml", ".pu"}
PLANTUML_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
SUPPORTED_FORMATS = {"svg", "png"}


@dataclass
class RenderOutput:
    format: str
    path: str
    size_bytes: int
    engine: str


@dataclass
class DiagramResult:
    source: str
    diagram_id: str
    start_directive: str
    themed_source: str | None
    outputs: list[RenderOutput]
    ok: bool
    error: str | None


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def discover_sources(input_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in PLANTUML_SUFFIXES
    )


def first_start_directive(source: str) -> str:
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("@start"):
            return stripped
    raise ValueError("PlantUML source is missing an @start... directive")


def inject_theme(source: str, theme: str) -> str:
    if "plantuml-colorset-renderer: cs2 custom theme" in source:
        return source
    lines = source.splitlines()
    for index, line in enumerate(lines):
        if line.strip().lower().startswith("@start"):
            return "\n".join(lines[: index + 1] + [theme.rstrip()] + lines[index + 1 :]) + "\n"
    raise ValueError("PlantUML source is missing an @start... directive")


def encode_triplet(b1: int, b2: int, b3: int) -> str:
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return "".join(PLANTUML_ALPHABET[c] for c in (c1, c2, c3, c4))


def plantuml_encode(source: str) -> str:
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed = compressor.compress(source.encode("utf-8")) + compressor.flush()
    encoded_parts: list[str] = []
    for index in range(0, len(compressed), 3):
        chunk = compressed[index : index + 3]
        padded = chunk + b"\x00" * (3 - len(chunk))
        encoded_parts.append(encode_triplet(padded[0], padded[1], padded[2]))
    return "".join(encoded_parts)


def kroki_encode(source: str) -> str:
    compressed = zlib.compress(source.encode("utf-8"), 9)
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def fetch_url(url: str, timeout: int, retries: int) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, headers={"User-Agent": "plantuml-colorset-renderer/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:500]
            last_error = RuntimeError(f"HTTP {error.code}: {detail}")
            if error.code not in {408, 429, 500, 502, 503, 504} or attempt >= retries:
                break
        except urllib.error.URLError as error:
            last_error = RuntimeError(f"request failed: {error}")
            if attempt >= retries:
                break
        time.sleep(min(2**attempt, 8))
    assert last_error is not None
    raise last_error


def validate_payload(payload: bytes, fmt: str) -> None:
    if fmt == "svg":
        text = payload.decode("utf-8", errors="replace")
        if "<svg" not in text:
            raise RuntimeError("SVG response does not contain an <svg> element")
        lowered = text.lower()
        if "syntax error" in lowered or ">error line" in lowered:
            raise RuntimeError("PlantUML rendered an SVG error response")
    elif fmt == "png":
        if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError("PNG response does not start with a PNG signature")


def render_with_server(source: str, fmt: str, output_path: Path, server_url: str, timeout: int) -> None:
    url = f"{server_url.rstrip('/')}/{fmt}/{plantuml_encode(source)}"
    payload = fetch_url(url, timeout, retries=3)
    validate_payload(payload, fmt)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(payload)


def render_with_kroki(source: str, fmt: str, output_path: Path, kroki_url: str, timeout: int) -> None:
    url = f"{kroki_url.rstrip('/')}/plantuml/{fmt}/{kroki_encode(source)}"
    payload = fetch_url(url, timeout, retries=3)
    validate_payload(payload, fmt)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(payload)


def render_with_cli(source: str, fmt: str, output_path: Path, command: str, timeout: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [command, f"-t{fmt}", "-pipe"],
        input=source.encode("utf-8"),
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"PlantUML command failed with exit {result.returncode}: {stderr}")
    payload = result.stdout
    if fmt == "svg" and b"<svg" not in payload:
        raise RuntimeError("PlantUML command did not emit SVG")
    if fmt == "png" and not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("PlantUML command did not emit PNG")
    output_path.write_bytes(payload)


def choose_engine(engine: str) -> str:
    if engine == "auto":
        return "cli" if shutil.which("plantuml") else "kroki"
    return engine


def output_path_for(source: Path, input_dir: Path, output_dir: Path, fmt: str) -> Path:
    relative_source = source.relative_to(input_dir)
    return output_dir / fmt / relative_source.with_suffix(f".{fmt}")


def diagram_id_for(source: Path, input_dir: Path) -> str:
    return source.relative_to(input_dir).with_suffix("").as_posix().replace("/", "-")


def render_source(
    *,
    source_path: Path,
    input_dir: Path,
    output_dir: Path,
    formats: list[str],
    theme: str,
    engine: str,
    server_url: str,
    kroki_url: str,
    plantuml_command: str,
    timeout: int,
    write_themed: bool,
) -> DiagramResult:
    raw_source = source_path.read_text(encoding="utf-8")
    start_directive = first_start_directive(raw_source)
    themed_source_text = inject_theme(raw_source, theme)
    themed_source_path: Path | None = None
    if write_themed:
        themed_source_path = output_dir / "themed-source" / source_path.relative_to(input_dir)
        themed_source_path.parent.mkdir(parents=True, exist_ok=True)
        themed_source_path.write_text(themed_source_text, encoding="utf-8", newline="\n")

    outputs: list[RenderOutput] = []
    try:
        for fmt in formats:
            target = output_path_for(source_path, input_dir, output_dir, fmt)
            if engine == "server":
                render_with_server(themed_source_text, fmt, target, server_url, timeout)
            elif engine == "kroki":
                render_with_kroki(themed_source_text, fmt, target, kroki_url, timeout)
            elif engine == "cli":
                render_with_cli(themed_source_text, fmt, target, plantuml_command, timeout)
            else:
                raise ValueError(f"Unsupported engine: {engine}")
            outputs.append(
                RenderOutput(
                    format=fmt,
                    path=relative(target, output_dir),
                    size_bytes=target.stat().st_size,
                    engine=engine,
                )
            )
        return DiagramResult(
            source=source_path.relative_to(input_dir).as_posix(),
            diagram_id=diagram_id_for(source_path, input_dir),
            start_directive=start_directive,
            themed_source=relative(themed_source_path, output_dir) if themed_source_path else None,
            outputs=outputs,
            ok=True,
            error=None,
        )
    except Exception as error:
        return DiagramResult(
            source=source_path.relative_to(input_dir).as_posix(),
            diagram_id=diagram_id_for(source_path, input_dir),
            start_directive=start_directive,
            themed_source=relative(themed_source_path, output_dir) if themed_source_path else None,
            outputs=outputs,
            ok=False,
            error=str(error),
        )


def write_report(report_path: Path, report: dict[str, object]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render PlantUML sources to SVG and PNG with the bundled CS2 theme.")
    parser.add_argument("input", type=Path, help="Directory containing .puml, .plantuml, or .pu files.")
    parser.add_argument("--output", type=Path, required=True, help="Output directory for rendered files.")
    parser.add_argument("--format", choices=sorted(SUPPORTED_FORMATS), action="append", dest="formats", help="Output format. May be repeated.")
    parser.add_argument("--theme", type=Path, default=DEFAULT_THEME, help="PlantUML theme file to inject after @start.")
    parser.add_argument("--engine", choices=["auto", "kroki", "server", "cli"], default="auto", help="Render engine. Default: auto.")
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL, help="PlantUML Server base URL for server rendering.")
    parser.add_argument("--kroki-url", default=DEFAULT_KROKI_URL, help="Kroki base URL for Kroki PlantUML rendering.")
    parser.add_argument("--plantuml-command", default="plantuml", help="PlantUML CLI command for CLI rendering.")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds per render.")
    parser.add_argument("--write-themed", action="store_true", help="Write themed source copies under output/themed-source.")
    parser.add_argument("--report", type=Path, required=True, help="JSON report path.")
    args = parser.parse_args()

    input_dir = args.input.resolve()
    output_dir = args.output.resolve()
    formats = args.formats or ["svg", "png"]
    engine = choose_engine(args.engine)

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input directory does not exist: {input_dir}", file=sys.stderr)
        return 2
    theme_path = args.theme.resolve()
    if not theme_path.exists():
        print(f"Theme file does not exist: {theme_path}", file=sys.stderr)
        return 2

    theme = theme_path.read_text(encoding="utf-8")
    sources = discover_sources(input_dir)
    results = [
        render_source(
            source_path=source,
            input_dir=input_dir,
            output_dir=output_dir,
            formats=formats,
            theme=theme,
            engine=engine,
            server_url=args.server_url,
            kroki_url=args.kroki_url,
            plantuml_command=args.plantuml_command,
            timeout=args.timeout,
            write_themed=args.write_themed,
        )
        for source in sources
    ]
    failed = [result for result in results if not result.ok]
    rendered_output_count = sum(len(result.outputs) for result in results)
    report = {
        "ok": not failed and bool(sources),
        "theme": relative(theme_path, SKILL_DIR),
        "engine": engine,
        "serverUrl": args.server_url if engine == "server" else None,
        "krokiUrl": args.kroki_url if engine == "kroki" else None,
        "formats": formats,
        "sourceDiagramCount": len(sources),
        "renderedDiagramCount": len([result for result in results if result.ok]),
        "renderedOutputCount": rendered_output_count,
        "failedDiagramCount": len(failed),
        "results": [
            {
                "source": result.source,
                "diagramId": result.diagram_id,
                "startDirective": result.start_directive,
                "themedSource": result.themed_source,
                "ok": result.ok,
                "error": result.error,
                "outputs": [output.__dict__ for output in result.outputs],
            }
            for result in results
        ],
    }
    write_report(args.report, report)
    print(json.dumps({key: report[key] for key in ("ok", "sourceDiagramCount", "renderedOutputCount", "failedDiagramCount")}, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
