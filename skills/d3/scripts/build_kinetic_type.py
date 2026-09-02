#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a deterministic, offline D3 kinetic-type deconstruction page."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
PALETTE_PATH = SKILL_ROOT / "assets" / "palettes" / "colorsets.json"
D3_RUNTIME_PATH = SKILL_ROOT / "assets" / "vendor" / "d3.v7.9.0.min.js"
PATTERN_ID = "d3-kinetic-glyph-mosaic"
VARIANTS = ("tiles", "lines", "dots", "hybrid")
DEFAULT_ITEMS = (
    ("MOSAIC", "tiles"),
    ("VECTOR", "lines"),
    ("PULSE", "dots"),
    ("HYBRID", "hybrid"),
)


def load_palette(colorset: str) -> dict[str, Any]:
    payload = json.loads(PALETTE_PATH.read_text(encoding="utf-8"))
    record = payload.get("colorsets", {}).get(colorset)
    if not isinstance(record, dict):
        raise ValueError(f"Unknown colorset: {colorset}")
    roles = record.get("roles")
    sequence = record.get("sequence")
    if not isinstance(roles, dict) or not isinstance(sequence, list):
        raise ValueError(f"Malformed palette record for {colorset}")
    return {"id": colorset, "name": record["name"], "roles": roles, "sequence": sequence}


def normalize_items(texts: list[str], variants: list[str]) -> list[dict[str, str]]:
    if not texts:
        if variants:
            raise ValueError("--variant requires at least one --text")
        return [{"text": text, "variant": variant} for text, variant in DEFAULT_ITEMS]

    cleaned: list[str] = []
    for raw in texts:
        text = " ".join(raw.split())
        if not text:
            raise ValueError("--text values must contain visible characters")
        if len(text) > 40:
            raise ValueError("--text values must be 40 characters or fewer")
        cleaned.append(text)
    if len(cleaned) > 8:
        raise ValueError("At most eight --text values are supported")

    if not variants:
        variants = ["hybrid"] * len(cleaned)
    elif len(variants) == 1:
        variants = variants * len(cleaned)
    elif len(variants) != len(cleaned):
        raise ValueError("Repeat --variant once, or provide exactly one variant per --text")

    return [{"text": text, "variant": variant} for text, variant in zip(cleaned, variants, strict=True)]


def initial_font_size(text: str) -> int:
    estimated = int(640 / max(3.5, len(text) * 0.64))
    return max(42, min(126, estimated))


def build_cards(items: list[dict[str, str]], colorset: str, roles: dict[str, str]) -> str:
    descriptions = {
        "tiles": "Square tiles reconstruct the glyph silhouette, then rotate and scatter on activation.",
        "lines": "Short line segments reconstruct the glyph silhouette, then slide and sweep on activation.",
        "dots": "Dots reconstruct the glyph silhouette, then move through offset orbital phases on activation.",
        "hybrid": "Squares, line segments, and dots reconstruct the same glyph silhouette, then move with distinct material behaviors.",
    }
    cards: list[str] = []
    for index, item in enumerate(items, start=1):
        text = escape(item["text"])
        attribute_text = escape(item["text"], quote=True)
        variant = item["variant"]
        label = variant.capitalize()
        title_id = f"kinetic-title-{index}"
        desc_id = f"kinetic-desc-{index}"
        svg_id = f"kinetic-word-{index}"
        font_size = initial_font_size(item["text"])
        cards.append(
            f'''        <button class="kinetic-word" type="button" data-card-index="{index - 1}" data-variant="{variant}" data-text="{attribute_text}" aria-pressed="false" aria-label="Reveal {label.lower()} structure in {attribute_text}">
          <svg id="{svg_id}" viewBox="0 0 720 220" role="img" aria-labelledby="{title_id} {desc_id}" data-pattern-id="{PATTERN_ID}" data-colorset="{colorset}" data-variant="{variant}" font-family="Open Sans, Arial, sans-serif">
            <title id="{title_id}">{text}: {label} kinetic type</title>
            <desc id="{desc_id}">{escape(descriptions[variant])} Hover, focus, or press to reveal the structure.</desc>
            <rect class="word-surface" x="1" y="1" width="718" height="218" fill="{roles['surface']}" stroke="{roles['line']}"/>
            <text class="base-text" x="360" y="154" text-anchor="middle" font-size="{font_size}" font-weight="900" fill="{roles['inkDark']}">{text}</text>
            <g class="piece-layer" aria-hidden="true"></g>
            <text class="material-label" x="24" y="202" font-size="12" font-weight="700" fill="{roles['muted']}">{label} · hover, focus, or tap</text>
          </svg>
        </button>'''
        )
    return "\n".join(cards)


