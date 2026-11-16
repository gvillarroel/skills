#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Check that every portrait has a spoken name, contribution, caption and cue."""
import argparse
import functools
import http.server
import json
import math
import re
import threading
import unicodedata
from pathlib import Path
from urllib.parse import urlparse


def words(text):
    plain = ''.join(c for c in unicodedata.normalize('NFD', str(text).casefold()) if unicodedata.category(c) != 'Mn')
    return re.findall(r'[a-z0-9]+', plain)


def positions(haystack, needle):
    return [i for i in range(len(haystack)-len(needle)+1) if needle and haystack[i:i+len(needle)] == needle]


def review(story, media=None, cues=None, visible=None, require_observed=False):
    findings = []; people = []; scenes = story.get('scenes', [])
    def fail(kind, scene, person, message): findings.append({'kind': kind, 'scene': scene, 'person': person, 'message': message})
    assets = {a['id']: a for a in (media or {}).get('assets', [])}
    planned = {(s['id'], p['id']) for s in scenes for p in s.get('people', [])}
    for asset in assets.values():
        bound = (asset.get('stage'), asset['id']) in planned if asset.get('stage') else any(pid == asset['id'] for sid, pid in planned)
        if asset.get('kind') == 'portrait' and not bound:
            fail('unintroduced-portrait', asset.get('stage'), asset['id'], 'Bind this visible portrait to a named contribution before voice generation.')
    observed = {(s['id'], p['id']): p for s in (visible or {}).get('scenes', []) for p in s.get('people', [])}
    for sid, pid in observed:
        if (sid, pid) not in planned: fail('unintroduced-visible-person', sid, pid, 'The rendered portrait has no matching story introduction.')
    cue_scenes = {s['id']: s for s in (cues or {}).get('scenes', [])}
    seen = set()
    for scene in scenes:
        sid = scene['id']; script = words(scene.get('script', scene.get('narration', '')))
        for person in scene.get('people', []):
            pid = person['id']; key = (sid, pid); name = person.get('name', ''); caption = person.get('caption', []); target = person.get('target')
            if key in seen: fail('duplicate-person', sid, pid, 'Use one introduction binding per person and scene.')
            seen.add(key)
            name_at = positions(script, words(person.get('spokenName', name)))
            role_at = positions(script, words(person.get('narrationRole', '')))
            if len(words(name)) < 2 or not name_at: fail('missing-spoken-name', sid, pid, 'Say the person name in the narration.')
            if len(words(person.get('narrationRole', ''))) < 2 or not role_at: fail('missing-spoken-contribution', sid, pid, 'Say the relevant contribution; a name or job title alone is insufficient.')
            elif name_at and min(abs(a-b) for a in name_at for b in role_at) > 45: fail('distant-context', sid, pid, 'Explain the contribution near the first name mention.')
            if not isinstance(caption, list) or not 1 <= len(caption) <= 2 or any(not isinstance(t, str) or not t.strip() or len(t) > 56 for t in caption):
                fail('missing-contribution-caption', sid, pid, 'Use one or two concise factual contribution lines beside the portrait.')
            if not person.get('sources') or any(urlparse(u).scheme not in ['http', 'https'] or not urlparse(u).netloc for u in person.get('sources', [])):
                fail('missing-contribution-source', sid, pid, 'Retain a reviewed institutional or original-paper source for this role.')
            if target not in [c.get('target') for c in scene.get('cues', [])]: fail('missing-name-cue', sid, pid, 'Bind a distinct semantic cue to this spoken person.')
            if assets and (pid not in assets or assets[pid].get('kind') != 'portrait'): fail('missing-portrait-asset', sid, pid, 'Resolve this binding to its actual reviewed portrait asset.')
            if visible is not None:
                item = observed.get(key)
                if item is None: fail('missing-visible-person', sid, pid, 'The source inspection did not observe this portrait.')
                else:
                    if words(item.get('name', '')) != words(name): fail('visible-name-mismatch', sid, pid, 'Render the complete person name beside the image.')
                    if item.get('caption') != caption: fail('visible-contribution-mismatch', sid, pid, 'The actual visible contribution differs from the current story.')
                    if not item.get('legible', False): fail('illegible-person-context', sid, pid, 'Keep loaded labels readable, in frame and outside the photograph.')
            if cues is not None:
                block = cue_scenes.get(sid, {}); matched = [c for c in block.get('cues', []) if c.get('target') == target]
                if cues.get('status') != 'aligned-to-audio' or not matched:
                    fail('missing-measured-name-cue', sid, pid, 'Align the name to actual narration word timestamps.')
                else:
                    cue = matched[0]; numbers = [cue.get(k) for k in ['at', 'end', 'audioStart', 'audioEnd']]
                    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in numbers) or numbers[1] <= numbers[0] or not cue.get('evidence'):
                        fail('invalid-measured-name-cue', sid, pid, 'Retain finite actual word timing and alignment evidence.')
                    if not any(positions(words(phrase), words(person.get('spokenName', name))) for phrase in [cue.get('phrase', ''), *cue.get('alternatives', [])]):
                        fail('wrong-name-cue', sid, pid, 'Use the person name, rather than a later generic term, for this cue.')
            people.append({'scene': sid, 'id': pid, 'name': name, 'caption': caption, 'target': target})
    if visible is not None and (visible.get('observed') is not True or not visible.get('evidence')): fail('unobserved-source', None, None, 'Supply actual browser observations, not an expected caption manifest.')
    pending = ([] if visible is not None else ['visible captions'])+([] if cues is not None else ['actual audio name timing'])
    if require_observed and pending: fail('incomplete-observation', None, None, 'Complete source and measured-audio checks before delivery.')
    return {'ok': not findings, 'people': people, 'findings': findings, 'pending': pending,
            'scope': 'Checks supplied script/context and optional actual local SVG observations/ASR cues. Sources still require factual review; ASR timing is approximate.'}


