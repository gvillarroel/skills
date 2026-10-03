#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build an offline, replayable draft-prefix verification explanation and portable SVG."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys
import unicodedata


PATTERN_ID = "d3-speculative-decoding"


def literal(value: str, field: str) -> str:
    if not value or value != value.strip() or any(unicodedata.category(c).startswith("C") for c in value):
        raise ValueError(f"{field} must be non-empty literal text without surrounding whitespace or control characters")
    return value


def text_size(value: str, maximum: float, width: float) -> float:
    # Conservative advance estimate for the bundled system-font stack. Reject
    # unsupported densities rather than silently truncate data or widen output.
    units = sum(1.1 if unicodedata.east_asian_width(c) in {"W", "F"} else .72 for c in value)
    size = min(maximum, width / max(units, 1))
    if size < 12:
        raise ValueError(f"Text {value!r} cannot fit readably in the requested layout; use a wider viewport or the custom recipe workflow")
    return size


def build_svg(tokens: list[str], accepted: int, resume: str, *, width: int = 720,
              height: int = 440, colorset: str = "colorset1", title: str = "Speculative decoding",
              alternates: list[tuple[int, str]] | None = None) -> str:
    if not 1 <= len(tokens) <= 12:
        raise ValueError("Supply 1 to 12 draft tokens; use the custom recipe workflow for larger structures")
    if not 0 <= accepted <= len(tokens):
        raise ValueError("accepted-count must be between zero and the draft-token count")
    if width < 480 or height < 400:
        raise ValueError("This layout requires width >= 480 and height >= 400; use the custom recipe workflow for smaller viewports")
    if colorset not in {"colorset1", "colorset2"}:
        raise ValueError("colorset must be colorset1 or colorset2")
    tokens = [literal(t, "draft-token") for t in tokens]
    resume, title = literal(resume, "resume-token"), literal(title, "title")
    alternates = alternates or []
    positions = set()
    for position, label in alternates:
        literal(label, "alternate")
        if not 1 <= position <= len(tokens) or position in positions:
            raise ValueError("Each alternate must name a unique draft position from 1 to the draft-token count")
        positions.add(position)
    palette_path = Path(__file__).resolve().parents[1] / "assets/palettes/colorsets.json"
    palette = json.loads(palette_path.read_text(encoding="utf-8"))["colorsets"][colorset]["roles"]
    bg, ink, surface = palette["background"], palette["ink"], palette["surface"]
    draft = palette.get("secondary", palette["primaryDark"])
    positive = palette.get("positive", palette["primaryDark"])
    rejected, target = palette["primary"], palette.get("special", palette["inkDark"])
    verifier = palette.get("attention", palette["quiet"])
    w, h = width, height
    x0, x1 = 74, w - 74
    step = (x1 - x0) / (len(tokens) + 1)
    box = min(100, step - 18)
    if box < 40:
        raise ValueError("Too many tokens for the requested width; use a wider viewport or the custom recipe workflow")
    xs = [x0 + i * step for i in range(len(tokens) + 2)]
    # Extra height expands whitespace instead of scaling fonts into clipped text.
    shift = (h - 440) / 2
    token_y, rail_y, branch_y = 238 + shift, 334 + shift, 180 + shift
    caption_y = h - 66
    title_font = text_size(title, 22, w - 48)
    desc = (f"A draft model proposes {len(tokens)} tokens. The target model verifies the batch, "
            f"accepts the first {accepted}, rejects the remaining {len(tokens) - accepted}, "
            "and resumes generation. A separate moving indicator shows progress without covering token labels.")
    chunks = [f'<svg xmlns="http://www.w3.org/2000/svg" id="decode" width="{w}" height="{h}" '
              f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="decode-title decode-description" '
              f'data-pattern-id="{PATTERN_ID}" data-colorset="{colorset}">',
              f'<title id="decode-title">{escape(title)}</title><desc id="decode-description">{escape(desc)}</desc>',
              '<style>text{font-family:Arial,Helvetica,sans-serif} .token-label{font-family:Consolas,monospace}'
              '@media(prefers-reduced-motion:reduce){.motion-marker{display:none}}</style>',
              f'<rect width="{w}" height="{h}" fill="{bg}"/>']

    def add_text(x: float, y: float, label: str, *, size: float = 14, fill: str = ink,
                 anchor: str = "start", css: str = "", weight: str = "normal") -> None:
        chunks.append(f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" fill="{fill}" '
                      f'text-anchor="{anchor}" font-weight="{weight}" class="{css}">{escape(label)}</text>')

    add_text(24, 40, title, size=title_font, weight="bold")
    subtitle = "Draft ahead. Verify together. Keep the prefix."
    add_text(24, 65, subtitle, size=text_size(subtitle, 14, w - 48))
    chunks.append(f'<g class="verification-batch"><rect x="24" y="92" width="{w - 48}" height="60" rx="10" '
                  f'fill="{surface}" stroke="{palette["line"]}"/>')
    chunks.append(f'<rect x="25" y="93" width="{w - 50}" height="58" rx="9" fill="{verifier}" fill-opacity=".45">'
                  f'<animate attributeName="width" from="0" to="{w - 50}" begin=".65s" dur="1.2s" fill="remove"/></rect>')
    add_text(38, 116, f"Target verifies {len(tokens)} draft tokens together", size=14, weight="bold")
    add_text(38, 138, f"Accept {accepted}  /  Reject {len(tokens) - accepted}  /  Resume target", size=13)
    chunks.append('</g>')
    # Connectors are behind the token cards. The resumed branch comes from the
    # last accepted prefix rather than treating rejected draft text as context.
    for index in range(len(xs) - 1):
        chunks.append(f'<path d="M {xs[index]:g} {token_y:g} H {xs[index + 1]:g}" fill="none" '
                      f'stroke="{draft}" stroke-width="2" stroke-dasharray="5 4"/>')
    resume_y = token_y + 58
    exit_x, entry_x = xs[accepted] + box / 2 + 5, xs[-1] - box / 2 - 5
    chunks.append(f'<path class="target-resume" d="M {xs[accepted] + box / 2:g} {token_y:g} '
                  f'H {exit_x:g} V {resume_y:g} H {entry_x:g} V {token_y:g} H {xs[-1] - box / 2:g}" '
                  f'fill="none" stroke="{target}" stroke-width="2"/>')
    for position, label in alternates:
        x = xs[position]
        chunks.append(f'<path d="M {x - 35:g} {token_y - 21:g} V {branch_y + 10:g} H {x:g}" fill="none" '
                      f'stroke="{palette["muted"]}" stroke-dasharray="3 4"/>')
        add_text(x, branch_y, label, anchor="middle", size=text_size(label, 13, box), fill=ink, css="alternate-label")

    for index, label in enumerate(["prompt", *tokens, resume]):
        is_draft = 1 <= index <= len(tokens)
        status = ("accepted" if index <= accepted else "rejected") if is_draft else ("context" if index == 0 else "target")
        color = {"accepted": positive, "rejected": rejected, "context": ink, "target": target}[status]
        x = xs[index]
        top = "Prompt" if index == 0 else (f"Draft {index}" if is_draft else "Target")
        add_text(x, token_y - 30, top, anchor="middle", size=12)
        chunks.append(f'<g class="token {status}" data-token-index="{index}">'
                      f'<rect x="{x - box / 2:g}" y="{token_y - 21:g}" width="{box:g}" height="42" rx="8" '
                      f'fill="{color}" stroke="{color}"/>')
        add_text(x, token_y + 5, label, anchor="middle", size=text_size(label, 16, box - 12), fill=surface, css="token-label", weight="bold")
        chunks.append('</g>')
        add_text(x, token_y + 43, {"accepted": "Accepted", "rejected": "Rejected", "context": "Context", "target": "Resumes"}[status],
                 size=12, anchor="middle", css="token-status")
    # This rail remains clear of every token, status, and caption, including the
    # final frame. Removing the marker after the finite pass preserves meaning.
    chunks.append(f'<path d="M {x0} {rail_y:g} H {x1}" fill="none" stroke="{palette["line"]}" stroke-width="2"/>')
    chunks.append(f'<circle class="motion-marker" cx="{x1}" cy="{rail_y:g}" r="5" fill="{draft}" opacity="0">'
                  f'<animate attributeName="cx" from="{x0}" to="{x1}" begin=".1s" dur="2.6s" fill="remove"/>'
                  '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.05;.9;1" begin=".1s" dur="2.6s" fill="remove"/></circle>')
    summary = f"Accepted prefix: {accepted}. Rejected tail: {len(tokens) - accepted}."
    add_text(24, caption_y, summary, size=text_size(summary, 14, w - 48), weight="bold")
    # Two short lines keep the explanation readable at the minimum viewport.
    add_text(24, caption_y + 23, "The target resumes from the accepted context.", size=13)
    add_text(24, caption_y + 43, "The dashed path is the draft proposal.", size=13)
    chunks.append('</svg>')
    return "\n".join(chunks) + "\n"


