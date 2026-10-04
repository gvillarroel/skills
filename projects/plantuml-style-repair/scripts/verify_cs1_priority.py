#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify actual primary category paint and finite CS2 artifact stability."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


PRIMARY_FAMILIES = [
    'activity', 'archimate', 'chart', 'chen', 'class', 'component', 'deployment',
    'ebnf', 'gantt', 'ie', 'json', 'mindmap', 'nwdiag', 'object', 'packetdiag',
    'regex', 'salt', 'sdl', 'sequence', 'state', 'timing', 'usecase', 'wbs', 'yaml',
]


def property_value(node, key, fallback=''):
    found = re.findall(r'(?:^|;)\s*'+re.escape(key)+r'\s*:\s*([^;!]+)', node.get('style', ''))
    return found[-1].strip().lower() if found else node.get(key, fallback).lower()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cs1', type=Path, required=True)
    parser.add_argument('--cs2', type=Path, required=True)
    parser.add_argument('--previous-cs2', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    findings, primary_rows, stable_rows = [], [], []
    for family in PRIMARY_FAMILIES:
        path = args.cs1/'svg'/f'{family}.svg'
        root = ET.parse(path).getroot()
        fills = [property_value(node, 'fill') for node in root.iter()
                 if node.tag.rsplit('}', 1)[-1] in {'rect', 'path', 'polygon', 'ellipse', 'circle'}
                 and node.get('data-arrow-id') is None]
        row = {'family': family, 'sha256': digest(path), 'primaryRedPresent': '#9e1b32' in fills,
               'earlyRemainingHues': sorted(set(fills)&{'#6d1222', '#e8002a', '#ffccd5'}),
               'nativeStyle': root.get('data-native-style')}
        primary_rows.append(row)
        if not row['primaryRedPresent'] or row['earlyRemainingHues'] or row['nativeStyle'] != 'scoped-solid-v3':
            findings.append(f'{family}: primary red or remaining-hue priority failed')
    for path in sorted(args.cs2.glob('*/*')):
        if path.suffix not in {'.svg', '.png'}:
            continue
        relative = path.relative_to(args.cs2)
        old = args.previous_cs2/relative
        if not old.is_file():
            findings.append(f'CS2 baseline missing: {relative.as_posix()}')
            continue
        actual, previous = path.read_bytes(), old.read_bytes()
        if path.suffix == '.svg':
            normalized = actual.replace(b'scoped-solid-v3', b'scoped-solid-v2').replace(b'\r\n', b'\n')
            expected = previous.replace(b'\r\n', b'\n')
            unchanged = normalized == expected
        else:
            unchanged = actual == previous
        stable_rows.append({'path': relative.as_posix(), 'sha256': digest(path),
                            'previousSha256': digest(old), 'paintGeometryUnchanged': unchanged,
                            'svgNormalization': 'native style version and line endings only' if path.suffix == '.svg' else None})
        if not unchanged:
            findings.append(f'CS2 paint or geometry changed: {relative.as_posix()}')
    report = {'ok': not findings, 'primaryFamilies': primary_rows, 'cs2Stability': stable_rows,
              'findings': findings}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'ok': report['ok'], 'primaryFamilies': len(primary_rows),
                      'cs2Artifacts': len(stable_rows), 'findings': findings}, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
