#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain unmodified selected and rejected Commons candidates for local review."""

import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path


FILES = {
    'observing-astrolabe.svg': 'Astrolabe PSF.svg',
    'sextant.png': 'Stronomiska instrument, Sextant, Nordisk familjebok transparent.png',
    'vase-psf.png': 'Vase (PSF).png',
    'pendulum-psf.png': 'Pendulum 2 (PSF).png',
    'telescope-psf.svg': 'Telescope (PSF).svg',
    'cuneiform-tablet.png': 'Cuneiform script2.png',
    'conch-psf.png': 'Conch (PSF).png',
}

# Vase, pendulum and conch were rejected after inspection of their opaque
# backgrounds. Keeping this local evidence does not add them to the skill.


def main():
    folder=Path(__file__).resolve().parent.parent/'artifacts/images/engraving-sources'
    folder.mkdir(parents=True,exist_ok=True)
    records=[]
    for filename,title in FILES.items():
        canonical=title.replace(' ','_')
        digest=hashlib.md5(canonical.encode()).hexdigest()
        url=f'https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/'+urllib.parse.quote(canonical)
        if (folder/filename).exists():
            content=(folder/filename).read_bytes()
        else:
            time.sleep(2)
            request=urllib.request.Request(url,headers={'User-Agent':'EducationalPosterResearch/1.0 (local visual study)'})
            with urllib.request.urlopen(request,timeout=30) as response:
                content=response.read()
            (folder/filename).write_bytes(content)
        record=dict(file=filename,source_title=title,source_url='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(canonical),image_url=url,
            bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),modified=False)
        records.append(record)
        print(json.dumps(record))
        (folder/'downloads.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
