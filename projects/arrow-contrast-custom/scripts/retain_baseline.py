#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Correct misleading initial inventory labels and retain the evidence limitation."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/arrow-contrast-custom/artifacts'
EVIDENCE=ROOT/'evaluations/arrow-contrast-custom'
raw=OUT/'data/inventory-before.json'
if raw.exists():
 raw.rename(OUT/'data/inventory-intermediate-overwrite.json')
for path in (OUT/'screenshots').glob('d3-*-before.png'):
 path.rename(path.with_name(path.name.replace('-before.png','-intermediate.png')))
report={
 'date':'2026-10-03','phase':'before','evidenceStatus':'Initial D3 and SVG-brief raw inventory was accidentally overwritten by an intermediate rerun before phase-specific output paths were introduced. These counts were reported to the parent before edits and are retained as a session-derived summary, not as recreated raw measurements. Current raw file and mislabeled screenshots are renamed intermediate-overwrite/intermediate. The independent Three.js before report and later non-marker glyph before inventory were preserved.',
 'galleries':[
  {'gallery':'d3-animated-svg-cs1','markerArrowCount':50,'headOcclusionCount':13,'headLowContrastCount':16,'shaftLowContrastCount':30,'markerMismatchCount':8},
  {'gallery':'d3-animated-svg-colorset2','markerArrowCount':50,'headOcclusionCount':13,'headLowContrastCount':13,'shaftLowContrastCount':23,'markerMismatchCount':8}],
 'svgBrief':{'allowedTokenCount':54,'lowContrastTokenCount':24,'baselineMechanism':'Arrow inherited category fill on white canvas'},
 'threePublishedVectorField':{'arrowCount':20,'deliveryTimes':[0,1,2,3,4],'interiorSampleCount':100,'lowContrastInteriorSampleCount':28,'rawReport':'projects/arrow-contrast-custom/artifacts/data/three-vector-field-before.json'},
 'separateNonMarkerGlyphBaseline':'evaluations/arrow-contrast-custom/glyphs-before-20261003.json'}
(EVIDENCE/'inventory-before-20261003.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Retained the initial summary with explicit raw-overwrite limitation; preserved independent baselines.')
