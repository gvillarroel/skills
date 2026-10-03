#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare palette evidence and isolated prompts for support-output skills."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
PALETTE = ROOT / "skills/hyperframes-explainer/assets/palettes/colorsets.json"
PREVIEW_SKILLS = ("ambientcg-material-search", "iconify-icon-search", "kenney-asset-search", "pexels-media-search", "polyhaven-asset-search", "destockd-video-search")
for skill in PREVIEW_SKILLS:
    path = ROOT / f"skills/{skill}/SKILL.md"
    before = path.read_text(encoding="utf-8")
    note = "## Presentation colors\n\nUse colorset1 for authored preview chrome: `#f7f7f7` stage, `#ffffff` cards, `#333e48` text, `#cfcfcf` borders and `#9e1b32` links/emphasis. If extended authored categories are requested, use only the bundled [colorset2 tokens](assets/palettes/colorsets.json). Preserve provider image, video, texture and multicolor icon bytes as source material; never claim that their original pixels fit an authored colorset. Render selected monochrome icons with a colorset token.\n\n"
    if "## Presentation colors" not in before:
        marker = before.find("\n## ")
        after = before[:marker + 1] + note + before[marker + 1:] if marker >= 0 else before + "\n" + note
        path.write_text(after, encoding="utf-8", newline="\n")
    target = ROOT / f"skills/{skill}/assets/palettes/colorsets.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PALETTE, target)
    if skill != "destockd-video-search":
        prompt = f"""Create an offline candidate preview as exact `preview.html` using only the installed `{skill}` skill. Do not call a provider or download anything. Use its bundled `scripts/asset_io.py` gallery writer with a manifest you create in `candidates.json`: schema_version 1, provider Synthetic, and one result with option 1, id sample-1, title Example, type preview, page_url https://example.com/resource, author Fixture, license title CC0, and no thumbnail. Keep generated helper/manifest files outside the read-only skill. Deliver `preview.html` and `candidates.json`. The authored interface must use colorset1, with dark readable labels, a light surface and red links; preserve the option and source identity. Use a small workspace-local uv Python script if you need to import the bundled writer. Run a structural check of the produced HTML.\n"""
        output = ROOT / f"evaluations/pi-prompts/colorset-{skill}.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(prompt, encoding="utf-8")

prompts = {
    "pixel-art-image-video": "Read the installed pixel-art-image-video skill. Create exact source.svg (80x48), with a white background, a red rectangle and blue circle. Produce pixel.png and pixel.json using the default palette, and extended.webp plus extended.json using colorset2. Use a logical pixel size of 2. Validate both using the bundled independent validator. The default must fit colorset1, the extended file colorset2. Create all six exact paths outside the read-only skill. Do not fetch source media.",
    "one-bit-dither-svg": "Read the installed one-bit-dither-svg skill. Create exact source.svg, an 80x48 three-region illustration with white paper, a blue circle and a red rectangle. Produce regional.svg, regional.png, regional.json in regional mode with colorset1, and extended.svg, extended.png, extended.json with colorset2; render width 80, cell-size 2. Use the regional palette mapping, validate both SVGs with the bundled validator and inspect their previews. All seven exact files must exist outside the read-only skill. Do not fetch media.",
    "animated-svg-to-gif": "Read the installed animated-svg-to-gif skill. Copy its pulse template to exact pulse.animated.svg and convert it to exact pulse.gif: duration 2 seconds, width 360, fps 12, scale 1, white background. Validate actual dimensions and motion. The authored source must fit colorset1. Generate exact pulse.animated.svg and pulse.gif outside the skill, preserving names and the template semantics.",
    "asciinema-real-command-video": "Read the installed asciinema-real-command-video skill. This is a plan-only offline color contract; do not run any target commands, recordings or external tools. Create exact sample.cast (asciicast v2 width80 height24 with output A plus an off-palette truecolor SGR red-ish foreground and then B with reset), and exact themed.cast by using scripts/terminal_colorsets.py write_presentation_cast in colorset1. Create exact theme.json containing colorset colorset1 and aggTheme from agg_theme(colorset1). Validate theme RGB entries fit the bundled palette, that sample.cast remains unchanged, that themed.cast keeps event timings/text, and that the extended paint has been mapped. Generated files/helper belong outside the read-only skill.",
}
prompts["destockd-video-search"] = "Read the installed destockd-video-search skill. Create an offline synthetic candidate document candidates.json with one result: id fixture-shot, option1, shot Fixture shot, film Fixture film, color_type bw, page_url https://example.com/shot, keyframe empty and preview empty. Use its scripts/destockd.py gallery(document,path) function to generate exact preview.html without calling a provider or downloading. Validate actual option/source identity and authored colorset1 CSS. Keep all generated files outside the read-only skill. Deliver candidates.json and preview.html."
prompts["technical-logo-assets"] = "Read the installed technical-logo-assets skill. Export exact devicon-python identity using its adaptive variant baked to colorset1 red #9e1b32. Required paths: logo.svg, logo.provenance.json and logo.license.txt. Preserve vector identity and catalog/source provenance, validate the exported SVG colors and metadata, and do not modify the bundle or enumerate thousands of logo files. Do not fetch anything."
prompts["harbor-author-evaluation-datasets"] = "Read the installed harbor-author-evaluation-datasets skill. Produce an offline sanitized aggregate comparison for a synthetic schemaVersion1 Harbor final report you create in final-report.json, following the bundled final-report/aggregate contracts. Use two complete synthetic jobs with aggregate metrics and labels baseline/candidate (no private task names or prompts), with different input/cached/output tokens, reported cost, correctness and agent/wall time. Run the bundled report consolidator to produce exact comparison/comparison-report.json, comparison/comparison-report.md, comparison/quality-comparison.svg, comparison/resource-comparison.svg and comparison/efficiency-frontier.svg. Validate the five outputs and actual SVG authored paint membership in colorset2. Do not run Harbor tasks or call any target systems. Keep generated files outside the read-only skill."
for skill, prompt in prompts.items():
    output = ROOT / f"evaluations/pi-prompts/colorset-{skill}.md"
    output.write_text(prompt + "\n", encoding="utf-8")
print("Prepared six preview contracts and four isolated color prompts.")
