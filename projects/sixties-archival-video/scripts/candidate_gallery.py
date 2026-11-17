#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13"]
# ///
"""Cache source thumbnails and make a numbered, visually inspectable contact sheet."""
import argparse
import concurrent.futures
import json
import textwrap
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--count', type=int)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding='utf-8'))
    rows = data.get('results', data.get('shots', []))
    rows = rows[args.start-1:args.start-1+args.count if args.count else None]
    cache = ROOT/'artifacts/images/candidates'; cache.mkdir(parents=True, exist_ok=True)
    def fetch(row):
        key = row.get('id', row['shot']); file = cache/(key+'.jpg')
        if not file.exists():
            request = urllib.request.Request(row['keyframe'], headers={'User-Agent':'ArchivalVideoReview/1.0'})
            with urllib.request.urlopen(request, timeout=30) as response:
                file.write_bytes(response.read())
        return file
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        files = list(pool.map(fetch, rows))
    width, height, columns = 480, 350, 3
    sheet = Image.new('RGB', (columns*width, ((len(rows)+columns-1)//columns)*height), 'white')
    draw = ImageDraw.Draw(sheet)
    font_path = 'C:/Windows/Fonts/arial.ttf'
    font = ImageFont.truetype(font_path, 19) if Path(font_path).is_file() else ImageFont.load_default(size=19)
    for i, (row, file) in enumerate(zip(rows, files, strict=True)):
        x, y = i%columns*width, i//columns*height
        thumb = ImageOps.contain(Image.open(file).convert('RGB'), (width-20, 260))
        sheet.paste(thumb, (x+(width-thumb.width)//2, y+(260-thumb.height)//2))
        text = f"{row.get('option',i+1)} | {row['shot']} | {row.get('film',data.get('film',''))}"
        draw.multiline_text((x+12,y+268),'\n'.join(textwrap.wrap(text,43)[:3]),font=font,fill='#333e48',spacing=3)
    args.output.parent.mkdir(parents=True, exist_ok=True); sheet.save(args.output)
    print(json.dumps({'options':len(rows),'sheet':str(args.output)}))


if __name__ == '__main__': main()
