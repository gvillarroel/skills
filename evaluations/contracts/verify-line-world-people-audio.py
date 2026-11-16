#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify actual contributor names and roles in native-reference ASR words."""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path


def tokens(value):
    plain = ''.join(c for c in unicodedata.normalize('NFD', value.lower()) if unicodedata.category(c) != 'Mn')
    return re.findall('[a-z0-9]+', plain)


def matches(words, phrase):
    needle = tokens(phrase)
    return [i for i in range(len(words)-len(needle)+1) if needle and words[i:i+len(needle)] == needle]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['story','cues','transcript','timing','voice-report','reference','output']: p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args(); read = lambda file: json.loads(file.read_text(encoding='utf-8-sig'))
    story, cues, transcript, timing, report = map(read, [a.story,a.cues,a.transcript,a.timing,a.voice_report])
    digest = hashlib.sha256(a.reference.read_bytes()).hexdigest()
    hashes = digest == cues['sourceVideoSha256'] == report['voiceReferenceSha256']
    blocks = {b['id']:b for b in cues['scenes']}; starts = {}; cursor = 0
    for scene in timing['scenes']: starts[scene['id']] = (cursor,cursor+scene['sceneSeconds']); cursor += scene['sceneSeconds']
    windows = {w['id']: w for w in report['checks']['voiceWindows']}; observations = []
    for scene in story['scenes']:
        for person in scene.get('people', []):
            start,end = starts[scene['id']]
            words = [token for seg in transcript['segments'] for w in seg['words'] if start <= w['start'] < end for token in tokens(w['word'])]
            cue = next(c for c in blocks[scene['id']]['cues'] if c['target'] == person['target'])
            names = [person.get('spokenName',person['name']),*cue.get('alternatives',[])]
            name_found = any(matches(words,name) for name in names); role_found = bool(matches(words,person['narrationRole']))
            window = windows[scene['id']]; retained = window['correlation'] > .985 and abs(window['localOffsetSeconds']) < .1
            observations.append({'scene':scene['id'],'person':person['id'],'nameInActualAsr':name_found,'contributionInActualAsr':role_found,'finalVoiceMatchesReference':retained,'ok':hashes and name_found and role_found and retained})
    result = {'ok': bool(observations) and report['ok'] and all(o['ok'] for o in observations), 'referenceHashesMatch':hashes,'people':observations,'scope':'Actual native-reference ASR words and final/reference voice-window comparison. Spelling alternatives and word boundaries remain approximate.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':result['ok'],'people':len(observations),'failures':[x for x in observations if not x['ok']]}))
    return 0 if result['ok'] else 2


if __name__ == '__main__': raise SystemExit(main())
