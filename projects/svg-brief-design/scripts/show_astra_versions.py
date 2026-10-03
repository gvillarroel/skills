#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow==11.3.0", "resvg-py==0.2.6", "defusedxml==0.7.1"]
# ///
"""Show every generated development output across two distinct model profiles."""
import base64
import html
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from inspect_technique_evolution import collect
from show_technique_evolution import LABELS, has_judged_quality, main as paired_gallery

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svt8"
PRIOR = REPO / "evaluations/runs/svt7"


def main():
    paired_gallery(ROOT, "c")
    out = ROOT / "gallery-models"
    out.mkdir(exist_ok=False)
    groups = [("Luna · current skill · historical", collect(PRIOR / "jobs/b", 18)),
              ("Astra · current skill", collect(ROOT / "jobs/b", 18)),
              ("Astra · purpose guide", collect(ROOT / "jobs/c", 18))]
    sections, strips = [], []
    font = ImageFont.truetype(str(ROOT / "evaluator/fonts/DejaVuSans.ttf"), 20)
    for task in sorted({row["task"] for _, rows in groups for row in rows}):
        title = LABELS[task.split("--")[0][-3:]]
        brief = (ROOT / "development" / task / "instruction.md").read_text(encoding="utf-8").split("\n\n")[0]
        rows = [(label, sorted([r for r in items if r["task"] == task], key=lambda r: r["trial"])) for label, items in groups]
        cards = []
        for attempt in range(3):
            strip = Image.new("RGB", (1440, 450), "white")
            draw = ImageDraw.Draw(strip)
            for i, (label, items) in enumerate(rows):
                row = items[attempt]
                source = Path(row["verifier_path"]) / "candidate.png"
                scored = has_judged_quality(row)
                if source.exists():
                    raw = source.read_bytes()
                else:
                    missing = Image.new("RGB", (480, 350), "#f0f0f0")
                    ImageDraw.Draw(missing).text((30, 155), "No evaluated preview; failed attempt", fill="black")
                    buffer = io.BytesIO()
                    missing.save(buffer, format="PNG")
                    raw = buffer.getvalue()
                img = Image.open(io.BytesIO(raw)).convert("RGBA")
                matte = Image.new("RGBA", img.size, "white")
                matte.alpha_composite(img)
                fit = ImageOps.contain(matte.convert("RGB"), (440, 335), Image.Resampling.LANCZOS)
                strip.paste(fit, (i*480+(480-fit.width)//2, 95+(335-fit.height)//2))
                score = f'{100*row["reward"]["technique_quality"]:.2f}' if scored else "unscored"
                draw.text((i*480+15, 13), label.split(" · ")[0]+" / "+("purpose guide" if i == 2 else "current skill"), font=font, fill="black")
                draw.text((i*480+15, 43), score + (" / review flag" if row["review_recommended"] else ""), font=font, fill="black")
                data = "data:image/png;base64,"+base64.b64encode(raw).decode()
                note = f'Jev utility: {score}; review flag: {row["review_recommended"]}' if scored else "Preserved failed or unjudged trial. No visual grade assigned."
                cards.append(f'<figure><figcaption>{html.escape(label)} · repeat {attempt+1}</figcaption><img src="{data}" alt="{html.escape(title+": "+label)}"><p>{html.escape(note)}</p><details><summary>Provenance</summary><code>{html.escape(row["trial"])}</code></details></figure>')
            if attempt == 0:
                strips.append((title, strip))
                strip.save(out / f"{task.split('--')[0]}-first-repeat.png")
        sections.append(f'<section id="{task.split("--")[0]}"><h2>{html.escape(title)}</h2><p lang="es">{html.escape(brief)}</p><div class="grid">{"".join(cards)}</div></section>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SVG skill versions: Luna and Astra</title><style>*{box-sizing:border-box}body{font:16px/1.5 system-ui;background:#f3f3f3;color:#171717;margin:auto;max-width:1500px;padding:22px}h1{font-size:30px;line-height:1.2}section{margin:32px 0;background:white;padding:18px;border:1px solid #ddd}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}figure{margin:0;padding:12px;border:1px solid #ddd;min-width:0}figcaption{font-weight:650}img{width:100%;height:310px;object-fit:contain;background:white}figure p{font-size:13px}code{font-size:11px;overflow-wrap:anywhere}.notice{padding:10px;background:white;border-left:4px solid #51666f}nav{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0}nav a{padding:6px 10px;background:white;border:1px solid #ccc;border-radius:6px;color:#244e65;text-decoration:none}summary{cursor:pointer}@media(max-width:700px){body{padding:10px}.grid{grid-template-columns:1fr}section{padding:12px}img{height:290px}}</style><main><h1>SVG skill versions: Luna and Astra</h1><p>All six public briefs and all three fixed attempts. Medium reasoning and unchanged Jev 6.3.</p><details class="notice"><summary>How to read this comparison</summary><p>The current-skill files are identical across Luna and Astra. Luna is a historical control; only the two fresh Astra arms belong to this Pareto comparison. Display rows are not paired random seeds. Jev utility measures the declared reference-relative design criteria, not absolute excellence or pixel similarity. A review flag means the judgment deserves human attention.</p><p>This page includes generated outputs only. The separate local Astra gallery also includes purchased reference previews.</p></details><nav aria-label="Examples"><a href="#vector-004">Figure</a><a href="#vector-011">Ornament</a><a href="#vector-019">HUD</a><a href="#vector-020">Label</a><a href="#vector-024">Vintage</a><a href="#vector-030">Space</a></nav>'''+"".join(sections)+"</main></html>"
    (out / "index.html").write_text(page, encoding="utf-8")
    board = Image.new("RGB", (1440, len(strips)*500), "#eeeeee")
    draw = ImageDraw.Draw(board)
    for i, (title, strip) in enumerate(strips):
        draw.text((18, i*500+8), title, font=font, fill="black")
        board.paste(strip, (0, i*500+45))
    board.save(out / "comparison.png")
    assert page.count("<figure>") == 54 and page.count("data:image/png;base64,") == 54
    print(json.dumps({"model_gallery": str(out / "index.html"), "attempt_slots": 54, "purchased_artwork_in_model_gallery": False}))


if __name__ == "__main__":
    main()
