#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2"]
# ///
"""Cache reviewed documentary photographs and bake restrained visual treatments."""
import argparse
import base64
import functools
import html
import io
import inspect
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from media_assets import digest, fetch, save

ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / 'assets/vendor/photo-onebit/stylize_svg.py'
MODES = {'photo', 'grayscale', 'edges', 'pixel', 'one-bit'}
INKS = {'#9e1b32', '#696969', '#8e8e8e', '#cfcfcf', '#333e48', '#000000'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def check(entry):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry.get('id', '')):
        raise ValueError('Use a stable lowercase asset ID.')
    if entry.get('reviewed') is not True:
        raise ValueError('Review the actual source image before preparing it.')
    for field in ['label', 'sourcePage', 'identityEvidence', 'scope']:
        if not entry.get(field): raise ValueError('Missing documentary field: ' + field)
    for field in ['creator', 'license', 'credit']:
        if not entry.get('rights', {}).get(field): raise ValueError('Missing rights field: ' + field)
    if not entry.get('sourceFile') and not entry.get('downloadUrl'):
        raise ValueError('Provide sourceFile or downloadUrl.')
    for field in ['model', 'variant']:
        if field in entry and (not entry[field].get('expected') or entry[field].get('expected') != entry[field].get('observed')):
            raise ValueError('Documented ' + field + ' does not match the requested identity. Use exact normalized identifiers; put supporting qualifiers in identityEvidence.')
    if not entry.get('treatments'): raise ValueError('Select at least one treatment.')
    ids = [s.get('id') for s in entry['treatments']]
    if len(ids) != len(set(ids)): raise ValueError('Treatment IDs must be unique.')
    for style in entry['treatments']:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', style.get('id', '')) or style.get('mode') not in MODES:
            raise ValueError('Use a stable treatment ID and supported mode.')
        if style.get('ink', '#696969').lower() not in INKS: raise ValueError('Select a canonical film ink.')
        if not isinstance(style.get('cell', 2), int) or not 1 <= style.get('cell', 2) <= 64: raise ValueError('Cell size must be 1-64 pixels.')
    if not isinstance(entry.get('width', 640), int) or not 32 <= entry.get('width', 640) <= 2048:
        raise ValueError('Prepared width must be 32-2048 pixels.')


def prepare_image(data, entry):
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert('RGBA')
    if image.width * image.height > 64000000: raise ValueError('Source dimensions exceed the preparation budget.')
    if entry.get('subjectPolygon'):
        points = entry['subjectPolygon']
        if len(points) < 3 or any(len(p) != 2 or not 0 <= p[0] <= image.width or not 0 <= p[1] <= image.height for p in points):
            raise ValueError('Subject polygon must stay inside the oriented source.')
        mask = Image.new('L', image.size, 0); ImageDraw.Draw(mask).polygon([tuple(p) for p in points], fill=255)
        image.putalpha(ImageChops.multiply(image.getchannel('A'), mask))
    if entry.get('crop'):
        box = entry['crop']
        if len(box) != 4 or any(not isinstance(v, int) for v in box) or not (0 <= box[0] < box[2] <= image.width and 0 <= box[1] < box[3] <= image.height):
            raise ValueError('Crop must fit the EXIF-oriented source without padding.')
        image = image.crop(tuple(box))
    if entry.get('flip'): image = ImageOps.mirror(image)
    white = Image.new('RGBA', image.size, 'white'); white.alpha_composite(image); image = white.convert('RGB')
    width = entry.get('width', 640)
    image = image.resize((width, max(1, round(image.height * width / image.width))), Image.Resampling.LANCZOS)
    if ImageChops.difference(image, Image.new('RGB', image.size, 'white')).getbbox() is None:
        raise ValueError('The prepared source contains no visible subject.')
    return image


def acquire(url, output):
    receipt = output.with_suffix(output.suffix + '.source.json')
    if output.is_file() and receipt.is_file():
        old = read(receipt)
        if old.get('downloadUrl') == url and old.get('sourceSha256') == digest(output.read_bytes()):
            return {**old, 'reused': True}
    if output.exists(): raise ValueError('Choose a new source path; existing bytes lack a matching acquisition receipt.')
    data = fetch(url)
    with Image.open(io.BytesIO(data)) as image:
        width, height, kind = image.width, image.height, image.format
        image.verify()
    output.parent.mkdir(parents=True, exist_ok=True); output.write_bytes(data)
    result = {'ok': True, 'downloadUrl': url, 'file': str(output), 'sourceSha256': digest(data), 'format': kind,
              'width': width, 'height': height, 'identityReview': 'pending', 'reused': False}
    save(receipt, result); return result


