#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Record the unedited generated sheet and verify the source snapshot remains intact."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'
SPECIMENS=[
    'Wooden card catalog: retrieval and external indexing',
    'Navy switchboard: tool contracts and routing',
    'Neural lattice in glass: learned representations and model proposals',
    'Field manual and toolkit: reusable skills and instructions',
    'Control booth: policy and authority',
    'Tape recorder: durable execution traces',
    'Balance: paired comparison and evaluation',
    'Laboratory bench: verification and fitness checks',
    'Computer enclosure: an isolated workspace',
    'Evidence folios: provenance and retained feedback',
    'Rail junction: coordination, branches and coupled roles',
    'Sealed archive: held-aside evaluation data',
]
BRIEF='''Create one cohesive 4 by 3 specimen sheet of twelve distinct conceptual workshop objects, in the row-major order recorded below. Use a consistent elevated three-quarter camera, upper-left soft studio light, tactile editorial museum miniatures and a warm ivory field approximately #F7F2E8. Use navy, brass, coral, turquoise, sage and lilac. Keep complete objects inside equally sized cells with generous crop margins, subtle shadows, no labels, numbers, logos, borders, arrows or connector lines. Make each specimen recognizable at approximately 200 pixels. These are conceptual explanatory objects, not claimed photographs of historical hardware.'''

def main():
    sheet=OUT/'images/specimen-sheet.png'
    raw=sheet.read_bytes();w,h=Image.open(sheet).size
    provenance=dict(tool='image_gen.imagegen',generated_date='2026-09-13',asset='specimen-sheet.png',sha256=hashlib.sha256(raw).hexdigest(),pixels=[w,h],reference_images=[],prompt_record_type='Normalized art-direction record, not a verbatim tool-call transcript',art_direction=BRIEF,specimens=[dict(index=i,description=s,viewport=[(i%4)*w/4,(i//4)*h/3,w/4,h/3]) for i,s in enumerate(SPECIMENS)],postprocessing='No raster edits. Each SVG embeds the intact sheet once and uses nested SVG viewports to select specimens. The original generated file was copied without modification.',disclosure='AI-generated conceptual specimens; not documented historical objects or software product logos.')
    (OUT/'images/provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    source=json.loads((OUT/'data/sources.json').read_text())
    results=[]
    for s in source['files']:
        p=Path(source['source_repository'])/s['path']
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        results.append(dict(path=s['path'],sha256=digest,unchanged=digest==s['sha256']))
    assert all(r['unchanged'] for r in results)
    (OUT/'reviews/source-integrity.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(dict(source_files_unchanged=len(results),sheet_pixels=[w,h],specimens=12)))


if __name__=='__main__':main()
