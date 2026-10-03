#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Report every public retrospective artifact, including unsupported judge inputs."""
from collections import defaultdict
import argparse
import html
from pathlib import Path
import statistics
from PIL import Image, ImageDraw, ImageFont
from svg_excellence import REPO, read, write


def main(results_name="current-results.json", report_name="review", visual=False):
    root = REPO/"evaluations/runs/svgq2"
    prepared = root/"current-bounded"
    coordinator = read(prepared/"coordinator-only.json")
    results = read(root/results_name)
    outcome = {row["id"]: row for row in results["results"]+([] if visual else read(prepared/"unsupported.json"))}
    report = root/report_name
    report.mkdir(exist_ok=False)
    fonts = root/"fonts/DejaVuSans.ttf"
    font = ImageFont.truetype(str(fonts), 13)
    cells, records, summaries = [], [], {}
    for arm in ["b", "q"]:
        items = [row for row in coordinator if row["candidate"] == arm]
        items.sort(key=lambda row: (row["task"], row["name"]))
        sheet = Image.new("RGB", (1200, 1800), "#eeeeee")
        draw = ImageDraw.Draw(sheet)
        scores = []
        for index, row in enumerate(items):
            result = outcome[row["id"]]
            evidence = read(prepared/"evidence"/(row["id"]+".json"))
            source = prepared/"renders"/(row["id"]+".png")
            picture = Image.open(source).convert("RGBA")
            picture.thumbnail((380, 250))
            x, y = index%3*400, index//3*300
            canvas = Image.new("RGBA", (400, 270), "white")
            canvas.alpha_composite(picture, ((400-picture.width)//2, (270-picture.height)//2))
            sheet.paste(canvas.convert("RGB"), (x, y+30))
            score = result["score_100"]
            label = f"{row['task'][:10]} / {row['name'][-7:]} / " + (f"{score:.2f}" if score is not None else "needs review")
            draw.text((x+8,y+8), label, fill="black", font=font)
            if score is not None:
                scores.append(score)
            record = row | result | {"text_measurements": evidence.get("measurements", {}).get("text", []),
                                     "render": str(source)}
            observation = read(root/"visual-current"/row["id"]/"observation.json") if visual else None
            if observation:
                record["visual_observations"] = observation
            records.append(record)
            details = ''
            if observation:
                facts = [feature["requirement"]+": "+feature["observation"]+" ("+feature["status"]+")" for feature in observation["brief_features"]]
                facts += observation["geometry"]+observation["composition"]+observation["legibility"]
                details = '<details><summary>Visual evidence and design ratings</summary><p>'+html.escape(str(result.get("dimensions", {})))+'</p><ul>'+''.join('<li>'+html.escape(fact)+'</li>' for fact in facts)+'</ul></details>'
            cells.append(f'<article data-arm="{arm}"><h2>{html.escape(label)}</h2><img src="../current-bounded/renders/{row["id"]}.png"><p>{html.escape(evidence["request"])}</p><p>Arm: {arm}. Review signal: {result.get("review_recommended", False)}.</p>{details}<a href="../current-bounded/artifacts/{row["id"]}.svg">SVG</a> · <a href="../current-bounded/evidence/{row["id"]}.json">Evidence</a></article>')
        sheet.save(report/(arm+"-all.png"))
        missing = len(items)-len(scores)
        summaries[arm] = {"total": len(items), "scored": len(scores), "needs_review_unscored": missing,
                          "mean_scored": statistics.mean(scores) if scores else None,
                          "whole_cohort_mean_bounds": [sum(scores)/len(items), (sum(scores)+100*missing)/len(items)],
                          "full_marks": sum(score == 100 for score in scores)}
    scope = 'Jev assigns design grades using the actual brief, deterministic measurements and factual visual observations from GPT-6 Luna. All 36 SVGs were assessed, including the large source. No reference artwork or old score reached either model.' if visual else 'Text-only experimental version: 35 assessed and one oversized source needs review. This saturated configuration was superseded.'
    document = '<!doctype html><html lang="en"><meta charset="utf-8"><title>Jev expert SVG evaluation</title><style>body{font:15px system-ui;margin:30px;background:#f3f4f6;color:#15202b}main{display:grid;grid-template-columns:repeat(3,minmax(300px,1fr));gap:18px}article{background:white;padding:18px;border-radius:12px}img{width:100%;height:290px;object-fit:contain}h2{font-size:17px}p,li{line-height:1.45}button{padding:10px;margin:6px}details{padding:12px;background:#f4f6f8;margin:12px 0}article[hidden]{display:none}</style><h1>Prompt-conditioned technical review</h1><p>'+scope+' Scores and uncertainty are distinct. b: original guide; q: current procedural guide.</p><button onclick="show(\'all\')">All</button><button onclick="show(\'b\')">Baseline</button><button onclick="show(\'q\')">Current skill</button><main>'+''.join(cells)+'</main><script>function show(a){document.querySelectorAll("article").forEach(e=>e.hidden=a!=="all"&&e.dataset.arm!==a)}</script></html>'
    (report/"index.html").write_text(document,encoding="utf-8")
    write(report/"summary.json", {"summary": summaries, "records": records, "judge_report": results["report"],
          "rating_ceiling": "Retain the full-credit count: categorical ratings can still have a ceiling." if visual else "All assessed existing artifacts received full categorical credit; this evaluator does not discriminate this public population."})
    print(summaries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="current-results.json")
    parser.add_argument("--out", default="review")
    parser.add_argument("--visual", action="store_true")
    args = parser.parse_args()
    main(args.results, args.out, args.visual)
