#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Verify that a skill remains guidance-only and carries no reference artwork."""
from pathlib import Path
import argparse,hashlib,json,re
p=argparse.ArgumentParser();p.add_argument('skill',type=Path);p.add_argument('--output',type=Path)
args=p.parse_args();root=args.skill.resolve()
expected={'SKILL.md','agents/openai.yaml','references/svg-mechanics.md'}
actual={file.relative_to(root).as_posix() for file in root.rglob('*') if file.is_file()}
assert actual==expected,actual
for file in root.rglob('*'):
    assert not file.is_symlink(),file
    if not file.is_file():continue
    text=file.read_text(encoding='utf-8')
    assert file.suffix in {'.md','.yaml'} and file.stat().st_size<25000
    assert not re.search(r'<(?:svg|path|image|polygon|polyline)\b|data:image|base64,|vector-\d{3}|p\d{2}-s\d{3}|Fox Rockett|\bd\s*=\s*["\']\s*[Mm]\s*\d',text,re.I),file
    assert not re.search(r'(?:https?://)[^\s)>]+\.(?:svg|png|jpe?g|webp)(?:\?|\b)',text,re.I),file
report={'passed':True,'artwork_files':0,'encoded_artwork_or_path_data':False,'reference_asset_links':0,'files':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in sorted(actual)}}
if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
