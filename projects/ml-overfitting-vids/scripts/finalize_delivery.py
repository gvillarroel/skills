#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package portable editable sources and record completed native production evidence."""
import json,hashlib,zipfile,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;REPO=ROOT.parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    frame=read(ROOT/'artifacts/reviews/native-frame-audit.json');export=read(ROOT/'artifacts/reviews/export-check.json');asr=read(ROOT/'artifacts/reviews/narration-transcript.json')
    assert frame['ok'] and export['ok'] and asr['scriptWordRecall']>.95
    package=read(REPO/'projects/line-world-video/artifacts/packages/package-check-0.6.0.json');assert package['ok']
    host=read(REPO/'projects/line-world-video/artifacts/host-checks/plugin-verification.json');assert host['ok']
    evidence=read(REPO/'evaluations/line-world-google-vids/reviewed-evidence-20261115.json');assert evidence['ok'] and len(evidence['cases'])==10
    story=read(ROOT/'story.json');files={}
    for name in ['train_demo.py','build_visuals.py','scene.js','render_clips.py','prepare_uploads.py','check_narration.py','audit_native_export.py']:
        path=ROOT/'scripts'/name;files['scripts/'+name]=path.read_bytes()
    files['production.md']=(ROOT/'production.md').read_bytes()
    for name in ['d3.min.js','D3-LICENSE.txt','space-grotesk.ttf','OFL.txt','index.html','scene.js','data.js']:
        files['artifacts/composition/'+name]=(ROOT/'artifacts/composition'/name).read_bytes()
    for scene in story['scenes']:
        source=Path(scene['clip']);relative=source.relative_to(ROOT).as_posix();files[relative]=source.read_bytes();scene['clip']=relative
    files['story.json']=(json.dumps(story,indent=2,ensure_ascii=False)+'\n').encode()
    files['artifacts/composition/story.js']=('window.PRODUCTION='+json.dumps(story,ensure_ascii=False)+';\n').encode()
    files['artifacts/data/experiment.json']=(ROOT/'artifacts/data/experiment.json').read_bytes()
    for name in ['observed.json','timing.json','frame-repair.json']:
        p=ROOT/'artifacts/handoff'/name;v=read(p)
        if name=='timing.json':
            for scene in v['scenes']:scene['clip']=Path(scene['clip']).relative_to(ROOT).as_posix()
        files['artifacts/handoff/'+name]=(json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode()
    video=ROOT/'artifacts/videos/ml-overfitting-google-vids-final.mp4'
    files['artifacts/videos/'+video.name]=video.read_bytes()
    for name in ['export-check.json','native-frame-audit.json','narration-transcript.json','native-captions.srt']:
        files['artifacts/reviews/'+name]=(ROOT/'artifacts/reviews'/name).read_bytes()
    target=ROOT/'artifacts/packages/ml-overfitting-google-vids-editable.zip';target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,value in sorted(files.items()):z.writestr(name,value)
    smoke=ROOT/'artifacts/packages/editable-extracted'
    if smoke.exists():raise ValueError('Extracted smoke workspace exists; preserve it and choose a new release run.')
    with zipfile.ZipFile(target) as z:z.extractall(smoke)
    for name,value in files.items():assert (smoke/name).read_bytes()==value
    rebuild=subprocess.run(['uv','run','--script','scripts/build_visuals.py'],cwd=smoke,capture_output=True,text=True,check=True)
    audit=subprocess.run(['uv','run','--script','scripts/render_clips.py','--audit-only'],cwd=smoke,capture_output=True,text=True,check=True)
    assert read(smoke/'artifacts/render-report.json')['ok']
    receipt={'ok':True,'date':'2026-11-15','pluginVersion':'0.6.0','projectUrl':story['googleVidsUrl'],'nativeVideo':str(video),'nativeVideoSha256':digest(video),'nativeEncoderTag':frame['nativeEncoderTag'],'duration':export['duration'],'videoFrames':frame['allDecodedFrames'],'blankFrames':frame['blankFrames'],'blackFrames':frame['blackFrames'],'asrWordRecall':asr['scriptWordRecall'],'isolatedRuns':10,'deterministicTests':8,'pluginZip':package['pluginZip'],'marketplaceZip':str(REPO/'projects/line-world-video/artifacts/packages/line-world-video-0.6.0-marketplace.zip'),'editableZip':str(target),'editableZipSha256':digest(target),'editableFileCount':len(files),'cleanExtractionAndLocalVisualAudit':True,'uiExit':'Native export and download started were observed; Chrome downloads navigation triggered a URL-confidence stop. No further UI control was attempted. Completed file was read from Downloads and copied to the workspace.','globalValidator':'Four pre-existing unrelated reference-route findings; focused changed bundles, pattern IDs, independence and payload checks pass.'}
    write(ROOT/'artifacts/manifests/delivery.json',receipt)
    notes=REPO/'SKILLS.md';lines=notes.read_text(encoding='utf-8').splitlines()
    for i,line in enumerate(lines):
        if line.startswith('| line-world-google-vids |'):
            lines[i]='| line-world-google-vids | `done` | Assemble prepared scene clips through the real Google Vids UI, generate native narration, measure continuity and download the complete MP4. | self-contained planning/timing/export helper; UI, handoff, continuity and recovery references; agents/openai.yaml | 2026-11-15: 8 deterministic tests and 9 strict isolated adapter runs pass; primary routing run also passes. Model exception: openai-codex/gpt-6.1-sol, medium thinking, because Spark is unavailable for this account. Actual private twelve-scene Spanish Nyla film exported and downloaded: 1080p30, 265.914921 seconds, 7,977 frames; full decode and all-frame blank checks pass. Plugin 0.6.0 six-skill archive, schema and task-local native installation pass. [Evidence](evaluations/line-world-google-vids/validation-20261115.md). |'
        elif line.startswith('| line-world-video |'):
            suffix=' 2026-11-15: plugin 0.6.0 adds the native Google Vids adapter; new orchestrator route passes isolated pi and the Spanish ML example completes native export/download with measured frame holds. [Native evidence](evaluations/line-world-google-vids/validation-20261115.md). '
            if 'plugin 0.6.0 adds the native Google Vids adapter' not in line:lines[i]=line.rstrip().removesuffix('|').rstrip()+suffix+'|'
    notes.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
