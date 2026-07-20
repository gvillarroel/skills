#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Build deterministic, standalone procedural SVG animations.

The bundled pattern catalog is the source of truth.  Each catalog renderer owns
six variants, while this script supplies the deterministic geometry, motion,
metadata, and exact-path CLI used by the skill at runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
from dataclasses import dataclass, replace
from html import escape
from pathlib import Path
from typing import Callable, Iterable, Sequence, TypeVar


for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="backslashreplace")


SKILL_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = SKILL_ROOT / "assets" / "pattern-specs.json"
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

PALETTES: dict[str, dict[str, str | list[str]]] = {
    "colorset1": {
        "background": "#f7f7f7",
        "surface": "#ffffff",
        "ink": "#333e48",
        "muted": "#696969",
        "line": "#cfcfcf",
        "soft": "#e7e7e7",
        "highlight": "#ffccd5",
        "accents": ["#9e1b32", "#6d1222", "#696969", "#9f9f9f", "#333e48", "#cfcfcf"],
    },
    "colorset2": {
        "background": "#f7f7f7",
        "surface": "#ffffff",
        "ink": "#333e48",
        "muted": "#696969",
        "line": "#cfcfcf",
        "soft": "#e7e7e7",
        "highlight": "#cdf3ff",
        "accents": ["#9e1b32", "#e77204", "#f1c319", "#45842a", "#007298", "#652f6c"],
    },
}


@dataclass(frozen=True)
class Context:
    spec: dict[str, object]
    seed: int
    width: int
    height: int
    duration_ms: int
    palette_name: str
    palette: dict[str, str | list[str]]
    motion: str
    id_suffix: str = ""

    @property
    def full_motion(self) -> bool:
        return self.motion == "full"

    @property
    def duration_s(self) -> str:
        return f"{self.duration_ms / 1000:.3f}s"

    @property
    def left(self) -> float:
        return 40.0

    @property
    def right(self) -> float:
        return self.width - 40.0

    @property
    def top(self) -> float:
        return 112.0

    @property
    def bottom(self) -> float:
        return self.height - 44.0

    @property
    def art_width(self) -> float:
        return self.right - self.left

    @property
    def art_height(self) -> float:
        return self.bottom - self.top

    @property
    def accents(self) -> list[str]:
        return list(self.palette["accents"])  # type: ignore[arg-type]

    def color(self, index: int) -> str:
        colors = self.accents
        return colors[index % len(colors)]

    def rng(self, label: str = "geometry") -> random.Random:
        raw = f"{self.seed}|{self.spec['id']}|{label}".encode("utf-8")
        value = int.from_bytes(hashlib.sha256(raw).digest()[:16], "big")
        return random.Random(value)

    def ident(self, base: str) -> str:
        return f"{base}{self.id_suffix}"


