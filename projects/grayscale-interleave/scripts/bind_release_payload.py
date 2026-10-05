#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind accepted isolated runtime inventories to exact staged or committed Git blobs."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ref', default=':', help='Use : for the index or an exact commit SHA.')
    parser.add_argument('--report', default='projects/grayscale-interleave/artifacts/manifests/release-payload.json')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('collector', ROOT/'evaluations/grayscale-interleave/collect_acceptance.py')
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    accepted = json.loads((ROOT/'evaluations/grayscale-interleave/results.json').read_bytes())
    if accepted.get('ok') is not True or accepted.get('acceptedOwnerCount') != 30:
        raise ValueError('All thirty current-payload scoped cohorts must be accepted before release binding')
    if args.ref == ':':
        command = ['git', 'ls-files', '--stage', '-z', 'skills/']
    else:
        command = ['git', 'ls-tree', '-r', '-z', args.ref, '--', 'skills/']
    records = subprocess.check_output(command, cwd=ROOT).decode().split('\0')
    inventories = {owner: {} for owner in accepted['selected']}
    selected = []
    for record in filter(None, records):
        metadata, name = record.split('\t', 1)
        fields = metadata.split()
        object_id = fields[1] if args.ref == ':' else fields[2]
        if args.ref == ':' and fields[2] != '0':
            raise ValueError(f'Unmerged release source: {name}')
        if args.ref != ':' and fields[1] != 'blob':
            raise ValueError(f'Unexpected source object type: {name}')
        parts = Path(name).parts
        if len(parts) < 3 or parts[1] not in inventories:
            continue
        relative = Path(*parts[2:])
        if any(part in collector.IGNORED for part in relative.parts) or relative.parts[:2] == ('assets', 'examples') or relative.suffix in {'.pyc', '.pyo'}:
            continue
        selected.append((parts[1], relative, object_id))
    # Read immutable objects in one process. The technical-logo bundle contains
    # thousands of small vectors; one Git process per file is unnecessarily slow.
    object_ids = list(dict.fromkeys(row[2] for row in selected))
    stream = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=('\n'.join(object_ids)+'\n').encode(), capture_output=True, check=True).stdout
    objects, offset = {}, 0
    for expected_id in object_ids:
        end = stream.index(b'\n', offset)
        fields = stream[offset:end].decode('ascii').split()
        if len(fields) != 3 or fields[0] != expected_id or fields[1] != 'blob':
            raise ValueError(f'Invalid immutable Git object: {expected_id}')
        size = int(fields[2])
        offset = end + 1
        data = stream[offset:offset+size]
        if len(data) != size or stream[offset+size:offset+size+1] != b'\n':
            raise ValueError(f'Truncated immutable Git object: {expected_id}')
        objects[expected_id] = data
        offset += size + 1
    if offset != len(stream):
        raise ValueError('Unexpected trailing Git batch data')
    checkout_conversions = []
    for owner, relative, object_id in selected:
        data = objects[object_id]
        if relative.suffix.lower() == '.vue':
            validated = (ROOT/'skills'/owner/relative).read_bytes()
            if data != validated and data == validated.replace(b'\r\n', b'\n'):
                # The frozen runtime profile did not list Vue as text. Prove
                # only Git's checkout newline conversion, then materialize its
                # validated representation for the unchanged accepted digest.
                validated.decode('utf-8')
                if b'\0' in validated:
                    raise ValueError('A Vue checkout conversion contains binary data')
                checkout_conversions.append({'skill': owner, 'path': relative.as_posix(),
                                             'gitSha256': hashlib.sha256(data).hexdigest(),
                                             'validatedSha256': hashlib.sha256(validated).hexdigest(),
                                             'conversion': 'Git LF equals validated CRLF converted to LF; all other bytes equal.'})
                data = validated
        if relative.suffix.lower() in collector.TEXT:
            data = data.replace(b'\r\n', b'\n')
        inventories[owner][relative.as_posix()] = hashlib.sha256(data).hexdigest()
    rows = []
    for owner, expected in accepted['selected'].items():
        actual = inventories[owner]
        canonical = collector.inventory(ROOT/'skills'/owner)
        digest = collector.digest(actual)
        ok = actual == canonical and digest == expected['normalizedPayloadSha256'] and len(actual) == expected['sourceFileCount']
        differences = sorted(name for name in set(actual) | set(canonical) if actual.get(name) != canonical.get(name))
        rows.append({'skill': owner, 'ok': ok, 'fileCount': len(actual), 'normalizedPayloadSha256': digest,
                     'differences': differences,
                     'contract': expected['contract'], 'naturalistic': expected['naturalistic']})
    report = {'ref': args.ref, 'ok': all(row['ok'] for row in rows), 'ownerCount': len(rows),
              'normalization': accepted['normalization'], 'provenVueCheckoutConversions': checkout_conversions,
              'binderSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'owners': rows}
    target = (ROOT/args.report).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError('The report must stay inside the repository')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'ref': args.ref, 'ok': report['ok'], 'ownerCount': len(rows)}))
    if not report['ok']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
