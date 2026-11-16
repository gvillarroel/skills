#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["faster-whisper==1.2.1"]
# ///
"""Independently transcribe the downloaded native film; retain local evidence."""
import argparse,json,os,re,unicodedata,subprocess
import numpy as np
from difflib import SequenceMatcher
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
cache=ROOT/'artifacts/models';cache.mkdir(parents=True,exist_ok=True)
os.environ['HF_HOME']=str(cache/'huggingface');os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
from faster_whisper import WhisperModel

def norm(s):return re.findall(r'[a-z0-9]+',''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--prepare-model',action='store_true');p.add_argument('--video',type=Path);a=p.parse_args()
    model=WhisperModel('base',device='cpu',compute_type='int8',cpu_threads=8,download_root=str(cache))
    if a.prepare_model:print(json.dumps({'ok':True,'model':'base','cache':str(cache)}));return
    if not a.video:raise ValueError('Provide the actual downloaded native export.')
    pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(a.video),'-vn','-sn','-f','f32le','-acodec','pcm_f32le','-ac','1','-ar','16000','pipe:1'])
    audio=np.frombuffer(pcm,dtype=np.float32)
    segments,info=model.transcribe(audio,language='es',beam_size=5,word_timestamps=True,condition_on_previous_text=False)
    rows=[]
    for s in segments:
        rows.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in s.words or []]})
        print(json.dumps({'end':s.end,'text':s.text},ensure_ascii=False),flush=True)
    story=json.loads((ROOT/'story.json').read_text(encoding='utf-8-sig'));expected=norm(' '.join(s['script'] for s in story['scenes']));actual=norm(' '.join(s['text'] for s in rows));m=SequenceMatcher(None,expected,actual,autojunk=False)
    matched=sum(block.size for block in m.get_matching_blocks());report={'model':'faster-whisper base, CPU int8','language':info.language,'duration':info.duration,'expectedWords':len(expected),'recognizedWords':len(actual),'matchedWords':matched,'scriptWordRecall':matched/len(expected),'note':'ASR provides independent content/order evidence; recognition differences require review and do not prove an audio defect.','segments':rows}
    out=ROOT/'artifacts/reviews';out.mkdir(parents=True,exist_ok=True);(out/'narration-transcript.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='segments'},ensure_ascii=False))
if __name__=='__main__':main()
