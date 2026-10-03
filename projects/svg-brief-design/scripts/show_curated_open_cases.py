#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Display the preserved tied and unresolved judgments without rescoring."""
import hashlib
import html
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svg-art-v5"
NAMES = {"004": "Android head", "011": "Circular ornament", "019": "HUD bar", "020": "Industrial label", "024": "Vintage oscillation", "030": "Space insignia"}
DIMENSIONS = {"silhouette_intent": "Silhouette", "composition_space": "Composition and negative space", "shape_rhythm": "Shape rhythm", "craft_finish": "Contour and junction finish", "information_hierarchy": "Hierarchy", "style_coherence": "Style coherence"}


def main():
    source = ROOT / "results.json"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    results = json.loads(source.read_text(encoding="utf-8"))
    generated = [r for r in results["records"] if r["kind"] == "generated"]
    selected = [r for r in generated if r["choices"]["overall"] in {"parity", "unknown"}]
    counts = {key: sum(r["choices"]["overall"] == value for r in selected) for key, value in [("unresolved", "unknown"), ("ties", "parity")]}
    if counts != {"unresolved": 4, "ties": 4}:
        raise ValueError("The preserved decision set changed; inspect before displaying")
    out = ROOT / "open-cases-v5.2"
    out.mkdir(exist_ok=True)
    cards = []
    manifest = []
    for row in sorted(selected, key=lambda r: (r["choices"]["overall"] != "unknown", generated.index(r))):
        group = "unresolved" if row["overall_preference_unresolved"] else "ties"
        number = [r["id"] for r in generated if r["task"] == row["task"]].index(row["id"]) + 1
        title = NAMES[row["task"].split("--")[0][-3:]] + f" · attempt {number}"
        low, high = row["score_interval_100"]
        score = f"{low:g}" if low == high else f"{low:g}–{high:g}"
        label = "Global preference unresolved" if group == "unresolved" else "Overall tie"
        detail = "Also unresolved: " + ", ".join(DIMENSIONS[d] for d in row["uncertain_dimensions"]) if row["uncertain_dimensions"] else "All six dimension choices are resolved."
        # Replace anonymous sides only for display; the original blinded evidence stays unchanged.
        side = row["candidate_side"]
        dim_rows = []
        for key, name in DIMENSIONS.items():
            choice = row["choices"][key]
            meaning = "Unresolved" if choice == "unknown" else "Comparable" if choice == "parity" else ("Generated" if choice.startswith(side + "_") else "Purchased") + (" clearly stronger" if choice.endswith("_clear") else " slightly stronger")
            dim_rows.append(f"<tr><th>{name}</th><td>{meaning}</td></tr>")
        pair = "".join(f'<figure><a href="../review-v5.2/{row["id"]}-{kind}.svg" target="_blank"><img src="../review-v5.2/{row["id"]}-{kind}.png" alt="{name}: {html.escape(title)}"></a><figcaption>{name}</figcaption></figure>' for kind, name in [("anchor", "Purchased original"), ("candidate", "Luna + skill")])
        cards.append(f'''<article data-group="{group}" id="{row['id']}">
<header><h2>{html.escape(title)}</h2><span class="badge {group}">{label}</span></header>
<div class="pair">{pair}</div>
<div class="score">Generated dimension score: <b>{score}</b> <span>/ 100</span></div>
<details><summary>View request, reasoning and decisions</summary>
<p class="note">The overall verdict is separate from the weighted dimension score. {html.escape(detail)}</p>
<blockquote lang="es">{html.escape(row['brief'])}</blockquote>
<p>{html.escape(row['comparison']['overall_contrast'])}</p>
<p class="note">Original blind labels: generated = {side}; purchased = {'B' if side == 'A' else 'A'}.</p>
<table>{''.join(dim_rows)}</table>
<a href="../review-v5.2/index.html#{row['id']}">Open full case</a>
</details></article>''')
        manifest.append({"id": row["id"], "title": title, "group": group, "score_interval_100": [low, high], "uncertain_dimensions": row["uncertain_dimensions"]})
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SVG review — ties and unresolved cases</title>
<style>*{box-sizing:border-box}body{margin:0;background:#edf1f6;color:#182639;font:14px/1.45 system-ui,sans-serif}main{max-width:1380px;margin:auto;padding:18px 22px 30px}h1{font-size:27px;margin:0 0 6px;letter-spacing:-.5px}.intro{margin:4px 0 12px;color:#596b80;max-width:1100px}nav{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 15px}button{font:600 14px system-ui;padding:9px 17px;border:1px solid #b9c6d6;border-radius:8px;background:white;color:#344c69;cursor:pointer}button[aria-pressed=true]{background:#203e62;color:white;border-color:#203e62}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}article{background:white;border:1px solid #d5deea;border-radius:12px;overflow:hidden}article[hidden]{display:none}header{padding:12px 15px 3px;display:flex;align-items:center;justify-content:space-between;gap:10px}h2{font-size:15px;margin:0}.badge{font-size:10px;font-weight:700;padding:4px 7px;border-radius:5px;white-space:nowrap}.unresolved{background:#fff0d0;color:#79500d}.ties{background:#e1eaf9;color:#355989}.pair{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:5px 15px 0}figure{margin:0}img{width:100%;height:180px;object-fit:contain;display:block}figcaption{text-align:center;font-size:11px;color:#62758c;margin:3px 0 0}.score{padding:9px 15px 7px;font-size:12px}.score b{font-size:17px;color:#1c334f}.score span{color:#6d7b8c}details{border-top:1px solid #e8edf4;padding:9px 15px;font-size:12px}summary{cursor:pointer;color:#285789;font-weight:600}.note{color:#65758b}blockquote{margin:13px 0;border-left:3px solid #ccd6e3;padding-left:12px}table{border-collapse:collapse;width:100%;margin:12px 0}th,td{text-align:left;padding:6px;border-bottom:1px solid #e5eaf0}a{color:#225d9c}footer{color:#68788b;font-size:12px;margin:14px 0}.legend{font-weight:600;color:#365170}@media(max-width:780px){main{padding:16px 12px}.grid{grid-template-columns:1fr}header{flex-wrap:wrap}img{height:190px}}
</style><main><h1>Ties and unresolved SVG judgments</h1>
<p class="intro">Eight preserved comparisons. <span class="legend">Purchased original on the left · Luna + skill on the right.</span> Overall preference and dimension score are separate judgments; 90 denotes parity with the curated anchor on the dimension scale.</p>
<nav aria-label="Review category"><button data-filter="unresolved" aria-pressed="true">Unresolved · 4</button><button data-filter="ties" aria-pressed="false">Ties · 4</button><button data-filter="all" aria-pressed="false">All · 8</button></nav>
<div class="grid">''' + "".join(cards) + '''</div><footer>Existing v5.2 evidence only. No new scoring or image generation. Click a drawing to open its editable SVG. <a href="../review-v5.2/index.html">Full 18-case gallery</a></footer></main>
<script>function show(group){if(!['unresolved','ties','all'].includes(group))group='unresolved';document.querySelectorAll('article').forEach(x=>x.hidden=group!=='all'&&x.dataset.group!==group);document.querySelectorAll('button[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.filter===group)))}document.querySelectorAll('button[data-filter]').forEach(x=>x.addEventListener('click',()=>{location.hash=x.dataset.filter}));addEventListener('hashchange',()=>show(location.hash.slice(1)));show(location.hash.slice(1));</script></html>'''
    (out / "index.html").write_text(page, encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps({"results_sha256": before, "counts": counts, "cases": manifest}, indent=2) + "\n", encoding="utf-8")
    if hashlib.sha256(source.read_bytes()).hexdigest() != before:
        raise ValueError("Source results changed")
    for row in selected:
        for kind in ["anchor", "candidate"]:
            for suffix in ["png", "svg"]:
                if not (ROOT / "review-v5.2" / f"{row['id']}-{kind}.{suffix}").is_file():
                    raise ValueError("A linked artwork is missing")
    print(json.dumps({"gallery": str(out / "index.html"), "counts": counts, "source_results_unchanged": True}))


if __name__ == "__main__":main()
