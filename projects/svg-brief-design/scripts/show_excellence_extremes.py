#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow==11.3.0"]
# ///
"""Present existing Jev v3 scores without rerunning models or modifying SVGs."""

import hashlib
import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[3]
RUN = REPO / "evaluations/runs/svgq2"
SOURCE = RUN / "review-v3/summary.json"
OUT = RUN / "extremes-v3"
NAMES = {
    "vector-004--eb6eabbcb9ca2ad4": "Android head",
    "vector-011--6b42f7e2789d1bd1": "Interlaced circular frame",
    "vector-019--75606bdb4ee5b4af": "HUD bar",
    "vector-020--09ee2ae28c7c367a": "Industrial label",
    "vector-024--652120566170fbf2": "Periodic oscillation",
    "vector-030--d3c57e0c21dbede0": "Angled space insignia",
}
NOTES = {
    "5ab30d87ea241b6f8deb": "The review records a frontal, slender head, large round eyes and a visible neck. All four dimensions received full credit.",
    "535397d745a964fa8efc": "The review records a clear elongated opening, diagonal accents and a compact angular silhouette. All four dimensions received full credit.",
    "e9c76cf11d35497bc20d": "The review records a black header, aligned readable text and a small barcode. Barcode decoding was not established.",
    "705dc2f92b01db65b798": "Jev reduced brief adherence and geometry. The visual evidence describes dense crossings and unclear over-under weaving.",
    "83357534a209d4b9577d": "Jev reduced brief adherence: the visual evidence describes overlapping curves without a clearly established over-under weave.",
    "d4fd7ceb8fbd62ac3f26": "Jev reduced brief adherence: the visual evidence describes continuous crossings without a distinct over-under weave.",
}
DIMENSIONS = [
    ("brief_adherence", "Brief"),
    ("geometric_finish", "Geometry"),
    ("composition", "Composition"),
    ("legibility", "Legibility"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size):
    return ImageFont.truetype(str(RUN / "fonts/DejaVuSans.ttf"), size)


def wrapped(draw, text, x, y, width, size, fill="#263348"):
    face = font(size)
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and draw.textlength(candidate, font=face) > width:
            draw.text((x, y), line, font=face, fill=fill)
            y += size + 6
            line = word
        else:
            line = candidate
    if line:
        draw.text((x, y), line, font=face, fill=fill)
        y += size + 6
    return y


def score_text(record):
    return f'{record["score_100"]:g} / 100'


def poster(group, title, subtitle, records):
    canvas = Image.new("RGB", (1440, 920), "#eef2f6")
    draw = ImageDraw.Draw(canvas)
    draw.text((32, 22), title, font=font(34), fill="#172333")
    draw.text((32, 70), subtitle, font=font(17), fill="#526177")
    for index, record in enumerate(records):
        x = 32 + index * 464
        draw.rounded_rectangle((x, 112, x + 448, 874), radius=14, fill="white")
        draw.text((x + 20, 132), f'{index+1}. {NAMES[record["task"]]}', font=font(22), fill="#172333")
        draw.text((x + 20, 168), score_text(record), font=font(29), fill="#11624c" if group == "best" else "#9a4323")
        draw.text((x + 20, 207), record["name"].split("__")[-1], font=font(13), fill="#66758a")
        rgba = Image.open(OUT / record["preview"]).convert("RGBA")
        preview = ImageOps.contain(rgba, (408, 280), Image.Resampling.LANCZOS)
        canvas.paste(preview, (x + 20 + (408-preview.width)//2, 240+(280-preview.height)//2), preview)
        draw.line((x+20, 532, x+428, 532), fill="#e2e7ed")
        draw.text((x+20, 548), "ORIGINAL REQUEST (SPANISH)", font=font(13), fill="#66758a")
        end = wrapped(draw, record["brief"], x+20, 573, 408, 17)
        assert end < 728, (record["id"], end)
        draw.text((x+20, 738), "RECORDED EVALUATION", font=font(13), fill="#66758a")
        end = wrapped(draw, record["review_note"], x+20, 763, 408, 15)
        assert end < 868, (record["id"], end)
    draw.text((32, 891), "Existing GPT-6 Luna + skill outputs | Jev v3 technical-excellence scores | 18 trials | No new model calls", font=font(14), fill="#526177")
    canvas.save(OUT / f"{group}-3.png")


def main():
    report = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = [row for row in report["records"] if row["candidate"] == "q"]
    assert len(rows) == 18 and all(isinstance(r["score_100"], (int, float)) for r in rows)
    maximum = max(r["score_100"] for r in rows)
    top_pool = sorted([r for r in rows if r["score_100"] == maximum], key=lambda r: (r["task"], r["name"]))
    best, seen = [], set()
    for row in top_pool:
        if row["task"] not in seen:
            best.append(row)
            seen.add(row["task"])
        if len(best) == 3:
            break
    assert len(best) == 3
    worst = sorted(rows, key=lambda r: (r["score_100"], r["task"], r["name"]))[:3]
    cutoff_ties = [r["name"] for r in rows if r["score_100"] == worst[-1]["score_100"]]
    OUT.mkdir(parents=True, exist_ok=True)
    selections, sections = [], []
    for group, title, subtitle, records in [
        ("best", "Three examples at the highest score", "12 outputs tie at 100. Three different task families are shown.", best),
        ("worst", "Three outputs with the lowest scores", "70, 82.5 and 82.5. Ties use task ID, then trial name; an oscillation also scored 82.5.", worst),
    ]:
        cards, enriched = [], []
        for index, row in enumerate(records, 1):
            source = Path(row["artifact"])
            assert digest(source) == row["artifact_sha256"], row["id"]
            evidence = json.loads((RUN / "current-bounded/evidence" / f'{row["id"]}.json').read_text(encoding="utf-8"))
            record = {**row, "group": group, "position": index,
                      "brief": evidence["request"].split("\n\n")[0],
                      "review_note": NOTES[row["id"]],
                      "preview": f"{group}-{index}-preview.png", "svg": f"{group}-{index}.svg"}
            (OUT / record["svg"]).write_bytes(source.read_bytes())
            assert digest(OUT / record["svg"]) == row["artifact_sha256"]
            rgba = Image.open(row["render"]).convert("RGBA")
            background = Image.new("RGBA", rgba.size, "white")
            Image.alpha_composite(background, rgba).convert("RGB").save(OUT / record["preview"])
            enriched.append(record)
            selections.append(record)
            dims = "".join(f'<div><dt>{label}</dt><dd>{row["dimensions"][key]} / 4</dd></div>' for key, label in DIMENSIONS)
            cards.append(f'''<article data-score="{row['score_100']}" data-id="{row['id']}">
<header><h3>{index}. {html.escape(NAMES[row['task']])}</h3><strong>{score_text(row)}</strong></header>
<a class="art" href="{record['svg']}" target="_blank" aria-label="Open {html.escape(NAMES[row['task']])} SVG"><img src="{record['preview']}" alt="{html.escape(NAMES[row['task']])}, trial {html.escape(row['name'].split('__')[-1])}"></a>
<div class="detail"><p class="eyebrow">Original request (Spanish)</p><blockquote lang="es">{html.escape(record['brief'])}</blockquote>
<dl>{dims}</dl><p>{html.escape(record['review_note'])}</p><details><summary>Recorded visual observations</summary><pre>{html.escape(json.dumps(row['visual_observations'], indent=2, ensure_ascii=False))}</pre></details>
<footer><a href="{record['svg']}" target="_blank">Open original SVG</a><span>Trial {html.escape(row['name'].split('__')[-1])}</span></footer></div></article>''')
        poster(group, title, subtitle, enriched)
        sections.append(f'<section id="{group}"><h2>{title}</h2><p>{subtitle}</p><div class="grid">{"".join(cards)}</div><p><a href="{group}-3.png">Open contact sheet</a></p></section>')
    manifest = {"candidate": "q", "population": len(rows), "evaluator": "Jev technical excellence v3",
                "ranking_key": "score_100", "top_score_count": len(top_pool),
                "top_selection": "At maximum score: first trial per task, ordered by task ID and trial name; first three distinct tasks.",
                "bottom_selection": "Ascending score, then task ID, then trial name; first three.",
                "bottom_cutoff_ties": sorted(cutoff_ties), "new_model_calls": 0,
                "source_report": str(SOURCE), "source_report_sha256": digest(SOURCE),
                "scores_recomputed": False, "purchased_references_included": False, "selections": selections}
    (OUT / "selection.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SVG skill: Jev top and bottom examples</title><style>
*{box-sizing:border-box}body{margin:0;background:#eef2f6;color:#172333;font:16px/1.55 system-ui,sans-serif}main{max-width:1460px;margin:auto;padding:32px 24px}h1{font-size:clamp(28px,4vw,44px);line-height:1.2;letter-spacing:-.03em}h2{font-size:28px;line-height:1.25}h3{margin:0;font-size:20px}p{max-width:100ch}a{color:#1453a0}nav{display:flex;flex-wrap:wrap;gap:20px;margin:24px 0}section{margin-top:46px;scroll-margin-top:20px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}article{background:white;border-radius:16px;overflow:hidden;border:1px solid #dce3ec}article header{padding:22px 22px 0}strong{display:block;font-size:30px;color:#11624c}#worst strong{color:#9a4323}.art{display:flex;height:315px;padding:22px;align-items:center;justify-content:center}.art img{display:block;width:100%;height:100%;object-fit:contain}.detail{padding:0 22px 22px}.eyebrow{text-transform:uppercase;font-size:12px;letter-spacing:.07em;color:#68768a}blockquote{margin:0;min-height:145px}dl{display:grid;grid-template-columns:1fr 1fr;gap:8px;background:#f3f6f9;padding:12px;border-radius:8px}dl div{display:flex;justify-content:space-between;gap:6px;font-size:13px}dd{margin:0;white-space:nowrap}pre{font-size:12px;white-space:pre-wrap;overflow-wrap:anywhere}summary{cursor:pointer}footer{display:flex;flex-wrap:wrap;gap:8px;justify-content:space-between;margin-top:20px;font-size:12px;color:#66758a}.note{background:#fff;padding:18px 22px;border-left:4px solid #94a4ba;border-radius:6px}@media(max-width:950px){.grid{grid-template-columns:1fr}blockquote{min-height:0}.art{height:340px}main{padding:20px 16px}}
</style></head><body><main><p class="eyebrow">GPT-6 Luna + current SVG skill · 18 existing trials</p><h1>Top and bottom examples, scored by Jev</h1><p>Technical-excellence v3 scores cover brief adherence (35%), geometric finish (25%), composition (20%) and legibility (20%). Click an image to inspect its unchanged SVG.</p><div class="note">12 of 18 outputs received 100/100: the top three below are representative tied examples, not a unique ranking. Full rubric credit does not establish flawless design. The lower scores reflect the recorded evaluator's interpretation, including its reading of “interlaced” as a visible over-under weave.</div><nav><a href="#best">Highest scores</a><a href="#worst">Lowest scores</a><a href="selection.json">Selection and source evidence</a><a href="../review-v3/index.html">All evaluated outputs</a></nav>'''+"".join(sections)+'''<p>Existing scores and artifacts only. No SVG regeneration or model calls. Purchased references are not included. Within the 82.5 tie, the periodic-oscillation trial hmgfCWr follows the circular frames under the documented tie rule.</p></main></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(json.dumps({"gallery": str(OUT / "index.html"), "top_ties": len(top_pool), "selected": [{"id": r["id"], "score": r["score_100"], "group": r["group"]} for r in selections]}, indent=2))


if __name__ == "__main__":
    main()
