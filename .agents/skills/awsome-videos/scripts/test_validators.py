#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.45.0"]
# ///
"""Run fast regression tests for awsome-videos validators."""

from __future__ import annotations

import argparse
import copy
import hashlib
from io import BytesIO
import json
import re
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_production_package  # noqa: E402
import check_reference_completeness  # noqa: E402
import check_renderer_contract  # noqa: E402
import check_video_artifact  # noqa: E402
import check_video_brief  # noqa: E402
import check_visual_contract  # noqa: E402
import extract_voiceover_cues  # noqa: E402
import finalize_production_notes  # noqa: E402
import render_concept_video  # noqa: E402
import check_runtime_tools  # noqa: E402
import score_style_fidelity  # noqa: E402
import score_video_readiness  # noqa: E402
import scaffold_production_package  # noqa: E402
import select_video_patterns  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402


STRONG_BRIEF = """# What Is A Rate Limit?

Promise: Explain a rate limit as a token budget that protects a service and gives clients retry timing.
Audience: Developers who know HTTP and basic API clients.
Format: compressed explainer
Runtime: 1:10

## Hook

Cold-open line: Your API did not crash because users were bad; it crashed because every request got treated as free.
First visual: API gateway screenshot plus token bucket diagram proof visual.
Audio cue: Hit plus bed starts under voiceover.

## Timed Beat Table

| Time | Beat ID | Scene ID | Script purpose | Visual | Animation | Transition | Audio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0:00-0:05 | b01 | s01 | Claim and proof | API gateway source screenshot plus token bucket diagram | Smash scale-in | Hard cut | Hit plus bed starts |
| 0:05-0:12 | b02 | s02 | Definition | Docs excerpt and code header for X-RateLimit | Highlight sweep | Punch-in | Voiceover duck |
| 0:12-0:20 | b03 | s03 | Input enters | Client requests flow into token budget | Trace motion | Match cut | Tick accents |
| 0:20-0:30 | b04 | s04 | Mechanism state | Bucket drains and refills over time | State change | Hard cut | Whoosh |
| 0:30-0:40 | b05 | s05 | Output | 200 responses versus 429 retry output | Pop output cards | Jump cut | Light hit |
| 0:40-0:50 | b06 | s06 | Contrast | No limit meltdown versus protected service diagram | Split-screen contrast | Smash cut | Riser |
| 0:50-1:02 | b07 | s07 | Warning | Bad retry loop overloads the queue | Glitch warning | Hard cut | Dropout and low impact |
| 1:02-1:10 | b08 | s08 | Callback rule | Final mechanism summary: budget, refill, retry-after | Zoom out callback | Final cut | Final hit and tail |

## Visual Source Plan

- Screenshots: gateway dashboard screenshot, docs page, terminal output.
- Code/UI captures: client retry code, API response headers.
- Diagrams/generated visuals: token bucket state machine, request flow, warning split screen.
- Source links: https://www.rfc-editor.org/rfc/rfc6585, docs.example.com/rate-limits, https://github.com/example/api/issues/429.

## Animation And Transition Plan

- Visual punctuation cadence: one visible idea every 6-10 seconds.
- Reusable motion vocabulary: punch-in, trace, highlight sweep, split-screen contrast, callback zoom.
- Transition map: hard cut for claims, match cut for state changes, smash cut for warning.

## Music And SFX Plan

- Background bed: starts at 0:00 and ducks under voiceover.
- Voiceover ducking: every dense script beat.
- Hits/stingers: hook, output reveal, final callback.
- Ticks/whooshes: request traces and code highlight.
- Risers/dropouts: contrast and warning.

## Voiceover Draft

- 0:00-0:05: Your API did not crash because users were bad; every request got treated as free.
- 0:05-0:12: A rate limit is a token budget with a clock and a visible retry rule.
- 0:12-0:20: Each request spends a token, so traffic becomes measurable instead of magical.
- 0:20-0:30: The bucket drains under load and refills on schedule, which protects the service.
- 0:30-0:40: The output is simple: allowed requests get 200, exhausted clients get 429.
- 0:40-0:50: Without a limit the service melts; with a budget it degrades predictably.
- 0:50-1:02: Bad retry code can still overload the queue, so Retry-After matters.
- 1:02-1:10: The callback is the rule: budget, refill, and retry timing.

## Script Style Notes

- Density: each beat defines, proves, contrasts, warns, or callbacks.
- Joke/claim cadence: one claim or proof per beat.
- Setup/payoff: free requests create overload; the payoff is retry timing.
- Final callback: a rate limit is a budget with a clock.

## Evaluation

- Validation checklist:
- Hook is visible in the first 5 seconds.
- At least 8 timed beats are present.
- Every beat has script purpose, visual, animation, transition, and audio.
- Expected pass result: final output will be validated with check_video_brief.py and score_video_readiness.py.
- Review the contact sheet for source-bound visual proof.
"""


WEAK_BRIEF = """# Generic Video

Promise: Explain something.
Audience: Everyone.
Format: compressed explainer
Runtime: 1:10

## Hook

Cold-open line: This is important.

## Timed Beat Table

| Time | Script purpose | Visual | Animation | Transition | Audio |
| --- | --- | --- | --- | --- | --- |
| 0:00-0:05 | Claim | Text | Fade | Cut | Music |
| 0:05-0:12 | More | Text | Fade | Cut | Music |
| 0:12-0:20 | More | Text | Fade | Cut | Music |
| 0:20-0:30 | More | Text | Fade | Cut | Music |
| 0:30-0:40 | More | Text | Fade | Cut | Music |
| 0:40-0:50 | More | Text | Fade | Cut | Music |
| 0:50-1:02 | More | Text | Fade | Cut | Music |
| 1:02-1:10 | End | Text | Fade | Cut | Music |

## Evaluation

This has timing but no source-bound mechanism.
"""


SLOW_STRUCTURED_BRIEF = """# What Is A Rate Limit?

Promise: Explain a rate limit as a basic API control.
Audience: Developers who know HTTP.
Format: compressed explainer
Runtime: 1:10

## Hook

Cold-open line: A rate limit is an important rule that controls how clients use an API.
First visual: Whiteboard title slide with a simple label and a calm diagram.
Audio cue: Soft ambient pad fades in under narration.

## Timed Beat Table

| Time | Script purpose | Visual | Animation | Transition | Audio |
| --- | --- | --- | --- | --- | --- |
| 0:00-0:05 | Introduce the concept | Whiteboard title slide with API label | Gentle reveal | Dissolve | Soft ambient pad |
| 0:05-0:12 | Define the concept | Minimal definition card and icon | Fade up | Dissolve | Calm narration |
| 0:12-0:20 | Explain the input | Simple request label on a clean slide | Slow reveal | Fade through | Soft ambient pad |
| 0:20-0:30 | Explain the limit | Static limit number on a whiteboard | Gentle reveal | Dissolve | Calm narration |
| 0:30-0:40 | Explain the output | Basic success and error labels | Fade up | Fade through | Soft ambient pad |
| 0:40-0:50 | Mention a problem | Simple warning label | Slow reveal | Dissolve | Calm narration |
| 0:50-1:02 | Mention a solution | Plain best-practice card | Gentle reveal | Fade through | Soft ambient pad |
| 1:02-1:10 | Summarize the idea | Final whiteboard summary | Fade up | Dissolve | Soft ambient tail |

## Visual Source Plan

- Screenshots: none needed.
- Code/UI captures: none needed.
- Diagrams/generated visuals: simple whiteboard cards.
- Source links: official docs.

## Animation And Transition Plan

Use slow fades, gentle reveals, and dissolve transitions.

## Music And SFX Plan

Use soft ambient music throughout.

## Voiceover Draft

- 0:00-0:05: A rate limit is a rule that controls how clients use an API.
- 0:05-0:12: It defines how many requests are allowed in a period of time.
- 0:12-0:20: The client sends a request and the server checks the rule.
- 0:20-0:30: If the limit is reached, the request is delayed or rejected.
- 0:30-0:40: Successful requests continue and blocked requests get an error.
- 0:40-0:50: This prevents too much traffic from causing service problems.
- 0:50-1:02: Good clients wait before trying again.
- 1:02-1:10: A rate limit is a simple rule for controlling API usage.

## Script Style Notes

- Density: simple explanation.
- Joke/claim cadence: calm and clear.
- Setup/payoff: define and summarize.
- Final callback: a rate limit controls API usage.

## Evaluation

- Validate the brief structure and timing.
"""


MISSING_BEATS_BRIEF = """# Broken

Promise: Explain a topic.
Audience: Developers.
Hook: Something happens.
Visuals: a diagram.
Audio: a bed.
Transitions: hard cuts.
Evaluation: pass.
"""


BLANK_HOOK_BRIEF = STRONG_BRIEF.replace(
    "Cold-open line: Your API did not crash because users were bad; it crashed because every request got treated as free.",
    "Cold-open line:",
).replace(
    "First visual: API gateway screenshot plus token bucket diagram proof visual.",
    "First visual:",
).replace(
    "Audio cue: Hit plus bed starts under voiceover.",
    "Audio cue:",
)


NO_SOURCE_LINKS_BRIEF = STRONG_BRIEF.replace(
    "- Source links: https://www.rfc-editor.org/rfc/rfc6585, docs.example.com/rate-limits, https://github.com/example/api/issues/429.",
    "- Source links: official API docs, service dashboard, GitHub issue.",
)


INDENTED_SOURCE_LINKS_BRIEF = STRONG_BRIEF.replace(
    "- Source links: https://www.rfc-editor.org/rfc/rfc6585, docs.example.com/rate-limits, https://github.com/example/api/issues/429.",
    "Source links:\n  - https://www.rfc-editor.org/rfc/rfc6585\n  - https://docs.example.com/rate-limits\n  - https://github.com/example/api/issues/429",
)


MARKDOWN_LABEL_BRIEF = (
    STRONG_BRIEF.replace(
        "Promise: Explain a rate limit as a token budget that protects a service and gives clients retry timing.",
        "**Promise:** Explain a rate limit as a token budget that protects a service and gives clients retry timing.",
    )
    .replace(
        "Audience: Developers who know HTTP and basic API clients.",
        "**Audience:** Developers who know HTTP and basic API clients.",
    )
    .replace("Format: compressed explainer", "**Format:** compressed explainer")
    .replace("Runtime: 1:10", "**Runtime:** 1:10")
    .replace(
        "Cold-open line: Your API did not crash because users were bad; it crashed because every request got treated as free.",
        "**Cold-open line:** Your API did not crash because users were bad; it crashed because every request got treated as free.",
    )
    .replace(
        "First visual: API gateway screenshot plus token bucket diagram proof visual.",
        "**First visual:** API gateway screenshot plus token bucket diagram proof visual.",
    )
    .replace(
        "Audio cue: Hit plus bed starts under voiceover.",
        "**Audio cue:** Hit plus bed starts under voiceover.",
    )
    .replace(
        "- Source links: https://www.rfc-editor.org/rfc/rfc6585, docs.example.com/rate-limits, https://github.com/example/api/issues/429.",
        "- **Source links:** https://www.rfc-editor.org/rfc/rfc6585, docs.example.com/rate-limits, https://github.com/example/api/issues/429.",
    )
)


GENERIC_VOICEOVER_LINES = """- 0:00-0:05: Open with the claim and name the consequence.
- 0:05-0:12: Define the concept in one compressed sentence.
- 0:12-0:20: Show the first mechanism step and why it matters.
- 0:20-0:30: Show the state change that makes the mechanism work.
- 0:30-0:40: Prove the practical output with a concrete example.
- 0:40-0:50: Contrast the failure path with the controlled path.
- 0:50-1:02: Give the rule of thumb viewers can reuse.
- 1:02-1:10: Callback to the hook and close on the practical rule."""


REPEATED_VOICEOVER_LINES = """- 0:00-0:05: This beat explains the topic in a clear simple way.
- 0:05-0:12: This beat explains the topic in a clear simple way.
- 0:12-0:20: This beat explains the topic in a clear simple way.
- 0:20-0:30: This beat explains the topic in a clear simple way.
- 0:30-0:40: This beat explains the topic in a clear simple way.
- 0:40-0:50: This beat explains the topic in a clear simple way.
- 0:50-1:02: This beat explains the topic in a clear simple way.
- 1:02-1:10: This beat explains the topic in a clear simple way."""


def replace_voiceover(text: str, voiceover_lines: str) -> str:
    return re.sub(
        r"\n## Voiceover Draft\n.*?(?=\n## Script Style Notes)",
        "\n## Voiceover Draft\n\n" + voiceover_lines + "\n",
        text,
        flags=re.DOTALL,
    )


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_bytes(path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)


def write_silent_wav(path: Path, seconds: float, sample_rate: int = 8000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame_count = max(1, int(seconds * sample_rate))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\x00\x00" * frame_count)


def make_args(**kwargs: Any) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_visual_png(path: Path, seed: int, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (640, 360), (10 + seed * 3, 18 + seed * 2, 30 + seed * 4))
    draw = ImageDraw.Draw(image)
    for band in range(24):
        y0 = band * 15
        color = (
            (25 + seed * 17 + band * 7) % 220 + 20,
            (45 + seed * 11 + band * 5) % 200 + 25,
            (70 + seed * 13 + band * 9) % 180 + 35,
        )
        draw.rectangle((0, y0, 640, y0 + 14), fill=color)
    for index in range(10):
        x = 32 + ((index * 73 + seed * 29) % 520)
        y = 40 + ((index * 41 + seed * 23) % 230)
        radius = 12 + ((index + seed) % 5) * 4
        fill = (
            (210 + index * 9 + seed * 5) % 255,
            (110 + index * 17 + seed * 7) % 255,
            (40 + index * 21 + seed * 11) % 255,
        )
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline="white", width=2)
    draw.rounded_rectangle((52, 248, 588, 326), radius=16, fill=(8, 12, 22), outline=(238, 242, 255), width=3)
    draw.text((76, 276), f"{label} / deterministic proof {seed:02d}", fill=(250, 250, 255))
    image.save(path, format="PNG")


def create_visual_svg(path: Path, seed: int, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    hue = (seed * 37) % 255
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
  <defs><linearGradient id="g{seed}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="rgb({hue},80,180)"/><stop offset="1" stop-color="rgb(20,190,{255 - hue})"/></linearGradient></defs>
  <rect width="640" height="360" fill="#101522"/>
  <rect x="44" y="42" width="552" height="276" rx="28" fill="url(#g{seed})" stroke="#f6f8ff" stroke-width="4"/>
  <circle cx="{150 + seed * 11}" cy="150" r="58" fill="#111827" stroke="#ffffff" stroke-width="5"/>
  <path d="M230 238 C310 {70 + seed * 3}, 410 {285 - seed * 2}, 548 112" fill="none" stroke="#ffe66d" stroke-width="14"/>
  <text x="250" y="178" fill="#ffffff" font-size="28" font-family="sans-serif">{label} proof {seed:02d}</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8", newline="\n")


def create_inline_fake_renderer(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#07111f;color:white;font-family:sans-serif}
#stage{position:relative;width:100vw;height:100vh;overflow:hidden;background:linear-gradient(135deg,#0b1b34,#174f6e 55%,#522c75)}
.composition{position:absolute;inset:0}.proof{position:absolute;display:block}.support{position:absolute;background:#101827;border:3px solid #ffe66d;padding:8px;box-sizing:border-box}
.is-visible{filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))}
</style></head><body><div id="stage"></div><script>
window.renderConceptFrame = (_videoId, seconds) => {
  const beat = Math.max(1, Math.min(8, Math.floor(seconds) + 1));
  const scene = `s${String(beat).padStart(2,'0')}`;
  const asset = `asset-${String(beat).padStart(2,'0')}`;
  const focalX = beat % 2 ? 12 : 8;
  document.querySelector('#stage').innerHTML = `<section class="composition is-visible" data-composition-id="${scene}">
    <svg class="proof is-visible" data-asset-id="${asset}" data-object-id="${scene}-focal" data-role="focal" style="left:${focalX}%;top:12%;width:58%;height:64%" viewBox="0 0 580 360" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="fake" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ff477e"/><stop offset="1" stop-color="#4cc9f0"/></linearGradient></defs>
      <rect width="580" height="360" rx="26" fill="url(#fake)"/><circle cx="155" cy="180" r="92" fill="#111827" stroke="#fff" stroke-width="8"/>
      <path d="M245 260 C315 75 420 285 535 96" fill="none" stroke="#ffe66d" stroke-width="18"/><text x="265" y="175" fill="white" font-size="30">inline fake ${asset}</text>
    </svg>
    <div class="support is-visible" data-object-id="${scene}-support" data-role="support" style="left:74%;top:18%;width:18%;height:42%">Inline SVG only; the manifest output is never loaded.</div>
  </section>`;
  return {
    activeBeat: beat, visualPattern: 'inline-fake-proof', visibleMechanismCount: 2,
    hookVisible: beat === 1, sourceProofVisible: true, sourceProofAssetIds: [asset],
    transitionVisible: true, warningVisible: beat === 6, outputVisible: beat >= 5,
    finalCallbackVisible: beat === 8, activeAssetIds: [asset], activeCompositionId: scene,
    rendererMode: 'production'
  };
};
</script></body></html>
""",
        encoding="utf-8",
        newline="\n",
    )


def create_bound_asset_renderer(path: Path, visual_fixture: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    assets = {
        str(item["id"]): {
            "output": str(item["output"]),
            "sha256": str(item["sha256"]),
        }
        for item in visual_fixture["assetManifest"].get("assets", [])
    }
    beat_ranges = extract_voiceover_cues.extract_beat_ranges(
        visual_fixture["brief"].read_text(encoding="utf-8")
    )
    scenes = []
    for scene_index, scene in enumerate(visual_fixture["compositionPlan"].get("scenes", [])):
        asset_id = str(scene["assetIds"][0])
        bounds = {str(item["id"]): item for item in scene.get("objectBounds", [])}
        focal = bounds[f"{scene['id']}-focal"]
        support = bounds[f"{scene['id']}-support"]
        scenes.append(
            {
                "id": str(scene["id"]),
                "assetId": asset_id,
                "output": assets[asset_id]["output"],
                "sha256": assets[asset_id]["sha256"],
                "mediaSrc": "../" + assets[asset_id]["output"],
                "focal": {key: focal[key] for key in ["x", "y", "width", "height"]},
                "support": {key: support[key] for key in ["x", "y", "width", "height"]},
                "start": float(beat_ranges[scene_index]["startSeconds"]),
                "end": float(beat_ranges[scene_index]["endSeconds"]),
            }
        )
    preload_markup = "".join(
        f'<img src="{scene["mediaSrc"]}" alt="" loading="eager">' for scene in scenes
    )
    path.write_text(
        f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#08111f;color:white;font-family:sans-serif}}
#stage{{position:relative;width:100vw;height:100vh;overflow:hidden;background:#0b1629}}
.composition{{position:absolute;inset:0}}.proof,.support{{position:absolute;box-sizing:border-box}}
.proof{{object-fit:contain;border:3px solid #fff;background:#111827}}.support{{padding:12px;background:#17223a;border:2px solid #ffe66d}}
.is-visible{{display:block}}
</style></head><body><div hidden>{preload_markup}</div><div id="stage"></div><script>
const scenes = {json.dumps(scenes)};
const pct = value => `${{value * 100}}%`;
window.renderConceptFrame = (_videoId, seconds) => {{
  const matchedIndex = scenes.findIndex(item => seconds >= item.start && seconds < item.end);
  const beat = matchedIndex >= 0 ? matchedIndex + 1 : scenes.length;
  const scene = scenes[beat - 1];
  const focal = scene.focal;
  const support = scene.support;
  document.querySelector('#stage').innerHTML = `<section class="composition is-visible" data-composition-id="${{scene.id}}">
    <img class="proof is-visible" data-asset-id="${{scene.assetId}}" data-asset-src="${{scene.output}}" data-asset-sha256="${{scene.sha256}}" data-object-id="${{scene.id}}-focal" data-role="focal" src="${{scene.mediaSrc}}" style="left:${{pct(focal.x)}};top:${{pct(focal.y)}};width:${{pct(focal.width)}};height:${{pct(focal.height)}}">
    <div class="support is-visible" data-object-id="${{scene.id}}-support" data-role="support" style="left:${{pct(support.x)}};top:${{pct(support.y)}};width:${{pct(support.width)}};height:${{pct(support.height)}}">Manifest-bound proof ${{scene.assetId}} for beat ${{beat}}.</div>
  </section>`;
  return {{
    activeBeat: beat, visualPattern: 'manifest-bound-proof', visibleMechanismCount: 2,
    hookVisible: beat === 1, sourceProofVisible: true, sourceProofAssetIds: [scene.assetId],
    transitionVisible: beat > 1, warningVisible: beat === 6, outputVisible: beat >= 5,
    finalCallbackVisible: beat === scenes.length, activeAssetIds: [scene.assetId],
    activeCompositionId: scene.id, rendererMode: 'production'
  }};
}};
</script></body></html>
""",
        encoding="utf-8",
        newline="\n",
    )


def create_inline_resource_spoof_renderer(path: Path, visual_fixture: dict[str, Any]) -> None:
    create_bound_asset_renderer(path, visual_fixture)
    text = path.read_text(encoding="utf-8")
    image_markup = '<img class="proof is-visible" data-asset-id="${scene.assetId}" data-asset-src="${scene.output}" data-asset-sha256="${scene.sha256}" data-object-id="${scene.id}-focal" data-role="focal" src="${scene.mediaSrc}" style="left:${pct(focal.x)};top:${pct(focal.y)};width:${pct(focal.width)};height:${pct(focal.height)}">'
    spoof_markup = '<svg class="proof is-visible" data-asset-id="${scene.assetId}" data-asset-src="${scene.output}" data-asset-sha256="${scene.sha256}" data-asset-resource-src="${scene.mediaSrc}" data-object-id="${scene.id}-focal" data-role="focal" style="left:${pct(focal.x)};top:${pct(focal.y)};width:${pct(focal.width)};height:${pct(focal.height)}" viewBox="0 0 640 360"><rect width="640" height="360" fill="#15345a"/><text x="80" y="180" fill="white">Inline spoof never loaded the manifest output.</text></svg>'
    if image_markup not in text:
        raise AssertionError("bound renderer image markup changed; update spoof fixture")
    text = re.sub(r'<div hidden>.*?</div><div id="stage">', '<div id="stage">', text, count=1)
    path.write_text(text.replace(image_markup, spoof_markup), encoding="utf-8", newline="\n")


def create_evidence_video(video: Path, decoded_frames: Path, *, duration_seconds: float = 70.0) -> None:
    video.parent.mkdir(parents=True, exist_ok=True)
    decoded_frames.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"testsrc2=size=640x360:rate=10:duration={duration_seconds:g}",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "18",
            "-g",
            "1",
            "-pix_fmt",
            "yuv420p",
            str(video),
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(video),
            "-vf",
            "fps=10",
            "-start_number",
            "0",
            str(decoded_frames / "video-frame-%03d.png"),
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )


def create_renderer_hold_video(
    renderer_report: dict[str, Any],
    output: Path,
    scene_ranges: list[tuple[float, float]],
) -> None:
    analyses = renderer_report.get("screenshotAnalyses", [])
    states = renderer_report.get("states", [])
    screenshots_by_beat: dict[int, Path] = {}
    for state_entry, analysis in zip(states, analyses, strict=True):
        state = state_entry.get("state", {}) if isinstance(state_entry, dict) else {}
        beat = state.get("activeBeat") if isinstance(state, dict) else None
        path = analysis.get("path") if isinstance(analysis, dict) else None
        if isinstance(beat, int) and isinstance(path, str) and Path(path).is_file():
            screenshots_by_beat.setdefault(beat, Path(path))
    if set(screenshots_by_beat) != set(range(1, len(scene_ranges) + 1)):
        raise AssertionError("renderer report does not contain one saved screenshot for every beat")
    output.parent.mkdir(parents=True, exist_ok=True)
    concat_path = output.with_suffix(".concat.txt")
    lines: list[str] = []
    for beat, (start, end) in enumerate(scene_ranges, start=1):
        frame_path = screenshots_by_beat[beat].resolve().as_posix().replace("'", "'\\''")
        lines.extend([f"file '{frame_path}'", f"duration {end - start:g}"])
    final_path = screenshots_by_beat[len(scene_ranges)].resolve().as_posix().replace("'", "'\\''")
    lines.append(f"file '{final_path}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-vf",
            "fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "18",
            str(output),
        ],
        check=True,
        capture_output=True,
        timeout=90,
    )


