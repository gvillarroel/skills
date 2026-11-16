#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Expose a verified release in the existing workspace-local Codex marketplace."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'projects/line-world-video'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    catalog = ROOT / '.agents/plugins/marketplace.json'
    package = PROJECT / 'artifacts/packages' / ('line-world-video-' + args.version) / 'plugin'
    if not package.resolve().is_relative_to(PROJECT.resolve()) or not catalog.is_file():
        raise ValueError('Use an existing workspace marketplace and a contained built package.')
    manifest = json.loads((package / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    if manifest['name'] != 'line-world-video' or manifest['version'] != args.version:
        raise ValueError('The actual native plugin manifest differs from the selected release.')
    bundle = json.loads((package / 'bundle-manifest.json').read_text(encoding='utf-8'))
    for file in bundle['files']:
        path = (package / file['path']).resolve()
        if not path.is_relative_to(package.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != file['sha256']:
            raise ValueError('Release payload integrity check failed.')
    data = json.loads(catalog.read_text(encoding='utf-8'))
    entry = {'name': 'line-world-video', 'source': {'source': 'local', 'path': './' + package.relative_to(ROOT).as_posix()},
             'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Creativity'}
    others = [p for p in data['plugins'] if p['name'] != entry['name']]
    if next((p for p in data['plugins'] if p['name'] == entry['name']), None) == entry:
        print(json.dumps({'ok': True, 'reused': True, 'marketplace': data['name'], 'pluginId': entry['name'] + '@' + data['name'], 'version': args.version})); return
    backups = PROJECT / 'artifacts/reviews/local-marketplace'; backups.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(catalog.read_bytes()).hexdigest()
    (backups / (digest + '.json')).write_bytes(catalog.read_bytes())
    data['plugins'] = [*others, entry]
    temporary = catalog.with_suffix('.json.pending')
    temporary.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8'); temporary.replace(catalog)
    print(json.dumps({'ok': True, 'reused': False, 'marketplace': data['name'], 'pluginId': entry['name'] + '@' + data['name'],
                      'version': args.version, 'preservedEntries': [p['name'] for p in others], 'scope': 'Workspace catalog availability only; no global installation or permissions changed.'}))


if __name__ == '__main__': main()
