#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build an offline draggable graph preview and a portable credited media pack."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    media = ROOT / "artifacts/media"
    data = json.loads((media / "graph-nodes.json").read_text(encoding="utf-8"))
    positions = {"ian-buck": [190, 170], "nvidia": [190, 440], "fei-fei-li": [550, 170], "jia-deng": [550, 440], "alex-krizhevsky": [900, 170], "ilya-sutskever": [1080, 440], "geoffrey-hinton": [740, 440]}
    data["edges"] = [{"source": "ian-buck", "target": "nvidia", "label": "CUDA"}, {"source": "fei-fei-li", "target": "jia-deng", "label": "ImageNet"}, {"source": "alex-krizhevsky", "target": "ilya-sutskever", "label": "AlexNet"}, {"source": "alex-krizhevsky", "target": "geoffrey-hinton", "label": "AlexNet"}]
    for node in data["nodes"]:
        node["x"], node["y"] = positions[node["id"]]
    (media / "graph-nodes.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(ROOT / "artifacts/composition/d3.min.js", media / "d3.min.js")
    shutil.copyfile(ROOT / "artifacts/composition/D3-LICENSE.txt", media / "D3-LICENSE.txt")
    code = '''<!doctype html><html lang="en"><meta charset="utf-8"><title>CUDA and AlexNet media graph</title><style>body{margin:0;background:white;font:18px Arial;color:#333e48}svg{display:block;width:100vw;height:90vh}image{cursor:grab}text{pointer-events:none}p{margin:12px 24px}a{color:#9e1b32}</style><p>Drag a node; pan or zoom the canvas. <a href="credits.md">Media credits</a></p><svg viewBox="0 0 1280 620" role="img" aria-label="Selected CUDA, ImageNet and AlexNet contributors"></svg><script src="d3.min.js"></script><script>const data=DATA;const svg=d3.select('svg'),world=svg.append('g'),nodes=new Map(data.nodes.map(n=>[n.id,n]));svg.call(d3.zoom().scaleExtent([.5,3]).on('zoom',e=>world.attr('transform',e.transform)));const links=world.selectAll('g.edge').data(data.edges).join('g').attr('class','edge');links.append('line').attr('stroke','#cfcfcf').attr('stroke-width',2);links.append('text').text(d=>d.label).attr('text-anchor','middle').attr('fill','#696969').attr('font-size',17);const marks=world.selectAll('g.node').data(data.nodes).join('g').attr('class','node').attr('data-asset-id',d=>d.id);marks.append('image').attr('href',d=>d.image).attr('x',-60).attr('y',-60).attr('width',120).attr('height',120).attr('preserveAspectRatio','xMidYMid meet');marks.append('text').text(d=>d.label).attr('text-anchor','middle').attr('y',87).attr('font-size',20);marks.append('title').text(d=>d.role||d.label);function draw(){marks.attr('transform',d=>`translate(${d.x} ${d.y})`);links.select('line').attr('x1',d=>nodes.get(d.source).x).attr('y1',d=>nodes.get(d.source).y+65).attr('x2',d=>nodes.get(d.target).x).attr('y2',d=>nodes.get(d.target).y-65);links.select('text').attr('x',d=>(nodes.get(d.source).x+nodes.get(d.target).x)/2+35).attr('y',d=>(nodes.get(d.source).y+nodes.get(d.target).y)/2)}marks.call(d3.drag().on('drag',(e,d)=>{d.x=e.x;d.y=e.y;draw()}));draw();</script></html>'''.replace("DATA", json.dumps(data, ensure_ascii=False))
    (media / "graph-preview.html").write_text(code, encoding="utf-8")
    output = ROOT / "artifacts/packages/cuda-alexnet-media.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(media.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(media))
        archive.write(ROOT / "logos-and-portraits.md", "logos-and-portraits.md")
    print(json.dumps({"ok": True, "nodes": len(data["nodes"]), "edges": len(data["edges"]), "archive": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
