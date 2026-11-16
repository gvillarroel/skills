#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Replace reviewed visuals while preserving the approved AAC voice byte for byte."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
PROJECT=Path(__file__).resolve().parent.parent
ENTRIES={
 'ml':('ml-overfitting-vids','ml-overfitting-subject-first-local.mp4','clips-revised','ml-overfitting-polished.mp4'),
 'cuda':('cuda-alexnet-vids','cuda-alexnet-reusable-local.mp4','clips','cuda-alexnet-polished.mp4'),
 'seal':('seal-paper-vids','seal-paper-subject-first-local.mp4','clips','seal-paper-polished.mp4')}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def audio_sha(path):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])).hexdigest()


def assemble(identity):
    project_name,baseline_name,clip_folder,output_name=ENTRIES[identity];root=REPO/'projects'/project_name
    baseline=root/'artifacts/videos'/baseline_name;story=json.loads((root/'story.json').read_text(encoding='utf-8-sig'))
    clips=[root/'artifacts/videos'/clip_folder/f'{i+1:02d}-{s["id"]}.mp4' for i,s in enumerate(story['scenes'])]
    expected=int(next(s for s in probe(baseline)['streams'] if s['codec_type']=='video')['nb_frames'])
    frames=[int(next(s for s in probe(p)['streams'] if s['codec_type']=='video')['nb_frames']) for p in clips]
    for scene,n in zip(story['scenes'],frames,strict=True):
        if n!=round(scene.get('clipSeconds',scene.get('duration'))*30):raise ValueError('Stale scene frame budget: '+scene['id'])
    delta=expected-sum(frames)
    if not 0<=delta<=3:raise ValueError('An approved timeline changed; investigate before assembling.')
    folder=PROJECT/'artifacts/assembly'/identity;folder.mkdir(parents=True,exist_ok=True)
    inputs=hashlib.sha256(json.dumps({'voice':sha(baseline),'clips':[sha(p) for p in clips],'expected':expected,'tool':sha(Path(__file__))},sort_keys=True).encode()).hexdigest()
    output=root/'artifacts/videos'/output_name;receipt=folder/'receipt.json'
    if receipt.is_file() and output.is_file():
        old=json.loads(receipt.read_text(encoding='utf-8'))
        if old['inputsSha256']==inputs and old['videoSha256']==sha(output):print(json.dumps({'id':identity,'reused':True,'video':str(output)}));return
    if delta:
        held=folder/'final-hold.mp4'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(clips[-1]),'-vf','tpad=stop_mode=clone:stop_duration=0.25','-frames:v',str(frames[-1]+delta),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(held)],check=True)
        clips[-1]=held
    listing=folder/'clips.txt';listing.write_text(''.join("file '"+p.resolve().as_posix()+"'\n" for p in clips),encoding='utf-8')
    temporary=output.with_name(output.stem+'.partial.mp4')
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-i',str(baseline),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(temporary)],check=True)
    actual=probe(temporary);stream=next(s for s in actual['streams'] if s['codec_type']=='video')
    if int(stream['nb_frames'])!=expected:raise ValueError('Final frame count changed.')
    approved_audio=audio_sha(baseline)
    if audio_sha(temporary)!=approved_audio:raise ValueError('Approved compressed narration changed.')
    temporary.replace(output)
    report={'ok':True,'nativeGoogleVidsExport':False,'renderer':'D3/native Mermaid or pinned paper captures + isolated Playwright + FFmpeg','voice':'Approved actual Google Vids voice, unchanged AAC payload','approvedAudioSha256':approved_audio,'audioBitstreamPreserved':True,'baseline':str(baseline),'inputsSha256':inputs,'video':str(output),'videoSha256':sha(output),'frames':expected,'extraFinalHoldFrames':delta,'duration':float(stream['duration']),'sceneCount':len(clips)}
    receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--id',choices=list(ENTRIES),action='append');args=parser.parse_args()
    for identity in args.id or ENTRIES:assemble(identity)
