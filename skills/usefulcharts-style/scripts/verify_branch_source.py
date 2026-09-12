#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify a data-first branch source after the composer adds layout fields."""

import argparse
import json
from pathlib import Path


def identity(item, path):
    if not isinstance(item, dict):
        return None
    if 'id' in item:
        return ('id', item['id'])
    if path == 'annotations' and 'node' in item:
        return ('caption', item['node'], item.get('kind'), item.get('label'), item.get('field'))
    return None


def verify_fields(original, resolved):
    """Allow added measurements, but preserve every supplied field and item."""
    findings = []
    def compare(before, after, path=''):
        if isinstance(before, dict):
            if not isinstance(after, dict):
                findings.append(dict(path=path, issue='Object type changed.'))
                return
            for key, value in before.items():
                # The documented transformation resolves branches into authored
                # coordinates. This is the only supplied field it may replace.
                if not path and key == 'layout' and value == 'branches' and after.get(key) == 'authored':
                    continue
                child = f'{path}.{key}' if path else key
                if key not in after:
                    findings.append(dict(path=child, issue='Supplied field is missing.'))
                else:
                    compare(value, after[key], child)
        elif isinstance(before, list):
            if not isinstance(after, list) or len(before) != len(after):
                findings.append(dict(path=path, issue='Item inventory changed.'))
                return
            keys = [identity(item, path) for item in before]
            current = [identity(item, path) for item in after]
            if before and all(key is not None for key in keys):
                if len(set(keys)) != len(keys) or len(set(current)) != len(current) or set(keys) != set(current):
                    findings.append(dict(path=path, issue='Stable item identities changed or are duplicated.'))
                    return
                lookup = dict(zip(current, after))
                for key, item in zip(keys, before):
                    compare(item, lookup[key], f'{path}[{key[1]}]')
            else:
                for index, (a, b) in enumerate(zip(before, after)):
                    compare(a, b, f'{path}[{index}]')
        elif before != after or (isinstance(before, bool) != isinstance(after, bool)):
            findings.append(dict(path=path, issue='Supplied value changed.'))
    compare(original, resolved)
    return dict(status='fail' if findings else 'pass', findings=findings,
                nodes=len(resolved.get('nodes', [])), edges=len(resolved.get('edges', [])),
                captions=len(resolved.get('annotations', [])),
                scope='Supplied fields and inventories only. Added layout fields are allowed; inspect the rendered poster separately.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('resolved', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if len({p.resolve() for p in (args.original, args.resolved, args.report)}) != 3:
        parser.error('Input and report paths must be distinct.')
    original = json.loads(args.original.read_text(encoding='utf-8-sig'))
    resolved = json.loads(args.resolved.read_text(encoding='utf-8-sig'))
    result = verify_fields(original, resolved)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))
    return result['status'] != 'pass'


if __name__ == '__main__':
    raise SystemExit(main())
