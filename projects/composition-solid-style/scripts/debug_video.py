#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
import functools,http.server,threading,json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[3]
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1600,'height':1000})
    page.goto(f'http://127.0.0.1:{server.server_port}/skills/video/assets/examples/ai-concept-videos/index.html')
    page.wait_for_function('typeof window.renderConceptFrame === "function"')
    page.evaluate('renderConceptFrame(AI_CONCEPTS[0].id,119,{capture:true})')
    result=page.evaluate('''() => [...document.querySelectorAll('svg text')].filter(t=>/Gemma|4/.test(t.textContent)).map(t=> {const b=t.getBoundingClientRect();return {text:t.textContent,fill:getComputedStyle(t).fill,style:t.style.fill,box:b.toJSON(),parents:t.parentNode.outerHTML.slice(0,500),candidates:[...document.querySelectorAll('svg rect')].filter(r=>{const b2=r.getBoundingClientRect();return b2.left<b.left&&b2.right>b.right&&b2.top<b.top&&b2.bottom>b.bottom}).map(r=>{const m=r.getScreenCTM();const p=new DOMPoint(b.left+b.width*.2,b.top+b.height*.5).matrixTransform(m.inverse());return {fill:getComputedStyle(r).fill,style:r.style.fill,bbox:[r.getBBox().x,r.getBBox().y,r.getBBox().width,r.getBBox().height],point:[p.x,p.y],inside:r.isPointInFill(p),follow:!!(r.compareDocumentPosition(t)&Node.DOCUMENT_POSITION_FOLLOWING)}})};})''')
    print(json.dumps(result,indent=2));browser.close()
server.shutdown()