def decoded_frame_at(decoded_frames: Path, timestamp: float) -> Path:
    path = decoded_frames / f"video-frame-{int(round(timestamp * 10)):03d}.png"
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def create_unrelated_evidence(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        inverted = Image.eval(image.convert("RGB"), lambda value: 255 - value)
        inverted.save(destination, format="PNG")


def build_visual_contract_fixture(project: Path) -> dict[str, Any]:
    source = project / "source"
    assets_dir = project / "assets" / "generated"
    reviews = project / "artifacts" / "reviews"
    frames = reviews / "frames"
    producers = reviews / "producers"
    video = project / "artifacts" / "videos" / "visual-contract.mp4"
    brief = source / "brief.md"
    asset_manifest_path = source / "asset-manifest.json"
    composition_plan_path = source / "composition-plan.json"
    visual_review_path = reviews / "visual-review.json"
    visual_contract_report_path = reviews / "asset-composition-validation.json"
    brief.parent.mkdir(parents=True, exist_ok=True)
    brief.write_text(STRONG_BRIEF, encoding="utf-8", newline="\n")
    decoded_video_frames = reviews / "decoded-video"
    create_evidence_video(video, decoded_video_frames, duration_seconds=70.0)

    asset_skills = [
        "imagegen",
        "d3-animated-svg",
        "mermaid-animated-svg",
        "echarts-animated-svg",
        "imagegen",
        "d3-animated-svg",
        "mermaid-animated-svg",
        "echarts-animated-svg",
    ]
    assets: list[dict[str, Any]] = []
    asset_paths: list[Path] = []
    for index in range(1, 9):
        asset_id = f"asset-{index:02d}"
        suffix = ".png" if index % 2 else ".svg"
        output = assets_dir / f"{asset_id}{suffix}"
        if suffix == ".png":
            create_visual_png(output, index, f"scene {index:02d} asset")
            kind = "illustration"
        else:
            create_visual_svg(output, index, f"scene-{index:02d}")
            kind = "svg"
        asset_paths.append(output)
        report = producers / f"{asset_id}.json"
        write_json(
            report,
            {
                "schemaVersion": 1,
                "ok": True,
                "assetId": asset_id,
                "skill": asset_skills[index - 1],
                "output": output.relative_to(project).as_posix(),
                "sha256": sha256_path(output),
                "outputSha256": sha256_path(output),
                "checks": [
                    {
                        "name": "dimensions",
                        "method": "inspect decoded output dimensions",
                        "finding": "Output meets its declared target resolution and crop contract.",
                        "passed": True,
                    },
                    {
                        "name": "contrast",
                        "method": "inspect luminance and color variation",
                        "finding": "Focal geometry remains visibly distinct from its support and background.",
                        "passed": True,
                    },
                    {
                        "name": "semantic content",
                        "method": "compare the visual against its scene claim",
                        "finding": "The output depicts the declared mechanism state with scene-specific geometry.",
                        "passed": True,
                    },
                ],
            },
        )
        assets.append(
            {
                "id": asset_id,
                "kind": kind,
                "claim": f"Scene {index:02d} shows a concrete rate-limit mechanism state and its observable result.",
                "output": output.relative_to(project).as_posix(),
                "sha256": sha256_path(output),
                "origin": {
                    "type": "generated",
                    "uri": f"generated://visual-contract/{asset_id}",
                    "rightsStatus": "project-generated",
                    "attribution": "Original deterministic regression fixture.",
                },
                "producer": {
                    "skill": asset_skills[index - 1],
                    "method": "Generated a source-bound mechanism visual with deterministic geometry and contrast.",
                    "report": report.relative_to(project).as_posix(),
                },
                "technical": {
                    "targetWidth": 640,
                    "targetHeight": 360,
                    "aspectRatio": "16:9",
                    "maxUpscale": 1.0,
                    "crop": "Preserve the full mechanism proof and its source label.",
                },
                "uses": [
                    {
                        "sceneId": f"s{index:02d}",
                        "beatId": f"b{index:02d}",
                        "role": "primary mechanism proof",
                        "fit": "contain inside the declared focal bounds",
                    }
                ],
                "qualityChecks": [
                    "Verify the focal mechanism remains legible at delivery resolution.",
                    "Confirm the asset contains varied geometry and meaningful contrast.",
                    "Match the rendered asset ID to its declared scene and beat usage.",
                ],
                "status": "approved",
            }
        )

    routes = [
        {
            "stage": "source freeze",
            "skill": "source-to-video-director",
            "reason": "Freeze claims and beat identifiers before generating visual proof assets.",
            "output": "source/source-package.json and source/shot-contract.json",
            "outputPaths": ["source/source-package.json", "source/shot-contract.json"],
            "status": "complete",
        },
        {
            "stage": "composition",
            "skill": "scene-composition-director",
            "reason": "Assign a deliberate focal hierarchy and armature to every scene.",
            "output": "source/composition-plan.json",
            "status": "complete",
        },
        {
            "stage": "transitions",
            "skill": "scene-transition-director",
            "reason": "Design semantic handoffs across all adjacent scene boundaries.",
            "output": "source/transition-plan.json",
            "status": "complete",
        },
        {
            "stage": "renderer",
            "skill": "html-d3-anime-video-workflow",
            "reason": "Render the composed assets with deterministic browser frame control.",
            "output": "src/index.html",
            "status": "complete",
        },
    ]
    for index, route in enumerate(routes, start=1):
        proof = reviews / "routing" / f"route-{index:02d}.json"
        route.setdefault("outputPaths", [route["output"]])
        route["proof"] = proof.relative_to(project).as_posix()
    asset_manifest = {
        "schemaVersion": 1,
        "canvas": {"width": 1280, "height": 720, "aspectRatio": "16:9"},
        "skillRouting": routes,
        "assets": assets,
    }
    write_json(asset_manifest_path, asset_manifest)

    composition_choices = [
        "radial focus",
        "diagonal contrast",
        "split comparison",
        "flow corridor",
        "radial focus",
        "diagonal contrast",
        "split comparison",
        "flow corridor",
    ]
    armatures = [
        "golden spiral",
        "ascending diagonal",
        "bilateral split",
        "serpentine flow",
        "golden spiral",
        "ascending diagonal",
        "bilateral split",
        "serpentine flow",
    ]
    scene_durations = [
        "0:00-0:05",
        "0:05-0:12",
        "0:12-0:20",
        "0:20-0:30",
        "0:30-0:40",
        "0:40-0:50",
        "0:50-1:02",
        "1:02-1:10",
    ]
    scene_ranges_seconds = [
        (0.0, 5.0),
        (5.0, 12.0),
        (12.0, 20.0),
        (20.0, 30.0),
        (30.0, 40.0),
        (40.0, 50.0),
        (50.0, 62.0),
        (62.0, 70.0),
    ]
    focal_bounds = [
        {"x": 0.08, "y": 0.12, "width": 0.60, "height": 0.64},
        {"x": 0.34, "y": 0.10, "width": 0.56, "height": 0.58},
        {"x": 0.10, "y": 0.24, "width": 0.72, "height": 0.48},
        {"x": 0.22, "y": 0.08, "width": 0.56, "height": 0.72},
        {"x": 0.08, "y": 0.12, "width": 0.66, "height": 0.58},
        {"x": 0.08, "y": 0.18, "width": 0.40, "height": 0.62},
        {"x": 0.30, "y": 0.16, "width": 0.62, "height": 0.54},
        {"x": 0.18, "y": 0.20, "width": 0.68, "height": 0.60},
    ]
    support_bounds = [
        {"x": 0.72, "y": 0.18, "width": 0.20, "height": 0.42},
        {"x": 0.08, "y": 0.18, "width": 0.20, "height": 0.44},
        {"x": 0.16, "y": 0.06, "width": 0.68, "height": 0.12},
        {"x": 0.08, "y": 0.70, "width": 0.84, "height": 0.16},
        {"x": 0.76, "y": 0.18, "width": 0.16, "height": 0.50},
        {"x": 0.54, "y": 0.18, "width": 0.38, "height": 0.62},
        {"x": 0.08, "y": 0.18, "width": 0.18, "height": 0.54},
        {"x": 0.08, "y": 0.08, "width": 0.30, "height": 0.18},
    ]
    scenes: list[dict[str, Any]] = []
    for index in range(1, 9):
        scenes.append(
            {
                "id": f"s{index:02d}",
                "duration": scene_durations[index - 1],
                "sceneJob": f"Prove mechanism state {index:02d} with a visible input and outcome.",
                "viewerTask": "Track the focal state change and connect it to the spoken technical claim.",
                "compositionChoice": composition_choices[index - 1],
                "rejectedAlternatives": [
                    "text-only slide without visible mechanism state",
                    "repeated generic card wall without a governing armature",
                ],
                "choiceRationale": "This armature keeps the generated proof dominant while preserving a clean semantic handoff.",
                "focal": f"asset-{index:02d} mechanism state",
                "roles": {"focal": "mechanism proof", "support": "claim label", "handoff": "persistent state token"},
                "armature": armatures[index - 1],
                "armatureAnchors": [
                    "primary focal axis through the mechanism proof",
                    "secondary handoff axis aligned with the next scene token",
                ],
                "alignmentGrid": "Twelve-column grid with an eight-pixel baseline and a named focal axis.",
                "edgePolicy": "Keep source geometry inside a five-percent frame-safe margin.",
                "cornerPolicy": "Use consistent rounded corners only for generated proof surfaces.",
                "layout": "Place the focal proof across the primary two-thirds and reserve the edge for the handoff.",
                "hierarchy": "The mechanism proof dominates; claim label and transition token remain subordinate.",
                "safeZones": {"frameMargin": "5 percent", "captionBand": "bottom 12 percent"},
                "textRegion": {
                    "placement": "Supporting claim text stays on the secondary edge rail.",
                    "maxLineCharacters": 42,
                    "contrastTreatment": "Use an opaque dark backing surface with high-contrast white type.",
                    "clearance": "Keep at least twenty-four pixels between text and focal proof geometry.",
                },
                "depthLayers": ["background context field", "midground mechanism trace", "foreground focal proof"],
                "motionPhases": [
                    {
                        "name": "entrance",
                        "cue": "scene entry",
                        "visualChange": "Reveal the focal proof before its supporting label.",
                        "motionVerb": "reveal",
                    },
                    {
                        "name": "hold",
                        "cue": "definition clause",
                        "visualChange": "Hold the complete proof long enough for its source label to register.",
                        "motionVerb": "hold",
                    },
                    {
                        "name": "emphasis",
                        "cue": "mechanism clause",
                        "visualChange": "Transform the visible state to expose the technical outcome.",
                        "motionVerb": "emphasize",
                    },
                    {
                        "name": "exit",
                        "cue": "handoff clause",
                        "visualChange": "Align the proof token with the next scene before the semantic cut.",
                        "motionVerb": "handoff",
                    },
                ],
                "reducedMotion": "Reveal the same final states without interpolation and preserve the hold and emphasis hierarchy.",
                "outgoingSeam": {
                    "seamId": f"s{index:02d}__s{index + 1:02d}" if index < 8 else "end",
                    "fromScene": f"s{index:02d}",
                    "toScene": f"s{index + 1:02d}" if index < 8 else None,
                    "type": "transition" if index < 8 else "end",
                    "persistentElement": "The highlighted mechanism state token persists across the cut.",
                    "attentionHandoff": "The focal trace points toward the next scene's primary proof position.",
                    "beforeState": "Current scene holds its approved emphasis frame and source label.",
                    "afterState": "Next proof receives the persistent token, or the final callback resolves the chain.",
                },
                "validationChecks": [
                    {
                        "method": "full-resolution frame review",
                        "target": f"s{index:02d} focal proof",
                        "passCriterion": "Proof is legible, unclipped, and visually dominant.",
                    },
                    {
                        "method": "renderer DOM state review",
                        "target": f"s{index:02d} asset and object identifiers",
                        "passCriterion": "Visible identifiers match the active scene contract.",
                    },
                ],
                "validationContract": {
                    "alignment": "Verify the focal proof and support label land on the declared grid and armature anchors.",
                    "safeZones": "Verify focal geometry, source label, and caption band remain inside declared margins.",
                    "edgePolicy": "Verify no proof or label clips the frame and source-native geometry stays intact.",
                    "boxPadding": "Verify generated proof surfaces preserve at least sixteen pixels of internal clearance.",
                    "grayscaleHierarchy": "Verify the focal proof remains the brightest readable mass above support and background.",
                    "focalHierarchy": "Verify the mechanism proof dominates before claim labels and transition handoff tokens.",
                    "verificationArtifacts": [
                        f"artifacts/reviews/frames/scene-{index:02d}.png",
                        f"artifacts/reviews/renderer/scene-{index:02d}-state.json",
                    ],
                },
                "assetIds": [f"asset-{index:02d}"],
                "beatIds": [f"b{index:02d}"],
                "objectBounds": [
                    {
                        "id": f"s{index:02d}-focal",
                        "role": "focal",
                        **focal_bounds[index - 1],
                    },
                    {
                        "id": f"s{index:02d}-support",
                        "role": "support",
                        **support_bounds[index - 1],
                    },
                ],
            }
        )
    composition_plan = {
        "version": 1,
        "format": "1280x720",
        "videoDirection": {
            "alignmentMode": "Twelve-column grid with scene-specific armatures and shared baselines.",
            "edgeCornerPolicy": "Preserve source-native geometry and one coherent generated-surface policy.",
            "paletteTypeSource": "Use the declared original blue, amber, and white mechanism palette.",
            "rhythm": "Alternate radial, diagonal, split, and flow scenes around semantic handoffs.",
            "safeZones": "Keep proof, captions, and source labels inside five-percent frame margins.",
            "negativeList": [
                "repeated generic card wall",
                "decorative movement without state change",
                "tiny proof stretched beyond source resolution",
            ],
        },
        "scenes": scenes,
    }
    write_json(composition_plan_path, composition_plan)
    transition_plan_path = source / "transition-plan.json"
    write_json(
        transition_plan_path,
        {
            "ok": True,
            "transitions": [
                {"fromScene": f"s{index:02d}", "toScene": f"s{index + 1:02d}", "semanticHandoff": "state token"}
                for index in range(1, 8)
            ],
        },
    )
    source_package_path = source / "source-package.json"
    shot_contract_path = source / "shot-contract.json"
    write_json(
        source_package_path,
        {
            "schemaVersion": 1,
            "videoId": "visual-contract",
            "status": "frozen",
            "facts": [
                {
                    "id": f"f{index:02d}",
                    "beatId": f"b{index:02d}",
                    "time": scene_durations[index - 1],
                    "claim": f"Verified rate-limit fact {index:02d} explains a concrete mechanism state and observable outcome.",
                    "sourceUrl": "https://www.rfc-editor.org/rfc/rfc6585",
                    "rightsStatus": "official-source",
                    "verificationStatus": "verified",
                }
                for index in range(1, 9)
            ],
        },
    )
    write_json(
        shot_contract_path,
        {
            "version": 1,
            "videoId": "visual-contract",
            "shots": [
                {
                    "id": f"s{index:02d}",
                    "beatId": f"b{index:02d}",
                    "time": scene_durations[index - 1],
                    "job": f"Prove verified mechanism state {index:02d} with source-bound evidence.",
                    "viewerTask": "Track the visible state change and connect it to the verified technical claim.",
                    "assetIds": [f"asset-{index:02d}"],
                    "sourceFactIds": [f"f{index:02d}"],
                    "status": "approved",
                }
                for index in range(1, 9)
            ],
        },
    )
    renderer_output_path = project / "src" / "index.html"
    renderer_output_path.parent.mkdir(parents=True, exist_ok=True)
    renderer_output_path.write_text(
        "<!doctype html><title>Bound renderer route output</title><main>Deterministic production renderer proof.</main>",
        encoding="utf-8",
        newline="\n",
    )
    for route in routes:
        output_paths = [project / str(item) for item in route["outputPaths"]]
        proof_path = project / str(route["proof"])
        write_json(
            proof_path,
            {
                "schemaVersion": 1,
                "ok": True,
                "stage": route["stage"],
                "skill": route["skill"],
                "output": route["output"],
                "sha256": sha256_path(output_paths[0]),
                "outputSha256": sha256_path(output_paths[0]),
                "artifacts": [
                    {
                        "path": str(output_path.relative_to(project).as_posix()),
                        "sha256": sha256_path(output_path),
                    }
                    for output_path in output_paths
                ],
            },
        )

    contact_sheet = reviews / "contact-sheet.png"
    create_visual_png(contact_sheet, 30, "contact sheet")
    scene_reviews: list[dict[str, Any]] = []
    for index in range(1, 9):
        scene_start, scene_end = scene_ranges_seconds[index - 1]
        scene_duration = scene_end - scene_start
        scene_timestamps = {
            "first": round(scene_start + min(0.4, scene_duration * 0.08), 1),
            "hold": round(scene_start + scene_duration * 0.35, 1),
            "emphasis": round(scene_start + scene_duration * 0.70, 1),
            "final": round(scene_end - min(0.4, scene_duration * 0.08), 1),
        }
        scene_reviews.append(
            {
                "sceneId": f"s{index:02d}",
                "compositionId": f"s{index:02d}",
                "assetIds": [f"asset-{index:02d}"],
                "evidenceFrames": [
                    {
                        "phase": phase,
                        "timestamp": timestamp,
                        "path": decoded_frame_at(decoded_video_frames, timestamp).relative_to(project).as_posix(),
                        "sha256": sha256_path(decoded_frame_at(decoded_video_frames, timestamp)),
                    }
                    for phase, timestamp in scene_timestamps.items()
                ],
                "checks": {name: "pass" for name in check_visual_contract.REVIEW_CHECKS},
                "status": "approved",
                "finding": "The focal generated asset is legible, source-bound, unclipped, and compositionally dominant.",
                "correction": "Tightened the focal crop and label clearance before capturing this approved evidence frame.",
            }
        )
    transitions: list[dict[str, Any]] = []
    for index in range(1, 8):
        seam_time = scene_ranges_seconds[index - 1][1]
        transition_timestamps = {
            "before": round(seam_time - 0.2, 1),
            "midpoint": round(seam_time, 1),
            "after": round(seam_time + 0.2, 1),
        }
        transitions.append(
            {
                "id": f"s{index:02d}__s{index + 1:02d}",
                "fromScene": f"s{index:02d}",
                "toScene": f"s{index + 1:02d}",
                "evidenceFrames": [
                    {
                        "phase": phase,
                        "timestamp": timestamp,
                        "path": decoded_frame_at(decoded_video_frames, timestamp).relative_to(project).as_posix(),
                        "sha256": sha256_path(decoded_frame_at(decoded_video_frames, timestamp)),
                    }
                    for phase, timestamp in transition_timestamps.items()
                ],
                "status": "pass",
                "finding": "The persistent state token hands attention to the next focal proof without clipping or ambiguity.",
            }
        )
    visual_review = {
        "schemaVersion": 1,
        "videoId": "visual-contract",
        "inputDigests": {
            "assetManifestSha256": sha256_path(asset_manifest_path),
            "compositionPlanSha256": sha256_path(composition_plan_path),
        },
        "reviewer": "deterministic regression reviewer",
        "reviewMethod": "Inspect first, hold, emphasis, and final scene frames plus before, midpoint, and after transition evidence extracted from the candidate video.",
        "contactSheet": contact_sheet.relative_to(project).as_posix(),
        "candidateVideo": {
            "path": video.relative_to(project).as_posix(),
            "sha256": sha256_path(video),
        },
        "fullSpeedPlayback": {
            "reviewed": True,
            "notes": "Full-speed playback preserves focal hierarchy and clean semantic handoffs across all eight scenes.",
        },
        "scenes": scene_reviews,
        "transitions": transitions,
        "unresolvedBlockers": [],
        "overallStatus": "approved",
    }
    write_json(visual_review_path, visual_review)

    args = make_args(
        asset_manifest=asset_manifest_path,
        composition_plan=composition_plan_path,
        visual_review=visual_review_path,
        video=video,
        brief=brief,
        project_root=project,
        min_assets=8,
        min_scenes=8,
        require_ready_assets=True,
        require_specialist_routing=True,
        require_source_routing=True,
        require_reviewed_scenes=True,
        output=None,
        json=True,
    )
    report = check_visual_contract.validate(args)
    write_json(visual_contract_report_path, report)
    return {
        "project": project,
        "args": args,
        "brief": brief,
        "video": video,
        "assetManifestPath": asset_manifest_path,
        "assetManifest": asset_manifest,
        "assetPaths": asset_paths,
        "compositionPlanPath": composition_plan_path,
        "compositionPlan": composition_plan,
        "sceneRanges": scene_ranges_seconds,
        "visualReviewPath": visual_review_path,
        "visualReview": visual_review,
        "contactSheet": contact_sheet,
        "visualContractReportPath": visual_contract_report_path,
        "report": report,
    }


def build_valid_renderer_evidence(visual_fixture: dict[str, Any]) -> dict[str, Any]:
    asset_ids = [str(item["id"]) for item in visual_fixture["assetManifest"].get("assets", [])]
    composition_ids = [str(item["id"]) for item in visual_fixture["compositionPlan"].get("scenes", [])]
    scene_count = len(composition_ids)
    return {
        "ok": True,
        "failures": [],
        "sampleCount": scene_count,
        "states": [{"state": {"activeBeat": index}} for index in range(1, scene_count + 1)],
        "uniqueBeats": list(range(1, scene_count + 1)),
        "briefBeatCoverageOk": True,
        "missingBriefBeats": [],
        "visualAssetCoverageOk": True,
        "assetBindingCoverageOk": True,
        "compositionCoverageOk": True,
        "expectedAssetIds": asset_ids,
        "observedAssetIds": asset_ids,
        "missingAssetIds": [],
        "expectedCompositionIds": composition_ids,
        "observedCompositionIds": composition_ids,
        "missingCompositionIds": [],
        "missingCompositionObjectIds": [],
        "rendererSha256": sha256_path(visual_fixture["project"] / "src" / "index.html"),
        "assetManifestSha256": visual_fixture["report"]["inputDigests"]["assetManifestSha256"],
        "compositionPlanSha256": visual_fixture["report"]["inputDigests"]["compositionPlanSha256"],
    }


def build_complete_readiness_payload(
    visual_fixture: dict[str, Any],
    renderer_report: dict[str, Any],
    *,
    score: int = 22,
    weak_categories: list[str] | None = None,
) -> dict[str, Any]:
    base_score, extra = divmod(score, len(score_video_readiness.CATEGORIES))
    categories: dict[str, dict[str, Any]] = {}
    for index, name in enumerate(score_video_readiness.CATEGORIES):
        category_score = base_score + (1 if index < extra else 0)
        categories[name] = {
            "score": category_score,
            "evidence": [f"Deterministic {name} evidence is present."],
            "improvement": "No fixture improvement required.",
        }
    return {
        "ok": True,
        "score": score,
        "maxScore": len(score_video_readiness.CATEGORIES) * 3,
        "readiness": "ready",
        "weakCategories": list(weak_categories or []),
        "categories": categories,
        "visualContractReport": copy.deepcopy(visual_fixture["report"]),
        "rendererReport": copy.deepcopy(renderer_report),
        "failures": [],
    }


def test_visual_contract(tmp: Path, fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    fixture = fixture or build_visual_contract_fixture(tmp / "visual-contract")
    report = fixture["report"]
    project = fixture["project"]

    planned_manifest = copy.deepcopy(fixture["assetManifest"])
    planned_manifest["assets"][0]["status"] = "planned"
    planned_manifest["assets"][0]["output"] = "assets/generated/missing-asset.png"
    planned_path = project / "source" / "asset-manifest-planned.json"
    write_json(planned_path, planned_manifest)
    planned_args = copy.copy(fixture["args"])
    planned_args.asset_manifest = planned_path
    planned_args.visual_review = None
    planned_args.video = None
    planned_args.require_reviewed_scenes = False
    planned = check_visual_contract.validate(planned_args)

    stale_manifest = copy.deepcopy(fixture["assetManifest"])
    stale_report_path = project / "artifacts" / "reviews" / "producers" / "stale-asset-01.json"
    write_json(stale_report_path, {"ok": False, "assetId": "asset-01", "reason": "stale producer output"})
    stale_manifest["assets"][0]["sha256"] = "0" * 64
    stale_manifest["assets"][0]["producer"]["report"] = stale_report_path.relative_to(project).as_posix()
    stale_path = project / "source" / "asset-manifest-stale.json"
    write_json(stale_path, stale_manifest)
    stale_args = copy.copy(fixture["args"])
    stale_args.asset_manifest = stale_path
    stale_args.visual_review = None
    stale_args.video = None
    stale_args.require_reviewed_scenes = False
    stale = check_visual_contract.validate(stale_args)

    seam_plan = copy.deepcopy(fixture["compositionPlan"])
    seam_plan["scenes"][0]["assetIds"] = ["unknown-asset"]
    seam_path = project / "source" / "composition-plan-unknown.json"
    write_json(seam_path, seam_plan)
    seam_args = copy.copy(fixture["args"])
    seam_args.composition_plan = seam_path
    seam_args.visual_review = None
    seam_args.video = None
    seam_args.require_reviewed_scenes = False
    seam = check_visual_contract.validate(seam_args)

    reversed_manifest = copy.deepcopy(fixture["assetManifest"])
    reversed_plan = copy.deepcopy(fixture["compositionPlan"])
    for index in range(8):
        reversed_beat = f"b{8 - index:02d}"
        reversed_manifest["assets"][index]["uses"][0]["beatId"] = reversed_beat
        reversed_plan["scenes"][index]["beatIds"] = [reversed_beat]
    reversed_manifest_path = project / "source" / "asset-manifest-reversed-beats.json"
    reversed_plan_path = project / "source" / "composition-plan-reversed-beats.json"
    write_json(reversed_manifest_path, reversed_manifest)
    write_json(reversed_plan_path, reversed_plan)
    reversed_args = copy.copy(fixture["args"])
    reversed_args.asset_manifest = reversed_manifest_path
    reversed_args.composition_plan = reversed_plan_path
    reversed_args.visual_review = None
    reversed_args.video = None
    reversed_args.require_reviewed_scenes = False
    reversed_beats = check_visual_contract.validate(reversed_args)

    thin_plan = copy.deepcopy(fixture["compositionPlan"])
    for scene in thin_plan["scenes"]:
        scene["compositionChoice"] = "grid"
        scene["armature"] = "center"
        scene["objectBounds"] = [
            {"id": f"{scene['id']}-focal", "role": "focal", "x": 0.12, "y": 0.14, "width": 0.58, "height": 0.62},
            {"id": f"{scene['id']}-support", "role": "support", "x": 0.74, "y": 0.18, "width": 0.18, "height": 0.42},
        ]
    thin_plan["scenes"][0]["choiceRationale"] = "thin"
    thin_plan["scenes"][0]["layout"] = "small"
    thin_plan["scenes"][0]["rejectedAlternatives"] = ["cards"]
    thin_plan["scenes"][0]["armatureAnchors"] = ["center"]
    thin_plan["scenes"][0]["validationContract"]["verificationArtifacts"] = ["one-frame.png"]
    thin_plan["scenes"][0]["textRegion"]["maxLineCharacters"] = 8
    thin_plan["scenes"][0]["motionPhases"] = thin_plan["scenes"][0]["motionPhases"][:2]
    thin_plan["scenes"][0]["reducedMotion"] = "none"
    thin_plan["scenes"][0]["outgoingSeam"]["seamId"] = "wrong-seam"
    thin_path = project / "source" / "composition-plan-thin.json"
    write_json(thin_path, thin_plan)
    thin_args = copy.copy(fixture["args"])
    thin_args.composition_plan = thin_path
    thin_args.visual_review = None
    thin_args.video = None
    thin_args.require_reviewed_scenes = False
    thin = check_visual_contract.validate(thin_args)

    pending_review = copy.deepcopy(fixture["visualReview"])
    pending_review["overallStatus"] = "pending"
    pending_review["candidateVideo"] = {"path": "", "sha256": None}
    pending_review["fullSpeedPlayback"] = {
        "reviewed": False,
        "notes": "Playback review remains incomplete for this negative contract fixture.",
    }
    pending_review["scenes"][0]["status"] = "pending"
    pending_review["scenes"][0]["checks"]["sourceProof"] = "pending"
    pending_review_path = project / "artifacts" / "reviews" / "visual-review-pending.json"
    write_json(pending_review_path, pending_review)
    pending_args = copy.copy(fixture["args"])
    pending_args.visual_review = pending_review_path
    pending = check_visual_contract.validate(pending_args)

    unrelated_review = copy.deepcopy(fixture["visualReview"])
    hold_frame = next(
        frame for frame in unrelated_review["scenes"][0]["evidenceFrames"] if frame.get("phase") == "hold"
    )
    unrelated_hold_path = project / "artifacts" / "reviews" / "frames" / "unrelated-hold.png"
    create_unrelated_evidence(project / str(hold_frame["path"]), unrelated_hold_path)
    hold_frame["path"] = unrelated_hold_path.relative_to(project).as_posix()
    hold_frame["sha256"] = sha256_path(unrelated_hold_path)
    before_frame = next(
        frame
        for frame in unrelated_review["transitions"][0]["evidenceFrames"]
        if frame.get("phase") == "before"
    )
    unrelated_before_path = project / "artifacts" / "reviews" / "frames" / "unrelated-before.png"
    create_unrelated_evidence(project / str(before_frame["path"]), unrelated_before_path)
    before_frame["path"] = unrelated_before_path.relative_to(project).as_posix()
    before_frame["sha256"] = sha256_path(unrelated_before_path)
    unrelated_review["scenes"] = [unrelated_review["scenes"][0]]
    unrelated_review["transitions"] = [unrelated_review["transitions"][0]]
    unrelated_review_path = project / "artifacts" / "reviews" / "visual-review-unrelated-frame.json"
    write_json(unrelated_review_path, unrelated_review)
    unrelated_args = copy.copy(fixture["args"])
    unrelated_args.visual_review = unrelated_review_path
    unrelated_evidence = check_visual_contract.validate(unrelated_args)

    timing_review = copy.deepcopy(fixture["visualReview"])
    timing_scene = timing_review["scenes"][0]
    timing_scene["evidenceFrames"][0] = {
        "phase": "first",
        "timestamp": 5.4,
        "path": (project / "artifacts" / "reviews" / "decoded-video" / "video-frame-054.png")
        .relative_to(project)
        .as_posix(),
        "sha256": sha256_path(project / "artifacts" / "reviews" / "decoded-video" / "video-frame-054.png"),
    }
    timing_scene["evidenceFrames"][1]["phase"] = "emphasis"
    timing_scene["evidenceFrames"][2]["phase"] = "hold"
    timing_review["scenes"] = [timing_scene]
    timing_review["transitions"] = []
    timing_review_path = project / "artifacts" / "reviews" / "visual-review-bad-timing.json"
    write_json(timing_review_path, timing_review)
    timing_args = copy.copy(fixture["args"])
    timing_args.visual_review = timing_review_path
    bad_timing = check_visual_contract.validate(timing_args)

    repeated_hash_review = copy.deepcopy(fixture["visualReview"])
    original_hash_frame = project / str(repeated_hash_review["scenes"][0]["evidenceFrames"][0]["path"])
    repeated_hash_frame = project / "artifacts" / "reviews" / "frames" / "repeated-frame-copy.png"
    repeated_hash_frame.write_bytes(original_hash_frame.read_bytes())
    repeated_hash_review["scenes"][1]["evidenceFrames"][0]["path"] = repeated_hash_frame.relative_to(
        project
    ).as_posix()
    repeated_hash_review["scenes"][1]["evidenceFrames"][0]["sha256"] = sha256_path(repeated_hash_frame)
    repeated_hash_review["scenes"] = repeated_hash_review["scenes"][:2]
    repeated_hash_review["transitions"] = []
    repeated_hash_review_path = project / "artifacts" / "reviews" / "visual-review-repeated-hash.json"
    write_json(repeated_hash_review_path, repeated_hash_review)
    repeated_hash_args = copy.copy(fixture["args"])
    repeated_hash_args.visual_review = repeated_hash_review_path
    repeated_hash_evidence = check_visual_contract.validate(repeated_hash_args)

    non_straddling_review = copy.deepcopy(fixture["visualReview"])
    non_straddling_review["scenes"] = []
    transition_review = non_straddling_review["transitions"][0]
    for frame, timestamp in zip(transition_review["evidenceFrames"], [4.1, 4.2, 4.3], strict=True):
        source_frame = project / "artifacts" / "reviews" / "decoded-video" / f"video-frame-{int(timestamp * 10):03d}.png"
        frame["timestamp"] = timestamp
        frame["path"] = source_frame.relative_to(project).as_posix()
        frame["sha256"] = sha256_path(source_frame)
    non_straddling_review["transitions"] = [transition_review]
    non_straddling_review_path = project / "artifacts" / "reviews" / "visual-review-non-straddling.json"
    write_json(non_straddling_review_path, non_straddling_review)
    non_straddling_args = copy.copy(fixture["args"])
    non_straddling_args.visual_review = non_straddling_review_path
    non_straddling_evidence = check_visual_contract.validate(non_straddling_args)

    missing_object_ids_plan = copy.deepcopy(fixture["compositionPlan"])
    missing_object_ids_plan["scenes"][0]["objectBounds"][0].pop("id", None)
    missing_object_ids_path = project / "source" / "composition-plan-missing-object-ids.json"
    write_json(missing_object_ids_path, missing_object_ids_plan)
    missing_object_ids_args = copy.copy(fixture["args"])
    missing_object_ids_args.composition_plan = missing_object_ids_path
    missing_object_ids_args.visual_review = None
    missing_object_ids_args.video = None
    missing_object_ids_args.require_reviewed_scenes = False
    missing_object_ids = check_visual_contract.validate(missing_object_ids_args)

    escaped_asset = project.parent / "escaped-asset.png"
    create_visual_png(escaped_asset, 91, "escaped project asset")
    escaped_report = project / "artifacts" / "reviews" / "producers" / "escaped-asset.json"
    write_json(
        escaped_report,
        {
            "ok": True,
            "assetId": "asset-01",
            "skill": "imagegen",
            "output": "../escaped-asset.png",
            "sha256": sha256_path(escaped_asset),
            "outputSha256": sha256_path(escaped_asset),
        },
    )
    escaped_manifest = copy.deepcopy(fixture["assetManifest"])
    escaped_manifest["assets"][0]["output"] = "../escaped-asset.png"
    escaped_manifest["assets"][0]["sha256"] = sha256_path(escaped_asset)
    escaped_manifest["assets"][0]["producer"]["report"] = escaped_report.relative_to(project).as_posix()
    escaped_manifest_path = project / "source" / "asset-manifest-escaped-path.json"
    write_json(escaped_manifest_path, escaped_manifest)
    escaped_args = copy.copy(fixture["args"])
    escaped_args.asset_manifest = escaped_manifest_path
    escaped_args.visual_review = None
    escaped_args.video = None
    escaped_args.require_reviewed_scenes = False
    escaped = check_visual_contract.validate(escaped_args)

    bare_route_proof = project / "artifacts" / "reviews" / "routing" / "bare-route-proof.json"
    bare_producer_report = project / "artifacts" / "reviews" / "producers" / "bare-producer-report.json"
    write_json(bare_route_proof, {"ok": True})
    bare_manifest = copy.deepcopy(fixture["assetManifest"])
    first_asset = bare_manifest["assets"][0]
    write_json(
        bare_producer_report,
        {
            "schemaVersion": 1,
            "ok": True,
            "assetId": first_asset["id"],
            "skill": first_asset["producer"]["skill"],
            "output": first_asset["output"],
            "sha256": first_asset["sha256"],
        },
    )
    bare_manifest["skillRouting"][0]["proof"] = bare_route_proof.relative_to(project).as_posix()
    bare_manifest["assets"][0]["producer"]["report"] = bare_producer_report.relative_to(project).as_posix()
    bare_manifest_path = project / "source" / "asset-manifest-bare-proofs.json"
    write_json(bare_manifest_path, bare_manifest)
    bare_args = copy.copy(fixture["args"])
    bare_args.asset_manifest = bare_manifest_path
    bare_args.visual_review = None
    bare_args.video = None
    bare_args.require_reviewed_scenes = False
    bare_proofs = check_visual_contract.validate(bare_args)

    text_asset_path = project / "assets" / "generated" / "asset-01.txt"
    text_asset_path.write_text(
        "This prose file is intentionally not a visible media asset.",
        encoding="utf-8",
        newline="\n",
    )
    text_manifest = copy.deepcopy(fixture["assetManifest"])
    text_asset = text_manifest["assets"][0]
    text_asset["output"] = text_asset_path.relative_to(project).as_posix()
    text_asset["sha256"] = sha256_path(text_asset_path)
    original_producer_report = project / str(fixture["assetManifest"]["assets"][0]["producer"]["report"])
    text_producer_payload = json.loads(original_producer_report.read_text(encoding="utf-8"))
    text_producer_payload["output"] = text_asset["output"]
    text_producer_payload["sha256"] = text_asset["sha256"]
    text_producer_payload["outputSha256"] = text_asset["sha256"]
    text_producer_report = project / "artifacts" / "reviews" / "producers" / "asset-01-text.json"
    write_json(text_producer_report, text_producer_payload)
    text_asset["producer"]["report"] = text_producer_report.relative_to(project).as_posix()
    text_manifest_path = project / "source" / "asset-manifest-text-output.json"
    write_json(text_manifest_path, text_manifest)
    text_args = copy.copy(fixture["args"])
    text_args.asset_manifest = text_manifest_path
    text_args.visual_review = None
    text_args.video = None
    text_args.require_reviewed_scenes = False
    text_asset_result = check_visual_contract.validate(text_args)

    media_technical = {
        "targetWidth": 640,
        "targetHeight": 360,
        "aspectRatio": "16:9",
        "maxUpscale": 1.0,
        "crop": "Preserve the complete validation surface.",
    }
    valid_video_asset = check_visual_contract.inspect_asset(fixture["video"], media_technical)
    invalid_video_path = project / "assets" / "generated" / "invalid-video.mp4"
    write_bytes(invalid_video_path, 1_024)
    invalid_video_asset = check_visual_contract.inspect_asset(invalid_video_path, media_technical)
    valid_gltf_path = project / "assets" / "generated" / "valid-scene.gltf"
    write_json(
        valid_gltf_path,
        {
            "asset": {"version": "2.0", "generator": "awsome-videos deterministic contract fixture"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0, "name": "source-bound mechanism node"}],
            "meshes": [{"name": "source-bound mechanism mesh", "primitives": [{"attributes": {}}]}],
            "extras": {"validationNote": "x" * 320},
        },
    )
    valid_gltf_asset = check_visual_contract.inspect_asset(valid_gltf_path, media_technical)
    invalid_gltf_path = project / "assets" / "generated" / "invalid-scene.gltf"
    invalid_gltf_path.write_text("not-json-" + ("x" * 320), encoding="utf-8", newline="\n")
    invalid_gltf_asset = check_visual_contract.inspect_asset(invalid_gltf_path, media_technical)
    glb_document = json.dumps(
        {
            "asset": {"version": "2.0"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{"primitives": [{"attributes": {}}]}],
            "extras": {"validationNote": "y" * 320},
        },
        separators=(",", ":"),
    ).encode("utf-8")
    glb_document += b" " * ((4 - len(glb_document) % 4) % 4)
    valid_glb_payload = (
        struct.pack("<III", 0x46546C67, 2, 20 + len(glb_document))
        + struct.pack("<II", len(glb_document), 0x4E4F534A)
        + glb_document
    )
    valid_glb_path = project / "assets" / "generated" / "valid-scene.glb"
    valid_glb_path.write_bytes(valid_glb_payload)
    valid_glb_asset = check_visual_contract.inspect_asset(valid_glb_path, media_technical)
    invalid_glb_path = project / "assets" / "generated" / "invalid-scene.glb"
    write_bytes(invalid_glb_path, 1_024)
    invalid_glb_asset = check_visual_contract.inspect_asset(invalid_glb_path, media_technical)

    inline_renderer = project / "src" / "inline-fake-renderer.html"
    create_inline_fake_renderer(inline_renderer)
    inline_renderer_report = check_renderer_contract.sample_renderer(
        make_args(
            html=inline_renderer,
            video_id="inline-fake",
            duration=8.0,
            width=640,
            height=360,
            brief=None,
            asset_manifest=fixture["assetManifestPath"],
            composition_plan=fixture["compositionPlanPath"],
            require_visual_ids=True,
            require_all_brief_beats=False,
            brief_beat_sample_position=0.5,
            times=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5],
            min_unique_beats=8,
            min_screenshot_stddev=4.0,
            min_screenshot_colors=32,
            screenshot_dir=None,
            output=None,
            install_browser=False,
            json=True,
        )
    )

    bound_renderer = project / "src" / "bound-asset-renderer.html"
    create_bound_asset_renderer(bound_renderer, fixture)
    bound_screenshot_dir = project / "artifacts" / "reviews" / "bound-renderer-frames"
    live_bound_renderer_report = check_renderer_contract.sample_renderer(
        make_args(
            html=bound_renderer,
            video_id="bound-assets",
            duration=70.0,
            width=640,
            height=360,
            brief=fixture["brief"],
            asset_manifest=fixture["assetManifestPath"],
            composition_plan=fixture["compositionPlanPath"],
            require_visual_ids=True,
            require_all_brief_beats=True,
            brief_beat_sample_position=0.5,
            times=None,
            min_unique_beats=8,
            min_screenshot_stddev=4.0,
            min_screenshot_colors=32,
            screenshot_dir=bound_screenshot_dir,
            output=None,
            install_browser=False,
            json=True,
        )
    )
    inline_spoof_renderer = project / "src" / "inline-resource-spoof.html"
    create_inline_resource_spoof_renderer(inline_spoof_renderer, fixture)
    inline_spoof_report = check_renderer_contract.sample_renderer(
        make_args(
            html=inline_spoof_renderer,
            video_id="inline-resource-spoof",
            duration=70.0,
            width=640,
            height=360,
            brief=fixture["brief"],
            asset_manifest=fixture["assetManifestPath"],
            composition_plan=fixture["compositionPlanPath"],
            require_visual_ids=True,
            require_all_brief_beats=True,
            brief_beat_sample_position=0.5,
            times=None,
            min_unique_beats=8,
            min_screenshot_stddev=4.0,
            min_screenshot_colors=32,
            screenshot_dir=None,
            output=None,
            install_browser=False,
            json=True,
        )
    )
    first_asset = fixture["assetManifest"]["assets"][0]
    first_asset_path = project / str(first_asset["output"])
    single_binding_expectation = {
        str(first_asset["id"]): {
            "output": str(first_asset["output"]),
            "sha256": str(first_asset["sha256"]),
            "resolvedOutput": str(first_asset_path.resolve()),
        }
    }
    broken_video_binding = check_renderer_contract.validate_visible_asset_bindings(
        [
            {
                "time": 0.5,
                "visibleAssetBindings": [
                    {
                        "id": first_asset["id"],
                        "source": first_asset["output"],
                        "sha256": first_asset["sha256"],
                        "tag": "video",
                        "bindingElementIsVisual": True,
                        "mediaUrl": first_asset_path.resolve().as_uri(),
                        "mediaReady": False,
                        "mediaError": "video readyState is below decoded-current-data",
                    }
                ],
            }
        ],
        single_binding_expectation,
    )
    hidden_wrapper_binding = check_renderer_contract.validate_visible_asset_bindings(
        [
            {
                "time": 0.5,
                "visibleAssetBindings": [
                    {
                        "id": first_asset["id"],
                        "source": first_asset["output"],
                        "sha256": first_asset["sha256"],
                        "tag": "div",
                        "bindingElementIsVisual": False,
                    }
                ],
            }
        ],
        single_binding_expectation,
    )

    scaffold_renderer = project / "src" / "wireframe.html"
    scaffold_renderer.parent.mkdir(parents=True, exist_ok=True)
    scaffold_renderer.write_text(
        "<!doctype html><script>window.AWSOME_SCAFFOLD_WIREFRAME=true; window.renderConceptFrame=()=>({});</script>",
        encoding="utf-8",
        newline="\n",
    )
    scaffold_failures: list[str] = []
    scaffold_warnings: list[str] = []
    scaffold_info = check_production_package.validate_renderer(
        scaffold_renderer,
        scaffold_failures,
        scaffold_warnings,
        required=True,
        forbid_scaffold=True,
    )
    markerless_scaffold = project / "src" / "markerless-wireframe.html"
    markerless_text = (
        (check_production_package.SCAFFOLD_TEMPLATE.read_text(encoding="utf-8"))
        .replace("AWSOME_SCAFFOLD_WIREFRAME", "REMOVED_STARTER_MARKER")
        .replace('rendererMode: "wireframe"', 'rendererMode: "production"')
    )
    markerless_scaffold.write_text(markerless_text, encoding="utf-8", newline="\n")
    markerless_failures: list[str] = []
    markerless_info = check_production_package.validate_renderer(
        markerless_scaffold,
        markerless_failures,
        [],
        required=True,
        forbid_scaffold=True,
    )
    expected_renderer_digests = {
        "rendererSha256": sha256_path(bound_renderer),
        "assetManifestSha256": sha256_path(fixture["assetManifestPath"]),
        "compositionPlanSha256": sha256_path(fixture["compositionPlanPath"]),
    }
    bound_renderer_report = project / "artifacts" / "reviews" / "renderer-bound-coverage.json"
    write_json(bound_renderer_report, live_bound_renderer_report)
    bound_candidate_video = project / "artifacts" / "videos" / "bound-renderer.mp4"
    create_renderer_hold_video(
        live_bound_renderer_report,
        bound_candidate_video,
        fixture["sceneRanges"],
    )
    live_package_args = make_args(
        renderer=bound_renderer,
        renderer_report=bound_renderer_report,
        asset_manifest=fixture["assetManifestPath"],
        composition_plan=fixture["compositionPlanPath"],
        brief=fixture["brief"],
        video=bound_candidate_video,
        expect_duration=70.0,
        expect_width=640,
        expect_height=360,
        expect_fps=30.0,
    )
    live_package_failures: list[str] = []
    live_package_renderer, _ = check_production_package.live_renderer_contract(
        live_package_args,
        {"properties": {"durationSeconds": 70.0, "width": 640, "height": 360, "fps": 30.0}},
        live_package_failures,
    )
    forged_renderer_report = project / "artifacts" / "reviews" / "renderer-forged-coverage.json"
    forged_renderer_payload = copy.deepcopy(live_bound_renderer_report)
    forged_renderer_payload["observedAssetIds"] = list(reversed(forged_renderer_payload["observedAssetIds"]))[:-1]
    write_json(forged_renderer_report, forged_renderer_payload)
    forged_live_args = copy.copy(live_package_args)
    forged_live_args.renderer_report = forged_renderer_report
    forged_live_args.video = fixture["video"]
    forged_live_failures: list[str] = []
    forged_live_renderer, _ = check_production_package.live_renderer_contract(
        forged_live_args,
        {"properties": {"durationSeconds": 70.0, "width": 640, "height": 360, "fps": 30.0}},
        forged_live_failures,
    )
    bound_renderer_failures: list[str] = []
    bound_renderer_warnings: list[str] = []
    bound_renderer_info = check_production_package.validate_json_report(
        bound_renderer_report,
        "renderer contract report",
        bound_renderer_failures,
        bound_renderer_warnings,
        required=True,
        require_renderer_visual_coverage=True,
        expected_input_digests=expected_renderer_digests,
    )
    thin_renderer_report = project / "artifacts" / "reviews" / "renderer-thin-coverage.json"
    write_json(
        thin_renderer_report,
        {
            "ok": False,
            "briefBeatCoverageOk": True,
            "visualAssetCoverageOk": False,
            "assetBindingCoverageOk": False,
            "compositionCoverageOk": False,
            "missingAssetIds": ["asset-08"],
            "missingCompositionIds": ["s08", "s08-focal"],
            "missingCompositionObjectIds": ["s08:s08-focal"],
            "assetManifestSha256": "0" * 64,
        },
    )
    renderer_coverage_info = check_production_package.validate_json_report(
        thin_renderer_report,
        "renderer contract report",
        scaffold_failures,
        scaffold_warnings,
        required=True,
        require_renderer_visual_coverage=True,
        expected_input_digests=expected_renderer_digests,
    )

    report_on_disk = json.loads(fixture["visualContractReportPath"].read_text(encoding="utf-8"))
    digest_keys = {"assetManifestSha256", "compositionPlanSha256", "visualReviewSha256", "videoSha256"}
    passed = bool(
        report.get("ok")
        and report_on_disk == report
        and report.get("assetManifest", {}).get("assetCount") == 8
        and report.get("assetManifest", {}).get("readyAssetCount") == 8
        and len(report.get("assetManifest", {}).get("inspections", {})) == 8
        and report.get("compositionPlan", {}).get("sceneCount") == 8
        and report.get("compositionPlan", {}).get("compositionChoiceCount", 0) >= 4
        and report.get("compositionPlan", {}).get("armatureCount", 0) >= 4
        and report.get("compositionPlan", {}).get("spatialLayoutCount", 0) >= 3
        and report.get("visualReview", {}).get("sceneReviewCount") == 8
        and report.get("visualReview", {}).get("evidenceFrameCount") == 53
        and report.get("visualReview", {}).get("sceneEvidenceFrameCount") == 32
        and report.get("visualReview", {}).get("transitionEvidenceFrameCount") == 21
        and report.get("visualReview", {}).get("transitionReviewCount") == 7
        and report.get("visualReview", {}).get("videoFrameMatchCount") == 53
        and all(item.get("ok") is True for item in report.get("visualReview", {}).get("videoFrameMatches", []))
        and report.get("visualReview", {}).get("overallStatus") == "approved"
        and digest_keys.issubset(report.get("inputDigests", {}))
        and all(report.get("inputDigests", {}).get(key) for key in digest_keys)
        and not planned.get("ok")
        and any("is not ready" in item for item in planned.get("failures", []))
        and any("asset file missing" in item for item in planned.get("failures", []))
        and not stale.get("ok")
        and any("sha256 does not match" in item for item in stale.get("failures", []))
        and any("producer report does not carry a passing status" in item for item in stale.get("failures", []))
        and not seam.get("ok")
        and any("unknown asset" in item for item in seam.get("failures", []))
        and any("never used" in item for item in seam.get("failures", []))
        and not reversed_beats.get("ok")
        and any(
            "beat id to scene id mapping" in item.lower()
            for item in reversed_beats.get("failures", [])
        )
        and not thin.get("ok")
        and any("distinct composition choices" in item for item in thin.get("failures", []))
        and any("distinct armatures" in item for item in thin.get("failures", []))
        and any("distinct spatial layouts" in item for item in thin.get("failures", []))
        and any("missing or too thin" in item for item in thin.get("failures", []))
        and not pending.get("ok")
        and any("full-speed playback" in item for item in pending.get("failures", []))
        and any("overallStatus" in item for item in pending.get("failures", []))
        and not unrelated_evidence.get("ok")
        and any("does not match candidate video" in item for item in unrelated_evidence.get("failures", []))
        and any(
            item.get("ok") is False
            for item in unrelated_evidence.get("visualReview", {}).get("videoFrameMatches", [])
        )
        and {
            item.get("phase")
            for item in unrelated_evidence.get("visualReview", {}).get("videoFrameMatches", [])
            if item.get("ok") is False
        }.issuperset({"hold", "before"})
        and not bad_timing.get("ok")
        and any("timestamps must increase" in item for item in bad_timing.get("failures", []))
        and any("timestamps must stay inside" in item for item in bad_timing.get("failures", []))
        and not repeated_hash_evidence.get("ok")
        and any("reuses an evidence-frame hash" in item for item in repeated_hash_evidence.get("failures", []))
        and not non_straddling_evidence.get("ok")
        and any("evidence must straddle" in item for item in non_straddling_evidence.get("failures", []))
        and not missing_object_ids.get("ok")
        and any(
            "objectbounds" in item.lower() and "id" in item.lower()
            for item in missing_object_ids.get("failures", [])
        )
        and not escaped.get("ok")
        and any(
            "project root" in item.lower() and any(term in item.lower() for term in ["escape", "outside", "within"])
            for item in escaped.get("failures", [])
        )
        and not bare_proofs.get("ok")
        and any(
            "skillrouting[0] proof" in item.lower()
            and any(term in item.lower() for term in ["skill", "output", "sha256", "hash", "bind"])
            for item in bare_proofs.get("failures", [])
        )
        and any(
            "producer report" in item.lower()
            and any(term in item.lower() for term in ["structured checks", "check"])
            for item in bare_proofs.get("failures", [])
        )
        and not text_asset_result.get("ok")
        and any(
            "unsupported visual/media extension" in item.lower()
            for item in text_asset_result.get("failures", [])
        )
        and valid_video_asset.get("ok")
        and not invalid_video_asset.get("ok")
        and valid_gltf_asset.get("ok")
        and not invalid_gltf_asset.get("ok")
        and valid_glb_asset.get("ok")
        and not invalid_glb_asset.get("ok")
        and not inline_renderer_report.get("ok")
        and inline_renderer_report.get("assetBindingCoverageOk") is False
        and any(
            "asset" in item.lower()
            and any(term in item.lower() for term in ["output", "sha256", "hash", "media", "source file"])
            for item in inline_renderer_report.get("failures", [])
        )
        and live_bound_renderer_report.get("ok")
        and live_bound_renderer_report.get("assetBindingCoverageOk") is True
        and live_bound_renderer_report.get("visualAssetCoverageOk") is True
        and live_bound_renderer_report.get("compositionCoverageOk") is True
        and not inline_spoof_report.get("ok")
        and any("did not actually load" in item for item in inline_spoof_report.get("failures", []))
        and not broken_video_binding.get("ok")
        and any("not a healthy loaded video" in item for item in broken_video_binding.get("failures", []))
        and not hidden_wrapper_binding.get("ok")
        and any("visible media element" in item for item in hidden_wrapper_binding.get("failures", []))
        and scaffold_info
        and scaffold_info.get("scaffoldWireframe") is True
        and any("AWSOME_SCAFFOLD_WIREFRAME" in item for item in scaffold_failures)
        and markerless_info
        and markerless_info.get("scaffoldWireframe") is True
        and any("structurally similar" in item for item in markerless_failures)
        and bound_renderer_info
        and not bound_renderer_failures
        and bound_renderer_info.get("ok") is True
        and bound_renderer_info.get("assetBindingCoverageOk") is True
        and all(bound_renderer_info.get(key) == value for key, value in expected_renderer_digests.items())
        and live_package_renderer.get("ok")
        and live_package_renderer.get("candidateVideoPixelCoverageOk") is True
        and live_package_renderer.get("storedReportMatches") is True
        and not live_package_failures
        and not forged_live_renderer.get("ok")
        and any("pixels are not bound" in item for item in forged_live_failures)
        and any("stored renderer report differs" in item for item in forged_live_failures)
        and renderer_coverage_info
        and renderer_coverage_info.get("ok") is False
        and renderer_coverage_info.get("visualAssetCoverageOk") is False
        and renderer_coverage_info.get("compositionCoverageOk") is False
        and any("visible asset ID coverage" in item for item in scaffold_failures)
        and any("visible composition ID coverage" in item for item in scaffold_failures)
        and any("must carry ok=true" in item for item in scaffold_failures)
        and any("stale or missing assetManifestSha256" in item for item in scaffold_failures)
        and any("stale or missing compositionPlanSha256" in item for item in scaffold_failures)
    )
    return {
        "passed": passed,
        "positiveOk": report.get("ok"),
        "positiveFailures": report.get("failures"),
        "assetCount": report.get("assetManifest", {}).get("assetCount"),
        "readyAssetCount": report.get("assetManifest", {}).get("readyAssetCount"),
        "assetInspectionCount": len(report.get("assetManifest", {}).get("inspections", {})),
        "sceneCount": report.get("compositionPlan", {}).get("sceneCount"),
        "compositionChoiceCount": report.get("compositionPlan", {}).get("compositionChoiceCount"),
        "armatureCount": report.get("compositionPlan", {}).get("armatureCount"),
        "spatialLayoutCount": report.get("compositionPlan", {}).get("spatialLayoutCount"),
        "evidenceFrameCount": report.get("visualReview", {}).get("evidenceFrameCount"),
        "sceneEvidenceFrameCount": report.get("visualReview", {}).get("sceneEvidenceFrameCount"),
        "transitionEvidenceFrameCount": report.get("visualReview", {}).get("transitionEvidenceFrameCount"),
        "transitionReviewCount": report.get("visualReview", {}).get("transitionReviewCount"),
        "videoFrameMatchCount": report.get("visualReview", {}).get("videoFrameMatchCount"),
        "videoFrameMatches": report.get("visualReview", {}).get("videoFrameMatches"),
        "inputDigestKeys": sorted(report.get("inputDigests", {})),
        "plannedFailures": planned.get("failures"),
        "staleFailures": stale.get("failures"),
        "seamFailures": seam.get("failures"),
        "reversedBeatFailures": reversed_beats.get("failures"),
        "thinCompositionFailures": thin.get("failures"),
        "pendingReviewFailures": pending.get("failures"),
        "unrelatedEvidenceFailures": unrelated_evidence.get("failures"),
        "unrelatedEvidenceVideoMatches": unrelated_evidence.get("visualReview", {}).get("videoFrameMatches"),
        "badTimingFailures": bad_timing.get("failures"),
        "repeatedHashFailures": repeated_hash_evidence.get("failures"),
        "nonStraddlingFailures": non_straddling_evidence.get("failures"),
        "missingObjectIdsFailures": missing_object_ids.get("failures"),
        "escapedPathFailures": escaped.get("failures"),
        "bareProofFailures": bare_proofs.get("failures"),
        "textAssetFailures": text_asset_result.get("failures"),
        "validVideoAsset": valid_video_asset,
        "invalidVideoAsset": invalid_video_asset,
        "validGltfAsset": valid_gltf_asset,
        "invalidGltfAsset": invalid_gltf_asset,
        "validGlbAsset": valid_glb_asset,
        "invalidGlbAsset": invalid_glb_asset,
        "inlineFakeRendererOk": inline_renderer_report.get("ok"),
        "inlineFakeRendererFailures": inline_renderer_report.get("failures"),
        "inlineFakeRendererMediaBindingOk": inline_renderer_report.get("assetMediaBindingOk"),
        "liveBoundRendererOk": live_bound_renderer_report.get("ok"),
        "liveBoundRendererFailures": live_bound_renderer_report.get("failures"),
        "inlineResourceSpoofFailures": inline_spoof_report.get("failures"),
        "brokenVideoBindingFailures": broken_video_binding.get("failures"),
        "hiddenWrapperBindingFailures": hidden_wrapper_binding.get("failures"),
        "scaffoldRendererInfo": scaffold_info,
        "markerlessScaffoldInfo": markerless_info,
        "markerlessScaffoldFailures": markerless_failures,
        "boundRendererInfo": bound_renderer_info,
        "boundRendererFailures": bound_renderer_failures,
        "livePackageRenderer": live_package_renderer,
        "livePackageFailures": live_package_failures,
        "forgedLiveRenderer": forged_live_renderer,
        "forgedLiveFailures": forged_live_failures,
        "rendererCoverageInfo": renderer_coverage_info,
        "scaffoldCoverageFailures": scaffold_failures,
        "warnings": report.get("warnings"),
    }


