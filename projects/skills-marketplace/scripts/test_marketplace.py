#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise Git-snapshot builds, integrity checks and non-destructive publication."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('marketplace', Path(__file__).with_name('marketplace.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
BASE = m.PROJECT / 'artifacts/tests'


class MarketplaceTests(unittest.TestCase):
    def setUp(self):
        BASE.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix='registry-', dir=BASE)).resolve()
        self.repo = self.root / 'source'; self.repo.mkdir()
        (self.repo / '.gitignore').write_text('**/artifacts/\n', encoding='utf-8')
        self.project = self.repo / 'projects/skills-marketplace'; self.project.mkdir(parents=True)
        self.folder = self.repo / 'projects/demo/plugin'
        m.write(self.folder / '.codex-plugin/plugin.json', {'name': 'demo', 'version': '1.0.0', 'description': 'A fixture.', 'skills': './skills/'})
        skill = self.folder / 'skills/demo/SKILL.md'; skill.parent.mkdir(parents=True)
        skill.write_bytes(b'---\nname: demo\ndescription: A fixture.\n---\n\nUse this synthetic fixture.\n')
        self.catalog = {'schemaVersion': 1, 'name': 'test-market', 'displayName': 'Test Market', 'repository': 'unused', 'distributionBranch': 'marketplace', 'plugins': [{'name': 'demo', 'kind': 'directory', 'path': 'projects/demo/plugin', 'displayName': 'Demo', 'description': 'A fixture.', 'category': 'Creativity'}]}
        m.write(self.project / 'catalog.json', self.catalog)
        m.git(self.repo, 'init', '--quiet'); m.git(self.repo, 'config', 'user.name', 'Marketplace Fixture'); m.git(self.repo, 'config', 'user.email', 'fixture@example.invalid')
        self.commit()
        self.context = patch.multiple(m, REPO=self.repo, PROJECT=self.project); self.context.start(); self.addCleanup(self.context.stop)

    def commit(self):
        m.git(self.repo, 'add', '.'); m.git(self.repo, 'commit', '--quiet', '-m', 'Fixture source')

    def build(self, name='build'): return m.build(self.repo, 'HEAD', self.project / 'artifacts' / name)

    def test_committed_snapshot_ignores_dirty_inputs_and_reuses_exact_build(self):
        (self.folder / 'skills/demo/SKILL.md').write_text('Dirty unpublished input.', encoding='utf-8')
        result = self.build(); root = self.project / 'artifacts/build'
        self.assertEqual(result['plugins'][0]['version'], '1.0.0')
        self.assertIn('synthetic fixture', (root / 'plugins/demo/skills/demo/SKILL.md').read_text())
        self.assertTrue(self.build()['reused'])
        catalog = m.read(root / '.agents/plugins/marketplace.json')
        self.assertEqual(catalog['plugins'][0]['source']['path'], './plugins/demo')

    def test_integrity_rejects_changed_and_unlisted_files(self):
        self.build(); root = self.project / 'artifacts/build'
        extra = root / 'extra.txt'; extra.write_text('Unlisted', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'inventory'): m.check(root)
        extra.unlink()
        (root / 'plugins/demo/skills/demo/SKILL.md').write_text('Changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Changed distribution'): m.check(root)

    def test_registry_rejects_duplicate_ignored_and_escaping_inputs(self):
        self.catalog['plugins'].append(dict(self.catalog['plugins'][0]))
        with self.assertRaisesRegex(ValueError, 'unique'): m.entries(self.catalog)
        self.catalog['plugins'].pop()
        for path in ['projects/demo/artifacts/plugin', '../other', 'C:/other', 'projects/demo/../other']:
            self.catalog['plugins'][0]['path'] = path
            with self.assertRaises(ValueError): m.entries(self.catalog)

    def test_add_checks_tracked_native_identity(self):
        second = self.repo / 'projects/second/plugin'
        m.write(second / '.codex-plugin/plugin.json', {'name': 'second', 'version': '1.0.0'})
        args = (self.project / 'catalog.json', 'second', 'projects/second/plugin', 'Second', 'Fixture.', 'Creativity')
        with self.assertRaisesRegex(ValueError, 'Track'): m.add(*args)
        m.git(self.repo, 'add', 'projects/second')
        self.assertTrue(m.add(*args)['ok'])
        with self.assertRaisesRegex(ValueError, 'already exists'): m.add(*args)

    def test_publish_fast_forward_immutable_versions_and_preserved_authored_files(self):
        remote = self.root / 'remote.git'
        subprocess.run(['git', 'init', '--bare', '--quiet', str(remote)], check=True, capture_output=True)
        self.build(); build = self.project / 'artifacts/build'; checkout = self.project / 'artifacts/distribution'
        first = m.publish(build, checkout, str(remote), 'marketplace')
        self.assertTrue(first['changed'])
        self.assertFalse(m.publish(build, checkout, str(remote), 'marketplace')['changed'])
        authored = checkout / 'maintainer-note.md'; authored.write_text('Keep this authored note.\n', encoding='utf-8')
        m.git(checkout, 'add', 'maintainer-note.md'); m.git(checkout, 'commit', '--quiet', '-m', 'Keep authored note'); m.git(checkout, 'push', 'origin', 'HEAD:marketplace')
        (self.folder / 'skills/demo/SKILL.md').write_text('Changed fixture.\n', encoding='utf-8'); self.commit(); self.build('changed')
        with self.assertRaisesRegex(ValueError, 'immutable'): m.publish(self.project / 'artifacts/changed', checkout, str(remote), 'marketplace')
        native = self.folder / '.codex-plugin/plugin.json'; data = m.read(native); data['version'] = '1.0.1'; m.write(native, data)
        self.commit(); self.build('next')
        next_release = m.publish(self.project / 'artifacts/next', checkout, str(remote), 'marketplace')
        self.assertTrue(next_release['changed']); self.assertTrue(authored.exists())
        self.assertEqual(m.git(checkout, 'rev-parse', first['commit'] + '^', check=False).returncode, 128)
        self.assertEqual(m.git(checkout, 'merge-base', '--is-ancestor', first['commit'], next_release['commit']).returncode, 0)
        authored.write_text('Unsaved author change.\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'clean'): m.publish(self.project / 'artifacts/next', checkout, str(remote), 'marketplace')


if __name__ == '__main__': unittest.main()