def script_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def build_document(
    *,
    items: list[dict[str, str]],
    title: str,
    colorset: str,
    motion: str,
    seed: int,
) -> str:
    palette = load_palette(colorset)
    roles = palette["roles"]
    runtime = D3_RUNTIME_PATH.read_text(encoding="utf-8")
    if "</script" in runtime.lower():
        raise ValueError("Bundled D3 runtime unexpectedly contains a closing script tag")

    config = {
        "patternId": PATTERN_ID,
        "colorset": colorset,
        "motion": motion,
        "seed": seed,
        "width": 720,
        "height": 220,
        "baseline": 154,
        "sampleBottom": 178,
        "palette": palette,
        "items": [
            {
                **item,
                "index": index,
                "fontSize": initial_font_size(item["text"]),
                "svgId": f"kinetic-word-{index + 1}",
            }
            for index, item in enumerate(items)
        ],
    }

    template = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="pattern-id" content="__PATTERN_ID__">
  <link rel="icon" href="data:,">
  <title>__TITLE__</title>
  <style>
    :root {
      color-scheme: light;
      --background: __BACKGROUND__;
      --surface: __SURFACE__;
      --ink: __INK__;
      --ink-dark: __INK_DARK__;
      --primary: __PRIMARY__;
      --primary-dark: __PRIMARY_DARK__;
      --accent: __ACCENT__;
      --accent-soft: __ACCENT_SOFT__;
      --secondary: __SECONDARY__;
      --tertiary: __TERTIARY__;
      --positive: __POSITIVE__;
      --special: __SPECIAL__;
      --muted: __MUTED__;
      --line: __LINE__;
      --quiet: __QUIET__;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-width: 320px;
      background: var(--background);
      color: var(--ink);
      font: 15px/1.5 "Open Sans", Arial, sans-serif;
    }
    main {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: clamp(34px, 6vw, 72px) 0 64px;
    }
    .eyebrow {
      margin: 0 0 10px;
      color: var(--primary);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .14em;
      text-transform: uppercase;
    }
    h1 {
      max-width: 900px;
      margin: 0;
      color: var(--ink-dark);
      font-size: clamp(36px, 6vw, 68px);
      line-height: .98;
      letter-spacing: -.04em;
    }
    .lede {
      max-width: 760px;
      margin: 18px 0 0;
      color: var(--muted);
      font-size: clamp(16px, 2vw, 19px);
    }
    .word-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-top: 32px;
    }
    .kinetic-word {
      display: block;
      width: 100%;
      min-width: 0;
      margin: 0;
      border: 1px solid var(--line);
      border-radius: 0;
      padding: 0;
      overflow: hidden;
      background: var(--surface);
      color: var(--ink);
      cursor: pointer;
      text-align: left;
      transition: border-color 160ms ease, transform 160ms ease;
    }
    .kinetic-word:hover,
    .kinetic-word.is-pinned { border-color: var(--primary); }
    .kinetic-word:hover { transform: translateY(-2px); }
    .kinetic-word:focus-visible {
      outline: 3px solid var(--accent);
      outline-offset: 3px;
    }
    .kinetic-word svg {
      display: block;
      width: 100%;
      height: auto;
      overflow: hidden;
      font-family: "Open Sans", Arial, sans-serif;
    }
    .base-text,
    .piece-layer {
      transition: opacity 180ms ease;
    }
    .base-text { opacity: 1; }
    .piece-layer {
      opacity: 0;
      pointer-events: none;
    }
    .piece-geometry {
      transform-box: fill-box;
      transform-origin: center;
      vector-effect: non-scaling-stroke;
      will-change: transform;
    }
    .piece--line {
      stroke-linecap: square;
      stroke-dasharray: 5 4;
    }
    .kinetic-word[data-variant="tiles"] .material-label { fill: var(--primary); }
    .kinetic-word[data-variant="lines"] .material-label { fill: var(--secondary); }
    .kinetic-word[data-variant="dots"] .material-label { fill: var(--positive); }
    .kinetic-word[data-variant="hybrid"] .material-label { fill: var(--special); }
    .kinetic-word:is(:hover, :focus-visible, .is-pinned) .base-text { opacity: .07; }
    .kinetic-word:is(:hover, :focus-visible, .is-pinned) .piece-layer { opacity: 1; }
    .kinetic-word:is(:hover, :focus-visible, .is-pinned) .piece--tile {
      animation: tile-break var(--duration) cubic-bezier(.2,.74,.2,1) var(--delay) infinite alternate both;
    }
    .kinetic-word:is(:hover, :focus-visible, .is-pinned) .piece--line {
      animation: line-sweep var(--duration) cubic-bezier(.22,.7,.2,1) var(--delay) infinite alternate both;
    }
    .kinetic-word:is(:hover, :focus-visible, .is-pinned) .piece--dot {
      animation: dot-orbit var(--duration) cubic-bezier(.3,.68,.24,1) var(--delay) infinite both;
    }
    @keyframes tile-break {
      0%, 12% { transform: translate(0, 0) rotate(0) scale(1); }
      62% { transform: translate(var(--dx), var(--dy)) rotate(var(--rot)) scale(var(--scale)); }
      100% { transform: translate(var(--dx2), var(--dy2)) rotate(calc(var(--rot) * -.42)) scale(.9); }
    }
    @keyframes line-sweep {
      0%, 12% { transform: translate(0, 0); stroke-dashoffset: 0; }
      58% { transform: translate(var(--dx), var(--dy)); stroke-dashoffset: var(--dash); }
      100% { transform: translate(var(--dx2), var(--dy2)); stroke-dashoffset: calc(var(--dash) * -1); }
    }
    @keyframes dot-orbit {
      0%, 12%, 100% { transform: translate(0, 0) scale(1); }
      42% { transform: translate(var(--dx), var(--dy)) scale(var(--scale)); }
      72% { transform: translate(var(--dx2), var(--dy2)) scale(.82); }
    }
    .hint {
      display: flex;
      flex-wrap: wrap;
      gap: 8px 18px;
      margin: 16px 0 0;
      color: var(--muted);
      font-size: 13px;
    }
    .hint strong { color: var(--primary); }
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }
    @media (max-width: 760px) {
      main { width: min(100% - 20px, 1180px); padding-top: 30px; }
      .word-grid { grid-template-columns: 1fr; }
    }
    @media (prefers-reduced-motion: reduce) {
      .kinetic-word,
      .base-text,
      .piece-layer { transition-duration: 1ms !important; }
      .kinetic-word:hover { transform: none; }
      .piece-geometry { animation: none !important; }
      .kinetic-word:is(:hover, :focus-visible, .is-pinned) .piece-layer { opacity: 1 !important; }
    }
  </style>
