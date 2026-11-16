#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check fresh native scene announcements against an ordered prepared-clip story."""
import argparse,json,re
from pathlib import Path

def parse_announcement(raw):
    position=re.search(r'Scene (\d+) of (\d+), duration ',raw)
    duration=re.search(r'duration ((?:\d+\s+(?:milliseconds?|minutes?|seconds?)\s*)+)',raw)
    objects=re.search(r'(\d+) objects? on the page',raw)
    if not position or not duration or not objects:raise ValueError('A fresh English native scene announcement with duration and object count is required.')
    seconds=sum(int(n)*({'minute':60,'second':1,'millisecond':.001}[unit.rstrip('s')]) for n,unit in re.findall(r'(\d+)\s+(milliseconds?|minutes?|seconds?)',duration.group(1)))
    audio=re.search(r'(\d+) audio clips? starts? in the scene',raw);media=re.search(r'Alt text title:\s*(.*?\.mp4)(?:\s|["\u00a0]|$)',raw)
    return {'order':int(position.group(1)),'total':int(position.group(2)),'sceneSeconds':seconds,'objects':int(objects.group(1)),'audioClipsStarting':int(audio.group(1)) if audio else 0,'media':media.group(1).strip() if media else None}

def inspect(story,observed):
    count=observed.get('sceneButtonCount');records=observed.get('scenes',[]);expected=story['scenes'];findings=[];scenes=[]
    if not isinstance(count,int) or count<1:raise ValueError('Record the actual current native scene-button count.')
    if count!=len(expected):findings.append({'kind':'scene-count-mismatch','expected':len(expected),'observed':count})
    if len(records)!=count:findings.append({'kind':'incomplete-inventory','sceneButtons':count,'announcements':len(records)})
    for order,record in enumerate(records,1):
        parsed=parse_announcement(record['announcement']);scenes.append(parsed)
        if record.get('order')!=order or parsed['order']!=order or parsed['total']!=count:findings.append({'kind':'stale-or-mismatched-announcement','order':order,'announcedOrder':parsed['order'],'announcedTotal':parsed['total'],'sceneButtons':count})
        if parsed['objects']==0:findings.append({'kind':'empty-visual-scene','order':order,'sceneSeconds':parsed['sceneSeconds'],'audioClipsStarting':parsed['audioClipsStarting']})
        if parsed['sceneSeconds']<=0:findings.append({'kind':'nonpositive-scene-duration','order':order})
    actual=[Path(s['media']).name for s in scenes if s['objects']>0 and s['media']]
    # Producer filenames can be numbered while stable scene IDs remain semantic.
    identifiers=[Path(s.get('clip') or s.get('sourceClip') or (s['id']+'.mp4')).name for s in expected]
    if actual!=identifiers:findings.append({'kind':'ordered-media-mismatch','expected':identifiers,'observed':actual})
    if actual==identifiers:
        present=[s for s in scenes if s['objects']>0 and s['media']]
        for source,native in zip(expected,present):
            if 'clipSeconds' in source and abs(source['clipSeconds']-native['sceneSeconds'])>.12:findings.append({'kind':'scene-extent-mismatch','id':source['id'],'expected':source['clipSeconds'],'observed':native['sceneSeconds']})
    return {'ok':not findings,'expectedSceneCount':len(expected),'sceneButtonCount':count,'emptyVisualScenes':sum(s['objects']==0 for s in scenes),'totalSceneSeconds':sum(s['sceneSeconds'] for s in scenes),'scenes':scenes,'findings':findings,'scope':'Supplied fresh UI observations only; no account action, media-pixel verification or speech generation is performed.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--story',type=Path,required=True);parser.add_argument('--observed',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.resolve().is_relative_to(Path(__file__).resolve().parent.parent) or args.output.resolve() in [args.story.resolve(),args.observed.resolve()]:parser.error('Keep generated reports separate from the skill and authored inputs.')
    try:
        result=inspect(json.loads(args.story.read_text(encoding='utf-8')),json.loads(args.observed.read_text(encoding='utf-8')));args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:result[k] for k in ['ok','sceneButtonCount','emptyVisualScenes','totalSceneSeconds','findings']}));return 0 if result['ok'] else 2
    except (ValueError,KeyError) as error:print(json.dumps({'ok':False,'error':str(error)}));return 2

if __name__=='__main__':raise SystemExit(main())