def test_brief_validator() -> dict[str, Any]:
    strong = check_video_brief.validate(STRONG_BRIEF, min_beats=8)
    strong_voiceover = check_video_brief.validate(STRONG_BRIEF, min_beats=8, require_voiceover=True)
    strong_source_links = check_video_brief.validate(STRONG_BRIEF, min_beats=8, require_source_links=True)
    indented_source_links = check_video_brief.validate(
        INDENTED_SOURCE_LINKS_BRIEF,
        min_beats=8,
        require_source_links=True,
    )
    markdown_labels = check_video_brief.validate(
        MARKDOWN_LABEL_BRIEF,
        min_beats=8,
        require_voiceover=True,
        require_source_links=True,
    )
    no_source_links = check_video_brief.validate(NO_SOURCE_LINKS_BRIEF, min_beats=8, require_source_links=True)
    missing = check_video_brief.validate(MISSING_BEATS_BRIEF, min_beats=8)
    weak = check_video_brief.validate(WEAK_BRIEF, min_beats=8)
    blank_hook = check_video_brief.validate(BLANK_HOOK_BRIEF, min_beats=8)
    generic_voiceover = check_video_brief.validate(
        replace_voiceover(STRONG_BRIEF, GENERIC_VOICEOVER_LINES),
        min_beats=8,
        require_voiceover=True,
    )
    repeated_voiceover = check_video_brief.validate(
        replace_voiceover(STRONG_BRIEF, REPEATED_VOICEOVER_LINES),
        min_beats=8,
        require_voiceover=True,
    )
    no_voiceover_text = re.sub(
        r"\n## Voiceover Draft\n.*?(?=\n## Script Style Notes)",
        "\n",
        STRONG_BRIEF,
        flags=re.DOTALL,
    )
    missing_voiceover = check_video_brief.validate(no_voiceover_text, min_beats=8, require_voiceover=True)
    return {
        "passed": bool(
            strong["ok"]
            and strong_voiceover["ok"]
            and strong_source_links["ok"]
            and strong_source_links["source_link_count"] >= 2
            and indented_source_links["ok"]
            and indented_source_links["source_link_count"] >= 3
            and markdown_labels["ok"]
            and markdown_labels["source_link_count"] >= 2
            and not no_source_links["ok"]
            and no_source_links["source_link_failures"]
            and not missing["ok"]
            and not weak["ok"]
            and weak["beat_table_generic_fields"]
            and not blank_hook["ok"]
            and blank_hook["labeled_field_missing"]
            and not missing_voiceover["ok"]
            and not generic_voiceover["ok"]
            and generic_voiceover["voiceover_generic_lines"]
            and not repeated_voiceover["ok"]
            and repeated_voiceover["voiceover_duplicate_lines"]
        ),
        "strongOk": strong["ok"],
        "strongBeatRows": strong["beat_table_rows"],
        "strongVoiceoverOk": strong_voiceover["ok"],
        "strongVoiceoverLineCount": strong_voiceover["voiceover_line_count"],
        "strongSourceLinksOk": strong_source_links["ok"],
        "strongSourceLinkCount": strong_source_links["source_link_count"],
        "indentedSourceLinksOk": indented_source_links["ok"],
        "indentedSourceLinkCount": indented_source_links["source_link_count"],
        "indentedSourceLinks": indented_source_links["source_links"],
        "markdownLabelsOk": markdown_labels["ok"],
        "markdownLabelValues": markdown_labels["labeled_field_values"],
        "markdownLabelSourceLinkCount": markdown_labels["source_link_count"],
        "noSourceLinksOk": no_source_links["ok"],
        "noSourceLinkFailures": no_source_links["source_link_failures"],
        "missingOk": missing["ok"],
        "missingFailures": missing["failures"],
        "weakOk": weak["ok"],
        "weakGenericFields": weak["beat_table_generic_fields"],
        "blankHookOk": blank_hook["ok"],
        "blankHookMissingFields": blank_hook["labeled_field_missing"],
        "missingVoiceoverOk": missing_voiceover["ok"],
        "missingVoiceoverFailures": missing_voiceover["failures"],
        "genericVoiceoverOk": generic_voiceover["ok"],
        "genericVoiceoverLines": generic_voiceover["voiceover_generic_lines"],
        "genericVoiceoverFailures": generic_voiceover["failures"],
        "repeatedVoiceoverOk": repeated_voiceover["ok"],
        "repeatedVoiceoverLines": repeated_voiceover["voiceover_duplicate_lines"],
        "repeatedVoiceoverFailures": repeated_voiceover["failures"],
    }