</head>
<body data-pattern-id="__PATTERN_ID__" data-colorset="__COLORSET__" data-motion="__MOTION__" data-seed="__SEED__" data-render-state="loading">
  <main>
    <header>
      <p class="eyebrow">D3 · Kinetic glyph mosaic</p>
      <h1>__TITLE__</h1>
      <p class="lede">These words read as ordinary type at rest. Hover, focus, or press a word to reveal the deterministic squares, segments, and dots sampled from its real glyph silhouette.</p>
    </header>
    <div class="word-grid" aria-label="Kinetic type material variants">
__CARDS__
    </div>
    <p class="hint"><span><strong>Hover</strong> to preview</span><span><strong>Tab</strong> to focus</span><span><strong>Press</strong> to pin or unpin</span></p>
    <p id="kinetic-status" class="sr-only" role="status" aria-live="polite"></p>
  </main>
  <script id="kinetic-type-data" type="application/json">__CONFIG__</script>
  <script id="d3-runtime">__D3_RUNTIME__</script>
  <script id="kinetic-type-runtime">
  (() => {
    "use strict";
    const config = JSON.parse(document.getElementById("kinetic-type-data").textContent);
    const width = config.width;
    const baseline = config.baseline;
    const amplitude = config.motion === "calm" ? 16 : 32;
    const fontFamily = '"Open Sans", Arial, sans-serif';
    const status = d3.select("#kinetic-status");

    function mix32(value) {
      let x = value >>> 0;
      x ^= x >>> 16;
      x = Math.imul(x, 0x7feb352d);
      x ^= x >>> 15;
      x = Math.imul(x, 0x846ca68b);
      x ^= x >>> 16;
      return x >>> 0;
    }

    function unit(index, salt, itemIndex) {
      return mix32(config.seed + index * 374761393 + salt * 668265263 + itemIndex * 2246822519) / 4294967295;
    }

    function fitFont(context, text, proposed) {
      let size = proposed;
      while (size > 42) {
        context.font = `900 ${size}px ${fontFamily}`;
        if (context.measureText(text).width <= 640) break;
        size -= 2;
      }
      return size;
    }

    function shapeFor(variant, index, itemIndex) {
      if (variant !== "hybrid") return variant === "tiles" ? "tile" : variant === "lines" ? "line" : "dot";
      const selector = unit(index, 31, itemIndex);
      return selector < .42 ? "tile" : selector < .74 ? "line" : "dot";
    }

    function sampleGlyph(item) {
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = 184;
      const context = canvas.getContext("2d", { willReadFrequently: true });
      const fontSize = fitFont(context, item.text, item.fontSize);
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.font = `900 ${fontSize}px ${fontFamily}`;
      context.textAlign = "center";
      context.textBaseline = "alphabetic";
      context.fillStyle = config.palette.roles.inkDark;
      context.fillText(item.text, width / 2, baseline);
      const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
      const step = item.variant === "dots" ? 8 : item.variant === "lines" ? 9 : 10;
      const pieces = [];
      let ordinal = 0;
      for (let y = 22; y <= config.sampleBottom; y += step) {
        for (let x = 20; x <= width - 20; x += step) {
          const alpha = pixels[(Math.floor(y) * canvas.width + Math.floor(x)) * 4 + 3];
          if (alpha < 56) continue;
          const shape = shapeFor(item.variant, ordinal, item.index);
          const rx = (x - width / 2) / (width / 2);
          const ry = (y - 100) / 100;
          const jitterX = (unit(ordinal, 3, item.index) - .5) * amplitude * 1.3;
          const jitterY = (unit(ordinal, 5, item.index) - .5) * amplitude * 1.05;
          const dx = rx * amplitude * .75 + jitterX;
          const dy = ry * amplitude * .55 + jitterY;
          const dx2 = -dy * .58 + (unit(ordinal, 7, item.index) - .5) * amplitude * .65;
          const dy2 = dx * .42 + (unit(ordinal, 11, item.index) - .5) * amplitude * .55;
          pieces.push({
            id: `${item.index}-${ordinal}`,
            index: ordinal,
            x,
            y,
            step,
            shape,
            dx,
            dy,
            dx2,
            dy2,
            rotation: (unit(ordinal, 13, item.index) - .5) * 150,
            scale: .72 + unit(ordinal, 17, item.index) * .58,
            duration: 1080 + unit(ordinal, 19, item.index) * 820,
            delay: unit(ordinal, 23, item.index) * 150,
            angle: (unit(ordinal, 29, item.index) - .5) * 78,
            colorIndex: Math.floor(unit(ordinal, 37, item.index) * config.palette.sequence.length)
          });
          ordinal += 1;
        }
      }
      return { fontSize, pieces };
    }

    function appendGeometry(selection, piece, color) {
      if (piece.shape === "tile") {
        const size = piece.step * .88;
        selection.append("rect")
          .attr("class", "piece-geometry piece--tile")
          .attr("x", -size / 2)
          .attr("y", -size / 2)
          .attr("width", size)
          .attr("height", size)
          .attr("fill", color);
        return;
      }
      if (piece.shape === "line") {
        const length = piece.step * 1.52;
        const radians = piece.angle * Math.PI / 180;
        const vx = Math.cos(radians) * length / 2;
        const vy = Math.sin(radians) * length / 2;
        selection.append("line")
          .attr("class", "piece-geometry piece--line")
          .attr("x1", -vx)
          .attr("y1", -vy)
          .attr("x2", vx)
          .attr("y2", vy)
          .attr("stroke", color)
          .attr("stroke-width", 3.4);
        return;
      }
      selection.append("circle")
        .attr("class", "piece-geometry piece--dot")
        .attr("r", piece.step * .34)
        .attr("fill", color);
    }

    function renderItem(item) {
      const button = d3.select(`[data-card-index="${item.index}"]`).datum(item);
      const svg = button.select("svg");
      const sampled = sampleGlyph(item);
      svg.select(".base-text").attr("font-size", sampled.fontSize);
      const color = d3.scaleOrdinal(d3.range(config.palette.sequence.length), config.palette.sequence);
      const anchors = svg.select(".piece-layer")
        .selectAll("g.piece-anchor")
        .data(sampled.pieces, piece => piece.id)
        .join(
          enter => enter.append("g").attr("class", "piece-anchor"),
          update => update,
          exit => exit.remove()
        )
        .attr("transform", piece => `translate(${piece.x},${piece.y})`)
        .attr("data-piece-id", piece => piece.id)
        .attr("data-shape", piece => piece.shape);

      anchors.each(function(piece) {
        const anchor = d3.select(this);
        anchor.selectAll("*").remove();
        appendGeometry(anchor, piece, color(piece.colorIndex));
        anchor.select(".piece-geometry")
          .style("--dx", `${piece.dx.toFixed(2)}px`)
          .style("--dy", `${piece.dy.toFixed(2)}px`)
          .style("--dx2", `${piece.dx2.toFixed(2)}px`)
          .style("--dy2", `${piece.dy2.toFixed(2)}px`)
          .style("--rot", `${piece.rotation.toFixed(2)}deg`)
          .style("--scale", piece.scale.toFixed(3))
          .style("--duration", `${piece.duration.toFixed(0)}ms`)
          .style("--delay", `${piece.delay.toFixed(0)}ms`)
          .style("--dash", `${(piece.step * 1.8).toFixed(1)}px`);
      });

      const shapeCounts = d3.rollup(sampled.pieces, values => values.length, piece => piece.shape);
      svg.attr("data-piece-count", sampled.pieces.length)
        .attr("data-tile-count", shapeCounts.get("tile") || 0)
        .attr("data-line-count", shapeCounts.get("line") || 0)
        .attr("data-dot-count", shapeCounts.get("dot") || 0)
        .attr("data-font-size", sampled.fontSize);
      return {
        index: item.index,
        text: item.text,
        variant: item.variant,
        pieceCount: sampled.pieces.length,
        tileCount: shapeCounts.get("tile") || 0,
        lineCount: shapeCounts.get("line") || 0,
        dotCount: shapeCounts.get("dot") || 0,
        fontSize: sampled.fontSize
      };
    }

    function bindInteraction() {
      d3.selectAll(".kinetic-word").on("click.kinetic-type", function(event, item) {
        const button = d3.select(this);
        const pinned = !button.classed("is-pinned");
        button.classed("is-pinned", pinned).attr("aria-pressed", pinned ? "true" : "false");
        status.text(`${item.text} ${pinned ? "pinned open" : "returned to normal type"}.`);
      });
    }

    function renderAll() {
      const cards = config.items.map(renderItem);
      bindInteraction();
      document.body.dataset.renderState = "ready";
      window.__kineticTypeDiagnostics = {
        ready: true,
        patternId: config.patternId,
        colorset: config.colorset,
        motion: config.motion,
        seed: config.seed,
        cards
      };
      window.__kineticTypeSetPinned = (index, pinned) => {
        const button = d3.select(`[data-card-index="${index}"]`);
        button.classed("is-pinned", Boolean(pinned)).attr("aria-pressed", pinned ? "true" : "false");
      };
    }

    const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
    fontsReady.then(renderAll).catch(error => {
      document.body.dataset.renderState = "error";
      window.__kineticTypeDiagnostics = { ready: false, error: String(error) };
      throw error;
    });
  })();
  </script>
