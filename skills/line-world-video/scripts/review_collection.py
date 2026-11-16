#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Review an explicit video collection and distinguish current deliveries from history."""
import argparse
import hashlib
import html
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SKILL=Path(__file__).resolve().parent.parent
SCRIPTS=SKILL/'scripts'


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def resolve(base,value): return (base/value).resolve()


def source_fingerprint(document, extras=()):
    extensions={'.html','.js','.css','.json','.svg','.png','.jpg','.jpeg','.webp','.ttf','.woff','.woff2','.mp3','.wav','.csv'}
    files=sorted((p for p in document.parent.rglob('*') if p.is_file() and p.suffix.lower() in extensions and not any(n in {'node_modules','.cache','__pycache__'} for n in p.parts)),key=lambda p:p.relative_to(document.parent).as_posix())
    values=[(p.relative_to(document.parent).as_posix(),sha(p)) for p in files]+[(str(p),sha(p)) for p in extras]
    return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()


def normalize_story(value):
    scenes=value.get('scenes',value.get('beats',[]))
    result=[]
    for s in scenes:
        duration=s.get('clipSeconds',s.get('duration'))
        if duration is None: raise ValueError('Each scene or beat needs an explicit duration.')
        result.append({**s,'clipSeconds':duration})
    if not result: raise ValueError('Provide an ordered scene or beat clock.')
    return {'scenes':result}


def validate_entries(entries):
    ids=set();current=set()
    for entry in entries:
        identity=entry.get('id','')
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',identity) or identity in ids: raise ValueError('Use unique lowercase hyphen-case video IDs.')
        ids.add(identity)
        if entry.get('role','current') not in {'current','reference'}: raise ValueError('Use current or reference roles.')
        if entry.get('sourceKind','encoded') not in {'encoded','svg','paper','website','starter'}: raise ValueError('Declare the actual source kind.')
        if any(c not in {'focus-motion','photo-focus'} for c in entry.get('checks',[])):raise ValueError('Use focus-motion or photo-focus supplemental checks.')
        if entry.get('role','current')=='current':
            key=entry.get('production',identity)
            if key in current: raise ValueError('Declare only one current delivery per production.')
            current.add(key)


def manual_status(path,video_sha,source_sha,scenes):
    if path is None or not path.is_file():return 'pending'
    data=read(path)
    if data.get('videoSha256')!=video_sha or data.get('sourceSha256')!=source_sha:return 'stale'
    records=data.get('scenes',[])
    if len(records)!=len(scenes) or {s.get('id') for s in records}!={s['id'] for s in scenes}:return 'incomplete'
    return 'recorded' if all(s.get('reviewed') is True and str(s.get('notes','')).strip() for s in records) else 'incomplete'


def invoke(command,log):
    # Each specialist owns its UV metadata (for example PyMuPDF or resvg).
    # Do not assume the collection's interpreter has their optional packages.
    process=subprocess.run(['uv','run','--script',*map(str,command)],capture_output=True,text=True,encoding='utf-8')
    log.write_text(process.stdout+process.stderr,encoding='utf-8')
    # A diagnostic failure is retained as evidence; never convert it to success.
    return process.returncode


