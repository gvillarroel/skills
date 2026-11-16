#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "pymupdf>=1.26,<2"]
# ///
"""Extract reviewed paper photographs and declare exact documentary treatments."""
import hashlib
import io
import json
from pathlib import Path
import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'artifacts/sources/hardware'
PAPER = 'https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf'


def base(identity, label, file, page, evidence, scope, rights, treatments, **more):
    return {'id': identity, 'label': label, 'sourceFile': str(file.relative_to(ROOT)).replace('\\', '/'), 'sourcePage': page,
            'identityEvidence': evidence, 'scope': scope, 'rights': rights, 'reviewed': True,
            'sourceSha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'width': 640, 'treatments': treatments, **more}


def main():
    entries = []
    variants = [{'id': 'gray', 'mode': 'grayscale'}, {'id': 'edges', 'mode': 'edges'}, {'id': 'pixel', 'mode': 'pixel', 'cell': 4, 'levels': 4}, {'id': 'one-bit', 'mode': 'one-bit', 'ink': '#696969', 'cell': 2}]
    entries.append(base('gtx580', 'EVGA GeForce GTX 580 3 GB', SOURCE / 'gtx580-card.jpg',
        'https://www.newegg.com/evga-03g-p3-1584-ar-geforce-gtx-580-3gb-graphics-card-single-fan/p/N82E16814130655',
        'Reviewed product photograph shows GTX 580; source product record identifies 03G-P3-1584-AR with 3 GB GDDR5.',
        'Photograph of the model/memory variant, not a claim that this exact EVGA specimen was used by the AlexNet authors.',
        {'creator': 'Product photograph distributed by EVGA/Newegg; individual photographer not credited', 'license': 'No open license asserted; source product-photograph rights retained', 'credit': 'EVGA GeForce GTX 580 3 GB product photograph, Newegg item 14-130-655, view 04'}, variants,
        model={'expected': 'GeForce GTX 580', 'observed': 'GeForce GTX 580'}, variant={'expected': '3 GB', 'observed': '3 GB'}))
    entries.append(base('cpu', 'Intel Core i7-920 CPU', SOURCE / 'cpu-core-i7.jpg',
        'https://commons.wikimedia.org/wiki/File:Nehalem_Corei7-920_DSCF1581_(15990812314).jpg',
        'Reviewed source and visible package marking identify Intel Core i7-920.',
        'Illustrates the CPU role in a heterogeneous system; the historical experiment host CPU is not specified here.',
        {'creator': 'Fritzchens Fritz', 'license': 'CC0 1.0 Universal', 'licenseUrl': 'https://creativecommons.org/publicdomain/zero/1.0/', 'credit': 'Fritzchens Fritz, Nehalem Corei7-920 DSCF1581, 2009, CC0; via Wikimedia Commons'}, variants,
        crop=[650, 275, 2170, 1880], subjectPolygon=[[693, 317], [2124, 322], [2119, 1849], [680, 1851]]))
    document = pymupdf.open(SOURCE / 'alexnet-paper.pdf')
    paper_sha = hashlib.sha256((SOURCE / 'alexnet-paper.pdf').read_bytes()).hexdigest()
    page = document[7]
    images = page.get_images(full=True)
    right_info = next(x for x in images if x[2:4] == (484, 346))
    left_info = next(x for x in images if x[2:4] == (820, 670))
    right = Image.open(io.BytesIO(document.extract_image(right_info[0])['image'])).convert('RGB')
    left = Image.open(io.BytesIO(document.extract_image(left_info[0])['image'])).convert('RGB')
    rights = {'creator': 'Alex Krizhevsky, Ilya Sutskever and Geoffrey Hinton; underlying ImageNet image rights retained',
              'license': 'Original paper/underlying photographs; no Creative Commons license asserted',
              'credit': 'ImageNet photographs reproduced in Figure 4, ImageNet Classification with Deep Convolutional Neural Networks, NeurIPS 2012, page 8'}
    folder = SOURCE / 'paper-photos'; folder.mkdir(exist_ok=True)
    for row, category in enumerate(['flower', 'elephant', 'sailboat', 'pumpkin', 'dog']):
        for col in range(1, 7):
            bounds = [round(col * 484 / 7), round(row * 346 / 5), round((col + 1) * 484 / 7), round((row + 1) * 346 / 5)]
            tile = right.crop(tuple(bounds))
            file = folder / f'{category}-{col}.png'; tile.save(file)
            entries.append(base(f'imagenet-{category}-{col}', 'Published ImageNet training example: ' + category, file, PAPER + '#page=8',
                'Figure 4 right panel: one of the six training-image neighbours in this row; first test-image column excluded.',
                'Published ILSVRC-2010 training example; illustrates ImageNet variety without asserting a specific 2012 training-file inventory.', rights, [{'id': 'gray', 'mode': 'grayscale'}], width=112,
                derivedFrom={'file': 'artifacts/sources/hardware/alexnet-paper.pdf', 'sha256': paper_sha, 'page': 8, 'figure': '4 right', 'imageXref': right_info[0], 'imageDimensions': [484, 346], 'crop': bounds}))
    leopard = folder / 'leopard.png'; left.crop((615, 0, 820, 205)).save(leopard)
    for identity, crop, flip in [('leopard', None, False), ('leopard-flip', None, True), ('leopard-crop', [20, 20, 185, 185], False), ('leopard-crop-flip', [10, 10, 190, 190], True)]:
        extra = {'flip': flip, 'derivedFrom': {'file': 'artifacts/sources/hardware/alexnet-paper.pdf', 'sha256': paper_sha, 'page': 8, 'figure': '4 left', 'imageXref': left_info[0], 'imageDimensions': [820, 670], 'crop': [615, 0, 820, 205]}}
        if crop: extra['crop'] = crop
        treatments = [{'id': 'gray', 'mode': 'grayscale'}]
        if identity == 'leopard': treatments.append({'id': 'pixel', 'mode': 'pixel', 'cell': 4, 'levels': 4})
        entries.append(base(identity, 'Leopard photograph from the AlexNet paper', leopard, PAPER + '#page=8',
            'Figure 4 left panel explicitly labels the upper-right test photograph as leopard.',
            'Published test photograph; cropped/mirrored versions illustrate augmentation, not additional historical training examples.', rights, treatments, width=204, **extra))
    (ROOT / 'object-media.json').write_text(json.dumps({'assets': entries}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'documentaryObjects': 2, 'publishedTrainingPhotos': 30, 'photoExamples': 4}))


if __name__ == '__main__': main()