</body>
</html>
'''

    replacements = {
        "__PATTERN_ID__": PATTERN_ID,
        "__TITLE__": escape(title),
        "__BACKGROUND__": roles["background"],
        "__SURFACE__": roles["surface"],
        "__INK__": roles["ink"],
        "__INK_DARK__": roles["inkDark"],
        "__PRIMARY__": roles["primary"],
        "__PRIMARY_DARK__": roles["primaryDark"],
        "__ACCENT__": roles["accent"],
        "__ACCENT_SOFT__": roles["accentSoft"],
        "__SECONDARY__": roles.get("secondary", roles["primaryDark"]),
        "__TERTIARY__": roles.get("tertiary", roles["primary"]),
        "__POSITIVE__": roles.get("positive", roles["ink"]),
        "__SPECIAL__": roles.get("special", roles["accent"]),
        "__MUTED__": roles["muted"],
        "__LINE__": roles["line"],
        "__QUIET__": roles["quiet"],
        "__COLORSET__": colorset,
        "__MOTION__": motion,
        "__SEED__": str(seed),
        "__CARDS__": build_cards(items, colorset, roles),
        "__CONFIG__": script_json(config),
        "__D3_RUNTIME__": runtime,
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    remaining = sorted({token for token in template.split() if token.startswith("__") and token.endswith("__")})
    if remaining:
        raise ValueError(f"Unresolved template placeholders: {remaining}")
    return template


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build an offline D3 page where ordinary text reveals deterministic tile, line, dot, "
            "or hybrid glyph components on hover, keyboard focus, or press."
        )
    )
    parser.add_argument("output", type=Path, help="Exact output HTML path.")
    parser.add_argument(
        "--text",
        action="append",
        default=[],
        metavar="TEXT",
        help="Text to render; repeat for multiple cards. Defaults to a four-material showcase.",
    )
    parser.add_argument(
        "--variant",
        action="append",
        choices=VARIANTS,
        default=[],
        help="Material for the matching --text; repeat once or once per text. Custom text defaults to hybrid.",
    )
    parser.add_argument("--title", default="Type has an inner life", help="Visible page title.")
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    parser.add_argument("--motion", choices=("calm", "energetic"), default="energetic")
    parser.add_argument("--seed", type=int, default=37, help="Deterministic integer motion seed.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    try:
        items = normalize_items(args.text, args.variant)
        document = build_document(
            items=items,
            title=args.title,
            colorset=args.colorset,
            motion=args.motion,
            seed=args.seed,
        )
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.error(str(error))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8", newline="\n")
    print(f"Wrote kinetic type HTML: {args.output}")
    print(f"Pattern ID: {PATTERN_ID}; cards: {len(items)}; colorset: {args.colorset}; motion: {args.motion}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