def treatment(image, style):
    mode = style['mode']
    if mode == 'photo': return image
    gray = ImageOps.grayscale(image)
    if mode == 'grayscale': return gray.convert('RGB')
    if mode == 'pixel':
        cell = style.get('cell', 4); levels = style.get('levels', 4)
        if not isinstance(levels, int) or not 2 <= levels <= 16: raise ValueError('Pixel levels must be 2-16.')
        small = gray.resize((max(1, image.width // cell), max(1, image.height // cell)), Image.Resampling.BOX)
        small = small.point([round(round(i / 255 * (levels - 1)) * 255 / (levels - 1)) for i in range(256)])
        return small.resize(image.size, Image.Resampling.NEAREST).convert('RGB')
    edges = gray.filter(ImageFilter.SMOOTH).filter(ImageFilter.FIND_EDGES)
    strength = style.get('strength', 2.4)
    if not isinstance(strength, (int, float)) or not .1 <= strength <= 10: raise ValueError('Edge strength must be 0.1-10.')
    alpha = ImageEnhance.Contrast(edges).enhance(strength).point(lambda v: min(255, v * 2))
    ImageDraw.Draw(alpha).rectangle((0, 0, image.width - 1, image.height - 1), outline=0, width=2)
    return Image.composite(Image.new('RGB', image.size, style.get('ink', '#696969')), Image.new('RGB', image.size, 'white'), alpha)


def wrapper(path, image, label):
    data = path.read_bytes()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{image.width}" height="{image.height}" viewBox="0 0 {image.width} {image.height}"><title>{html.escape(label)}</title><image width="{image.width}" height="{image.height}" href="data:image/png;base64,{base64.b64encode(data).decode()}"/></svg>').encode()


def prepare(request, output, comparison=None, refresh=False):
    entries = read(request)['assets']
    if not isinstance(entries, list) or not entries: raise ValueError('Provide a nonempty assets array.')
    ids = [s['id'] for s in entries]
    if len(set(ids)) != len(ids): raise ValueError('Asset IDs must be unique.')
    for entry in entries: check(entry)
    output.mkdir(parents=True, exist_ok=True)
    prior = {s['id']: s for s in read(output / 'manifest.json')['assets']} if (output / 'manifest.json').is_file() else {}
    records, reused = [], []
    engine_sha = digest(ENGINE.read_bytes() + ENGINE.with_name('colorset_contract.py').read_bytes())
    treatment_sha = digest(inspect.getsource(treatment).encode())
    for entry in entries:
        old = prior.get(entry['id'], {})
        cached = output / old.get('original', 'missing')
        if entry.get('sourceFile'): data = (request.parent / entry['sourceFile']).read_bytes()
        elif not refresh and old.get('downloadUrl') == entry['downloadUrl'] and cached.is_file() and digest(cached.read_bytes()) == old.get('sourceSha256'): data = cached.read_bytes()
        else: data = fetch(entry['downloadUrl'])
        source_sha = digest(data)
        if entry.get('sourceSha256') and source_sha != entry['sourceSha256']: raise ValueError('Pinned source changed: ' + entry['id'])
        raw = Image.open(io.BytesIO(data)); extension = '.jpg' if raw.format == 'JPEG' else '.png'
        if raw.format not in {'JPEG', 'PNG'}: extension = '.' + raw.format.lower()
        original = output / 'originals' / (entry['id'] + extension); original.parent.mkdir(exist_ok=True); original.write_bytes(data)
        image = prepare_image(data, entry)
        base = output / (entry['id'] + '.prepared.png'); image.save(base); prepared_sha = digest(base.read_bytes())
        variants = []
        for style in entry['treatments']:
            key = digest(json.dumps({'prepared': prepared_sha, 'style': style, 'renderer': engine_sha if style['mode'] == 'one-bit' else treatment_sha, 'version': 1}, sort_keys=True).encode())
            png = output / f'{entry["id"]}-{style["id"]}.png'; svg = png.with_suffix('.svg')
            previous = next((v for v in old.get('variants', []) if v['id'] == style['id']), {})
            if previous.get('cacheKey') == key and png.is_file() and svg.is_file() and digest(png.read_bytes()) == previous.get('pngSha256') and digest(svg.read_bytes()) == previous.get('svgSha256'):
                variants.append(previous); reused.append(entry['id'] + '/' + style['id']); continue
            if style['mode'] == 'one-bit':
                result = subprocess.run([sys.executable, str(ENGINE), str(base), '-o', str(svg), '--mode', 'custom', '--color', style.get('ink', '#696969'), '--quality-profile', 'manual', '--render-width', str(image.width), '--render-height', str(image.height), '--cell-size', str(style.get('cell', 2)), '--contrast', str(style.get('contrast', 1.1)), '--preview-png', str(png)], capture_output=True, text=True, encoding='utf-8')
                if result.returncode: raise ValueError(result.stderr)
            else:
                rendered = treatment(image, style); rendered.save(png); svg.write_bytes(wrapper(png, rendered, entry['label']))
            variants.append({**style, 'png': png.name, 'svg': svg.name, 'pngSha256': digest(png.read_bytes()), 'svgSha256': digest(svg.read_bytes()), 'cacheKey': key, 'width': image.width, 'height': image.height, 'recognitionReview': 'required at final display size', 'vectorArtwork': False})
        records.append({**entry, 'original': original.relative_to(output).as_posix(), 'sourceSha256': source_sha, 'preparedSha256': prepared_sha, 'variants': variants})
    save(output / 'manifest.json', {'schemaVersion': 1, 'assets': records, 'limits': 'Reviewed source records and deterministic treatments; no automated visual identity or reuse-permission certification.'})
    credits = ['# Documentary image credits', '', 'Keep original source and transformation records with the film.', '']
    for record in records:
        credits += ['## ' + record['label'], '', record['rights']['credit'], '', 'Source: ' + record['sourcePage'], 'Rights: ' + record['rights']['license'], 'Scope: ' + record['scope'], 'Changes: ' + ', '.join(v['mode'] for v in record['variants']), '']
    (output / 'credits.md').write_text('\n'.join(credits), encoding='utf-8')
    if comparison:
        comparisons = [r for r in records if len(r['variants']) > 1] or records[:6]
        width, height = 400, 300; count = max(len(r['variants']) + 1 for r in comparisons)
        sheet = Image.new('RGB', (count * width, len(comparisons) * height), 'white'); draw = ImageDraw.Draw(sheet); font = ImageFont.load_default(size=18)
        for row, record in enumerate(comparisons):
            paths = [('Original', output / (record['id'] + '.prepared.png'))] + [(v['id'], output / v['png']) for v in record['variants']]
            for col, (name, path) in enumerate(paths):
                thumb = ImageOps.contain(Image.open(path).convert('RGB'), (width - 28, height - 65))
                x, y = col * width, row * height; sheet.paste(thumb, (x + (width - thumb.width) // 2, y + 16 + (height - 65 - thumb.height) // 2)); draw.text((x + 16, y + height - 40), record['id'] + ' / ' + name, fill='#333e48', font=font)
        comparison.parent.mkdir(parents=True, exist_ok=True); sheet.save(comparison)
    return {'ok': True, 'assets': len(records), 'variants': sum(len(r['variants']) for r in records), 'reused': reused}


def audit(story, manifest, output, html_path=None, screenshot=None):
    assets = {a['id']: a for a in read(manifest)['assets']}; bindings, issues = [], []
    one_bit = 0
    for asset in assets.values():
        for filename, expected in [(asset['original'], asset['sourceSha256']), (asset['id'] + '.prepared.png', asset['preparedSha256'])]:
            path = manifest.parent / filename
            if not path.is_file() or digest(path.read_bytes()) != expected: issues.append(asset['id'] + ': changed source or prepared bytes')
        for variant in asset['variants']:
            intact = True
            for field in ['png', 'svg']:
                path = manifest.parent / variant[field]
                if not path.is_file() or digest(path.read_bytes()) != variant[field + 'Sha256']:
                    issues.append(asset['id'] + ': changed treatment bytes'); intact = False
            if variant['mode'] == 'one-bit' and intact:
                from PIL import ImageColor
                with Image.open(manifest.parent / variant['png']) as image: colors = image.convert('RGB').getcolors(maxcolors=3)
                if colors is None or {value for _, value in colors} != {(255, 255, 255), ImageColor.getrgb(variant.get('ink', '#696969'))}:
                    issues.append(asset['id'] + ': one-bit palette must contain exactly white and its declared ink')
                else: one_bit += 1
    for scene in read(story)['scenes']:
        for item in scene.get('objects', []):
            if item.get('depiction') == 'diagram':
                if item.get('kind') == 'physical' and item.get('purpose') == 'identity': issues.append(scene['id'] + '/' + item['id'] + ': use a real photograph for physical identity')
                elif not item.get('reason'): issues.append(scene['id'] + '/' + item['id'] + ': explain the diagram purpose')
                continue
            asset = assets.get(item.get('asset'))
            variant = next((v for v in asset.get('variants', []) if v['id'] == item.get('variant')), None) if asset else None
            if not variant: issues.append(scene['id'] + '/' + item['id'] + ': missing photo binding'); continue
            bindings.append({'scene': scene['id'], 'object': item['id'], 'asset': asset['id'], 'file': variant['png']})
    observed = []
    if html_path:
        from playwright.sync_api import sync_playwright
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(html_path.parent.resolve())))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as pw:
                cache = Path(os.environ.get('LOCALAPPDATA', '')) / 'ms-playwright'; paths = sorted(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'), reverse=True)
                browser = pw.chromium.launch(executable_path=str(paths[0]) if paths else None, headless=True)
                page = browser.new_page(viewport={'width': 1920, 'height': 1080}); page.goto(f'http://127.0.0.1:{server.server_port}/{html_path.name}'); page.evaluate('async()=>{await document.fonts.ready;if(window.ready)await window.ready;}')
                for binding in bindings:
                    actual = page.evaluate('''b=>{const scene=document.getElementById('scene-'+b.scene)||document;const object=[...scene.querySelectorAll('[data-object-id]')].find(e=>e.dataset.objectId===b.object);const image=object?.querySelector('[data-documentary-id]');return{asset:image?.dataset.documentaryId,href:image?.getAttribute('href')||image?.getAttribute('src'),box:object?(()=>{const x=typeof object.getBBox==='function'?object.getBBox():object.getBoundingClientRect();return{x:x.x,y:x.y,width:x.width,height:x.height};})():null};}''', binding)
                    if actual['asset'] != binding['asset'] or not (actual.get('href') or '').endswith(binding['file']) or not actual.get('box') or min(actual['box']['width'], actual['box']['height']) <= 0:
                        issues.append(binding['scene'] + '/' + binding['object'] + ': rendered image does not match the photo binding')
                    observed.append({**binding, 'actual': actual})
                if screenshot:
                    screenshot.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot))
                browser.close()
        finally: server.shutdown()
    report = {'ok': not issues, 'sourceAssetsVerified': len(assets) if not issues else None, 'oneBitPalettesVerified': one_bit, 'photoBindings': len(bindings), 'renderedVerification': 'observed' if html_path else 'pending', 'bindings': observed or bindings, 'issues': issues}
    if screenshot: report['screenshot'] = str(screenshot)
    save(output, report); return report


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('fetch'); p.add_argument('--url', required=True); p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('prepare'); p.add_argument('--request', type=Path, required=True); p.add_argument('--output', type=Path, required=True); p.add_argument('--comparison', type=Path); p.add_argument('--refresh', action='store_true')
    p = sub.add_parser('audit'); p.add_argument('--story', type=Path, required=True); p.add_argument('--manifest', type=Path, required=True); p.add_argument('--output', type=Path, required=True); p.add_argument('--html', type=Path); p.add_argument('--screenshot', type=Path)
    args = parser.parse_args()
    if args.command == 'audit' and args.screenshot and not args.html: parser.error('--screenshot requires --html')
    try:
        if args.command == 'fetch': report = acquire(args.url, args.output)
        elif args.command == 'prepare': report = prepare(args.request, args.output, args.comparison, args.refresh)
        else: report = audit(args.story, args.manifest, args.output, args.html, args.screenshot)
        compact = {k: v for k, v in report.items() if k not in ['bindings', 'reused']}
        if isinstance(report.get('reused'), list): compact['reusedVariants'] = len(report['reused'])
        elif 'reused' in report: compact['reused'] = report['reused']
        print(json.dumps(compact)); return 0 if report['ok'] else 2
    except (ValueError, KeyError, OSError) as error:
        print(json.dumps({'ok': False, 'error': str(error)})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
