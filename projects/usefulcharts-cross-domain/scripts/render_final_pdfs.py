#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.25"]
# ///
"""Render the final exported PDFs for independent visual inspection."""
from pathlib import Path
import pymupdf
root=Path(__file__).resolve().parents[1]/'artifacts'
for case in ['bsd','instruments','mars']:
    with pymupdf.open(root/'revision-2'/case/'poster.pdf') as pdf:
        scale=1700/pdf[0].rect.width
        pdf[0].get_pixmap(matrix=pymupdf.Matrix(scale,scale)).save(root/'screenshots'/f'{case}-pdf.png')
print('Rendered all three final one-page PDFs at a common 1700-pixel width.')
