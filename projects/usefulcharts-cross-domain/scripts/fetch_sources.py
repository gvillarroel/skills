#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.28", "pymupdf>=1.25"]
# ///
"""Retain official factual source snapshots for three diagram critique cases."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import httpx
import pymupdf

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/sources'
SOURCES={
    'bsd-family-tree.txt':'https://raw.githubusercontent.com/freebsd/freebsd-src/main/share/misc/bsd-family-tree',
    'hornbostel-sachs-2011.pdf':'https://biblio.ugent.be/publication/01HN30DTX2BZYYEVXRG7Q7M06Q/file/01HN30HH8E2E3BWM8YAZ7CPP8C.pdf',
    'mars-press-kit.pdf':'https://mars.nasa.gov/system/downloadable_items/45585_mars_2020_landing_press_kit.pdf',
}
def fetch(item):
    name,url=item;target=OUT/name
    if not target.is_file() or (name.endswith('.pdf') and not target.read_bytes().startswith(b'%PDF')):
        response=httpx.get(url,follow_redirects=True,timeout=60);response.raise_for_status();target.write_bytes(response.content)
    record=dict(file=name,url=url,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size)
    if name.endswith('.pdf'):
        doc=pymupdf.open(target);record['pages']=len(doc)
        target.with_suffix('.txt').write_text('\n'.join(f'\nPAGE {i+1}\n'+page.get_text() for i,page in enumerate(doc)),encoding='utf-8')
    return record
def main():
    OUT.mkdir(parents=True,exist_ok=True);records=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(fetch,SOURCES.items()):records.append(result);print(json.dumps(result))
    (OUT/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
