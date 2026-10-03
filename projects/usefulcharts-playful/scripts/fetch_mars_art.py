#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.28", "beautifulsoup4>=4.13"]
# ///
"""Discover and retain NASA visual references with image-level provenance."""
from pathlib import Path
import json
import hashlib
import httpx
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
PAGES={
 'mariner':'https://science.nasa.gov/mission/mariner-9/',
 'viking':'https://science.nasa.gov/mission/viking/spacecraft-and-science/',
 'mgs':'https://science.nasa.gov/mission/mars-global-surveyor/',
 'pathfinder':'https://science.nasa.gov/mission/mars-pathfinder/',
 'nozomi':'https://science.nasa.gov/mission/nozomi/',
 'soviet':'https://www.nasa.gov/history/50-years-ago-mariner-9-launches-to-orbit-mars/',
 'mars96':'https://www.nasa.gov/history/25-years-of-continuous-robotic-mars-exploration-from-pathfinder-to-perseverance/',
}
def main():
    out=ROOT/'artifacts/references';out.mkdir(parents=True,exist_ok=True);results=[]
    for key,url in PAGES.items():
        cache=out/(key+'.html')
        if not cache.exists():
            response=httpx.get(url,follow_redirects=True,timeout=45);response.raise_for_status();cache.write_text(response.text,encoding='utf-8')
        soup=BeautifulSoup(cache.read_text(encoding='utf-8'),'html.parser')
        for index,img in enumerate(soup.find_all('img')):
            alt=img.get('alt','');src=img.get('src','')
            if key in ('nozomi','soviet','mars96') or any(word in (alt+' '+src).lower() for word in ('mariner','viking','surveyor','pathfinder','sojourner')):
                if key in ('nozomi','soviet','mars96') and ('.svg' in src or 'NASA'==alt):continue
                results.append(dict(id=key+'-'+str(index),page=url,alt=alt,url=src))
    (out/'discovered.json').write_text(json.dumps(results,indent=2)+'\n')
    selected=['mariner-38','viking-38','viking-41','pathfinder-41','mariner-42','nozomi-39','soviet-43','soviet-44','mars96-45','mars96-40','mars96-39']
    saved=[]
    for record in results:
        if record['id'] not in selected:continue
        target=out/(record['id']+'.jpg')
        if not target.exists():
            response=httpx.get(record['url'],follow_redirects=True,timeout=45);response.raise_for_status();target.write_bytes(response.content)
        saved.append(dict(record,path=target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    (out/'selected.json').write_text(json.dumps(saved,indent=2)+'\n')
    print(json.dumps(dict(saved=len(saved),ids=[r['id'] for r in saved])))
if __name__=='__main__':main()