def build_html(svg: str, colorset: str, title: str) -> str:
    palette = json.loads((Path(__file__).resolve().parents[1] / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"][colorset]["roles"]
    # Replay clones only the SVG. No source string is injected into executable
    # JavaScript, and no external runtime is required for the exported SVG.
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title>'
            f'<style>body{{margin:0;padding:16px;background:{palette["background"]};color:{palette["ink"]};font-family:Arial,Helvetica,sans-serif}}'
            'main{max-width:1200px;margin:auto}svg{display:block;max-width:100%;height:auto}'
            f'button{{font:inherit;padding:8px 16px;margin-top:12px;border:1px solid {palette["primary"]};'
            f'border-radius:6px;background:{palette["surface"]};color:{palette["ink"]};cursor:pointer}}'
            f'button:focus-visible{{outline:2px solid {palette["primaryDark"]};outline-offset:3px}}</style></head>'
            f'<body><main>{svg}<button id="replay" type="button" aria-controls="decode">Replay</button></main>'
            '<script>document.getElementById("replay").addEventListener("click",()=>{'
            'const svg=document.getElementById("decode");svg.replaceWith(svg.cloneNode(true));});</script></body></html>\n')


def alternate(value: str) -> tuple[int, str]:
    position, separator, label = value.partition(":")
    if not separator or not position.isdecimal() or not label:
        raise argparse.ArgumentTypeError("Expected draft-position:literal-label, such as 2:maybe")
    return int(position), label


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-svg", type=Path, required=True)
    parser.add_argument("--draft-token", action="append", required=True, help="Repeat in proposal order; quote literal whitespace")
    parser.add_argument("--accepted-count", type=int, required=True)
    parser.add_argument("--resume-token", required=True)
    parser.add_argument("--alternate", action="append", type=alternate, default=[], help="Optional 1-based draft-position:label")
    parser.add_argument("--colorset", choices=["colorset1", "colorset2"], default="colorset1")
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=440)
    parser.add_argument("--title", default="Speculative decoding")
    args = parser.parse_args()
    try:
        if args.output_html.resolve() == args.output_svg.resolve():
            raise ValueError("HTML and SVG output paths must be distinct")
        bundle = Path(__file__).resolve().parents[1]
        for path in (args.output_html, args.output_svg):
            if path.resolve().is_relative_to(bundle):
                raise ValueError("Output paths must be outside the read-only skill bundle")
        svg = build_svg(args.draft_token, args.accepted_count, args.resume_token, width=args.width,
                        height=args.height, colorset=args.colorset, title=args.title, alternates=args.alternate)
        html = build_html(svg, args.colorset, args.title)
        for path, content in ((args.output_html, html), (args.output_svg, svg)):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"html": str(args.output_html), "svg": str(args.output_svg), "patternId": PATTERN_ID,
                      "colorset": args.colorset, "draftTokens": len(args.draft_token), "accepted": args.accepted_count}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
