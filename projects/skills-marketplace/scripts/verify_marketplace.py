#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Install a marketplace with the real Codex loader in an isolated task-local home."""
import argparse
import hashlib
import json
import os
import queue
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, value): path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def discover(binary, environment, cwd, installed, work):
    events = []; messages = queue.Queue()
    with (work / 'app-server.stderr.txt').open('w', encoding='utf-8') as stderr:
        proc = subprocess.Popen([binary, 'app-server'], cwd=cwd, env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr, text=True, encoding='utf-8')
        def reader():
            for line in proc.stdout: messages.put(line)
        threading.Thread(target=reader, daemon=True).start()
        def send(value): proc.stdin.write(json.dumps(value) + '\n'); proc.stdin.flush()
        def request(number, method, params):
            send({'id': number, 'method': method, 'params': params})
            while True:
                value = json.loads(messages.get(timeout=40)); events.append(value)
                if value.get('id') == number:
                    if 'error' in value: raise ValueError('Native discovery failed: ' + str(value['error']))
                    return value['result']
        try:
            request(1, 'initialize', {'clientInfo': {'name': 'skills_marketplace_check', 'version': '1.0.0'}, 'capabilities': {'experimentalApi': True}})
            send({'method': 'initialized'})
            result = request(2, 'skills/list', {'cwds': [str(cwd)], 'forceReload': True}); found = []
            for group in result.get('data', []):
                for skill in group.get('skills', []):
                    path = Path(skill.get('path', '')).resolve()
                    for name, root in installed.items():
                        if path.is_relative_to(root): found.append({'plugin': name, 'name': skill['name'], 'path': str(path), 'enabled': skill.get('enabled', True)})
            return found
        finally:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait()
            proc.stdin.close(); proc.stdout.close(); save(work / 'app-server-events.json', events)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Expected checked distribution.')
    parser.add_argument('--source', help='Local directory or remote owner/repo. Defaults to --root.')
    parser.add_argument('--ref', help='Remote Git reference, for example marketplace.')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); output = args.output.resolve()
    if not output.is_relative_to((PROJECT / 'artifacts').resolve()): raise ValueError('Keep native verification inside project artifacts.')
    output.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='native-', dir=output)); home = work / 'codex-home'; home.mkdir(); temp = work / 'tmp'; temp.mkdir()
    environment = {**os.environ, 'CODEX_HOME': str(home), 'TMP': str(temp), 'TEMP': str(temp)}
    binary = shutil.which('codex.cmd') or shutil.which('codex')
    report = {'ok': False, 'modelTurns': 0, 'source': args.source or str(args.root.resolve()), 'ref': args.ref, 'workdir': str(work), 'commands': [], 'installed': []}
    try:
        if not binary: raise ValueError('Install Codex CLI before running native verification.')
        manifest = read(args.root / 'distribution-manifest.json'); name = manifest['name']; expected = {p['name']: p for p in manifest['plugins']}
        def run(arguments):
            result = subprocess.run([binary, *arguments], cwd=work, env=environment, capture_output=True, text=True, encoding='utf-8', timeout=60)
            n = len(report['commands']); (work / f'command-{n}.stdout.txt').write_text(result.stdout, encoding='utf-8'); (work / f'command-{n}.stderr.txt').write_text(result.stderr, encoding='utf-8')
            report['commands'].append({'args': arguments, 'exitCode': result.returncode})
            if result.returncode: raise ValueError('Codex command failed: ' + ' '.join(arguments))
            return result.stdout
        report['codexVersion'] = run(['--version']).strip()
        command = ['plugin', 'marketplace', 'add', report['source'], '--json']
        if args.ref: command += ['--ref', args.ref]
        run(command)
        available = json.loads(run(['plugin', 'list', '--available', '--marketplace', name, '--json']))
        report['available'] = available
        installed = {}
        for plugin_name, expected_plugin in expected.items():
            result = json.loads(run(['plugin', 'add', plugin_name + '@' + name, '--json']))
            folder = Path(result['installedPath']).resolve(); installed[plugin_name] = folder
            native = read(folder / '.codex-plugin/plugin.json')
            if native['version'] != expected_plugin['version']: raise ValueError('Installed version differs from the expected release.')
            for item in read(args.root / 'plugins' / plugin_name / 'bundle-manifest.json')['files']:
                actual = folder / item['path']
                if not actual.is_file() or digest(actual) != item['sha256']: raise ValueError('Installed bytes differ from the checked release: ' + item['path'])
            report['installed'].append({'name': plugin_name, 'version': native['version'], 'bytesMatch': True})
        listing = json.loads(run(['plugin', 'list', '--marketplace', name, '--json']))
        if any(not next((v.get('enabled') for v in listing['installed'] if v['name'] == n), False) for n in expected): raise ValueError('An installed plugin is not enabled.')
        cwd = work / 'project'; cwd.mkdir(); subprocess.run(['git', 'init', '--quiet', str(cwd)], check=True, capture_output=True)
        found = discover(binary, environment, cwd, installed, work); report['nativeSkills'] = found
        for plugin_name, folder in installed.items():
            wanted = sorted(p.parent.name for p in (folder / 'skills').glob('*/SKILL.md'))
            observed = sorted(Path(s['path']).parent.name for s in found if s['plugin'] == plugin_name and s['enabled'])
            if wanted != observed: raise ValueError('Native skill discovery omitted plugin skills: ' + plugin_name)
        report['ok'] = True
    except Exception as error: report['error'] = str(error)
    report['scope'] = 'Actual native marketplace registration, installation, payload equality and app-server skill discovery. Uses a project-local home, no model turns and no desktop UI activation.'
    save(work / 'verification.json', report); save(output / 'verification.json', report)
    print(json.dumps({'ok': report['ok'], 'report': str(output / 'verification.json'), 'plugins': report['installed'], 'skills': len(report.get('nativeSkills', [])), 'error': report.get('error')}))
    return 0 if report['ok'] else 2


if __name__ == '__main__': raise SystemExit(main())
