#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Create nearest-neighbor raw-pixel crops without altering native screenshots."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run_id')
args = parser.parse_args()
folder = ROOT / 'projects/diagram-compactness/artifacts/reviews' / args.run_id / 'independent-deck'
folder.resolve().relative_to(ROOT)
browser = json.loads((folder / 'browser.json').read_text(encoding='utf-8'))
rows = []
for state in browser['states']:
    if state['state'] not in ['resized', 'reduced-motion']:
        continue
    graph = state['graphs'][0]
    label = next(label for label in graph['labels'] if label['text'] == 'Failed sample' and label.get('relationshipRole'))
    bounds, canvas = label['bounds'], graph['bounds']
    x, y = bounds['x'] + canvas['x'], bounds['y'] + canvas['y']
    crop = (int(x - 50), int(y - 60), int(x + bounds['width'] + 110), int(y + bounds['height'] + 70))
    source = folder / f"{state['state']}.png"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target = folder / f"{state['state']}-caption-4x.png"
    with Image.open(source) as image:
        image.crop(crop).resize(((crop[2]-crop[0])*4, (crop[3]-crop[1])*4), Image.Resampling.NEAREST).save(target)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    rows.append({'state': state['state'], 'sourceSha256': digest, 'crop': crop, 'nearestPixelCrop': target.name, 'sourceUnchanged': True})
(folder / 'caption-pixel-crops.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
print(json.dumps({'ok': True, 'run': args.run_id, 'crops': len(rows)}))
