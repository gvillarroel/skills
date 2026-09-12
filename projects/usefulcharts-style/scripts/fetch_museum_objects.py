#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fetch a small, explicitly selected public-domain museum object collection."""

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (educational poster study)'})
    return urllib.request.urlopen(request,timeout=45).read()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    items=[]
    for identifier in [90589,57819,246,60878,191,50240,27881,15190]:
        record=json.loads(fetch(f'https://api.artic.edu/api/v1/artworks/{identifier}?fields=id,title,image_id,is_public_domain,artist_title,date_start,date_end'))['data']
        if not record['is_public_domain'] or not record['image_id']:raise ValueError('Selected artwork lacks public-domain imagery.')
        url=f'https://www.artic.edu/iiif/2/{record["image_id"]}/full/200,/0/default.jpg'
        content=fetch(url);filename=f'{identifier}.jpg';(args.output/filename).write_bytes(content)
        items.append(dict(record,file=filename,image_url=url,source=f'https://www.artic.edu/artworks/{identifier}',sha256=hashlib.sha256(content).hexdigest()))
    provenance=dict(provider='Art Institute of Chicago',rights='Public-domain artworks according to the museum API; museum imagery offered under CC0.',terms='https://api.artic.edu/docs/#copyright',purpose='Decorative collection samples for synthetic posters; their real titles and dates are preserved here. They are not evidence of invented events.',items=items)
    (args.output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    print(f'Fetched {len(items)} verified museum object samples.')


if __name__=='__main__':main()
