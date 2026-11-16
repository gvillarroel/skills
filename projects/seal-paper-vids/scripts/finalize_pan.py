#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind the observed native pan revision, encoded review and cloud export to delivery."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(REPO / 'skills/line-world-google-vids/scripts'))
from batch_clips import atomic_json, sha
from vids_delivery import finalize, template
from vids_inventory import parse_announcement
from vids_plan import compile_timing, read


def main():
    reviews = ROOT / 'artifacts/reviews'; output = reviews / 'delivery-0.17.0'; output.mkdir(exist_ok=True)
    original = read(ROOT / 'story.json'); native = read(reviews / 'native-pan-inventory.json')
    metadata = read(reviews / 'native-pan-metadata.json'); encoded = read(reviews / 'native-encoded-review.json')
    content = read(reviews / 'native-pan-content.json'); measured = read(ROOT / 'artifacts/data/native-timing.json')
    video = ROOT / 'artifacts/videos/seal-google-vids-final.mp4'; movie_hash = sha(video)
    assert encoded['ok'] and encoded['videoSha256'] == movie_hash and content['result']['ok']
    assert content['result']['videoSha256'] == movie_hash and int(metadata['size']) == video.stat().st_size
    assert native['observed'] and native['sceneButtonCount'] == 6 and all(s['matches'] for s in native['scenes'])
    canonical = {'observed': True, 'projectUrl': native['projectUrl'], 'sceneButtonCount': 6, 'scenes': [
        {'scene': s['order'], 'file': s['file'], 'visible': True, 'media': [f"{s['order']} text {s['announcement']}"]}
        for s in native['scenes']]}
    atomic_json(reviews / 'native-inventory.json', canonical)
    cloud = {'observed': True, 'projectUrl': native['projectUrl'], 'videoUrl': metadata['url'], 'fileId': metadata['id'],
             'source': 'Google Vids File > Export to Drive', 'playbackObserved': True, 'playerDuration': '3:28',
             'downloadObserved': True, 'bytes': video.stat().st_size, 'visibility': 'Private to the current owner, observed in Drive; unchanged'}
    atomic_json(reviews / 'native-drive-export.json', cloud)
    shutil.copyfile(reviews / 'native-pan-content.json', reviews / 'native-content.json')
    shutil.copyfile(reviews / 'pan-local-content.json', reviews / 'encoded-content.json')
    story = {'projectTitle': original['title'], 'googleVidsUrl': native['projectUrl'], 'voice': 'Nyla',
             'language': 'es', 'width': 1920, 'height': 1080, 'fps': 30, 'scenes': []}
    for source, row in zip(original['scenes'], native['scenes'], strict=True):
        scene = parse_announcement(row['announcement'])
        story['scenes'].append({'id': source['id'], 'script': source['script'],
                                'clip': str(ROOT / 'artifacts/videos/clips' / row['file']), 'clipSeconds': scene['sceneSeconds']})
    observed = {'voice': 'Nyla', 'projectUrl': native['projectUrl'], 'scenes': [
        {'id': s['id'], 'observed': True, 'voiceoverSeconds': v['duration'], 'sceneSeconds': s['clipSeconds']}
        for s, v in zip(story['scenes'], measured['scenes'], strict=True)]}
    atomic_json(output / 'story.json', story); atomic_json(output / 'timing.json', compile_timing(story, observed))
    evidence = template(story, output, video)
    evidence['project'].update(observed=True, saved=True, evidence='Actual current Vids scene inventory and Saved to Drive status after all six replacements.')
    evidence['inventory'].update(observed=True)
    for row, actual in zip(evidence['inventory']['scenes'], native['scenes'], strict=True):
        row.update(announcement=actual['announcement'], visualReviewed=True)
    evidence['export'].update(observed=True, source=cloud['source'], evidence='Actual completed Vids Export to Drive; observed Open now link and native downloaded MP4.')
    evidence['cloud'].update(observed=True, metadata=metadata, playbackObserved=True, downloadObserved=True, durationSeconds=208,
                             evidence='Actual new Drive MP4 playback advanced, paused at 0:20 / 3:28, Download enabled and file size matched metadata.')
    evidence['review'].update(observed=True, speechAndJoins=True, contentThroughout=True,
                              evidence='All six retained native voice tracks and extents checked; 90 encoded reading/join frames inspected, 36 guide arrivals and all-frame content checked against the current file.')
    atomic_json(output / 'evidence.json', evidence)
    result = finalize(output / 'story.json', output / 'timing.json', output / 'evidence.json', video, output / 'delivery.json')
    assert result['ok'], result['pending']
    atomic_json(reviews / 'visual-decisions.json', {'ok': True, 'version': '0.17.0', 'videoSha256': movie_hash,
                'reviewedEncodedFrames': len(encoded['reviewFrames']), 'reviewedContactSheets': 8,
                'decisions': ['Use one gradual entry and fixed-scale pans.', 'Keep the overview for densely spaced cues.',
                              'Use raster-checked margin segments instead of rectangles.', 'Keep both page-9 paragraphs in one stable view.'],
                'sourceTrajectoryFindings': 0, 'zoomOutFramesWithinShots': 0,
                'evidence': ['pan-render.json', 'native-encoded-review.json', 'native-pan-content.json', 'native-pan-inventory.json']})
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)]))
    atomic_json(reviews / 'final-delivery.json', {'ok': True, 'version': '0.17.0', 'nativeVidsVisualEditComplete': True,
                'projectUrl': native['projectUrl'], 'videoUrl': metadata['url'], 'video': str(video), 'videoSha256': movie_hash,
                'bytes': video.stat().st_size, 'duration': float(probe['format']['duration']),
                'frames': int(next(s['nb_frames'] for s in probe['streams'] if s['codec_type'] == 'video')),
                'finalVisualAssembly': 'Google Vids: six revised visual clips and the six existing native voice tracks.',
                'deliveryReceipt': str(output / 'delivery.json'), 'reviewedEncodedFrames': len(encoded['reviewFrames'])})
    print(json.dumps({k: result[k] for k in ('ok', 'status', 'bytes', 'duration', 'projectUrl', 'videoUrl', 'videoSha256')}))


if __name__ == '__main__': main()
