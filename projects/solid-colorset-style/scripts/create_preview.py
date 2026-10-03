#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a portable style preview from the exact canonical palette metadata."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HTML = r'''<!doctype html>
<html lang="en" data-colorset="colorset1">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Solid fills first</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f7f7f7;color:#000000;font:16px/1.5 system-ui,sans-serif}
main{max-width:1200px;margin:auto;padding:36px 24px}h1{font-size:42px;line-height:1.1;margin:0 0 12px}p{max-width:80ch;margin:10px 0 24px}
nav{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}button{border:0;background:#e7e7e7;color:#000000;padding:12px 20px;font:inherit;cursor:pointer}
button[aria-pressed="true"]{background:#9e1b32;color:#ffffff}button:focus-visible{outline:3px solid #9e1b32;outline-offset:4px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:12px}.tile{min-height:100px;display:grid;align-content:center;gap:4px;padding:16px;position:relative}
.tile strong{font-size:19px}.tile small{font-size:12px}.tile code{font:13px Consolas,monospace}.diagram{display:flex;gap:12px;align-items:center;overflow:auto;margin:24px 0 32px;padding:2px 0}.node{flex:0 0 154px;padding:22px 12px;text-align:center;font-weight:700}.arrow{flex:0 0 16px;color:#000000}
.overflow{margin:36px 0}.overflow[hidden]{display:none}h2{font-size:25px;margin:32px 0 12px}.hint{font-size:14px}.tier{font-size:12px;letter-spacing:.07em;text-transform:uppercase}
@media(max-width:500px){main{padding:24px 16px}h1{font-size:32px}.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}.tile{padding:12px}.tile strong{font-size:16px}}
</style>
<main>
<div class="tier">Colorset presentation</div><h1>Solid fills first</h1>
<p>One opaque fill per mark, no decorative outline. Black or white text follows the actual contrast of its backing. Distinct solid colors come before border variants.</p>
<nav><button id="cs1" aria-pressed="true">Colorset 1</button><button id="cs2" aria-pressed="false">Colorset 2</button><button id="overflow" aria-pressed="false">Show overflow variants</button></nav>
<div class="diagram" aria-label="Six connected stages"></div>
<h2 id="capacity"></h2><p class="hint">The canvas is #f7f7f7. Every other allowed color is available as a solid fill; soft colors are placed late. Category assignments stay stable.</p>
<section class="tiles" id="solids" aria-label="Solid style sequence"></section>
<section class="overflow" hidden><h2>After all solid fills are used</h2><p class="hint">Reuse fills with a contrasting border color, then dash and width. These options are reserved for categories beyond the solid capacity.</p><div class="tiles" id="variants"></div></section>
</main><script>
const palettes=__PALETTES__;
let active='colorset1',showOverflow=false;
function luminance(color){const c=[1,3,5].map(i=>parseInt(color.slice(i,i+2),16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2]}
function contrast(a,b){const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
function tile(fill,index,overflow=false){const p=palettes[active],text=p.textOnFill[fill],node=document.createElement('div');node.className='tile';node.dataset.fill=fill;node.dataset.styleIndex=index;node.dataset.tier=overflow?'overflow':'solid';node.style.background=fill;node.style.color=text;node.style.border='0';if(overflow){node.style.border=`${index%2?3:2}px ${['solid','dashed','dotted'][Math.floor(index/2)%3]} ${text}`};node.innerHTML=`<strong>${overflow?'Overflow '+(index+1):'Category '+(index+1)}</strong><code>${fill}</code><small>${text==='\u0023ffffff'?'White':'Black'} text · ${contrast(fill,text).toFixed(2)}:1</small>`;return node}
function draw(){document.documentElement.dataset.colorset=active;const fills=palettes[active].solidSequence.filter(c=>c!=='#f7f7f7');const solids=document.querySelector('#solids');solids.replaceChildren(...fills.map((fill,index)=>tile(fill,index)));document.querySelector('#capacity').textContent=`${fills.length} solid styles before any outline`;const diagram=document.querySelector('.diagram');diagram.replaceChildren();fills.slice(0,6).forEach((fill,index)=>{if(index){const arrow=document.createElement('span');arrow.className='arrow';arrow.textContent='→';diagram.append(arrow)}const node=document.createElement('div');node.className='node';node.style.background=fill;node.style.color=palettes[active].textOnFill[fill];node.textContent=['Capture','Prepare','Model','Validate','Publish','Review'][index];diagram.append(node)});document.querySelector('#variants').replaceChildren(...fills.slice(0,6).map((fill,index)=>tile(fill,index,true)));document.querySelector('.overflow').hidden=!showOverflow;document.querySelector('#cs1').setAttribute('aria-pressed',active==='colorset1');document.querySelector('#cs2').setAttribute('aria-pressed',active==='colorset2');document.querySelector('#overflow').setAttribute('aria-pressed',showOverflow)}
document.querySelector('#cs1').onclick=()=>{active='colorset1';draw()};document.querySelector('#cs2').onclick=()=>{active='colorset2';draw()};document.querySelector('#overflow').onclick=()=>{showOverflow=!showOverflow;draw()};draw();
</script></html>'''


def main():
    document = json.loads((ROOT / "docs/colorsets.json").read_text(encoding="utf-8"))
    target = ROOT / "projects/solid-colorset-style/artifacts/previews/style-guide.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(HTML.replace("__PALETTES__", json.dumps(document["colorsets"])), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
