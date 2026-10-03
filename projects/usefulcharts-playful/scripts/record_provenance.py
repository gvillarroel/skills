#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind generated sheets and selected reference photographs to local hashes."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def main():
    refs=json.loads((ROOT/'artifacts/references/selected.json').read_text());prompts=json.loads((ROOT/'design/image-prompts.json').read_text())
    retained=[]
    for k in ['mariner-38','viking-38','viking-41','pathfinder-41','nozomi-39','soviet-43']:
        ref=next(r for r in refs if r['id']==k);ref['path']='artifacts/references/'+ref['path'];retained.append(ref)
    retained.append(dict(id='mars96-dlr',page='https://www.planetary.org/space-images/mars-96-orbiter',url='https://planetary.s3.amazonaws.com/web/assets/pictures/Mars96_Model.jpg',path='artifacts/references/mars96-dlr.jpg',credit='DLR Institute of Planetary Exploration via The Planetary Society',kind='computer model'))
    generated=[]
    for k in ['instruments','bsd','species','mars']:
        path=ROOT/'artifacts/images'/f'{k}-sheet.png';generated.append(dict(id=k+'-sheet',path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),method='Built-in image generation',prompt=prompts[k]['prompt'],kind={'instruments':'Illustrative real-world instrument specimens','bsd':'Period-inspired hardware archetypes, not exact machines','species':'Generic fictional species representatives, not named portraits','mars':'Interpretive reference-guided spacecraft illustrations'}[k],reference_ids=['mariner-38','viking-38','viking-41','pathfinder-41'] if k=='mars' else []))
    for r in retained:r['sha256']=hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()
    manifest=dict(date='2026-09-13',generated_assets=generated,primary_reference_assets=retained,reused_starship_art=dict(manifest='projects/star-trek-starships/design/image-generation.json',manifest_sha256=hashlib.sha256((REPO/'projects/star-trek-starships/design/image-generation.json').read_bytes()).hexdigest(),note='Existing accepted reference-guided ship artwork and the original Enterprise reference photograph are reused. No blocked Enterprise-D generation was retried.'),placement_note='SVG viewports and blend modes compose intact original bitmaps. Instrument object bounds were manually measured. The Mariner viewport excludes a neighboring antenna fragment while retaining its complete wingtip. Illustrations do not establish construction dates or operational success.')
    (ROOT/'design/artwork-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(generated_sheets=len(generated),retained_primary_references=len(retained))))
if __name__=='__main__':main()
