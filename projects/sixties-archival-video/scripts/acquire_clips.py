#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Download the visually selected stable Destockd identities, retaining original receipts."""
import concurrent.futures
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[1]
HELPER = REPO/'skills/destockd-video-search/scripts/destockd.py'
SELECTIONS = [
    ('street-01','hampton62-shots','shot_011',1962,'Hampton', 'Street, cars, shops and parade spectators.'),
    ('street-02','hampton62-shots','shot_021',1962,'Hampton', 'A second actual view of the same parade route.'),
    ('travel-01','fashion64-shots','shot_006',1964,'Rome / fashion report', 'Model at a TWA aircraft; fashion-report context, not a typical passenger survey.'),
    ('travel-02','fashion64-shots','shot_007',1964,'Rome / fashion report', 'Red travel coat and hat in the original color report.'),
    ('fashion-01','fashion64-shots','shot_011',1964,'Rome', 'Red textured garment; actual filmed fashion presentation.'),
    ('fashion-02','fashion64-shots','shot_015',1964,'Rome', 'Ochre outfit in a full-length original shot.'),
    ('fashion-03','fashion64-shots','shot_018',1964,'Rome', 'Evening clothes on a terrace; no unverified personal identity.'),
    ('cinema-01','newsreel38-shots','shot_048',1965,'Hollywood', 'Exterior of the 37th Academy Awards and arrivals.'),
    ('cinema-02','newsreel38-shots','shot_049',1965,'Hollywood', 'Wide auditorium view; not an ordinary theater audience.'),
    ('cinema-03','newsreel38-shots','shot_050',1965,'Hollywood', 'Academy Awards audience; no individual identification claimed.'),
    ('phone-01','chicago68-shots','shot_026',1968,'Chicago', 'Campaign workers using wired telephones.'),
    ('phone-02','chicago68-shots','shot_027',1968,'Chicago', 'Campaign telephone desks; not a private home.'),
    ('television-01','chicago68-shots','shot_028',1968,'Chicago', 'A worker watches the convention on an actual television.'),
    ('office-01','chicago68-shots','shot_029',1968,'Chicago', 'Telephones and paper in the convention workplace.'),
    ('rights-01','rights63-shots','shot_007',1963,'Somerville, Tennessee', 'Street and storefront in a documented civil-rights demonstration.'),
    ('rights-02','rights63-shots','shot_008',1963,'Somerville, Tennessee', 'People outside the storefront; archive describes protest and alleged police abuses.'),
]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def acquire(spec):
    alias, manifest_name, shot, year, place, observation = spec
    manifest = ROOT/'artifacts/data'/(manifest_name+'.json')
    rows = json.loads(manifest.read_text(encoding='utf-8'))['results']
    row = next(r for r in rows if r['shot']==shot)
    destination = ROOT/'artifacts/clips'/(alias+'.mp4'); receipt=destination.with_suffix('.mp4.json')
    if destination.is_file() and receipt.is_file():
        old = json.loads(receipt.read_text(encoding='utf-8'))
        if old.get('sha256') != sha(destination):raise ValueError('Changed downloaded clip: '+alias)
    else:
        result=subprocess.run(['uv','run','--script',str(HELPER),'download','--manifest',str(manifest),'--id',row['id'],'--output',str(destination)],capture_output=True,text=True,encoding='utf-8')
        (ROOT/'artifacts/reviews'/(alias+'-download.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
        if result.returncode:raise ValueError('Download failed: '+alias+'; inspect its download log.')
    metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(destination)],text=True,encoding='utf-8'))
    video=next(s for s in metadata['streams'] if s['codec_type']=='video')
    record={'alias':alias,'id':row['id'],'film':row['film'],'shot':shot,'option':row['option'],'searchManifest':manifest.relative_to(ROOT).as_posix(),'pageUrl':row['page_url'],'year':year,'place':place,'observation':observation,'file':destination.relative_to(ROOT).as_posix(),'receipt':receipt.relative_to(ROOT).as_posix(),'sha256':sha(destination),'seconds':float(metadata['format']['duration']),'width':video['width'],'height':video['height'],'sampleAspectRatio':video.get('sample_aspect_ratio'),'avgFrameRate':video['avg_frame_rate']}
    print(json.dumps({k:record[k] for k in ['alias','seconds','width','height']}),flush=True)
    return record


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(acquire,SELECTIONS))
    output=ROOT/'artifacts/data/selected-clips.json';output.write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'selected':len(records),'manifest':str(output)}))


if __name__=='__main__':main()
