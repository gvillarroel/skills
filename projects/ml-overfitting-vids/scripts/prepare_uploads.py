#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare frame-budget clips from the current story, preserving native observations."""
import json,subprocess,argparse,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--through',type=int,default=12);a=p.parse_args()
    story=json.loads((ROOT/'story.json').read_text(encoding='utf-8-sig'))
    for i,s in enumerate(story['scenes'][:a.through]):
        source=ROOT/f'artifacts/videos/clips/{i+1:02d}-{s["id"]}.mp4';target=Path(s['clip'])
        if not target.is_absolute():target=ROOT/target
        if not target.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Upload target must remain inside this project.')
        frames=math.ceil(s['clipSeconds']*story['fps']-1e-8);duration=frames/story['fps']
        target.parent.mkdir(parents=True,exist_ok=True)
        check=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(source)],text=True));available=float(check['format']['duration'])
        if available<s['essentialAnimationSeconds']:raise ValueError('Source clip cuts essential motion: '+s['id'])
        pad=max(0,duration-available)+.1
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-vf',f'tpad=stop_mode=clone:stop_duration={pad}','-frames:v',str(frames),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
        print(json.dumps({'id':s['id'],'duration':duration,'target':str(target)}),flush=True)
if __name__=='__main__':main()
