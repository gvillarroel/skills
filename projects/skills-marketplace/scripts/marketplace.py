#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build, verify, extend and publish the repository's generated plugin marketplace."""
import argparse
import base64
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

PROJECT = Path(__file__).resolve().parent.parent
REPO = PROJECT.parents[1]
TEXT = {'.json', '.md', '.txt', '.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.css', '.html', '.yaml', '.yml', '.svg', '.in'}


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=True) + '\n').encode())
def sha(data): return hashlib.sha256(data).hexdigest()
def git(root, *args, check=True):
    return subprocess.run(['git', *args], cwd=root, check=check, capture_output=True, text=True, encoding='utf-8')
def contained(root, name):
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or '.git' in relative.parts or '\\' in name or ':' in name:
        raise ValueError('Use a contained relative distribution path: ' + name)
    path = root / name
    if not path.resolve().is_relative_to(root.resolve()): raise ValueError('Distribution path escapes its root.')
    return path


def entries(catalog):
    names = []
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', catalog['name']): raise ValueError('Use a stable marketplace name.')
    for entry in catalog['plugins']:
        name = entry['name']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in names: raise ValueError('Use unique stable plugin names.')
        if entry['kind'] not in ['directory', 'line-world-release']: raise ValueError('Unknown build recipe.')
        if not entry.get('displayName') or not entry.get('description') or not entry.get('category'): raise ValueError('Supply install-surface metadata.')
        path = entry.get('path', entry.get('spec', ''))
        contained(REPO, path)
        if any(p in {'artifacts', 'node_modules', '.cache'} for p in PurePosixPath(path).parts): raise ValueError('Catalog sources must be versioned authoring inputs, not ignored build output.')
        names.append(name)
    if not names: raise ValueError('Provide at least one plugin.')
    return names


def export_snapshot(repo, ref, catalog, destination):
    paths = ['projects/skills-marketplace/catalog.json']
    for entry in catalog['plugins']:
        if entry['kind'] == 'directory': paths.append(entry['path'])
        else:
            spec = json.loads(git(repo, 'show', ref + ':' + entry['spec']).stdout)
            paths += ['projects/line-world-video/package-spec.json', 'projects/line-world-video/plugin.json', 'projects/line-world-video/scripts/package_plugin.py']
            paths += ['skills/' + spec.get('sources', {}).get(name, name) for name in spec['skills']]
    result = subprocess.run(['git', 'archive', '--format=zip', ref, '--', *sorted(set(paths))], cwd=repo, capture_output=True, check=True)
    destination.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(result.stdout)) as archive:
        for member in archive.infolist():
            if member.is_dir(): continue
            path = contained(destination, member.filename)
            parts = PurePosixPath(member.filename).parts
            if any(p in {'node_modules', '__pycache__', '.cache'} for p in parts): continue
            if any(parts[i:i+2] == ('assets', 'examples') for i in range(len(parts)-1)): continue
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(archive.read(member))


def check(root):
    manifest = read(root / 'distribution-manifest.json')
    listed = [item['path'] for item in manifest['files']]
    actual = [p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts and p != root / 'distribution-manifest.json']
    if len(set(listed)) != len(listed) or set(listed) != set(actual): raise ValueError('Distribution inventory is incomplete or duplicated.')
    for item in manifest['files']:
        path = contained(root, item['path'])
        if not path.is_file() or sha(path.read_bytes()) != item['sha256']: raise ValueError('Changed distribution file: ' + item['path'])
    catalog = read(root / '.agents/plugins/marketplace.json')
    if catalog['name'] != manifest['name'] or len(catalog['plugins']) != len(manifest['plugins']): raise ValueError('Catalog and distribution inventory differ.')
    for entry in catalog['plugins']:
        folder = contained(root, entry['source']['path'].removeprefix('./'))
        plugin = read(folder / '.codex-plugin/plugin.json')
        if plugin['name'] != entry['name'] or not plugin.get('version'): raise ValueError('Invalid native plugin identity.')
        bundle = read(folder / 'bundle-manifest.json')
        release = next((p for p in manifest['plugins'] if p['name'] == plugin['name']), None)
        payload = sha(json.dumps(bundle['files'], sort_keys=True).encode())
        if not release or release['version'] != plugin['version'] or payload != release['payloadSha256']: raise ValueError('Plugin release and payload inventory differ.')
        for file in bundle['files']:
            path = contained(folder, file['path'])
            if sha(path.read_bytes()) != file['sha256']: raise ValueError('Invalid plugin payload digest.')
    return {'ok': True, 'marketplace': manifest['name'], 'plugins': manifest['plugins'], 'files': len(manifest['files']), 'sourceCommit': manifest['sourceCommit']}


