#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify real media assembly, quiet-tail preservation and portable cache integrity."""
import array
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
import zipfile
from pathlib import Path
from unittest.mock import patch
from project_delivery import RATE, assemble, bundle, local, prepare, probe, save, sha


class DeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(); cls.base = Path(cls.fixture.name)
        for name, color in [('first', 'white'), ('second', 'gray')]:
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', f'color=c={color}:s=320x180:r=30:d=1', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(cls.base / (name + '.mp4'))], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls): cls.fixture.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(); self.root = Path(self.temporary.name) / "a user's film"; self.root.mkdir()
        (self.root / 'clips').mkdir()
        for index, name in enumerate(['first', 'second'], 1): shutil.copyfile(self.base / (name + '.mp4'), self.root / f'clips/{index:02d}-{name}.mp4')
        self.voice = self.root / 'voice.wav'; self.write_voice()
        self.request = self.root / 'assembly.json'
        self.value = {'fps': 30, 'voice': {'file': 'voice.wav', 'provenance': 'Synthetic deterministic audio fixture, not generated speech'}, 'scenes': [{'id': name, 'clip': f'clips/{i:02d}-{name}.mp4', 'voiceSeconds': 1} for i, name in enumerate(['first', 'second'], 1)]}
        save(self.request, self.value)
        self.output, self.report = self.root / 'complete.mp4', self.root / 'report.json'

    def tearDown(self): self.temporary.cleanup()

    def write_voice(self, tail=0):
        samples = array.array('h', [800 if (i // 100) % 2 else -800 for i in range(2 * RATE * 2)])
        samples.extend([1] * round(tail * RATE * 2))
        with wave.open(str(self.voice), 'wb') as wav:
            wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(RATE); wav.writeframes(samples.tobytes())

    def test_actual_assembly_preserves_frames_and_declares_local_provenance(self):
        result = assemble(self.request, self.output, self.report)
        self.assertEqual(result['frames'], 60); self.assertFalse(result['nativeGoogleVidsExport'])
        self.assertEqual(result['deliveryKind'], 'local-assembly')
        self.assertEqual({s['codec_type'] for s in probe(self.output)['streams']}, {'audio', 'video'})
        self.assertEqual([s['voiceSamples'] for s in result['scenes']], [RATE, RATE])

    def test_unchanged_output_reuses_without_media_commands(self):
        first = assemble(self.request, self.output, self.report)
        with patch('project_delivery.run', side_effect=AssertionError('Cached bytes should not be decoded again.')):
            again = assemble(self.request, self.output, self.report)
        self.assertTrue(again['reused']); self.assertEqual(first['videoSha256'], again['videoSha256'])
        self.assertTrue(json.loads(self.report.read_text())['reused'])

    def test_corrupt_output_requires_explicit_owned_replacement(self):
        assemble(self.request, self.output, self.report); self.output.write_bytes(b'broken')
        with self.assertRaisesRegex(ValueError, 'matching cache'): assemble(self.request, self.output, self.report)
        self.assertFalse(assemble(self.request, self.output, self.report, replace=True)['reused'])

    def test_speech_budget_failure_keeps_existing_output(self):
        self.value['scenes'][0]['voiceSeconds'] = 1.1; self.value['scenes'][1]['voiceSeconds'] = .9; save(self.request, self.value)
        self.output.write_bytes(b'previous approved output')
        with self.assertRaisesRegex(ValueError, 'exceeds clip budget'): assemble(self.request, self.output, self.report, replace=True)
        self.assertEqual(self.output.read_bytes(), b'previous approved output')

    def test_quiet_nonzero_container_tail_is_preserved(self):
        self.write_voice(.06)
        result = assemble(self.request, self.output, self.report)
        self.assertEqual(result['frames'], 62); self.assertEqual(result['scenes'][-1]['voiceSamples'], round(1.06 * RATE))
        self.assertEqual(result['discardedZeroTailSamples'], 0)

    def test_wrong_clock_is_rejected(self):
        self.value['fps'] = 25; save(self.request, self.value)
        with self.assertRaisesRegex(ValueError, 'frame rate'): assemble(self.request, self.output, self.report)

    def test_prepare_rejects_reordered_observed_reference(self):
        story, observed = self.root / 'story.json', self.root / 'observed.json'
        save(story, {'scenes': [{'id': 'first', 'clipSeconds': 1}, {'id': 'second', 'clipSeconds': 1}]})
        save(observed, {'scenes': [{'id': 'second', 'sceneSeconds': 1}, {'id': 'first', 'sceneSeconds': 1}]})
        with self.assertRaisesRegex(ValueError, 'order'): prepare(story, observed, self.voice, self.root / 'clips', self.request, 'Fixture')

    def test_portable_bundle_reassembles_in_clean_directory(self):
        archive, report = self.root / 'sources.zip', self.root / 'bundle.json'
        result = bundle(self.request, archive, report, [])
        self.assertTrue(bundle(self.request, archive, report, [])['reused'])
        clean = self.root / 'clean'; clean.mkdir()
        with zipfile.ZipFile(archive) as zipped: zipped.extractall(clean)
        manifest = json.loads((clean / 'source-manifest.json').read_text(encoding='utf-8'))
        self.assertTrue(all(sha(clean / r['path']) == r['sha256'] for r in manifest['files']))
        subprocess.run([sys.executable, str(clean / 'tools/project_delivery.py'), 'assemble', '--request', str(clean / 'assembly.json'), '--output', str(clean / 'rebuilt.mp4'), '--report', str(clean / 'rebuilt.json')], check=True, capture_output=True)
        self.assertEqual(json.loads((clean / 'rebuilt.json').read_text())['frames'], 60)
        self.assertFalse(result['nativeGoogleVidsExport'])

    def test_renamed_optional_source_invalidates_bundle_cache(self):
        archive, report = self.root / 'sources.zip', self.root / 'bundle.json'
        (self.root / 'credit.txt').write_text('Credit'); bundle(self.request, archive, report, ['credit.txt'])
        (self.root / 'renamed.txt').write_text('Credit')
        with self.assertRaisesRegex(ValueError, 'immutable'): bundle(self.request, archive, report, ['renamed.txt'])

    def test_outputs_cannot_overwrite_voice_or_request(self):
        with self.assertRaisesRegex(ValueError, 'inputs'): assemble(self.request, self.voice, self.report)
        with self.assertRaisesRegex(ValueError, 'inputs'): bundle(self.request, self.root / 'source.zip', self.voice, [])

    def test_parent_traversal_cannot_enter_bundle(self):
        for path in ['../secret', 'C:/secret', '/secret']:
            with self.assertRaisesRegex(ValueError, 'relative'): local(self.root, path)


if __name__ == '__main__': unittest.main()
