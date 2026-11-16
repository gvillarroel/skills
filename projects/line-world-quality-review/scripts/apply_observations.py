#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply frozen observations only to the exact movies and sources actually reviewed."""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parents[1]
sys.path.insert(0,str(REPO/'skills/line-world-video/scripts'))
from review_collection import source_fingerprint,manual_status


def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    observed=read(ROOT/'observations.json');entries={e['id']:e for e in read(ROOT/'collection.json')['videos'] if e['role']=='current'}
    for record in observed['videos']:
        identity=record['id'];entry=entries[identity];result=read(ROOT/'artifacts/current'/identity/'result.json')
        if not result['machineOK']:raise ValueError('Resolve the actual machine findings first: '+identity)
        if record['videoSha256']!=result['videoSha256'] or record['sourceSha256']!=result['sourceSha256']:raise ValueError('Frozen observations are stale: '+identity)
        if hashlib.sha256((ROOT/entry['video']).read_bytes()).hexdigest()!=record['videoSha256']:raise ValueError('The reviewed movie changed: '+identity)
        source=source_fingerprint((ROOT/entry['html']).resolve(),[REPO/'skills/line-world-video/scripts/review_video.py',REPO/'skills/line-world-video/scripts/review_collection.py'])
        if source!=record['sourceSha256']:raise ValueError('The reviewed source changed: '+identity)
        path=ROOT/'artifacts/manual'/(identity+'.json');path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps({k:v for k,v in record.items() if k!='id'},indent=2)+'\n',encoding='utf-8')
        if manual_status(path,record['videoSha256'],record['sourceSha256'],result['scenes'])!='recorded':raise ValueError('Scene observations are incomplete: '+identity)
        print(json.dumps({'id':identity,'frozenSceneObservations':len(record['scenes'])}))


if __name__=='__main__':main()
