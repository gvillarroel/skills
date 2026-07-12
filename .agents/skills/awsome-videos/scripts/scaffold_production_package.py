#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scaffold an awsome-videos production package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "templates"
BASE_BEAT_WEIGHTS = [5, 10, 10, 10, 10, 10, 10, 5]

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import create_concept_renderer  # noqa: E402
import select_video_patterns  # noqa: E402


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "video-package"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold an awsome-videos production package.")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--promise", default="")
    parser.add_argument("--audience", default="Developers and technical viewers.")
    parser.add_argument("--format", default="compressed explainer")
    parser.add_argument("--runtime", default="1:10")
    parser.add_argument("--project-id")
    parser.add_argument("--skill-path", help="Path to the awsome-videos skill folder for generated commands.")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffolded text files if they already exist.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def write_file(path: Path, text: str, force: bool, written: list[str], skipped: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        skipped.append(str(path))
        return
    path.write_text(text, encoding="utf-8", newline="\n")
    written.append(str(path))


def load_template(name: str) -> str:
    path = TEMPLATE_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def concept_name(title: str) -> str:
    clean = re.sub(r"^\s*what\s+is\s+(?:an?\s+|the\s+)?", "", title.strip(), flags=re.IGNORECASE)
    clean = clean.strip(" ?!.")
    return clean or title.strip(" ?!.") or "the concept"


def sanitize_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("|", "/")).strip()


def compact_number(value: float) -> str:
    if abs(value - round(value)) < 0.001:
        return str(int(round(value)))
    return f"{value:.1f}".rstrip("0").rstrip(".")


def format_time(value: float) -> str:
    if abs(value - round(value)) >= 0.001:
        return f"{compact_number(value)}s"
    total = int(round(value))
    minutes, seconds = divmod(total, 60)
    return f"{minutes}:{seconds:02d}"


