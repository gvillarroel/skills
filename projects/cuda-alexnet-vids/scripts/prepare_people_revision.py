#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare sourced portrait introductions and retain the prior production."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKUP = ROOT/'artifacts/revisions/people-context-0190'


def main():
    BACKUP.mkdir(parents=True, exist_ok=True)
    for file in ['story.json', 'scripts/scene.js', 'artifacts/data/cues.json',
                 'artifacts/data/final-native-observed.json', 'artifacts/data/transcript.json',
                 'artifacts/videos/cuda-alexnet-google-vids-final.mp4']:
        source = ROOT/file; target = BACKUP/file
        if source.is_file() and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
    story = json.loads((ROOT/'story.json').read_text(encoding='utf-8'))
    scripts = {
        'cuda-platform': 'La historia de CUDA también tiene protagonistas. Ian Buck desarrolló Brook con su equipo en Stanford y después lideró el software de CUDA en NVIDIA. La plataforma se presentó en 2006 y abrió su beta pública en 2007. Permitió usar las GPU para cálculos generales. La CPU mantiene el control y la GPU ejecuta muchas operaciones en paralelo. Ese puente facilitó entrenar redes más grandes.',
        'imagenet-scale': 'Para reconocer imágenes también hacían falta datos. Fei-Fei Li impulsó ImageNet, y Jia Deng fue el primer autor de su artículo de 2009. Con un equipo más amplio, construyeron una gran base de imágenes etiquetadas. El concurso permitió comparar los modelos con una prueba común. AlexNet se entrenó con alrededor de un millón doscientas mil imágenes y mil categorías. Esta escala permitió medir el avance con muchos ejemplos.',
        'alexnet-model': 'En 2012, tres investigadores de la Universidad de Toronto presentaron AlexNet: Alex Krizhevsky, Ilya Sutskever y Geoffrey Hinton. Son los coautores de una red profunda entrenada eficientemente en GPU. Su arquitectura tenía cinco capas convolucionales y tres totalmente conectadas. Los píxeles atravesaban etapas que aprendían características hasta producir categorías. El esquema simplifica las ocho capas con pesos.'
    }
    def person(id, name, caption, spoken_role, source):
        return {'id': id, 'name': name, 'caption': caption, 'narrationRole': spoken_role,
                'target': 'person-'+id, 'sources': [source]}
    people = {
        'cuda-platform': [person('ian-buck', 'Ian Buck', ['Lideró el software de CUDA', 'NVIDIA · antes, Brook en Stanford'], 'lideró el software de CUDA', 'https://developer.nvidia.com/blog/inside-the-programming-evolution-of-gpu-computing/')],
        'imagenet-scale': [
            person('fei-fei-li', 'Fei-Fei Li', ['Impulsó el proyecto ImageNet'], 'impulsó ImageNet', 'https://hai.stanford.edu/people/fei-fei-li'),
            person('jia-deng', 'Jia Deng', ['Primer autor · ImageNet 2009'], 'primer autor', 'https://www.image-net.org/static_files/papers/imagenet_cvpr09.pdf')],
        'alexnet-model': [person(id, name, ['Coautor de AlexNet · Toronto'], 'coautores de una red profunda', 'https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf') for id, name in [('alex-krizhevsky', 'Alex Krizhevsky'), ('ilya-sutskever', 'Ilya Sutskever'), ('geoffrey-hinton', 'Geoffrey Hinton')]]
    }
    cues = {
        'cuda-platform': [('person-ian-buck','Ian Buck'),('cuda-2006','2006'),('cuda-2007','2007'),('cpu','CPU'),('gpu','GPU ejecuta'),('parallel','en paralelo')],
        'imagenet-scale': [('person-fei-fei-li','Fei-Fei Li'),('person-jia-deng','Jia Deng'),('imagenet-2009','2009'),('labels','imágenes etiquetadas'),('challenge','concurso'),('images-count','un millón doscientas mil'),('classes-count','mil categorías')],
        'alexnet-model': [('person-alex-krizhevsky','Alex Krizhevsky'),('person-ilya-sutskever','Ilya Sutskever'),('person-geoffrey-hinton','Geoffrey Hinton'),('conv-layers','cinco capas'),('dense-layers','tres totalmente'),('pixels','píxeles'),('categories','categorías')]
    }
    for scene in story['scenes']:
        if scene['id'] in scripts:
            scene['script'] = scripts[scene['id']]; scene['people'] = people[scene['id']]
            scene['cues'] = [{'target': target, 'phrase': phrase} for target, phrase in cues[scene['id']]]
    (ROOT/'story.json').write_text(json.dumps(story, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    (BACKUP/'scripts-to-generate.json').write_text(json.dumps(scripts, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'changedScenes': list(scripts), 'people': sum(map(len, people.values())), 'timing': 'Pending measured native narration; existing budgets are not claimed final.'}))


if __name__ == '__main__': main()
