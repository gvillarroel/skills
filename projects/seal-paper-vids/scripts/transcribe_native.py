#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["faster-whisper==1.2.1"]
# ///
"""Transcribe actual native audio with an existing local model and word evidence."""
import argparse,json,os,re,subprocess,unicodedata
from difflib import SequenceMatcher
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
os.environ['HF_HOME']=str(ROOT/'artifacts/tools/huggingface')
from faster_whisper import WhisperModel
def norm(s):return re.findall('[a-z0-9]+',''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--video',type=Path,required=True);p.add_argument('--model-dir',type=Path,required=True);a=p.parse_args()
 model=WhisperModel(str(a.model_dir.resolve()),device='cpu',compute_type='int8',cpu_threads=8)
 pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(a.video),'-vn','-sn','-f','f32le','-acodec','pcm_f32le','-ac','1','-ar','16000','pipe:1']);audio=np.frombuffer(pcm,dtype=np.float32)
 segments,info=model.transcribe(audio,language='es',beam_size=5,word_timestamps=True,condition_on_previous_text=False)
 result=[]
 for s in segments:
  result.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in s.words or []]});print(json.dumps({'end':s.end,'text':s.text},ensure_ascii=False),flush=True)
 story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'));expected=norm(' '.join(s['script'] for s in story['scenes']));actual=norm(' '.join(s['text'] for s in result));matched=sum(b.size for b in SequenceMatcher(None,expected,actual,autojunk=False).get_matching_blocks())
 report={'model':'faster-whisper base, CPU int8, reused local model','sourceVideo':str(a.video.resolve()),'duration':info.duration,'language':info.language,'expectedWords':len(expected),'recognizedWords':len(actual),'matchedWords':matched,'scriptWordRecall':matched/len(expected),'evidence':'Approximate independent ASR word boundaries from the actual native Google Vids export; review spelling and alignment.','segments':result}
 target=ROOT/'artifacts/data/transcript.json';target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({'output':str(target),'scriptWordRecall':report['scriptWordRecall']}))
if __name__=='__main__':main()
