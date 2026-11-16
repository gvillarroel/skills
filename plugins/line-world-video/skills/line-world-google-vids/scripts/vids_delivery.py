#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compile observed native/cloud evidence and cached media checks into a delivery receipt."""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from batch_clips import atomic_json, sha, signature
from vids_inventory import inspect as inspect_inventory
from vids_plan import read, validate_story, verify_export

VERSION = 1
SCOPE = ('Supplied native/cloud observations plus local file verification. '
         'This utility does not operate Google Vids, authenticate, upload, '
         'observe playback, or change sharing. Observations remain attestations.')


def project_id(url):
    match = re.fullmatch(r'https://docs\.google\.com/videos/d/([\w-]+)/(?:edit|preview)(?:[?#].*)?', str(url))
    return match[1] if match else None


def cloud_file_id(url):
    parsed = urlparse(str(url))
    if parsed.scheme != 'https' or parsed.netloc != 'drive.google.com':
        return None
    match = re.fullmatch(r'/file/d/([\w-]+)/view', parsed.path)
    query = parse_qs(parsed.query)
    if match and not (set(query) - {'usp'}):
        return match[1]
    values = query.get('id', [])
    return values[0] if parsed.path == '/open' and len(values) == 1 and not (set(query) - {'id', 'usp'}) else None


def revision(story, base):
    clips = []
    for scene in story['scenes']:
        value = scene.get('clip') or scene.get('sourceClip')
        path = Path(value) if value else None
        if path and not path.is_absolute():
            path = Path(base) / path
        clips.append({'id': scene['id'], 'sha256': sha(path) if path and path.is_file() else None})
    return signature({'story': story, 'clips': clips})


def template(story, base, video=None):
    return {
        'schemaVersion': VERSION, 'revision': revision(story, base),
        'project': {'url': story.get('googleVidsUrl', ''), 'observed': False, 'saved': False, 'evidence': ''},
        'inventory': {'observed': False, 'sceneButtonCount': len(story['scenes']), 'scenes': [
            {'id': s['id'], 'order': i + 1, 'announcement': '', 'visualReviewed': False}
            for i, s in enumerate(story['scenes'])]},
        'export': {'observed': False, 'source': 'Google Vids File > Export to Drive',
                   'projectUrl': story.get('googleVidsUrl', ''),
                   'localSha256': sha(video) if video and Path(video).is_file() else '', 'evidence': ''},
        'cloud': {'observed': False, 'metadata': {}, 'playbackObserved': False,
                  'downloadObserved': False, 'durationSeconds': None,
                  'durationResolutionSeconds': 1, 'evidence': ''},
        'review': {'observed': False, 'speechAndJoins': False, 'contentThroughout': False, 'evidence': ''}
    }


def attested(value):
    return value.get('observed') is True and isinstance(value.get('evidence'), str) and bool(value['evidence'].strip())


def assess(story, evidence, media, video_hash, current_revision):
    """Pure receipt assessment. Missing evidence yields specific pending actions, never success."""
    checks = {}; pending = []
    def check(key, passed, action):
        checks[key] = bool(passed)
        if not passed:
            pending.append({'check': key, 'next': action})

    project = evidence.get('project', {}); native = evidence.get('inventory', {})
    exported = evidence.get('export', {}); cloud = evidence.get('cloud', {})
    review = evidence.get('review', {}); metadata = cloud.get('metadata', {})
    pid = project_id(project.get('url')); requested = story.get('googleVidsUrl')
    check('currentRevision', evidence.get('schemaVersion') == VERSION and evidence.get('revision') == current_revision,
          'Prepare a new receipt for the current story and clip bytes; retain the old evidence.')
    check('nativeProjectSaved', attested(project) and project.get('saved') is True and pid and (not requested or project_id(requested) == pid),
          'Observe the intended Vids URL and Saved to Drive status.')
    try:
        inventory = inspect_inventory(story, native)
    except (ValueError, KeyError, TypeError):
        inventory = {'ok': False, 'scenes': [], 'findings': [{'kind': 'missing-fresh-native-announcements'}]}
    check('nativeSceneInventory', native.get('observed') is True and inventory['ok'],
          'Select every current scene; record its fresh exact announcement, media and duration.')
    rows = native.get('scenes', [])
    check('nativeSceneVisualsReviewed', len(rows) == len(story['scenes']) and
          [r.get('id') for r in rows] == [s['id'] for s in story['scenes']] and all(r.get('visualReviewed') is True for r in rows),
          'Inspect the actual current pixels of every scene; filenames alone do not prove replacement.')
    check('nativeNarrationPresent', len(inventory['scenes']) == len(story['scenes']) and
          all(s['audioClipsStarting'] >= 1 for s in inventory['scenes']),
          'Verify retained native narration in each visual scene.')
    check('nativeExportProvenance', attested(exported) and pid and project_id(exported.get('projectUrl')) == pid and
          exported.get('source') in ('Google Vids File > Export to Drive', 'Google Vids File > Download'),
          'Export the complete intended native project and record the observed action.')
    check('downloadedBytesBound', bool(video_hash) and exported.get('localSha256') == video_hash,
          'Bind the observed native download to its actual SHA-256; do not substitute a local render.')
    check('localExportVerified', media.get('ok') is True and
          all(media.get('checks', {}).get(k) is True for k in ('videoPresent', 'audioPresent', 'fullDecode', 'durationMatches')) and
          all(not story.get(k) or media.get(k) == story[k] for k in ('width', 'height')),
          'Verify the actual MP4, audio, full decode, dimensions and measured duration.')
    url = metadata.get('webViewLink') or metadata.get('url') or ''
    mime = metadata.get('mimeType') or metadata.get('mime_type')
    try:
        size_matches = int(metadata.get('size', 0)) == media.get('bytes') and media.get('bytes', 0) > 0
    except (ValueError, TypeError):
        size_matches = False
    check('cloudFileMetadata', attested(cloud) and mime == 'video/mp4' and size_matches and
          bool(metadata.get('id')) and cloud_file_id(url) == metadata.get('id'),
          'Read metadata for the observed exported Drive file ID: stable URL, MP4 type and matching byte size.')
    seconds = cloud.get('durationSeconds'); resolution = cloud.get('durationResolutionSeconds', 1)
    numeric = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
    duration_matches = (numeric(seconds) and numeric(resolution) and 0 < resolution <= 1 and
                        numeric(media.get('duration')) and abs(seconds - media['duration']) <= max(resolution, .1))
    check('cloudPlayback', cloud.get('observed') is True and cloud.get('playbackObserved') is True and duration_matches,
          'Open that Drive MP4, play it and record its visible duration with at most one-second resolution.')
    check('cloudDownload', cloud.get('observed') is True and cloud.get('downloadObserved') is True,
          'Observe the enabled Download action on the same exported Drive MP4.')
    check('continuityReviewed', attested(review) and review.get('speechAndJoins') is True and review.get('contentThroughout') is True,
          'Review speech endings, scene joins and explanatory content throughout the downloaded movie.')
    ready = all(checks.values())
    stage = ('ready' if ready else 'native-scenes-incomplete' if not all(checks[k] for k in
             ('currentRevision', 'nativeProjectSaved', 'nativeSceneInventory', 'nativeSceneVisualsReviewed', 'nativeNarrationPresent'))
             else 'native-export-needed' if not all(checks[k] for k in ('nativeExportProvenance', 'downloadedBytesBound', 'localExportVerified'))
             else 'cloud-delivery-needed' if not all(checks[k] for k in ('cloudFileMetadata', 'cloudPlayback', 'cloudDownload')) else 'review-needed')
    return {'ok': ready, 'status': stage, 'checks': checks, 'pending': pending,
            'projectUrl': project.get('url') if checks['nativeProjectSaved'] else None,
            'videoUrl': url if checks['cloudFileMetadata'] else None,
            'fileId': metadata.get('id') if checks['cloudFileMetadata'] else None,
            'inventoryFindings': inventory['findings'], 'scope': SCOPE}