def fmt(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError(f"Non-finite geometry value: {value!r}")
    rounded = round(value, 3)
    if rounded == 0:
        rounded = 0
    return f"{rounded:.3f}".rstrip("0").rstrip(".")


def slug_from_pattern(pattern_id: str) -> str:
    prefix = "procedural-svg-"
    return pattern_id[len(prefix) :] if pattern_id.startswith(prefix) else pattern_id


def path_from_points(points: Iterable[tuple[float, float]], close: bool = False) -> str:
    values = list(points)
    if not values:
        return ""
    command = [f"M {fmt(values[0][0])} {fmt(values[0][1])}"]
    command.extend(f"L {fmt(x)} {fmt(y)}" for x, y in values[1:])
    if close:
        command.append("Z")
    return " ".join(command)


def smooth_path(points: Sequence[tuple[float, float]], close: bool = False) -> str:
    if len(points) < 2:
        return path_from_points(points, close)
    parts = [f"M {fmt(points[0][0])} {fmt(points[0][1])}"]
    limit = len(points) if close else len(points) - 1
    for index in range(limit):
        current = points[index % len(points)]
        following = points[(index + 1) % len(points)]
        midpoint = ((current[0] + following[0]) / 2, (current[1] + following[1]) / 2)
        parts.append(f"Q {fmt(current[0])} {fmt(current[1])} {fmt(midpoint[0])} {fmt(midpoint[1])}")
    if not close:
        parts.append(f"L {fmt(points[-1][0])} {fmt(points[-1][1])}")
    else:
        parts.append("Z")
    return " ".join(parts)


def regular_polygon(cx: float, cy: float, radius: float, sides: int, rotation: float = -math.pi / 2) -> str:
    points = [
        (cx + radius * math.cos(rotation + index * math.tau / sides), cy + radius * math.sin(rotation + index * math.tau / sides))
        for index in range(sides)
    ]
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def smil(ctx: Context, markup: str) -> str:
    if not ctx.full_motion:
        return ""
    # One master duration makes every declarative animation return to the same
    # phase at the SVG loop boundary. Numeric positive begins become negative
    # phase offsets so there is no one-time startup state.
    markup = re.sub(r'dur="[^"]+"', f'dur="{ctx.duration_s}"', markup)

    def phase_offset(match: re.Match[str]) -> str:
        value = float(match.group(1))
        return f'begin="{fmt(-value) if value > 0 else fmt(value)}s"'

    markup = re.sub(r'begin="([+-]?(?:\d+(?:\.\d*)?|\.\d+))s"', phase_offset, markup)
    auto_oriented_ping_pong = (
        markup.startswith("<animateMotion")
        and "keyPoints=" not in markup
        and 'rotate="auto"' in markup
    )
    if markup.startswith("<animateMotion") and "keyPoints=" not in markup:
        markup = markup.replace(
            "<animateMotion ",
            '<animateMotion keyPoints="0;1;0" keyTimes="0;0.5;1" calcMode="linear" ',
            1,
        )
    if auto_oriented_ping_pong:
        # An auto-oriented marker reverses direction at the path endpoints.
        # Hide the narrow reversal windows so the 180-degree heading change is
        # never exposed at the midpoint or master-loop seam.
        begin_match = re.search(r'begin="([^"]+)"', markup)
        fade_begin = f' begin="{begin_match.group(1)}"' if begin_match else ""
        markup += (
            f'<animate attributeName="opacity" values="0;1;1;0;0;1;1;0" '
            'keyTimes="0;.04;.46;.5;.54;.58;.96;1" '
            f'dur="{ctx.duration_s}"{fade_begin} repeatCount="indefinite"/>'
        )
    return markup


def css_animation(ctx: Context, name: str, duration_factor: float = 1.0, delay_ms: int = 0, timing: str = "ease-in-out") -> str:
    if not ctx.full_motion:
        return ""
    # Quantize requested speed variants to an integer number of cycles inside
    # the master duration. Arbitrary child periods cannot form a seamless loop.
    cycles = max(1, round(1 / max(duration_factor, 1e-9)))
    duration = ctx.duration_ms / cycles
    return f"animation:{name} {fmt(duration)}ms {timing} {delay_ms}ms infinite both"


def load_catalog() -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read procedural pattern catalog: {error}") from error
    if not isinstance(catalog, dict) or not isinstance(catalog.get("patterns"), list):
        raise RuntimeError("Pattern catalog must contain a patterns array.")
    patterns: dict[str, dict[str, object]] = {}
    renderers: set[str] = set()
    for raw in catalog["patterns"]:  # type: ignore[index]
        if not isinstance(raw, dict):
            raise RuntimeError("Every pattern catalog entry must be an object.")
        pattern_id = raw.get("id")
        renderer = raw.get("renderer")
        variant = raw.get("variant")
        if not isinstance(pattern_id, str) or not re.fullmatch(r"procedural-svg-[a-z0-9]+(?:-[a-z0-9]+)*", pattern_id):
            raise RuntimeError(f"Invalid procedural pattern ID: {pattern_id!r}")
        if pattern_id in patterns:
            raise RuntimeError(f"Duplicate procedural pattern ID: {pattern_id}")
        if not isinstance(renderer, str) or not renderer:
            raise RuntimeError(f"Pattern {pattern_id} is missing a renderer.")
        if not isinstance(variant, int) or variant not in range(6):
            raise RuntimeError(f"Pattern {pattern_id} must use variant 0..5.")
        patterns[pattern_id] = raw
        renderers.add(renderer)
    if len(patterns) != 60 or len(renderers) != 10:
        raise RuntimeError(f"Expected 60 patterns and 10 renderers, found {len(patterns)} and {len(renderers)}.")
    return catalog, patterns


def panel_frame(ctx: Context, body: str, note: str = "") -> str:
    x, y, width, height = ctx.left, ctx.top, ctx.art_width, ctx.art_height
    note_markup = ""
    if note:
        note_markup = (
            f'<text class="psvg-note" x="{fmt(x + 18)}" y="{fmt(y + height - 16)}">'
            f"{escape(note)}</text>"
        )
    return (
        f'<rect class="psvg-panel" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(width)}" height="{fmt(height)}" rx="12"/>'
        f'<g class="psvg-art" data-role="procedural-art">{body}</g>{note_markup}'
    )


def render_timing(ctx: Context) -> str:
    variant = int(ctx.spec["variant"])
    x0, y0, aw, ah = ctx.left, ctx.top, ctx.art_width, ctx.art_height
    body: list[str] = []
    if variant in (0, 1):
        rows, columns = 6, 11
        gap_x, gap_y = aw / (columns + 1), (ah - 38) / (rows + 1)
        for row in range(rows):
            for column in range(columns):
                cx, cy = x0 + gap_x * (column + 1), y0 + gap_y * (row + 1)
                delay = -int(ctx.duration_ms * ((row + column) / (rows + columns)))
                color = ctx.color(row + column)
                if variant == 0:
                    style = css_animation(ctx, "psvg-wave", 1.0, delay)
                    body.append(f'<circle class="psvg-cell" cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(min(gap_x, gap_y) * .24)}" fill="{color}" style="{style}"/>')
                else:
                    animate = smil(ctx, f'<animate attributeName="opacity" values="0.28;1;0.28" dur="{ctx.duration_s}" begin="{fmt((row + column) * ctx.duration_ms / 1000 / 24)}s" repeatCount="indefinite"/>')
                    body.append(f'<rect class="psvg-cell" x="{fmt(cx - 7)}" y="{fmt(cy - 7)}" width="14" height="14" rx="3" fill="{color}" opacity="0.65">{animate}</rect>')
    elif variant == 2:
        profiles = [
            ("linear", "psvg-travel", "linear"),
            ("symmetric ease", "psvg-travel", "ease-in-out"),
            ("overshoot", "psvg-travel-overshoot", "linear"),
            ("steps", "psvg-travel", "steps(5,end)"),
            ("asymmetric", "psvg-travel-asymmetric", "linear"),
        ]
        for index, (label, animation_name, timing) in enumerate(profiles):
            y = y0 + 52 + index * (ah - 86) / (len(profiles) - 1)
            body.append(f'<line x1="{fmt(x0 + 142)}" y1="{fmt(y)}" x2="{fmt(x0 + aw - 44)}" y2="{fmt(y)}" class="psvg-guide"/>')
            body.append(f'<text x="{fmt(x0 + 24)}" y="{fmt(y + 5)}" class="psvg-label">{label}</text>')
            style = css_animation(ctx, animation_name, 1.0, 0, timing)
            body.append(f'<circle cx="{fmt(x0 + 154)}" cy="{fmt(y)}" r="10" fill="{ctx.color(index)}" style="{style};--psvg-distance:{fmt(aw - 212)}px"/>')
    elif variant == 3:
        cx, cy, radius = x0 + aw / 2, y0 + ah / 2, min(aw, ah) * .32
        count = 8
        key_times = ";".join(fmt(index / count) for index in range(count + 1))
        for index in range(count):
            angle = -math.pi / 2 + index * math.tau / count
            nx, ny = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
            nnx, nny = cx + radius * math.cos(angle + math.tau / count), cy + radius * math.sin(angle + math.tau / count)
            body.append(f'<path d="M {fmt(nx)} {fmt(ny)} Q {fmt(cx)} {fmt(cy)} {fmt(nnx)} {fmt(nny)}" class="psvg-guide"/>')
            radii = ["21" if step % count == index else "12" for step in range(count + 1)]
            opacities = ["1" if step % count == index else ".38" for step in range(count + 1)]
            radius_animation = smil(
                ctx,
                f'<animate attributeName="r" values="{";".join(radii)}" keyTimes="{key_times}" calcMode="discrete" dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            opacity_animation = smil(
                ctx,
                f'<animate attributeName="opacity" values="{";".join(opacities)}" keyTimes="{key_times}" calcMode="discrete" dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            base_radius = 21 if index == 0 else 12
            base_opacity = 1 if index == 0 else .38
            body.append(
                f'<circle cx="{fmt(nx)}" cy="{fmt(ny)}" r="{base_radius}" opacity="{fmt(base_opacity)}" fill="{ctx.color(index)}">'
                f'{radius_animation}{opacity_animation}</circle>'
            )
            body.append(f'<text x="{fmt(nx)}" y="{fmt(ny + 4)}" text-anchor="middle" class="psvg-node-label">{index + 1}</text>')
        body.append(f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="44" fill="{ctx.palette["highlight"]}" stroke="{ctx.color(0)}" stroke-width="2"/><text x="{fmt(cx)}" y="{fmt(cy + 5)}" text-anchor="middle" class="psvg-label">CLOCK</text>')
    elif variant == 4:
        cx, cy = x0 + aw / 2, y0 + ah / 2
        for layer in range(2):
            points = []
            for index in range(121):
                t = index / 120 * math.tau
                radius = min(aw, ah) * (.2 + .045 * math.sin(5 * t + layer * math.pi))
                points.append((cx + radius * math.cos(t), cy + radius * math.sin(t)))
            style = css_animation(ctx, "psvg-crossfade-a" if layer == 0 else "psvg-crossfade-b", 1.0)
            body.append(f'<path d="{path_from_points(points, True)}" fill="{ctx.color(layer + 3)}" opacity="0.62" style="{style}"/>')
        body.append(f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="10" fill="{ctx.palette["surface"]}" stroke="{ctx.palette["ink"]}"/>')
    else:
        count = 10
        base_y = y0 + ah / 2
        start_x, step = x0 + 70, (aw - 140) / (count - 1)
        displacement = [0.0] * count
        velocity = [0.0] * count
        displacement[0] = -52.0
        raw_frames: list[list[float]] = []
        omega, damping_ratio, coupling, dt = 2.25, .16, 5.2, .045
        for _frame in range(42):
            raw_frames.append(list(displacement))
            for _substep in range(4):
                acceleration: list[float] = []
                for index in range(count):
                    neighbor_force = 0.0
                    if index:
                        neighbor_force += displacement[index - 1] - displacement[index]
                    if index + 1 < count:
                        neighbor_force += displacement[index + 1] - displacement[index]
                    acceleration.append(
                        -(omega * omega) * displacement[index]
                        - 2 * damping_ratio * omega * velocity[index]
                        + coupling * neighbor_force
                    )
                for index in range(count):
                    velocity[index] += acceleration[index] * dt
                    displacement[index] += velocity[index] * dt
        frames = ping_pong_frames(raw_frames)
        key_times = ";".join(fmt(index / (len(frames) - 1)) for index in range(len(frames)))
        display_frame = frames[0] if ctx.full_motion else raw_frames[len(raw_frames) // 3]
        point_frames = [
            " ".join(f"{fmt(start_x + index * step)},{fmt(base_y + frame[index])}" for index in range(count))
            for frame in frames
        ]
        display_points = " ".join(
            f"{fmt(start_x + index * step)},{fmt(base_y + display_frame[index])}" for index in range(count)
        )
        link_animation = smil(
            ctx,
            f'<animate attributeName="points" values="{";".join(point_frames)}" keyTimes="{key_times}" '
            f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
        )
        body.append(f'<polyline points="{display_points}" fill="none" stroke="{ctx.palette["line"]}" stroke-width="3">{link_animation}</polyline>')
        for index in range(count):
            cx = start_x + index * step
            y_values = ";".join(fmt(base_y + frame[index]) for frame in frames)
            animate = smil(ctx, f'<animate attributeName="cy" values="{y_values}" keyTimes="{key_times}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<circle cx="{fmt(cx)}" cy="{fmt(base_y + display_frame[index])}" r="{fmt(7 + index * .45)}" fill="{ctx.color(index)}">{animate}</circle>')
    return panel_frame(ctx, "".join(body), str(ctx.spec["signature"]))


def render_transform(ctx: Context) -> str:
    variant = int(ctx.spec["variant"])
    x0, y0, aw, ah = ctx.left, ctx.top, ctx.art_width, ctx.art_height
    cx, cy = x0 + aw / 2, y0 + ah / 2
    body: list[str] = []
    if variant == 0:
        radii = [min(aw, ah) * value for value in (.25, .115, .055)]
        phases = [0.0, 38.0, -27.0]
        relative_turns = [1, -3, 5]
        chain = [f'<g transform="translate({fmt(cx)} {fmt(cy)})">']
        chain.append(f'<circle cx="0" cy="0" r="22" fill="{ctx.color(0)}"/>')
        for index, (radius, phase, turns) in enumerate(zip(radii, phases, relative_turns)):
            animate = smil(
                ctx,
                f'<animateTransform attributeName="transform" type="rotate" from="{fmt(phase)}" to="{fmt(phase + turns * 360)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            chain.append(
                f'<circle cx="0" cy="0" r="{fmt(radius)}" fill="none" class="psvg-guide"/>'
                f'<g transform="rotate({fmt(phase)})">{animate}'
                f'<g transform="translate({fmt(radius)} 0)">'
                f'<circle cx="0" cy="0" r="{fmt(15 - index * 3)}" fill="{ctx.color(index + 2)}"/>'
            )
        chain.append('</g></g>' * len(radii))
        chain.append('</g>')
        body.append("".join(chain))
    elif variant == 1:
        radius = min(aw, ah) * .31
        animate_parent = smil(ctx, f'<animateTransform attributeName="transform" type="rotate" from="0 {fmt(cx)} {fmt(cy)}" to="360 {fmt(cx)} {fmt(cy)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
        body.append(f'<g>{animate_parent}<polygon points="{regular_polygon(cx, cy, radius, 8)}" fill="none" stroke="{ctx.color(4)}" stroke-width="3"/>')
        for index in range(8):
            angle = index * math.tau / 8 - math.pi / 2
            tx, ty = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
            inverse = smil(ctx, f'<animateTransform attributeName="transform" type="rotate" from="0 {fmt(tx)} {fmt(ty)}" to="-360 {fmt(tx)} {fmt(ty)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<g>{inverse}<rect x="{fmt(tx - 26)}" y="{fmt(ty - 13)}" width="52" height="26" rx="7" fill="{ctx.palette["surface"]}" stroke="{ctx.color(index)}"/><text x="{fmt(tx)}" y="{fmt(ty + 4)}" text-anchor="middle" class="psvg-node-label">UP</text></g>')
        body.append('</g>')
    elif variant == 2:
        count = 13
        top_y = y0 + 42
        gap = (aw - 100) / (count - 1)
        length = min(ah * .52, gap * 4.2)
        sample_count = 48
        key_times = ";".join(fmt(sample / sample_count) for sample in range(sample_count + 1))
        for index in range(count):
            px = x0 + 50 + index * gap
            frequency = index + 5
            amplitude = 19 + 8 * math.sin((index + 1) * .47) ** 2
            angles = [
                f'{fmt(amplitude * math.sin(math.tau * frequency * sample / sample_count))} {fmt(px)} {fmt(top_y)}'
                for sample in range(sample_count + 1)
            ]
            animate = smil(
                ctx,
                f'<animateTransform attributeName="transform" type="rotate" values="{";".join(angles)}" keyTimes="{key_times}" calcMode="linear" dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            body.append(f'<g>{animate}<line x1="{fmt(px)}" y1="{fmt(top_y)}" x2="{fmt(px)}" y2="{fmt(top_y + length)}" stroke="{ctx.palette["ink"]}" stroke-width="2"/><circle cx="{fmt(px)}" cy="{fmt(top_y + length)}" r="10" fill="{ctx.color(index)}"/></g>')
        body.append(f'<line x1="{fmt(x0 + 36)}" y1="{fmt(top_y)}" x2="{fmt(x0 + aw - 36)}" y2="{fmt(top_y)}" stroke="{ctx.palette["line"]}" stroke-width="4"/>')
    elif variant == 3:
        tooth_counts = [12, 8, 6]
        normalized_width = 27.1
        module = min(aw * .76 / normalized_width, ah * .72 / 13.1)
        pitch_radii = [module * teeth / 2 for teeth in tooth_counts]
        center_span = pitch_radii[0] + 2 * pitch_radii[1] + pitch_radii[2]
        first_x = cx - center_span / 2
        centers = [
            first_x,
            first_x + pitch_radii[0] + pitch_radii[1],
            first_x + pitch_radii[0] + 2 * pitch_radii[1] + pitch_radii[2],
        ]
        base_phases = [0.0, math.pi - math.pi / tooth_counts[1], math.pi]
        closure_turns = math.lcm(*tooth_counts)
        for index, (gx, pitch_radius, teeth, base_phase) in enumerate(zip(centers, pitch_radii, tooth_counts, base_phases)):
            gy = cy
            outer_radius = pitch_radius + module * .55
            root_radius = pitch_radius - module * .48
            points: list[tuple[float, float]] = []
            for tooth in range(teeth * 2):
                angle = base_phase + tooth * math.pi / teeth
                rr = outer_radius if tooth % 2 == 0 else root_radius
                points.append((gx + rr * math.cos(angle), gy + rr * math.sin(angle)))
            turns = closure_turns // teeth
            degrees = 360 * turns * (1 if index % 2 == 0 else -1)
            animate = smil(ctx, f'<animateTransform attributeName="transform" type="rotate" from="0 {fmt(gx)} {fmt(gy)}" to="{degrees} {fmt(gx)} {fmt(gy)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<circle cx="{fmt(gx)}" cy="{fmt(gy)}" r="{fmt(pitch_radius)}" fill="none" class="psvg-guide"/>')
            body.append(
                f'<g>{animate}<path d="{path_from_points(points, True)}" fill="{ctx.color(index + 1)}" stroke="{ctx.palette["ink"]}" stroke-width="2"/>'
                f'<circle cx="{fmt(gx)}" cy="{fmt(gy)}" r="{fmt(module * 1.05)}" fill="{ctx.palette["surface"]}" stroke="{ctx.palette["ink"]}" stroke-width="2"/></g>'
            )
            body.append(f'<text x="{fmt(gx)}" y="{fmt(gy + 5)}" text-anchor="middle" class="psvg-node-label">{teeth}</text>')
    elif variant == 4:
        base_x, base_y = x0 + aw * .28, y0 + ah * .78
        lengths = [aw * .22, aw * .18, aw * .14]
        angles = [-52, 62, -42]
        body.append(f'<circle cx="{fmt(base_x)}" cy="{fmt(base_y)}" r="28" fill="{ctx.palette["soft"]}" stroke="{ctx.palette["ink"]}"/>')
        chain = [f'<g transform="translate({fmt(base_x)} {fmt(base_y)})">']
        for index, (length, angle) in enumerate(zip(lengths, angles)):
            animate = smil(ctx, f'<animateTransform attributeName="transform" type="rotate" values="{angle - 18};{angle + 18};{angle - 18}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            chain.append(
                f'<g transform="rotate({angle})">{animate}'
                f'<line x1="0" y1="0" x2="{fmt(length)}" y2="0" stroke="{ctx.color(index + 3)}" stroke-width="16" stroke-linecap="round"/>'
                f'<circle cx="0" cy="0" r="10" fill="{ctx.palette["surface"]}" stroke="{ctx.palette["ink"]}"/>'
                f'<g transform="translate({fmt(length)} 0)">'
            )
        chain.append(f'<circle cx="0" cy="0" r="16" fill="{ctx.color(0)}" stroke="{ctx.palette["surface"]}" stroke-width="3"/>')
        chain.append('</g></g>' * len(lengths))
        chain.append('</g>')
        body.append("".join(chain))
    else:
        rng = ctx.rng("parallax")
        for layer in range(4):
            baseline = y0 + ah * (.3 + layer * .16)
            points = [(x0 - 80, y0 + ah)]
            for index in range(9):
                x = x0 - 40 + index * (aw + 80) / 8
                y = baseline + rng.uniform(-32, 24) * (1 + layer * .15)
                points.append((x, y))
            points.extend([(x0 + aw + 80, y0 + ah), (x0 - 80, y0 + ah)])
            style = css_animation(ctx, "psvg-parallax", 1.0 + layer * .35, -layer * 220, "linear")
            body.append(f'<path d="{smooth_path(points, True)}" fill="{ctx.color(5 - layer)}" opacity="{fmt(.22 + layer * .14)}" style="{style};--psvg-shift:{fmt(18 + layer * 18)}px"/>')
    return panel_frame(ctx, "".join(body), str(ctx.spec["signature"]))


def render_path(ctx: Context) -> str:
    variant = int(ctx.spec["variant"])
    x0, y0, aw, ah = ctx.left, ctx.top, ctx.art_width, ctx.art_height
    body: list[str] = []
    route = f"M {fmt(x0 + 48)} {fmt(y0 + ah * .7)} C {fmt(x0 + aw * .2)} {fmt(y0 + ah * .08)}, {fmt(x0 + aw * .38)} {fmt(y0 + ah * .94)}, {fmt(x0 + aw * .54)} {fmt(y0 + ah * .42)} S {fmt(x0 + aw * .8)} {fmt(y0 + ah * .14)}, {fmt(x0 + aw - 48)} {fmt(y0 + ah * .55)}"
    if variant == 0:
        body.append(f'<path d="{route}" fill="none" stroke="{ctx.palette["soft"]}" stroke-width="10" stroke-linecap="round"/>')
        style = css_animation(ctx, "psvg-draw", 1.0, 0, "ease-in-out")
        body.append(f'<path d="{route}" pathLength="1" fill="none" stroke="{ctx.color(0)}" stroke-width="7" stroke-linecap="round" style="{style}"/>')
    elif variant == 1:
        for index in range(4):
            y_shift = (index - 1.5) * 34
            shifted = f"M {fmt(x0 + 46)} {fmt(y0 + ah * .5 + y_shift)} C {fmt(x0 + aw * .28)} {fmt(y0 + ah * .18 + y_shift)}, {fmt(x0 + aw * .64)} {fmt(y0 + ah * .82 + y_shift)}, {fmt(x0 + aw - 46)} {fmt(y0 + ah * .5 + y_shift)}"
            style = css_animation(ctx, "psvg-conveyor", .55 + index * .1, -index * 110, "linear")
            body.append(f'<path d="{shifted}" pathLength="1" fill="none" stroke="{ctx.color(index)}" stroke-width="5" stroke-dasharray=".055 .045" style="{style}"/>')
    elif variant == 2:
        route_id = ctx.ident(f"{slug_from_pattern(str(ctx.spec['id']))}-route")
        body.append(f'<path id="{route_id}" d="{route}" fill="none" stroke="{ctx.palette["line"]}" stroke-width="4"/>')

        def cubic_pose(control_points: Sequence[tuple[float, float]], t: float) -> tuple[float, float, float]:
            p0, p1, p2, p3 = control_points
            inverse = 1 - t
            px = inverse**3*p0[0] + 3*inverse*inverse*t*p1[0] + 3*inverse*t*t*p2[0] + t**3*p3[0]
            py = inverse**3*p0[1] + 3*inverse*inverse*t*p1[1] + 3*inverse*t*t*p2[1] + t**3*p3[1]
            dx = 3*inverse*inverse*(p1[0]-p0[0]) + 6*inverse*t*(p2[0]-p1[0]) + 3*t*t*(p3[0]-p2[0])
            dy = 3*inverse*inverse*(p1[1]-p0[1]) + 6*inverse*t*(p2[1]-p1[1]) + 3*t*t*(p3[1]-p2[1])
            return px, py, math.degrees(math.atan2(dy, dx))

        first_curve = (
            (x0 + 48, y0 + ah * .7),
            (x0 + aw * .2, y0 + ah * .08),
            (x0 + aw * .38, y0 + ah * .94),
            (x0 + aw * .54, y0 + ah * .42),
        )
        reflected_control = (
            2 * first_curve[3][0] - first_curve[2][0],
            2 * first_curve[3][1] - first_curve[2][1],
        )
        second_curve = (
            first_curve[3],
            reflected_control,
            (x0 + aw * .8, y0 + ah * .14),
            (x0 + aw - 48, y0 + ah * .55),
        )
        static_poses = [
            cubic_pose(first_curve, .18),
            cubic_pose(first_curve, .58),
            cubic_pose(first_curve, .9),
            cubic_pose(second_curve, .38),
            cubic_pose(second_curve, .78),
        ]
        for index in range(5):
            begin = f"{fmt(index * ctx.duration_ms / 1000 / 5)}s"
            motion = smil(ctx, f'<animateMotion dur="{ctx.duration_s}" begin="{begin}" repeatCount="indefinite" rotate="auto"><mpath href="#{route_id}"/></animateMotion>')
            transform = "" if ctx.full_motion else f' transform="translate({fmt(static_poses[index][0])} {fmt(static_poses[index][1])}) rotate({static_poses[index][2]})"'
            body.append(f'<g{transform}>{motion}<path d="M -14 -8 L 15 0 L -14 8 Z" fill="{ctx.color(index)}"/></g>')
    elif variant == 3:
        cx, cy, rx, ry = x0 + aw / 2, y0 + ah / 2, aw * .24, ah * .28
        d1 = f"M {fmt(cx-rx)} {fmt(cy)} C {fmt(cx-rx)} {fmt(cy-ry)}, {fmt(cx+rx)} {fmt(cy-ry)}, {fmt(cx+rx)} {fmt(cy)} C {fmt(cx+rx)} {fmt(cy+ry)}, {fmt(cx-rx)} {fmt(cy+ry)}, {fmt(cx-rx)} {fmt(cy)} Z"
        d2 = f"M {fmt(cx-rx)} {fmt(cy)} C {fmt(cx-rx*.3)} {fmt(cy-ry)}, {fmt(cx+rx*.3)} {fmt(cy-ry)}, {fmt(cx+rx)} {fmt(cy)} C {fmt(cx+rx*.3)} {fmt(cy+ry)}, {fmt(cx-rx*.3)} {fmt(cy+ry)}, {fmt(cx-rx)} {fmt(cy)} Z"
        animate = smil(ctx, f'<animate attributeName="d" values="{d1};{d2};{d1}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
        body.append(f'<path d="{d1}" fill="{ctx.palette["highlight"]}" stroke="{ctx.color(4)}" stroke-width="5">{animate}</path>')
    elif variant == 4:
        body.append(f'<path d="{route}" fill="none" stroke="{ctx.palette["soft"]}" stroke-width="5"/>')
        style = css_animation(ctx, "psvg-trim", .7, 0, "linear")
        body.append(f'<path d="{route}" pathLength="1" fill="none" stroke="{ctx.color(3)}" stroke-width="12" stroke-linecap="round" style="{style}"/>')
    else:
        trace_id = ctx.ident(f"{slug_from_pattern(str(ctx.spec['id']))}-trace")
        mask_id = ctx.ident(f"{slug_from_pattern(str(ctx.spec['id']))}-mask")
        handwriting = f"M {fmt(x0 + aw*.14)} {fmt(y0 + ah*.65)} C {fmt(x0+aw*.2)} {fmt(y0+ah*.18)}, {fmt(x0+aw*.25)} {fmt(y0+ah*.88)}, {fmt(x0+aw*.33)} {fmt(y0+ah*.45)} S {fmt(x0+aw*.46)} {fmt(y0+ah*.2)}, {fmt(x0+aw*.5)} {fmt(y0+ah*.62)} S {fmt(x0+aw*.64)} {fmt(y0+ah*.86)}, {fmt(x0+aw*.7)} {fmt(y0+ah*.38)} S {fmt(x0+aw*.82)} {fmt(y0+ah*.2)}, {fmt(x0+aw*.87)} {fmt(y0+ah*.58)}"
        style = css_animation(ctx, "psvg-draw", .9, 0, "ease-out")
        defs = f'<defs><mask id="{mask_id}"><rect x="0" y="0" width="{ctx.width}" height="{ctx.height}" fill="black"/><path id="{trace_id}" d="{handwriting}" pathLength="1" fill="none" stroke="white" stroke-width="28" stroke-linecap="round" style="{style}"/></mask></defs>'
        body.append(defs)
        body.append(f'<path d="{handwriting}" fill="none" stroke="{ctx.palette["line"]}" stroke-width="5" stroke-linecap="round" opacity=".6"/>')
        body.append(f'<path d="{handwriting}" fill="none" stroke="{ctx.color(0)}" stroke-width="20" stroke-linecap="round" mask="url(#{mask_id})"/>')
        if ctx.full_motion:
            motion = smil(ctx, f'<animateMotion dur="{ctx.duration_s}" repeatCount="indefinite" rotate="auto"><mpath href="#{trace_id}"/></animateMotion>')
            body.append(f'<g>{motion}<circle r="9" fill="{ctx.palette["ink"]}"/><path d="M 0 0 L -22 8" stroke="{ctx.palette["ink"]}" stroke-width="5" stroke-linecap="round"/></g>')
        else:
            body.append(
                f'<g transform="translate({fmt(x0+aw*.87)} {fmt(y0+ah*.58)}) rotate(18)">'
                f'<circle r="9" fill="{ctx.palette["ink"]}"/>'
                f'<path d="M 0 0 L -22 8" stroke="{ctx.palette["ink"]}" stroke-width="5" stroke-linecap="round"/></g>'
            )
    return panel_frame(ctx, "".join(body), str(ctx.spec["signature"]))


def sample_parametric(ctx: Context, variant: int, count: int = 360) -> list[tuple[float, float]]:
    cx, cy = ctx.left + ctx.art_width / 2, ctx.top + ctx.art_height / 2
    scale = min(ctx.art_width, ctx.art_height) * .37
    period = math.tau
    if variant == 2:
        # A hypotrochoid closes after 2πr/gcd(R,r), not necessarily 2π.
        period = math.tau * 3 / math.gcd(5, 3)
    points: list[tuple[float, float]] = []
    for index in range(count + 1):
        t = index / count * period
        if variant == 0:
            x, y = math.sin(3 * t + math.pi / 3), math.sin(5 * t)
        elif variant == 1:
            radius = math.cos(7 * t)
            x, y = radius * math.cos(t), radius * math.sin(t)
        elif variant == 2:
            big, small, pen = 5.0, 3.0, 4.1
            x = ((big - small) * math.cos(t) + pen * math.cos((big - small) / small * t)) / 6.2
            y = ((big - small) * math.sin(t) - pen * math.sin((big - small) / small * t)) / 6.2
        elif variant == 4:
            m, n1, n2, n3 = 6, .34, 1.25, 1.25
            a = abs(math.cos(m * t / 4)) ** n2
            b = abs(math.sin(m * t / 4)) ** n3
            radius = (a + b) ** (-1 / n1) if a + b > 1e-9 else 0
            x, y = radius * math.cos(t) * .52, radius * math.sin(t) * .52
        else:
            x, y = math.cos(t), math.sin(t)
        points.append((cx + x * scale, cy + y * scale))
    return points


def render_parametric(ctx: Context) -> str:
    variant = int(ctx.spec["variant"])
    x0, y0, aw, ah = ctx.left, ctx.top, ctx.art_width, ctx.art_height
    cx, cy = x0 + aw / 2, y0 + ah / 2
    body: list[str] = []
    if variant in (0, 1, 2):
        points = sample_parametric(ctx, variant, 480 if variant == 2 else 360)
        path = path_from_points(points, True)
        body.append(f'<path d="{path}" fill="none" stroke="{ctx.palette["soft"]}" stroke-width="9" opacity=".55"/>')
        style = css_animation(ctx, "psvg-draw", 1.0, 0, "ease-in-out")
        rotate = smil(ctx, f'<animateTransform attributeName="transform" type="rotate" from="0 {fmt(cx)} {fmt(cy)}" to="360 {fmt(cx)} {fmt(cy)}" dur="{fmt(ctx.duration_ms/1000*1.8)}s" repeatCount="indefinite"/>')
        body.append(f'<path d="{path}" pathLength="1" fill="none" stroke="{ctx.color(variant)}" stroke-width="4" style="{style}">{rotate}</path>')
    elif variant == 3:
        harmonics = [(1, .42, 0), (2, .24, .4), (3, .15, 1.1), (5, .1, 2.2)]
        radius_scale = min(aw, ah) * .42
        base_x, base_y = cx, cy
        trace: list[tuple[float, float]] = []
        for sample in range(361):
            t = sample / 360 * math.tau
            tx, ty = base_x, base_y
            for frequency, amplitude, phase in harmonics:
                radius = radius_scale * amplitude
                tx += radius * math.cos(frequency * t + phase)
                ty += radius * math.sin(frequency * t + phase)
            trace.append((tx, ty))
        trace_path = path_from_points(trace)
        style = css_animation(ctx, "psvg-draw", 1.0, 0, "linear")
        body.append(f'<path d="{trace_path}" fill="none" stroke="{ctx.palette["soft"]}" stroke-width="9" opacity=".7"/>')
        body.append(f'<path d="{trace_path}" pathLength="1" fill="none" stroke="{ctx.color(4)}" stroke-width="4" style="{style}"/>')

        previous_frequency = 0
        previous_phase = 0.0
        chain = [f'<g transform="translate({fmt(base_x)} {fmt(base_y)})">']
        for index, (frequency, amplitude, phase) in enumerate(harmonics):
            radius = radius_scale * amplitude
            relative_frequency = frequency - previous_frequency
            relative_phase = math.degrees(phase - previous_phase)
            animate = smil(
                ctx,
                f'<animateTransform attributeName="transform" type="rotate" from="{fmt(relative_phase)}" to="{fmt(relative_phase + relative_frequency * 360)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            chain.append(
                f'<g transform="rotate({fmt(relative_phase)})">{animate}'
                f'<circle cx="0" cy="0" r="{fmt(radius)}" fill="none" stroke="{ctx.color(index)}" opacity=".55"/>'
                f'<line x1="0" y1="0" x2="{fmt(radius)}" y2="0" stroke="{ctx.color(index)}" stroke-width="3"/>'
                f'<g transform="translate({fmt(radius)} 0)"><circle cx="0" cy="0" r="4.5" fill="{ctx.color(index)}"/>'
            )
            previous_frequency = frequency
            previous_phase = phase
        chain.append(f'<circle cx="0" cy="0" r="8" fill="{ctx.palette["ink"]}" stroke="{ctx.palette["surface"]}" stroke-width="2"/>')
        chain.append('</g></g>' * len(harmonics))
        chain.append('</g>')
        body.append("".join(chain))
    elif variant == 4:
        points = sample_parametric(ctx, 4, 360)
        d1 = path_from_points(points, True)
        altered: list[tuple[float, float]] = []
        scale = min(aw, ah) * .34
        for index in range(361):
            t = index / 360 * math.tau
            radius = 1 / ((abs(math.cos(4 * t / 4)) ** 2.7 + abs(math.sin(4 * t / 4)) ** 2.7) ** (1 / .6) + 1e-9)
            altered.append((cx + radius * math.cos(t) * scale * .62, cy + radius * math.sin(t) * scale * .62))
        d2 = path_from_points(altered, True)
        animate = smil(ctx, f'<animate attributeName="d" values="{d1};{d2};{d1}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
        body.append(f'<path d="{d1}" fill="{ctx.palette["highlight"]}" stroke="{ctx.color(5)}" stroke-width="5">{animate}</path>')
    else:
        frame_count = 16
        point_count = 96
        key_times = ";".join(fmt(frame / frame_count) for frame in range(frame_count + 1))
        components = [(1.0, 1, 13.0, 0.0), (2.2, 2, 8.0, .72), (3.7, 3, 5.0, -1.05)]
        for band in range(7):
            baseline = y0 + 46 + band * (ah - 92) / 6
            frames: list[str] = []
            for frame in range(frame_count + 1):
                normalized_time = frame / frame_count
                points: list[tuple[float, float]] = []
                for point in range(point_count + 1):
                    normalized_x = point / point_count
                    x = x0 + 36 + normalized_x * (aw - 72)
                    y = baseline
                    for component_index, (spatial_frequency, temporal_frequency, amplitude, phase) in enumerate(components):
                        band_phase = band * (.21 + component_index * .13)
                        y += amplitude * math.sin(
                            math.tau * (spatial_frequency * normalized_x - temporal_frequency * normalized_time)
                            + phase
                            + band_phase
                        )
                    points.append((x, y))
                frames.append(path_from_points(points))
            animate = smil(
                ctx,
                f'<animate attributeName="d" values="{";".join(frames)}" keyTimes="{key_times}" calcMode="linear" dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            body.append(f'<path d="{frames[0]}" fill="none" stroke="{ctx.color(band)}" stroke-width="3.5">{animate}</path>')
    return panel_frame(ctx, "".join(body), str(ctx.spec["signature"]))


def vector_at(x: float, y: float, phase: float = 0.0) -> tuple[float, float]:
    return (-y + .36 * math.sin(3 * x + phase), x + .36 * math.cos(3 * y - phase))


def periodic_value_noise(position: float, lattice: Sequence[float]) -> float:
    """Interpolate a seeded one-dimensional lattice with a seamless period."""
    scaled = (position % 1.0) * len(lattice)
    left = math.floor(scaled)
    fraction = scaled - left
    smooth = fraction * fraction * (3 - 2 * fraction)
    a = lattice[left % len(lattice)]
    b = lattice[(left + 1) % len(lattice)]
    return a + (b - a) * smooth


def marching_squares_path(
    xs: Sequence[float],
    ys: Sequence[float],
    values: Sequence[Sequence[float]],
    level: float,
) -> str:
    """Extract line segments for one scalar iso-level with marching squares."""
    pieces: list[str] = []

    def crossing(
        point_a: tuple[float, float],
        point_b: tuple[float, float],
        value_a: float,
        value_b: float,
    ) -> tuple[float, float]:
        fraction = .5 if value_a == value_b else (level - value_a) / (value_b - value_a)
        fraction = min(1.0, max(0.0, fraction))
        return (
            point_a[0] + (point_b[0] - point_a[0]) * fraction,
            point_a[1] + (point_b[1] - point_a[1]) * fraction,
        )

    for row in range(len(ys) - 1):
        for column in range(len(xs) - 1):
            points = [
                (xs[column], ys[row]),
                (xs[column + 1], ys[row]),
                (xs[column + 1], ys[row + 1]),
                (xs[column], ys[row + 1]),
            ]
            samples = [
                values[row][column],
                values[row][column + 1],
                values[row + 1][column + 1],
                values[row + 1][column],
            ]
            edges = ((0, 1), (1, 2), (3, 2), (0, 3))
            hits: dict[int, tuple[float, float]] = {}
            for edge_index, (start, end) in enumerate(edges):
                if (samples[start] >= level) != (samples[end] >= level):
                    hits[edge_index] = crossing(points[start], points[end], samples[start], samples[end])
            pairs: list[tuple[int, int]] = []
            if len(hits) == 2:
                keys = sorted(hits)
                pairs = [(keys[0], keys[1])]
            elif len(hits) == 4:
                center = sum(samples) / 4
                pairs = [(0, 1), (2, 3)] if center >= level else [(0, 3), (1, 2)]
            for edge_a, edge_b in pairs:
                a, b = hits[edge_a], hits[edge_b]
                pieces.append(f'M {fmt(a[0])} {fmt(a[1])} L {fmt(b[0])} {fmt(b[1])}')
    return " ".join(pieces)


def render_field(ctx: Context) -> str:
    variant = int(ctx.spec["variant"])
    x0, y0, aw, ah = ctx.left, ctx.top, ctx.art_width, ctx.art_height
    body: list[str] = []
    rng = ctx.rng("field")
    if variant == 0:
        rows, columns = 9, 15
        for row in range(rows):
            for column in range(columns):
                x = x0 + 34 + column * (aw - 68) / (columns - 1)
                y = y0 + 32 + row * (ah - 64) / (rows - 1)
                nx = (x - (x0 + aw / 2)) / (aw / 2)
                ny = (y - (y0 + ah / 2)) / (ah / 2)
                vx, vy = vector_at(nx, ny)
                magnitude = math.hypot(vx, vy) or 1
                length = 8 + min(20, magnitude * 11)
                dx, dy = vx / magnitude * length, vy / magnitude * length
                animate = smil(ctx, f'<animate attributeName="opacity" values=".35;1;.35" dur="{ctx.duration_s}" begin="{fmt(-(row+column)*.05)}s" repeatCount="indefinite"/>')
                body.append(f'<line x1="{fmt(x-dx/2)}" y1="{fmt(y-dy/2)}" x2="{fmt(x+dx/2)}" y2="{fmt(y+dy/2)}" stroke="{ctx.color(int(magnitude*3))}" stroke-width="2.4" stroke-linecap="round">{animate}</line>')
    elif variant in (1, 3):
        paths: list[str] = []
        representative_points: list[tuple[float, float]] = []
        count = 28 if variant == 1 else 18
        for index in range(count):
            px = rng.uniform(-.9, .9)
            py = rng.uniform(-.75, .75)
            points: list[tuple[float, float]] = []
            for _ in range(90):
                sx = x0 + (px + 1) / 2 * aw
                sy = y0 + (py + 1) / 2 * ah
                points.append((sx, sy))
                vx, vy = vector_at(px, py, index * .17)
                magnitude = math.hypot(vx, vy) or 1
                px += vx / magnitude * .024
                py += vy / magnitude * .024
                if abs(px) > 1.05 or abs(py) > 1.05:
                    break
            paths.append(path_from_points(points))
            representative_points.append(points[min(len(points) - 1, len(points) // 2)])
        if variant == 1:
            for index, path in enumerate(paths):
                style = css_animation(ctx, "psvg-draw", .65 + index % 5 * .07, -index * 50, "ease-out")
                body.append(f'<path d="{path}" pathLength="1" fill="none" stroke="{ctx.color(index)}" stroke-width="{fmt(1.8 + index % 3)}" opacity=".75" style="{style}"/>')
        else:
            for index, path in enumerate(paths):
                route_id = ctx.ident(f"field-route-{index}")
                body.append(f'<path id="{route_id}" d="{path}" fill="none" stroke="{ctx.palette["line"]}" stroke-width="1" opacity=".35"/>')
                motion = smil(ctx, f'<animateMotion dur="{fmt(ctx.duration_ms/1000*(.65+(index%4)*.08))}s" begin="{fmt(-index*.11)}s" repeatCount="indefinite"><mpath href="#{route_id}"/></animateMotion>')
                static_position = representative_points[index]
                position = "" if ctx.full_motion else f' cx="{fmt(static_position[0])}" cy="{fmt(static_position[1])}"'
                body.append(f'<circle{position} r="{fmt(3+index%4)}" fill="{ctx.color(index)}">{motion}</circle>')
    elif variant == 2:
        for ribbon in range(12):
            baseline = y0 + 34 + ribbon * (ah - 68) / 11
            octave_lattices = [
                [rng.uniform(-1, 1) for _ in range(6 * 2**octave)]
                for octave in range(4)
            ]
            frame_paths: list[str] = []
            for frame in range(9):
                phase = frame / 8
                points: list[tuple[float, float]] = []
                for index in range(100):
                    u = index / 99
                    displacement = sum(
                        11 / (2**octave) * periodic_value_noise(u + phase + ribbon * .071, lattice)
                        for octave, lattice in enumerate(octave_lattices)
                    )
                    points.append((x0 + 26 + u * (aw - 52), baseline + displacement))
                frame_paths.append(smooth_path(points))
            animate = smil(ctx, f'<animate attributeName="d" values="{";".join(frame_paths)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<path d="{frame_paths[0]}" fill="none" stroke="{ctx.color(ribbon)}" stroke-width="5" opacity=".7">{animate}</path>')
    elif variant == 4:
        sites = [(rng.uniform(x0 + aw*.18, x0 + aw*.82), rng.uniform(y0 + ah*.18, y0 + ah*.82)) for _ in range(5)]
        columns, rows = 52, 34
        xs = [x0 + column * aw / (columns - 1) for column in range(columns)]
        ys = [y0 + row * ah / (rows - 1) for row in range(rows)]
        values = [
            [min(math.hypot(x - sx, y - sy) for sx, sy in sites) for x in xs]
            for y in ys
        ]
        for level_index, fraction in enumerate((.055, .09, .125, .16, .195, .23)):
            level = min(aw, ah) * fraction
            path = marching_squares_path(xs, ys, values, level)
            style = css_animation(ctx, "psvg-contour", .65, -level_index * 170, "ease-in-out")
            body.append(f'<path d="{path}" fill="none" stroke="{ctx.color(level_index + 1)}" stroke-width="{fmt(4-level_index*.35)}" opacity=".58" style="{style}"/>')
        for site_index, (sx, sy) in enumerate(sites):
            body.append(f'<circle cx="{fmt(sx)}" cy="{fmt(sy)}" r="6" fill="{ctx.color(site_index)}" stroke="{ctx.palette["surface"]}" stroke-width="2"/>')
    else:
        filter_id = ctx.ident(f"{slug_from_pattern(str(ctx.spec['id']))}-goo")
        defs = f'<defs><filter id="{filter_id}" x="-25%" y="-25%" width="150%" height="150%"><feGaussianBlur in="SourceGraphic" stdDeviation="14" result="blur"/><feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 24 -10"/></filter></defs>'
        body.append(defs + f'<g filter="url(#{filter_id})">')
        for index in range(8):
            cx = x0 + aw * (.25 + .5 * rng.random())
            cy = y0 + ah * (.25 + .5 * rng.random())
            dx, dy = rng.uniform(-aw*.16, aw*.16), rng.uniform(-ah*.18, ah*.18)
            animate_x = smil(ctx, f'<animate attributeName="cx" values="{fmt(cx)};{fmt(cx+dx)};{fmt(cx)}" dur="{fmt(ctx.duration_ms/1000*(.7+index*.05))}s" repeatCount="indefinite"/>')
            animate_y = smil(ctx, f'<animate attributeName="cy" values="{fmt(cy)};{fmt(cy+dy)};{fmt(cy)}" dur="{fmt(ctx.duration_ms/1000*(.82+index*.04))}s" repeatCount="indefinite"/>')
            body.append(f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(32+index%3*9)}" fill="{ctx.color(index)}">{animate_x}{animate_y}</circle>')
        body.append('</g>')
    return panel_frame(ctx, "".join(body), str(ctx.spec["signature"]))


def branching_segments(ctx: Context, depth: int, spread: float, jitter: float, coral: bool = False) -> list[tuple[float, float, float, float, int]]:
    rng = ctx.rng(f"branches-{depth}-{spread}-{jitter}-{coral}")
    segments: list[tuple[float, float, float, float, int]] = []
    start_x = ctx.left + ctx.art_width / 2
    start_y = ctx.top + ctx.art_height * .88

    def branch(x: float, y: float, length: float, angle: float, level: int) -> None:
        if level > depth or length < 3:
            return
        x2 = x + math.cos(angle) * length
        y2 = y + math.sin(angle) * length
        segments.append((x, y, x2, y2, level))
        child_count = 3 if coral and level % 2 == 0 else 2
        for child in range(child_count):
            offset = (child - (child_count - 1) / 2) * spread
            branch(x2, y2, length * rng.uniform(.67, .79), angle + offset + rng.uniform(-jitter, jitter), level + 1)

    branch(start_x, start_y, ctx.art_height * .24, -math.pi / 2, 0)
    return segments


def lsystem_segments(ctx: Context, iterations: int = 3) -> list[tuple[float, float, float, float, int]]:
    """Expand a deterministic context-free grammar and interpret it with a turtle."""
    sentence = "F"
    production = "F[+F]F[-F]F"
    for _ in range(iterations):
        sentence = "".join(production if symbol == "F" else symbol for symbol in sentence)

    x = y = 0.0
    heading = -math.pi / 2
    turn = math.radians(24)
    stack: list[tuple[float, float, float, int]] = []
    depth = 0
    raw: list[tuple[float, float, float, float, int]] = []
    for symbol in sentence:
        if symbol == "F":
            nx, ny = x + math.cos(heading), y + math.sin(heading)
            raw.append((x, y, nx, ny, depth))
            x, y = nx, ny
        elif symbol == "+":
            heading += turn
        elif symbol == "-":
            heading -= turn
        elif symbol == "[":
            stack.append((x, y, heading, depth))
            depth += 1
        elif symbol == "]" and stack:
            x, y, heading, depth = stack.pop()

    xs = [coordinate for segment in raw for coordinate in (segment[0], segment[2])]
    ys = [coordinate for segment in raw for coordinate in (segment[1], segment[3])]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    scale = min(
        (ctx.art_width - 72) / max(1e-6, max_x - min_x),
        (ctx.art_height - 50) / max(1e-6, max_y - min_y),
    )
    offset_x = ctx.left + (ctx.art_width - (max_x - min_x) * scale) / 2 - min_x * scale
    offset_y = ctx.top + 24 - min_y * scale
    return [
        (
            offset_x + x1 * scale,
            offset_y + y1 * scale,
            offset_x + x2 * scale,
            offset_y + y2 * scale,
            level,
        )
        for x1, y1, x2, y2, level in raw
    ]


def precompute_space_colonization(
    ctx: Context,
    attractor_count: int = 150,
    max_nodes: int = 300,
) -> tuple[list[tuple[float, float, int | None, int]], list[tuple[float, float]]]:
    """Grow a branching graph by assigning nearby attractors to their closest node."""
    rng = ctx.rng("space-colonization-attractors")
    attractors: list[tuple[float, float]] = []
    while len(attractors) < attractor_count:
        y = rng.uniform(.08, .73)
        crown_phase = min(1.0, max(0.0, (y - .06) / .7))
        half_width = .09 + .36 * math.sin(math.pi * crown_phase) ** .72
        x = rng.uniform(.5 - half_width, .5 + half_width)
        attractors.append((x, y))
    source_attractors = list(attractors)

    nodes: list[tuple[float, float, int | None, int]] = [(0.5, .92, None, 0)]
    for generation in range(1, 8):
        parent = len(nodes) - 1
        nodes.append((.5, .92 - generation * .026, parent, generation))

    influence_radius = .145
    kill_radius = .032
    step_size = .026
    for generation in range(8, 150):
        if not attractors or len(nodes) >= max_nodes:
            break
        influences: dict[int, list[tuple[float, float]]] = {}
        survivors: list[tuple[float, float]] = []
        for attractor_x, attractor_y in attractors:
            nearest_index = -1
            nearest_distance = float("inf")
            for node_index, (node_x, node_y, _parent, _generation) in enumerate(nodes):
                distance = math.hypot(attractor_x - node_x, attractor_y - node_y)
                if distance < nearest_distance:
                    nearest_index, nearest_distance = node_index, distance
            if nearest_distance < kill_radius:
                continue
            survivors.append((attractor_x, attractor_y))
            if nearest_distance <= influence_radius:
                node_x, node_y, _parent, _generation = nodes[nearest_index]
                influences.setdefault(nearest_index, []).append(
                    ((attractor_x - node_x) / nearest_distance, (attractor_y - node_y) / nearest_distance)
                )
        attractors = survivors
        if not influences:
            nearest = min(
                attractors,
                key=lambda point: math.hypot(point[0] - nodes[-1][0], point[1] - nodes[-1][1]),
                default=None,
            )
            if nearest is None:
                break
            node_x, node_y, _parent, _generation = nodes[-1]
            direction_x, direction_y = nearest[0] - node_x, nearest[1] - node_y
            magnitude = math.hypot(direction_x, direction_y) or 1.0
            nodes.append((node_x + direction_x / magnitude * step_size, node_y + direction_y / magnitude * step_size, len(nodes) - 1, generation))
            continue

        additions: list[tuple[float, float, int, int]] = []
        for parent_index, directions in sorted(influences.items()):
            direction_x = sum(direction[0] for direction in directions) / len(directions)
            direction_y = sum(direction[1] for direction in directions) / len(directions)
            magnitude = math.hypot(direction_x, direction_y) or 1.0
            parent_x, parent_y, _parent, _generation = nodes[parent_index]
            new_x = parent_x + direction_x / magnitude * step_size
            new_y = parent_y + direction_y / magnitude * step_size
            if all(math.hypot(new_x - node[0], new_y - node[1]) > step_size * .42 for node in nodes):
                additions.append((new_x, new_y, parent_index, generation))
        if not additions:
            break
        nodes.extend(additions[: max_nodes - len(nodes)])

    scaled_nodes = [
        (
            ctx.left + x * ctx.art_width,
            ctx.top + y * ctx.art_height,
            parent,
            generation,
        )
        for x, y, parent, generation in nodes
    ]
    scaled_attractors = [
        (ctx.left + x * ctx.art_width, ctx.top + y * ctx.art_height)
        for x, y in source_attractors
    ]
    return scaled_nodes, scaled_attractors


FrameT = TypeVar("FrameT")


def ping_pong_frames(frames: Sequence[FrameT]) -> list[FrameT]:
    if not frames:
        return []
    if len(frames) == 1:
        return [frames[0], frames[0]]
    return list(frames) + list(frames[-2:0:-1]) + [frames[0]]


def precompute_boid_trajectories(ctx: Context, count: int = 32, steps: int = 56) -> list[list[tuple[float, float]]]:
    """Record a deterministic Reynolds-style flock using three local rules."""
    rng = ctx.rng("boids-local-steering")
    positions = [(rng.uniform(.14, .86), rng.uniform(.16, .84)) for _ in range(count)]
    velocities: list[tuple[float, float]] = []
    for _ in range(count):
        angle = rng.random() * math.tau
        speed = rng.uniform(.006, .012)
        velocities.append((math.cos(angle) * speed, math.sin(angle) * speed))
    frames: list[list[tuple[float, float]]] = []
    for _step in range(steps):
        frames.append(list(positions))
        next_velocities: list[tuple[float, float]] = []
        for index, ((px, py), (vx, vy)) in enumerate(zip(positions, velocities)):
            neighbors: list[int] = []
            separation_x = separation_y = 0.0
            for other_index, (ox, oy) in enumerate(positions):
                if other_index == index:
                    continue
                dx, dy = px - ox, py - oy
                distance = math.hypot(dx, dy)
                if distance < .22:
                    neighbors.append(other_index)
                if 1e-6 < distance < .075:
                    separation_x += dx / (distance * distance)
                    separation_y += dy / (distance * distance)
            alignment_x = alignment_y = cohesion_x = cohesion_y = 0.0
            if neighbors:
                alignment_x = sum(velocities[item][0] for item in neighbors) / len(neighbors) - vx
                alignment_y = sum(velocities[item][1] for item in neighbors) / len(neighbors) - vy
                cohesion_x = sum(positions[item][0] for item in neighbors) / len(neighbors) - px
                cohesion_y = sum(positions[item][1] for item in neighbors) / len(neighbors) - py
            boundary_x = .0018 if px < .1 else -.0018 if px > .9 else 0.0
            boundary_y = .0018 if py < .1 else -.0018 if py > .9 else 0.0
            nvx = vx + separation_x * .000035 + alignment_x * .075 + cohesion_x * .006 + boundary_x
            nvy = vy + separation_y * .000035 + alignment_y * .075 + cohesion_y * .006 + boundary_y
            speed = math.hypot(nvx, nvy) or 1e-9
            limited = min(.016, max(.0045, speed))
            next_velocities.append((nvx / speed * limited, nvy / speed * limited))
        next_positions: list[tuple[float, float]] = []
        for (px, py), (vx, vy) in zip(positions, next_velocities):
            nx, ny = px + vx, py + vy
            if nx < .035 or nx > .965:
                vx = -vx
                nx = min(.965, max(.035, nx))
            if ny < .045 or ny > .955:
                vy = -vy
                ny = min(.955, max(.045, ny))
            next_positions.append((nx, ny))
        positions, velocities = next_positions, next_velocities
    trajectories: list[list[tuple[float, float]]] = []
    for index in range(count):
        trajectories.append(
            [
                (ctx.left + px * ctx.art_width, ctx.top + py * ctx.art_height)
                for px, py in (frame[index] for frame in frames)
            ]
        )
    return trajectories


def precompute_verlet_cloth(ctx: Context, rows: int = 7, columns: int = 12) -> list[list[tuple[float, float]]]:
    """Advance particles with Verlet integration and project structural constraints."""
    rng = ctx.rng("verlet-cloth")
    rest_x = (ctx.art_width - 104) / (columns - 1)
    rest_y = (ctx.art_height - 78) / (rows - 1)
    points: list[list[float]] = []
    for row in range(rows):
        for column in range(columns):
            points.append(
                [
                    ctx.left + 52 + column * rest_x,
                    ctx.top + 34 + row * rest_y + (rng.uniform(-.7, .7) if row else 0),
                ]
            )
    previous = [[x, y] for x, y in points]
    pinned = {column for column in range(columns)}
    edges: list[tuple[int, int, float]] = []
    for row in range(rows):
        for column in range(columns):
            index = row * columns + column
            if column + 1 < columns:
                edges.append((index, index + 1, rest_x))
            if row + 1 < rows:
                edges.append((index, index + columns, rest_y))
    frames: list[list[tuple[float, float]]] = [[(x, y) for x, y in points]]
    for step in range(42):
        for index, point in enumerate(points):
            if index in pinned:
                continue
            row = index // columns
            velocity_x = (point[0] - previous[index][0]) * .992
            velocity_y = (point[1] - previous[index][1]) * .992
            previous[index] = [point[0], point[1]]
            point[0] += velocity_x + math.sin(step * .23 + row * .41) * .18 * row
            point[1] += velocity_y + .38
        for _ in range(6):
            for first, second, rest in edges:
                ax, ay = points[first]
                bx, by = points[second]
                dx, dy = bx - ax, by - ay
                distance = math.hypot(dx, dy) or 1e-9
                correction = (distance - rest) / distance
                first_pinned, second_pinned = first in pinned, second in pinned
                if not first_pinned and not second_pinned:
                    points[first][0] += dx * correction * .5
                    points[first][1] += dy * correction * .5
                    points[second][0] -= dx * correction * .5
                    points[second][1] -= dy * correction * .5
                elif first_pinned and not second_pinned:
                    points[second][0] -= dx * correction
                    points[second][1] -= dy * correction
                elif not first_pinned and second_pinned:
                    points[first][0] += dx * correction
                    points[first][1] += dy * correction
        for column in range(columns):
            points[column][0] = ctx.left + 52 + column * rest_x
            points[column][1] = ctx.top + 34
        if step % 2 == 1:
            frames.append([(x, y) for x, y in points])
    return ping_pong_frames(frames)


def precompute_spring_mesh(ctx: Context, rows: int = 5, columns: int = 9) -> list[list[tuple[float, float]]]:
    """Integrate a damped nearest-neighbor mass-spring lattice after one impulse."""
    base = [
        (
            ctx.left + 70 + column * (ctx.art_width - 140) / (columns - 1),
            ctx.top + 55 + row * (ctx.art_height - 110) / (rows - 1),
        )
        for row in range(rows)
        for column in range(columns)
    ]
    displacement = [0.0] * (rows * columns)
    velocity = [0.0] * (rows * columns)
    center = (rows // 2) * columns + columns // 2
    displacement[center] = -38.0
    frames: list[list[tuple[float, float]]] = [[(x, y + displacement[index]) for index, (x, y) in enumerate(base)]]
    for step in range(72):
        acceleration = [0.0] * len(displacement)
        for row in range(rows):
            for column in range(columns):
                index = row * columns + column
                if row in (0, rows - 1) or column in (0, columns - 1):
                    displacement[index] = 0.0
                    velocity[index] = 0.0
                    continue
                neighbors = (index - 1, index + 1, index - columns, index + columns)
                coupling = sum(displacement[item] - displacement[index] for item in neighbors)
                acceleration[index] = 1.65 * coupling - .32 * velocity[index]
        for index in range(len(displacement)):
            velocity[index] += acceleration[index] * .075
            displacement[index] += velocity[index] * .075
        if step % 3 == 2:
            frames.append([(x, y + displacement[index]) for index, (x, y) in enumerate(base)])
    return ping_pong_frames(frames)


def precompute_cellular_automaton(ctx: Context, rows: int = 16, columns: int = 25) -> list[list[list[bool]]]:
    """Compute deterministic Conway Life generations on a toroidal grid."""
    rng = ctx.rng("cellular-automaton-life")
    state = [[rng.random() < .36 for _ in range(columns)] for _ in range(rows)]
    frames: list[list[list[bool]]] = []
    for _generation in range(18):
        frames.append([list(row) for row in state])
        following = [[False] * columns for _ in range(rows)]
        for row in range(rows):
            for column in range(columns):
                neighbors = sum(
                    state[(row + dy) % rows][(column + dx) % columns]
                    for dy in (-1, 0, 1)
                    for dx in (-1, 0, 1)
                    if dx or dy
                )
                following[row][column] = neighbors == 3 or (state[row][column] and neighbors == 2)
        state = following
    return ping_pong_frames(frames)


def precompute_gray_scott(ctx: Context, rows: int = 20, columns: int = 32) -> list[list[list[float]]]:
    """Integrate a compact Gray-Scott reaction-diffusion field."""
    rng = ctx.rng("gray-scott")
    u = [[1.0] * columns for _ in range(rows)]
    v = [[0.0] * columns for _ in range(rows)]
    seeds = [(rows // 2, columns // 2)] + [
        (rng.randrange(4, rows - 4), rng.randrange(4, columns - 4)) for _ in range(3)
    ]
    for center_row, center_column in seeds:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                row, column = (center_row + dy) % rows, (center_column + dx) % columns
                u[row][column] = .18 + rng.random() * .04
                v[row][column] = .82 + rng.random() * .08
    diffusion_u, diffusion_v, feed, kill, dt = .16, .08, .0367, .0649, 1.0
    frames: list[list[list[float]]] = []
    for iteration in range(380):
        next_u = [[0.0] * columns for _ in range(rows)]
        next_v = [[0.0] * columns for _ in range(rows)]
        for row in range(rows):
            for column in range(columns):
                current_u, current_v = u[row][column], v[row][column]
                lap_u = (
                    u[(row - 1) % rows][column]
                    + u[(row + 1) % rows][column]
                    + u[row][(column - 1) % columns]
                    + u[row][(column + 1) % columns]
                    - 4 * current_u
                )
                lap_v = (
                    v[(row - 1) % rows][column]
                    + v[(row + 1) % rows][column]
                    + v[row][(column - 1) % columns]
                    + v[row][(column + 1) % columns]
                    - 4 * current_v
                )
                reaction = current_u * current_v * current_v
                next_u[row][column] = min(1.0, max(0.0, current_u + (diffusion_u * lap_u - reaction + feed * (1 - current_u)) * dt))
                next_v[row][column] = min(1.0, max(0.0, current_v + (diffusion_v * lap_v + reaction - (feed + kill) * current_v) * dt))
        u, v = next_u, next_v
        if iteration >= 80 and (iteration - 80) % 25 == 0:
            frames.append([list(row) for row in v])
    return ping_pong_frames(frames)


def precompute_dla(ctx: Context, target: int = 220) -> list[tuple[tuple[int, int], tuple[int, int] | None]]:
    """Grow a lattice DLA cluster with random walkers and neighbor sticking."""
    rng = ctx.rng("diffusion-limited-aggregation")
    occupied: set[tuple[int, int]] = {(0, 0)}
    records: list[tuple[tuple[int, int], tuple[int, int] | None]] = [((0, 0), None)]
    radius = 1.0
    bound = 22
    cardinal = ((1, 0), (-1, 0), (0, 1), (0, -1))
    attempts = 0
    while len(records) < target and attempts < target * 90:
        attempts += 1
        launch_radius = min(bound - 2, max(4, int(math.ceil(radius)) + 4))
        angle = rng.random() * math.tau
        x, y = round(math.cos(angle) * launch_radius), round(math.sin(angle) * launch_radius)
        for _step in range(2600):
            touching = [(x + dx, y + dy) for dx, dy in cardinal if (x + dx, y + dy) in occupied]
            if touching and (x, y) not in occupied:
                parent = touching[rng.randrange(len(touching))]
                occupied.add((x, y))
                records.append(((x, y), parent))
                radius = max(radius, math.hypot(x, y))
                break
            if math.hypot(x, y) > launch_radius + 7 and rng.random() < .45:
                dx = -1 if x > 0 else 1 if x < 0 else 0
                dy = -1 if y > 0 else 1 if y < 0 else 0
                if dx and dy:
                    if rng.random() < .5:
                        dy = 0
                    else:
                        dx = 0
            else:
                dx, dy = cardinal[rng.randrange(len(cardinal))]
            x += dx
            y += dy
            if abs(x) > bound or abs(y) > bound:
                break
    return records


def render_simulation(ctx: Context) -> str:
    variant = int(ctx.spec["variant"])
    x0, y0, aw, ah = ctx.left, ctx.top, ctx.art_width, ctx.art_height
    body: list[str] = []
    if variant == 0:
        trajectories = precompute_boid_trajectories(ctx)
        for index, points in enumerate(trajectories):
            path = path_from_points(points)
            route_id = ctx.ident(f"boid-route-{index}")
            body.append(f'<path id="{route_id}" d="{path}" fill="none" stroke="{ctx.palette["line"]}" stroke-width=".7" opacity=".16"/>')
            loop_points = ping_pong_frames(points)
            if ctx.full_motion:
                key_times = ";".join(fmt(frame / (len(loop_points) - 1)) for frame in range(len(loop_points)))
                translations = ";".join(f"{fmt(px)} {fmt(py)}" for px, py in loop_points)
                motion = smil(
                    ctx,
                    f'<animateTransform attributeName="transform" type="translate" values="{translations}" '
                    f'keyTimes="{key_times}" dur="{ctx.duration_s}" repeatCount="indefinite"/>',
                )
                body.append(f'<path d="M 9 0 L 0 -6 L -9 0 L 0 6 Z" fill="{ctx.color(index)}">{motion}</path>')
            else:
                point_index = min(len(points) - 2, len(points) // 2)
                px, py = points[point_index]
                body.append(f'<path d="M 9 0 L 0 -6 L -9 0 L 0 6 Z" fill="{ctx.color(index)}" transform="translate({fmt(px)} {fmt(py)})"/>')
    elif variant == 1:
        rows, columns = 7, 12
        frames = precompute_verlet_cloth(ctx, rows, columns)
        display = frames[0] if ctx.full_motion else frames[len(frames) // 2]
        key_times = ";".join(fmt(index / (len(frames) - 1)) for index in range(len(frames)))
        for row in range(rows):
            row_frames = [" ".join(f"{fmt(frame[row * columns + column][0])},{fmt(frame[row * columns + column][1])}" for column in range(columns)) for frame in frames]
            points = " ".join(f"{fmt(display[row * columns + column][0])},{fmt(display[row * columns + column][1])}" for column in range(columns))
            animate = smil(ctx, f'<animate attributeName="points" values="{";".join(row_frames)}" keyTimes="{key_times}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<polyline points="{points}" fill="none" stroke="{ctx.color(row)}" stroke-width="2.2">{animate}</polyline>')
        for column in range(columns):
            column_frames = [" ".join(f"{fmt(frame[row * columns + column][0])},{fmt(frame[row * columns + column][1])}" for row in range(rows)) for frame in frames]
            points = " ".join(f"{fmt(display[row * columns + column][0])},{fmt(display[row * columns + column][1])}" for row in range(rows))
            animate = smil(ctx, f'<animate attributeName="points" values="{";".join(column_frames)}" keyTimes="{key_times}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<polyline points="{points}" fill="none" stroke="{ctx.palette["line"]}" stroke-width="1.2" opacity=".62">{animate}</polyline>')
        for column in range(columns):
            px, py = display[column]
            body.append(f'<circle cx="{fmt(px)}" cy="{fmt(py)}" r="4" fill="{ctx.palette["ink"]}"/>')
    elif variant == 2:
        rows, columns = 5, 9
        frames = precompute_spring_mesh(ctx, rows, columns)
        display = frames[0] if ctx.full_motion else frames[len(frames) // 2]
        key_times = ";".join(fmt(index / (len(frames) - 1)) for index in range(len(frames)))
        for row in range(rows):
            row_frames = [" ".join(f"{fmt(frame[row * columns + column][0])},{fmt(frame[row * columns + column][1])}" for column in range(columns)) for frame in frames]
            points = " ".join(f"{fmt(display[row * columns + column][0])},{fmt(display[row * columns + column][1])}" for column in range(columns))
            animate = smil(ctx, f'<animate attributeName="points" values="{";".join(row_frames)}" keyTimes="{key_times}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<polyline points="{points}" fill="none" stroke="{ctx.color(row)}" stroke-width="2">{animate}</polyline>')
        for column in range(columns):
            column_frames = [" ".join(f"{fmt(frame[row * columns + column][0])},{fmt(frame[row * columns + column][1])}" for row in range(rows)) for frame in frames]
            points = " ".join(f"{fmt(display[row * columns + column][0])},{fmt(display[row * columns + column][1])}" for row in range(rows))
            animate = smil(ctx, f'<animate attributeName="points" values="{";".join(column_frames)}" keyTimes="{key_times}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<polyline points="{points}" fill="none" stroke="{ctx.palette["line"]}" stroke-width="1.2">{animate}</polyline>')
        for index, (x, y) in enumerate(display):
            y_values = ";".join(fmt(frame[index][1]) for frame in frames)
            animate = smil(ctx, f'<animate attributeName="cy" values="{y_values}" keyTimes="{key_times}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="5.5" fill="{ctx.color(index)}">{animate}</circle>')
    elif variant == 3:
        rows, columns = 16, 25
        cell_w, cell_h = (aw-56)/columns, (ah-56)/rows
        frames = precompute_cellular_automaton(ctx, rows, columns)
        display = frames[0] if ctx.full_motion else frames[len(frames) // 2]
        key_times = ";".join(fmt(index / (len(frames) - 1)) for index in range(len(frames)))
        for row in range(rows):
            for column in range(columns):
                opacity_values = ";".join("1" if frame[row][column] else ".12" for frame in frames)
                opacity = "1" if display[row][column] else ".12"
                animate = smil(ctx, f'<animate attributeName="opacity" values="{opacity_values}" keyTimes="{key_times}" calcMode="discrete" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
                body.append(f'<rect x="{fmt(x0+28+column*cell_w)}" y="{fmt(y0+28+row*cell_h)}" width="{fmt(max(1,cell_w-1.2))}" height="{fmt(max(1,cell_h-1.2))}" rx="1.5" fill="{ctx.color((row+column)%6)}" opacity="{opacity}">{animate}</rect>')
    elif variant == 4:
        rows, columns = 20, 32
        cell_w, cell_h = (aw-48)/columns, (ah-48)/rows
        frames = precompute_gray_scott(ctx, rows, columns)
        display = frames[0] if ctx.full_motion else frames[len(frames) // 2]
        key_times = ";".join(fmt(index / (len(frames) - 1)) for index in range(len(frames)))

        def concentration_color(value: float) -> str:
            if value < .025:
                return str(ctx.palette["soft"])
            return ctx.color(min(5, max(0, int((value - .025) * 24))))

        for row in range(rows):
            for column in range(columns):
                colors = [concentration_color(frame[row][column]) for frame in frames]
                animate = smil(ctx, f'<animate attributeName="fill" values="{";".join(colors)}" keyTimes="{key_times}" calcMode="discrete" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
                body.append(f'<rect x="{fmt(x0+24+column*cell_w)}" y="{fmt(y0+24+row*cell_h)}" width="{fmt(cell_w+.35)}" height="{fmt(cell_h+.35)}" fill="{concentration_color(display[row][column])}">{animate}</rect>')
    else:
        records = precompute_dla(ctx)
        bound = max(1, max(max(abs(x), abs(y)) for (x, y), _parent in records))
        scale = min((aw - 80) / (2 * bound + 1), (ah - 68) / (2 * bound + 1))
        cx, cy = x0 + aw / 2, y0 + ah / 2
        for order, ((grid_x, grid_y), parent) in enumerate(records):
            px, py = cx + grid_x * scale, cy + grid_y * scale
            delay = -int(order / max(1, len(records) - 1) * ctx.duration_ms)
            if parent is not None:
                parent_x, parent_y = cx + parent[0] * scale, cy + parent[1] * scale
                style = css_animation(ctx, "psvg-draw", .5, delay, "ease-out")
                body.append(f'<path d="M {fmt(parent_x)} {fmt(parent_y)} L {fmt(px)} {fmt(py)}" pathLength="1" stroke="{ctx.color(order)}" stroke-width="{fmt(max(1.2, scale*.34))}" stroke-linecap="round" style="{style}"/>')
            style = css_animation(ctx, "psvg-seed", .5, delay, "ease-out")
            body.append(f'<circle cx="{fmt(px)}" cy="{fmt(py)}" r="{fmt(max(1.8, scale*.43))}" fill="{ctx.color(order+1)}" style="{style}"/>')
    return panel_frame(ctx,"".join(body),str(ctx.spec["signature"]))


def render_growth(ctx: Context) -> str:
    variant=int(ctx.spec["variant"])
    x0,y0,aw,ah=ctx.left,ctx.top,ctx.art_width,ctx.art_height
    body:list[str]=[]
    rng=ctx.rng("growth")
    if variant==0:
        segments=lsystem_segments(ctx,3)
        for order,(x1,y1,x2,y2,level) in enumerate(segments):
            style=css_animation(ctx,"psvg-draw",.65,-(level*520+(order%7)*14),"ease-out")
            body.append(f'<path d="M {fmt(x1)} {fmt(y1)} L {fmt(x2)} {fmt(y2)}" pathLength="1" stroke="{ctx.color(level+3)}" stroke-width="{fmt(max(1.2,7-level*.75))}" stroke-linecap="round" style="{style}"/>')
    elif variant==1:
        cx,cy=x0+aw/2,y0+ah/2
        golden=math.pi*(3-math.sqrt(5)); count=260
        max_radius=min(aw,ah)*.39
        for index in range(count):
            radius=max_radius*math.sqrt(index/max(1,count-1)); angle=index*golden
            px,py=cx+radius*math.cos(angle),cy+radius*math.sin(angle)
            size=2.4+3.2*(index/count)
            style=css_animation(ctx,"psvg-seed",.7,-index*9,"ease-out")
            body.append(f'<circle cx="{fmt(px)}" cy="{fmt(py)}" r="{fmt(size)}" fill="{ctx.color(index//24)}" style="{style}"/>')
    elif variant==2:
        start=(x0+aw*.16,y0+ah*.72); end=(x0+aw*.84,y0+ah*.28)
        def lightning(a:tuple[float,float],b:tuple[float,float],depth:int,order:int=0)->None:
            if depth==0:
                style=css_animation(ctx,"psvg-draw",.45,-order*18,"linear")
                body.append(f'<path d="M {fmt(a[0])} {fmt(a[1])} L {fmt(b[0])} {fmt(b[1])}" pathLength="1" stroke="{ctx.color(depth+4)}" stroke-width="{fmt(2.2+order%3)}" stroke-linecap="round" style="{style}"/>')
                return
            mx=(a[0]+b[0])/2+rng.uniform(-aw*.035,aw*.035); my=(a[1]+b[1])/2+rng.uniform(-ah*.04,ah*.04)
            lightning(a,(mx,my),depth-1,order*2); lightning((mx,my),b,depth-1,order*2+1)
            if depth in (2,3) and rng.random()>.45:
                angle=math.atan2(b[1]-a[1],b[0]-a[0])+rng.choice([-1,1])*rng.uniform(.45,.85)
                length=math.hypot(b[0]-a[0],b[1]-a[1])*.55
                lightning((mx,my),(mx+math.cos(angle)*length,my+math.sin(angle)*length),depth-1,order+31)
        lightning(start,end,5)
    elif variant==3:
        nodes,attractors=precompute_space_colonization(ctx)
        for index,(ax,ay) in enumerate(attractors):
            body.append(f'<circle cx="{fmt(ax)}" cy="{fmt(ay)}" r="{fmt(1.5 + index % 3 * .25)}" fill="{ctx.palette["muted"]}" opacity=".23"/>')
        for order,(x2,y2,parent,generation) in enumerate(nodes):
            if parent is None:
                continue
            x1,y1,_parent,_generation=nodes[parent]
            style=css_animation(ctx,"psvg-draw",.6,-order*35,"ease-out")
            width=max(1.35,7.5-generation*.11)
            body.append(f'<path d="M {fmt(x1)} {fmt(y1)} L {fmt(x2)} {fmt(y2)}" pathLength="1" fill="none" stroke="{ctx.color(generation)}" stroke-width="{fmt(width)}" stroke-linecap="round" style="{style}"/>')
    elif variant==4:
        cx,cy=x0+aw/2,y0+ah/2
        leaf=[]
        for index in range(101):
            t=index/100*math.pi
            leaf.append((cx+math.sin(t)*aw*.28,cy-ah*.38+index/100*ah*.76))
        for index in range(100,-1,-1):
            t=index/100*math.pi
            leaf.append((cx-math.sin(t)*aw*.28,cy-ah*.38+index/100*ah*.76))
        body.append(f'<path d="{path_from_points(leaf,True)}" fill="{ctx.palette["highlight"]}" stroke="{ctx.color(3)}" stroke-width="3"/>')
        body.append(f'<line x1="{fmt(cx)}" y1="{fmt(cy-ah*.36)}" x2="{fmt(cx)}" y2="{fmt(cy+ah*.36)}" stroke="{ctx.color(3)}" stroke-width="6"/>')
        for index in range(1,10):
            y=cy-ah*.34+index*ah*.068; span=aw*.25*math.sin(index/10*math.pi)
            for direction in (-1,1):
                x2=cx+direction*span
                style=css_animation(ctx,"psvg-draw",.55,-index*80,"ease-out")
                control=(cx+direction*span*.45,y-ah*.05); end=(x2,y-ah*.1)
                body.append(f'<path d="M {fmt(cx)} {fmt(y)} Q {fmt(control[0])} {fmt(control[1])} {fmt(end[0])} {fmt(end[1])}" pathLength="1" fill="none" stroke="{ctx.color(index)}" stroke-width="2.2" style="{style}"/>')
                for capillary_index,t in enumerate((.38,.62,.82)):
                    one_minus=1-t
                    px=one_minus*one_minus*cx+2*one_minus*t*control[0]+t*t*end[0]
                    py=one_minus*one_minus*y+2*one_minus*t*control[1]+t*t*end[1]
                    tangent_x=2*one_minus*(control[0]-cx)+2*t*(end[0]-control[0])
                    tangent_y=2*one_minus*(control[1]-y)+2*t*(end[1]-control[1])
                    magnitude=math.hypot(tangent_x,tangent_y) or 1
                    normal_x,normal_y=-tangent_y/magnitude,tangent_x/magnitude
                    side=1 if (capillary_index+index)%2==0 else -1
                    length=ah*(.024+.006*capillary_index)
                    cap_x=px+normal_x*length*side; cap_y=py+normal_y*length*side
                    capillary_style=css_animation(ctx,"psvg-draw",.55,-(index*3+capillary_index)*80,"ease-out")
                    body.append(f'<path d="M {fmt(px)} {fmt(py)} L {fmt(cap_x)} {fmt(cap_y)}" pathLength="1" fill="none" stroke="{ctx.color(index+2)}" stroke-width="1.25" stroke-linecap="round" style="{capillary_style}"/>')
    else:
        segments=branching_segments(ctx,6,.58,.2,True)
        for order,(x1,y1,x2,y2,level) in enumerate(segments):
            style=css_animation(ctx,"psvg-seed",.8,-(level*470+(order%9)*11),"ease-out")
            body.append(f'<path d="M {fmt(x1)} {fmt(y1)} Q {fmt((x1+x2)/2+rng.uniform(-8,8))} {fmt((y1+y2)/2)} {fmt(x2)} {fmt(y2)}" fill="none" stroke="{ctx.color(level+1)}" stroke-width="{fmt(max(1.5,9-level))}" stroke-linecap="round" style="{style}"/>')
    return panel_frame(ctx,"".join(body),str(ctx.spec["signature"]))


def render_tiling(ctx: Context) -> str:
    variant=int(ctx.spec["variant"])
    x0,y0,aw,ah=ctx.left,ctx.top,ctx.art_width,ctx.art_height
    body:list[str]=[]
    rng=ctx.rng("tiling")
    if variant==0:
        size=max(28,min(48,aw/14)); columns=int((aw-36)//size); rows=int((ah-36)//size)
        ox=x0+(aw-columns*size)/2; oy=y0+(ah-rows*size)/2
        for row in range(rows):
            for column in range(columns):
                x=ox+column*size; y=oy+row*size; flip=rng.random()>.5
                if flip:
                    arcs=[f'M {fmt(x)} {fmt(y+size/2)} A {fmt(size/2)} {fmt(size/2)} 0 0 1 {fmt(x+size/2)} {fmt(y)}',f'M {fmt(x+size)} {fmt(y+size/2)} A {fmt(size/2)} {fmt(size/2)} 0 0 1 {fmt(x+size/2)} {fmt(y+size)}']
                else:
                    arcs=[f'M {fmt(x)} {fmt(y+size/2)} A {fmt(size/2)} {fmt(size/2)} 0 0 0 {fmt(x+size/2)} {fmt(y+size)}',f'M {fmt(x+size)} {fmt(y+size/2)} A {fmt(size/2)} {fmt(size/2)} 0 0 0 {fmt(x+size/2)} {fmt(y)}']
                for arc in arcs:
                    style=css_animation(ctx,"psvg-conveyor",.7,-(row+column)*35,"linear")
                    body.append(f'<path d="{arc}" pathLength="1" fill="none" stroke="{ctx.color(row+column)}" stroke-width="4" stroke-dasharray=".18 .07" style="{style}"/>')
    elif variant==1:
        radius=min(aw/18,ah/13); dx=radius*math.sqrt(3); dy=radius*1.5
        rows=int((ah-30)//dy); columns=int((aw-30)//dx)
        center=(x0+aw/2,y0+ah/2)
        for row in range(rows):
            for column in range(columns):
                cx=x0+24+column*dx+(row%2)*dx/2; cy=y0+24+row*dy
                distance=math.hypot(cx-center[0],cy-center[1]); angle=(math.atan2(cy-center[1],cx-center[0])+math.tau)%math.tau
                phase=(distance/max(1,math.hypot(aw/2,ah/2))+.55*angle/math.tau)%1
                delay=-int(phase*ctx.duration_ms)
                style=css_animation(ctx,"psvg-wave",.7,delay,"ease-in-out")
                body.append(f'<polygon points="{regular_polygon(cx,cy,radius*.88,6,0)}" fill="{ctx.color(int(phase*12))}" opacity=".66" style="{style}"/>')
    elif variant==2:
        sites=[(rng.uniform(x0+40,x0+aw-40),rng.uniform(y0+36,y0+ah-36)) for _ in range(10)]
        columns,rows=34,22; cw,ch=(aw-32)/columns,(ah-32)/rows
        for row in range(rows):
            for column in range(columns):
                cx=x0+16+(column+.5)*cw; cy=y0+16+(row+.5)*ch
                owner=min(range(len(sites)),key=lambda i:(cx-sites[i][0])**2+(cy-sites[i][1])**2)
                style=css_animation(ctx,"psvg-cell-state",.85,-owner*140,"ease-in-out")
                body.append(f'<rect x="{fmt(cx-cw/2)}" y="{fmt(cy-ch/2)}" width="{fmt(cw+.3)}" height="{fmt(ch+.3)}" fill="{ctx.color(owner)}" opacity=".42" style="{style}"/>')
        for index,(sx,sy) in enumerate(sites): body.append(f'<circle cx="{fmt(sx)}" cy="{fmt(sy)}" r="5" fill="{ctx.color(index)}" stroke="{ctx.palette["surface"]}" stroke-width="2"/>')
    elif variant==3:
        clip_id=ctx.ident(f"{slug_from_pattern(str(ctx.spec['id']))}-moire-clip")
        body.append(f'<defs><clipPath id="{clip_id}"><rect x="{fmt(x0+20)}" y="{fmt(y0+20)}" width="{fmt(aw-40)}" height="{fmt(ah-40)}" rx="8"/></clipPath></defs>')
        for layer in range(2):
            start = layer * 7
            end = start + (18 if layer == 0 else -23)
            animate=smil(ctx,f'<animateTransform attributeName="transform" type="rotate" values="{start} {fmt(x0+aw/2)} {fmt(y0+ah/2)};{end} {fmt(x0+aw/2)} {fmt(y0+ah/2)};{start} {fmt(x0+aw/2)} {fmt(y0+ah/2)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<g clip-path="url(#{clip_id})" opacity=".65" transform="rotate({start} {fmt(x0+aw/2)} {fmt(y0+ah/2)})">{animate}')
            for index in range(-18,40):
                px=x0+index*22
                body.append(f'<line x1="{fmt(px)}" y1="{fmt(y0-150)}" x2="{fmt(px)}" y2="{fmt(y0+ah+150)}" stroke="{ctx.color(layer+4)}" stroke-width="4"/>')
            body.append('</g>')
    elif variant==4:
        motif_id=ctx.ident(f"{slug_from_pattern(str(ctx.spec['id']))}-motif"); cx,cy=x0+aw/2,y0+ah/2; sectors=12; radius=min(aw,ah)*.38
        motif=f'<g id="{motif_id}"><path d="M {fmt(cx)} {fmt(cy)} Q {fmt(cx+radius*.34)} {fmt(cy-radius*.7)} {fmt(cx+radius*.72)} {fmt(cy-radius*.26)} Q {fmt(cx+radius*.38)} {fmt(cy-radius*.02)} {fmt(cx)} {fmt(cy)} Z" fill="{ctx.color(4)}" opacity=".64"/><circle cx="{fmt(cx+radius*.52)}" cy="{fmt(cy-radius*.28)}" r="{fmt(radius*.08)}" fill="{ctx.color(1)}"/></g>'
        body.append(f'<defs>{motif}</defs>')
        rotation=smil(ctx,f'<animateTransform attributeName="transform" type="rotate" from="0 {fmt(cx)} {fmt(cy)}" to="360 {fmt(cx)} {fmt(cy)}" dur="{fmt(ctx.duration_ms/1000*2)}s" repeatCount="indefinite"/>')
        body.append(f'<g>{rotation}')
        for index in range(sectors):
            reflection=-1 if index%2 else 1
            transform=f'translate({fmt(cx)} {fmt(cy)}) rotate({fmt(index*360/sectors)}) scale(1 {reflection}) translate({fmt(-cx)} {fmt(-cy)})'
            body.append(f'<use href="#{motif_id}" transform="{transform}"/>')
        body.append('</g>')
    else:
        columns,rows=37,24; spacing_x=(aw-46)/(columns-1); spacing_y=(ah-46)/(rows-1); axes=5
        for row in range(rows):
            for column in range(columns):
                x=x0+23+column*spacing_x; y=y0+23+row*spacing_y; nx=(x-(x0+aw/2))/aw; ny=(y-(y0+ah/2))/ah
                value=sum(math.cos((nx*math.cos(k*math.pi/axes)+ny*math.sin(k*math.pi/axes))*70) for k in range(axes))
                if value>1.0:
                    radius=1.5+min(5,(value-1)*1.2); style=css_animation(ctx,"psvg-seed",.75,-int((row+column)*9),"ease-in-out")
                    body.append(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(radius)}" fill="{ctx.color(int(value*2))}" style="{style}"/>')
    return panel_frame(ctx,"".join(body),str(ctx.spec["signature"]))


def render_paint(ctx: Context) -> str:
    variant=int(ctx.spec["variant"])
    x0,y0,aw,ah=ctx.left,ctx.top,ctx.art_width,ctx.art_height
    cx,cy=x0+aw/2,y0+ah/2
    body:list[str]=[]
    prefix=slug_from_pattern(str(ctx.spec["id"]))
    if variant==0:
        gradient_id=ctx.ident(f"{prefix}-gradient")
        stops=[]
        for index,offset in enumerate((0,.33,.66,1)):
            animate=smil(ctx,f'<animate attributeName="stop-color" values="{ctx.color(index)};{ctx.color(index+2)};{ctx.color(index)}" dur="{ctx.duration_s}" repeatCount="indefinite"/><animate attributeName="offset" values="{fmt(offset)};{fmt(min(1,offset+.18))};{fmt(offset)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            stops.append(f'<stop offset="{fmt(offset)}" stop-color="{ctx.color(index)}">{animate}</stop>')
        body.append(f'<defs><linearGradient id="{gradient_id}" x1="0" y1="0" x2="1" y2="1">{"".join(stops)}</linearGradient></defs>')
        body.append(f'<rect x="{fmt(x0+aw*.12)}" y="{fmt(y0+ah*.18)}" width="{fmt(aw*.76)}" height="{fmt(ah*.64)}" rx="{fmt(min(aw,ah)*.14)}" fill="url(#{gradient_id})"/>')
        for index in range(7): body.append(f'<circle cx="{fmt(x0+aw*(.2+index*.1))}" cy="{fmt(cy)}" r="{fmt(12+index*4)}" fill="none" stroke="{ctx.palette["surface"]}" stroke-width="3" opacity=".7"/>')
    elif variant==1:
        mask_id=ctx.ident(f"{prefix}-mask")
        animate=smil(ctx,f'<animate attributeName="x" values="{fmt(x0-aw*.7)};{fmt(x0+aw*.9)};{fmt(x0-aw*.7)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
        mask_x=x0-aw*.7 if ctx.full_motion else x0
        mask_width=aw*.8 if ctx.full_motion else aw
        body.append(f'<defs><mask id="{mask_id}"><rect x="{fmt(mask_x)}" y="{fmt(y0)}" width="{fmt(mask_width)}" height="{fmt(ah)}" fill="white">{animate}</rect></mask></defs>')
        for index in range(14):
            radius=min(aw,ah)*(.07+index*.014)
            body.append(f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(radius)}" fill="none" stroke="{ctx.color(index)}" stroke-width="12" mask="url(#{mask_id})"/>')
    elif variant==2:
        clip_id=ctx.ident(f"{prefix}-clip"); d1=f"M {fmt(cx-aw*.28)} {fmt(cy)} C {fmt(cx-aw*.28)} {fmt(cy-ah*.28)} {fmt(cx+aw*.28)} {fmt(cy-ah*.28)} {fmt(cx+aw*.28)} {fmt(cy)} C {fmt(cx+aw*.28)} {fmt(cy+ah*.28)} {fmt(cx-aw*.28)} {fmt(cy+ah*.28)} {fmt(cx-aw*.28)} {fmt(cy)} Z"; d2=f"M {fmt(cx-aw*.32)} {fmt(cy)} C {fmt(cx-aw*.08)} {fmt(cy-ah*.35)} {fmt(cx+aw*.08)} {fmt(cy-ah*.35)} {fmt(cx+aw*.32)} {fmt(cy)} C {fmt(cx+aw*.08)} {fmt(cy+ah*.35)} {fmt(cx-aw*.08)} {fmt(cy+ah*.35)} {fmt(cx-aw*.32)} {fmt(cy)} Z"
        animate=smil(ctx,f'<animate attributeName="d" values="{d1};{d2};{d1}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
        body.append(f'<defs><clipPath id="{clip_id}"><path d="{d1}">{animate}</path></clipPath></defs><g clip-path="url(#{clip_id})">')
        for index in range(22): body.append(f'<rect x="{fmt(x0+index*aw/22)}" y="{fmt(y0)}" width="{fmt(aw/22+1)}" height="{fmt(ah)}" fill="{ctx.color(index)}"/>')
        body.append('</g>')
    elif variant==3:
        filter_id=ctx.ident(f"{prefix}-warp"); turbulence=smil(ctx,f'<animate attributeName="baseFrequency" values="0.008 0.025;0.022 0.008;0.008 0.025" dur="{ctx.duration_s}" repeatCount="indefinite"/>'); scale=smil(ctx,f'<animate attributeName="scale" values="8;34;8" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
        body.append(f'<defs><filter id="{filter_id}" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.008 0.025" numOctaves="2" seed="{abs(ctx.seed)%999}" result="noise">{turbulence}</feTurbulence><feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="B">{scale}</feDisplacementMap></filter></defs>')
        body.append(f'<g filter="url(#{filter_id})">')
        for index in range(13):
            y=y0+32+index*(ah-64)/12; points=[]
            for sample in range(80):
                x=x0+24+sample/79*(aw-48); yy=y+14*math.sin(sample*.23+index*.8); points.append((x,yy))
            body.append(f'<path d="{path_from_points(points)}" fill="none" stroke="{ctx.color(index)}" stroke-width="8" opacity=".65"/>')
        body.append('</g>')
    elif variant==4:
        filter_id=ctx.ident(f"{prefix}-goo"); blobs=[]
        for index in range(7):
            bx=cx+(index-3)*aw*.08; by=cy+math.sin(index)*ah*.08; dx=(-1 if index%2 else 1)*aw*.18
            blobs.append((index,bx,by,dx,math.cos(index)*ah*.14,34+index%3*8))
        body.append(f'<defs><filter id="{filter_id}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="16" result="blur"/><feColorMatrix in="blur" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 28 -12"/></filter></defs><g filter="url(#{filter_id})">')
        for index,bx,by,dx,dy,radius in blobs:
            ax=smil(ctx,f'<animate attributeName="cx" values="{fmt(bx)};{fmt(bx+dx)};{fmt(bx)}" dur="{fmt(ctx.duration_ms/1000*(.7+index*.05))}s" repeatCount="indefinite"/>'); ay=smil(ctx,f'<animate attributeName="cy" values="{fmt(by)};{fmt(by+math.cos(index)*ah*.14)};{fmt(by)}" dur="{fmt(ctx.duration_ms/1000*(.85+index*.04))}s" repeatCount="indefinite"/>')
            body.append(f'<circle cx="{fmt(bx)}" cy="{fmt(by)}" r="{fmt(radius)}" fill="{ctx.color(index)}">{ax}{ay}</circle>')
        body.append('</g>')
        for index,bx,by,dx,dy,radius in blobs:
            ax=smil(ctx,f'<animate attributeName="cx" values="{fmt(bx)};{fmt(bx+dx)};{fmt(bx)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>'); ay=smil(ctx,f'<animate attributeName="cy" values="{fmt(by)};{fmt(by+dy)};{fmt(by)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
            body.append(f'<circle cx="{fmt(bx)}" cy="{fmt(by)}" r="{fmt(radius*.72)}" fill="none" stroke="{ctx.palette["surface"]}" stroke-width="2" opacity=".72">{ax}{ay}</circle>')
    else:
        filter_id=ctx.ident(f"{prefix}-light"); light=smil(ctx,f'<animate attributeName="x" values="{fmt(x0)};{fmt(x0+aw)};{fmt(x0)}" dur="{ctx.duration_s}" repeatCount="indefinite"/>')
        body.append(f'<defs><filter id="{filter_id}" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".018" numOctaves="2" seed="{abs(ctx.seed)%997}" result="height"/><feSpecularLighting in="height" surfaceScale="4" specularConstant=".8" specularExponent="18" lighting-color="{ctx.palette["surface"]}" result="spec"><fePointLight x="{fmt(x0)}" y="{fmt(cy)}" z="140">{light}</fePointLight></feSpecularLighting><feComposite in="spec" in2="SourceGraphic" operator="in" result="lit"/><feBlend in="SourceGraphic" in2="lit" mode="screen"/></filter></defs>')
        points=[]
        for index in range(160):
            t=index/159*math.tau; radius=min(aw,ah)*(.28+.05*math.sin(7*t)); points.append((cx+radius*math.cos(t),cy+radius*math.sin(t)))
        body.append(f'<path d="{path_from_points(points,True)}" fill="{ctx.color(4)}" stroke="{ctx.color(5)}" stroke-width="7" filter="url(#{filter_id})"/>')
    return panel_frame(ctx,"".join(body),str(ctx.spec["signature"]))


def render_composition(ctx: Context) -> str:
    variant = int(ctx.spec["variant"])
    x0, y0, aw, ah = ctx.left, ctx.top, ctx.art_width, ctx.art_height
    body: list[str] = []

    if variant == 0:
        # A shared master clock advances breadth-first through this small DAG.
        nodes = [
            (x0 + aw * .12, y0 + ah * .5),
            (x0 + aw * .32, y0 + ah * .25),
            (x0 + aw * .32, y0 + ah * .75),
            (x0 + aw * .57, y0 + ah * .5),
            (x0 + aw * .82, y0 + ah * .25),
            (x0 + aw * .82, y0 + ah * .75),
        ]
        node_depths = [0, 1, 1, 2, 3, 3]
        links = [(0, 1, 0), (0, 2, 0), (1, 3, 1), (2, 3, 1), (3, 4, 2), (3, 5, 2)]
        for index, (source, target, depth) in enumerate(links):
            route_id = ctx.ident(f"pulse-link-{index}")
            x1, y1 = nodes[source]
            x2, y2 = nodes[target]
            route = (
                f"M {fmt(x1)} {fmt(y1)} C {fmt((x1 + x2) / 2)} {fmt(y1)} "
                f"{fmt((x1 + x2) / 2)} {fmt(y2)} {fmt(x2)} {fmt(y2)}"
            )
            reveal_start = .08 + depth * .2
            reveal_end = reveal_start + .11
            dash_attributes = ' pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"' if ctx.full_motion else ""
            reveal = smil(
                ctx,
                f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" '
                f'keyTimes="0;{fmt(reveal_start)};{fmt(reveal_end)};.92;1" '
                f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            body.append(
                f'<path id="{route_id}" d="{route}" fill="none" stroke="{ctx.palette["line"]}" '
                f'stroke-width="5"{dash_attributes}>{reveal}</path>'
            )
            if ctx.full_motion:
                emit = reveal_end
                arrive = emit + .13
                motion = smil(
                    ctx,
                    f'<animateMotion keyPoints="0;0;1;1;0" '
                    f'keyTimes="0;{fmt(emit)};{fmt(arrive)};.93;1" calcMode="linear" '
                    f'dur="{ctx.duration_s}" repeatCount="indefinite"><mpath href="#{route_id}"/></animateMotion>',
                )
                visibility = smil(
                    ctx,
                    f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                    f'keyTimes="0;{fmt(emit)};{fmt(emit + .01)};{fmt(arrive)};{fmt(arrive + .015)};1" '
                    f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
                )
                body.append(f'<circle r="7" fill="{ctx.color(index)}" opacity="0">{motion}{visibility}</circle>')
        for index, ((x, y), depth) in enumerate(zip(nodes, node_depths)):
            activation = .07 if depth == 0 else .19 + (depth - 1) * .2 + .13
            settle = min(.87, activation + .12)
            pulse = smil(
                ctx,
                f'<animate attributeName="r" values="22;22;32;25;25;22" '
                f'keyTimes="0;{fmt(activation)};{fmt(activation + .035)};{fmt(settle)};.9;1" '
                f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            body.append(
                f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="25" fill="{ctx.color(index)}" '
                f'stroke="{ctx.palette["surface"]}" stroke-width="5">{pulse}</circle>'
                f'<text x="{fmt(x)}" y="{fmt(y + 5)}" text-anchor="middle" class="psvg-node-label">{index + 1}</text>'
            )

    elif variant == 1:
        # Reveal branch levels first, then transport tokens along complete root-to-leaf paths.
        segments = branching_segments(ctx, 5, .5, .08)
        endpoint_to_index = {(x2, y2): index for index, (_x1, _y1, x2, y2, _level) in enumerate(segments)}
        starts = {(x1, y1) for x1, y1, _x2, _y2, _level in segments}
        parents = [endpoint_to_index.get((x1, y1)) for x1, y1, _x2, _y2, _level in segments]
        leaf_indices = [index for index, (_x1, _y1, x2, y2, _level) in enumerate(segments) if (x2, y2) not in starts]

        for order, (x1, y1, x2, y2, level) in enumerate(segments):
            reveal_start = .04 + level * .055
            reveal_end = reveal_start + .08
            dash_attributes = ' pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"' if ctx.full_motion else ""
            reveal = smil(
                ctx,
                f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" '
                f'keyTimes="0;{fmt(reveal_start)};{fmt(reveal_end)};.9;1" '
                f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            reset_fade = smil(
                ctx,
                f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.88;.92;.98;1" '
                f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            body.append(
                f'<path d="M {fmt(x1)} {fmt(y1)} L {fmt(x2)} {fmt(y2)}" fill="none" '
                f'stroke="{ctx.color(level)}" stroke-width="{fmt(max(2, 8 - level))}" '
                f'stroke-linecap="round"{dash_attributes}>{reveal}{reset_fade}</path>'
            )

        if ctx.full_motion and leaf_indices:
            stride = max(1, len(leaf_indices) // 10)
            selected_leaves = leaf_indices[::stride][:12]
            for route_index, leaf_index in enumerate(selected_leaves):
                chain: list[tuple[float, float]] = []
                current: int | None = leaf_index
                while current is not None:
                    x1, y1, x2, y2, _level = segments[current]
                    if not chain:
                        chain.append((x2, y2))
                    chain.append((x1, y1))
                    current = parents[current]
                chain.reverse()
                route_id = ctx.ident(f"growth-flow-route-{route_index}")
                route = path_from_points(chain)
                route_visibility = smil(
                    ctx,
                    f'<animate attributeName="opacity" values="0;0;.28;.28;0;0" '
                    f'keyTimes="0;.46;.5;.87;.91;1" dur="{ctx.duration_s}" repeatCount="indefinite"/>',
                )
                body.append(
                    f'<path id="{route_id}" d="{route}" fill="none" stroke="{ctx.palette["surface"]}" '
                    f'stroke-width="2" opacity="0">{route_visibility}</path>'
                )
                flow_start = .48 + (route_index % 6) * .025
                flow_end = flow_start + .28
                motion = smil(
                    ctx,
                    f'<animateMotion keyPoints="0;0;1;1;0" '
                    f'keyTimes="0;{fmt(flow_start)};{fmt(flow_end)};.92;1" calcMode="linear" '
                    f'dur="{ctx.duration_s}" repeatCount="indefinite"><mpath href="#{route_id}"/></animateMotion>',
                )
                visibility = smil(
                    ctx,
                    f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                    f'keyTimes="0;{fmt(flow_start)};{fmt(flow_start + .01)};{fmt(flow_end)};{fmt(flow_end + .015)};1" '
                    f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
                )
                body.append(
                    f'<circle r="4" fill="{ctx.palette["surface"]}" stroke="{ctx.color(route_index)}" '
                    f'stroke-width="2" opacity="0">{motion}{visibility}</circle>'
                )

    elif variant == 2:
        # Two sampled field states drive orientation, opacity, and compatible four-point glyph geometry.
        rows, columns = 7, 12

        def glyph_path(magnitude: float) -> str:
            blend = max(0.0, min(1.0, magnitude))
            width = 7 + blend * 4
            height = 9 - blend * 1.5
            diamond = [(-width, 0.0), (0.0, -height), (width, 0.0), (0.0, height)]
            rectangle = [(-width, -height * .62), (width, -height * .62), (width, height * .62), (-width, height * .62)]
            points = [
                (dx * (1 - blend) + rx * blend, dy * (1 - blend) + ry * blend)
                for (dx, dy), (rx, ry) in zip(diamond, rectangle)
            ]
            return path_from_points(points, True)

        for row in range(rows):
            for column in range(columns):
                x = x0 + 55 + column * (aw - 110) / (columns - 1)
                y = y0 + 42 + row * (ah - 84) / (rows - 1)
                nx = (x - (x0 + aw / 2)) / (aw / 2)
                ny = (y - (y0 + ah / 2)) / (ah / 2)
                vx0, vy0 = vector_at(nx, ny, 0)
                vx1, vy1 = vector_at(nx, ny, math.pi)
                magnitude0 = min(1.0, math.hypot(vx0, vy0))
                magnitude1 = min(1.0, math.hypot(vx1, vy1))
                angle0 = math.degrees(math.atan2(vy0, vx0))
                angle1 = math.degrees(math.atan2(vy1, vx1))
                d0 = glyph_path(magnitude0)
                d1 = glyph_path(magnitude1)
                morph = smil(
                    ctx,
                    f'<animate attributeName="d" values="{d0};{d1};{d0}" keyTimes="0;.5;1" '
                    f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
                )
                turn = smil(
                    ctx,
                    f'<animateTransform attributeName="transform" type="rotate" '
                    f'values="{fmt(angle0)};{fmt(angle1)};{fmt(angle0)}" keyTimes="0;.5;1" '
                    f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
                )
                opacity = smil(
                    ctx,
                    f'<animate attributeName="opacity" values="{fmt(.3 + .7 * magnitude0)};'
                    f'{fmt(.3 + .7 * magnitude1)};{fmt(.3 + .7 * magnitude0)}" keyTimes="0;.5;1" '
                    f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
                )
                body.append(
                    f'<g transform="translate({fmt(x)} {fmt(y)})"><g transform="rotate({fmt(angle0)})">{turn}'
                    f'<path d="{d0}" fill="{ctx.color(row + column)}" opacity="{fmt(.3 + .7 * magnitude0)}">'
                    f'{morph}{opacity}</path></g></g>'
                )

    elif variant == 3:
        # The visible linkage and the precomputed endpoint trace use the same nested-frame equations.
        cx, cy = x0 + aw / 2, y0 + ah / 2
        scale = min(aw, ah)
        radii = [scale * .21, scale * .135, scale * .085]
        frequencies = [1, -2, 3]
        phases = [0.0, .62, -.38]
        trace_points: list[tuple[float, float]] = []
        for sample in range(361):
            t = sample / 360
            px, py = cx, cy
            cumulative = 0.0
            for radius, frequency, phase in zip(radii, frequencies, phases):
                cumulative += phase + math.tau * frequency * t
                px += radius * math.cos(cumulative)
                py += radius * math.sin(cumulative)
            trace_points.append((px, py))
        trace = path_from_points(trace_points, True)
        draw_style = css_animation(ctx, "psvg-draw", 1.0, 0, "ease-in-out")
        body.append(
            f'<path d="{trace}" pathLength="1" fill="none" stroke="{ctx.palette["line"]}" '
            f'stroke-width="3" style="{draw_style}"/>'
        )
        if ctx.full_motion:
            for echo in range(6):
                trail_style = css_animation(ctx, "psvg-conveyor", 1.0, -echo * 130, "linear")
                body.append(
                    f'<path d="{trace}" pathLength="1" fill="none" stroke="{ctx.color(echo + 1)}" '
                    f'stroke-width="{fmt(7 - echo * .8)}" stroke-linecap="round" '
                    f'stroke-dasharray=".035 .965" opacity="{fmt(.62 - echo * .085)}" style="{trail_style}"/>'
                )

        chain = [f'<g transform="translate({fmt(cx)} {fmt(cy)})">']
        for index, (radius, frequency, phase) in enumerate(zip(radii, frequencies, phases)):
            phase_degrees = float(fmt(math.degrees(phase)))
            turn = smil(
                ctx,
                f'<animateTransform attributeName="transform" type="rotate" '
                f'from="{fmt(phase_degrees)}" to="{fmt(phase_degrees + 360 * frequency)}" '
                f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            chain.append(
                f'<g transform="rotate({fmt(phase_degrees)})">{turn}'
                f'<circle cx="0" cy="0" r="{fmt(radius)}" fill="none" stroke="{ctx.color(index + 3)}" '
                f'stroke-width="2" opacity=".3"/>'
                f'<line x1="0" y1="0" x2="{fmt(radius)}" y2="0" stroke="{ctx.palette["ink"]}" '
                f'stroke-width="{fmt(5 - index)}" stroke-linecap="round"/>'
                f'<circle cx="{fmt(radius)}" cy="0" r="{fmt(10 - index * 2)}" fill="{ctx.color(index)}"/>'
                f'<g transform="translate({fmt(radius)} 0)">'
            )
        chain.append(f'<circle cx="0" cy="0" r="8" fill="{ctx.palette["surface"]}" stroke="{ctx.color(0)}" stroke-width="3"/>')
        chain.append('</g></g>' * len(radii))
        chain.append('</g>')
        body.append("".join(chain))

    elif variant == 4:
        # Four-neighbor breadth-first distance bends around two deterministic barriers.
        columns, rows = 14, 9
        size = min((aw - 54) / columns, (ah - 48) / rows)
        ox = x0 + (aw - columns * size) / 2
        oy = y0 + (ah - rows * size) / 2
        source = (1, rows // 2)
        blocked: set[tuple[int, int]] = set()
        for column, gate in ((4, 2), (9, 6)):
            for row in range(rows):
                if row not in (gate, gate + 1):
                    blocked.add((column, row))
        distances = {source: 0}
        queue = [source]
        cursor = 0
        while cursor < len(queue):
            column, row = queue[cursor]
            cursor += 1
            for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                neighbor = (column + dc, row + dr)
                if not (0 <= neighbor[0] < columns and 0 <= neighbor[1] < rows):
                    continue
                if neighbor in blocked or neighbor in distances:
                    continue
                distances[neighbor] = distances[(column, row)] + 1
                queue.append(neighbor)
        maximum_distance = max(distances.values())
        for row in range(rows):
            for column in range(columns):
                cx = ox + (column + .5) * size
                cy = oy + (row + .5) * size
                points = regular_polygon(cx, cy, size * .42, 4, math.pi / 4)
                cell = (column, row)
                if cell in blocked:
                    body.append(
                        f'<polygon points="{points}" fill="{ctx.palette["soft"]}" stroke="{ctx.palette["line"]}" '
                        f'stroke-width="1" opacity=".72"/>'
                    )
                    continue
                distance = distances[cell]
                phase = distance / maximum_distance
                activation = .06 + phase * .68
                peak = activation + .055
                settle = peak + .065
                wave = smil(
                    ctx,
                    f'<animate attributeName="opacity" values=".3;.3;1;.45;.3" '
                    f'keyTimes="0;{fmt(activation)};{fmt(peak)};{fmt(settle)};1" '
                    f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
                )
                body.append(
                    f'<polygon points="{points}" fill="{ctx.color(distance)}" opacity=".3" '
                    f'stroke="{ctx.palette["surface"]}" stroke-width="1">{wave}</polygon>'
                )
        source_x = ox + (source[0] + .5) * size
        source_y = oy + (source[1] + .5) * size
        body.append(
            f'<circle cx="{fmt(source_x)}" cy="{fmt(source_y)}" r="{fmt(size * .16)}" '
            f'fill="{ctx.palette["surface"]}" stroke="{ctx.color(0)}" stroke-width="3"/>'
        )

    else:
        # One four-state clock coordinates the cards, route reveals, tokens, and a masked focus spotlight.
        stages = [
            ("CONTEXT", x0 + aw * .14, ctx.color(4), .04, .22),
            ("TRANSITION", x0 + aw * .39, ctx.color(1), .26, .42),
            ("FOCUS", x0 + aw * .65, ctx.color(0), .47, .66),
            ("RESET", x0 + aw * .87, ctx.color(3), .71, .88),
        ]
        y = y0 + ah * .52
        focus_mask_id = ctx.ident("stateful-focus-mask")
        focus_positions = ";".join(fmt(stage[1]) for stage in stages) + f";{fmt(stages[0][1])}"
        spotlight_motion = smil(
            ctx,
            f'<animate attributeName="cx" values="{focus_positions}" keyTimes="0;.26;.47;.71;1" '
            f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
        )
        body.append(
            f'<defs><mask id="{focus_mask_id}" maskUnits="userSpaceOnUse" '
            f'x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(aw)}" height="{fmt(ah)}">'
            f'<rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(aw)}" height="{fmt(ah)}" fill="black"/>'
            f'<circle cx="{fmt(stages[0][1])}" cy="{fmt(y)}" r="68" fill="white">{spotlight_motion}</circle>'
            f'</mask></defs>'
        )

        route_windows = [(.18, .3), (.38, .5), (.6, .72), (.82, .94)]
        route_ids: list[str] = []
        for index in range(4):
            source_x = stages[index][1]
            target_x = stages[(index + 1) % 4][1]
            if index < 3:
                route = (
                    f"M {fmt(source_x + 48)} {fmt(y)} C {fmt((source_x + target_x) / 2)} {fmt(y - ah * .18)} "
                    f"{fmt((source_x + target_x) / 2)} {fmt(y + ah * .18)} {fmt(target_x - 48)} {fmt(y)}"
                )
            else:
                route = (
                    f"M {fmt(source_x)} {fmt(y + 48)} Q {fmt(x0 + aw * .5)} {fmt(y0 + ah * .94)} "
                    f"{fmt(target_x)} {fmt(y + 48)}"
                )
            route_id = ctx.ident(f"state-route-{index}")
            route_ids.append(route_id)
            start, finish = route_windows[index]
            dash_attributes = ' pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"' if ctx.full_motion else ""
            reveal = smil(
                ctx,
                f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" '
                f'keyTimes="0;{fmt(start)};{fmt(finish)};.96;1" '
                f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            body.append(
                f'<path id="{route_id}" d="{route}" fill="none" stroke="{ctx.palette["line"]}" '
                f'stroke-width="6" stroke-linecap="round"{dash_attributes}>{reveal}</path>'
            )
            if ctx.full_motion:
                motion = smil(
                    ctx,
                    f'<animateMotion keyPoints="0;0;1;1;0" keyTimes="0;{fmt(start)};{fmt(finish)};.96;1" '
                    f'calcMode="linear" dur="{ctx.duration_s}" repeatCount="indefinite">'
                    f'<mpath href="#{route_id}"/></animateMotion>',
                )
                visibility = smil(
                    ctx,
                    f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
                    f'keyTimes="0;{fmt(start)};{fmt(start + .01)};{fmt(finish)};{fmt(finish + .01)};1" '
                    f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
                )
                body.append(f'<circle r="7" fill="{stages[(index + 1) % 4][2]}" opacity="0">{motion}{visibility}</circle>')

        for label, x, color, active_start, active_end in stages:
            active = smil(
                ctx,
                f'<animate attributeName="opacity" values=".48;.48;1;1;.48;.48" '
                f'keyTimes="0;{fmt(active_start)};{fmt(active_start + .02)};{fmt(active_end)};{fmt(active_end + .02)};1" '
                f'dur="{ctx.duration_s}" repeatCount="indefinite"/>',
            )
            body.append(
                f'<rect x="{fmt(x - 48)}" y="{fmt(y - 38)}" width="96" height="76" rx="12" '
                f'fill="{color}" opacity=".48" stroke="{ctx.palette["surface"]}" stroke-width="4">{active}</rect>'
                f'<text x="{fmt(x)}" y="{fmt(y + 5)}" text-anchor="middle" class="psvg-node-label">{label}</text>'
            )
        body.append(f'<g mask="url(#{focus_mask_id})" pointer-events="none">')
        for _label, x, color, _active_start, _active_end in stages:
            body.append(
                f'<rect x="{fmt(x - 55)}" y="{fmt(y - 45)}" width="110" height="90" rx="16" '
                f'fill="none" stroke="{color}" stroke-width="8" opacity=".9"/>'
            )
        body.append('</g>')

    return panel_frame(ctx, "".join(body), str(ctx.spec["signature"]))


RENDERERS: dict[str, Callable[[Context], str]] = {
    "timing": render_timing,
    "transform": render_transform,
    "path": render_path,
    "parametric": render_parametric,
    "field": render_field,
    "simulation": render_simulation,
    "growth": render_growth,
    "tiling": render_tiling,
    "paint": render_paint,
    "composition": render_composition,
}


def common_style(ctx: Context) -> str:
    animation_css = ""
    if ctx.full_motion:
        animation_css = """
@keyframes psvg-wave{0%,100%{transform:scale(.72);opacity:.42}50%{transform:scale(1.28);opacity:1}}
@keyframes psvg-travel{0%,100%{transform:translateX(0)}50%{transform:translateX(var(--psvg-distance))}}
@keyframes psvg-travel-overshoot{0%,100%{transform:translateX(0)}8%,92%{transform:translateX(-14px)}45%,55%{transform:translateX(calc(var(--psvg-distance) + 18px))}50%{transform:translateX(var(--psvg-distance))}}
@keyframes psvg-travel-asymmetric{0%,100%{transform:translateX(0)}28%,66%{transform:translateX(var(--psvg-distance))}}
@keyframes psvg-crossfade-a{0%,100%{opacity:.18;transform:scale(.86)}50%{opacity:.78;transform:scale(1.06)}}
@keyframes psvg-crossfade-b{0%,100%{opacity:.78;transform:scale(1.06)}50%{opacity:.18;transform:scale(.86)}}
@keyframes psvg-parallax{0%,100%{transform:translateX(calc(var(--psvg-shift)*-1))}50%{transform:translateX(var(--psvg-shift))}}
@keyframes psvg-draw{0%,10%,100%{stroke-dasharray:1;stroke-dashoffset:1}55%,78%{stroke-dasharray:1;stroke-dashoffset:0}}
@keyframes psvg-conveyor{to{stroke-dashoffset:-1}}
@keyframes psvg-trim{0%{stroke-dasharray:.16 .84;stroke-dashoffset:.2}100%{stroke-dasharray:.16 .84;stroke-dashoffset:-.8}}
@keyframes psvg-ribbon{0%,100%{transform:translateX(-9px);opacity:.4}50%{transform:translateX(9px);opacity:.9}}
@keyframes psvg-contour{0%,100%{transform:scale(.88);opacity:.18}50%{transform:scale(1.1);opacity:.62}}
@keyframes psvg-cell-state{0%,100%{opacity:.28}50%{opacity:.95}}
@keyframes psvg-rd{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes psvg-seed{0%,8%,100%{transform:scale(.35);opacity:.25}48%,78%{transform:scale(1);opacity:1}}
@keyframes psvg-tile-wave{0%,100%{transform:scale(.72) rotate(0deg);opacity:.32}50%{transform:scale(1.12) rotate(45deg);opacity:.92}}
@keyframes psvg-state-card{0%,18%,100%{opacity:.38;transform:scale(.94)}35%,58%{opacity:1;transform:scale(1.08)}75%{opacity:.62;transform:scale(1)}}
"""
    return f"""
:root{{color-scheme:light}}
*{{box-sizing:border-box}}
.psvg-panel{{fill:{ctx.palette['surface']};stroke:{ctx.palette['line']};stroke-width:1.5}}
.psvg-guide{{fill:none;stroke:{ctx.palette['line']};stroke-width:2}}
.psvg-title{{font:700 24px Arial,sans-serif;fill:{ctx.palette['ink']}}}
.psvg-subtitle{{font:13px Arial,sans-serif;fill:{ctx.palette['muted']}}}
.psvg-kicker{{font:700 11px Arial,sans-serif;letter-spacing:1.2px;fill:{ctx.color(0)}}}
.psvg-label{{font:600 13px Arial,sans-serif;fill:{ctx.palette['ink']}}}
.psvg-node-label{{font:700 10px Arial,sans-serif;fill:{ctx.palette['surface']};pointer-events:none}}
.psvg-note{{font:11px Arial,sans-serif;fill:{ctx.palette['muted']}}}
.psvg-cell,.psvg-art circle,.psvg-art rect,.psvg-art path,.psvg-art polygon{{transform-box:fill-box;transform-origin:center}}
.psvg-reduced-layer{{display:none}}
{animation_css}
@media(prefers-reduced-motion:reduce){{.psvg-motion-layer{{display:none!important}}.psvg-reduced-layer{{display:inline!important}}*{{animation:none!important}}}}
""".strip()


def build_svg(ctx: Context) -> str:
    renderer_name = str(ctx.spec["renderer"])
    renderer = RENDERERS.get(renderer_name)
    if renderer is None:
        raise RuntimeError(f"No renderer implementation for {renderer_name!r}.")
    pattern_id = str(ctx.spec["id"])
    slug = slug_from_pattern(pattern_id)
    title_id = f"{slug}-title"
    desc_id = f"{slug}-desc"
    animated_body = renderer(ctx)
    if ctx.full_motion:
        reduced_ctx = replace(ctx, motion="reduced", id_suffix="-reduced")
        reduced_body = renderer(reduced_ctx)
        body = (
            f'<g class="psvg-motion-layer" data-motion-layer="animated">{animated_body}</g>'
            f'<g class="psvg-reduced-layer" data-motion-layer="reduced">{reduced_body}</g>'
        )
    else:
        body = animated_body
    style = common_style(ctx)
    has_smil = "<animate" in body
    has_css_motion = "animation:" in body
    if not ctx.full_motion:
        motion_engine = "static"
    elif has_smil and has_css_motion:
        motion_engine = "mixed"
    elif has_smil:
        motion_engine = "smil"
    elif has_css_motion:
        motion_engine = "css"
    else:
        motion_engine = "static"
    attrs = {
        "xmlns": SVG_NS,
        "xmlns:xlink": XLINK_NS,
        "viewBox": f"0 0 {ctx.width} {ctx.height}",
        "width": str(ctx.width),
        "height": str(ctx.height),
        "role": "img",
        "aria-labelledby": f"{title_id} {desc_id}",
        "data-procedural-svg-version": "1",
        "data-pattern-id": pattern_id,
        "data-example-id": slug,
        "data-family": str(ctx.spec["family"]),
        "data-renderer": renderer_name,
        "data-variant": str(ctx.spec["variant"]),
        "data-seed": str(ctx.seed),
        "data-palette": ctx.palette_name,
        "data-motion": ctx.motion,
        "data-motion-engine": motion_engine,
        "data-duration-ms": str(ctx.duration_ms),
        "data-loop": "true" if ctx.full_motion else "false",
        "data-loop-contract": "master-phase" if ctx.full_motion else "static",
        "data-reduced-motion-fallback": "layered" if ctx.full_motion else "static",
        "data-driver": str(ctx.spec["driver"]),
        "data-technique": str(ctx.spec["technique"]),
        "data-deterministic": "true",
        "data-standalone": "true",
        "data-parameter-hash": parameter_hash(ctx),
    }
    attr_text = " ".join(f'{name}="{escape(value, quote=True)}"' for name, value in attrs.items())
    title = escape(str(ctx.spec["name"]))
    description = escape(str(ctx.spec["description"]))
    family = escape(str(ctx.spec["family"]).upper())
    technique = escape(str(ctx.spec["technique"]))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg {attr_text}>
  <title id="{title_id}">{title}</title>
  <desc id="{desc_id}">{description} Deterministic seed {ctx.seed}; {ctx.motion} motion.</desc>
  <style>{style}</style>
  <rect width="{ctx.width}" height="{ctx.height}" fill="{ctx.palette['background']}"/>
  <text class="psvg-kicker" x="40" y="34">{family} · {technique}</text>
  <text class="psvg-title" x="40" y="68">{title}</text>
  <text class="psvg-subtitle" x="40" y="92">seed {ctx.seed} · {ctx.duration_ms} ms · {escape(ctx.palette_name)} · {escape(ctx.motion)} motion</text>
  {body}
</svg>
'''


def parameter_hash(ctx: Context) -> str:
    payload = {
        "pattern": ctx.spec["id"],
        "seed": ctx.seed,
        "width": ctx.width,
        "height": ctx.height,
        "durationMs": ctx.duration_ms,
        "palette": ctx.palette_name,
        "motion": ctx.motion,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def write_exact(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Output already exists; pass --force to replace it: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_context(args: argparse.Namespace, spec: dict[str, object]) -> Context:
    return Context(
        spec=spec,
        seed=args.seed,
        width=args.width,
        height=args.height,
        duration_ms=args.duration_ms,
        palette_name=args.palette,
        palette=PALETTES[args.palette],
        motion=args.motion,
    )


def result_for(ctx: Context, output: Path) -> dict[str, object]:
    content = build_svg(ctx)
    write_exact(output, content, ctx_args_force.get())
    return {
        "patternId": ctx.spec["id"],
        "family": ctx.spec["family"],
        "renderer": ctx.spec["renderer"],
        "variant": ctx.spec["variant"],
        "seed": ctx.seed,
        "palette": ctx.palette_name,
        "motion": ctx.motion,
        "durationMs": ctx.duration_ms,
        "width": ctx.width,
        "height": ctx.height,
        "parameterHash": parameter_hash(ctx),
        "svgSha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "output": str(output.resolve()),
        "bytes": len(content.encode("utf-8")),
    }


class _ForceFlag:
    """Avoid threading a write-only flag through every renderer call."""

    value = False

    @classmethod
    def set(cls, value: bool) -> None:
        cls.value = value

    @classmethod
    def get(cls) -> bool:
        return cls.value


ctx_args_force = _ForceFlag


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build deterministic standalone procedural SVG animations.")
    parser.add_argument("pattern", nargs="?", help="Canonical procedural-svg-* pattern ID for one output.")
    parser.add_argument("--pattern", dest="pattern_option", help="Canonical pattern ID; alternative to the positional ID.")
    parser.add_argument("-o", "--output", type=Path, help="Exact SVG output path for one pattern.")
    parser.add_argument("--all", dest="all_directory", type=Path, metavar="DIRECTORY", help="Build all catalog patterns into this exact directory.")
    parser.add_argument("--list", action="store_true", help="List every bundled pattern.")
    parser.add_argument("--describe", metavar="PATTERN_ID", help="Describe one bundled pattern.")
    parser.add_argument("--seed", type=int, default=20260720, help="Deterministic signed integer seed.")
    parser.add_argument("--width", type=int, default=960, help="SVG width and viewBox width (320..4096).")
    parser.add_argument("--height", type=int, default=640, help="SVG height and viewBox height (240..4096).")
    parser.add_argument("--duration-ms", type=int, default=6000, help="Loop duration in milliseconds (400..120000).")
    parser.add_argument("--palette", choices=sorted(PALETTES), default="colorset2")
    parser.add_argument("--motion", choices=("full", "reduced"), default="full")
    motion_group = parser.add_mutually_exclusive_group()
    motion_group.add_argument("--full-motion", dest="motion", action="store_const", const="full", help="Emit full animation (default).")
    motion_group.add_argument("--reduced-motion", dest="motion", action="store_const", const="reduced", help="Emit a readable static reduced-motion state.")
    parser.add_argument("--report", type=Path, help="Optional exact JSON build-report path.")
    parser.add_argument("--force", action="store_true", help="Replace existing requested outputs.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    modes = sum(bool(value) for value in (args.list, args.describe, args.all_directory, args.pattern, args.pattern_option))
    if modes != 1:
        parser.error("Choose exactly one mode: --list, --describe ID, --all DIRECTORY, or one pattern ID.")
    if args.pattern and args.pattern_option:
        parser.error("Use either the positional pattern ID or --pattern, not both.")
    if not 320 <= args.width <= 4096:
        parser.error("--width must be between 320 and 4096.")
    if not 240 <= args.height <= 4096:
        parser.error("--height must be between 240 and 4096.")
    if not 400 <= args.duration_ms <= 120000:
        parser.error("--duration-ms must be between 400 and 120000.")
    if (args.pattern or args.pattern_option) and args.output is None:
        parser.error("One-pattern mode requires --output with the exact SVG path.")
    if args.output is not None and not (args.pattern or args.pattern_option):
        parser.error("--output is valid only in one-pattern mode.")
    if args.report is not None and (args.list or args.describe):
        parser.error("--report is valid only for generated output modes.")


def validate_write_targets(
    args: argparse.Namespace,
    patterns: dict[str, dict[str, object]],
) -> None:
    """Preflight every generated path so a batch cannot fail after partial writes."""

    if args.all_directory is not None:
        output_directory = args.all_directory.expanduser().resolve()
        if output_directory.exists() and not output_directory.is_dir():
            raise NotADirectoryError(f"--all target exists and is not a directory: {output_directory}")
        svg_paths = [
            args.all_directory.expanduser().resolve() / f"{pattern_id}.svg"
            for pattern_id in patterns
        ]
    else:
        svg_paths = [args.output.expanduser().resolve()]

    report_path = args.report.expanduser().resolve() if args.report is not None else None
    if report_path is not None:
        if args.all_directory is not None and report_path == args.all_directory.expanduser().resolve():
            raise ValueError(f"--report path collides with --all directory: {report_path}")
        if report_path in svg_paths:
            raise ValueError(
                f"--report path collides with generated SVG output: {report_path}"
            )
    targets = svg_paths + ([report_path] if report_path is not None else [])
    for target in targets:
        if target.exists() and target.is_dir():
            raise IsADirectoryError(f"Requested output path is a directory: {target}")
        if target.exists() and not args.force:
            raise FileExistsError(f"Refusing to overwrite existing output without --force: {target}")


def print_listing(patterns: dict[str, dict[str, object]], json_mode: bool) -> None:
    values = [
        {key: spec[key] for key in ("id", "name", "family", "renderer", "variant", "technique")}
        for spec in patterns.values()
    ]
    if json_mode:
        print(json.dumps({"ok": True, "count": len(values), "patterns": values}, indent=2))
    else:
        for item in values:
            print(f"{item['id']}\t{item['family']}\t{item['name']}")


def print_description(spec: dict[str, object], json_mode: bool) -> None:
    if json_mode:
        print(json.dumps({"ok": True, "pattern": spec}, indent=2))
        return
    for key in ("id", "name", "family", "renderer", "variant", "driver", "technique", "signature", "description"):
        print(f"{key}: {spec[key]}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    validate_args(parser, args)
    try:
        catalog, patterns = load_catalog()
        if args.list:
            print_listing(patterns, args.json)
            return 0
        if args.describe:
            spec = patterns.get(args.describe)
            if spec is None:
                raise KeyError(f"Unknown procedural pattern ID: {args.describe}")
            print_description(spec, args.json)
            return 0

        validate_write_targets(args, patterns)
        ctx_args_force.set(args.force)
        results: list[dict[str, object]] = []
        if args.all_directory:
            output_dir: Path = args.all_directory
            if output_dir.exists() and not output_dir.is_dir():
                raise NotADirectoryError(f"--all target exists and is not a directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)
            for pattern_id, spec in patterns.items():
                ctx = make_context(args, spec)
                results.append(result_for(ctx, output_dir / f"{pattern_id}.svg"))
        else:
            pattern_id = args.pattern_option or args.pattern
            spec = patterns.get(pattern_id)
            if spec is None:
                raise KeyError(f"Unknown procedural pattern ID: {pattern_id}")
            ctx = make_context(args, spec)
            results.append(result_for(ctx, args.output))

        report: dict[str, object] = {
            "ok": True,
            "catalogVersion": catalog.get("version"),
            "catalog": str(CATALOG_PATH.resolve()),
            "count": len(results),
            "outputs": results,
        }
        if args.report:
            write_exact(args.report, json.dumps(report, indent=2) + "\n", args.force)
            report["report"] = str(args.report.resolve())
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            if len(results) == 1:
                print(f"Built {results[0]['patternId']} at {results[0]['output']}.")
            else:
                print(f"Built {len(results)} procedural SVG patterns in {args.all_directory.resolve()}.")
        return 0
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        if args.json:
            print(json.dumps({"ok": False, "error": str(error)}, indent=2), file=sys.stderr)
        else:
            print(f"Procedural SVG build failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