def build(repo, ref, output):
    commit = git(repo, 'rev-parse', ref + '^{commit}').stdout.strip()
    catalog = json.loads(git(repo, 'show', commit + ':projects/skills-marketplace/catalog.json').stdout); entries(catalog)
    if output.exists() and any(output.iterdir()):
        old = read(output / 'distribution-manifest.json')
        if old['sourceCommit'] == commit: return {**check(output), 'reused': True}
        raise ValueError('Choose a new empty build directory for a different source commit.')
    output.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='source-', dir=output.parent)); snapshot = workspace / 'repo'
    export_snapshot(repo, commit, catalog, snapshot)
    results, public = [], []
    for entry in catalog['plugins']:
        if entry['kind'] == 'line-world-release':
            spec = read(snapshot / entry['spec']); version = spec['version']
            result = subprocess.run(['uv', 'run', '--script', str(snapshot / 'projects/line-world-video/scripts/package_plugin.py')], cwd=snapshot, capture_output=True, text=True)
            if result.returncode: raise ValueError('Plugin build failed: ' + result.stdout + result.stderr)
            source = snapshot / 'projects/line-world-video/artifacts/packages' / ('line-world-video-' + version) / 'plugin'
        else: source = snapshot / entry['path']
        target = output / 'plugins' / entry['name']; shutil.copytree(source, target)
        native = read(target / '.codex-plugin/plugin.json')
        if native['name'] != entry['name']: raise ValueError('Registry/plugin name mismatch.')
        native.setdefault('interface', {}).update(displayName=entry['displayName'], shortDescription=entry['description'])
        write(target / '.codex-plugin/plugin.json', native)
        # Keep canonical primary/adapter bytes exact. Normalize generated profile
        # metadata so Windows and Linux produce the same distribution bytes.
        for path in target.rglob('*'):
            if not path.is_file(): continue
            rel = path.relative_to(target).as_posix()
            canonical = rel.startswith(('skills/line-world-video/', 'skills/line-world-google-vids/'))
            if not canonical and path.suffix in TEXT:
                raw = path.read_bytes()
                try: raw.decode('utf-8')
                except UnicodeDecodeError: continue
                path.write_bytes(raw.replace(b'\r\n', b'\n'))
        bundle_path = target / 'bundle-manifest.json'
        files = [{'path': p.relative_to(target).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in sorted(target.rglob('*')) if p.is_file() and p != bundle_path]
        write(bundle_path, {'name': native['name'], 'version': native['version'], 'files': files})
        digest = sha(json.dumps(files, sort_keys=True).encode())
        results.append({'name': native['name'], 'displayName': entry['displayName'], 'version': native['version'], 'payloadSha256': digest, 'files': len(files)})
        public.append({'name': native['name'], 'source': {'source': 'local', 'path': './plugins/' + native['name']}, 'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': entry['category']})
    write(output / '.agents/plugins/marketplace.json', {'name': catalog['name'], 'interface': {'displayName': catalog['displayName']}, 'plugins': public})
    write(output / '.claude-plugin/marketplace.json', {'name': catalog['name'], 'owner': {'name': 'Gerardo Villarroel'}, 'plugins': [{'name': e['name'], 'source': e['source']['path'], 'description': next(c['description'] for c in catalog['plugins'] if c['name'] == e['name'])} for e in public]})
    (output / '.gitattributes').write_bytes(b'* -text\n')
    lines = ['# ' + catalog['displayName'], '', 'Generated installable distribution from [the canonical skills repository](https://github.com/gvillarroel/skills/tree/main).', '', '## Install', '', '```sh', 'codex plugin marketplace add gvillarroel/skills --ref marketplace', 'codex plugin add line-world-video@' + catalog['name'], '```', '', 'Restart ChatGPT Desktop, choose **Skills Marketplace** in Plugins, and start a new chat after installation.', '', '## Plugins', '', '| Plugin | Version | Install |', '| --- | --- | --- |']
    lines += ['| ' + p['displayName'] + ' | ' + p['version'] + ' | `codex plugin add ' + p['name'] + '@' + catalog['name'] + '` |' for p in results]
    lines += ['', '## Maintain', '', 'Edit versioned sources and `projects/skills-marketplace/catalog.json` on `main`. The marketplace workflow rebuilds and validates this branch. Do not edit generated plugin copies here.', '', 'Refresh this source with `codex plugin marketplace upgrade ' + catalog['name'] + '`.', '', 'Source commit: `' + commit + '`.', '', 'Catalog availability, installation, external account authentication and frontend activation are separate states. No user account configuration or credentials are bundled.', '']
    (output / 'README.md').write_bytes('\n'.join(lines).encode())
    files = [{'path': p.relative_to(output).as_posix(), 'sha256': sha(p.read_bytes())} for p in sorted(output.rglob('*')) if p.is_file()]
    write(output / 'distribution-manifest.json', {'schemaVersion': 1, 'name': catalog['name'], 'sourceCommit': commit, 'plugins': results, 'files': files})
    return check(output)


def publish(build_root, checkout, remote, branch, token_env=None):
    result = check(build_root); incoming = read(build_root / 'distribution-manifest.json')
    if not checkout.resolve().is_relative_to(PROJECT / 'artifacts'): raise ValueError('Publish only through an owned project artifact checkout.')
    env = os.environ.copy()
    if token_env:
        token = env.get(token_env)
        if not token: raise ValueError('The named CI token variable is not set.')
        # extraheader is multi-valued. Clear an inherited checkout credential
        # before adding one header; duplicate Authorization headers fail remotely.
        env.update(GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='http.https://github.com/.extraheader', GIT_CONFIG_VALUE_0='', GIT_CONFIG_KEY_1='http.https://github.com/.extraheader', GIT_CONFIG_VALUE_1='AUTHORIZATION: basic ' + base64.b64encode(('x-access-token:' + token).encode()).decode())
    def run(*args, check=True): return subprocess.run(['git', *args], cwd=checkout, env=env, check=check, capture_output=True, text=True, encoding='utf-8')
    if not checkout.exists():
        found = subprocess.run(['git', 'ls-remote', '--exit-code', '--heads', remote, branch], env=env, capture_output=True, text=True)
        checkout.parent.mkdir(parents=True, exist_ok=True)
        if found.returncode == 0: subprocess.run(['git', 'clone', '--quiet', '--single-branch', '--branch', branch, remote, str(checkout)], env=env, check=True, capture_output=True)
        elif found.returncode == 2:
            checkout.mkdir(); run('init', '--quiet'); run('symbolic-ref', 'HEAD', 'refs/heads/' + branch); run('remote', 'add', 'origin', remote)
        else:
            detail = found.stderr.strip()
            if token_env:
                for secret in [token, base64.b64encode(('x-access-token:' + token).encode()).decode()]: detail = detail.replace(secret, '[redacted]')
            raise ValueError('Cannot inspect the distribution remote (exit ' + str(found.returncode) + '): ' + detail[-500:])
    if run('status', '--porcelain').stdout.strip(): raise ValueError('Use a clean distribution checkout; preserve existing changes.')
    if run('remote', 'get-url', 'origin').stdout.strip() != remote or run('symbolic-ref', '--short', 'HEAD').stdout.strip() != branch: raise ValueError('Wrong distribution remote or branch.')
    old_path = checkout / 'distribution-manifest.json'; old = read(old_path) if old_path.exists() else {'files': [], 'plugins': []}
    for previous in old['plugins']:
        current = next((p for p in incoming['plugins'] if p['name'] == previous['name']), None)
        if current and current['version'] == previous['version'] and current['payloadSha256'] != previous['payloadSha256']:
            raise ValueError('Bump the changed plugin version before replacing an immutable release: ' + current['name'])
    old_files = {p['path']: p['sha256'] for p in old['files']}; new_files = {p['path']: p['sha256'] for p in incoming['files']}
    for name, digest in old_files.items():
        target = contained(checkout, name)
        if target.exists() and sha(target.read_bytes()) != digest: raise ValueError('Preserve manually changed distribution file: ' + name)
        if name not in new_files and target.exists(): target.unlink()
    for name in [*new_files, 'distribution-manifest.json']:
        destination = contained(checkout, name); destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and name not in old_files and name != 'distribution-manifest.json' and destination.read_bytes() != (build_root / name).read_bytes(): raise ValueError('Refuse to overwrite an unmanaged file.')
        shutil.copyfile(build_root / name, destination)
    paths = sorted({*old_files, *new_files, 'distribution-manifest.json'})
    spec = checkout.parent / (checkout.name + '-stage.paths'); spec.write_bytes(b'\0'.join(p.encode() for p in paths) + b'\0')
    run('--literal-pathspecs', 'add', '--pathspec-from-file=' + str(spec.resolve()), '--pathspec-file-nul')
    changed = run('diff', '--cached', '--quiet', check=False).returncode != 0
    if changed:
        name = git(REPO, 'config', 'user.name', check=False).stdout.strip() or 'Skills Marketplace'
        email = git(REPO, 'config', 'user.email', check=False).stdout.strip() or '41898282+github-actions[bot]@users.noreply.github.com'
        run('config', 'user.name', name); run('config', 'user.email', email)
        run('commit', '-m', 'Publish marketplace from ' + incoming['sourceCommit'][:12])
        run('push', 'origin', 'HEAD:' + branch)
    return {'ok': True, 'changed': changed, 'branch': branch, 'commit': run('rev-parse', 'HEAD').stdout.strip(), 'plugins': result['plugins']}


def add(catalog_path, name, source, display_name, description, category):
    data = read(catalog_path)
    if any(e['name'] == name for e in data['plugins']): raise ValueError('Plugin already exists in the registry.')
    folder = contained(REPO, source); manifest = read(folder / '.codex-plugin/plugin.json')
    if manifest['name'] != name or not manifest.get('version'): raise ValueError('Supply an actual matching native plugin manifest.')
    if not git(REPO, 'ls-files', '--', source + '/.codex-plugin/plugin.json').stdout.strip(): raise ValueError('Track the plugin authoring source before adding it to the registry.')
    data['plugins'].append({'name': name, 'displayName': display_name, 'description': description, 'category': category, 'kind': 'directory', 'path': source})
    entries(data); write(catalog_path, data)
    return {'ok': True, 'added': name, 'catalog': str(catalog_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build'); p.add_argument('--repo', type=Path, default=REPO); p.add_argument('--ref', default='HEAD'); p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('check'); p.add_argument('--root', type=Path, required=True)
    p = sub.add_parser('publish'); p.add_argument('--root', type=Path, required=True); p.add_argument('--checkout', type=Path, required=True); p.add_argument('--remote', default='https://github.com/gvillarroel/skills.git'); p.add_argument('--branch', default='marketplace'); p.add_argument('--token-env')
    p = sub.add_parser('add'); p.add_argument('--catalog', type=Path, default=PROJECT / 'catalog.json'); p.add_argument('--name', required=True); p.add_argument('--source', required=True); p.add_argument('--display-name', required=True); p.add_argument('--description', required=True); p.add_argument('--category', default='Productivity')
    args = parser.parse_args()
    try:
        if args.command == 'build': result = build(args.repo.resolve(), args.ref, args.output.resolve())
        elif args.command == 'check': result = check(args.root.resolve())
        elif args.command == 'publish': result = publish(args.root.resolve(), args.checkout.resolve(), args.remote, args.branch, args.token_env)
        else: result = add(args.catalog, args.name, args.source, args.display_name, args.description, args.category)
        print(json.dumps(result)); return 0
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({'ok': False, 'error': str(error)})); return 2


if __name__ == '__main__': raise SystemExit(main())
