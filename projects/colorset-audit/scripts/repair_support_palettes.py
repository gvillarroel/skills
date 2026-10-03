#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply the reviewed palette substitutions to support-output renderers."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
BACKUP = ROOT / "projects/colorset-audit/artifacts/baseline"


def update(relative: str, substitutions: dict[str, str]) -> None:
    path = ROOT / relative
    before = path.read_text(encoding="utf-8")
    after = before
    for old, new in substitutions.items():
        if old == 'role="img"' and 'data-colorset="colorset2"' in after:
            continue
        after = after.replace(old, new)
    if before != after:
        saved = BACKUP / relative
        if not saved.exists():
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, saved)
        path.write_text(after, encoding="utf-8", newline="\n")
        print(f"Updated {relative}")


for skill in ("ambientcg-material-search", "iconify-icon-search", "kenney-asset-search", "pexels-media-search", "polyhaven-asset-search"):
    update(f"skills/{skill}/scripts/asset_io.py", {
        "#101923": "#f7f7f7", "#eef4f9": "#333e48", "#50687c": "#cfcfcf",
        "#1d2c3b": "#ffffff", "#f1f4f7": "#e7e7e7", "#98dcff": "#9e1b32",
        '<html lang="en">': '<html lang="en" data-colorset="colorset1">',
    })
update("skills/iconify-icon-search/scripts/iconify.py", {"%2317222d": "%23333e48"})
update("skills/destockd-video-search/scripts/destockd.py", {
    "#101923": "#f7f7f7", "#eff4f8": "#333e48", "#1d2a38": "#ffffff",
    "#4a6175": "#cfcfcf", "#080c10": "#e7e7e7", "#8cdaff": "#9e1b32",
    "#d3e0eb": "#333e48", '<html lang="en">': '<html lang="en" data-colorset="colorset1">',
})
update("skills/harbor-author-evaluation-datasets/scripts/consolidate_harbor_reports.py", {
    'data-colorset="colorset2" data-colorset="colorset2"': 'data-colorset="colorset2"',
    "#38BDF8": "#007298", "#A78BFA": "#652f6c", "#34D399": "#45842a",
    "#FBBF24": "#98700c", "#FB7185": "#9e1b32", "#22D3EE": "#004d66",
    "#C084FC": "#431f47", "#A3E635": "#294d19", "#F97316": "#e77204",
    "#60A5FA": "#00ace6", "#F472B6": "#9e00b3", "#2DD4BF": "#36b300",
    "#070B18": "#f7f7f7", "#10172A": "#f7f7f7", "#071827": "#f7f7f7",
    "#E5EEF9": "#333e48", "#7DD3FC": "#9e1b32", "#94A3B8": "#4f4f4f",
    "#334155": "#cfcfcf", "#111827": "#ffffff", "#263247": "#cfcfcf",
    "#0C4A6E": "#e7e7e7", "#0F2234": "#ffffff", "#155E75": "#cfcfcf",
    "#1E293B": "#e7e7e7", "#64748B": "#828282", "#E2E8F0": "#333e48",
    "#F8FAFC": "#ffffff",
    'role="img"': 'role="img" data-colorset="colorset2"',
})

for path in (ROOT / "skills/asciinema-real-command-video/assets/templates").glob("*.json"):
    update(path.relative_to(ROOT).as_posix(), {'"theme": "github-dark"': '"theme": "colorset1"'})
update("skills/asciinema-real-command-video/references/session-plan.md", {'"theme": "github-dark"': '"theme": "colorset1"'})
update("skills/asciinema-real-command-video/scripts/test_asciinema_command_video.py", {'"theme": "github-dark"': '"theme": "colorset1"'})
update("skills/technical-logo-assets/assets/logo-audit.html", {
    "#172434": "#333e48", "#edf1f5": "#f7f7f7", "#173b63": "#9e1b32",
    "#526173": "#4f4f4f", "#d9e0e8": "#cfcfcf", "#64748b": "#696969",
    "var(--chosen-color,#007298)": "var(--chosen-color,#9e1b32)",
    '<html lang="en">': '<html lang="en" data-colorset="colorset2">',
    '<input id="chosen-color" type="color" value="#007298">': '<select id="chosen-color"><option value="#9e1b32">Colorset 1 red</option><option value="#333e48">Colorset 1 ink</option><option value="#6d1222">Colorset 1 dark red</option><option value="#007298">Colorset 2 blue</option><option value="#45842a">Colorset 2 green</option><option value="#652f6c">Colorset 2 purple</option><option value="#e77204">Colorset 2 orange</option></select>',
    "rgb(209, 47, 103)": "rgb(158, 27, 50)",
})
for skill in ("one-bit-dither-svg", "pixel-art-image-video"):
    for path in [ROOT / f"skills/{skill}/SKILL.md", *(ROOT / f"skills/{skill}/references").glob("*.md")]:
        update(path.relative_to(ROOT).as_posix(), {
            "#b7410e": "#9e1b32", "#172b3a": "#333e48", "#497b7b": "#9e1b32",
            "#d0a86c": "#828282", "#fff0d0": "#ffffff",
        })
