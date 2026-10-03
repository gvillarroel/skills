#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Inspect actual navigation text paint against its opaque ink panel."""
import argparse,functools,http.server,json,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
rows=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1600,'height':1000})
    for stem in ['inference-pulse','heatwave-tree']:
        page.goto(f'http://127.0.0.1:{server.server_port}/skills/compose-synchronized-svg/assets/examples/compose-synchronized-svg/{stem}.svg')
        page.wait_for_function('typeof svgSync !== "undefined"')
        rows.append(page.evaluate('''stem => {
          const panel=document.querySelector('.navigation-hud-panel');
          const hex=rgb=>'#'+rgb.match(/\d+/g).slice(0,3).map(x=>Number(x).toString(16).padStart(2,'0')).join('');
          const fill=panel?hex(getComputedStyle(panel).fill):null;
          const channels=fill&&[1,3,5].map(i=>parseInt(fill.slice(i,i+2),16)/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4);
          const L=channels&&channels.reduce((s,c,i)=>s+c*[.2126,.7152,.0722][i],0);
          const expected=fill&&((L+.05)/.05>=1.05/(L+.05)?'#000000':'#ffffff');
          const labels=[...document.querySelectorAll('.navigation-help,.navigation-current-tier,.navigation-handoff,.navigation-current-label,.navigation-eyebrow,.navigation-control text')].map(t=>({class:t.getAttribute('class'),text:t.textContent,fill:hex(getComputedStyle(t).fill)}));
          const failures=labels.filter(t=>t.fill!==expected);
          return {stem,panelFill:fill,expected,labels,failures,applicable:!!panel,passed:!panel||labels.length>0&&failures.length===0};
        }''',stem))
    browser.close()
server.shutdown()
report={'passed':all(r['passed'] for r in rows),'rows':rows}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
if not report['passed']:raise SystemExit(1)
