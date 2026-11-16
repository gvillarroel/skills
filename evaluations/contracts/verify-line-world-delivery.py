#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently inspect isolated delivery outputs and actual fixture media."""
import argparse
import array
import hashlib
import json
import math
import subprocess
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def inspect(run):
    root = run / 'workspace/artifacts'; findings = []
    def require(condition, label):
        if not condition: findings.append(label)
    ready = read(root / 'ready.json'); blocked = read(root / 'blocked.json'); stale = read(root / 'stale.json')
    checks = read(root / 'checks.json'); ui = read(root / 'ui-next.json'); video = root / '01-method.mp4'
    require(ready.get('ok') is True and ready.get('status') == 'ready', 'ready-status')
    expected = {'currentRevision', 'nativeProjectSaved', 'nativeSceneInventory', 'nativeSceneVisualsReviewed',
                'nativeNarrationPresent', 'nativeExportProvenance', 'downloadedBytesBound', 'localExportVerified',
                'cloudFileMetadata', 'cloudPlayback', 'cloudDownload', 'continuityReviewed'}
    require(set(ready['checks']) == expected and all(ready['checks'].values()), 'complete-delivery-checks')
    require(ready['pending'] == [], 'ready-has-no-pending-actions')
    require(blocked.get('ok') is False and blocked['checks']['cloudPlayback'] is False and
            any(p['check'] == 'cloudPlayback' for p in blocked['pending']), 'missing-playback-not-waived')
    require(stale.get('ok') is False and stale['checks']['currentRevision'] is False, 'stale-revision-not-waived')
    require(all(checks.get(k) is True for k in ('ok', 'mediaCheckReused', 'blockedForPlayback', 'staleRevisionRejected', 'syntheticOnly')), 'rehearsal-summary')
    require(ready.get('mediaCheckReused') is True, 'actual-cached-ready-report')
    for key, kind in {'diffOnly': 'read-full-state', 'background': 'foreground-tab', 'delayedDialog': 'observe-upload-result',
                      'nativeDialog': 'fill-native-filename', 'inserted': 'verify-inserted-scene'}.items():
        require(ui[key]['kind'] == kind, 'ui-' + key)
    require('index' not in ui['nativeDialog'] and ui['nativeDialog']['file'] == 'C:/fixture/01-method.mp4', 'native-dialog-no-stale-index')
    movie_url = 'https://drive.google.com/file/d/test-export/view'; project_url = 'https://docs.google.com/videos/d/test-project/edit'
    text = (root / 'ready.md').read_text(encoding='utf-8')
    require(movie_url in text and project_url in text and text.index(movie_url) < text.index(project_url), 'cloud-first-handoff')
    require(ready['videoUrl'] == movie_url and ready['projectUrl'] == project_url, 'exact-observed-links')
    require('incomplete' in (root / 'blocked.md').read_text(encoding='utf-8').lower(), 'blocked-handoff-is-explicit')
    require(ready['videoSha256'] == hashlib.sha256(video.read_bytes()).hexdigest() and ready['bytes'] == video.stat().st_size, 'actual-byte-binding')
    probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)],
                                      capture_output=True, text=True, check=True).stdout)
    visual = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    require(visual['width'] == 320 and visual['height'] == 180 and visual['r_frame_rate'] == '30/1', 'native-fixture-geometry')
    require(abs(float(probe['format']['duration']) - 2) < .1, 'native-fixture-duration')
    decoded = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'], capture_output=True)
    require(decoded.returncode == 0 and not decoded.stderr.strip(), 'independent-full-decode')
    pixels = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-frames:v', '1', '-vf', 'scale=160:90', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
                            capture_output=True, check=True).stdout
    rgb = list(zip(pixels[0::3], pixels[1::3], pixels[2::3])); total = len(rgb)
    require(sum(min(p) > 235 for p in rgb) / total > .5, 'predominantly-white-composition')
    require(sum(r > 1.4*g and r > 1.2*b and r > 100 for r, g, b in rgb) > 3, 'visible-red-mark')
    require(sum(max(p)-min(p) < 8 and 35 < sum(p)/3 < 225 for p in rgb) > 30, 'visible-gray-object')
    audio_bytes = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-t', '0.5', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'],
                                 capture_output=True, check=True).stdout
    samples = array.array('h', audio_bytes)
    energy = math.sqrt(sum(v*v for v in samples) / max(1, len(samples)))
    crossings = sum(a <= 0 < b for a, b in zip(samples, samples[1:]))
    require(energy > 100 and abs(crossings / (len(samples)/8000) - 440) < 20, 'audible-440-hz-fixture-tone')
    review = run / 'review'; review.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '1', '-i', str(video), '-frames:v', '1', str(review / 'fixture.png')], capture_output=True, check=True)
    report = {'ok': not findings, 'findings': findings, 'videoBytes': video.stat().st_size,
              'videoSha256': hashlib.sha256(video.read_bytes()).hexdigest(), 'scope': 'Evaluator-side outputs, media decode, pixels and tone; no live account claim.'}
    (run / 'artifact-quality.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('run', type=Path, nargs='+'); args = parser.parse_args()
    results = [{'run': str(run), **inspect(run)} for run in args.run]
    print(json.dumps(results)); return 0 if all(r['ok'] for r in results) else 2


if __name__ == '__main__':
    raise SystemExit(main())
