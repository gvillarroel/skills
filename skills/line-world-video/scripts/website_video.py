#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2"]
# ///
"""Build, audit and render narrated tours of already captured website screenshots."""
import argparse
import functools
import hashlib
import json
import math
import re
import shutil
import subprocess
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from PIL import Image, ImageChops
from inspect_focus import Quiet, browser_path

SKILL = Path(__file__).resolve().parent.parent


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def stable(data): return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
def probe(path): return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], text=True))
def finite(value): return type(value) in [int, float] and math.isfinite(value)


def theme_audit(crop):
    pixels = list(crop.resize((120, 80)).getdata()); count = len(pixels)
    dark = sum(max(p) - min(p) <= 40 and max(p) <= 105 for p in pixels) / count
    light = sum(min(p) >= 180 for p in pixels) / count
    if dark > .4 and dark > light * 2:
        raise ValueError('Screenshot region appears to use a dark theme. Select the native light theme and recapture; do not recolor website pixels.')
    return {'method': 'sampled-neutral-background', 'darkFraction': round(dark, 4), 'lightFraction': round(light, 4), 'likelyDark': False, 'scope': 'A dark-UI regression heuristic, not certification of the native theme setting.'}


def owned(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()): raise ValueError('Keep screenshot, audio and generated paths inside the project.')
    return path


