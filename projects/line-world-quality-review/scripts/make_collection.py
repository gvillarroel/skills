#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Declare the maintained deliveries and retain earlier movies as historical evidence."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent


def main():
    videos=[]
    entries=[
      ('ml','ml-overfitting-vids','ml-overfitting-polished.mp4','svg','artifacts/composition','story.json','artifacts/revision/cues.json'),
      ('cuda','cuda-alexnet-vids','cuda-alexnet-polished.mp4','svg','artifacts/composition','story.json','artifacts/data/cues.json'),
      ('seal','seal-paper-vids','seal-paper-polished.mp4','paper','artifacts/composition','story.json',None),
      ('reddit','reddit-navigation-video','reddit-navigation.mp4','website','artifacts/composition','story.json',None),
      ('linked','line-world-video','line-world-polished-linked.mp4','starter','artifacts/polished-linked','artifacts/polished-linked/timing.json',None),
      ('atlas','line-world-video','line-world-reviewed-atlas.mp4','starter','artifacts/polished-atlas','artifacts/polished-atlas/timing.json',None)]
    for identity,project,movie,kind,source,story,cues in entries:
        prefix='../'+project+'/'
        row={'id':identity,'role':'current','production':identity,'video':prefix+'artifacts/videos/'+movie,'story':prefix+story,'sourceKind':kind,'html':prefix+source+'/index.html','manualReview':'artifacts/manual/'+identity+'.json','provenance':{'nativeGoogleVidsExport':False,'nativeHyperFramesRender':False,'renderer':'Local HTML/SVG, isolated browser and FFmpeg','voice':'Actual approved Google Vids generation, unchanged AAC stream' if identity in ['ml','cuda','seal'] else 'Edge speech, es-CL-CatalinaNeural' if identity=='reddit' else 'Intentionally silent style demonstration'}}
        if cues:row.update(cues=prefix+cues,clock='scene-local')
        if identity in ['ml','cuda','linked','atlas']:row['checks']=['focus-motion']
        if identity=='cuda':row['checks'].append('photo-focus')
        videos.append(row)
    for identity in ['focus-motion','photo-focus']:
        prefix='../line-world-video/artifacts/'+identity+'-demo/'
        clock=ROOT/'artifacts'/(identity+'-clock.json');clock.write_text(json.dumps({'scenes':[{'id':identity,'clipSeconds':9}]})+'\n',encoding='utf-8')
        videos.append({'id':identity,'role':'current','video':prefix+identity+'-demo.mp4','story':'artifacts/'+clock.name,'sourceKind':'encoded','html':prefix+'scene.html','checks':[identity],'manualReview':'artifacts/manual/'+identity+'.json','provenance':{'nativeGoogleVidsExport':False,'nativeHyperFramesRender':False,'voice':'Intentionally silent feature demonstration'}})
    current_paths={(ROOT/v['video']).resolve() for v in videos}
    for i,item in enumerate(json.loads((ROOT/'baseline-inventory.json').read_text(encoding='utf-8'))):
        path=ROOT.parents[1]/item['path']
        if path.resolve() in current_paths:continue
        videos.append({'id':'history-'+str(i+1).zfill(2)+'-'+path.stem[:48].replace('_','-'),'role':'reference','video':'../../'+item['path'],'sourceKind':'encoded','provenance':{'status':'Superseded export, draft or retained native voice reference; not the current delivery.'}})
    (ROOT/'collection.json').write_text(json.dumps({'schemaVersion':1,'videos':videos},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'current':sum(v['role']=='current' for v in videos),'references':sum(v['role']=='reference' for v in videos),'manifest':str(ROOT/'collection.json')}))


if __name__=='__main__':main()
