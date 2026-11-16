#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a caption-free native stream copy after current export verification."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def run(args):return subprocess.check_output(args,text=True,encoding='utf-8').strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def stream(path,selector):return run(['ffmpeg','-v','error','-i',str(path),'-map',selector,'-c','copy','-f','hash','-hash','sha256','-'])
def main():
 native=ROOT/'artifacts/videos/ml-overfitting-google-vids-revised.mp4';clean=ROOT/'artifacts/videos/ml-overfitting-solid-final.mp4';check=json.loads((ROOT/'artifacts/revision/native-verification.json').read_text(encoding='utf-8'))
 if not check['ok'] or sha(native)!=check['sha256']:raise ValueError('Verify the actual current native export first.')
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(native),'-map','0:v:0','-map','0:a:0','-c','copy','-map_metadata','0','-movflags','+faststart',str(clean)],check=True)
 parity={key:{'native':stream(native,selector),'delivery':stream(clean,selector)} for key,selector in [('video','0:v:0'),('audio','0:a:0')]}
 report={'ok':all(x['native']==x['delivery'] for x in parity.values()),'nativeSha256':sha(native),'deliverySha256':sha(clean),'delivery':str(clean),'duration':check['duration'],'frames':check['decodedFrames'],'streams':parity,'voicePreservation':check['voicePreservation'],'operation':'Container stream copy omitting only the optional default subtitle stream; no audio or video re-encoding.'}
 (ROOT/'artifacts/revision/solid-delivery.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report));return 0 if report['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