def scaled_beat_ranges(runtime: str, count: int) -> list[str]:
    if count <= 0:
        return []
    total_seconds = create_concept_renderer.seconds(runtime)
    if total_seconds <= 0:
        total_seconds = float(count)
    if total_seconds < count:
        duration = total_seconds / count
        edges = [round(duration * index, 3) for index in range(count + 1)]
        return [f"{format_time(edges[index])}-{format_time(edges[index + 1])}" for index in range(count)]

    total = int(round(total_seconds))
    weights = (BASE_BEAT_WEIGHTS * ((count // len(BASE_BEAT_WEIGHTS)) + 1))[:count]
    durations = [1] * count
    remaining = total - count
    shares = [remaining * weight / sum(weights) for weight in weights]
    extras = [int(share) for share in shares]
    for index, extra in enumerate(extras):
        durations[index] += extra
    leftover = remaining - sum(extras)
    order = sorted(range(count), key=lambda index: shares[index] - extras[index], reverse=True)
    for index in order[:leftover]:
        durations[index] += 1

    ranges: list[str] = []
    cursor = 0
    for duration in durations:
        start = cursor
        cursor += duration
        ranges.append(f"{format_time(start)}-{format_time(cursor)}")
    return ranges


def mechanism_terms(title: str, promise: str) -> str:
    source = promise or title
    title_terms = {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9+-]{2,}", concept_name(title))
    }
    skip = {
        "what",
        "with",
        "that",
        "this",
        "from",
        "into",
        "then",
        "than",
        "the",
        "when",
        "where",
        "many",
        "same",
        "explain",
        "clear",
        "mechanism",
        "practical",
        "example",
        "limitation",
        "concept",
    }
    terms: list[str] = []
    for token in re.findall(r"[A-Za-z][A-Za-z0-9+-]{2,}", source):
        lower = token.lower()
        if promise and lower in title_terms:
            continue
        if lower in skip or lower in terms:
            continue
        terms.append(lower)
        if len(terms) >= 4:
            break
    return ", ".join(terms) if terms else "input, state, output, tradeoff"


def concept_rows(args: argparse.Namespace, promise: str) -> str:
    concept = sanitize_cell(concept_name(args.title))
    terms = sanitize_cell(mechanism_terms(args.title, promise))
    rows = [
        ("Claim or contradiction", f"{concept} title anchor plus promise consequence proof", "Smash scale-in on consequence", "Hard cut", "Hit plus bed starts"),
        ("Definition", f"{concept} definition card with docs/code/UI source surface", "Highlight sweep over definition terms", "Punch-in", "Bed ducked under voiceover"),
        ("Mechanism input", f"Input/source surface feeding {concept}: {terms}", "Trace input path into mechanism", "Match cut", "Tick accents"),
        ("Mechanism state", f"State diagram showing {concept} changing through {terms}", "State nodes build and pulse", "Hard cut", "Whoosh on state change"),
        ("Practical output", f"UI/code/output proof showing {concept} result", "Output card pops from mechanism", "Jump cut", "Light hit"),
        ("Contrast or warning", f"Split screen: uncontrolled {concept} failure versus controlled mitigation path", "Snap contrast plus warning strip", "Smash cut", "Riser into brief dropout"),
        ("Rule of thumb", f"Checklist for {concept}: trigger, control, proof, and tradeoff", "Checklist chips highlight in order", "Wipe or hard cut", "Bed returns with ticks"),
        ("Callback", f"Full {concept} mechanism summary with final practical rule", "Zoom out to complete system", "Final cut", "Final hit and tail"),
    ]
    ranges = scaled_beat_ranges(args.runtime, len(rows))
    return "\n".join(
        f"| {ranges[index]} | b{index + 1:02d} | s{index + 1:02d} | {purpose} | {visual} | {animation} | {transition} | {audio} |"
        for index, (purpose, visual, animation, transition, audio) in enumerate(rows)
    )


def voiceover_lines(args: argparse.Namespace, promise: str) -> str:
    concept = sanitize_cell(concept_name(args.title))
    terms = sanitize_cell(mechanism_terms(args.title, promise))
    lines = [
        f"{concept} looks simple until {terms} reveal the hidden mechanism.",
        f"In practice, {concept} is the part that turns input into visible state and output.",
        f"First, the input enters through {terms}, which decides what the system can change.",
        f"Then {concept} changes state, and that state is the difference between a label and a system.",
        f"The proof is the output: you can see {concept} produce a result, not just a diagram.",
        f"Without control, {concept} drifts into the failure path; with checks, it stays usable.",
        "The reusable rule is to name the trigger, the control, the proof, and the tradeoff.",
        f"So {concept} is not magic; it is visible state movement you can test.",
    ]
    ranges = scaled_beat_ranges(args.runtime, len(lines))
    return "\n".join(f"- {ranges[index]}: {line}" for index, line in enumerate(lines))


def replace_voiceover_block(text: str, args: argparse.Namespace, promise: str) -> str:
    return re.sub(
        r"(## Voiceover Draft\n\n).*?(\n\n## Script Style Notes)",
        lambda match: match.group(1) + voiceover_lines(args, promise) + match.group(2),
        text,
        flags=re.DOTALL,
    )


def replace_template_rows(text: str, rows: str) -> str:
    old_rows = """| 0:00-0:05 | b01 | s01 | Claim or contradiction | Logo, source, UI, code, or mechanism anchor | Smash scale-in or reveal | Hard cut | Hit plus bed starts |
| 0:05-0:15 | b02 | s02 | Definition | Diagram, docs, UI, or code proof | Highlight sweep | Punch-in | Bed ducked |
| 0:15-0:25 | b03 | s03 | Mechanism step 1 | Source-bound visual | Trace or pan | Match cut | Tick or whoosh |
| 0:25-0:35 | b04 | s04 | Mechanism step 2 | Source-bound visual | State change | Hard cut | Light hit |
| 0:35-0:45 | b05 | s05 | Practical example | UI/code/output state | Build or type-on | Jump cut | Tick accents |
| 0:45-0:55 | b06 | s06 | Contrast or warning | Split screen or warning proof | Snap contrast or glitch | Smash cut | Dropout or low impact |
| 0:55-1:05 | b07 | s07 | Rule of thumb | Checklist, diagram, or code outcome | Chips or highlights | Wipe or hard cut | Bed returns |
| 1:05-1:10 | b08 | s08 | Callback | Final mechanism summary | Zoom out or resolve | Final cut | Final hit and tail |"""
    return text.replace(old_rows, rows)


def fill_brief_sections(text: str, args: argparse.Namespace, promise: str) -> str:
    concept = sanitize_cell(concept_name(args.title))
    terms = sanitize_cell(mechanism_terms(args.title, promise))
    replacements = {
        "Cold-open line:\n": (
            f"Cold-open line: {concept} looks simple until {terms} reveal the actual mechanism.\n"
        ),
        "First visual:\n": (
            f"First visual: {concept} title anchor beside docs/code/UI proof and a compact mechanism diagram.\n"
        ),
        "Audio cue:\n": "Audio cue: Cold hit at 0:00, continuous bed starts, voiceover ducks under definition and proof beats.\n",
        "- Screenshots:\n": (
            f"- Screenshots: docs, UI, terminal, or source page that names {concept} and shows {terms}.\n"
        ),
        "- Code/UI captures:\n": (
            f"- Code/UI captures: minimal example where {concept} changes visible input, state, or output.\n"
        ),
        "- Diagrams/generated visuals:\n": (
            f"- Diagrams/generated visuals: {concept} state flow with trigger, control, proof, and tradeoff zones.\n"
        ),
        "- Source links:\n": f"- Source links: official docs or primary sources for {concept} behavior and limits.\n",
        "- Image/video assets:\n": (
            f"- Image/video assets: title/logo anchor, source captures, generated {concept} mechanism frames.\n"
        ),
        "- Visual punctuation cadence:\n": (
            "- Visual punctuation cadence: new visible proof, state, contrast, or callback every 6-10 seconds.\n"
        ),
        "- Reusable motion vocabulary:\n": (
            "- Reusable motion vocabulary: hard cuts, punch-ins, trace paths, highlight sweeps, warning strip, callback zoom.\n"
        ),
        "- Transition map:\n": (
            "- Transition map: hard cut for claim, punch-in for definition, match cut for state, smash cut for warning, final cut for callback.\n"
        ),
        "- Background bed:\n": "- Background bed: starts at 0:00, low and continuous, ducked under narration.\n",
        "- Voiceover ducking:\n": "- Voiceover ducking: lower bed during definition, mechanism, and warning lines.\n",
        "- Hits/stingers:\n": "- Hits/stingers: hook, output reveal, warning contrast, and final callback.\n",
        "- Ticks/whooshes:\n": "- Ticks/whooshes: input trace, state build, highlight sweep, and checklist reveals.\n",
        "- Risers/dropouts:\n": "- Risers/dropouts: riser before warning, sub-1-second dropout before the practical rule.\n",
        "- 0:00-0:05: Open with the claim and name the consequence.\n": (
            f"- 0:00-0:05: {concept} looks simple until {terms} reveal the hidden mechanism.\n"
        ),
        "- 0:05-0:15: Define the concept in one compressed sentence.\n": (
            f"- 0:05-0:15: In practice, {concept} is the part that turns input into visible state and output.\n"
        ),
        "- 0:15-0:25: Show the first mechanism step and why it matters.\n": (
            f"- 0:15-0:25: First, the input enters through {terms}, which decides what the system can change.\n"
        ),
        "- 0:25-0:35: Show the state change that makes the mechanism work.\n": (
            f"- 0:25-0:35: Then {concept} changes state, and that state is the difference between a label and a system.\n"
        ),
        "- 0:35-0:45: Prove the practical output with a concrete example.\n": (
            f"- 0:35-0:45: The proof is the output: you can see {concept} produce a result, not just a diagram.\n"
        ),
        "- 0:45-0:55: Contrast the failure path with the controlled path.\n": (
            f"- 0:45-0:55: Without control, {concept} drifts into the failure path; with checks, it stays usable.\n"
        ),
        "- 0:55-1:05: Give the rule of thumb viewers can reuse.\n": (
            f"- 0:55-1:05: The reusable rule is to name the trigger, the control, the proof, and the tradeoff.\n"
        ),
        "- 1:05-1:10: Callback to the hook and close on the practical rule.\n": (
            f"- 1:05-1:10: So {concept} is not magic; it is visible state movement you can test.\n"
        ),
        "- Density:\n": "- Density: each beat defines, proves, contrasts, warns, or callbacks; no filler setup.\n",
        "- Joke/claim cadence:\n": "- Joke/claim cadence: one clear claim or reversal per beat, with jokes only when they explain the mechanism.\n",
        "- Setup/payoff:\n": f"- Setup/payoff: {concept} starts as a compressed claim and pays off as a visible control rule.\n",
        "- Final callback:\n": f"- Final callback: return to the opening {concept} claim and state the practical rule.\n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def render_brief(args: argparse.Namespace) -> str:
    text = load_template("brief-template.md")
    promise = args.promise or f"Explain {args.title} with one clear mechanism, one practical example, and one limitation."
    replacements = {
        "<Title>": args.title,
        "Promise:\n": f"Promise: {promise}\n",
        "Audience:\n": f"Audience: {args.audience}\n",
        "Format:\n": f"Format: {args.format}\n",
        "Runtime:\n": f"Runtime: {args.runtime}\n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = replace_template_rows(text, concept_rows(args, promise))
    text = fill_brief_sections(text, args, promise)
    return replace_voiceover_block(text, args, promise)


def render_design_note(args: argparse.Namespace) -> str:
    concept = sanitize_cell(concept_name(args.title))
    terms = sanitize_cell(mechanism_terms(args.title, args.promise))
    return f"""# {args.title} Design Note

## Concept Claim

{args.promise or f"{args.title} can be explained as a concrete technical mechanism with inputs, state changes, outputs, and a limitation."}

## Chosen Visual Metaphor

Describe the mechanism as visible state movement rather than a generic icon montage.

## Rejected Metaphors

- Decorative logo storm: does not prove the mechanism.
- Generic brain/magic imagery: implies behavior the system does not have.
- Text-only slides: depend too much on narration.

## Visual Vocabulary

- Input/source surface: docs, code, UI, or terminal evidence that introduces {concept}.
- Mechanism/state surface: diagram or structured layout showing {terms}.
- Proof/output surface: concrete result that changes after the {concept} mechanism runs.
- Warning or tradeoff surface: failure, stale state, cost, overload, or limitation path.
- Final callback surface: compact {concept} system view plus one practical rule.

## Timing Contract

Use at least 8 beats, with one visible idea change every 6-10 seconds and a callback in the final beat.
"""


def render_storyboard(args: argparse.Namespace) -> str:
    concept = sanitize_cell(concept_name(args.title))
    terms = sanitize_cell(mechanism_terms(args.title, args.promise))
    rows = [
        ("Cold claim and first proof visual", "Name the payoff", "Smash reveal", "Hit plus bed"),
        ("Definition", f"Show {concept} as a concrete object or state", "Punch-in", "Voiceover duck"),
        ("Input", f"Source enters the {concept} system: {terms}", "Slide or trace", "Tick accents"),
        ("Core mechanism", f"{concept} state changes visibly", "Flow trace", "Whoosh"),
        ("Output", f"Result appears from the {concept} mechanism", "Type-on or pop", "Light hit"),
        ("Contrast", f"Uncontrolled {concept} failure versus controlled mitigation path", "Split screen", "Riser"),
        ("Limitation", f"Warning or failure mode for {concept}", "Glitch/dropout", "Brief dropout"),
        ("Callback", f"Full {concept} mechanism summary", "Zoom out", "Final tail"),
    ]
    ranges = scaled_beat_ranges(args.runtime, len(rows))
    body = "\n".join(
        f"| s{index + 1:02d} | b{index + 1:02d} | {ranges[index]} | {shot} | {mechanism} | {motion} | {audio} |"
        for index, (shot, mechanism, motion, audio) in enumerate(rows)
    )
    return f"""# {args.title} Storyboard

| Scene ID | Beat ID | Time | Shot | Mechanism | Motion | Audio |
| --- | --- | --- | --- | --- | --- | --- |
{body}
"""


def render_production_notes(args: argparse.Namespace, project_id: str, root: Path) -> str:
    concept = sanitize_cell(concept_name(args.title))
    promise = args.promise or f"{concept} can be explained as input, state, output, and tradeoff."
    terms = sanitize_cell(mechanism_terms(args.title, promise))
    duration_seconds = create_concept_renderer.seconds(args.runtime)
    skill_path = args.skill_path or default_skill_path(root)
    text = load_template("production-notes-template.md")
    text = text.replace("<Project Title>", args.title)
    text = text.replace("{{SKILL_PATH}}", skill_path)
    text = text.replace("Concept claim:\n", f"Concept claim: {promise}\n")
    text = text.replace(
        "Chosen visual metaphor:\n",
        f"Chosen visual metaphor: {concept} as visible state movement through {terms}.\n",
    )
    text = text.replace(
        "Rejected metaphors:\n",
        "Rejected metaphors: decorative logo storm, generic magic imagery, and text-only slides.\n",
    )
    text = text.replace(
        "Visual vocabulary:\n",
        f"Visual vocabulary: source/input surface, {concept} state surface, proof/output surface, warning path, final callback.\n",
    )
    text = text.replace(
        "Timing contract:\n",
        f"Timing contract: 8 beats over {duration_seconds:g}s, one visible change every 6-10 seconds, final callback visible.\n",
    )
    text = text.replace("Brief:\n", "Brief: source/brief.md\n")
    text = text.replace("Pattern blueprint:\n", "Pattern blueprint: source/pattern-blueprint.json and source/pattern-blueprint.md\n")
    text = text.replace("Source package:\n", "Source package: source/source-package.json\n")
    text = text.replace("Shot contract:\n", "Shot contract: source/shot-contract.json\n")
    text = text.replace("Asset manifest:\n", "Asset manifest: source/asset-manifest.json\n")
    text = text.replace("Composition plan:\n", "Composition plan: source/composition-plan.json\n")
    text = text.replace("Transition plan:\n", "Transition plan: source/transition-plan.json\n")
    text = text.replace("Renderer/storyboard:\n", "Renderer/storyboard: src/index.html and src/storyboard.md\n")
    text = text.replace("Audio:\n", "Audio: artifacts/audio/voiceover-bed-sfx-plan.md or final mix assets\n")
    text = text.replace(
        "Voiceover cues:\n",
        "Voiceover cues: artifacts/audio/voiceover-cues.json; optional SRT/CSV from extract_voiceover_cues.py\n",
    )
    text = text.replace("Final MP4:\n", f"Final MP4: artifacts/videos/{project_id}.mp4\n")
    text = text.replace("Silent preview:\n", f"Silent preview: artifacts/videos/{project_id}-silent-preview.mp4 optional\n")
    text = text.replace("Contact sheet:\n", "Contact sheet: artifacts/reviews/contact-sheet.jpg\n")
    text = text.replace("Motion report:\n", "Motion report: artifacts/reviews/motion-report.json\n")
    text = text.replace("Audio report:\n", "Audio report: artifacts/reviews/audio-report.json\n")
    text = text.replace("Renderer contract report:\n", "Renderer contract report: artifacts/reviews/renderer-contract.json\n")
    text = text.replace("Readiness score:\n", "Readiness score: artifacts/reviews/readiness-score.json\n")
    text = text.replace("Review reports:\n", "Review reports: artifacts/reviews/\n")
    text = text.replace("Visual review:\n", "Visual review: artifacts/reviews/visual-review.json\n")
    text = text.replace(
        "Visual contract report:\n",
        "Visual contract report: artifacts/reviews/asset-composition-validation.json\n",
    )
    text = text.replace(
        f'uv run --script {skill_path}/scripts/select_video_patterns.py --title "What Is X?" --runtime 1:10 --output source/pattern-blueprint.json --json',
        f"uv run --script {skill_path}/scripts/select_video_patterns.py "
        f"--title {quote_arg(args.title)} --promise {quote_arg(promise)} "
        f"--format {quote_arg(args.format)} --runtime {quote_arg(args.runtime)} "
        "--output source/pattern-blueprint.json --json",
    )
    text = text.replace("Required states:\n", "Required states: `window.renderConceptFrame` must return the fields below.\n")
    text = text.replace("Core mechanism visible:\n", "Core mechanism visible: `visibleMechanismCount` stays above zero in sampled states.\n")
    text = text.replace("Final callback visible:\n", "Final callback visible: final sampled state reports `finalCallbackVisible=true`.\n")
    text = text.replace("Audio present:\n", "Audio present: final MP4 contains an audio stream or final mix track.\n")
    text = text.replace("artifacts/videos/final.mp4", f"artifacts/videos/{project_id}.mp4")
    text = text.replace(
        "--expect-fps 30 --require-audio",
        f"--expect-fps 30 --expect-duration {duration_seconds:g} --duration-tolerance 1 --require-audio",
    )
    text = text.replace(
        "--design-note source/design-note.md --renderer src/index.html",
        "--design-note source/design-note.md --production-notes source/production-notes.md "
        "--package-manifest source/package-manifest.json --renderer src/index.html",
    )
    text = text.replace(
        "--require-audio --require-design-note --require-renderer",
        "--require-audio --require-design-note --require-production-notes "
        "--require-package-manifest --require-renderer",
    )
    text = text.replace("Renderer contract passed:\n", "Renderer contract passed: pending validation\n")
    text = text.replace("Readiness score:\n", "Readiness score: pending validation\n")
    text = text.replace("Contact sheet inspected:\n", "Contact sheet inspected: pending visual review\n")
    text = text.replace("Asset quality check:\n", "Asset quality check: pending ready-asset validation\n")
    text = text.replace("Composition check:\n", "Composition check: pending per-scene frame review\n")
    text = text.replace(
        "Renderer asset-binding check:\n",
        "Renderer asset-binding check: pending DOM and renderer-state ID coverage\n",
    )
    text = text.replace("Legibility check:\n", "Legibility check: pending contact-sheet review\n")
    text = text.replace("Beat coverage check:\n", "Beat coverage check: pending renderer coverage report\n")
    text = text.replace("Visual mechanism check:\n", "Visual mechanism check: pending source-bound mechanism review\n")
    text = text.replace("Pacing/transition check:\n", "Pacing/transition check: pending motion report\n")
    text = text.replace("Source-binding check:\n", "Source-binding check: pending source plan review\n")
    text = text.replace("Audio sync check:\n", "Audio sync check: pending audio report\n")
    text = text.replace("Motion/quality checks passed:\n", "Motion/quality checks passed: pending validation\n")
    text = text.replace("Known caveats:\n", "Known caveats: replace synthetic validation audio with final narration/music/SFX.\n")
    text = text.replace("--duration 70", f"--duration {duration_seconds:g}")
    text = text.replace("--expect-duration 70", f"--expect-duration {duration_seconds:g}")
    return text


def command_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def quote_arg(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def pattern_blueprint(args: argparse.Namespace) -> dict[str, object]:
    return select_video_patterns.select_blueprint(
        argparse.Namespace(
            title=args.title,
            promise=args.promise,
            requested_format=args.format,
            runtime=args.runtime,
            summary=select_video_patterns.DEFAULT_SUMMARY,
        )
    )


def scene_specs(args: argparse.Namespace) -> list[dict[str, str]]:
    concept = sanitize_cell(concept_name(args.title))
    return [
        {
            "sceneJob": "Hook with immediate proof",
            "viewerTask": f"Recognize the {concept} claim and inspect one source proof",
            "compositionChoice": "centered hero",
            "armature": "triangular hierarchy",
            "focal": f"{concept} consequence proof",
            "assetKind": "screenshot",
            "assetRole": "source proof",
            "producerSkill": "playwright",
            "outputSuffix": "png",
        },
        {
            "sceneJob": "Compressed definition",
            "viewerTask": f"Connect the {concept} label to its concrete parts",
            "compositionChoice": "asymmetric editorial",
            "armature": "golden root split",
            "focal": f"{concept} definition mechanism",
            "assetKind": "diagram",
            "assetRole": "definition diagram",
            "producerSkill": "mermaid-animated-svg",
            "outputSuffix": "svg",
        },
        {
            "sceneJob": "Mechanism input",
            "viewerTask": f"Trace the input entering the {concept} system",
            "compositionChoice": "flow spine",
            "armature": "horizontal flow spine",
            "focal": f"{concept} input route",
            "assetKind": "diagram",
            "assetRole": "mechanism input",
            "producerSkill": "d3-animated-svg",
            "outputSuffix": "svg",
        },
        {
            "sceneJob": "Mechanism state change",
            "viewerTask": f"See which {concept} state changes and why",
            "compositionChoice": "radial hub",
            "armature": "radial state loop",
            "focal": f"{concept} state transition",
            "assetKind": "diagram",
            "assetRole": "state mechanism",
            "producerSkill": "d3-animated-svg",
            "outputSuffix": "svg",
        },
        {
            "sceneJob": "Practical output proof",
            "viewerTask": f"Inspect the real output produced by {concept}",
            "compositionChoice": "golden root split",
            "armature": "dominant proof surface with detail rail",
            "focal": f"{concept} output evidence",
            "assetKind": "ui-capture",
            "assetRole": "output proof",
            "producerSkill": "playwright",
            "outputSuffix": "png",
        },
        {
            "sceneJob": "Failure versus control contrast",
            "viewerTask": f"Compare uncontrolled and controlled {concept} behavior",
            "compositionChoice": "split screen",
            "armature": "axis-locked bilateral split",
            "focal": f"{concept} failure-control contrast",
            "assetKind": "diagram",
            "assetRole": "contrast mechanism",
            "producerSkill": "d3-animated-svg",
            "outputSuffix": "svg",
        },
        {
            "sceneJob": "Reusable rule",
            "viewerTask": f"Scan and retain the practical {concept} rule",
            "compositionChoice": "modular board",
            "armature": "four-cell orthogonal grid",
            "focal": f"{concept} rule sequence",
            "assetKind": "diagram",
            "assetRole": "rule summary",
            "producerSkill": "mermaid-animated-svg",
            "outputSuffix": "svg",
        },
        {
            "sceneJob": "Callback and system resolve",
            "viewerTask": f"Reconnect the opening claim to the full {concept} mechanism",
            "compositionChoice": "diagonal armature",
            "armature": "low-left to high-right resolution path",
            "focal": f"complete {concept} system",
            "assetKind": "diagram",
            "assetRole": "callback system",
            "producerSkill": "d3-animated-svg",
            "outputSuffix": "svg",
        },
    ]


def range_seconds(value: str) -> tuple[float, float]:
    def parse_token(token: str) -> float:
        clean = token.strip().removesuffix("s")
        if ":" in clean:
            minutes, seconds = clean.split(":", 1)
            return float(minutes) * 60 + float(seconds)
        return float(clean)

    start, end = value.split("-", 1)
    return parse_token(start), parse_token(end)


def build_source_package(args: argparse.Namespace, project_id: str) -> dict[str, object]:
    concept = sanitize_cell(concept_name(args.title))
    ranges = scaled_beat_ranges(args.runtime, len(scene_specs(args)))
    return {
        "schemaVersion": 1,
        "videoId": project_id,
        "title": args.title,
        "promise": args.promise,
        "audience": args.audience,
        "status": "planned",
        "sourcePolicy": "Replace every planned item with a concrete source URL, exact quote/fact paraphrase, rights decision, and verification result before route completion.",
        "facts": [
            {
                "id": f"f{index:02d}",
                "beatId": f"b{index:02d}",
                "time": ranges[index - 1],
                "claim": f"Freeze the exact {concept} claim required for {spec['sceneJob'].lower()}.",
                "sourceUrl": None,
                "rightsStatus": "unverified",
                "verificationStatus": "planned",
            }
            for index, spec in enumerate(scene_specs(args), start=1)
        ],
    }


def build_shot_contract(args: argparse.Namespace, project_id: str) -> dict[str, object]:
    ranges = scaled_beat_ranges(args.runtime, len(scene_specs(args)))
    return {
        "version": 1,
        "videoId": project_id,
        "shots": [
            {
                "id": f"s{index:02d}",
                "beatId": f"b{index:02d}",
                "time": ranges[index - 1],
                "job": spec["sceneJob"],
                "viewerTask": spec["viewerTask"],
                "assetIds": [f"a{index:02d}-{slugify(spec['assetRole'])}"],
                "sourceFactIds": [f"f{index:02d}"],
                "status": "planned",
            }
            for index, spec in enumerate(scene_specs(args), start=1)
        ],
    }


def build_transition_plan(args: argparse.Namespace, project_id: str) -> dict[str, object]:
    concept = sanitize_cell(concept_name(args.title))
    specs = scene_specs(args)
    ranges = scaled_beat_ranges(args.runtime, len(specs))
    families = [
        "match cut axis",
        "persistent object",
        "color handoff",
        "spatial portal reveal",
        "match cut axis",
        "persistent object flight",
        "hard cut",
    ]
    transitions: list[dict[str, object]] = []
    for index in range(1, len(specs)):
        _, cut_time = range_seconds(ranges[index - 1])
        from_scene = f"s{index:02d}"
        to_scene = f"s{index + 1:02d}"
        transitions.append(
            {
                "id": f"t{index:02d}",
                "seamId": f"{from_scene}__{to_scene}",
                "fromScene": from_scene,
                "toScene": to_scene,
                "start": max(0.0, round(cut_time - 0.35, 3)),
                "duration": 0.7,
                "family": families[index - 1],
                "semanticPurpose": f"Carry the viewer from {specs[index - 1]['sceneJob'].lower()} into {specs[index]['sceneJob'].lower()} without resetting the {concept} mental model.",
                "stateChange": f"The persistent {concept} state token changes from {specs[index - 1]['assetRole']} to {specs[index]['assetRole']}.",
                "attentionHandoff": "The outgoing focal edge lands on the incoming scene's primary axis and focal asset.",
                "styleContinuity": "Palette, type scale, stroke weight, and source-native edge treatment persist through the seam.",
                "alignmentRule": "Outgoing focal center and incoming focal axis share a grid line at the midpoint.",
                "edgeRule": "Preserve the declared source-native or diagram edge policy without introducing decorative masks.",
                "boxPaddingRule": "Preserve each scene's declared boxModel; transition masks do not add hidden internal padding.",
                "grayscaleHierarchyRule": "Primary, secondary, and background roles stay distinct through outgoing, bridge, and incoming states.",
                "grayscaleHierarchy": [
                    {"level": 0, "role": "primary focal", "grayHex": "#f2f2f2"},
                    {"level": 1, "role": "secondary proof", "grayHex": "#a8a8a8"},
                    {"level": 2, "role": "background structure", "grayHex": "#333333"},
                ],
                "genericMotionRejected": "A generic fade or slide would hide the semantic state handoff and reset attention.",
                "surprise": f"The outgoing {specs[index - 1]['assetRole']} becomes the incoming {specs[index]['assetRole']}.",
                "outgoingState": f"{specs[index - 1]['focal']} is settled and the handoff edge is visible.",
                "bridgeAction": "The persistent state token crosses the shared axis while support detail clears.",
                "incomingState": f"{specs[index]['focal']} receives the token and becomes dominant.",
                "compositionShift": f"{specs[index - 1]['compositionChoice']} resolves into {specs[index]['compositionChoice']}.",
                "colorShift": "Semantic accent moves with the persistent token; hierarchy remains stable.",
                "cameraShift": "Use only the minimum reframe needed to land the incoming focal axis.",
                "spaceShift": f"{specs[index - 1]['armature']} gives way to {specs[index]['armature']}.",
                "validationFrames": [
                    {
                        "time": "pre-cut",
                        "target": f"{from_scene} focal and persistent state token",
                        "passCriterion": "Outgoing focal hierarchy and token are both visible and unclipped.",
                    },
                    {
                        "time": "transition midpoint",
                        "target": f"{from_scene} to {to_scene} shared axis",
                        "passCriterion": "Persistent token remains visible and attention crosses the declared axis.",
                    },
                    {
                        "time": "post-cut",
                        "target": f"{to_scene} incoming focal",
                        "passCriterion": "Incoming focal owns the first eye landing without overlap or clipping.",
                    },
                ],
                "validationChecks": [
                    {
                        "method": "three-frame-seam-review",
                        "target": f"{from_scene}__{to_scene}",
                        "passCriterion": "Before, midpoint, and after frames prove persistence and the attention handoff.",
                    }
                ],
            }
        )
    return {
        "version": 1,
        "videoId": project_id,
        "persistentElement": {
            "name": f"{concept} state token",
            "role": "viewer-tracked mechanism state",
            "states": [spec["assetRole"] for spec in specs],
        },
        "transitions": transitions,
    }


def build_asset_manifest(args: argparse.Namespace, project_id: str) -> dict[str, object]:
    concept = sanitize_cell(concept_name(args.title))
    assets: list[dict[str, object]] = []
    for index, spec in enumerate(scene_specs(args), start=1):
        asset_id = f"a{index:02d}-{slugify(spec['assetRole'])}"
        scene_id = f"s{index:02d}"
        beat_id = f"b{index:02d}"
        suffix = spec["outputSuffix"]
        captured = spec["producerSkill"] == "playwright"
        origin_uri = (
            f"https://replace.invalid/{slugify(concept)}/{beat_id}"
            if captured
            else f"generation-contract:source/design-note.md#{beat_id}-{slugify(spec['assetRole'])}"
        )
        assets.append(
            {
                "id": asset_id,
                "kind": spec["assetKind"],
                "claim": f"Show {spec['focal']} as the concrete proof for {spec['sceneJob'].lower()}.",
                "output": f"artifacts/images/{asset_id}.{suffix}",
                "sha256": None,
                "origin": {
                    "type": "captured" if captured else "generated",
                    "uri": origin_uri,
                    "rightsStatus": "official-source" if captured else "project-generated",
                    "attribution": f"Replace with the exact official source attribution for {concept}." if captured else "",
                },
                "producer": {
                    "skill": spec["producerSkill"],
                    "method": (
                        f"Capture the exact {concept} proof at the final crop with browser automation."
                        if captured
                        else f"Generate the {spec['assetRole']} from the frozen {concept} facts and composition contract."
                    ),
                    "report": f"artifacts/reviews/{asset_id}-validation.json",
                },
                "technical": {
                    "targetWidth": 1280 if captured else 960,
                    "targetHeight": 720 if captured else 540,
                    "aspectRatio": "16:9",
                    "maxUpscale": 1.0,
                    "crop": "Preserve the focal proof and declared safe area at the final 16:9 crop.",
                },
                "uses": [
                    {
                        "sceneId": scene_id,
                        "beatId": beat_id,
                        "role": spec["assetRole"],
                        "fit": "contain without cropping the focal proof or source labels",
                    }
                ],
                "status": "planned",
                "qualityChecks": [
                    "Inspect the asset at the final video crop and target resolution.",
                    "Verify the focal proof is legible without narration or placeholder labels.",
                    "Confirm provenance, rights, attribution, and output path before rendering.",
                    "Reject watermarks, accidental AI text, clipping, and visible compression damage.",
                ],
            }
        )
    return {
        "schemaVersion": 1,
        "videoId": project_id,
        "canvas": {"width": 1280, "height": 720, "aspectRatio": "16:9"},
        "skillRouting": [
            {
                "stage": "source",
                "skill": "source-to-video-director",
                "reason": "Freeze literal facts and shot IDs before visual interpretation.",
                "output": "source/source-package.json and source/shot-contract.json",
                "outputPaths": ["source/source-package.json", "source/shot-contract.json"],
                "proof": "artifacts/reviews/source-contract-validation.json",
                "status": "planned",
            },
            {
                "stage": "composition",
                "skill": "scene-composition-director",
                "reason": "Choose a focal hierarchy, armature, safe zones, and asset roles for every scene.",
                "output": "source/composition-plan.json",
                "outputPaths": ["source/composition-plan.json"],
                "proof": "artifacts/reviews/composition-plan-specialist-validation.json",
                "status": "planned",
            },
            {
                "stage": "transitions",
                "skill": "scene-transition-director",
                "reason": "Carry semantic state and attention across every adjacent scene boundary.",
                "output": "source/transition-plan.json",
                "outputPaths": ["source/transition-plan.json"],
                "proof": "artifacts/reviews/transition-plan-specialist-validation.json",
                "status": "planned",
            },
            {
                "stage": "asset-generation",
                "skill": "d3-animated-svg",
                "reason": "Build custom source-bound mechanism geometry and state motion.",
                "output": "artifacts/images/*.svg",
                "outputPaths": [
                    "artifacts/images/a03-mechanism-input.svg",
                    "artifacts/images/a04-state-mechanism.svg",
                    "artifacts/images/a06-contrast-mechanism.svg",
                    "artifacts/images/a08-callback-system.svg",
                ],
                "proof": "artifacts/reviews/asset-generation-validation.json",
                "status": "planned",
            },
            {
                "stage": "asset-generation",
                "skill": "mermaid-animated-svg",
                "reason": "Build conventional definition and rule diagrams with explicit semantic reveal order.",
                "output": "artifacts/images/a02-definition-diagram.svg and artifacts/images/a07-rule-summary.svg",
                "outputPaths": [
                    "artifacts/images/a02-definition-diagram.svg",
                    "artifacts/images/a07-rule-summary.svg",
                ],
                "proof": "artifacts/reviews/mermaid-assets-validation.json",
                "status": "planned",
            },
            {
                "stage": "asset-capture",
                "skill": "playwright",
                "reason": "Capture official UI, documentation, code, or output proof at the final crop.",
                "output": "artifacts/images/*.png",
                "outputPaths": [
                    "artifacts/images/a01-source-proof.png",
                    "artifacts/images/a05-output-proof.png",
                ],
                "proof": "artifacts/reviews/asset-capture-validation.json",
                "status": "planned",
            },
            {
                "stage": "renderer",
                "skill": "html-d3-anime-video-workflow",
                "reason": "Own deterministic browser frames, capture, encoding, and renderer-specific reports.",
                "output": "src/index.html and artifacts/videos/",
                "outputPaths": ["src/index.html", f"artifacts/videos/{project_id}.mp4"],
                "proof": "artifacts/reviews/renderer-route-validation.json",
                "status": "planned",
            },
        ],
        "assets": assets,
    }


def scene_object_bounds(scene_id: str, index: int) -> list[dict[str, object]]:
    layouts = [
        # Centered hero with a low support rail.
        ((0.22, 0.10, 0.56, 0.62), (0.28, 0.76, 0.44, 0.14)),
        # Asymmetric editorial split.
        ((0.08, 0.16, 0.54, 0.64), (0.68, 0.18, 0.24, 0.44)),
        # Horizontal mechanism flow with an upper proof key.
        ((0.16, 0.30, 0.68, 0.40), (0.08, 0.10, 0.30, 0.14)),
        # Radial center with a right-side state legend.
        ((0.27, 0.12, 0.48, 0.64), (0.78, 0.24, 0.16, 0.36)),
        # Dominant source proof plus narrow detail rail.
        ((0.06, 0.08, 0.68, 0.72), (0.79, 0.16, 0.15, 0.54)),
        # Bilateral comparison.
        ((0.05, 0.16, 0.44, 0.62), (0.53, 0.16, 0.42, 0.62)),
        # Modular board with a large upper-left rule cluster.
        ((0.08, 0.10, 0.52, 0.54), (0.62, 0.52, 0.30, 0.28)),
        # Diagonal resolve from lower-left proof to upper-right callback.
        ((0.07, 0.40, 0.54, 0.50), (0.64, 0.09, 0.28, 0.30)),
    ]
    focal, support = layouts[index - 1]
    return [
        {
            "id": f"{scene_id}-focal",
            "role": "focal",
            "x": focal[0],
            "y": focal[1],
            "width": focal[2],
            "height": focal[3],
        },
        {
            "id": f"{scene_id}-support",
            "role": "support",
            "x": support[0],
            "y": support[1],
            "width": support[2],
            "height": support[3],
        },
    ]


def build_composition_plan(args: argparse.Namespace) -> dict[str, object]:
    concept = sanitize_cell(concept_name(args.title))
    ranges = scaled_beat_ranges(args.runtime, len(scene_specs(args)))
    scenes: list[dict[str, object]] = []
    for index, spec in enumerate(scene_specs(args), start=1):
        scene_id = f"s{index:02d}"
        next_scene_id = f"s{index + 1:02d}" if index < len(scene_specs(args)) else None
        beat_id = f"b{index:02d}"
        asset_id = f"a{index:02d}-{slugify(spec['assetRole'])}"
        scenes.append(
            {
                "id": scene_id,
                "title": spec["sceneJob"],
                "duration": ranges[index - 1],
                "beatIds": [beat_id],
                "assetIds": [asset_id],
                "sourceAnchors": [concept, spec["assetRole"]],
                "sceneJob": spec["sceneJob"],
                "viewerTask": spec["viewerTask"],
                "compositionChoice": spec["compositionChoice"],
                "rejectedAlternatives": ["text-only slide", "generic repeated card wall"],
                "choiceRationale": (
                    f"The {spec['compositionChoice']} makes {spec['focal']} dominant while the supporting proof remains inspectable."
                ),
                "focal": spec["focal"],
                "roles": {
                    "focal": spec["assetRole"],
                    "support": "source anchor and mechanism context",
                    "handoff": "persistent trace or focal edge aligned to the next scene",
                },
                "armature": spec["armature"],
                "alignmentGrid": "12-column frame grid with an 8-pixel baseline and named focal axis",
                "armatureAnchors": [
                    f"{spec['focal']} locked to the primary focal axis",
                    "support proof aligned to the secondary column and shared baseline",
                ],
                "edgePolicy": "Source-native capture edges; diagram geometry follows the declared visual system.",
                "cornerPolicy": "Use one intentional corner policy; preserve literal source-media corners.",
                "boxInteriorPolicy": "Use spacing only when it supports the chosen armature and legibility.",
                "boxModel": {
                    "internalPaddingPx": 16,
                    "contentFlushToBounds": False,
                    "separation": "external gutters and role-based spacing",
                },
                "grayscaleHierarchy": [
                    {"level": 0, "role": "primary focal", "grayHex": "#f2f2f2"},
                    {"level": 1, "role": "secondary proof", "grayHex": "#a8a8a8"},
                    {"level": 2, "role": "background structure", "grayHex": "#333333"},
                ],
                "layout": f"Place {spec['focal']} on the governing {spec['armature']}; keep support on the secondary axis.",
                "hierarchy": "Primary proof occupies at least 25 percent of the frame; support stays visibly subordinate.",
                "density": "One focal proof, one support group, and one transition-ready handoff element.",
                "safeZones": {
                    "frameMargin": "5 percent on every edge",
                    "captionZone": "bottom 12 percent only when captions are enabled",
                    "protectedRegion": "focal proof and source labels remain unobstructed",
                },
                "textRegion": {
                    "placement": "secondary support rail outside the focal proof bounds",
                    "maxLineCharacters": 42,
                    "contrastTreatment": "Meet readable foreground/background contrast without covering source evidence.",
                    "clearance": "Keep at least one grid gutter from focal geometry, captions, and crop zones.",
                },
                "depthLayers": [
                    "background tonal field or source context",
                    "midground mechanism and supporting proof",
                    "foreground focal asset and transition handoff",
                ],
                "objectBounds": scene_object_bounds(scene_id, index),
                "motionPhases": [
                    {
                        "name": "entrance",
                        "cue": "scene entry",
                        "visualChange": "Reveal the focal asset before supporting labels or traces.",
                        "motionVerb": "reveal",
                    },
                    {
                        "name": "hold",
                        "cue": "readable proof clause",
                        "visualChange": "Hold the complete focal proof long enough for labels and state to be inspected.",
                        "motionVerb": "hold",
                    },
                    {
                        "name": "emphasis",
                        "cue": "voiceover mechanism clause",
                        "visualChange": "Change or accent the focal asset state so the technical claim becomes visible.",
                        "motionVerb": "emphasize",
                    },
                    {
                        "name": "exit",
                        "cue": "final clause and handoff",
                        "visualChange": "Align the persistent element with the next scene or settle the final callback.",
                        "motionVerb": "handoff",
                    },
                ],
                "reducedMotion": "Preserve the entrance, readable hold, emphasized state, and final handoff as four static keyframes.",
                "outgoingSeam": {
                    "seamId": f"{scene_id}__{next_scene_id}" if next_scene_id else "end",
                    "fromScene": scene_id,
                    "toScene": next_scene_id,
                    "persistentElement": f"{concept} state token",
                    "attentionHandoff": "Focal edge and semantic accent land on the incoming primary axis.",
                    "beforeState": f"{spec['focal']} is settled and readable.",
                    "afterState": (
                        f"{next_scene_id} receives the persistent token as its focal proof."
                        if next_scene_id
                        else "The full mechanism remains settled for the final callback."
                    ),
                    "type": "transition" if next_scene_id else "end",
                },
                "rendererHandoff": "Renderer must expose sceneId, compositionId, activeAssetIds, and visible source-proof IDs.",
                "validationChecks": [
                    {
                        "method": "full-resolution-frame-review",
                        "target": f"{scene_id} focal asset and safe areas",
                        "passCriterion": "Focal proof is large, legible, unclipped, and free of overlapping text.",
                    },
                    {
                        "method": "renderer-state-and-dom-review",
                        "target": f"{scene_id} asset and composition markers",
                        "passCriterion": "Declared asset ID and composition ID are visible and match the active beat.",
                    },
                ],
                "validationContract": {
                    "alignment": "Major objects remain locked to the declared 12-column grid, focal axis, and baseline.",
                    "safeZones": "Focal proof, source labels, and captions remain inside the declared frame-safe regions.",
                    "edgePolicy": "Source-native edges and the declared diagram edge policy survive the final crop.",
                    "boxPadding": "Any internal spacing follows the declared boxModel and never hides or shrinks proof.",
                    "grayscaleHierarchy": "Primary, secondary, and background roles remain distinct in grayscale.",
                    "focalHierarchy": "The focal object occupies at least five percent of frame area and wins the first eye landing.",
                    "verificationArtifacts": [
                        f"artifacts/reviews/frames/{scene_id}-settle.png",
                        "artifacts/reviews/renderer-contract.json",
                    ],
                },
                "risks": ["source proof may need a tighter crop", "support labels may compete with the focal asset"],
            }
        )
    return {
        "version": 1,
        "format": "1280x720",
        "videoDirection": {
            "sourceAnchors": [concept],
            "paletteTypeSource": "Use the project brief, supplied brand assets, or a declared original visual system.",
            "alignmentMode": "12-column frame grid plus scene-specific armatures and shared baselines.",
            "edgeCornerPolicy": "Choose one coherent policy and preserve source-native media geometry.",
            "safeZones": "Keep focal proof, captions, and source labels inside the declared frame-safe regions.",
            "captionPolicy": "Reserve a caption band only when narration captions are part of the deliverable.",
            "rhythm": "Vary armature by scene job while preserving palette, type, spacing, and persistent semantic roles.",
            "heldScenes": ["s05 practical output proof", "s08 callback resolve"],
            "negativeList": [
                "generic repeated card wall",
                "decorative motion with no state change",
                "tiny proof assets stretched beyond their source resolution",
                "text covering source UI or focal evidence",
            ],
        },
        "scenes": scenes,
    }


def build_visual_review(
    project_id: str,
    asset_manifest_text: str,
    composition_plan_text: str,
    composition_plan: dict[str, object],
) -> dict[str, object]:
    scenes = composition_plan.get("scenes", [])
    return {
        "schemaVersion": 1,
        "videoId": project_id,
        "inputDigests": {
            "assetManifestSha256": hashlib.sha256(asset_manifest_text.encode("utf-8")).hexdigest(),
            "compositionPlanSha256": hashlib.sha256(composition_plan_text.encode("utf-8")).hexdigest(),
        },
        "reviewer": "unassigned production reviewer",
        "reviewMethod": "Inspect the contact sheet, full-resolution scene frames, transition midpoints, and full-speed playback.",
        "contactSheet": "artifacts/reviews/contact-sheet.jpg",
        "candidateVideo": {"path": f"artifacts/videos/{project_id}.mp4", "sha256": None},
        "fullSpeedPlayback": {"reviewed": False, "notes": "Complete after the first encoded review render."},
        "scenes": [
            {
                "sceneId": scene.get("id"),
                "compositionId": scene.get("id"),
                "assetIds": scene.get("assetIds", []),
                "evidenceFrames": [],
                "checks": {name: "pending" for name in [
                    "focalClarity",
                    "safeAreas",
                    "clipping",
                    "overlap",
                    "contrast",
                    "typography",
                    "silentComprehension",
                    "sourceProof",
                ]},
                "silentTest": {
                    "durationSeconds": 3,
                    "object": "Pending silent-frame object identification.",
                    "action": "Pending silent-frame action identification.",
                    "result": "Pending silent-frame result identification.",
                },
                "finding": "Pending full-resolution visual inspection.",
                "correction": "Pending correction and rerender decision.",
                "status": "pending",
            }
            for scene in scenes
            if isinstance(scene, dict)
        ],
        "transitions": [],
        "unresolvedBlockers": ["Complete scene and transition visual inspection after rendering."],
        "overallStatus": "pending",
    }


def default_skill_path(command_root: Path | None = None) -> str:
    cwd = (command_root or Path.cwd()).resolve()
    try:
        return command_path(SKILL_DIR.resolve().relative_to(cwd))
    except ValueError:
        try:
            return command_path(Path(os.path.relpath(SKILL_DIR.resolve(), cwd)))
        except ValueError:
            return command_path(SKILL_DIR.resolve())


def build_manifest(args: argparse.Namespace, project_id: str, root: Path) -> dict[str, object]:
    skill_path = args.skill_path or default_skill_path(root)
    rel_video_path = f"artifacts/videos/{project_id}.mp4"
    brief_path = "source/brief.md"
    design_path = "source/design-note.md"
    production_notes_path = "source/production-notes.md"
    package_manifest_path = "source/package-manifest.json"
    pattern_blueprint_json_path = "source/pattern-blueprint.json"
    pattern_blueprint_md_path = "source/pattern-blueprint.md"
    asset_manifest_path = "source/asset-manifest.json"
    composition_plan_path = "source/composition-plan.json"
    visual_review_path = "artifacts/reviews/visual-review.json"
    visual_contract_report_path = "artifacts/reviews/asset-composition-validation.json"
    renderer_path = "src/index.html"
    renderer_report_path = "artifacts/reviews/renderer-contract.json"
    render_state_path = "artifacts/reviews/render-state.json"
    video_path = rel_video_path
    contact_sheet_path = "artifacts/reviews/contact-sheet.jpg"
    quality_report_path = "artifacts/reviews/quality-report.json"
    motion_report_path = "artifacts/reviews/motion-report.json"
    capture_manifest_path = "artifacts/reviews/capture-manifest.json"
    audio_report_path = "artifacts/reviews/audio-report.json"
    readiness_report_path = "artifacts/reviews/readiness-score.json"
    style_fidelity_report_path = "artifacts/reviews/style-fidelity.json"
    voiceover_cues_json_path = "artifacts/audio/voiceover-cues.json"
    voiceover_cues_srt_path = "artifacts/audio/voiceover-cues.srt"
    voiceover_cues_csv_path = "artifacts/audio/voiceover-cues.csv"
    duration_seconds = create_concept_renderer.seconds(args.runtime)
    return {
        "projectId": project_id,
        "title": args.title,
        "format": args.format,
        "runtime": args.runtime,
        "toolchain": build_asset_manifest(args, project_id)["skillRouting"],
        "contracts": {
            "sourcePackage": "source/source-package.json",
            "shotContract": "source/shot-contract.json",
            "assetManifest": asset_manifest_path,
            "compositionPlan": composition_plan_path,
            "transitionPlan": "source/transition-plan.json",
            "visualReview": visual_review_path,
            "validationReport": visual_contract_report_path,
        },
        "paths": {
            "brief": "source/brief.md",
            "sourcePackage": "source/source-package.json",
            "shotContract": "source/shot-contract.json",
            "designNote": "source/design-note.md",
            "productionNotes": "source/production-notes.md",
            "patternBlueprintJson": pattern_blueprint_json_path,
            "patternBlueprintMarkdown": pattern_blueprint_md_path,
            "assetManifest": asset_manifest_path,
            "compositionPlan": composition_plan_path,
            "transitionPlan": "source/transition-plan.json",
            "visualReview": visual_review_path,
            "visualContractValidation": visual_contract_report_path,
            "renderer": "src/index.html",
            "storyboard": "src/storyboard.md",
            "voiceoverCuesJson": voiceover_cues_json_path,
            "voiceoverCuesSrt": voiceover_cues_srt_path,
            "voiceoverCuesCsv": voiceover_cues_csv_path,
            "video": rel_video_path,
            "contactSheet": "artifacts/reviews/contact-sheet.jpg",
            "rendererValidation": renderer_report_path,
            "renderState": render_state_path,
            "qualityReport": "artifacts/reviews/quality-report.json",
            "motionReport": "artifacts/reviews/motion-report.json",
            "captureManifest": "artifacts/reviews/capture-manifest.json",
            "audioReport": "artifacts/reviews/audio-report.json",
            "readinessScore": "artifacts/reviews/readiness-score.json",
            "styleFidelity": style_fidelity_report_path,
            "packageValidation": "artifacts/reviews/package-validation.json",
        },
        "commands": {
            "runtimePreflight": (
                f"uv run --script {skill_path}/scripts/check_runtime_tools.py "
                "--require-render-tools --json"
            ),
            "selectPatterns": (
                f"uv run --script {skill_path}/scripts/select_video_patterns.py "
                f"--title {quote_arg(args.title)} "
                f"--promise {quote_arg(args.promise)} "
                f"--format {quote_arg(args.format)} "
                f"--runtime {quote_arg(args.runtime)} "
                f"--output {pattern_blueprint_json_path} --json"
            ),
            "briefValidation": (
                f"uv run --script {skill_path}/scripts/check_video_brief.py {brief_path} "
                "--require-voiceover --require-source-links --json"
            ),
            "visualContractValidation": (
                f"uv run --script {skill_path}/scripts/check_visual_contract.py "
                f"--asset-manifest {asset_manifest_path} --composition-plan {composition_plan_path} "
                f"--visual-review {visual_review_path} --video {video_path} --brief {brief_path} --project-root . "
                "--min-assets 8 --min-scenes 8 --require-ready-assets "
                "--require-specialist-routing --require-source-routing --require-reviewed-scenes "
                f"--output {visual_contract_report_path} --json"
            ),
            "extractVoiceoverCues": (
                f"uv run --script {skill_path}/scripts/extract_voiceover_cues.py {brief_path} "
                f"--format json --min-cues 8 --expect-duration {duration_seconds:g} --duration-tolerance 1 "
                f"--require-beat-match --output {voiceover_cues_json_path}"
            ),
            "extractVoiceoverCuesSrt": (
                f"uv run --script {skill_path}/scripts/extract_voiceover_cues.py {brief_path} "
                f"--format srt --min-cues 8 --expect-duration {duration_seconds:g} --duration-tolerance 1 "
                f"--require-beat-match --output {voiceover_cues_srt_path}"
            ),
            "extractVoiceoverCuesCsv": (
                f"uv run --script {skill_path}/scripts/extract_voiceover_cues.py {brief_path} "
                f"--format csv --min-cues 8 --expect-duration {duration_seconds:g} --duration-tolerance 1 "
                f"--require-beat-match --output {voiceover_cues_csv_path}"
            ),
            "styleFidelity": (
                f"uv run --script {skill_path}/scripts/score_style_fidelity.py "
                f"--brief {brief_path} --pattern-blueprint {pattern_blueprint_json_path} "
                f"--require-voiceover --require-pattern-blueprint --require-source-links "
                f"--output {style_fidelity_report_path} --json"
            ),
            "rendererValidation": (
                f"uv run --script {skill_path}/scripts/check_renderer_contract.py {renderer_path} "
                f"--brief {brief_path} --duration {duration_seconds:g} --require-all-brief-beats "
                f"--asset-manifest {asset_manifest_path} --composition-plan {composition_plan_path} "
                "--require-visual-ids "
                f"--output {renderer_report_path} --json"
            ),
            "renderVideo": (
                f"uv run --script {skill_path}/scripts/render_concept_video.py {renderer_path} {video_path} "
                f"--brief {brief_path} --require-all-brief-beats "
                f"--duration {duration_seconds:g} --fps 30 --capture-fps 12 --force --contact-sheet {contact_sheet_path} "
                f"--quality-report {quality_report_path} --motion-report {motion_report_path} "
                f"--capture-manifest {capture_manifest_path} "
                f"--render-state-report {render_state_path} --audio-report {audio_report_path} --json"
            ),
            "videoValidation": (
                f"uv run --script {skill_path}/scripts/check_video_artifact.py {video_path} "
                f"--expect-width 1280 --expect-height 720 --expect-fps 30 "
                f"--expect-duration {duration_seconds:g} --duration-tolerance 1 --require-audio "
                f"--audio-report {audio_report_path} --require-audio-report "
                f"--contact-sheet {contact_sheet_path} --quality-report {quality_report_path} "
                f"--motion-report {motion_report_path} "
                f"--capture-manifest {capture_manifest_path} --json"
            ),
            "scoreReadiness": (
                f"uv run --script {skill_path}/scripts/score_video_readiness.py "
                f"--require-source-links --brief {brief_path} --video {video_path} --renderer {renderer_path} "
                f"--renderer-report {renderer_report_path} --asset-manifest {asset_manifest_path} "
                f"--composition-plan {composition_plan_path} --visual-review {visual_review_path} "
                f"--quality-report {quality_report_path} --motion-report {motion_report_path} "
                f"--capture-manifest {capture_manifest_path} "
                f"--audio-report {audio_report_path} "
                f"--contact-sheet {contact_sheet_path} --visual-contract-report {visual_contract_report_path} "
                "--require-visual-contract-report --require-voiceover "
                f"--output {readiness_report_path} --json"
            ),
            "finalizeProductionNotes": (
                f"uv run --script {skill_path}/scripts/finalize_production_notes.py {production_notes_path} "
                f"--renderer-report {renderer_report_path} --readiness-report {readiness_report_path} "
                f"--contact-sheet {contact_sheet_path} --quality-report {quality_report_path} "
                f"--motion-report {motion_report_path} --audio-report {audio_report_path} "
                f"--visual-review {visual_review_path} --visual-contract-report {visual_contract_report_path} --json"
            ),
            "packageValidation": (
                f"uv run --script {skill_path}/scripts/check_production_package.py "
                f"--require-source-links --brief {brief_path} --video {video_path} --design-note {design_path} "
                f"--production-notes {production_notes_path} --package-manifest {package_manifest_path} "
                f"--pattern-blueprint {pattern_blueprint_json_path} "
                f"--asset-manifest {asset_manifest_path} --composition-plan {composition_plan_path} "
                f"--visual-review {visual_review_path} --visual-contract-report {visual_contract_report_path} "
                f"--renderer {renderer_path} --expect-width 1280 --expect-height 720 --expect-fps 30 "
                f"--expect-duration {duration_seconds:g} --duration-tolerance 1 "
                f"--renderer-report {renderer_report_path} "
                f"--contact-sheet {contact_sheet_path} --quality-report {quality_report_path} "
                f"--motion-report {motion_report_path} "
                f"--capture-manifest {capture_manifest_path} --audio-report {audio_report_path} "
                f"--readiness-report {readiness_report_path} --style-fidelity-report {style_fidelity_report_path} "
                "--min-readiness-score 18 "
                "--min-style-fidelity-score 12 "
                "--require-audio --require-audio-report --require-voiceover --require-design-note "
                "--require-production-notes --require-package-manifest "
                "--require-pattern-blueprint "
                "--require-visual-contract --require-ready-assets --require-specialist-routing "
                "--require-source-routing --require-reviewed-scenes "
                "--require-renderer --forbid-scaffold-renderer --require-renderer-report "
                "--require-renderer-beat-coverage --require-renderer-visual-coverage "
                "--require-readiness-report --require-style-fidelity-report --require-final-review-notes "
                "--require-contact-sheet --require-motion-report "
                "--output artifacts/reviews/package-validation.json --json"
            ),
        },
    }


def scaffold(args: argparse.Namespace) -> dict[str, object]:
    project_id = args.project_id or slugify(args.title)
    root = args.project_dir
    dirs = [
        root / "source",
        root / "src",
        root / "artifacts" / "videos",
        root / "artifacts" / "audio",
        root / "artifacts" / "reviews",
        root / "artifacts" / "images",
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

    brief_text = render_brief(args)
    blueprint = pattern_blueprint(args)
    asset_manifest = build_asset_manifest(args, project_id)
    composition_plan = build_composition_plan(args)
    source_package = build_source_package(args, project_id)
    shot_contract = build_shot_contract(args, project_id)
    transition_plan = build_transition_plan(args, project_id)
    asset_manifest_text = json.dumps(asset_manifest, indent=2) + "\n"
    composition_plan_text = json.dumps(composition_plan, indent=2) + "\n"
    visual_review = build_visual_review(
        project_id,
        asset_manifest_text,
        composition_plan_text,
        composition_plan,
    )
    written: list[str] = []
    skipped: list[str] = []
    write_file(root / "source" / "brief.md", brief_text, args.force, written, skipped)
    write_file(
        root / "source" / "source-package.json",
        json.dumps(source_package, indent=2) + "\n",
        args.force,
        written,
        skipped,
    )
    write_file(
        root / "source" / "shot-contract.json",
        json.dumps(shot_contract, indent=2) + "\n",
        args.force,
        written,
        skipped,
    )
    write_file(root / "source" / "design-note.md", render_design_note(args), args.force, written, skipped)
    write_file(root / "source" / "production-notes.md", render_production_notes(args, project_id, root), args.force, written, skipped)
    write_file(
        root / "source" / "pattern-blueprint.json",
        json.dumps(blueprint, indent=2) + "\n",
        args.force,
        written,
        skipped,
    )
    write_file(
        root / "source" / "pattern-blueprint.md",
        select_video_patterns.render_markdown(blueprint),
        args.force,
        written,
        skipped,
    )
    write_file(root / "source" / "asset-manifest.json", asset_manifest_text, args.force, written, skipped)
    write_file(root / "source" / "composition-plan.json", composition_plan_text, args.force, written, skipped)
    write_file(
        root / "source" / "transition-plan.json",
        json.dumps(transition_plan, indent=2) + "\n",
        args.force,
        written,
        skipped,
    )
    write_file(
        root / "artifacts" / "reviews" / "visual-review.json",
        json.dumps(visual_review, indent=2) + "\n",
        args.force,
        written,
        skipped,
    )
    write_file(root / "src" / "storyboard.md", render_storyboard(args), args.force, written, skipped)
    renderer_html, renderer_metadata = create_concept_renderer.render_html(
        brief_text,
        title=args.title,
        video_id=project_id,
        duration=args.runtime,
    )
    write_file(root / "src" / "index.html", renderer_html, args.force, written, skipped)
    manifest = build_manifest(args, project_id, root)
    write_file(
        root / "source" / "package-manifest.json",
        json.dumps(manifest, indent=2) + "\n",
        args.force,
        written,
        skipped,
    )

    return {
        "ok": True,
        "projectDir": str(root),
        "projectId": project_id,
        "createdDirectories": [str(path) for path in dirs],
        "written": written,
        "skipped": skipped,
        "manifest": str(root / "source" / "package-manifest.json"),
        "patternBlueprint": str(root / "source" / "pattern-blueprint.json"),
        "sourcePackage": str(root / "source" / "source-package.json"),
        "shotContract": str(root / "source" / "shot-contract.json"),
        "assetManifest": str(root / "source" / "asset-manifest.json"),
        "compositionPlan": str(root / "source" / "composition-plan.json"),
        "transitionPlan": str(root / "source" / "transition-plan.json"),
        "visualReview": str(root / "artifacts" / "reviews" / "visual-review.json"),
        "renderer": str(root / "src" / "index.html"),
        "rendererMetadata": renderer_metadata,
    }


def main() -> int:
    args = parse_args()
    result = scaffold(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"PASS awsome-videos scaffold: {result['projectDir']}")
        if result["skipped"]:
            print(f"WARN skipped existing files: {len(result['skipped'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
