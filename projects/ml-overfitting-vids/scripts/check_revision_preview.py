#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Check actual preview selection/scrub controls outside the film."""
import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def main():
 source=ROOT/'artifacts/revision/source-check-r3/artifacts/composition';server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(source)));threading.Thread(target=server.serve_forever,daemon=True).start();paths=sorted((Path(os.environ['LOCALAPPDATA'])/'ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=str(paths[0]),headless=True);page=browser.new_page(viewport={'width':1440,'height':950});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/preview.html');page.locator('#scene option').last.wait_for(state='attached');page.locator('#scene').select_option('2');page.locator('#seek').fill('8.3');state=page.evaluate('window.state');page.locator('#scene').select_option('4');page.locator('#seek').fill('12');state2=page.evaluate('window.state');page.locator('#play').click();playing=page.locator('#play').inner_text()=='Pause';page.locator('#play').click();outside=page.evaluate('document.querySelector("#controls").getBoundingClientRect().top>=document.querySelector("#stage").getBoundingClientRect().bottom');page.screenshot(path=str(ROOT/'artifacts/revision/preview-controls.png'));browser.close()
 server.shutdown();report={'ok':not errors and state['index']==2 and state['target']=='split-validation' and state2['index']==4 and playing and outside,'sceneSelection':state['index'],'scrubTarget':state['target'],'nextSelection':state2['index'],'playControl':playing,'controlsOutsideFilm':outside,'errors':errors};(ROOT/'artifacts/revision/preview-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return 0 if report['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
