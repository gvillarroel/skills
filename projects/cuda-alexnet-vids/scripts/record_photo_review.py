#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind observed photographic-revision review notes to the current movie and source."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = [
    'The opening AlexNet item and three conceptual inputs remain separated, with white text on the active red item and an adjacent guide.',
    'The two full-frame Mermaid pipelines retain readable labels and unobstructed connectors. These explain feature extraction and remain diagrams.',
    'The real CPU and GTX 580 photographs preserve complete silhouettes in fixed gray/white dither. Ian Buck and his contribution remain readable in the full-size source view; the guide clears both photographs and captions.',
    'Input values, kernel, thread blocks and output values remain distinct. Task partitioning is appropriately diagrammatic; cue travel and the two neighboring joins retain continuity.',
    'Thirty photographs extracted from the paper replace generic image pictograms. They form a quiet image field beside separate scale values; Fei-Fei Li and Jia Deng retain names and contributions. The published-samples caption avoids asserting an exact 2012 file inventory.',
    'The actual paper leopard photograph remains recognizable after restrained pixelation. Full-size C1-C5/F1-F3 labels, three contributor captions and layer groups remain clear. No photograph is substituted for the explanatory network architecture.',
    'Two instances of the verified 3 GB GTX 580 model photograph retain fan, shroud and ports. The center diagram explains model partitioning. The guide visits card, memory, model split and duration beside their visible bounds; the encoded full-size 145.533-second frame was inspected.',
    'The augmentation region uses four real photograph variants with reviewed crops and flips. ReLU and dropout retain their mechanism diagrams. Three full-height sections stay balanced; active guide routes clear photographs and text.',
    'Primary-red 15.3 percent and secondary-gray 26.2 percent bars remain readable, with a separate 10.9 pp annotation and top-five illustration. The incoming join includes the actual augmentation photographs.',
    'The closing conceptual convergence uses an abstract document stack for data, not a fake landscape photograph. The AlexNet item, dates, guide and outgoing hold remain separated.'
]


def main():
    root = ROOT / 'artifacts/reviews/photo-review'
    report = json.loads((root / 'report.json').read_text(encoding='utf-8'))
    assert len(report['scenes']) == len(NOTES)
    record = {
        'videoSha256': report['videoSha256'], 'sourceSha256': report['source']['sourceSha256'],
        'scope': 'Actual encoded reading/cue/join montages for all ten scenes, plus full-size photographic GPU encoded frame and contributor/architecture source views. Separate automated checks cover all frames. This is a locally assembled film with unchanged native Google Vids narration; no native final export is claimed.',
        'scenes': [{'id': scene['id'], 'reviewed': True, 'notes': note} for scene, note in zip(report['scenes'], NOTES, strict=True)]
    }
    (root / 'manual-review.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    previous = json.loads((ROOT / 'artifacts/revisions/subject-first-0200/resume.json').read_text(encoding='utf-8'))
    previous['localFinalVideo'] = 'projects/cuda-alexnet-vids/artifacts/videos/cuda-alexnet-photographic-local.mp4'
    previous['revision'] = 'photo-0210'
    previous['voiceGeneration'] = 'Keep the approved subject-first native voices and measured timing; decoded PCM is byte-identical. Do not regenerate speech for this visual-only revision.'
    for item in previous['uploads']:
        path = ROOT / 'artifacts/videos/clips' / Path(item['file']).name
        item.update(file=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), status='pending-current-upload')
    previous['uploads'][5]['note'] = 'Native scene 6 contains the earlier subject-first visual, which still needs this photographic replacement.'
    (ROOT / 'artifacts/revisions/photo-0210/resume.json').write_text(json.dumps(previous, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'reviewedScenes': len(NOTES), 'pendingNativeReplacements': len(previous['uploads'])}))


if __name__ == '__main__': main()
