#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow==11.3.0", "resvg-py==0.2.6", "defusedxml==0.7.1"]
# ///
"""Create a local responsive gallery of every paired development output."""
import base64
import html
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from PIL import Image, ImageDraw, ImageOps, ImageFont

REPO=Path(__file__).resolve().parents[3]
ROOT=REPO / "evaluations/runs/svt1"
LABELS={"004":"Expressive figure","011":"Integrated ornament","019":"Compact HUD","020":"Compact label","024":"Vintage diagram","030":"Open space insignia"}


def has_judged_quality(row):
    return not row.get("exception") and row["reward"].get("artifact_valid")==1 and row.get("overall") is not None and "technique_quality" in row["reward"]


def main(root=None, candidate_id=None):
    global ROOT
    if root is not None:
        ROOT = Path(root)
    revision=sys.argv[1:] == ["revision"]
    candidate=candidate_id or ("d" if revision else "c")
    supplement=json.loads((ROOT / (f"decision-{candidate}.json" if candidate_id else "revision-supplement.json" if revision else "development-supplement.json")).read_text())
    rows=supplement["trial_audit"]
    counts={sum(r["task"]==task for r in rs) for rs in rows.values() for task in {r["task"] for r in rs}}
    assert len(counts)==1 and next(iter(counts))>0
    repeats=next(iter(counts))
    out=ROOT / (f"gallery-{candidate}" if candidate_id else "gallery-d" if revision else "gallery");out.mkdir(exist_ok=False)
    cards=[]; montage=[]; review_renders=[]
    font=ImageFont.truetype(str(ROOT / "evaluator/fonts/DejaVuSans.ttf"),21)
    for task,means in sorted(supplement["comparison"]["families"].items()):
        arms={a:sorted([r for r in rows[a] if r["task"]==task],key=lambda r:r["trial"]) for a in ["b",candidate]}
        title=LABELS[task.split("--")[0][-3:]]
        brief=(ROOT / "development" / task / "instruction.md").read_text(encoding="utf-8").split("\n\n")[0]
        items=[]
        for attempt in range(repeats):
            sources=[("Purchased reference",Path(arms["b"][attempt]["verifier_path"])/"anchor.png",None),
                     ("Installed baseline",Path(arms["b"][attempt]["verifier_path"])/"candidate.png",arms["b"][attempt]),
                     (("Candidate "+candidate if candidate_id else "Guide + orbit base" if revision else "Construction guide"),Path(arms[candidate][attempt]["verifier_path"])/"candidate.png",arms[candidate][attempt])]
            strip=Image.new("RGB",(1440,450),"white"); draw=ImageDraw.Draw(strip)
            for i,(label,source,row) in enumerate(sources):
                # Native WSL output paths are converted only for local reading.
                source=Path(str(source).replace('/mnt/c/','C:/'))
                if not source.exists() and row is None:
                    source = Path(str(Path(arms[candidate][attempt]["verifier_path"])/"anchor.png").replace('/mnt/c/','C:/'))
                    if not source.exists():
                        source = next((ROOT / "jobs").glob(f"*/{task}__*/verifier/anchor.png"), source)
                review_only = False
                if not source.exists() and row is not None:
                    # A preserved tool failure can still leave a final SVG.
                    # Render it outside the immutable job for human review only;
                    # this neither replays the verifier nor creates a score.
                    instruction = (ROOT / "development" / task / "instruction.md").read_text(encoding="utf-8")
                    paths = re.findall(r"`(/logs/artifacts/[^`]+\.svg)`", instruction)
                    assert len(set(paths)) == 1
                    artifact = paths[0]
                    trial = Path(str(Path(row["verifier_path"]).parent).replace('/mnt/c/','C:/'))
                    saved = trial / "artifacts" / artifact.lstrip("/")
                    if saved.is_file() and saved.resolve().is_relative_to((trial / "artifacts").resolve()):
                        preview = out / (row["trial"]+"-review.png")
                        helper = ROOT / "inputs/b/svg-brief-design/scripts/render_svg.py"
                        result = subprocess.run([sys.executable, "-B", str(helper), str(saved), "--output", str(preview), "--font-dir", str(ROOT / "evaluator/fonts")], capture_output=True, text=True, encoding="utf-8")
                        review_renders.append({"trial": row["trial"], "source": str(saved), "preview": str(preview), "rendered": result.returncode==0, "scored":False})
                        if result.returncode == 0:
                            source = preview
                            review_only = True
                if source.exists():
                    raw=source.read_bytes()
                else:
                    placeholder=Image.new("RGB",(480,350),"#eeeeee")
                    ImageDraw.Draw(placeholder).text((35,155),"No evaluated preview is available",fill="black")
                    buffer=io.BytesIO();placeholder.save(buffer,format="PNG");raw=buffer.getvalue()
                image=Image.open(io.BytesIO(raw)).convert("RGBA")
                matte=Image.new("RGBA",image.size,"white");matte.alpha_composite(image)
                fit=ImageOps.contain(matte.convert("RGB"),(440,350),Image.Resampling.LANCZOS)
                strip.paste(fit,(i*480+(480-fit.width)//2,80+(350-fit.height)//2))
                score="" if row is None else f" | {100*row['reward']['technique_quality']:.1f}" if has_judged_quality(row) else " | unscored"
                draw.text((i*480+18,15),label+score,fill="black",font=font)
                data="data:image/png;base64,"+base64.b64encode(raw).decode()
                notes="" if row is None else f"<p>Jev utility: {100*row['reward']['technique_quality']:.2f}; review flag: {row['review_recommended']}</p>" if has_judged_quality(row) else "<p>Original failed or unjudged attempt retained. Any native failure zero is not a Jev quality judgment.</p>"
                if review_only:
                    notes += "<p>This preserved SVG was rendered afterward for visual review only; the original failed attempt remains unqualified.</p>"
                items.append(f'<figure><figcaption>{html.escape(label)} — repeat {attempt+1}</figcaption><img src="{data}" alt="{html.escape(title+": "+label)}">{notes}</figure>')
            strip.save(out / f"{task.split('--')[0]}-repeat-{attempt+1}.png")
            if attempt==0:montage.append((title,strip))
        comparison_complete = not any(row.get("exception") for group in arms.values() for row in group)
        delta = f'{100*means["delta"]:+.2f} points' if comparison_complete and isinstance(means.get("delta"), (int,float)) else 'not comparable because an execution or evaluation failed'
        cards.append(f'<section><h2>{html.escape(title)}</h2><p lang="es">{html.escape(brief)}</p><p>Mean change: {delta}. All {repeats} fixed repeats are shown; side-by-side rows are display pairings, not shared random seeds.</p><div class="grid">{"".join(items)}</div></section>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SVG construction study</title><style>body{font:16px system-ui;margin:auto;max-width:1500px;padding:22px;background:#f3f3f3;color:#171717}h1{font-size:28px}section{margin:30px 0;padding:20px;background:white;border:1px solid #ddd}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}figure{margin:0;border:1px solid #ddd;padding:12px}figcaption{font-weight:600}img{width:100%;height:320px;object-fit:contain}p{line-height:1.5}figure p{font-size:13px}@media(max-width:700px){.grid{grid-template-columns:1fr}body{padding:10px}img{height:300px}}</style><h1>SVG construction study: all development outputs</h1><p>Same short briefs, exact GPT-6 Luna, medium reasoning, two fixed executions per version. Scores are Jev 6.3 expected coded utility relative to a reference; they are not absolute grades or pixel similarity. The reference receives no invented numeric score. This local gallery contains licensed purchased reference previews for the owner's review.</p>'''+"".join(cards)+"</html>"
    page=page.replace("two fixed executions per version", f"{repeats} fixed executions per version")
    protocol_path = ROOT / "protocol.json"
    if protocol_path.exists():
        profile = json.loads(protocol_path.read_text(encoding="utf-8-sig"))["runtime"]
        model = profile["model"].split("/")[-1]
        names = {"gpt-6-luna": "GPT-6 Luna", "gpt-6-astra": "GPT-6 Astra"}
        page = page.replace("exact GPT-6 Luna, medium reasoning", "exact " + html.escape(names.get(model, model)) + ", " + html.escape(profile["thinking"]) + " reasoning")
    (out / "index.html").write_text(page,encoding="utf-8")
    (out / "review-render-receipt.json").write_text(json.dumps(review_renders,indent=2)+"\n",encoding="utf-8")
    board=Image.new("RGB",(1440,len(montage)*500),"#eeeeee");draw=ImageDraw.Draw(board)
    for i,(title,strip) in enumerate(montage):
        draw.text((18,i*500+8),title,fill="black",font=font);board.paste(strip,(0,i*500+45))
    board.save(out / "comparison.png")
    print(json.dumps({"gallery":str(out / "index.html"),"attempt_slots":sum(len(rs) for rs in rows.values()),
                      "scored_outputs":sum(has_judged_quality(r) for rs in rows.values() for r in rs),
                      "private_outputs_included":False}))


if __name__=="__main__":
    main(Path(sys.argv[1]),sys.argv[2]) if len(sys.argv)==3 else main()
