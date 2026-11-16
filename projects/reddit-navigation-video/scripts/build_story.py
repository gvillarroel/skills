#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["edge-tts>=7,<8"]
# ///
"""Create the Spanish Reddit walkthrough from reviewed real browser screenshots."""
import asyncio
import hashlib
import html
import json
import math
import re
import subprocess
import unicodedata
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT.parents[1] / 'skills/line-world-video'
VOICE = 'es-CL-CatalinaNeural'
RATE = '-6%'
LEAD = .65


def target(box, port): return {'box': box, 'port': port}


def request():
    # Spanish text is the requested narration/source fixture; all coordinates
    # refer to inspected original screenshot pixels, never reconstructed UI.
    return [
        {'id': 'search', 'capture': '01-search.jpg', 'region': [320, 0, 1160, 420], 'scale': 1.95,
         'script': 'Busca un tema en la barra superior. En este ejemplo usamos learnpython. Después elige Communities para ver comunidades, en lugar de publicaciones.',
         'targets': {'search': target([422, 8, 554, 42], [444, 66]), 'communities': target([462, 70, 111, 41], [517, 124])},
         'phrases': [('search', 'barra superior'), ('communities', 'Communities')]},
        {'id': 'choose-community', 'capture': '02-communities.jpg', 'region': [330, 65, 1390, 450], 'scale': 1.6,
         'script': 'Abre la comunidad learnpython. Su descripción te permite comprobar si el tema coincide con lo que buscas.',
         'targets': {'community': target([410, 131, 270, 31], [450, 117]), 'description': target([411, 168, 650, 20], [1082, 177])},
         'phrases': [('community', 'comunidad'), ('description', 'descripción')]},
        {'id': 'follow', 'capture': '03-community.jpg', 'region': [330, 62, 1390, 410], 'scale': 1.6,
         'script': 'Ya estás dentro de la comunidad. El botón Join te permite seguirla cuando hayas iniciado sesión.',
         'targets': {'community': target([445, 144, 420, 37], [650, 196]), 'join': target([1320, 139, 55, 40], [1347, 123])},
         'phrases': [('community', 'dentro'), ('join', 'Join')]},
        {'id': 'rules', 'capture': '04-rules.jpg', 'region': [1074, 344, 1384, 760], 'scale': 2,
         'script': 'Antes de participar, revisa las reglas. Aquí se pide ser amable y que las publicaciones sean preguntas para aprender Python. También puedes consultar las preguntas frecuentes.',
         'targets': {'rules': target([1090, 550, 275, 66], [1078, 588]), 'questions': target([1136, 623, 210, 64], [1078, 654]), 'faq': target([1091, 490, 280, 33], [1078, 506])},
         'phrases': [('rules', 'reglas'), ('questions', 'publicaciones'), ('faq', 'preguntas frecuentes')]},
        {'id': 'read-thread', 'capture': '05-thread.jpg', 'region': [320, 63, 1060, 475], 'scale': 2,
         'script': 'Abre una publicación y lee el contexto completo. Este hilo semanal reúne preguntas pequeñas. Revisa sus indicaciones antes de responder.',
         'targets': {'title': target([334, 126, 705, 32], [315, 142]), 'context': target([334, 166, 705, 91], [315, 213]), 'instructions': target([334, 311, 710, 143], [315, 382])},
         'phrases': [('title', 'publicación'), ('context', 'hilo semanal'), ('instructions', 'indicaciones')]},
        {'id': 'vote-and-reply', 'capture': '11-reply.jpg', 'region': [320, 238, 1059, 645], 'scale': 2,
         'script': 'La flecha hacia arriba sirve para votar a favor de una aportación útil. Reply responde a un comentario concreto, manteniendo el hilo de la conversación.',
         'targets': {'upvote': target([371, 370, 32, 33], [387, 420]), 'reply': target([439, 370, 77, 33], [478, 420])},
         'phrases': [('upvote', 'flecha'), ('reply', 'Reply')]},
        {'id': 'new-comment', 'capture': '06-comments.jpg', 'region': [306, 100, 1065, 645], 'scale': 2,
         'script': 'Para añadir un comentario nuevo a la publicación, utiliza Join the conversation.',
         'targets': {'comment': target([335, 131, 718, 43], [318, 152])},
         'phrases': [('comment', 'comentario nuevo')]},
        {'id': 'account', 'capture': '13-login.jpg', 'region': [448, 31, 978, 744], 'scale': 1.85,
         'script': 'Reddit solicita una cuenta para participar. Si ya tienes una, inicia sesión con Log In. Si eres nuevo, completa el registro antes de publicar.',
         'targets': {'account': target([662, 109, 101, 32], [644, 125]), 'login': target([529, 669, 369, 45], [511, 691]), 'signup': target([628, 620, 54, 24], [701, 632])},
         'phrases': [('account', 'cuenta'), ('login', 'Log In'), ('signup', 'registro')]},
        {'id': 'create-post', 'capture': '03-community.jpg', 'region': [330, 62, 1390, 410], 'scale': 1.6,
         'script': 'Para iniciar tu propio tema, vuelve a la comunidad y utiliza Create Post. Describe tu pregunta, explica qué has intentado y añade el error o un ejemplo breve. Revisa las reglas antes de enviarla.',
         'targets': {'post': target([1188, 139, 135, 40], [1255, 123])},
         'phrases': [('post', 'Create Post')]}
    ]


