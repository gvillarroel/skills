#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "defusedxml==0.7.1"]
# ///
"""Show the three highest and lowest existing selected-candidate SVG scores."""
import hashlib
import html
import json
from pathlib import Path
import textwrap
from PIL import Image, ImageDraw, ImageFont
from review_procedural_population import host_path, preview

REPO = Path(__file__).resolve().parents[3]
STUDY = REPO / "evaluations/runs/svp3"
OUT = REPO / "projects/svg-brief-design/artifacts/reviews/extremes-20260926"
NAMES = {
    "vector-011--6b42f7e2789d1bd1": "Interlaced circular frame",
    "vector-004--eb6eabbcb9ca2ad4": "Android head",
    "vector-024--652120566170fbf2": "Periodic oscillation",
    "vector-030--d3c57e0c21dbede0": "Angled space insignia",
}


def font(size):
    for path in ("C:/Windows/Fonts/segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def row_image(record, position):
    native = json.loads(Path(record["native_result"]).read_text(encoding="utf-8"))
    task = host_path(native["config"]["task"]["path"])
    brief = (task / "instruction.md").read_text(encoding="utf-8").split("\n\n")[0]
    reference = task / "tests/reference.svg"
    generated = Path(record["artifact"])
    canvas = Image.new("RGB", (1120, 510), "white")
    draw = ImageDraw.Draw(canvas)
    score = record["reward"]["visual_similarity"]
    draw.rounded_rectangle((16, 10, 1104, 56), radius=9, fill="#eff2f6")
    draw.text((30, 18), f'{position}. {NAMES[record["task"]]}', fill="#182333", font=font(25))
    draw.text((840, 21), f"Similarity  {score:.4f}", fill="#182333", font=font(22))
    draw.text((34, 71), "PURCHASED REFERENCE", fill="#687589", font=font(16))
    draw.text((594, 71), "LUNA + NEW SKILL", fill="#687589", font=font(16))
    canvas.paste(preview(reference, width=520, height=300), (20, 100))
    canvas.paste(preview(generated, width=520, height=300), (580, 100))
    draw.line((560, 100, 560, 400), fill="#dce2eb", width=1)
    draw.text((32, 414), "User brief (original Spanish):", fill="#687589", font=font(16))
    for index, line in enumerate(textwrap.wrap(brief, width=115)):
        draw.text((32, 439+24*index), line, fill="#182333", font=font(18))
    return canvas, {"brief": brief, "reference_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
                    "generated_sha256": hashlib.sha256(generated.read_bytes()).hexdigest()}


def main():
    audit = json.loads((STUDY / "revision-review/audit.json").read_text(encoding="utf-8"))
    rows = [r for r in audit["records"] if r["candidate"] == "q"]
    assert len(rows) == 18 and all(r["runtime_valid"] for r in rows)
    ranked = sorted(rows, key=lambda r: (-r["reward"]["visual_similarity"], r["trial"]))
    OUT.mkdir(parents=True, exist_ok=False)
    selected = []
    sections = []
    for group, title, records in (("best", "Top 3 by reference similarity", ranked[:3]),
                                   ("worst", "Bottom 3 by reference similarity", list(reversed(ranked[-3:])))):
        sheet = Image.new("RGB", (1120, 1630), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((30, 17), title, fill="#182333", font=font(31))
        draw.text((30, 61), "Existing GPT-6 Luna outputs · candidate q · selected from 18 public trials", fill="#687589", font=font(19))
        cards = []
        for position, record in enumerate(records, 1):
            row, metadata = row_image(record, position)
            file = f"{group}-{position}.png"
            row.save(OUT / file)
            sheet.paste(row, (0, 100+(position-1)*510))
            selected.append({"group": group, "position": position, "task": record["task"],
                             "trial": record["trial"], "reward": record["reward"],
                             "generated_svg": record["artifact"], "pair_preview": file, **metadata})
            cards.append(f'<article><a href="{file}"><img src="{file}" alt="{html.escape(NAMES[record["task"]])} comparison"></a><p><a href="{Path(record["artifact"]).as_uri()}">Open generated SVG</a> · {html.escape(record["trial"])}</p></article>')
        sheet.save(OUT / f"{group}-3.png")
        sections.append(f'<section id="{group}"><h2>{title}</h2>{"".join(cards)}</section>')
    manifest = {"candidate": "q", "population": 18, "ranking_key": "visual_similarity",
                "scores_recomputed": False, "new_model_calls": 0, "selections": selected,
                "privacy": "Local comparison only. Purchased references are rendered for review, never added to the skill or published.",
                "interpretation": "Ranking measures the frozen shape/style proxy. It is not a general aesthetic or semantic correctness verdict. Multiple repetitions of the same task remain eligible."}
    (OUT / "selection.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    (OUT / "index.html").write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SVG examples: best and worst similarity</title><style>body{font-family:system-ui,sans-serif;background:#f3f5f8;color:#182333;margin:28px auto;max-width:1160px;padding:0 16px}h1{font-size:30px}p{line-height:1.5}nav{display:flex;gap:20px;margin:24px 0}article{background:white;border-radius:14px;overflow:hidden;margin:20px 0;box-shadow:0 2px 10px #1020300b}article img{display:block;width:100%;height:auto}article p{padding:0 24px 14px;font-size:13px;color:#687589}a{color:#2456a0}section{scroll-margin-top:20px}</style><h1>Six existing outputs from the new SVG skill</h1><p>Three highest and three lowest scores among 18 public GPT-6 Luna trials. Reference on the left; generated SVG on the right. Click a comparison to enlarge it. Scores are the frozen shape/style proxy, not a general design-quality verdict.</p><p>Local evaluation gallery. Purchased reference artwork is excluded from the skill and must not be published as part of this review.</p><nav><a href="#best">Top three</a><a href="#worst">Bottom three</a><a href="selection.json">Score and source manifest</a></nav>'''+"".join(sections)+"</html>", encoding="utf-8")
    print(json.dumps({"gallery": str(OUT / "index.html"), "best_scores": [r["reward"]["visual_similarity"] for r in ranked[:3]],
                      "worst_scores": [r["reward"]["visual_similarity"] for r in reversed(ranked[-3:])]}))


if __name__ == "__main__":
    main()