def test_readiness_scorer(tmp: Path, visual_fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    strong_brief = tmp / "strong.md"
    weak_brief = tmp / "weak.md"
    no_voiceover_brief = tmp / "no-voiceover.md"
    no_source_links_brief = tmp / "no-source-links.md"
    strong_brief.write_text(STRONG_BRIEF, encoding="utf-8")
    weak_brief.write_text(WEAK_BRIEF, encoding="utf-8")
    no_source_links_brief.write_text(NO_SOURCE_LINKS_BRIEF, encoding="utf-8")
    no_voiceover_text = re.sub(
        r"\n## Voiceover Draft\n.*?(?=\n## Script Style Notes)",
        "\n",
        STRONG_BRIEF,
        flags=re.DOTALL,
    )
    no_voiceover_brief.write_text(no_voiceover_text, encoding="utf-8")
    video = tmp / "video.mp4"
    contact_sheet = tmp / "contact-sheet.jpg"
    renderer_report = tmp / "render-state.json"
    quality_report = tmp / "quality-report.json"
    motion_report = tmp / "motion-report.json"
    capture_manifest = tmp / "capture-manifest.json"
    audio_report = tmp / "audio-report.json"
    short_final_audio_report = tmp / "short-final-audio-report.json"
    write_bytes(video, 2_048)
    write_bytes(contact_sheet, 2_048)
    write_json(
        renderer_report,
        {
            "ok": True,
            "states": [{"state": {"activeBeat": index}} for index in range(1, 7)],
            "uniqueBeats": [1, 2, 3, 4, 5, 6],
            "visualAssetCoverageOk": True,
            "compositionCoverageOk": True,
            "observedAssetIds": [f"asset-{index:02d}" for index in range(1, 9)],
            "observedCompositionIds": [f"s{index:02d}" for index in range(1, 9)],
        },
    )
    write_json(quality_report, {"ok": True, "passed": True, "findings": []})
    write_json(motion_report, {"ok": True, "passed": True, "findings": []})
    write_json(capture_manifest, {"ok": True, "findings": []})
    write_json(
        audio_report,
        {
            "ok": True,
            "mode": "sine",
            "placeholderAudio": True,
            "finalAudioReady": False,
            "finalAudioDurationOk": True,
            "sourceDurationSeconds": 2.0,
            "expectedDurationSeconds": 2.0,
            "needsFinalAudio": True,
        },
    )
    write_json(
        short_final_audio_report,
        {
            "ok": True,
            "mode": "file",
            "placeholderAudio": False,
            "finalAudioReady": True,
            "finalAudioDurationOk": False,
            "sourceDurationSeconds": 0.4,
            "expectedDurationSeconds": 2.0,
            "needsFinalAudio": True,
        },
    )

    strong = score_video_readiness.score(
        make_args(
            brief=strong_brief,
            video=video,
            video_validation=None,
            package_validation=None,
            renderer_report=renderer_report,
            quality_report=quality_report,
            motion_report=motion_report,
            capture_manifest=capture_manifest,
            audio_report=audio_report,
            require_final_audio=False,
            contact_sheet=contact_sheet,
            require_voiceover=True,
            min_voiceover_lines=None,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    visual_fixture = visual_fixture or build_visual_contract_fixture(tmp / "readiness-visual-contract")
    verified_renderer_report = tmp / "readiness-verified-renderer.json"
    expected_assets = [f"asset-{index:02d}" for index in range(1, 9)]
    expected_compositions = [f"s{index:02d}" for index in range(1, 9)]
    write_json(
        verified_renderer_report,
        {
            "ok": True,
            "states": [{"state": {"activeBeat": index}} for index in range(1, 9)],
            "uniqueBeats": list(range(1, 9)),
            "briefBeatCoverageOk": True,
            "missingBriefBeats": [],
            "visualAssetCoverageOk": True,
            "assetBindingCoverageOk": True,
            "compositionCoverageOk": True,
            "expectedAssetIds": expected_assets,
            "observedAssetIds": expected_assets,
            "missingAssetIds": [],
            "expectedCompositionIds": expected_compositions,
            "observedCompositionIds": expected_compositions,
            "missingCompositionIds": [],
            "missingCompositionObjectIds": [],
            "rendererSha256": sha256_path(visual_fixture["project"] / "src" / "index.html"),
            "assetManifestSha256": visual_fixture["report"]["inputDigests"]["assetManifestSha256"],
            "compositionPlanSha256": visual_fixture["report"]["inputDigests"]["compositionPlanSha256"],
        },
    )
    visual_proven = score_video_readiness.score(
        make_args(
            brief=strong_brief,
            video=visual_fixture["video"],
            video_validation=None,
            package_validation=None,
            renderer_report=verified_renderer_report,
            renderer=visual_fixture["project"] / "src" / "index.html",
            asset_manifest=visual_fixture["assetManifestPath"],
            composition_plan=visual_fixture["compositionPlanPath"],
            visual_review=visual_fixture["visualReviewPath"],
            visual_contract_report=visual_fixture["visualContractReportPath"],
            require_visual_contract_report=True,
            quality_report=quality_report,
            motion_report=motion_report,
            capture_manifest=capture_manifest,
            audio_report=audio_report,
            require_final_audio=False,
            contact_sheet=contact_sheet,
            require_voiceover=True,
            min_voiceover_lines=None,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    live_readiness_path = tmp / "readiness-live-exact.json"
    write_json(live_readiness_path, visual_proven)
    live_readiness_args = make_args(
        brief=strong_brief,
        video=visual_fixture["video"],
        renderer_report=verified_renderer_report,
        renderer=visual_fixture["project"] / "src" / "index.html",
        asset_manifest=visual_fixture["assetManifestPath"],
        composition_plan=visual_fixture["compositionPlanPath"],
        visual_review=visual_fixture["visualReviewPath"],
        visual_contract_report=visual_fixture["visualContractReportPath"],
        require_visual_contract=True,
        require_renderer_visual_coverage=True,
        quality_report=quality_report,
        motion_report=motion_report,
        capture_manifest=capture_manifest,
        audio_report=audio_report,
        require_final_audio=False,
        contact_sheet=contact_sheet,
        require_voiceover=True,
        min_voiceover_lines=None,
        require_source_links=False,
        min_readiness_score=18,
        readiness_report=live_readiness_path,
    )
    live_readiness_failures: list[str] = []
    live_readiness = check_production_package.recompute_readiness(
        live_readiness_args,
        live_readiness_failures,
    )
    forged_readiness_path = tmp / "readiness-live-forged.json"
    forged_readiness_payload = copy.deepcopy(visual_proven)
    forged_readiness_payload["score"] = visual_proven["score"] - 1
    write_json(forged_readiness_path, forged_readiness_payload)
    forged_readiness_args = copy.copy(live_readiness_args)
    forged_readiness_args.readiness_report = forged_readiness_path
    forged_readiness_failures: list[str] = []
    forged_live_readiness = check_production_package.recompute_readiness(
        forged_readiness_args,
        forged_readiness_failures,
    )
    forged_visual_report = tmp / "forged-thin-visual-contract.json"
    zero_state_renderer_report = tmp / "forged-zero-state-renderer.json"
    write_json(
        forged_visual_report,
        {
            "schemaVersion": 1,
            "ok": True,
            "inputDigests": {
                "assetManifestSha256": "0" * 64,
                "compositionPlanSha256": "0" * 64,
                "visualReviewSha256": "0" * 64,
                "videoSha256": "0" * 64,
            },
            "assetManifest": {"assetCount": 0, "readyAssetCount": 0, "inspections": {}},
            "compositionPlan": {"sceneCount": 0, "compositionChoiceCount": 0, "armatureCount": 0},
            "seams": {
                "orphanAssetIds": [],
                "scenesWithoutAssets": [],
                "inconsistentSceneAssetLinks": [],
            },
            "visualReview": {
                "sceneReviewCount": 0,
                "evidenceFrameCount": 0,
                "transitionReviewCount": 0,
                "overallStatus": "approved",
            },
        },
    )
    write_json(
        zero_state_renderer_report,
        {
            "ok": True,
            "states": [],
            "uniqueBeats": [],
            "visualAssetCoverageOk": True,
            "assetBindingCoverageOk": True,
            "compositionCoverageOk": True,
            "expectedAssetIds": [],
            "missingAssetIds": [],
            "expectedCompositionIds": [],
            "missingCompositionIds": [],
            "missingCompositionObjectIds": [],
            "observedAssetIds": [],
            "observedCompositionIds": [],
            "rendererSha256": "0" * 64,
            "assetManifestSha256": "0" * 64,
            "compositionPlanSha256": "0" * 64,
        },
    )
    forged_visual_evidence = score_video_readiness.score(
        make_args(
            brief=strong_brief,
            video=video,
            video_validation=None,
            package_validation=None,
            renderer_report=zero_state_renderer_report,
            visual_contract_report=forged_visual_report,
            require_visual_contract_report=True,
            quality_report=quality_report,
            motion_report=motion_report,
            capture_manifest=capture_manifest,
            audio_report=audio_report,
            require_final_audio=False,
            contact_sheet=contact_sheet,
            require_voiceover=True,
            min_voiceover_lines=None,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    plan_only = score_video_readiness.score(
        make_args(
            brief=strong_brief,
            video=None,
            video_validation=None,
            package_validation=None,
            renderer_report=None,
            quality_report=None,
            motion_report=None,
            capture_manifest=None,
            audio_report=None,
            require_final_audio=False,
            contact_sheet=None,
            require_voiceover=True,
            min_voiceover_lines=None,
            require_source_links=True,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    weak = score_video_readiness.score(
        make_args(
            brief=weak_brief,
            video=None,
            video_validation=None,
            package_validation=None,
            renderer_report=None,
            quality_report=None,
            motion_report=None,
            capture_manifest=None,
            audio_report=None,
            require_final_audio=False,
            contact_sheet=None,
            require_voiceover=False,
            min_voiceover_lines=None,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    missing_voiceover = score_video_readiness.score(
        make_args(
            brief=no_voiceover_brief,
            video=video,
            video_validation=None,
            package_validation=None,
            renderer_report=renderer_report,
            quality_report=quality_report,
            motion_report=motion_report,
            capture_manifest=capture_manifest,
            audio_report=audio_report,
            require_final_audio=False,
            contact_sheet=contact_sheet,
            require_voiceover=True,
            min_voiceover_lines=None,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    missing_source_links = score_video_readiness.score(
        make_args(
            brief=no_source_links_brief,
            video=video,
            video_validation=None,
            package_validation=None,
            renderer_report=renderer_report,
            quality_report=quality_report,
            motion_report=motion_report,
            capture_manifest=capture_manifest,
            audio_report=audio_report,
            require_final_audio=False,
            contact_sheet=contact_sheet,
            require_voiceover=True,
            min_voiceover_lines=None,
            require_source_links=True,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    legacy_renderer_report = tmp / "legacy-render-state.json"
    write_json(
        legacy_renderer_report,
        {
            "passed": True,
            "samples": 12,
            "stateSummary": {
                "activeBeat": {"count": 12, "distinctCount": 10},
                "visibleMechanismCount": {"count": 12, "distinctCount": 10},
            },
            "statesSample": [
                {"sample": 0, "seconds": 0, "state": {"activeBeat": 1, "visibleMechanismCount": 1}},
                {"sample": 1, "seconds": 6.3, "state": {"activeBeat": 2, "visibleMechanismCount": 2}},
                {"sample": 11, "seconds": 69.7, "state": {"activeBeat": 10, "visibleMechanismCount": 10}},
            ],
        },
    )
    legacy = score_video_readiness.score(
        make_args(
            brief=strong_brief,
            video=video,
            video_validation=None,
            package_validation=None,
            renderer_report=legacy_renderer_report,
            quality_report=quality_report,
            motion_report=motion_report,
            capture_manifest=capture_manifest,
            audio_report=audio_report,
            require_final_audio=False,
            contact_sheet=contact_sheet,
            require_voiceover=True,
            min_voiceover_lines=None,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    final_audio_required = score_video_readiness.score(
        make_args(
            brief=strong_brief,
            video=video,
            video_validation=None,
            package_validation=None,
            renderer_report=renderer_report,
            quality_report=quality_report,
            motion_report=motion_report,
            capture_manifest=capture_manifest,
            audio_report=audio_report,
            require_final_audio=True,
            contact_sheet=contact_sheet,
            require_voiceover=True,
            min_voiceover_lines=None,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    short_final_audio_required = score_video_readiness.score(
        make_args(
            brief=strong_brief,
            video=video,
            video_validation=None,
            package_validation=None,
            renderer_report=renderer_report,
            quality_report=quality_report,
            motion_report=motion_report,
            capture_manifest=capture_manifest,
            audio_report=short_final_audio_report,
            require_final_audio=True,
            contact_sheet=contact_sheet,
            require_voiceover=True,
            min_voiceover_lines=None,
            min_ready_score=18,
            output=None,
            json=True,
        )
    )
    return {
        "passed": bool(
            not strong["ok"]
            and strong["score"] == 20
            and strong["categories"]["visual_mechanism"]["score"] == 1
            and strong["categories"]["source_binding"]["score"] == 1
            and strong["brief"].get("source_link_count", 0) >= 2
            and visual_proven["ok"]
            and visual_proven["score"] == 24
            and visual_proven["categories"]["visual_mechanism"]["score"] == 3
            and visual_proven["categories"]["source_binding"]["score"] == 3
            and visual_proven.get("visualContractReport", {}).get("ok") is True
            and live_readiness.get("ok")
            and live_readiness.get("storedReportMatches") is True
            and not live_readiness_failures
            and not forged_live_readiness.get("ok")
            and any("differs from a live recomputation" in item for item in forged_readiness_failures)
            and not forged_visual_evidence["ok"]
            and forged_visual_evidence["categories"]["visual_mechanism"]["score"] <= 1
            and forged_visual_evidence["categories"]["source_binding"]["score"] <= 1
            and plan_only["ok"]
            and plan_only["readiness"] in {"usable", "ready"}
            and plan_only["categories"]["visual_mechanism"]["score"] >= 2
            and plan_only["categories"]["validation"]["score"] >= 2
            and not plan_only["weakCategories"]
            and not legacy["ok"]
            and legacy["categories"]["visual_mechanism"]["score"] == 1
            and legacy["categories"]["source_binding"]["score"] == 1
            and not weak["ok"]
            and weak["weakCategories"]
            and not missing_voiceover["ok"]
            and any("voiceover" in failure for failure in missing_voiceover.get("failures", []))
            and not missing_source_links["ok"]
            and any("source links" in failure for failure in missing_source_links.get("failures", []))
            and not final_audio_required["ok"]
            and any("final audio" in failure for failure in final_audio_required.get("failures", []))
            and not short_final_audio_required["ok"]
            and any("duration coverage" in failure for failure in short_final_audio_required.get("failures", []))
        ),
        "strongScore": strong["score"],
        "strongReadiness": strong["readiness"],
        "strongSourceBinding": strong["categories"]["source_binding"],
        "strongSourceLinkCount": strong["brief"].get("source_link_count"),
        "strongVoiceoverRequiredOk": strong["brief"].get("voiceover_required"),
        "visualProvenOk": visual_proven["ok"],
        "visualProvenScore": visual_proven["score"],
        "visualProvenMechanism": visual_proven["categories"]["visual_mechanism"],
        "visualProvenSourceBinding": visual_proven["categories"]["source_binding"],
        "visualProvenFailures": visual_proven["failures"],
        "liveReadiness": live_readiness,
        "liveReadinessFailures": live_readiness_failures,
        "forgedLiveReadiness": forged_live_readiness,
        "forgedLiveReadinessFailures": forged_readiness_failures,
        "forgedVisualEvidenceOk": forged_visual_evidence["ok"],
        "forgedVisualMechanism": forged_visual_evidence["categories"]["visual_mechanism"],
        "forgedVisualSourceBinding": forged_visual_evidence["categories"]["source_binding"],
        "forgedVisualFailures": forged_visual_evidence["failures"],
        "planOnlyOk": plan_only["ok"],
        "planOnlyScore": plan_only["score"],
        "planOnlyReadiness": plan_only["readiness"],
        "planOnlyVisualMechanism": plan_only["categories"]["visual_mechanism"],
        "planOnlyValidation": plan_only["categories"]["validation"],
        "planOnlyWeakCategories": plan_only["weakCategories"],
        "legacyScore": legacy["score"],
        "legacyVisualMechanism": legacy["categories"]["visual_mechanism"],
        "weakScore": weak["score"],
        "weakCategories": weak["weakCategories"],
        "missingVoiceoverOk": missing_voiceover["ok"],
        "missingVoiceoverFailures": missing_voiceover["failures"],
        "missingSourceLinksOk": missing_source_links["ok"],
        "missingSourceLinksFailures": missing_source_links["failures"],
        "placeholderAudioFinalOk": final_audio_required["ok"],
        "placeholderAudioFinalFailures": final_audio_required["failures"],
        "shortFinalAudioOk": short_final_audio_required["ok"],
        "shortFinalAudioFailures": short_final_audio_required["failures"],
    }


def test_style_fidelity_scorer(tmp: Path) -> dict[str, Any]:
    strong_brief = tmp / "strong-style.md"
    slow_brief = tmp / "slow-style.md"
    blueprint_path = tmp / "pattern-blueprint.json"
    strong_brief.write_text(STRONG_BRIEF, encoding="utf-8")
    slow_brief.write_text(SLOW_STRUCTURED_BRIEF, encoding="utf-8")
    blueprint = select_video_patterns.select_blueprint(
        SimpleNamespace(
            title="What Is A Rate Limit?",
            promise="Explain a rate limit as a token budget with retry timing and failure modes.",
            requested_format="compressed explainer",
            runtime="1:10",
            summary=select_video_patterns.DEFAULT_SUMMARY,
        )
    )
    write_json(blueprint_path, blueprint)
    strong = score_style_fidelity.score(
        make_args(
            brief=strong_brief,
            pattern_blueprint=blueprint_path,
            summary=score_style_fidelity.DEFAULT_SUMMARY,
            min_score=12,
            require_voiceover=True,
            require_source_links=False,
            require_pattern_blueprint=True,
            output=None,
            json=True,
        )
    )
    slow = score_style_fidelity.score(
        make_args(
            brief=slow_brief,
            pattern_blueprint=None,
            summary=score_style_fidelity.DEFAULT_SUMMARY,
            min_score=12,
            require_voiceover=True,
            require_source_links=False,
            require_pattern_blueprint=False,
            output=None,
            json=True,
        )
    )
    missing_blueprint = score_style_fidelity.score(
        make_args(
            brief=strong_brief,
            pattern_blueprint=None,
            summary=score_style_fidelity.DEFAULT_SUMMARY,
            min_score=12,
            require_voiceover=True,
            require_source_links=False,
            require_pattern_blueprint=True,
            output=None,
            json=True,
        )
    )
    return {
        "passed": bool(
            strong.get("ok")
            and strong.get("score", 0) >= 12
            and not strong.get("penalties")
            and strong.get("patternBlueprint", {}).get("ok") is True
            and strong.get("inputDigests", {}).get("briefSha256") == sha256_path(strong_brief)
            and strong.get("inputDigests", {}).get("patternBlueprintSha256") == sha256_path(blueprint_path)
            and strong.get("inputDigests", {}).get("corpusSummarySha256")
            == sha256_path(score_style_fidelity.DEFAULT_SUMMARY)
            and not slow.get("ok")
            and slow.get("score", 16) < 12
            and slow.get("penalties")
            and "style fidelity score below threshold: " in "\n".join(slow.get("failures", []))
            and not missing_blueprint.get("ok")
            and "pattern blueprint is required" in missing_blueprint.get("failures", [])
        ),
        "strongOk": strong.get("ok"),
        "strongScore": strong.get("score"),
        "strongWeakCategories": strong.get("weakCategories"),
        "strongBlueprintOk": strong.get("patternBlueprint", {}).get("ok") if strong.get("patternBlueprint") else None,
        "strongInputDigests": strong.get("inputDigests"),
        "slowOk": slow.get("ok"),
        "slowScore": slow.get("score"),
        "slowPenalties": slow.get("penalties"),
        "slowWeakCategories": slow.get("weakCategories"),
        "slowFailures": slow.get("failures"),
        "missingBlueprintOk": missing_blueprint.get("ok"),
        "missingBlueprintFailures": missing_blueprint.get("failures"),
    }


def test_hook_timing_scoring() -> dict[str, Any]:
    six_second_hook = STRONG_BRIEF.replace("0:00-0:05", "0:00-0:06")
    long_hook = STRONG_BRIEF.replace("0:00-0:05", "0:00-0:12")
    six_brief = check_video_brief.validate(six_second_hook, min_beats=8)
    long_brief = check_video_brief.validate(long_hook, min_beats=8)
    six_score = score_video_readiness.score_hook(six_second_hook.lower(), six_brief)
    long_score = score_video_readiness.score_hook(long_hook.lower(), long_brief)
    return {
        "passed": bool(
            six_brief["ok"]
            and long_brief["ok"]
            and six_score["score"] == 3
            and long_score["score"] < 3
        ),
        "sixSecondHookScore": six_score["score"],
        "sixSecondHookEvidence": six_score["evidence"],
        "longHookScore": long_score["score"],
        "longHookEvidence": long_score["evidence"],
    }


def test_package_report_projection(
    tmp: Path,
    visual_fixture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    visual_fixture = visual_fixture or build_visual_contract_fixture(tmp / "package-report-visual-contract")
    renderer_report = build_valid_renderer_evidence(visual_fixture)
    readiness = tmp / "readiness-score.json"
    write_json(readiness, build_complete_readiness_payload(visual_fixture, renderer_report))
    info = check_production_package.validate_readiness_report(
        readiness,
        failures,
        warnings,
        required=True,
        min_score=18,
        allow_weak=False,
    )
    low_score = tmp / "low-readiness-score.json"
    write_json(
        low_score,
        build_complete_readiness_payload(visual_fixture, renderer_report, score=12),
    )
    low_failures: list[str] = []
    low_info = check_production_package.validate_readiness_report(
        low_score,
        low_failures,
        [],
        required=True,
        min_score=18,
        allow_weak=False,
    )
    weak_score = tmp / "weak-readiness-score.json"
    write_json(
        weak_score,
        build_complete_readiness_payload(
            visual_fixture,
            renderer_report,
            weak_categories=["transitions"],
        ),
    )
    weak_failures: list[str] = []
    weak_info = check_production_package.validate_readiness_report(
        weak_score,
        weak_failures,
        [],
        required=True,
        min_score=18,
        allow_weak=False,
    )
    return {
        "passed": bool(
            info
            and info.get("ok") is True
            and info.get("score") == 22
            and info.get("readiness") == "ready"
            and info.get("minReadinessScoreRequired") == 18
            and info.get("weakCategories") == []
            and not failures
            and low_info
            and low_failures
            and weak_info
            and weak_failures
        ),
        "info": info,
        "lowScoreFailures": low_failures,
        "weakCategoryFailures": weak_failures,
        "failures": failures,
        "warnings": warnings,
    }


def test_audio_level_parser() -> dict[str, Any]:
    audible = check_video_artifact.parse_volumedetect(
        """
        [Parsed_volumedetect_0 @ 000001] mean_volume: -31.4 dB
        [Parsed_volumedetect_0 @ 000001] max_volume: -18.2 dB
        """
    )
    silent = check_video_artifact.parse_volumedetect(
        """
        [Parsed_volumedetect_0 @ 000001] mean_volume: -91.0 dB
        [Parsed_volumedetect_0 @ 000001] max_volume: -91.0 dB
        """
    )
    audible_ok = (
        audible.get("meanVolumeDb") is not None
        and audible["meanVolumeDb"] >= -55
        and audible.get("maxVolumeDb") is not None
        and audible["maxVolumeDb"] >= -45
    )
    silent_ok = (
        silent.get("meanVolumeDb") is not None
        and silent["meanVolumeDb"] >= -55
        and silent.get("maxVolumeDb") is not None
        and silent["maxVolumeDb"] >= -45
    )
    return {
        "passed": bool(audible_ok and not silent_ok),
        "audibleMeanVolumeDb": audible.get("meanVolumeDb"),
        "audibleMaxVolumeDb": audible.get("maxVolumeDb"),
        "silentMeanVolumeDb": silent.get("meanVolumeDb"),
        "silentMaxVolumeDb": silent.get("maxVolumeDb"),
        "silentPassesThreshold": silent_ok,
    }


def test_audio_report_contract(tmp: Path) -> dict[str, Any]:
    sine_report_path = tmp / "audio-sine.json"
    final_report_path = tmp / "audio-final.json"
    short_report_path = tmp / "audio-short.json"
    final_audio = tmp / "voiceover.wav"
    short_audio = tmp / "short-voiceover.wav"
    write_silent_wav(final_audio, seconds=2.0)
    write_silent_wav(short_audio, seconds=0.4)
    sine_report = render_concept_video.build_audio_report(
        make_args(
            audio="sine",
            audio_file=None,
            output=tmp / "sine.mp4",
            duration=2.0,
            final_audio_duration_tolerance=0.2,
        ),
        sine_report_path,
    )
    final_report = render_concept_video.build_audio_report(
        make_args(
            audio="sine",
            audio_file=final_audio,
            output=tmp / "final.mp4",
            duration=2.0,
            final_audio_duration_tolerance=0.2,
        ),
        final_report_path,
    )
    short_report = render_concept_video.build_audio_report(
        make_args(
            audio="sine",
            audio_file=short_audio,
            output=tmp / "short.mp4",
            duration=2.0,
            final_audio_duration_tolerance=0.2,
        ),
        short_report_path,
    )
    loaded_final, final_failures = check_video_artifact.load_json_report(final_report_path, "audio_report")
    binding_video = tmp / "binding-video.mp4"
    write_bytes(binding_video, 1_024)
    valid_binding_failures = check_video_artifact.validate_video_binding(
        {
            "video": str(binding_video),
            "videoSha256": sha256_path(binding_video),
        },
        "fixture_report",
        binding_video,
    )
    stale_binding_failures = check_video_artifact.validate_video_binding(
        {
            "video": str(tmp / "other-video.mp4"),
            "videoSha256": "0" * 64,
        },
        "fixture_report",
        binding_video,
    )
    return {
        "passed": bool(
            sine_report_path.exists()
            and final_report_path.exists()
            and short_report_path.exists()
            and sine_report["placeholderAudio"] is True
            and sine_report["finalAudioReady"] is False
            and final_report["mode"] == "file"
            and final_report["placeholderAudio"] is False
            and final_report["finalAudioReady"] is True
            and final_report["finalAudioDurationOk"] is True
            and final_report["sourceDurationSeconds"] >= 1.9
            and short_report["mode"] == "file"
            and short_report["finalAudioReady"] is False
            and short_report["finalAudioDurationOk"] is False
            and loaded_final
            and loaded_final.get("ok") is True
            and not final_failures
            and not valid_binding_failures
            and len(stale_binding_failures) == 2
        ),
        "sinePlaceholder": sine_report["placeholderAudio"],
        "sineFinalReady": sine_report["finalAudioReady"],
        "sineDurationOk": sine_report["finalAudioDurationOk"],
        "fileMode": final_report["mode"],
        "fileFinalReady": final_report["finalAudioReady"],
        "fileFinalDurationOk": final_report["finalAudioDurationOk"],
        "fileSourceDurationSeconds": final_report["sourceDurationSeconds"],
        "shortFinalReady": short_report["finalAudioReady"],
        "shortFinalDurationOk": short_report["finalAudioDurationOk"],
        "shortSourceDurationSeconds": short_report["sourceDurationSeconds"],
        "loadFailures": final_failures,
        "validBindingFailures": valid_binding_failures,
        "staleBindingFailures": stale_binding_failures,
    }


def test_voiceover_cue_extractor(tmp: Path) -> dict[str, Any]:
    brief_path = tmp / "voiceover-brief.md"
    brief_path.write_text(STRONG_BRIEF, encoding="utf-8", newline="\n")
    result = extract_voiceover_cues.build_result(
        make_args(
            brief=brief_path,
            min_cues=8,
            expect_duration=70,
            duration_tolerance=0.1,
            cue_time_tolerance=0.05,
            require_beat_match=True,
            allow_overlap=False,
        )
    )
    srt = extract_voiceover_cues.render_srt(result["cues"])
    csv_text = extract_voiceover_cues.render_csv(result["cues"])

    overlap_path = tmp / "overlap-voiceover-brief.md"
    overlap_path.write_text(
        STRONG_BRIEF.replace("- 0:05-0:12:", "- 0:04-0:12:", 1),
        encoding="utf-8",
        newline="\n",
    )
    overlap_result = extract_voiceover_cues.build_result(
        make_args(
            brief=overlap_path,
            min_cues=8,
            expect_duration=70,
            duration_tolerance=0.1,
            cue_time_tolerance=0.05,
            require_beat_match=True,
            allow_overlap=False,
        )
    )
    mismatch_path = tmp / "mismatched-voiceover-brief.md"
    mismatch_path.write_text(
        STRONG_BRIEF.replace("- 0:00-0:05:", "- 0:00-0:06:", 1),
        encoding="utf-8",
        newline="\n",
    )
    mismatch_result = extract_voiceover_cues.build_result(
        make_args(
            brief=mismatch_path,
            min_cues=8,
            expect_duration=70,
            duration_tolerance=0.1,
            cue_time_tolerance=0.05,
            require_beat_match=True,
            allow_overlap=False,
        )
    )
    return {
        "passed": bool(
            result["ok"]
            and result["cueCount"] == 8
            and result["beatCount"] == 8
            and result["beatMatchRequired"] is True
            and not result["beatCueMismatches"]
            and result["finalCueEndSeconds"] == 70.0
            and result["coveredDurationSeconds"] == 70.0
            and result["cues"][0]["text"].startswith("Your API did not crash")
            and "00:00:00,000 --> 00:00:05,000" in srt
            and "index,start,end,startSeconds,endSeconds,durationSeconds,wordCount,text" in csv_text
            and not overlap_result["ok"]
            and any("overlaps" in failure for failure in overlap_result["failures"])
            and not mismatch_result["ok"]
            and mismatch_result["beatCueMismatches"]
        ),
        "cueCount": result["cueCount"],
        "beatCount": result["beatCount"],
        "beatMatchRequired": result["beatMatchRequired"],
        "beatCueMismatches": result["beatCueMismatches"],
        "finalCueEndSeconds": result["finalCueEndSeconds"],
        "coveredDurationSeconds": result["coveredDurationSeconds"],
        "firstCueText": result["cues"][0]["text"] if result["cues"] else None,
        "srtStartsOk": "00:00:00,000 --> 00:00:05,000" in srt,
        "csvHeaderOk": "index,start,end,startSeconds,endSeconds,durationSeconds,wordCount,text" in csv_text,
        "overlapOk": overlap_result["ok"],
        "overlapFailures": overlap_result["failures"],
        "mismatchOk": mismatch_result["ok"],
        "mismatchFailures": mismatch_result["failures"],
        "mismatchBeatCueMismatches": mismatch_result["beatCueMismatches"],
        "failures": result["failures"],
        "warnings": result["warnings"],
    }


def create_contact_sheet(path: Path, *, blank: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (640, 360), (18, 22, 28))
    draw = ImageDraw.Draw(image)
    if not blank:
        palette = [
            (0, 190, 255),
            (255, 69, 91),
            (250, 204, 21),
            (34, 197, 94),
            (148, 163, 184),
            (99, 102, 241),
        ]
        for row in range(2):
            for col in range(3):
                x0 = 24 + col * 202
                y0 = 24 + row * 150
                color = palette[row * 3 + col]
                draw.rectangle((x0, y0, x0 + 170, y0 + 112), fill=(30, 35, 44), outline=color, width=4)
                draw.rectangle((x0 + 14, y0 + 18, x0 + 14 + (col + 1) * 32, y0 + 40), fill=color)
                draw.line((x0 + 18, y0 + 72, x0 + 145, y0 + 44 + row * 20), fill=color, width=3)
                draw.text((x0 + 18, y0 + 88), f"beat {row * 3 + col + 1}", fill=(240, 246, 255))
    image.save(path, quality=90)


def test_contact_sheet_quality(tmp: Path) -> dict[str, Any]:
    rich = tmp / "contact-rich.jpg"
    blank = tmp / "contact-blank.jpg"
    create_contact_sheet(rich, blank=False)
    create_contact_sheet(blank, blank=True)
    rich_result = check_video_artifact.validate_contact_sheet(
        rich,
        min_width=320,
        min_height=180,
        min_stddev=4.0,
        min_colors=32,
    )
    blank_result = check_video_artifact.validate_contact_sheet(
        blank,
        min_width=320,
        min_height=180,
        min_stddev=4.0,
        min_colors=32,
    )
    return {
        "passed": bool(rich_result["ok"] and not blank_result["ok"]),
        "richOk": rich_result["ok"],
        "richWidth": rich_result.get("width"),
        "richHeight": rich_result.get("height"),
        "richLuminanceStddev": rich_result.get("luminanceStddev"),
        "richColorCount": rich_result.get("colorCount"),
        "blankOk": blank_result["ok"],
        "blankFailures": blank_result["failures"],
        "blankLuminanceStddev": blank_result.get("luminanceStddev"),
        "blankColorCount": blank_result.get("colorCount"),
    }


def image_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_renderer_screenshot_quality() -> dict[str, Any]:
    rich = Image.new("RGB", (640, 360), (10, 14, 22))
    draw = ImageDraw.Draw(rich)
    palette = [
        (0, 190, 255),
        (255, 69, 91),
        (250, 204, 21),
        (34, 197, 94),
        (148, 163, 184),
        (99, 102, 241),
    ]
    for index, color in enumerate(palette):
        x = 32 + index * 92
        draw.rectangle((x, 40, x + 62, 270), fill=(24, 31, 44), outline=color, width=4)
        draw.ellipse((x + 12, 66 + index * 8, x + 50, 104 + index * 8), fill=color)
        draw.line((x + 16, 210, x + 52, 130), fill=color, width=3)
    draw.text((32, 306), "visible source-bound mechanism", fill=(242, 247, 255))

    blank = Image.new("RGB", (640, 360), (255, 255, 255))
    rich_result = check_renderer_contract.analyze_screenshot_bytes(
        image_bytes(rich),
        min_stddev=4.0,
        min_colors=32,
    )
    blank_result = check_renderer_contract.analyze_screenshot_bytes(
        image_bytes(blank),
        min_stddev=4.0,
        min_colors=32,
    )
    return {
        "passed": bool(rich_result["ok"] and not blank_result["ok"]),
        "richOk": rich_result["ok"],
        "richLuminanceStddev": rich_result.get("luminanceStddev"),
        "richColorCount": rich_result.get("colorCount"),
        "blankOk": blank_result["ok"],
        "blankFailures": blank_result["failures"],
        "blankLuminanceStddev": blank_result.get("luminanceStddev"),
        "blankColorCount": blank_result.get("colorCount"),
    }


def create_motion_frames(frame_dir: Path, *, moving: bool, frame_count: int = 24) -> None:
    frame_dir.mkdir(parents=True, exist_ok=True)
    for index in range(frame_count):
        image = Image.new("RGB", (320, 180), (6, 8, 12))
        draw = ImageDraw.Draw(image)
        palette = [
            (22, 31, 45),
            (44, 62, 83),
            (0, 190, 255),
            (255, 69, 91),
            (250, 204, 21),
            (34, 197, 94),
            (148, 163, 184),
            (99, 102, 241),
        ]
        for slot, color in enumerate(palette):
            draw.rectangle((18 + slot * 18, 18, 30 + slot * 18, 36), fill=color)
        x = 20 + (index * 9 if moving else 0)
        draw.rectangle((x, 60, x + 72, 120), fill=(0, 190, 255))
        draw.rectangle((18, 140, 302, 152), fill=(45, 52, 64))
        draw.rectangle((18, 140, 18 + index * 10 if moving else 90, 152), fill=(255, 69, 91))
        image.save(frame_dir / f"frame_{index:06d}.png")


def test_motion_report_detection(tmp: Path) -> dict[str, Any]:
    moving_dir = tmp / "moving-frames"
    static_dir = tmp / "static-frames"
    short_dir = tmp / "short-moving-frames"
    create_motion_frames(moving_dir, moving=True)
    create_motion_frames(static_dir, moving=False)
    create_motion_frames(short_dir, moving=True, frame_count=9)
    moving_report = render_concept_video.build_motion_report(
        moving_dir,
        frame_count=24,
        fps=10,
        duration=2.4,
        output=tmp / "moving-motion-report.json",
        video_path=tmp / "moving.mp4",
        sample_fps=10,
        scale_width=160,
    )
    static_report = render_concept_video.build_motion_report(
        static_dir,
        frame_count=24,
        fps=10,
        duration=2.4,
        output=tmp / "static-motion-report.json",
        video_path=tmp / "static.mp4",
        sample_fps=10,
        scale_width=160,
    )
    short_report = render_concept_video.build_motion_report(
        short_dir,
        frame_count=9,
        fps=1,
        duration=9,
        output=tmp / "short-moving-motion-report.json",
        video_path=tmp / "short-moving.mp4",
        sample_fps=1,
        scale_width=160,
    )
    moving_metrics = moving_report.get("metrics", {}) if moving_report else {}
    static_metrics = static_report.get("metrics", {}) if static_report else {}
    short_metrics = short_report.get("metrics", {}) if short_report else {}
    return {
        "passed": bool(
            moving_report
            and static_report
            and short_report
            and moving_report.get("ok")
            and not static_report.get("ok")
            and short_report.get("ok")
            and moving_metrics.get("subtleChangingPairs", 0) >= 12
            and static_metrics.get("subtleChangingPairs", 1) == 0
            and short_report.get("effectiveThresholds", {}).get("minSamples", 20) < 20
        ),
        "movingOk": moving_report.get("ok") if moving_report else None,
        "movingSubtleChangingPairs": moving_metrics.get("subtleChangingPairs"),
        "staticOk": static_report.get("ok") if static_report else None,
        "staticFailures": static_report.get("findings") if static_report else None,
        "staticSubtleChangingPairs": static_metrics.get("subtleChangingPairs"),
        "shortMovingOk": short_report.get("ok") if short_report else None,
        "shortMovingSampleCount": short_metrics.get("sampleCount"),
        "shortMovingEffectiveMinSamples": (
            short_report.get("effectiveThresholds", {}).get("minSamples") if short_report else None
        ),
    }


def test_fast_capture_math() -> dict[str, Any]:
    default_args = SimpleNamespace(fps=30, capture_fps=None)
    fast_args = SimpleNamespace(fps=30, capture_fps=12)
    default_capture_fps = render_concept_video.effective_capture_fps(default_args)
    fast_capture_fps = render_concept_video.effective_capture_fps(fast_args)
    default_frames = render_concept_video.capture_frame_count(70, default_capture_fps)
    fast_frames = render_concept_video.capture_frame_count(70, fast_capture_fps)
    short_frames = render_concept_video.capture_frame_count(12, fast_capture_fps)
    return {
        "passed": bool(
            default_capture_fps == 30
            and fast_capture_fps == 12
            and default_frames == 2100
            and fast_frames == 840
            and short_frames == 144
            and fast_frames < default_frames
        ),
        "defaultCaptureFps": default_capture_fps,
        "fastCaptureFps": fast_capture_fps,
        "defaultFrames70s": default_frames,
        "fastFrames70s": fast_frames,
        "fastFrames12s": short_frames,
    }


def test_runtime_preflight(tmp: Path) -> dict[str, Any]:
    def simulated_resolver(name: str) -> str | None:
        if name in {"uv", "ffmpeg", "ffprobe"}:
            return sys.executable
        return None

    positive = check_runtime_tools.build_result(
        check_runtime_tools.SKILL_DIR,
        require_render_tools=True,
        resolver=simulated_resolver,
    )
    negative = check_runtime_tools.build_result(
        tmp / "missing-skill",
        require_render_tools=True,
        require_node=True,
        resolver=lambda _name: None,
    )
    negative_failures = "\n".join(negative.get("failures", []))
    return {
        "passed": bool(
            positive.get("ok")
            and positive.get("checks", {}).get("requiredFiles", {}).get("ok")
            and positive.get("checks", {}).get("ffmpeg", {}).get("ok")
            and positive.get("checks", {}).get("ffprobe", {}).get("ok")
            and positive.get("requirements", {}).get("ffmpeg") is True
            and positive.get("requirements", {}).get("ffprobe") is True
            and not negative.get("ok")
            and "uv" in negative_failures
            and "ffmpeg" in negative_failures
            and "ffprobe" in negative_failures
            and "node" in negative_failures
            and negative.get("checks", {}).get("requiredFiles", {}).get("missing")
        ),
        "positiveOk": positive.get("ok"),
        "positiveRequiredFilesOk": positive.get("checks", {}).get("requiredFiles", {}).get("ok"),
        "positiveFfmpegOk": positive.get("checks", {}).get("ffmpeg", {}).get("ok"),
        "positiveFfprobeOk": positive.get("checks", {}).get("ffprobe", {}).get("ok"),
        "negativeOk": negative.get("ok"),
        "negativeFailures": negative.get("failures"),
        "negativeMissingRequiredFiles": negative.get("checks", {}).get("requiredFiles", {}).get("missing"),
    }


def test_package_source_contracts(tmp: Path) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    production_notes = tmp / "production-notes.md"
    package_manifest = tmp / "package-manifest.json"
    production_notes.write_text(
        """# What Is A Cache? Production Notes

## Design Note

Concept claim: Explain cache as a visible reuse mechanism.
Chosen visual metaphor: Cache as state movement.

## Production Files

- Final MP4: artifacts/videos/cache.mp4
- Contact sheet: artifacts/reviews/contact-sheet.jpg
- Motion report: artifacts/reviews/motion-report.json
- Style fidelity score: artifacts/reviews/style-fidelity.json

## Render State Contract

Required states include `activeBeat` and `visibleMechanismCount`.

## Validation Commands

Command working directory: project root, the folder that contains `source/`, `src/`, and `artifacts/`.

```powershell
uv run --script skills/awsome-videos/scripts/check_video_brief.py source/brief.md --require-voiceover --json
uv run --script skills/awsome-videos/scripts/render_concept_video.py src/index.html artifacts/videos/cache.mp4 --brief source/brief.md --require-all-brief-beats --duration 70 --fps 30 --capture-fps 12 --force --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --render-state-report artifacts/reviews/render-state.json --audio-report artifacts/reviews/audio-report.json --json
uv run --script skills/awsome-videos/scripts/check_video_artifact.py artifacts/videos/cache.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --require-audio --audio-report artifacts/reviews/audio-report.json --require-audio-report --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --json
uv run --script skills/awsome-videos/scripts/score_video_readiness.py --brief source/brief.md --video artifacts/videos/cache.mp4 --renderer-report artifacts/reviews/render-state.json --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --contact-sheet artifacts/reviews/contact-sheet.jpg --require-voiceover --output artifacts/reviews/readiness-score.json --json
uv run --script skills/awsome-videos/scripts/score_style_fidelity.py --brief source/brief.md --pattern-blueprint source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --output artifacts/reviews/style-fidelity.json --json
uv run --script skills/awsome-videos/scripts/check_production_package.py --brief source/brief.md --video artifacts/videos/cache.mp4 --design-note source/design-note.md --production-notes source/production-notes.md --package-manifest source/package-manifest.json --renderer src/index.html --renderer-report artifacts/reviews/render-state.json --readiness-report artifacts/reviews/readiness-score.json --style-fidelity-report artifacts/reviews/style-fidelity.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --min-readiness-score 18 --min-style-fidelity-score 12 --require-audio --require-audio-report --require-voiceover --require-design-note --require-production-notes --require-package-manifest --require-renderer --require-renderer-report --require-renderer-beat-coverage --require-readiness-report --require-style-fidelity-report --require-contact-sheet --require-motion-report --json
```

## Visual review

- Contact sheet inspected: pending.
- Asset quality check: pending ready-asset and producer-report review.
- Composition check: pending per-scene hierarchy and armature review.
- Renderer asset-binding check: pending visible asset, composition, and object ID coverage.
- Legibility check: pending contact-sheet review.
- Beat coverage check: pending renderer coverage report.
- Visual mechanism check: pending mechanism review.
- Pacing/transition check: pending motion report.
- Source-binding check: pending source plan review.
- Audio sync check: pending audio report.
- Known caveats: pending final review.
""",
        encoding="utf-8",
    )
    write_json(
        package_manifest,
        {
            "paths": {
                "brief": "source/brief.md",
                "designNote": "source/design-note.md",
                "productionNotes": "source/production-notes.md",
                "renderer": "src/index.html",
                "storyboard": "src/storyboard.md",
                "video": "artifacts/videos/cache.mp4",
                "contactSheet": "artifacts/reviews/contact-sheet.jpg",
                "rendererValidation": "artifacts/reviews/render-state.json",
                "qualityReport": "artifacts/reviews/quality-report.json",
                "motionReport": "artifacts/reviews/motion-report.json",
                "captureManifest": "artifacts/reviews/capture-manifest.json",
                "audioReport": "artifacts/reviews/audio-report.json",
                "readinessScore": "artifacts/reviews/readiness-score.json",
                "styleFidelity": "artifacts/reviews/style-fidelity.json",
                "packageValidation": "artifacts/reviews/package-validation.json",
            },
            "commands": {
                "briefValidation": "uv run --script skills/awsome-videos/scripts/check_video_brief.py source/brief.md --require-voiceover --json",
                "rendererValidation": "uv run --script skills/awsome-videos/scripts/check_renderer_contract.py src/index.html --brief source/brief.md --duration 70 --require-all-brief-beats --output artifacts/reviews/render-state.json --json",
                "renderVideo": "uv run --script skills/awsome-videos/scripts/render_concept_video.py src/index.html artifacts/videos/cache.mp4 --brief source/brief.md --require-all-brief-beats --duration 70 --fps 30 --capture-fps 12 --force --audio-report artifacts/reviews/audio-report.json --render-state-report artifacts/reviews/render-state.json --contact-sheet artifacts/reviews/contact-sheet.jpg --motion-report artifacts/reviews/motion-report.json --json",
                "videoValidation": "uv run --script skills/awsome-videos/scripts/check_video_artifact.py artifacts/videos/cache.mp4 --audio-report artifacts/reviews/audio-report.json --require-audio-report --expect-duration 70 --duration-tolerance 1 --json",
                "scoreReadiness": "uv run --script skills/awsome-videos/scripts/score_video_readiness.py --brief source/brief.md --video artifacts/videos/cache.mp4 --renderer-report artifacts/reviews/render-state.json --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --contact-sheet artifacts/reviews/contact-sheet.jpg --require-voiceover --output artifacts/reviews/readiness-score.json --json",
                "styleFidelity": "uv run --script skills/awsome-videos/scripts/score_style_fidelity.py --brief source/brief.md --pattern-blueprint source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --output artifacts/reviews/style-fidelity.json --json",
                "packageValidation": "uv run --script skills/awsome-videos/scripts/check_production_package.py --brief source/brief.md --video artifacts/videos/cache.mp4 --design-note source/design-note.md --production-notes source/production-notes.md --package-manifest source/package-manifest.json --motion-report artifacts/reviews/motion-report.json --audio-report artifacts/reviews/audio-report.json --style-fidelity-report artifacts/reviews/style-fidelity.json --require-audio-report --expect-duration 70 --duration-tolerance 1 --min-readiness-score 18 --min-style-fidelity-score 12 --require-voiceover --require-production-notes --require-package-manifest --require-style-fidelity-report --require-renderer-beat-coverage --require-motion-report --json",
            },
        },
    )
    style_report = tmp / "artifacts" / "reviews" / "style-fidelity.json"
    style_input_digests = {
        "briefSha256": sha256_path(production_notes),
        "patternBlueprintSha256": sha256_path(package_manifest),
        "corpusSummarySha256": sha256_path(score_style_fidelity.DEFAULT_SUMMARY),
    }
    write_json(
        style_report,
        {
            "ok": True,
            "score": 15,
            "maxScore": 16,
            "minScore": 12,
            "penalties": [],
            "weakCategories": ["source_proof"],
            "inputDigests": style_input_digests,
        },
    )
    bad_style_report = tmp / "artifacts" / "reviews" / "bad-style-fidelity.json"
    write_json(
        bad_style_report,
        {
            "ok": False,
            "score": 8,
            "maxScore": 16,
            "minScore": 12,
            "penalties": ["slow generic presentation vocabulary"],
            "weakCategories": ["visual_atoms"],
        },
    )
    notes_info = check_production_package.validate_production_notes(
        production_notes,
        failures,
        warnings,
        required=True,
        expected_duration=70,
    )
    manifest_info = check_production_package.validate_package_manifest(
        package_manifest,
        failures,
        warnings,
        required=True,
    )
    mismatched_artifact_failures: list[str] = []
    mismatched_artifact_info = check_production_package.validate_package_manifest(
        package_manifest,
        mismatched_artifact_failures,
        [],
        required=True,
        expected_artifacts={"video": tmp / "artifacts" / "videos" / "different.mp4"},
    )
    missing_source_notes_failures: list[str] = []
    missing_source_notes_warnings: list[str] = []
    missing_source_notes_info = check_production_package.validate_production_notes(
        production_notes,
        missing_source_notes_failures,
        missing_source_notes_warnings,
        required=True,
        expected_duration=70,
        require_source_links=True,
    )
    source_notes = tmp / "source-link-production-notes.md"
    source_notes_text = production_notes.read_text(encoding="utf-8")
    source_notes_text = source_notes_text.replace(
        "check_video_brief.py source/brief.md --require-voiceover --json",
        "check_video_brief.py source/brief.md --require-voiceover --require-source-links --json",
    )
    source_notes_text = source_notes_text.replace(
        "score_video_readiness.py --brief source/brief.md",
        "score_video_readiness.py --require-source-links --brief source/brief.md",
    )
    source_notes_text = source_notes_text.replace(
        "score_style_fidelity.py --brief source/brief.md",
        "score_style_fidelity.py --require-source-links --brief source/brief.md",
    )
    source_notes_text = source_notes_text.replace(
        "check_production_package.py --brief source/brief.md",
        "check_production_package.py --require-source-links --brief source/brief.md",
    )
    source_notes.write_text(source_notes_text, encoding="utf-8", newline="\n")
    source_notes_failures: list[str] = []
    source_notes_warnings: list[str] = []
    source_notes_info = check_production_package.validate_production_notes(
        source_notes,
        source_notes_failures,
        source_notes_warnings,
        required=True,
        expected_duration=70,
        require_source_links=True,
    )
    missing_source_manifest_failures: list[str] = []
    missing_source_manifest_warnings: list[str] = []
    missing_source_manifest_info = check_production_package.validate_package_manifest(
        package_manifest,
        missing_source_manifest_failures,
        missing_source_manifest_warnings,
        required=True,
        require_source_links=True,
    )
    source_manifest = tmp / "source-link-package-manifest.json"
    source_manifest_data = json.loads(package_manifest.read_text(encoding="utf-8"))
    for command_name in ["briefValidation", "scoreReadiness", "styleFidelity", "packageValidation"]:
        source_manifest_data["commands"][command_name] += " --require-source-links"
    write_json(source_manifest, source_manifest_data)
    source_manifest_failures: list[str] = []
    source_manifest_warnings: list[str] = []
    source_manifest_info = check_production_package.validate_package_manifest(
        source_manifest,
        source_manifest_failures,
        source_manifest_warnings,
        required=True,
        require_source_links=True,
    )
    style_report_failures: list[str] = []
    style_report_warnings: list[str] = []
    style_report_info = check_production_package.validate_style_fidelity_report(
        style_report,
        style_report_failures,
        style_report_warnings,
        required=True,
        min_score=12,
        expected_input_digests=style_input_digests,
    )
    stale_style_report = tmp / "artifacts" / "reviews" / "stale-style-fidelity.json"
    stale_style_payload = json.loads(style_report.read_text(encoding="utf-8"))
    stale_style_payload["inputDigests"]["briefSha256"] = "0" * 64
    write_json(stale_style_report, stale_style_payload)
    stale_style_failures: list[str] = []
    stale_style_info = check_production_package.validate_style_fidelity_report(
        stale_style_report,
        stale_style_failures,
        [],
        required=True,
        min_score=12,
        expected_input_digests=style_input_digests,
    )
    bad_style_report_failures: list[str] = []
    bad_style_report_warnings: list[str] = []
    bad_style_report_info = check_production_package.validate_style_fidelity_report(
        bad_style_report,
        bad_style_report_failures,
        bad_style_report_warnings,
        required=True,
        min_score=12,
    )
    style_manifest = tmp / "source" / "style-package-manifest.json"
    write_json(style_manifest, json.loads(package_manifest.read_text(encoding="utf-8")))
    style_manifest_failures: list[str] = []
    style_manifest_warnings: list[str] = []
    style_manifest_info = check_production_package.validate_package_manifest(
        style_manifest,
        style_manifest_failures,
        style_manifest_warnings,
        required=True,
        require_style_fidelity_report=True,
    )
    missing_style_manifest = tmp / "source" / "missing-style-package-manifest.json"
    missing_style_manifest_data = json.loads(package_manifest.read_text(encoding="utf-8"))
    missing_style_manifest_data["paths"]["styleFidelity"] = "artifacts/reviews/missing-style-fidelity.json"
    write_json(missing_style_manifest, missing_style_manifest_data)
    missing_style_manifest_failures: list[str] = []
    missing_style_manifest_warnings: list[str] = []
    missing_style_manifest_info = check_production_package.validate_package_manifest(
        missing_style_manifest,
        missing_style_manifest_failures,
        missing_style_manifest_warnings,
        required=True,
        require_style_fidelity_report=True,
    )
    stale_review_failures: list[str] = []
    stale_review_warnings: list[str] = []
    stale_review_notes_info = check_production_package.validate_production_notes(
        production_notes,
        stale_review_failures,
        stale_review_warnings,
        required=True,
        expected_duration=70,
        require_final_review_notes=True,
    )
    clean_review_notes = tmp / "clean-review-production-notes.md"
    clean_review_text = production_notes.read_text(encoding="utf-8").replace(
        """- Contact sheet inspected: pending.
- Asset quality check: pending ready-asset and producer-report review.
- Composition check: pending per-scene hierarchy and armature review.
- Renderer asset-binding check: pending visible asset, composition, and object ID coverage.
- Legibility check: pending contact-sheet review.
- Beat coverage check: pending renderer coverage report.
- Visual mechanism check: pending mechanism review.
- Pacing/transition check: pending motion report.
- Source-binding check: pending source plan review.
- Audio sync check: pending audio report.
- Known caveats: pending final review.""",
        """- Contact sheet inspected: automated nonblank contact-sheet validation passed.
- Asset quality check: eight hash-bound generated assets passed their producer reports and technical inspections.
- Composition check: eight scenes use four distinct composition families and four armatures with dominant focal proofs.
- Renderer asset-binding check: visible asset, composition, and object IDs match every active scene contract.
- Legibility check: text labels and major shapes are readable in sampled frames.
- Beat coverage check: renderer report covers every brief beat.
- Visual mechanism check: cache hit, cache miss, and reuse path explain the claim.
- Pacing/transition check: motion report shows visible changes between sampled frames.
- Source-binding check: visuals map to the brief source plan and generated mechanism diagram.
- Audio sync check: audio report covers the expected runtime.
- Known caveats: caveats are closed for this validation fixture.""",
    )
    clean_review_text = clean_review_text.replace(
        "--require-readiness-report --require-style-fidelity-report --require-contact-sheet",
        "--require-readiness-report --require-style-fidelity-report --require-final-review-notes --require-contact-sheet",
    )
    clean_review_notes.write_text(clean_review_text, encoding="utf-8", newline="\n")
    thin_review_notes = tmp / "thin-review-production-notes.md"
    thin_review_text = clean_review_text
    for label in [
        "Asset quality check",
        "Composition check",
        "Renderer asset-binding check",
        "Legibility check",
        "Beat coverage check",
        "Visual mechanism check",
        "Pacing/transition check",
        "Source-binding check",
        "Audio sync check",
        "Known caveats",
    ]:
        thin_review_text = re.sub(rf"(- {re.escape(label)}: ).+", rf"\1ok", thin_review_text)
    thin_review_notes.write_text(thin_review_text, encoding="utf-8", newline="\n")
    clean_review_manifest = tmp / "clean-review-package-manifest.json"
    clean_review_manifest_data = json.loads(package_manifest.read_text(encoding="utf-8"))
    clean_review_manifest_data["commands"]["packageValidation"] = clean_review_manifest_data["commands"][
        "packageValidation"
    ].replace(
        "--require-production-notes --require-package-manifest --require-style-fidelity-report --require-renderer-beat-coverage --require-motion-report",
        "--require-production-notes --require-package-manifest --require-style-fidelity-report --require-renderer-beat-coverage --require-final-review-notes --require-motion-report",
    )
    write_json(clean_review_manifest, clean_review_manifest_data)
    clean_review_failures: list[str] = []
    clean_review_warnings: list[str] = []
    clean_review_notes_info = check_production_package.validate_production_notes(
        clean_review_notes,
        clean_review_failures,
        clean_review_warnings,
        required=True,
        expected_duration=70,
        require_final_review_notes=True,
    )
    thin_review_failures: list[str] = []
    thin_review_warnings: list[str] = []
    thin_review_notes_info = check_production_package.validate_production_notes(
        thin_review_notes,
        thin_review_failures,
        thin_review_warnings,
        required=True,
        expected_duration=70,
        require_final_review_notes=True,
    )
    clean_review_manifest_info = check_production_package.validate_package_manifest(
        clean_review_manifest,
        clean_review_failures,
        clean_review_warnings,
        required=True,
        require_final_review_notes=True,
    )
    final_audio = tmp / "artifacts" / "audio" / "final-narration.wav"
    write_bytes(final_audio, 16)
    final_notes = tmp / "final-production-notes.md"
    final_notes_text = production_notes.read_text(encoding="utf-8")
    final_notes_text = final_notes_text.replace(
        "- Motion report: artifacts/reviews/motion-report.json",
        "- Motion report: artifacts/reviews/motion-report.json\n- Final audio source: artifacts/audio/final-narration.wav",
    )
    final_notes_text = final_notes_text.replace(
        "--audio-report artifacts/reviews/audio-report.json --json",
        "--audio-report artifacts/reviews/audio-report.json --audio-file artifacts/audio/final-narration.wav --json",
        1,
    )
    final_notes_text = final_notes_text.replace(
        "--capture-manifest artifacts/reviews/capture-manifest.json --json",
        "--capture-manifest artifacts/reviews/capture-manifest.json --require-final-audio --json",
        1,
    )
    final_notes_text = final_notes_text.replace(
        "--require-voiceover --output artifacts/reviews/readiness-score.json",
        "--require-voiceover --require-final-audio --output artifacts/reviews/readiness-score.json",
    )
    final_notes_text = final_notes_text.replace(
        "--require-audio --require-audio-report --require-voiceover",
        "--require-audio --require-audio-report --require-final-audio --require-voiceover",
    )
    final_notes.write_text(final_notes_text, encoding="utf-8", newline="\n")
    final_manifest = tmp / "source" / "package-manifest.json"
    final_manifest_data = json.loads(package_manifest.read_text(encoding="utf-8"))
    final_manifest_data["paths"]["finalAudio"] = "artifacts/audio/final-narration.wav"
    final_commands = final_manifest_data["commands"]
    final_commands["renderVideo"] = final_commands["renderVideo"].replace(
        " --json",
        " --audio-file artifacts/audio/final-narration.wav --json",
        1,
    )
    final_commands["videoValidation"] = final_commands["videoValidation"].replace(
        "--duration-tolerance 1 --json",
        "--duration-tolerance 1 --require-final-audio --json",
    )
    final_commands["scoreReadiness"] = final_commands["scoreReadiness"].replace(
        "--require-voiceover --output artifacts/reviews/readiness-score.json",
        "--require-voiceover --require-final-audio --output artifacts/reviews/readiness-score.json",
    )
    final_commands["packageValidation"] = final_commands["packageValidation"].replace(
        "--require-audio-report --expect-duration 70",
        "--require-audio-report --require-final-audio --expect-duration 70",
    )
    write_json(final_manifest, final_manifest_data)
    final_failures: list[str] = []
    final_warnings: list[str] = []
    final_notes_info = check_production_package.validate_production_notes(
        final_notes,
        final_failures,
        final_warnings,
        required=True,
        expected_duration=70,
        require_final_audio=True,
    )
    final_manifest_info = check_production_package.validate_package_manifest(
        final_manifest,
        final_failures,
        final_warnings,
        required=True,
        require_final_audio=True,
    )
    missing_final_failures: list[str] = []
    missing_final_warnings: list[str] = []
    missing_final_notes_info = check_production_package.validate_production_notes(
        production_notes,
        missing_final_failures,
        missing_final_warnings,
        required=True,
        expected_duration=70,
        require_final_audio=True,
    )
    missing_final_manifest_info = check_production_package.validate_package_manifest(
        package_manifest,
        missing_final_failures,
        missing_final_warnings,
        required=True,
        require_final_audio=True,
    )
    bad_notes = tmp / "bad-production-notes.md"
    bad_notes.write_text(
        """# Bad Production Notes

Concept claim: Placeholder.
Chosen visual metaphor: Placeholder.
Production files: final MP4 and contact sheet.
Render state contract: activeBeat and visibleMechanismCount.
Validation commands:

```powershell
uv run --script {{SKILL_PATH}}/scripts/check_video_brief.py source/brief.md --json
uv run --script .agents/skills/awsome-videos/scripts/check_production_package.py --brief source/brief.md --video artifacts/videos/cache.mp4 --json
```

Visual review:
- Contact sheet inspected: no.
""",
        encoding="utf-8",
    )
    bad_failures: list[str] = []
    bad_warnings: list[str] = []
    bad_notes_info = check_production_package.validate_production_notes(
        bad_notes,
        bad_failures,
        bad_warnings,
        required=True,
        expected_duration=70,
    )
    command_contract = notes_info.get("commandContract") if notes_info else {}
    final_command_contract = final_notes_info.get("commandContract") if final_notes_info else {}
    missing_final_contract = missing_final_notes_info.get("commandContract") if missing_final_notes_info else {}
    bad_contract = bad_notes_info.get("commandContract") if bad_notes_info else {}
    return {
        "passed": bool(
            notes_info
            and manifest_info
            and not failures
            and not notes_info.get("missing")
            and command_contract.get("ok")
            and command_contract.get("commandCount") == 6
            and not manifest_info.get("missingPaths")
            and not manifest_info.get("missingCommands")
            and not manifest_info.get("missingPackageCommandTerms")
            and not manifest_info.get("missingReadinessCommandTerms")
            and not manifest_info.get("missingStyleCommandTerms")
            and mismatched_artifact_info
            and any(
                "paths.video does not match the CLI artifact" in item
                for item in mismatched_artifact_failures
            )
            and missing_source_notes_info
            and missing_source_notes_failures
            and missing_source_notes_info.get("commandContract", {}).get("missingSourceLinkCommandTerms")
            and source_notes_info
            and not source_notes_failures
            and not source_notes_info.get("commandContract", {}).get("missingSourceLinkCommandTerms")
            and missing_source_manifest_info
            and missing_source_manifest_failures
            and missing_source_manifest_info.get("missingSourceLinkCommandTerms")
            and source_manifest_info
            and not source_manifest_failures
            and not source_manifest_info.get("missingSourceLinkCommandTerms")
            and style_report_info
            and not style_report_failures
            and style_report_info.get("score") == 15
            and stale_style_info
            and any("inputDigests are stale" in item for item in stale_style_failures)
            and bad_style_report_info
            and bad_style_report_failures
            and style_manifest_info
            and not style_manifest_failures
            and style_manifest_info.get("styleFidelityExists") is True
            and missing_style_manifest_info
            and missing_style_manifest_failures
            and missing_style_manifest_info.get("styleFidelityExists") is False
            and stale_review_notes_info
            and stale_review_failures
            and stale_review_notes_info.get("finalReview", {}).get("staleLines")
            and clean_review_notes_info
            and clean_review_manifest_info
            and not clean_review_failures
            and clean_review_notes_info.get("finalReview", {}).get("ok")
            and not clean_review_notes_info.get("finalReview", {}).get("thinStructuredChecks")
            and thin_review_notes_info
            and thin_review_failures
            and thin_review_notes_info.get("finalReview", {}).get("thinStructuredChecks")
            and not clean_review_manifest_info.get("missingFinalReviewCommandTerms")
            and final_notes_info
            and final_manifest_info
            and not final_failures
            and final_command_contract.get("ok")
            and final_manifest_info.get("finalAudioExists") is True
            and final_manifest_info.get("finalAudioPath") == "artifacts/audio/final-narration.wav"
            and not final_manifest_info.get("missingFinalAudioCommandTerms")
            and missing_final_notes_info
            and missing_final_manifest_info
            and not missing_final_contract.get("ok")
            and missing_final_contract.get("missingFinalAudioCommandTerms")
            and "finalAudio" in missing_final_manifest_info.get("missingPaths", [])
            and missing_final_manifest_info.get("missingFinalAudioCommandTerms")
            and bad_notes_info
            and not bad_contract.get("ok")
            and bad_contract.get("unresolvedPlaceholders")
            and bad_contract.get("forbiddenPaths")
        ),
        "notesMissing": notes_info.get("missing") if notes_info else None,
        "notesCommandContractOk": command_contract.get("ok") if command_contract else None,
        "notesCommandCount": command_contract.get("commandCount") if command_contract else None,
        "badNotesOk": bad_contract.get("ok") if bad_contract else None,
        "badNotesFailures": bad_contract.get("failures") if bad_contract else None,
        "manifestMissingPaths": manifest_info.get("missingPaths") if manifest_info else None,
        "mismatchedArtifactInfo": mismatched_artifact_info,
        "mismatchedArtifactFailures": mismatched_artifact_failures,
        "manifestMissingCommands": manifest_info.get("missingCommands") if manifest_info else None,
        "manifestMissingPackageCommandTerms": manifest_info.get("missingPackageCommandTerms") if manifest_info else None,
        "manifestMissingReadinessCommandTerms": manifest_info.get("missingReadinessCommandTerms") if manifest_info else None,
        "manifestMissingStyleCommandTerms": manifest_info.get("missingStyleCommandTerms") if manifest_info else None,
        "missingSourceNotesTerms": (
            missing_source_notes_info.get("commandContract", {}).get("missingSourceLinkCommandTerms")
            if missing_source_notes_info
            else None
        ),
        "sourceNotesTermsOk": (
            not source_notes_info.get("commandContract", {}).get("missingSourceLinkCommandTerms")
            if source_notes_info
            else None
        ),
        "missingSourceManifestTerms": (
            missing_source_manifest_info.get("missingSourceLinkCommandTerms")
            if missing_source_manifest_info
            else None
        ),
        "sourceManifestTermsOk": (
            not source_manifest_info.get("missingSourceLinkCommandTerms") if source_manifest_info else None
        ),
        "styleReportOk": style_report_info.get("ok") if style_report_info else None,
        "styleReportScore": style_report_info.get("score") if style_report_info else None,
        "styleReportFailures": style_report_failures,
        "staleStyleFailures": stale_style_failures,
        "badStyleReportOk": bad_style_report_info.get("ok") if bad_style_report_info else None,
        "badStyleReportFailures": bad_style_report_failures,
        "styleManifestOk": bool(style_manifest_info and not style_manifest_failures),
        "styleManifestPath": style_manifest_info.get("styleFidelityPath") if style_manifest_info else None,
        "styleManifestFileExists": style_manifest_info.get("styleFidelityExists") if style_manifest_info else None,
        "missingStyleManifestFailures": missing_style_manifest_failures,
        "staleFinalReviewOk": (
            stale_review_notes_info.get("finalReview", {}).get("ok") if stale_review_notes_info else None
        ),
        "staleFinalReviewLines": (
            stale_review_notes_info.get("finalReview", {}).get("staleLines") if stale_review_notes_info else None
        ),
        "staleFinalReviewMissingStructuredChecks": (
            stale_review_notes_info.get("finalReview", {}).get("missingStructuredChecks")
            if stale_review_notes_info
            else None
        ),
        "cleanFinalReviewOk": (
            clean_review_notes_info.get("finalReview", {}).get("ok") if clean_review_notes_info else None
        ),
        "cleanFinalReviewMissingStructuredChecks": (
            clean_review_notes_info.get("finalReview", {}).get("missingStructuredChecks")
            if clean_review_notes_info
            else None
        ),
        "cleanFinalReviewThinStructuredChecks": (
            clean_review_notes_info.get("finalReview", {}).get("thinStructuredChecks")
            if clean_review_notes_info
            else None
        ),
        "thinFinalReviewThinStructuredChecks": (
            thin_review_notes_info.get("finalReview", {}).get("thinStructuredChecks")
            if thin_review_notes_info
            else None
        ),
        "thinReviewFailures": thin_review_failures,
        "cleanFinalReviewManifestMissingTerms": (
            clean_review_manifest_info.get("missingFinalReviewCommandTerms") if clean_review_manifest_info else None
        ),
        "staleReviewFailures": stale_review_failures,
        "cleanReviewFailures": clean_review_failures,
        "finalAudioNotesOk": final_command_contract.get("ok") if final_command_contract else None,
        "finalAudioManifestOk": bool(final_manifest_info and not final_failures),
        "finalAudioManifestPath": final_manifest_info.get("finalAudioPath") if final_manifest_info else None,
        "finalAudioFileExists": final_manifest_info.get("finalAudioExists") if final_manifest_info else None,
        "finalAudioManifestMissingTerms": (
            final_manifest_info.get("missingFinalAudioCommandTerms") if final_manifest_info else None
        ),
        "missingFinalAudioNotesOk": missing_final_contract.get("ok") if missing_final_contract else None,
        "missingFinalAudioNoteTerms": (
            missing_final_contract.get("missingFinalAudioCommandTerms") if missing_final_contract else None
        ),
        "missingFinalAudioManifestPaths": (
            missing_final_manifest_info.get("missingPaths") if missing_final_manifest_info else None
        ),
        "missingFinalAudioManifestTerms": (
            missing_final_manifest_info.get("missingFinalAudioCommandTerms") if missing_final_manifest_info else None
        ),
        "finalFailures": final_failures,
        "missingFinalFailures": missing_final_failures,
        "failures": failures,
        "warnings": warnings,
    }


def test_finalize_production_notes(tmp: Path, visual_fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    project = tmp / "finalize-notes"
    scaffold_production_package.scaffold(
        make_args(
            project_dir=project,
            title="What Is RAG?",
            promise="Explain retrieval augmented generation as grounded search plus generation.",
            audience="Developers validating a handoff.",
            format="compressed explainer",
            runtime="0:12",
            project_id="rag",
            skill_path="skills/awsome-videos",
            force=True,
            json=True,
        )
    )
    visual_fixture = visual_fixture or build_visual_contract_fixture(tmp / "finalize-visual-contract")
    notes = project / "source" / "production-notes.md"
    render_state = project / "artifacts" / "reviews" / "render-state.json"
    readiness = project / "artifacts" / "reviews" / "readiness-score.json"
    quality = project / "artifacts" / "reviews" / "quality-report.json"
    motion = project / "artifacts" / "reviews" / "motion-report.json"
    audio = project / "artifacts" / "reviews" / "audio-report.json"
    visual_review = visual_fixture["visualReviewPath"]
    visual_contract = visual_fixture["visualContractReportPath"]
    contact_sheet = visual_fixture["contactSheet"]
    scaffold_asset_manifest = json.loads(visual_fixture["assetManifestPath"].read_text(encoding="utf-8"))
    scaffold_composition_plan = json.loads(visual_fixture["compositionPlanPath"].read_text(encoding="utf-8"))
    renderer_asset_ids = [str(item["id"]) for item in scaffold_asset_manifest.get("assets", [])]
    renderer_composition_ids = [str(item["id"]) for item in scaffold_composition_plan.get("scenes", [])]
    renderer_payload = {
            "ok": True,
            "failures": [],
            "sampleCount": 8,
            "states": [
                {
                    "activeBeat": index,
                    "visualPattern": "grounded retrieval loop",
                    "visibleMechanismCount": 2,
                    "outputVisible": index == 8,
                    "finalCallbackVisible": index == 8,
                }
                for index in range(1, 9)
            ],
            "uniqueBeats": list(range(1, 9)),
            "briefBeatCoverageOk": True,
            "missingBriefBeats": [],
            "visualAssetCoverageOk": True,
            "assetBindingCoverageOk": True,
            "compositionCoverageOk": True,
            "expectedAssetIds": renderer_asset_ids,
            "observedAssetIds": renderer_asset_ids,
            "missingAssetIds": [],
            "expectedCompositionIds": renderer_composition_ids,
            "observedCompositionIds": renderer_composition_ids,
            "missingCompositionIds": [],
            "missingCompositionObjectIds": [],
            "rendererSha256": sha256_path(visual_fixture["project"] / "src" / "index.html"),
            "assetManifestSha256": visual_fixture["report"]["inputDigests"]["assetManifestSha256"],
            "compositionPlanSha256": visual_fixture["report"]["inputDigests"]["compositionPlanSha256"],
    }
    write_json(render_state, renderer_payload)
    readiness_payload = build_complete_readiness_payload(
        visual_fixture,
        renderer_payload,
    )
    readiness_payload["inputDigests"] = {
        "rendererReportSha256": sha256_path(render_state),
        "visualContractReportSha256": sha256_path(visual_contract),
        "contactSheetSha256": sha256_path(contact_sheet),
    }
    write_json(readiness, readiness_payload)
    write_json(quality, {"ok": True, "sampleCount": 8, "colorCount": 128})
    write_json(motion, {"ok": True, "changingPairs": 7, "strongChangingPairs": 7})
    write_json(audio, {"ok": True, "durationSeconds": 12, "placeholderAudio": True, "finalAudioReady": False})

    result = finalize_production_notes.finalize(
        make_args(
            production_notes=notes,
            renderer_report=render_state,
            readiness_report=readiness,
            contact_sheet=contact_sheet,
            quality_report=quality,
            motion_report=motion,
            audio_report=audio,
            visual_review=visual_review,
            visual_contract_report=visual_contract,
            video_validation=None,
            output=None,
            json=True,
        )
    )
    finalized = notes.read_text(encoding="utf-8")
    finalized_review = check_production_package.extract_markdown_section(finalized, "Visual Review")
    validation_failures: list[str] = []
    validation_warnings: list[str] = []
    notes_info = check_production_package.validate_production_notes(
        notes,
        validation_failures,
        validation_warnings,
        required=True,
        expected_duration=12,
        require_final_review_notes=True,
        require_pattern_blueprint=True,
    )
    final_review = notes_info.get("finalReview", {}) if notes_info else {}
    passed = bool(
        result.get("ok")
        and notes_info
        and final_review.get("ok")
        and not validation_failures
        and "pending" not in finalized_review.lower()
        and "## Visual Review" in finalized
    )
    return {
        "passed": passed,
        "resultOk": result.get("ok"),
        "finalReviewOk": final_review.get("ok"),
        "staleLines": final_review.get("staleLines"),
        "missingStructuredChecks": final_review.get("missingStructuredChecks"),
        "thinStructuredChecks": final_review.get("thinStructuredChecks"),
        "validationFailures": validation_failures,
        "visualReviewContainsPending": "pending" in finalized_review.lower(),
        "lineCount": len(result.get("lines", [])),
    }


def test_reference_completeness() -> dict[str, Any]:
    result = check_reference_completeness.check_reference(
        check_reference_completeness.DEFAULT_REFERENCE,
        check_reference_completeness.DEFAULT_IMAGE,
        min_image_bytes=10000,
    )
    audio_profile = result["summaryInfo"].get("audioProfile", {})
    audio_profile_ok = bool(
        audio_profile.get("nearContinuousAudio") is True
        and audio_profile.get("medianSilenceRatio") == 0.0035
        and audio_profile.get("maxSilenceRatio") == 0.041
    )
    image_link_ok = bool(
        result.get("imageLinkInfo", {}).get("ok")
        and result.get("imageLinkInfo", {}).get("matchingLinks")
    )
    contact_sheet_ok = result["summaryInfo"].get("contactSheet") == check_reference_completeness.DEFAULT_IMAGE.name
    artifact_audit = result["summaryInfo"].get("artifactAudit", {})
    artifact_audit_ok = bool(
        isinstance(artifact_audit, dict)
        and artifact_audit.get("status") == "passed"
        and artifact_audit.get("downloadedMp4") == 181
        and artifact_audit.get("downloadedThumbnails") == 181
        and artifact_audit.get("downloadedVtt") == 528
        and artifact_audit.get("analysisRows") == 181
        and artifact_audit.get("classificationRows") == 181
        and artifact_audit.get("visualMetricRows") == 181
        and artifact_audit.get("transcriptRows") == 181
        and artifact_audit.get("missingReferencedPaths") == 0
        and artifact_audit.get("failures") == 0
    )
    taxonomy_info = result["summaryInfo"].get("patternTaxonomy", {})
    structured_taxonomy_ok = bool(taxonomy_info.get("ok"))
    source_info = result.get("sourceInfo", {})
    playbook_info = result.get("playbookInfo", {})
    command_contracts_info = result.get("commandContractsInfo", {})
    reference_command_info = result.get("referenceCommandInfo", {})
    openai_yaml_info = result.get("openaiYamlInfo", {})
    portable_docs_info = result.get("portableCommandDocsInfo", {})
    source_manifest_ok = bool(
        source_info.get("ok")
        and source_info.get("entryCount") == 181
        and source_info.get("channelCounts", {}).get("Awesome") == 105
        and source_info.get("channelCounts", {}).get("Fireship") == 76
            and source_info.get("sourceIdSha256") == result["summaryInfo"].get("sourceManifest", {}).get("sourceIdSha256")
    )
    playbook_contracts_ok = bool(
        playbook_info.get("ok")
        and playbook_info.get("sequenceNumbers") == list(range(1, 17))
        and not playbook_info.get("missingStyleFidelityTerms")
        and not playbook_info.get("failures")
        and result.get("groups", {}).get("video_types", {}).get("ok")
    )
    command_contracts_ok = bool(
        command_contracts_info.get("ok")
        and command_contracts_info.get("commandBlockCount", 0) >= 8
        and not command_contracts_info.get("missing")
        and command_contracts_info.get("bytes", 0) <= command_contracts_info.get("maxBytes", 10000)
    )
    reference_command_contracts_ok = bool(
        reference_command_info.get("ok")
        and not any(reference_command_info.get("missingByScript", {}).values())
        and reference_command_info.get("commandLineCount", 0) >= 8
    )
    openai_yaml_ok = bool(
        openai_yaml_info.get("ok")
        and openai_yaml_info.get("displayName") == "Awesome/Fireship Video Director"
        and 25 <= int(openai_yaml_info.get("shortDescriptionLength", 0)) <= 64
        and "$awsome-videos" in str(openai_yaml_info.get("defaultPrompt", ""))
    )
    portable_command_docs_ok = bool(
        portable_docs_info.get("ok")
        and portable_docs_info.get("envVariable") == check_reference_completeness.PORTABLE_SKILL_ENV
        and all(
            not file_info.get("forbiddenLines")
            and not file_info.get("commandBlocksMissingEnv")
            and not file_info.get("commandLinesMissingEnv")
            for file_info in portable_docs_info.get("files", {}).values()
            if isinstance(file_info, dict)
        )
    )
    return {
        "passed": bool(
            result["ok"]
            and audio_profile_ok
            and image_link_ok
            and contact_sheet_ok
            and artifact_audit_ok
            and structured_taxonomy_ok
            and source_manifest_ok
            and playbook_contracts_ok
            and command_contracts_ok
            and reference_command_contracts_ok
            and openai_yaml_ok
            and portable_command_docs_ok
        ),
        "failures": result["failures"],
        "warnings": result["warnings"],
        "referenceBytes": result["referenceBytes"],
        "summaryBytes": result["summaryInfo"]["bytes"],
        "sourceBytes": source_info.get("bytes"),
        "summaryOk": result["summaryInfo"]["ok"],
        "sourceManifestOk": source_manifest_ok,
        "sourceEntryCount": source_info.get("entryCount"),
        "sourceChannelCounts": source_info.get("channelCounts"),
        "sourceIdSha256": source_info.get("sourceIdSha256"),
        "consistencyOk": result["consistencyInfo"]["ok"],
        "audioProfileOk": audio_profile_ok,
        "imageLinkOk": image_link_ok,
        "contactSheetOk": contact_sheet_ok,
        "artifactAuditOk": artifact_audit_ok,
        "artifactAudit": artifact_audit,
        "structuredTaxonomyOk": structured_taxonomy_ok,
        "structuredTaxonomyGroups": sorted(taxonomy_info.get("groups", {})),
        "playbookContractsOk": playbook_contracts_ok,
        "playbookSequenceNumbers": playbook_info.get("sequenceNumbers"),
        "playbookMissingStyleFidelityTerms": playbook_info.get("missingStyleFidelityTerms"),
        "playbookFailures": playbook_info.get("failures"),
        "commandContractsOk": command_contracts_ok,
        "commandContractsBytes": command_contracts_info.get("bytes"),
        "commandContractsCommandBlockCount": command_contracts_info.get("commandBlockCount"),
        "commandContractsFailures": command_contracts_info.get("failures"),
        "referenceCommandContractsOk": reference_command_contracts_ok,
        "referenceCommandMissingByScript": reference_command_info.get("missingByScript"),
        "referenceCommandFailures": reference_command_info.get("failures"),
        "openaiYamlOk": openai_yaml_ok,
        "openaiYamlDisplayName": openai_yaml_info.get("displayName"),
        "openaiYamlShortDescriptionLength": openai_yaml_info.get("shortDescriptionLength"),
        "openaiYamlFailures": openai_yaml_info.get("failures"),
        "portableCommandDocsOk": portable_command_docs_ok,
        "portableCommandDocsFiles": portable_docs_info.get("files"),
        "portableCommandDocsFailures": portable_docs_info.get("failures"),
    }


def test_pattern_selector() -> dict[str, Any]:
    explainer = select_video_patterns.select_blueprint(
        SimpleNamespace(
            title="What is a LLM?",
            promise="Explain large language models as token prediction, context, embeddings, and limitations.",
            requested_format="",
            runtime="1:10",
            summary=select_video_patterns.DEFAULT_SUMMARY,
        )
    )
    news = select_video_patterns.select_blueprint(
        SimpleNamespace(
            title="New AI browser security incident",
            promise="Explain what changed, why it matters, and what developers should watch next.",
            requested_format="",
            runtime="4:00",
            summary=select_video_patterns.DEFAULT_SUMMARY,
        )
    )
    explicit = select_video_patterns.select_blueprint(
        SimpleNamespace(
            title="Build a queue worker",
            promise="Show the smallest working queue and the failure mode.",
            requested_format="tutorial/overview",
            runtime="6:00",
            summary=select_video_patterns.DEFAULT_SUMMARY,
        )
    )
    short = select_video_patterns.select_blueprint(
        SimpleNamespace(
            title="What Is RAG?",
            promise="Explain retrieval augmented generation as a search-then-generate loop.",
            requested_format="compressed explainer",
            runtime="0:12",
            summary=select_video_patterns.DEFAULT_SUMMARY,
        )
    )
    markdown = select_video_patterns.render_markdown(explainer)
    short_ranges = [
        extract_voiceover_cues.parse_time_range(str(beat.get("time", "")))
        for beat in short.get("beatGuidance", [])
    ]
    short_ranges_ok = bool(
        short_ranges
        and all(item and item["endSeconds"] > item["startSeconds"] for item in short_ranges)
        and abs(float(short_ranges[-1]["endSeconds"]) - 12) < 0.001
    )
    failures: list[str] = []
    if explainer.get("selectedFormat") != "compressed explainer":
        failures.append("what-is explainer did not select compressed explainer")
    if len(explainer.get("beatGuidance", [])) != 8:
        failures.append("explainer did not produce 8 beatGuidance rows")
    if "code proof" not in [item.get("name") for item in explainer.get("visualSources", [])]:
        failures.append("explainer did not include code proof")
    if "diagram trace" not in [item.get("name") for item in explainer.get("animationAtoms", [])]:
        failures.append("explainer did not include diagram trace")
    if news.get("selectedFormat") != "trend/news commentary":
        failures.append("incident did not select trend/news commentary")
    if "human/context insert" not in [item.get("name") for item in news.get("visualSources", [])]:
        failures.append("news selector did not include human/context insert")
    if "low impact" not in [item.get("name") for item in news.get("audioRoles", [])]:
        failures.append("news selector did not include low impact")
    if explicit.get("selectedFormat") != "tutorial/overview":
        failures.append("explicit format was not honored")
    if not short_ranges_ok:
        failures.append("short selector beat ranges collapsed or missed the requested runtime")
    if "Pattern Blueprint" not in markdown or "Beat Guidance" not in markdown:
        failures.append("markdown blueprint is missing expected sections")
    return {
        "passed": not failures,
        "failures": failures,
        "explainerFormat": explainer.get("selectedFormat"),
        "explainerBeatCount": len(explainer.get("beatGuidance", [])),
        "newsFormat": news.get("selectedFormat"),
        "explicitFormat": explicit.get("selectedFormat"),
        "shortRangesOk": short_ranges_ok,
        "shortBeatRanges": [beat.get("time") for beat in short.get("beatGuidance", [])],
        "markdownHasBlueprint": "Pattern Blueprint" in markdown,
    }


def test_scaffold_manifest_duration(tmp: Path) -> dict[str, Any]:
    project = tmp / "scaffold-package"
    result = scaffold_production_package.scaffold(
        make_args(
            project_dir=project,
            title="What Is A Cache?",
            promise="Explain cache as a reuse layer with keys, hits, misses, stale data, and invalidation.",
            audience="Developers who know HTTP and basic storage.",
            format="compressed explainer",
            runtime="1:10",
            project_id="cache",
            skill_path="skills/awsome-videos",
            force=True,
            json=True,
        )
    )
    manifest_path = project / "source" / "package-manifest.json"
    brief_path = project / "source" / "brief.md"
    production_notes_path = project / "source" / "production-notes.md"
    pattern_blueprint_json_path = project / "source" / "pattern-blueprint.json"
    pattern_blueprint_md_path = project / "source" / "pattern-blueprint.md"
    asset_manifest_path = project / "source" / "asset-manifest.json"
    composition_plan_path = project / "source" / "composition-plan.json"
    source_package_path = project / "source" / "source-package.json"
    shot_contract_path = project / "source" / "shot-contract.json"
    transition_plan_path = project / "source" / "transition-plan.json"
    visual_review_path = project / "artifacts" / "reviews" / "visual-review.json"
    renderer_path = project / "src" / "index.html"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    brief_text = brief_path.read_text(encoding="utf-8")
    production_notes = production_notes_path.read_text(encoding="utf-8")
    pattern_blueprint = json.loads(pattern_blueprint_json_path.read_text(encoding="utf-8"))
    asset_manifest = json.loads(asset_manifest_path.read_text(encoding="utf-8"))
    visual_review = json.loads(visual_review_path.read_text(encoding="utf-8"))
    renderer_text = renderer_path.read_text(encoding="utf-8")
    brief_voiceover = check_video_brief.validate(brief_text, min_beats=8, require_voiceover=True)
    commands = manifest.get("commands", {})
    paths = manifest.get("paths", {})
    runtime_preflight_command = str(commands.get("runtimePreflight", ""))
    select_patterns_command = str(commands.get("selectPatterns", ""))
    brief_command = str(commands.get("briefValidation", ""))
    visual_contract_command = str(commands.get("visualContractValidation", ""))
    renderer_contract_command = str(commands.get("rendererValidation", ""))
    video_command = str(commands.get("videoValidation", ""))
    package_command = str(commands.get("packageValidation", ""))
    render_command = str(commands.get("renderVideo", ""))
    score_command = str(commands.get("scoreReadiness", ""))
    voiceover_cues_command = str(commands.get("extractVoiceoverCues", ""))
    style_fidelity_command = str(commands.get("styleFidelity", ""))
    finalize_notes_command = str(commands.get("finalizeProductionNotes", ""))
    package_contract_command_ok = all(
        term in package_command
        for term in [
            "--production-notes",
            "--package-manifest",
            "--motion-report",
            "--audio-report",
            "--require-audio-report",
            "--require-voiceover",
            "--require-production-notes",
            "--require-package-manifest",
            "--require-final-review-notes",
            "--pattern-blueprint source/pattern-blueprint.json",
            "--require-pattern-blueprint",
            "--style-fidelity-report artifacts/reviews/style-fidelity.json",
            "--min-style-fidelity-score 12",
            "--require-style-fidelity-report",
            "--asset-manifest source/asset-manifest.json",
            "--composition-plan source/composition-plan.json",
            "--visual-review artifacts/reviews/visual-review.json",
            "--visual-contract-report artifacts/reviews/asset-composition-validation.json",
            "--renderer-report artifacts/reviews/renderer-contract.json",
            "--require-visual-contract",
            "--require-ready-assets",
            "--require-specialist-routing",
            "--require-source-routing",
            "--require-reviewed-scenes",
            "--forbid-scaffold-renderer",
            "--require-renderer-beat-coverage",
            "--require-renderer-visual-coverage",
            "--require-motion-report",
            "--min-readiness-score 18",
        ]
    )
    renderer_beat_coverage_command_ok = all(
        term in render_command
        for term in [
            "--brief source/brief.md",
            "--require-all-brief-beats",
            "--capture-fps 12",
            "--render-state-report artifacts/reviews/render-state.json",
        ]
    ) and "--require-renderer-beat-coverage" in package_command
    visual_contract_command_ok = all(
        term in visual_contract_command
        for term in [
            "check_visual_contract.py",
            "--asset-manifest source/asset-manifest.json",
            "--composition-plan source/composition-plan.json",
            "--visual-review artifacts/reviews/visual-review.json",
            "--video artifacts/videos/cache.mp4",
            "--project-root .",
            "--min-assets 8",
            "--min-scenes 8",
            "--require-ready-assets",
            "--require-specialist-routing",
            "--require-source-routing",
            "--require-reviewed-scenes",
            "--output artifacts/reviews/asset-composition-validation.json",
        ]
    )
    renderer_contract_command_ok = all(
        term in renderer_contract_command
        for term in [
            "check_renderer_contract.py src/index.html",
            "--brief source/brief.md",
            "--require-all-brief-beats",
            "--asset-manifest source/asset-manifest.json",
            "--composition-plan source/composition-plan.json",
            "--require-visual-ids",
            "--output artifacts/reviews/renderer-contract.json",
        ]
    )
    fast_capture_command_ok = "--capture-fps 12" in render_command and "--capture-fps 12" in production_notes
    pattern_blueprint_ok = (
        pattern_blueprint.get("ok") is True
        and pattern_blueprint.get("selectedFormat") == "compressed explainer"
        and len(pattern_blueprint.get("beatGuidance", [])) == 8
        and pattern_blueprint_md_path.exists()
        and paths.get("patternBlueprintJson") == "source/pattern-blueprint.json"
        and paths.get("patternBlueprintMarkdown") == "source/pattern-blueprint.md"
        and all(
            term in select_patterns_command
            for term in [
                "select_video_patterns.py",
                '--title "What Is A Cache?"',
                "--output source/pattern-blueprint.json",
                "--json",
            ]
        )
    )
    contracts = manifest.get("contracts", {})
    visual_contract_paths_ok = bool(
        source_package_path.is_file()
        and shot_contract_path.is_file()
        and asset_manifest_path.is_file()
        and composition_plan_path.is_file()
        and transition_plan_path.is_file()
        and visual_review_path.is_file()
        and paths.get("sourcePackage") == "source/source-package.json"
        and paths.get("shotContract") == "source/shot-contract.json"
        and paths.get("assetManifest") == "source/asset-manifest.json"
        and paths.get("compositionPlan") == "source/composition-plan.json"
        and paths.get("transitionPlan") == "source/transition-plan.json"
        and paths.get("visualReview") == "artifacts/reviews/visual-review.json"
        and paths.get("visualContractValidation") == "artifacts/reviews/asset-composition-validation.json"
        and paths.get("rendererValidation") == "artifacts/reviews/renderer-contract.json"
        and paths.get("renderState") == "artifacts/reviews/render-state.json"
        and contracts.get("sourcePackage") == paths.get("sourcePackage")
        and contracts.get("shotContract") == paths.get("shotContract")
        and contracts.get("assetManifest") == paths.get("assetManifest")
        and contracts.get("compositionPlan") == paths.get("compositionPlan")
        and contracts.get("transitionPlan") == paths.get("transitionPlan")
        and contracts.get("visualReview") == paths.get("visualReview")
        and contracts.get("validationReport") == paths.get("visualContractValidation")
    )
    planned_route_proofs_ok = bool(
        asset_manifest.get("skillRouting")
        and all(
            route.get("status") == "planned"
            and isinstance(route.get("proof"), str)
            and route.get("proof", "").startswith("artifacts/reviews/")
            and not re.match(r"^(?:[A-Za-z]:|/)", route.get("proof", ""))
            and isinstance(route.get("outputPaths"), list)
            and bool(route.get("outputPaths"))
            for route in asset_manifest.get("skillRouting", [])
        )
        and any(route.get("skill") == "mermaid-animated-svg" for route in asset_manifest.get("skillRouting", []))
        and manifest.get("toolchain") == asset_manifest.get("skillRouting")
    )
    scaffold_wireframe_ok = bool(
        result.get("rendererMetadata", {}).get("rendererMode") == "wireframe"
        and result.get("rendererMetadata", {}).get("finalPackageEligible") is False
        and "AWSOME_SCAFFOLD_WIREFRAME" in renderer_text
        and "window.AWSOME_SCAFFOLD_WIREFRAME = true" in renderer_text
    )
    visual_review_scaffold_ok = bool(
        visual_review.get("overallStatus") == "pending"
        and visual_review.get("candidateVideo", {}).get("sha256") is None
        and visual_review.get("fullSpeedPlayback", {}).get("reviewed") is False
        and len(visual_review.get("scenes", [])) == 8
    )
    runtime_preflight_command_ok = all(
        term in runtime_preflight_command
        for term in [
            "check_runtime_tools.py",
            "--require-render-tools",
            "--json",
        ]
    )
    motion_report_command_ok = all(
        "--motion-report" in command
        for command in [render_command, video_command, score_command, package_command]
    )
    audio_report_command_ok = all(
        "--audio-report" in command
        for command in [render_command, video_command, score_command, package_command]
    ) and "--require-audio-report" in video_command and "--require-audio-report" in package_command
    voiceover_cues_command_ok = all(
        term in voiceover_cues_command
        for term in [
            "extract_voiceover_cues.py",
            "--format json",
            "--min-cues 8",
            "--expect-duration 70",
            "--duration-tolerance 1",
            "--require-beat-match",
            "--output artifacts/audio/voiceover-cues.json",
        ]
    )
    style_fidelity_command_ok = all(
        term in style_fidelity_command
        for term in [
            "score_style_fidelity.py",
            "--brief source/brief.md",
            "--pattern-blueprint source/pattern-blueprint.json",
            "--require-voiceover",
            "--require-pattern-blueprint",
            "--require-source-links",
            "--output artifacts/reviews/style-fidelity.json",
            "--json",
        ]
    )
    source_link_command_ok = all(
        "--require-source-links" in command
        for command in [brief_command, score_command, style_fidelity_command, package_command]
    )
    readiness_voiceover_command_ok = "--require-voiceover" in score_command
    readiness_visual_contract_command_ok = all(
        term in score_command
        for term in [
            "--renderer-report artifacts/reviews/renderer-contract.json",
            "--visual-contract-report artifacts/reviews/asset-composition-validation.json",
            "--require-visual-contract-report",
        ]
    )
    finalize_notes_command_ok = all(
        term in finalize_notes_command
        for term in [
            "finalize_production_notes.py",
            "source/production-notes.md",
            "--renderer-report artifacts/reviews/renderer-contract.json",
            "--readiness-report artifacts/reviews/readiness-score.json",
            "--contact-sheet artifacts/reviews/contact-sheet.jpg",
            "--quality-report artifacts/reviews/quality-report.json",
            "--motion-report artifacts/reviews/motion-report.json",
            "--audio-report artifacts/reviews/audio-report.json",
            "--visual-review artifacts/reviews/visual-review.json",
            "--visual-contract-report artifacts/reviews/asset-composition-validation.json",
            "--json",
        ]
    )
    tmp_marker = scaffold_production_package.command_path(tmp)
    manifest_commands_portable_ok = all(tmp_marker not in str(command) for command in commands.values())
    manifest_paths_relative_ok = all(
        isinstance(path, str) and not re.match(r"^(?:[A-Za-z]:|/)", path)
        for path in paths.values()
    )
    duration_command_ok = all(
        "--expect-duration 70" in command and "--duration-tolerance 1" in command
        for command in [video_command, package_command]
    )
    generic_placeholders = ["Source-bound visual", "Logo, source, UI", "Final mechanism summary"]
    brief_specificity_ok = (
        brief_text.count("Cache") >= 6
        and all(placeholder not in brief_text for placeholder in generic_placeholders)
        and all(blank not in brief_text for blank in ["Cold-open line:\n\n", "First visual:\n\n", "Audio cue:\n\n", "- Screenshots:\n"])
    )
    production_notes_ok = (
        "Concept claim: Explain cache" in production_notes
        and "Chosen visual metaphor: Cache" in production_notes
        and "artifacts/videos/cache.mp4" in production_notes
        and "--expect-duration 70" in production_notes
        and "Motion report: artifacts/reviews/motion-report.json" in production_notes
        and "Audio report: artifacts/reviews/audio-report.json" in production_notes
        and "Pattern blueprint: source/pattern-blueprint.json" in production_notes
        and "Asset manifest: source/asset-manifest.json" in production_notes
        and "Composition plan: source/composition-plan.json" in production_notes
        and "Visual review: artifacts/reviews/visual-review.json" in production_notes
        and "Visual contract report: artifacts/reviews/asset-composition-validation.json" in production_notes
        and "Renderer contract report: artifacts/reviews/renderer-contract.json" in production_notes
    )
    production_notes_command_ok = all(
        term in production_notes
        for term in [
            "uv run --script skills/awsome-videos/scripts/select_video_patterns.py",
            "--output source/pattern-blueprint.json",
            "uv run --script skills/awsome-videos/scripts/check_video_brief.py",
            "--require-voiceover",
            "--require-source-links",
            "uv run --script skills/awsome-videos/scripts/check_visual_contract.py",
            "--asset-manifest source/asset-manifest.json",
            "--composition-plan source/composition-plan.json",
            "--visual-review artifacts/reviews/visual-review.json",
            "--visual-contract-report artifacts/reviews/asset-composition-validation.json",
            "uv run --script skills/awsome-videos/scripts/check_renderer_contract.py",
            "--require-visual-ids",
            "--output artifacts/reviews/renderer-contract.json",
            "uv run --script skills/awsome-videos/scripts/score_style_fidelity.py",
            "--output artifacts/reviews/style-fidelity.json",
            "--style-fidelity-report artifacts/reviews/style-fidelity.json",
            "--min-style-fidelity-score 12",
            "uv run --script skills/awsome-videos/scripts/render_concept_video.py",
            "--require-all-brief-beats",
            "--capture-fps 12",
            "uv run --script skills/awsome-videos/scripts/check_video_artifact.py",
            "uv run --script skills/awsome-videos/scripts/score_video_readiness.py",
            "uv run --script skills/awsome-videos/scripts/finalize_production_notes.py",
            "--readiness-report artifacts/reviews/readiness-score.json",
            "score_video_readiness.py --require-source-links --brief",
            "uv run --script skills/awsome-videos/scripts/check_production_package.py",
            "Command working directory: project root",
            "source/",
            "artifacts/",
            "--duration 70",
            "--expect-duration 70",
            "--production-notes source/production-notes.md",
            "--package-manifest source/package-manifest.json",
            "--require-production-notes",
            "--require-package-manifest",
            "--require-style-fidelity-report",
            "--require-visual-contract",
            "--require-ready-assets",
            "--require-specialist-routing",
            "--require-source-routing",
            "--require-reviewed-scenes",
            "--forbid-scaffold-renderer",
            "--require-renderer-beat-coverage",
            "--require-renderer-visual-coverage",
            "--contact-sheet artifacts/reviews/contact-sheet.jpg",
            "--motion-report artifacts/reviews/motion-report.json",
            "--audio-report artifacts/reviews/audio-report.json",
            "--require-audio-report",
            "--require-contact-sheet",
            "--require-motion-report",
        ]
    )
    production_notes_skill_path_ok = "{{SKILL_PATH}}" not in production_notes and ".agents/skills/awsome-videos" not in production_notes
    production_notes_cwd_ok = all(
        term in production_notes
        for term in [
            "Command working directory: project root",
            "folder that contains `source/`, `src/`, and `artifacts/`",
        ]
    )
    notes_contract_failures: list[str] = []
    notes_contract_warnings: list[str] = []
    notes_contract_info = check_production_package.validate_production_notes(
        production_notes_path,
        notes_contract_failures,
        notes_contract_warnings,
        required=True,
        expected_duration=70,
        require_pattern_blueprint=True,
    )
    manifest_contract_failures: list[str] = []
    manifest_contract_warnings: list[str] = []
    manifest_contract_info = check_production_package.validate_package_manifest(
        manifest_path,
        manifest_contract_failures,
        manifest_contract_warnings,
        required=True,
        require_pattern_blueprint=True,
    )
    blueprint_contract_failures: list[str] = []
    blueprint_contract_warnings: list[str] = []
    blueprint_contract_info = check_production_package.validate_pattern_blueprint(
        pattern_blueprint_json_path,
        blueprint_contract_failures,
        blueprint_contract_warnings,
        required=True,
    )
    production_notes_contract_ok = bool(
        notes_contract_info
        and notes_contract_info.get("commandContract", {}).get("ok")
        and not notes_contract_failures
    )
    package_manifest_pattern_contract_ok = bool(
        manifest_contract_info
        and not manifest_contract_failures
        and not manifest_contract_info.get("missingPatternBlueprintCommandTerms")
        and "patternBlueprintJson" in manifest_contract_info.get("paths", [])
    )
    pattern_blueprint_contract_ok = bool(
        blueprint_contract_info
        and not blueprint_contract_failures
        and blueprint_contract_info.get("ok") is True
        and blueprint_contract_info.get("beatGuidanceRows") == 8
    )
    short_project = tmp / "scaffold-package-45s"
    scaffold_production_package.scaffold(
        make_args(
            project_dir=short_project,
            title="What Is A Job Queue?",
            promise="Explain a job queue as pending work, workers, retries, and completion.",
            audience="Developers who know background jobs.",
            format="compressed explainer",
            runtime="0:45",
            project_id="job-queue",
            skill_path="skills/awsome-videos",
            force=True,
            json=True,
        )
    )
    short_notes = (short_project / "source" / "production-notes.md").read_text(encoding="utf-8")
    dynamic_notes_duration_ok = (
        "--duration 45" in short_notes
        and "--expect-duration 45" in short_notes
        and "--duration 70" not in short_notes
        and "--expect-duration 70" not in short_notes
        and "skills/awsome-videos/scripts/render_concept_video.py" in short_notes
        and "--motion-report artifacts/reviews/motion-report.json" in short_notes
        and "--audio-report artifacts/reviews/audio-report.json" in short_notes
        and "{{SKILL_PATH}}" not in short_notes
    )
    smoke_project = tmp / "scaffold-package-12s"
    scaffold_production_package.scaffold(
        make_args(
            project_dir=smoke_project,
            title="What Is RAG?",
            promise="Explain retrieval augmented generation as a search-then-generate loop.",
            audience="Developers testing a short smoke render.",
            format="compressed explainer",
            runtime="0:12",
            project_id="rag",
            skill_path="skills/awsome-videos",
            force=True,
            json=True,
        )
    )
    smoke_brief_path = smoke_project / "source" / "brief.md"
    smoke_brief_text = smoke_brief_path.read_text(encoding="utf-8")
    smoke_brief_validation = check_video_brief.validate(smoke_brief_text, min_beats=8, require_voiceover=True)
    smoke_cues = extract_voiceover_cues.build_result(
        make_args(
            brief=smoke_brief_path,
            format="json",
            output=None,
            min_cues=8,
            expect_duration=12,
            duration_tolerance=0.1,
            cue_time_tolerance=0.05,
            require_beat_match=True,
            allow_overlap=False,
            json=False,
        )
    )
    smoke_cues_ok = bool(
        smoke_cues.get("ok")
        and smoke_cues.get("cueCount") == 8
        and smoke_cues.get("beatCount") == 8
        and abs(float(smoke_cues.get("finalCueEndSeconds", 0)) - 12) < 0.001
        and not smoke_cues.get("beatCueMismatches")
    )
    default_project = tmp / "nested" / "default-skill-path"
    scaffold_production_package.scaffold(
        make_args(
            project_dir=default_project,
            title="What Is A Default Path?",
            promise="Explain default paths as project-root-relative command targets.",
            audience="Developers packaging a video handoff.",
            format="compressed explainer",
            runtime="1:10",
            project_id="default-path",
            skill_path=None,
            force=True,
            json=True,
        )
    )
    default_notes = (default_project / "source" / "production-notes.md").read_text(encoding="utf-8")
    expected_default_skill_path = scaffold_production_package.default_skill_path(default_project)
    default_skill_path_project_root_ok = (
        expected_default_skill_path in default_notes
        and "uv run --script .agents/skills/awsome-videos" not in default_notes.replace("\\", "/")
    )
    return {
        "passed": bool(
            result["ok"]
            and manifest_path.exists()
            and runtime_preflight_command_ok
            and duration_command_ok
            and "--duration 70" in render_command
            and fast_capture_command_ok
            and package_contract_command_ok
            and renderer_beat_coverage_command_ok
            and visual_contract_command_ok
            and renderer_contract_command_ok
            and motion_report_command_ok
            and audio_report_command_ok
            and voiceover_cues_command_ok
            and style_fidelity_command_ok
            and source_link_command_ok
            and pattern_blueprint_ok
            and visual_contract_paths_ok
            and planned_route_proofs_ok
            and scaffold_wireframe_ok
            and visual_review_scaffold_ok
            and paths.get("voiceoverCuesJson") == "artifacts/audio/voiceover-cues.json"
            and paths.get("styleFidelity") == "artifacts/reviews/style-fidelity.json"
            and paths.get("voiceoverCuesSrt") == "artifacts/audio/voiceover-cues.srt"
            and paths.get("voiceoverCuesCsv") == "artifacts/audio/voiceover-cues.csv"
            and readiness_voiceover_command_ok
            and readiness_visual_contract_command_ok
            and finalize_notes_command_ok
            and manifest_commands_portable_ok
            and manifest_paths_relative_ok
            and brief_specificity_ok
            and brief_voiceover.get("ok")
            and brief_voiceover.get("voiceover_line_count") == 8
            and production_notes_ok
            and production_notes_command_ok
            and production_notes_skill_path_ok
            and production_notes_cwd_ok
            and production_notes_contract_ok
            and package_manifest_pattern_contract_ok
            and pattern_blueprint_contract_ok
            and dynamic_notes_duration_ok
            and smoke_brief_validation.get("ok")
            and smoke_cues_ok
            and default_skill_path_project_root_ok
        ),
        "manifest": str(manifest_path),
        "runtimePreflightCommandOk": runtime_preflight_command_ok,
        "runtimePreflightCommand": runtime_preflight_command,
        "durationCommandOk": duration_command_ok,
        "packageContractCommandOk": package_contract_command_ok,
        "rendererBeatCoverageCommandOk": renderer_beat_coverage_command_ok,
        "visualContractCommandOk": visual_contract_command_ok,
        "visualContractCommand": visual_contract_command,
        "rendererContractCommandOk": renderer_contract_command_ok,
        "rendererContractCommand": renderer_contract_command,
        "rendererContractPath": paths.get("rendererValidation"),
        "renderStatePath": paths.get("renderState"),
        "visualContractPathsOk": visual_contract_paths_ok,
        "plannedRouteProofsOk": planned_route_proofs_ok,
        "scaffoldWireframeOk": scaffold_wireframe_ok,
        "rendererMetadata": result.get("rendererMetadata"),
        "visualReviewScaffoldOk": visual_review_scaffold_ok,
        "fastCaptureCommandOk": fast_capture_command_ok,
        "fastCaptureRenderCommand": render_command,
        "patternBlueprintOk": pattern_blueprint_ok,
        "selectPatternsCommand": select_patterns_command,
        "motionReportCommandOk": motion_report_command_ok,
        "audioReportCommandOk": audio_report_command_ok,
        "voiceoverCuesCommandOk": voiceover_cues_command_ok,
        "voiceoverCuesJsonPath": paths.get("voiceoverCuesJson"),
        "styleFidelityCommandOk": style_fidelity_command_ok,
        "sourceLinkCommandOk": source_link_command_ok,
        "briefValidationCommand": brief_command,
        "styleFidelityPath": paths.get("styleFidelity"),
        "readinessVoiceoverCommandOk": readiness_voiceover_command_ok,
        "readinessVisualContractCommandOk": readiness_visual_contract_command_ok,
        "finalizeNotesCommandOk": finalize_notes_command_ok,
        "manifestCommandsPortableOk": manifest_commands_portable_ok,
        "manifestPathsRelativeOk": manifest_paths_relative_ok,
        "briefSpecificityOk": brief_specificity_ok,
        "briefVoiceoverOk": brief_voiceover.get("ok"),
        "briefVoiceoverLineCount": brief_voiceover.get("voiceover_line_count"),
        "productionNotesOk": production_notes_ok,
        "productionNotesCommandOk": production_notes_command_ok,
        "productionNotesSkillPathOk": production_notes_skill_path_ok,
        "productionNotesCwdOk": production_notes_cwd_ok,
        "productionNotesContractOk": production_notes_contract_ok,
        "productionNotesContractFailures": notes_contract_failures,
        "packageManifestPatternContractOk": package_manifest_pattern_contract_ok,
        "packageManifestPatternFailures": manifest_contract_failures,
        "patternBlueprintContractOk": pattern_blueprint_contract_ok,
        "patternBlueprintContractFailures": blueprint_contract_failures,
        "dynamicNotesDurationOk": dynamic_notes_duration_ok,
        "smokeBriefOk": smoke_brief_validation.get("ok"),
        "smokeCueOk": smoke_cues_ok,
        "smokeCueFinalEndSeconds": smoke_cues.get("finalCueEndSeconds"),
        "smokeCueFailures": smoke_cues.get("failures"),
        "defaultSkillPathProjectRootOk": default_skill_path_project_root_ok,
        "videoValidation": video_command,
        "scoreReadiness": score_command,
        "packageValidation": package_command,
    }


def run_tests() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="awsome-validator-tests-") as raw_tmp:
        tmp = Path(raw_tmp)
        shared_visual_fixture = build_visual_contract_fixture(tmp / "shared-visual-contract")
        tests = {
            "briefValidator": test_brief_validator(),
            "visualContract": test_visual_contract(tmp, shared_visual_fixture),
            "readinessScorer": test_readiness_scorer(tmp, shared_visual_fixture),
            "styleFidelityScorer": test_style_fidelity_scorer(tmp),
            "hookTimingScoring": test_hook_timing_scoring(),
            "packageReportProjection": test_package_report_projection(tmp, shared_visual_fixture),
            "audioLevelParser": test_audio_level_parser(),
            "audioReportContract": test_audio_report_contract(tmp),
            "voiceoverCueExtractor": test_voiceover_cue_extractor(tmp),
            "contactSheetQuality": test_contact_sheet_quality(tmp),
            "rendererScreenshotQuality": test_renderer_screenshot_quality(),
            "motionReportDetection": test_motion_report_detection(tmp),
            "fastCaptureMath": test_fast_capture_math(),
            "runtimePreflight": test_runtime_preflight(tmp),
            "packageSourceContracts": test_package_source_contracts(tmp),
            "finalizeProductionNotes": test_finalize_production_notes(tmp, shared_visual_fixture),
            "referenceCompleteness": test_reference_completeness(),
            "patternSelector": test_pattern_selector(),
            "scaffoldManifest": test_scaffold_manifest_duration(tmp),
        }
    failures = [name for name, result in tests.items() if not result.get("passed")]
    return {"ok": not failures, "failures": failures, "tests": tests}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run awsome-videos validator regression tests.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_tests()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print(f"PASS awsome-videos validator tests: {len(result['tests'])} checks")
    else:
        print("FAIL awsome-videos validator tests")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
