#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Audit icon foreground and two-axis centering in authored local SVG scenes."""
import argparse
import functools
import http.server
import json
import math
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from inspect_focus import browser_path, Quiet

SKILL = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--screenshot', type=Path, required=True)
    parser.add_argument('--times', default='0,2,4,8')
    parser.add_argument('--scene-index', type=int)
    parser.add_argument('--all-states', action='store_true', help='Use authored scene cues or beat reading poses in one run.')
    args = parser.parse_args(); html = args.html.resolve()
    times = [float(value) for value in args.times.split(',')]
    if any(not math.isfinite(t) or t < 0 for t in times): parser.error('Times must be finite nonnegative seconds.')
    for output in [args.output, args.screenshot]:
        if output.resolve().is_relative_to(SKILL) or output.resolve() == html: parser.error('Keep reports outside the read-only skill and source HTML.')
        output.parent.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(html.parent)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    result = {'ok': False, 'states': [], 'browserErrors': [], 'scope': 'Actual local SVG theme/geometry observations. No repair, account operation or encoded-video claim.'}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=browser_path(), headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            page.on('pageerror', lambda e: result['browserErrors'].append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/{html.name}?capture=1')
            page.evaluate('async()=>{await document.fonts.ready;if(window.ready?.then)await window.ready;else if(window.prepareFocus)window.prepareFocus()}')
            if not page.evaluate('!!window.LineWorldTheme?.audit'): raise ValueError('Load the actual theme runtime in the source before auditing.')
            plan = [{'scene': args.scene_index, 'at': t, 'id': 'supplied'} for t in times]
            if args.all_states:
                plan = page.evaluate('''()=>{const data=window.PRODUCTION||window.STORY||{},result=[];
                  if(data.scenes){const groups=window.NARRATION_CUES?.scenes||[];data.scenes.forEach((s,i)=>{const duration=s.clipSeconds||s.duration,cues=groups.find(g=>g.id===s.id)?.cues||s.cues||[],times=[Math.min(2,duration/2),duration/2,duration-.05,...cues.filter(c=>Number.isFinite(c.at)).map(c=>Math.min(duration-.01,c.at+.05))];for(const t of [...new Set(times)])result.push({scene:i,at:t,id:s.id});});}
                  else if(data.beats){for(const b of data.beats)for(const fraction of [.18,.4,.65,.9])result.push({scene:null,at:b.start+b.duration*fraction,id:b.id});}
                  return result;}''')
                if not plan: raise ValueError('No authored scene/beat clock found; supply --times instead.')
            if len(plan) > 1000: raise ValueError('Review at most 1000 states in one compact audit.')
            def render(state):
                return page.evaluate('''s=>{if(s.scene!==null){const render=window.renderClip||window.renderAt;return render?.(s.scene,s.at)||null;}return window.renderAt?.(s.at)||null;}''', state)
            best = plan[0]; score = -1
            for state in plan:
                render(state)
                audit = page.evaluate("()=>LineWorldTheme.audit(document.querySelector('#stage')||document.querySelector('svg'))")
                result['states'].append({**state, **audit})
                rank = audit.get('whiteIcons', 0)*10+audit.get('centered', 0)
                if rank > score: best = state; score = rank
            render(best); page.screenshot(path=str(args.screenshot.resolve())); browser.close()
            result['ok'] = not result['browserErrors'] and all(s['ok'] for s in result['states'])
            result['posterState'] = best
    except Exception as error:
        result['browserErrors'].append(str(error))
    finally:
        server.shutdown(); server.server_close()
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')
    print(json.dumps({'ok': result['ok'], 'states': len(result['states']), 'icons': max((s['icons'] for s in result['states']), default=0),
                      'centered': max((s['centered'] for s in result['states']), default=0), 'findings': [{**v, 'scene': s['id'], 'at': s['at']} for s in result['states'] for v in s['violations']],
                      'errors': result['browserErrors'], 'output': str(args.output)}, ensure_ascii=True))
    return 0 if result['ok'] else 2


if __name__ == '__main__': raise SystemExit(main())
