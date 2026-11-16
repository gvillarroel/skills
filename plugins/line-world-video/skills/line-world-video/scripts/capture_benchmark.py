#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "pillow>=11,<13", "resvg-py==0.5.0"]
# ///
"""Compare capture costs on local authored assets, without rendering a whole film."""
import functools,http.server,json,statistics,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
from render_line_world import capture,browser_path,QuietHandler

def benchmark(project,report_path,frames=6):
    if not 2<=frames<=30:raise ValueError('Benchmark frames must be between 2 and 30.')
    story=json.loads((project/'story.json').read_text(encoding='utf-8-sig'));timing=json.loads((project/'timing.json').read_text())
    report_path.parent.mkdir(parents=True,exist_ok=True);images=report_path.parent/(report_path.stem+'-samples');images.mkdir(exist_ok=True)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(project)))
    threading.Thread(target=server.serve_forever,daemon=True).start();methods={};errors=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=browser_path(),headless=True,args=['--disable-gpu'])
            page=browser.new_page(viewport={'width':story['width'],'height':story['height']});page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html',wait_until='networkidle');page.evaluate('document.fonts.ready')
            for method in ('browser','svg'):
                times=[]
                for i in range(frames):
                    t=(i+.5)*timing['duration']/frames;page.evaluate('t=>renderAt(t)',t);start=time.perf_counter();png=capture(page,project,method);times.append(time.perf_counter()-start)
                    if i==0:(images/(method+'.png')).write_bytes(png)
                methods[method]={'samples':frames,'medianSecondsPerFrame':statistics.median(times),'totalCaptureSeconds':sum(times)}
            browser.close()
    finally:server.shutdown()
    result={'ok':not errors,'scope':'Local per-frame capture microbenchmark; not an end-to-end render speed claim. Inspect saved samples for fidelity.','methods':methods,'browserVsSvgMedianSpeedup':methods['svg']['medianSecondsPerFrame']/methods['browser']['medianSecondsPerFrame'],'default':'browser','browserErrors':errors}
    report_path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return 0 if result['ok'] else 2
