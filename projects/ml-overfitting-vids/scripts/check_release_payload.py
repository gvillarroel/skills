#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the new plugin matches canonical sources and preserves prior producers."""
import json,hashlib,py_compile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
base=ROOT/'projects/line-world-video/artifacts/packages'
old=base/'line-world-video-0.5.1-extracted';new=base/'line-world-video-0.6.0-extracted'
changes=[]
for skill in ['line-world-d3','line-world-mermaid','line-world-icons','line-world-hyperframes']:
    a={p.relative_to(old/'skills'/skill).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (old/'skills'/skill).rglob('*') if p.is_file()}
    b={p.relative_to(new/'skills'/skill).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (new/'skills'/skill).rglob('*') if p.is_file()}
    assert a==b,'Prior producer payload changed: '+skill
for skill in ['line-world-video','line-world-google-vids']:
    source=ROOT/'skills'/skill
    for p in source.rglob('*'):
        if p.is_file() and not any(x in p.parts for x in ['__pycache__','node_modules']) and p.suffix not in ['.pyc','.pyo']:
            assert p.read_bytes()==(new/'skills'/skill/p.relative_to(source)).read_bytes(),str(p)
for p in (ROOT/'projects/ml-overfitting-vids/scripts').glob('*.py'):py_compile.compile(str(p),doraise=True)
report={'ok':True,'unchangedProducerBundles':4,'canonicalChangedBundlesEqualExtracted':True,'projectPythonSourcesCompile':True,'pluginVersion':'0.6.0'}
path=ROOT/'projects/ml-overfitting-vids/artifacts/reviews/payload-source-check.json';path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