def build(project, story_path):
    project = project.resolve(); story = read(story_path); fps = story.get('fps', 30)
    if fps not in [24, 25, 30, 60]: raise ValueError('Use 24, 25, 30 or 60 fps.')
    scenes = story.get('scenes'); ids = set()
    if not scenes or not story.get('source'): raise ValueError('Supply scenes and truthful screenshot source/provenance.')
    if story['source'].get('theme', 'light') != 'light': raise ValueError('Use the native light theme for website screenshots and record theme: light.')
    for scene in scenes:
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', scene['id']) or scene['id'] in ids: raise ValueError('Use unique stable scene IDs.')
        ids.add(scene['id']); capture = owned(project, scene['capture'])
        with Image.open(capture) as im:
            scene['width'], scene['height'] = im.size
            region = scene.get('region', [0, 0, im.width, im.height]); scene['region'] = region
            if len(region) != 4 or not all(finite(v) for v in region) or not (0 <= region[0] < region[2] <= im.width and 0 <= region[1] < region[3] <= im.height): raise ValueError('Crop must stay within the actual screenshot: ' + scene['id'])
            crop = im.crop(tuple(region)).convert('RGB')
            if max(high - low for low, high in crop.getextrema()) < 15: raise ValueError('Screenshot region has no meaningful visible content: ' + scene['id'])
            scene['themeAudit'] = theme_audit(crop)
        scene['captureSha256'] = sha(capture)
        duration = scene.get('duration', 0)
        if not finite(duration) or not 0 < duration <= 180: raise ValueError('Scene duration must be finite and above zero, up to 180 seconds.')
        scene['frames'] = math.ceil(duration * fps - 1e-7); scene['duration'] = scene['frames'] / fps
        scene['scale'] = scene.get('scale', 1.8)
        if not finite(scene['scale']) or not .2 <= scene['scale'] <= 4: raise ValueError('Choose a readable screenshot scale between 0.2 and 4.')
        previous = -1
        for cue in scene.get('cues', []):
            if not finite(cue.get('at')) or not 0 <= cue['at'] < scene['duration'] or cue['at'] <= previous: raise ValueError('Use ordered scene-local cue times inside the scene.')
            previous = cue['at']; target = scene['targets'][cue['target']]; b = target['box']; port = target['port']
            if len(b) != 4 or not all(finite(v) for v in b) or min(b[2:]) <= 0 or len(port) != 2 or not all(finite(v) for v in port): raise ValueError('Use source-pixel [x,y,width,height] controls and adjacent [x,y] ports.')
            if b[0] < region[0] or b[1] < region[1] or b[0] + b[2] > region[2] or b[1] + b[3] > region[3]: raise ValueError('A spoken control is cut by its selected screenshot region: ' + cue['target'])
        if previous < 0: raise ValueError('Each scene needs at least one semantic cue.')
        if scene.get('audio'):
            audio = owned(project, scene['audio']); p = probe(audio)
            if not any(s['codec_type'] == 'audio' for s in p['streams']): raise ValueError('Narration input has no audio stream.')
            observed = float(p['format']['duration']); lead = scene.get('audioLead', 0)
            if lead < 0 or lead + observed > scene['duration'] + .001: raise ValueError('Measured speech exceeds its scene. Extend the duration instead of cutting speech.')
            scene['audioSha256'] = sha(audio); scene['observedAudioSeconds'] = observed
    story['fps'] = fps; story['duration'] = sum(s['duration'] for s in scenes)
    project.mkdir(parents=True, exist_ok=True); save(project / 'tour.json', story)
    (project / 'tour.js').write_text('window.WEBSITE_STORY=' + json.dumps(story, ensure_ascii=True) + ';', encoding='utf-8')
    shutil.copyfile(SKILL / 'assets/runtime/website-tour.js', project / 'website-tour.js')
    shutil.copyfile(SKILL / 'assets/runtime/focus.js', project / 'focus.js')
    (project / 'index.html').write_text('<!doctype html><html><meta charset="utf-8"><style>html,body{margin:0;background:white;width:100%;height:100%;overflow:hidden}svg{display:block;width:100vw;height:100vh}</style><svg id="stage" viewBox="0 0 1920 1080" role="img" aria-label="Guided original website screenshots"></svg><script src="tour.js"></script><script src="focus.js"></script><script src="website-tour.js"></script></html>', encoding='utf-8')
    # A portable preview uses the same pure renderer and supplied audio clips.
    preview = '''<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#fff;font:16px Arial}iframe{width:100vw;height:calc(100vh - 60px);border:0}footer{display:flex;gap:12px;align-items:center;padding:12px}input{flex:1}</style><iframe src="index.html"></iframe><footer><button id="play">Play</button><input id="seek" type="range" min="0" step="0.01"><output></output></footer><script src="tour.js"></script><script>const frame=document.querySelector('iframe'),seek=document.querySelector('#seek'),out=document.querySelector('output'),audios=WEBSITE_STORY.scenes.map(s=>s.audio?new Audio(s.audio):null);seek.max=WEBSITE_STORY.duration;let playing=false,time=0,old=0;function paint(){frame.contentWindow.renderAt(time);out.value=time.toFixed(2)+' / '+WEBSITE_STORY.duration.toFixed(2);seek.value=time;let t=time,i=0;while(i<WEBSITE_STORY.scenes.length-1&&t>=WEBSITE_STORY.scenes[i].duration){t-=WEBSITE_STORY.scenes[i].duration;i++}audios.forEach((a,n)=>{if(!a)return;let at=t-(WEBSITE_STORY.scenes[i].audioLead||0);if(n===i&&at>=0&&at<a.duration&&playing){if(Math.abs(a.currentTime-at)>.12)a.currentTime=at;if(a.paused)a.play()}else a.pause()})}seek.oninput=()=>{time=+seek.value;paint()};document.querySelector('#play').onclick=()=>{playing=!playing;document.querySelector('#play').textContent=playing?'Pause':'Play';if(!playing)audios.forEach(a=>a?.pause())};frame.onload=()=>frame.contentWindow.ready.then(paint);function tick(now){if(playing){time=Math.min(+seek.max,time+(now-old)/1000);paint();if(time===+seek.max){playing=false;audios.forEach(a=>a?.pause())}}old=now;requestAnimationFrame(tick)}requestAnimationFrame(tick);</script>'''
    (project / 'preview.html').write_text(preview, encoding='utf-8')
    return {'ok': True, 'scenes': len(scenes), 'duration': story['duration'], 'fps': fps}


