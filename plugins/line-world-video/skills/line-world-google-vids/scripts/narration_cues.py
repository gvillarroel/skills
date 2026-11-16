#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Align semantic focus cues with supplied audio word timestamps, never word-count estimates."""
import argparse,json,math,re,unicodedata
from pathlib import Path

ALIASES={'sesenta':['60'],'veinte':['20'],'cinco':['5'],'ele':['l'],'dos':['2']}
def normalized(value):
    value=''.join(c for c in unicodedata.normalize('NFD',str(value).lower()) if unicodedata.category(c)!='Mn')
    words=re.findall(r'[a-z0-9]+',value)
    return [ALIASES.get(w,[w])[0] for w in words]
def align(transcript,timing,spec):
    words=[w for segment in transcript['segments'] for w in segment.get('words',[])]
    for w in words:
        if any(isinstance(w.get(k),bool) or not isinstance(w.get(k),(float,int)) or not math.isfinite(w[k]) for k in ['start','end']) or w['start']<0 or w['end']<w['start']:raise ValueError('Word timestamps must be finite ordered intervals.')
    if any(a['start']>b['start'] for a,b in zip(words,words[1:])):raise ValueError('Transcript words must follow audio order.')
    for s in timing['scenes']:
        if any(isinstance(s.get(k),bool) or not isinstance(s.get(k),(float,int)) or not math.isfinite(s[k]) for k in ['start','end','duration']) or s['start']<0 or s['end']<=s['start'] or abs(s['end']-s['start']-s['duration'])>1e-5:raise ValueError('Scene timing must contain finite consistent intervals.')
    if len({s['id'] for s in timing['scenes']})!=len(timing['scenes']):raise ValueError('Timing scene IDs must be unique.')
    by_id={s['id']:s for s in timing['scenes']};result=[];ids=set()
    for block in spec['scenes']:
        sid=block['id']
        if sid not in by_id or sid in ids:raise ValueError('Cue scenes need unique known stable IDs.')
        ids.add(sid);scene=by_id[sid]
        # A small boundary tolerance accommodates an ASR token straddling a cut.
        local=[w for w in words if scene['start']-.12<=w['start']<scene['end']];tokens=[]
        for index,w in enumerate(local):
            for token in normalized(w['word']):tokens.append((token,index))
        aligned=[];last=-1
        for cue in block['cues']:
            travel=cue.get('travelSeconds',.28)
            if not isinstance(cue.get('target'),str) or not cue['target'].strip() or isinstance(travel,bool) or not isinstance(travel,(int,float)) or not math.isfinite(travel) or not .1<=travel<=.45:raise ValueError('Cues need a target and travelSeconds between 0.1 and 0.45.')
            phrases=[cue['phrase'],*cue.get('alternatives',[])];matches={}
            for phrase in phrases:
                needle=normalized(phrase)
                if not needle:raise ValueError('Empty cue phrase.')
                for i in range(len(tokens)-len(needle)+1):
                    if [v[0] for v in tokens[i:i+len(needle)]]==needle:
                        a,b=tokens[i][1],tokens[i+len(needle)-1][1];matches[(a,b)]=(local[a]['start'],local[b]['end'])
            matches=sorted(matches.values());occurrence=cue.get('occurrence',1)
            if isinstance(occurrence,bool) or not isinstance(occurrence,int) or occurrence<1 or occurrence>len(matches):raise ValueError('Unmatched cue '+sid+'/'+cue['target']+': '+cue['phrase'])
            start,end=matches[occurrence-1];local_start=max(0,start-scene['start'])
            if local_start<last-1e-8:raise ValueError('Cues must follow speech order: '+sid)
            last=local_start
            aligned.append({**cue,'at':local_start,'end':end-scene['start'],'audioStart':start,'audioEnd':end,'evidence':'supplied ASR word timestamps; approximate alignment','travelSeconds':cue.get('travelSeconds',.28)})
        result.append({'id':sid,'duration':scene['duration'],'cues':aligned})
    return {'schemaVersion':1,'status':'aligned-to-audio','sourceModel':transcript.get('model','supplied word timestamps'),'clock':'scene-local seconds from measured scene starts','scenes':result}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ['transcript','timing','spec','output']:p.add_argument('--'+flag,type=Path,required=True)
    a=p.parse_args()
    try:
        value=align(json.loads(a.transcript.read_text(encoding='utf-8-sig')),json.loads(a.timing.read_text(encoding='utf-8-sig')),json.loads(a.spec.read_text(encoding='utf-8-sig')))
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps({'ok':True,'scenes':len(value['scenes']),'cues':sum(len(s['cues']) for s in value['scenes']),'output':str(a.output)}));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:print(json.dumps({'ok':False,'error':str(e)}));return 2
if __name__=='__main__':raise SystemExit(main())
