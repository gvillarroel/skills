#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Freeze raw poster candidates for preregistered isolated visual criticism."""
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from artwork import ROOT,REPO,art,save,render

def main():
    inputs=ROOT/'artifacts/evaluation-input';inputs.mkdir(parents=True,exist_ok=True)
    old=REPO/'projects/usefulcharts-cross-domain/artifacts/revision-2/instruments'
    new=ROOT/'artifacts/revision-2/instruments'
    source=json.loads((old/'source.json').read_text(encoding='utf-8'))
    baseline=ROOT/'artifacts/review-candidates/p';baseline.mkdir(parents=True,exist_ok=True)
    shutil.copy2(old/'poster.svg',baseline/'poster.svg');render(baseline,(18,215,1100,1100))
    header=ROOT/'artifacts/review-candidates/q';root=ET.parse(old/'poster.svg').getroot()
    a=art(root,ROOT/'artifacts/images/instruments-sheet.png',(944,32,160,115),'header-specimen',['122'],['1'],'Kalimba title decoration',(332,0,300,318))
    save(root,header,[a],source);render(header,(18,215,1100,1100))
    render(new,(32,215,1510,1100))
    for case,path in [('p',baseline),('q',header),('r',new)]:
        shutil.copy2(path/'preview.png',inputs/f'candidate-{case}.png');shutil.copy2(path/'detail.png',inputs/f'candidate-{case}-detail.png')
    (inputs/'source.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs.iterdir() if p.is_file()}
    (ROOT/'artifacts/evaluation-input-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(input_files=len(manifest))))
if __name__=='__main__':main()