def safe_outputs(outputs, inputs):
    skill = Path(__file__).resolve().parent.parent
    for output in outputs:
        resolved = Path(output).resolve()
        if resolved.is_relative_to(skill) or resolved in [Path(p).resolve() for p in inputs if p]:
            raise ValueError('Keep generated delivery files separate from the skill and all authored inputs.')


def finalize(story_path, timing_path, evidence_path, video, output):
    story_path = Path(story_path); output = Path(output); video = Path(video)
    cache = output.with_name(output.stem + '-media.json'); markdown = output.with_suffix('.md')
    safe_outputs([output, cache, markdown], [story_path, timing_path, evidence_path, video])
    story = validate_story(read(story_path)); timing = read(timing_path); evidence = read(evidence_path)
    video_hash = sha(video) if video.is_file() else None
    key = signature({'version': VERSION, 'videoSha256': video_hash, 'timing': timing})
    media = {}; reused = False
    if video_hash:
        if cache.is_file():
            try:
                prior = read(cache)
                if prior.get('verificationKey') == key and prior.get('video') == str(video.resolve()) and prior.get('ok') is True:
                    media = prior; reused = True
            except (ValueError, TypeError, OSError):
                pass
        if not reused:
            media = verify_export(video, timing, cache)
            media['verificationKey'] = key; atomic_json(cache, media)
    current_revision = revision(story, story_path.parent)
    result = assess(story, evidence, media, video_hash, current_revision)
    result.update(revision=current_revision, evidenceSha256=sha(evidence_path), evidencePath=str(Path(evidence_path).resolve()),
                  timingSha256=sha(timing_path), timingPath=str(Path(timing_path).resolve()),
                  video=str(video.resolve()), videoSha256=video_hash, bytes=media.get('bytes'),
                  duration=media.get('duration'), mediaCheckReused=reused)
    atomic_json(output, result)
    lines = ['Delivery status: ' + result['status'], '']
    if result['ok']:
        lines += [f"[Play or download the complete video]({result['videoUrl']})",
                  f"[Edit the Google Vids project]({result['projectUrl']})", '',
                  f"Duration: {result['duration']:.3f} seconds. Size: {result['bytes']} bytes.",
                  'Access: use the existing authorized account; sharing was not changed by this utility.']
    else:
        lines += ['The requested native/cloud delivery is incomplete.', '']
        lines += ['- ' + row['next'] for row in result['pending']]
    lines += ['', SCOPE, '']
    markdown.write_text('\n'.join(lines), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__); commands = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'check'):
        command = commands.add_parser(name); command.add_argument('--story', type=Path, required=True)
        command.add_argument('--video', type=Path, required=name == 'check'); command.add_argument('--output', type=Path, required=True)
        if name == 'check':
            command.add_argument('--timing', type=Path, required=True); command.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            safe_outputs([args.output], [args.story, args.video])
            if args.output.exists():
                raise ValueError('Receipt exists. Preserve it; choose a new output path for a new revision.')
            data = template(validate_story(read(args.story)), args.story.parent, args.video); atomic_json(args.output, data)
            result = {'ok': True, 'status': 'unobserved-template', 'output': str(args.output)}
        else:
            result = finalize(args.story, args.timing, args.evidence, args.video, args.output)
        print(json.dumps({k: v for k, v in result.items() if k not in ('scope', 'inventoryFindings')}, ensure_ascii=True))
        return 0 if result['ok'] else 2
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=True)); return 2


if __name__ == '__main__':
    raise SystemExit(main())