def normalize(text):
    text = ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))
    return re.findall(r'[a-z0-9]+', text)


async def audio(scene):
    folder = ROOT / 'artifacts/audio'; folder.mkdir(parents=True, exist_ok=True)
    file = folder / (scene['id'] + '.mp3'); metadata = file.with_suffix('.json')
    key = hashlib.sha256(json.dumps([scene['script'], VOICE, RATE], ensure_ascii=False).encode()).hexdigest()
    if metadata.exists() and file.exists():
        old = json.loads(metadata.read_text(encoding='utf-8'))
        if old['key'] == key and old['sha256'] == hashlib.sha256(file.read_bytes()).hexdigest(): return old
    stream = edge_tts.Communicate(scene['script'], VOICE, rate=RATE, boundary='WordBoundary')
    words = []; chunks = []
    async for part in stream.stream():
        if part['type'] == 'audio': chunks.append(part['data'])
        elif part['type'] == 'WordBoundary': words.append({'text': html.unescape(part['text']), 'at': part['offset'] / 1e7, 'duration': part['duration'] / 1e7})
    file.write_bytes(b''.join(chunks))
    duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(file)], text=True))
    result = {'key': key, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'duration': duration, 'words': words,
              'provider': 'Microsoft Edge speech via edge-tts', 'voice': VOICE, 'rate': RATE, 'nativeGoogleVids': False}
    metadata.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


async def main():
    scenes = request()
    draft = ROOT / 'artifacts/data/narration-draft.json'; draft.parent.mkdir(parents=True, exist_ok=True); draft.write_text(json.dumps({'scenes': scenes}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    review = ROOT / 'artifacts/reviews/narration.json'; review.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['uv', 'run', '--script', str(SKILL / 'scripts/narration_review.py'), '--story', str(draft), '--output', str(review)], check=True)
    for scene in scenes:
        observed = await audio(scene)
        tokens = [(token, word['at']) for word in observed['words'] for token in normalize(word['text'])]
        cues = []
        for target_id, phrase in scene.pop('phrases'):
            query = normalize(phrase)
            matches = [i for i in range(len(tokens) - len(query) + 1) if [s[0] for s in tokens[i:i+len(query)]] == query]
            if not matches: raise ValueError('No observed word boundary for ' + scene['id'] + ': ' + phrase)
            cues.append({'target': target_id, 'at': round(LEAD + tokens[matches[0]][1], 4), 'phrase': phrase})
        scene['cues'] = cues
        scene['audio'] = 'artifacts/audio/' + scene['id'] + '.mp3'
        scene['audioLead'] = LEAD
        scene['voiceSeconds'] = observed['duration']
        scene['duration'] = math.ceil((LEAD + observed['duration'] + .65) * 30) / 30
        scene['capture'] = 'artifacts/screenshots/light/' + scene['capture']
        print(json.dumps({'scene': scene['id'], 'voiceSeconds': observed['duration'], 'duration': scene['duration'], 'cues': cues}), flush=True)
    session = json.loads((ROOT / 'capture-session.json').read_text(encoding='utf-8'))
    story = {'fps': 30, 'source': session, 'voice': {'provider': 'Microsoft Edge speech via edge-tts', 'voice': VOICE, 'nativeGoogleVids': False}, 'scenes': scenes}
    (ROOT / 'story.json').write_text(json.dumps(story, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'scenes': len(scenes), 'duration': sum(s['duration'] for s in scenes), 'story': str(ROOT / 'story.json')}))


if __name__ == '__main__': asyncio.run(main())