def inspect_html(html, story, screenshot=None):
    from inspect_focus import browser_path, Quiet
    from playwright.sync_api import sync_playwright
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(html.resolve().parent)))
    threading.Thread(target=server.serve_forever, daemon=True).start(); scenes = []; errors = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=browser_path(), headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080}); page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/{html.name}?capture=1')
            page.evaluate('async()=>{await document.fonts.ready;if(window.ready?.then)await window.ready;}')
            for i, scene in enumerate(story['scenes']):
                if not scene.get('people'): continue
                page.evaluate('s=>{const f=window.renderClip||window.renderAt;f(s.i,s.at);}', {'i': i, 'at': scene.get('clipSeconds', scene.get('duration'))/2})
                people = page.evaluate('''sid=>{const frame=document.querySelector('#stage').getBoundingClientRect(),inside=(a,b)=>a.left>=b.left-1&&a.right<=b.right+1&&a.top>=b.top-1&&a.bottom<=b.bottom+1,hit=(a,b,p=3)=>a.left<b.right+p&&a.right>b.left-p&&a.top<b.bottom+p&&a.bottom>b.top-p;return [...document.querySelectorAll('[data-person-id]')].filter(g=>g.dataset.personScene===sid||g.closest('#scene-'+sid)||g.closest('[data-scene-id="'+sid+'"]')).map(g=>{const name=g.querySelector('[data-person-name]'),caption=[...g.querySelectorAll('[data-person-caption]')],photo=g.querySelector('image')?.getBoundingClientRect(),labels=[name,...caption].filter(Boolean);return{id:g.dataset.personId,name:name?.textContent||'',caption:caption.map(t=>t.textContent),legible:!!name&&!!photo&&caption.length>0&&labels.every((t,i)=>{const b=t.getBoundingClientRect();return inside(b,frame)&&!hit(b,photo)&&b.height>=19&&+getComputedStyle(t).opacity>.01&&labels.every((other,j)=>i===j||!hit(b,other.getBoundingClientRect()));})}});}''', scene['id'])
                scenes.append({'id': scene['id'], 'people': people})
            if screenshot:
                screenshot.parent.mkdir(parents=True, exist_ok=True); page.screenshot(path=str(screenshot.resolve()))
            browser.close()
    finally: server.shutdown(); server.server_close()
    if errors: raise ValueError('Source browser errors: '+str(errors))
    return {'observed': True, 'evidence': 'Actual loaded local SVG, rendered reading poses, measured label/image bounds.', 'scenes': scenes}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--story', type=Path, required=True); p.add_argument('--media', type=Path); p.add_argument('--cues', type=Path); p.add_argument('--html', type=Path); p.add_argument('--visible', type=Path); p.add_argument('--screenshot', type=Path); p.add_argument('--require-observed', action='store_true'); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.html and a.visible: p.error('Choose the actual HTML inspector or an existing observation, not both.')
    read = lambda path: json.loads(path.read_text(encoding='utf-8-sig')) if path else None
    if a.screenshot and not a.html: p.error('A source screenshot requires --html.')
    story = read(a.story); visible = inspect_html(a.html, story, a.screenshot) if a.html else read(a.visible)
    result = review(story, read(a.media), read(a.cues), visible, a.require_observed)
    if visible is not None: result['sourceObservation'] = visible
    a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(result, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')
    print(json.dumps({'ok': result['ok'], 'people': len(result['people']), 'findings': result['findings'], 'pending': result['pending']}))
    return 0 if result['ok'] else 2


if __name__ == '__main__': raise SystemExit(main())
