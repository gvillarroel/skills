#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Consolidate observed release evidence without copying bulky generated reports."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parents[1]
SKIP={'node_modules','__pycache__','.venv','.cache','dist','output'}


def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def payload(root):
    return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file() and not any(s in SKIP for s in p.relative_to(root).parts) and p.relative_to(root).parts[:2]!=('assets','examples') and p.suffix not in ['.pyc','.pyo']}


def main():
    summary=read(ROOT/'artifacts/current/summary.json');assert summary['deliveryReady']
    current=[r for r in summary['videos'] if r['role']=='current'];assert len(current)==8
    canonical=payload(REPO/'skills/line-world-video');runs=[]
    for folder in sorted((REPO/'evaluations/runs').glob('20261116-line-world-0260-*/')):
        result=read(folder/'evaluation-result.json');integrity=read(folder/'skill-integrity-check.json')
        matches=payload(folder/'workspace/skills/line-world-video')==canonical
        runs.append({'id':folder.name,'passed':result['passed'],'gates':result['gates'],'durationSeconds':result['durationSeconds'],'matchesFinalRuntimePayload':matches})
    final=[r for r in runs if '-release-' in r['id']];assert len(final)==2 and all(r['passed'] and r['matchesFinalRuntimePayload'] for r in final)
    suites={}
    for name,file in {'focus-motion':'test-motion-release.log','scene-effects':'test-effects-final.log','collection':'test-collection-release.log','atlas-reading':'test-atlas-transparent.log','single-film-review':'test-review-video-final.log','photo-focus':'test-photo.log','paper-motion':'test-paper-motion.log','paper-video':'test-paper-video-final.log'}.items():
        text=(ROOT/'artifacts'/file).read_text(encoding='utf-8');match=re.search(r'Ran (\d+) tests?',text);assert match and re.search(r'^OK$',text,re.M),file
        suites[name]=int(match.group(1))
    native=read(REPO/'projects/line-world-video/artifacts/host-checks/openai-0.26.0/verification.json');assert native['ok']
    playback=read(ROOT/'artifacts/playback.json');assert playback['ok'] and len(playback['videos'])==8
    movies=[]
    for row in current:
        item={k:row[k] for k in ['id','videoSha256','sourceSha256','sourceKind','machineOK','manualReview','deliveryReady','decodedFrames','insufficientContentFrames','guideEvents','advisories','provenance']}
        item.update(sceneCount=len(row['scenes']),videoPath=Path(row['video']).relative_to(REPO).as_posix())
        item['effectChecks']=[{'check':e['check'],'ok':e['ok']} for e in row.get('effectAudits',[])]
        movies.append(item)
    audio=[read(ROOT/'artifacts/assembly'/name/'receipt.json') for name in ['ml','cuda','seal']]
    report={'date':'2026-11-16','pluginVersion':'0.26.0','scope':'Eight current local deliveries and 29 historical/voice/utility references. Per-scene actual encoded visual observations plus separate source, decode/content and effect checks. Historical entries are not approved current movies.','currentVideos':movies,'filesReviewed':len(summary['videos']),'uniqueMovieDigests':len({r['videoSha256'] for r in summary['videos']}),'currentFrames':sum(r['decodedFrames'] for r in current),'allFileFrames':summary['decodedFrames'],'observedScenes':sum(len(r['scenes']) for r in current),'historicalFindings':[{'id':r['id'],'insufficientContentFrames':r['insufficientContentFrames']} for r in summary['videos'] if r['role']=='reference' and not r['machineOK']],'unitSuites':suites,'unitTests':sum(suites.values()),'model':'openai-codex/gpt-6.1-sol, medium; recorded Spark account exception','isolatedRuns':runs,'finalRuntimeFiles':len(canonical),'finalStrictPasses':len(final),'nativeOpenAIPackage':{'ok':native['ok'],'report':str(Path('projects/line-world-video/artifacts/host-checks/openai-0.26.0/verification.json')),'zipSha256':sha(REPO/'projects/line-world-video/artifacts/packages/line-world-video-0.26.0.zip')},'approvedAudio':[{'id':name,'audioBitstreamPreserved':r['audioBitstreamPreserved'],'aacSha256':r['approvedAudioSha256'],'extraFinalHoldFrames':r['extraFinalHoldFrames']} for name,r in zip(['ml','cuda','seal'],audio,strict=True)],'playback':{'ok':True,'movies':8,'actualMutedPlayback':True,'scope':playback['scope']},'repeatedReview':{'newGalleryFrames':sum((r.get('encodedCache') or {}).get('capturedFrames',0) for r in summary['videos']),'reusedGalleryFrames':sum((r.get('encodedCache') or {}).get('reusedFrames',0) for r in summary['videos']),'contentCacheReused':sum(r.get('contentReused') is True for r in summary['videos'])},'limitations':['Primary skill remains validating for previously recorded broader generation limits.','No new native Google Vids or HyperFrames render/export is claimed; upload permission remains unresolved.','Archive scan is not a new manual listening/visual pass over every historical scene.','Review reuse is qualified with separate composition and review directories.','Root global validation retains four pre-existing unrelated semantic reference-route findings; clean publication checks are recorded separately.']}
    out=REPO/'evaluations/line-world-video/collection-review-20261116.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['filesReviewed','uniqueMovieDigests','observedScenes','currentFrames','allFileFrames','unitTests','finalStrictPasses','finalRuntimeFiles','repeatedReview']}))


if __name__=='__main__':main()
