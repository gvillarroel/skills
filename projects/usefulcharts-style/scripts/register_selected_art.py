#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Register two visually inspected, unmodified sources with transparent fields."""

import hashlib
import json
import shutil
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'projects/usefulcharts-style/artifacts/images/engraving-sources'
TARGET=ROOT/'skills/usefulcharts-style/assets/illustrations'


def main():
    downloads={r['file']:r for r in json.loads((SOURCE/'downloads.json').read_text())}
    additions=[
        dict(id='telescope-observer',file='telescope-observer.svg',download='telescope-psf.svg',
             title='Observer at a large refracting telescope',creator='Pearson Scott Foresman; SVG uploaded by AzaToth',
             source_revision=1112658303,
             rights='Public domain dedication by Pearson Scott Foresman, confirmed by Wikimedia VRTS ticket 2010061110041093.',
             date_note='Undated explanatory illustration; vector file uploaded on 2007-12-02. This is not evidence of an instrument at a fictional event.',
             background='Transparent SVG field, visually inspected against the poster paper.'),
        dict(id='cuneiform-tablet',file='cuneiform-tablet.png',download='cuneiform-tablet.png',
             title='Cuneiform tablet, Kirkor Minassian collection, Library of Congress, cf0013',
             creator='Library of Congress; transparent derivative by Yjenith',source_revision=911771686,
             collection_url='https://hdl.loc.gov/loc.amed/amcune.cf0013',
             rights='Source marked PD-USGov and Public Domain Mark 1.0 on Wikimedia Commons.',
             date_note='Tablet dated 2041–2040 BCE in the source description. Transparent derivative uploaded on 2012-02-28. Contextual illustration, not a record of fictional Riverlands.',
             background='PNG with transparency, visually inspected against the poster paper.')]
    path=TARGET/'provenance.json';manifest=json.loads(path.read_text(encoding='utf-8'))
    for item in additions:
        filename=item.pop('download');record=downloads[filename];content=(SOURCE/filename).read_bytes()
        assert hashlib.sha256(content).hexdigest()==record['sha256']
        item.update({k:record[k] for k in ('source_url','image_url','sha256','bytes','modified')})
        if filename.endswith('.svg'):
            root=ET.fromstring(content)
            dims=root.get('viewBox').split() if root.get('viewBox') else None
            if dims:width,height=map(float,dims[2:])
            else:
                def dimension(value):
                    return float(value[:-2])*1.25 if value.endswith('pt') else float(value)
                width,height=dimension(root.get('width')),dimension(root.get('height'))
            item.update(width=width,height=height,mime_type='image/svg+xml')
        else:
            width,height=struct.unpack('>II',content[16:24])
            assert content[25] in (4,6) or b'tRNS' in content
            item.update(width=width,height=height,mime_type='image/png')
        shutil.copyfile(SOURCE/filename,TARGET/item['file'])
        manifest['items']=[r for r in manifest['items'] if r['id']!=item['id']]+[item]
    path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Registered two unchanged transparent illustration sources.')


if __name__=='__main__':main()
