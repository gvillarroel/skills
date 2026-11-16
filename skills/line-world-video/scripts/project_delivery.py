#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare, cache and package local scene assemblies with measured narration."""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath

RATE, STRIDE = 44100, 4


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def local(root, value):
    if not isinstance(value, str) or not value or any(p.is_absolute() or '..' in p.parts or p.drive for p in [PurePosixPath(value), PureWindowsPath(value)]):
        raise ValueError('Use project-relative paths without parent traversal.')
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()): raise ValueError('A source path leaves the project.')
    return path


def run(args):
    result = subprocess.run(args, capture_output=True)
    if result.returncode: raise ValueError(result.stderr.decode('utf-8', errors='replace')[-1600:])
    return result.stdout


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))


def video_info(path, fps):
    data = probe(path)
    stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
    if not stream or not str(stream.get('nb_frames', '')).isdigit(): raise ValueError('A clip needs a measured video frame count: ' + path.name)
    numerator, denominator = map(int, stream['r_frame_rate'].split('/'))
    if numerator != fps * denominator: raise ValueError('Clip frame rate differs from the assembly clock: ' + path.name)
    if stream['codec_name'] != 'h264': raise ValueError('Use compatible H.264 scene clips for stream-copy assembly.')
    return stream


def validate(request):
    data = read(request); root = request.parent.resolve()
    fps = data.get('fps', 30)
    if type(fps) is not int or fps not in [24, 25, 30, 60]: raise ValueError('Choose 24, 25, 30 or 60 fps.')
    if not data.get('voice', {}).get('provenance'): raise ValueError('Record the voice provenance; the helper cannot certify its provider.')
    voice = local(root, data['voice']['file'])
    if not voice.is_file(): raise ValueError('Voice reference is missing.')
    scenes = data.get('scenes', []); ids = [s.get('id') for s in scenes]
    if not scenes or len(ids) != len(set(ids)) or any(not isinstance(i, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', i) for i in ids):
        raise ValueError('Provide ordered scenes with unique stable IDs.')
    clips = []
    for scene in scenes:
        seconds = scene.get('voiceSeconds')
        if type(seconds) not in [int, float] or not math.isfinite(seconds) or seconds <= 0: raise ValueError('Each scene needs a positive measured voiceSeconds value.')
        clip = local(root, scene['clip'])
        if not clip.is_file(): raise ValueError('Missing scene clip: ' + scene['id'])
        clips.append(clip)
    return data, root, voice, clips


def prepare(story_path, observed_path, voice, clips, output, provenance, fps=30):
    story, observed = read(story_path)['scenes'], read(observed_path)['scenes']
    if [s['id'] for s in story] != [s['id'] for s in observed]:
        raise ValueError('Observed reference order must match story order; do not guess audio partitions.')
    root = output.parent.resolve(); root.mkdir(parents=True, exist_ok=True)
    def relative(path):
        if not path.resolve().is_relative_to(root): raise ValueError('Put the request at the project root above its voice and clips.')
        return path.resolve().relative_to(root).as_posix()
    value = {'schemaVersion': 1, 'fps': fps, 'voice': {'file': relative(voice), 'provenance': provenance}, 'scenes': []}
    for index, (scene, timing) in enumerate(zip(story, observed, strict=True), 1):
        clip = clips / f'{index:02d}-{scene["id"]}.mp4'
        measured = video_info(clip, fps)
        seconds = scene.get('clipSeconds', scene.get('duration'))
        if type(seconds) not in [int, float] or round(seconds * fps) != int(measured['nb_frames']):
            raise ValueError('Scene budget and actual clip frames differ: ' + scene['id'])
        value['scenes'].append({'id': scene['id'], 'clip': relative(clip), 'voiceSeconds': timing.get('sceneSeconds', timing.get('duration'))})
    if output.exists() and read(output) != value: raise ValueError('Use a new request path for a changed revision.')
    save(output, value); validate(output)
    return {'ok': True, 'request': str(output), 'scenes': len(story)}


def fingerprint(request, sources):
    value = {'request': sha(request), 'helper': sha(Path(__file__)), 'sources': [sha(p) for p in sources]}
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def cached(output, report, key, field):
    if not output.is_file() or not report.is_file(): return None
    old = read(report)
    if old.get('ok') and old.get('inputsSha256') == key and old.get(field + 'Sha256') == sha(output):
        result = {**old, 'reused': True}; save(report, result); return result
    return None


def assemble(request, output, report, replace=False):
    data, root, voice, clips = validate(request); fps = data.get('fps', 30)
    sources = [request.resolve(), voice, *clips]
    if output.resolve() in sources or report.resolve() in sources or output.resolve() == report.resolve(): raise ValueError('Outputs must not replace assembly inputs or each other.')
    key = fingerprint(request, [voice, *clips]); old = cached(output, report, key, 'video')
    if old: return old
    if output.exists() and not replace: raise ValueError('Output exists without a matching cache receipt. Choose a new path or use --replace for an owned revision.')
    if float(probe(voice)['format'].get('duration', 0)) * RATE * STRIDE > 512 * 1024 * 1024:
        raise ValueError('Split narration references larger than the 512 MiB decoded-audio budget.')
    pcm = run(['ffmpeg', '-v', 'error', '-i', str(voice), '-vn', '-f', 's16le', '-ar', str(RATE), '-ac', '2', 'pipe:1'])
    declared = round(sum(s['voiceSeconds'] for s in data['scenes']) * RATE) * STRIDE
    if declared > len(pcm) + STRIDE: raise ValueError('Measured narration extends beyond the actual decoded reference.')
    tail = array.array('h', pcm[declared:])
    if len(tail) > RATE * 2 / 4: raise ValueError('Reference exceeds the measured timeline by more than 250 ms. Remeasure it.')
    preserve_tail = any(tail)
    records, chunks, cursor, profiles = [], [], 0.0, []
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='assembly-', dir=output.parent) as temporary:
        work = Path(temporary)
        for index, (scene, clip) in enumerate(zip(data['scenes'], clips, strict=True)):
            stream = video_info(clip, fps); frames = original = int(stream['nb_frames'])
            profiles.append(tuple(stream.get(k) for k in ['codec_name', 'width', 'height', 'pix_fmt', 'time_base', 'profile', 'level']))
            if profiles[-1] != profiles[0]: raise ValueError('Scene clips have incompatible video parameters.')
            first = round(cursor * RATE) * STRIDE; cursor += scene['voiceSeconds']
            last = round(cursor * RATE) * STRIDE
            speech = pcm[first:last]
            if index == len(clips) - 1 and preserve_tail:
                speech = pcm[first:]; frames = max(frames, math.ceil(len(speech) / STRIDE * fps / RATE))
            target = round(frames * RATE / fps) * STRIDE
            rounding = max(0, len(speech) - target)
            if rounding > STRIDE: raise ValueError('Measured speech exceeds clip budget: ' + scene['id'] + '. Rerender the visual; do not shorten speech.')
            if rounding: speech = speech[:-rounding]
            chunks.append(speech + bytes(target - len(speech)))
            staged = work / f'clip-{index:04d}.mp4'
            if frames > original:
                run(['ffmpeg', '-v', 'error', '-i', str(clip), '-vf', 'tpad=stop_mode=clone:stop_duration=0.25', '-frames:v', str(frames), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', stream['pix_fmt'], '-video_track_timescale', str(int(stream['time_base'].split('/')[1])), str(staged)])
            else:
                try: os.link(clip, staged)
                except OSError: shutil.copyfile(clip, staged)
            records.append({'id': scene['id'], 'frames': frames, 'voiceSamples': len(speech) // STRIDE, 'paddingSamples': (target - len(speech)) // STRIDE, 'boundaryRoundingSamples': rounding // STRIDE, 'extraFinalHoldFrames': frames - original})
        aligned = b''.join(chunks)
        with wave.open(str(work / 'voice.wav'), 'wb') as wav:
            wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(RATE); wav.writeframes(aligned)
        (work / 'concat.txt').write_text(''.join(f"file 'clip-{i:04d}.mp4'\n" for i in range(len(clips))), encoding='utf-8')
        movie = work / 'complete.mp4'
        run(['ffmpeg', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(work / 'concat.txt'), '-i', str(work / 'voice.wav'), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(movie)])
        actual = video_info(movie, fps); expected = sum(s['frames'] for s in records)
        if int(actual['nb_frames']) != expected: raise ValueError('Complete movie frame count differs from the scene budgets.')
        run(['ffmpeg', '-v', 'error', '-i', str(movie), '-f', 'null', '-'])
        result = {'ok': True, 'reused': False, 'nativeGoogleVidsExport': False, 'deliveryKind': 'local-assembly', 'voiceProvenance': data['voice']['provenance'],
                  'inputsSha256': key, 'video': str(output.resolve()), 'videoSha256': sha(movie), 'frames': expected, 'fps': fps, 'duration': expected / fps,
                  'alignedPcmSha256': hashlib.sha256(aligned).hexdigest(), 'nativeReferenceSha256': sha(voice), 'discardedZeroTailSamples': 0 if preserve_tail else len(tail) // 2, 'scenes': records}
        os.replace(movie, output)
    save(report, result); return result


REBUILD = '''#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Reassemble the included measured voice and rendered clips locally."""
import argparse,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/videos/reassembled-local.mp4');a=p.parse_args()
subprocess.run(['uv','run','--script',str(root/'tools/project_delivery.py'),'assemble','--request',str(root/'assembly.json'),'--output',str(root/a.output),'--report',str(root/'artifacts/reviews/reassembly.json')],cwd=root,check=True)
'''


def bundle(request, output, report, includes):
    data, root, voice, clips = validate(request)
    if output.resolve() == report.resolve(): raise ValueError('Archive and report need distinct paths.')
    files = {p.relative_to(root).as_posix(): p for p in [voice, *clips]}
    for name in includes:
        path = local(root, name)
        if path == root: raise ValueError('Include specific owned sources, not the whole project.')
        if not path.exists(): raise ValueError('Missing included source: ' + name)
        for item in ([path] if path.is_file() else sorted(path.rglob('*'))):
            if not item.is_file(): continue
            rel = item.relative_to(root)
            if item.is_symlink() or not item.resolve().is_relative_to(root): raise ValueError('Do not bundle symlinks or outside-project files.')
            if any(p in {'.git', '.cache', '.venv', 'node_modules', '__pycache__'} or p.startswith('.env') for p in rel.parts): continue
            if item.resolve() not in [output.resolve(), report.resolve(), request.resolve()]: files[rel.as_posix()] = item
    reserved = {'assembly.json', 'rebuild.py', 'source-manifest.json', 'tools/project_delivery.py'}
    if reserved.intersection(files): raise ValueError('An included file collides with a reserved bundle member.')
    if report.resolve() in [request.resolve(), *files.values()] or output.resolve() in [request.resolve(), *files.values()]: raise ValueError('Bundle outputs must not replace project inputs.')
    key = hashlib.sha256(json.dumps({'sources': fingerprint(request, [files[n] for n in sorted(files)]), 'members': sorted(files)}).encode()).hexdigest()
    old = cached(output, report, key, 'archive')
    if old: return old
    if output.exists(): raise ValueError('Do not overwrite an immutable source archive; select a new revision path.')
    contents = {name: p.read_bytes() for name, p in files.items()}
    contents.update({'assembly.json': request.read_bytes(), 'rebuild.py': REBUILD.encode(), 'tools/project_delivery.py': Path(__file__).read_bytes()})
    manifest = {'schemaVersion': 1, 'deliveryKind': 'local-assembly-inputs', 'nativeGoogleVidsExport': False, 'files': [{'path': n, 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()} for n, b in sorted(contents.items())], 'scope': 'Reassembles included voice and rendered clips. Regenerating visual clips requires their project renderer; optional sources are included unchanged.'}
    contents['source-manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bundle-', dir=output.parent) as temporary:
        archive = Path(temporary) / 'sources.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zipped:
            for name, value in sorted(contents.items()):
                info = zipfile.ZipInfo(name, date_time=(2026, 11, 16, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; zipped.writestr(info, value)
        with zipfile.ZipFile(archive) as zipped:
            if zipped.testzip() or any(hashlib.sha256(zipped.read(r['path'])).hexdigest() != r['sha256'] for r in manifest['files']): raise ValueError('Source archive verification failed.')
        result = {'ok': True, 'reused': False, 'inputsSha256': key, 'archive': str(output.resolve()), 'archiveSha256': sha(archive), 'files': len(contents), 'nativeGoogleVidsExport': False}
        os.replace(archive, output)
    save(report, result); return result


def main():
    parser = argparse.ArgumentParser(description=__doc__); commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    for key in ['story', 'observed', 'voice', 'clips', 'output']: p.add_argument('--' + key, type=Path, required=True)
    p.add_argument('--voice-provenance', required=True); p.add_argument('--fps', type=int, default=30)
    for name in ['assemble', 'bundle']:
        p = commands.add_parser(name)
        for key in ['request', 'output', 'report']: p.add_argument('--' + key, type=Path, required=True)
        if name == 'assemble': p.add_argument('--replace', action='store_true')
        else: p.add_argument('--include', action='append', default=[])
    args = parser.parse_args()
    try:
        if args.command == 'prepare': result = prepare(args.story, args.observed, args.voice, args.clips, args.output, args.voice_provenance, args.fps)
        elif args.command == 'assemble': result = assemble(args.request, args.output, args.report, args.replace)
        else: result = bundle(args.request, args.output, args.report, args.include)
        print(json.dumps({k: v for k, v in result.items() if k != 'scenes'})); return 0
    except (ValueError, KeyError, OSError, StopIteration) as error:
        print(json.dumps({'ok': False, 'error': str(error)})); return 2


if __name__ == '__main__': raise SystemExit(main())
