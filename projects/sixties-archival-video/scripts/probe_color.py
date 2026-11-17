#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure authored colors through actual encoded-video range and matrix conversion."""
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent


def main():
    story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'))
    row=json.loads((ROOT/'artifacts/videos/clips/02-fashion.json').read_text(encoding='utf-8'))
    source=ROOT/row['rangeNormalization']['input']
    scene=story['scenes'][1];t=scene['cues'][1]['at']+.15
    policies={'declared':'format=rgb24','limited-601':'setparams=range=limited:colorspace=bt470bg,scale=in_range=tv:in_color_matrix=bt601:out_range=pc,format=rgb24','full-601':'setparams=range=full:colorspace=bt470bg,scale=in_range=pc:in_color_matrix=bt601:out_range=pc,format=rgb24','limited-709':'setparams=range=limited:colorspace=bt709,scale=in_range=tv:in_color_matrix=bt709:out_range=pc,format=rgb24'}
    result={}
    for name,vf in policies.items():
        data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(source),'-frames:v','1','-vf',vf,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        def pixel(x,y):return list(data[(y*1920+x)*3:(y*1920+x)*3+3])
        result[name]={'white':pixel(1000,50),'red':pixel(1280,280),'gray':pixel(1600,520)}
    out=ROOT/'artifacts/reviews/color-probe.json';out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':main()