def render(project, output, report_path, audit_only=False, poster=None):
    from playwright.sync_api import sync_playwright
    project = project.resolve(); story = read(project / 'tour.json'); fps = story['fps']
    for scene in story['scenes']:
        if sha(owned(project, scene['capture'])) != scene['captureSha256']: raise ValueError('Screenshot bytes changed. Rebuild the tour before rendering.')
        if scene.get('audio') and sha(owned(project, scene['audio'])) != scene['audioSha256']: raise ValueError('Narration bytes changed. Rebuild and remeasure cues before rendering.')
    expected_js = 'window.WEBSITE_STORY=' + json.dumps(story, ensure_ascii=True) + ';'
    if (project / 'tour.js').read_text(encoding='utf-8') != expected_js: raise ValueError('Compiled story differs. Edit source JSON and rebuild the tour.')
    runtime_key = [sha(Path(__file__)), *[sha(project / name) for name in ['website-tour.js', 'focus.js', 'index.html']]]
    key = stable([story, runtime_key, sha(project / 'tour.js')])
    if not audit_only and output.exists() and report_path.exists():
        prior = read(report_path)
        poster_ok = poster is None or (poster.is_file() and prior.get('poster', {}).get('sha256') == sha(poster))
        if prior.get('key') == key and prior.get('sha256') == sha(output) and poster_ok:
            return {'ok': prior['ok'], 'reused': True, 'output': str(output), 'duration': story['duration']}
    cache = project / 'artifacts/website-render'; cache.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(project)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    report = {'ok': False, 'key': key, 'scenes': [], 'issues': [], 'nativeGoogleVids': False, 'source': story['source'], 'scope': 'Saved original screenshots, supplied semantic boxes/ports, all-frame source checks and actual encoded media. No live browser actions, OCR completeness or independent audio transcript certification.'}
    clips = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=browser_path(), headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
            page.on('pageerror', lambda e: report['issues'].append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html'); page.evaluate('async()=>await window.ready')
            for i, scene in enumerate(story['scenes']):
                checked = page.evaluate('''([i,fps])=>{let issues=[],last=null,maxScaleRate=0,maxPanSpeed=0;const s=WEBSITE_STORY.scenes[i];for(let n=0;n<s.frames;n++){const p=renderClip(i,n/fps);if(p.issues.length&&issues.length<15)issues.push({frame:n,issues:p.issues});if(last){maxScaleRate=Math.max(maxScaleRate,Math.abs(p.camera.k-last.camera.k)*fps);maxPanSpeed=Math.max(maxPanSpeed,Math.hypot(p.camera.x-last.camera.x,p.camera.y-last.camera.y)*fps)}last=p}return{issues,maxScaleRate,maxPanSpeed}}''', [i, fps])
                states = []
                for j, cue in enumerate(scene['cues']):
                    state = page.evaluate('([i,t])=>renderClip(i,t)', [i, cue['at']]); states.append(state)
                    page.screenshot(path=str(cache / f'{i+1:02}-{j+1:02}-{cue["target"]}.png'))
                page.evaluate('([i,t])=>renderClip(i,t)', [i, scene['duration'] / 2]); before = page.screenshot()
                page.evaluate('([i,t])=>renderClip(i,t)', [i, 0]); page.evaluate('([i,t])=>renderClip(i,t)', [i, scene['duration'] / 2])
                if before != page.screenshot(): checked['issues'].append({'kind': 'repeat-seek-differs'})
                item = {'id': scene['id'], 'frames': scene['frames'], 'checks': checked, 'cueStates': states}
                report['scenes'].append(item)
                if checked['issues']: report['issues'].append(scene['id'] + ': ' + json.dumps(checked['issues']))
                clip = cache / f'{i+1:02}-{scene["id"]}.mp4'; receipt = clip.with_suffix('.json'); clips.append(clip)
                clip_key = stable([scene, story['scenes'][i-1] if i else None, runtime_key, fps])
                if not audit_only and not report['issues']:
                    reused = clip.exists() and receipt.exists() and read(receipt).get('key') == clip_key and read(receipt).get('sha256') == sha(clip)
                    if not reused:
                        cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-framerate', str(fps), '-i', 'pipe:0', '-frames:v', str(scene['frames']), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(clip)]
                        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE); previous = None; captures = 0
                        try:
                            for n in range(scene['frames']):
                                state = page.evaluate('([i,t])=>renderClip(i,t)', [i, n / fps]); pose_key = json.dumps(state, sort_keys=True)
                                if pose_key != previous: frame = page.screenshot(type='jpeg', quality=97); previous = pose_key; captures += 1
                                proc.stdin.write(frame)
                            proc.stdin.close(); error = proc.stderr.read().decode(); code = proc.wait()
                            if code: raise ValueError(error)
                        finally:
                            if proc.poll() is None: proc.kill(); proc.wait()
                            if not proc.stdin.closed: proc.stdin.close()
                            proc.stderr.close()
                        save(receipt, {'key': clip_key, 'sha256': sha(clip), 'capturedFrames': captures})
                    item['clipReused'] = reused; item['clip'] = str(clip)
                    print(json.dumps({'scene': scene['id'], 'frames': scene['frames'], 'reused': reused}), flush=True)
            if poster:
                # Prefer a complete actual community/control reading pose.
                i = min(1, len(story['scenes']) - 1); page.evaluate('([i,t])=>renderClip(i,t)', [i, story['scenes'][i]['cues'][0]['at'] + .4])
                poster.parent.mkdir(parents=True, exist_ok=True); page.screenshot(path=str(poster))
                report['poster'] = {'path': str(poster), 'sha256': sha(poster)}
            browser.close()
        if not audit_only and not report['issues']:
            listing = cache / 'clips.txt'; listing.write_text(''.join("file '" + str(p.resolve()).replace('\\', '/').replace("'", "'\\''") + "'\n" for p in clips), encoding='utf-8')
            voice = cache / 'narration.wav'; has_audio = any(s.get('audio') for s in story['scenes'])
            if has_audio:
                args = ['ffmpeg', '-y', '-v', 'error']; filters = []; audio_index = 0
                for i, s in enumerate(story['scenes']):
                    samples = s['frames'] * 48000 // fps
                    if s.get('audio'):
                        args += ['-i', str(owned(project, s['audio']))]
                        filters.append(f'[{audio_index}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,adelay={round(s.get("audioLead",0)*1000)}:all=1,apad,atrim=end_sample={samples},asetpts=PTS-STARTPTS[a{i}]'); audio_index += 1
                    else: filters.append(f'anullsrc=r=48000:cl=stereo,atrim=end_sample={samples}[a{i}]')
                filters.append(''.join(f'[a{i}]' for i in range(len(story['scenes']))) + f'concat=n={len(story["scenes"])}:v=0:a=1[a]')
                subprocess.run(args + ['-filter_complex', ';'.join(filters), '-map', '[a]', '-c:a', 'pcm_s16le', str(voice)], check=True, capture_output=True)
            output.parent.mkdir(parents=True, exist_ok=True)
            args = ['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(listing)]
            args += ['-i', str(voice), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k'] if has_audio else ['-c:v', 'copy', '-an']
            temporary = output.with_name(output.stem + '.partial.mp4')
            subprocess.run(args + ['-movflags', '+faststart', str(temporary)], check=True, capture_output=True)
            observed = probe(temporary); video = next(s for s in observed['streams'] if s['codec_type'] == 'video')
            if int(video['nb_frames']) != sum(s['frames'] for s in story['scenes']): raise ValueError('Final frame count differs from the actual scene clock.')
            subprocess.run(['ffmpeg', '-v', 'error', '-i', str(temporary), '-f', 'null', '-'], check=True, capture_output=True)
            temporary.replace(output)
            report.update(output=str(output), sha256=sha(output), frames=int(video['nb_frames']), duration=float(video['duration']), audio=has_audio, fullDecode=True)
        report['ok'] = not report['issues']
    except Exception as error:
        report['issues'].append(str(error)); report['ok'] = False
    finally:
        server.shutdown(); server.server_close(); save(report_path, report)
    return {'ok': report['ok'], 'report': str(report_path), 'issues': report['issues'], 'duration': story['duration'], 'output': str(output) if not audit_only else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build'); p.add_argument('--project', type=Path, required=True); p.add_argument('--story', type=Path, required=True)
    p = sub.add_parser('render'); p.add_argument('--project', type=Path, required=True); p.add_argument('--output', type=Path, required=True); p.add_argument('--report', type=Path, required=True); p.add_argument('--audit-only', action='store_true'); p.add_argument('--poster', type=Path)
    args = parser.parse_args()
    try:
        result = build(args.project, args.story) if args.command == 'build' else render(args.project, args.output, args.report, args.audit_only, args.poster)
        print(json.dumps(result)); return 0 if result['ok'] else 2
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({'ok': False, 'error': str(error)})); return 2


if __name__ == '__main__': raise SystemExit(main())
