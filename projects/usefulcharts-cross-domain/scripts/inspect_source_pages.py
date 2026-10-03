#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.25"]
# ///
"""Render the source pages used to validate classification and table context."""
from pathlib import Path
import pymupdf

root = Path(__file__).resolve().parents[1] / 'artifacts'
out = root / 'sources' / 'page-previews'
out.mkdir(exist_ok=True)
for name, pages in [('hornbostel-sachs-2011', [3,7,11,15,20,22]), ('mars-press-kit', [68,69])]:
    with pymupdf.open(root / 'sources' / (name + '.pdf')) as doc:
        for page in pages:
            doc[page].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(out / f'{name}-{page+1}.png')
print('Rendered eight factual source pages.')