def review_entry(entry,base,output):
    identity=entry['id'];folder=output/identity;folder.mkdir(exist_ok=True)
    video=resolve(base,entry['video']);video_sha=sha(video);kind=entry.get('sourceKind','encoded')
    document=resolve(base,entry['html']) if entry.get('html') else None
    if document and document.is_relative_to(output):raise ValueError('Review output must not contain authored source.')
    source_sha=source_fingerprint(document,[SCRIPTS/'review_video.py',SCRIPTS/'review_collection.py']) if document else None
    if entry.get('story'):story=normalize_story(read(resolve(base,entry['story'])))
    else:
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)]))
        stream=next(s for s in probe['streams'] if s['codec_type']=='video');a,b=map(int,stream['r_frame_rate'].split('/'))
        story={'scenes':[{'id':identity,'clipSeconds':int(stream['nb_frames'])*b/a}]}
    story_path=folder/'scene-clock.json';save(story_path,story)
    command=[SCRIPTS/'review_video.py','--video',video,'--story',story_path,'--output',folder/'encoded']
    for key in ['timing','cues']:
        if entry.get(key):command+=['--'+key,resolve(base,entry[key])]
    if kind=='svg':
        if not document:raise ValueError('SVG review requires html.')
        command+=['--html',document,'--clock',entry.get('clock','global'),'--guide-selector',entry.get('guideSelector','#guide')]
    code=invoke(command,folder/'review.log');machine=read(folder/'encoded/summary.json')
    source_audit=None
    if kind in {'paper','website','starter'}:
        if not document:raise ValueError('Specialist source review requires html.')
        specialist={'paper':'paper_video.py','website':'website_video.py','starter':'render_line_world.py'}[kind]
        stamp=hashlib.sha256((source_sha+sha(SCRIPTS/specialist)).encode()).hexdigest()
        receipt=folder/'source-receipt.json';audit=folder/'source-audit.json'
        cached=read(receipt) if receipt.is_file() else {}
        reused=cached.get('inputsSha256')==stamp and audit.is_file() and cached.get('auditSha256')==sha(audit)
        if not reused:
            args=[SCRIPTS/specialist]
            if kind=='paper':args+=['audit','--project',document.parent,'--report',audit]
            elif kind=='website':args+=['render','--project',document.parent,'--output',folder/'unused.mp4','--report',audit,'--audit-only']
            else:args+=['--project',document.parent,'--report',audit,'--audit-only']
            source_code=invoke(args,folder/'source.log')
            save(receipt,{'inputsSha256':stamp,'auditSha256':sha(audit) if audit.is_file() else None,'exitCode':source_code})
        else:source_code=cached['exitCode']
        source_audit={'ok':source_code==0 and audit.is_file() and read(audit).get('ok') is True,'reused':reused,'report':str(audit)}
    effects=[]
    for check in entry.get('checks',[]):
        if not document:raise ValueError('Effect checks require the actual source HTML.')
        tool=SCRIPTS/('inspect_focus_motion.py' if check=='focus-motion' else 'photo_focus.py')
        stamp=hashlib.sha256((source_sha+sha(tool)).encode()).hexdigest();receipt=folder/(check+'-receipt.json');audit=folder/(check+'.json')
        old=read(receipt) if receipt.is_file() else {}
        reused=old.get('inputsSha256')==stamp and audit.is_file() and old.get('auditSha256')==sha(audit)
        if reused:check_code=old['exitCode']
        else:
            args=[tool]+(['inspect'] if check=='photo-focus' else [])+['--html',document,'--output',audit,'--screenshot',folder/(check+'.png')]
            check_code=invoke(args,folder/(check+'.log'));save(receipt,{'inputsSha256':stamp,'auditSha256':sha(audit) if audit.is_file() else None,'exitCode':check_code})
        effects.append({'check':check,'ok':check_code==0 and audit.is_file() and read(audit).get('ok') is True,'reused':reused,'report':str(audit)})
    manual=manual_status(resolve(base,entry['manualReview']) if entry.get('manualReview') else None,video_sha,source_sha,story['scenes'])
    ok=code==0 and machine['ok'] and (source_audit is None or source_audit['ok']) and all(e['ok'] for e in effects)
    row={'id':identity,'production':entry.get('production',identity),'role':entry.get('role','current'),'video':str(video),'videoSha256':video_sha,'sourceSha256':source_sha,'sourceKind':kind,'machineOK':ok,'manualReview':manual,'deliveryReady':ok and manual=='recorded','decodedFrames':machine.get('decodedFrames',0),'insufficientContentFrames':machine.get('insufficientContentFrames'),'guideEvents':machine.get('guideEvents'),'advisories':machine.get('advisories'),'sourceAudit':source_audit,'effectAudits':effects,'review':str(folder/'encoded/index.html'),'scenes':story['scenes'],'provenance':entry.get('provenance',{})}
    row.update(encodedCache=machine.get('cache'),contentReused=machine.get('contentReused'),sourceReused=machine.get('sourceReused'))
    if row['role']=='current':
        samples=read(folder/'encoded/report.json').get('samples',[])
        if samples:row['poster']=str(folder/'encoded'/samples[0]['image'])
    save(folder/'result.json',row)
    print(json.dumps({k:row[k] for k in ['id','role','machineOK','manualReview','decodedFrames']}),flush=True)
    return row


def review(manifest,output,include_reference=False,jobs=2):
    if type(jobs) is not int or not 1<=jobs<=4:raise ValueError("Use one to four review jobs.")
    data=read(manifest);entries=data['videos'];validate_entries(entries);base=manifest.parent
    if output.is_relative_to(SKILL):raise ValueError('Keep the skill read-only.')
    selected=[e for e in entries if include_reference or e.get('role','current')=='current']
    output.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results=list(pool.map(lambda e:review_entry(e,base,output),selected))
    current=[r for r in results if r['role']=='current']
    summary={'ok':bool(current) and all(r['machineOK'] for r in current),'deliveryReady':bool(current) and all(r['deliveryReady'] for r in current),'currentVideos':len(current),'referenceVideos':len(results)-len(current),'decodedFrames':sum(r['decodedFrames'] for r in results),'videos':results,'scope':'Actual encoded content and decode for every selected movie, source-specific audits for current compositions, and explicit hash-bound visual observations. Reference findings do not certify or block a newer current delivery. Native Vids status is declared separately.'}
    save(output/'summary.json',summary)
    cards=[]
    for row in results:
        url=lambda p:html.escape(Path(os.path.relpath(p,output)).as_posix(),quote=True)
        player='<video controls preload="none" style="width:100%;aspect-ratio:16/9" src="'+url(row['video'])+'"'+(' poster="'+url(row['poster'])+'"' if row.get('poster') else '')+'></video>' if row['role']=='current' else ''
        cards.append('<article><h2>'+html.escape(row['id'])+'</h2>'+player+'<p>'+html.escape(row['role']+' · '+row['sourceKind']+' · manual: '+row['manualReview'])+'</p><p><a href="'+url(row['video'])+'">Open / download MP4</a> · <a href="'+url(row['review'])+'">Inspect frames</a></p><p>Machine: '+str(row['machineOK'])+' · Ready: '+str(row['deliveryReady'])+'</p><code>'+row['videoSha256']+'</code></article>')
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Video collection review</title><style>body{font:18px system-ui;max-width:1100px;margin:40px auto;background:white;color:#333e48}article{padding:24px 0;border-bottom:1px solid #ccc}a{color:#9e1b32}code{font-size:12px;overflow-wrap:anywhere}</style><h1>Video collection review</h1><p>'+html.escape(summary['scope'])+'</p>'+''.join(cards),encoding='utf-8')
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--include-reference',action='store_true');parser.add_argument('--jobs',type=int,choices=[1,2,3,4],default=2);args=parser.parse_args()
    try:
        result=review(args.manifest.resolve(),args.output.resolve(),args.include_reference,args.jobs)
        print(json.dumps({k:v for k,v in result.items() if k!='videos'}));return 0 if result['ok'] else 2
    except (ValueError,KeyError,OSError) as error:print(json.dumps({'ok':False,'error':str(error)}));return 2


if __name__=='__main__':raise SystemExit(main())
