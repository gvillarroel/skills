#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test delivery failures, numbered clips, real media caching and stale receipts."""
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from batch_clips import atomic_json, sha
from vids_delivery import assess, cloud_file_id, finalize, revision, safe_outputs, template
from vids_plan import verify_export

PROJECT = 'https://docs.google.com/videos/d/fixture-project/edit'
MOVIE = 'https://drive.google.com/file/d/fixture-export/view'


def fixture(story, base, media, digest):
    receipt = template(story, base)
    receipt['project'].update(url=PROJECT, observed=True, saved=True, evidence='Synthetic fixture: saved project observed.')
    receipt['inventory'].update(observed=True)
    for row in receipt['inventory']['scenes']:
        row.update(visualReviewed=True, announcement='Scene 1 of 1, duration 2 seconds Alt text title: 01-method.mp4 Has speaker notes 1 objects on the page 1 audio clip starts in the scene Selected')
    receipt['export'].update(observed=True, projectUrl=PROJECT, localSha256=digest, evidence='Synthetic fixture: native complete export observed.')
    receipt['cloud'].update(observed=True, metadata={'id': 'fixture-export', 'mimeType': 'video/mp4', 'size': str(media['bytes']), 'webViewLink': MOVIE},
                            playbackObserved=True, downloadObserved=True, durationSeconds=2, evidence='Synthetic fixture: same exported file played; Download enabled.')
    receipt['review'].update(observed=True, speechAndJoins=True, contentThroughout=True, evidence='Synthetic fixture: film reviewed throughout.')
    return receipt


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.story = {'projectTitle': 'Delivery fixture', 'googleVidsUrl': PROJECT, 'width': 320, 'height': 180,
                      'scenes': [{'id': 'method', 'script': 'Explain the method.', 'clip': '01-method.mp4', 'clipSeconds': 2}]}
        self.media = {'ok': True, 'checks': {k: True for k in ('videoPresent', 'audioPresent', 'fullDecode', 'durationMatches')},
                      'bytes': 12345, 'duration': 2.04, 'width': 320, 'height': 180}
        self.rev = revision(self.story, Path.cwd())
        self.evidence = fixture(self.story, Path.cwd(), self.media, 'abc')

    def report(self, evidence=None, media=None, digest='abc'):
        return assess(self.story, evidence or self.evidence, media or self.media, digest, self.rev)

    def test_complete_receipt_and_numbered_filename(self):
        report = self.report(); self.assertTrue(report['ok']); self.assertEqual(report['videoUrl'], MOVIE)

    def test_unobserved_template_cannot_be_delivery(self):
        report = self.report(template(self.story, Path.cwd())); self.assertFalse(report['ok']); self.assertEqual(report['status'], 'native-scenes-incomplete')

    def test_voice_only_project_fails_native_visual_gate(self):
        self.evidence['inventory']['scenes'][0].update(announcement='Scene 1 of 1, duration 2 seconds 0 objects on the page 1 audio clip starts in the scene Selected', visualReviewed=False)
        self.assertFalse(self.report()['checks']['nativeSceneInventory'])

    def test_stale_revision_and_wrong_project(self):
        self.evidence['revision'] = 'old'; self.evidence['project']['url'] = PROJECT.replace('fixture-project', 'wrong-project')
        report = self.report(); self.assertFalse(report['checks']['currentRevision']); self.assertFalse(report['checks']['nativeProjectSaved'])

    def test_new_local_bytes_cannot_reuse_export_receipt(self):
        self.assertFalse(self.report(digest='changed')['checks']['downloadedBytesBound'])

    def test_metadata_id_type_size_and_url_must_match(self):
        for key, value in [('id', 'wrong-id'), ('mimeType', 'application/pdf'), ('size', '99'), ('webViewLink', 'https://example.org/file')]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.evidence); data['cloud']['metadata'][key] = value
                self.assertFalse(self.report(data)['checks']['cloudFileMetadata'])

    def test_normalized_connector_metadata_is_accepted(self):
        self.evidence['cloud']['metadata'] = {'id': 'fixture-export', 'mime_type': 'video/mp4', 'size': 12345, 'url': MOVIE}
        self.assertTrue(self.report()['ok'])

    def test_rounded_player_clock_is_accepted_but_wrong_length_is_not(self):
        self.assertTrue(self.report()['checks']['cloudPlayback'])
        self.evidence['cloud']['durationSeconds'] = 20
        self.assertFalse(self.report()['checks']['cloudPlayback'])

    def test_playback_and_download_are_independent_observations(self):
        self.evidence['cloud']['playbackObserved'] = False
        self.evidence['cloud']['downloadObserved'] = False
        report = self.report(); self.assertEqual(report['status'], 'cloud-delivery-needed'); self.assertEqual(len(report['pending']), 2)

    def test_speech_and_content_review_are_required(self):
        self.evidence['review']['speechAndJoins'] = False
        self.assertEqual(self.report()['status'], 'review-needed')

    def test_signed_download_urls_are_not_delivery_links(self):
        self.assertIsNone(cloud_file_id('https://download.example.org/file?token=secret'))
        self.assertIsNone(cloud_file_id(MOVIE + '?access_token=secret'))

    def test_audio_and_decode_failures_are_material(self):
        for field in ('audioPresent', 'fullDecode', 'durationMatches'):
            media = copy.deepcopy(self.media); media['checks'][field] = False
            self.assertFalse(self.report(media=media)['checks']['localExportVerified'])

    def test_authored_inputs_and_skill_are_read_only(self):
        source = Path(__file__).resolve()
        with self.assertRaises(ValueError): safe_outputs([source.parent / 'generated.json'], [])
        with self.assertRaises(ValueError): safe_outputs([Path.cwd() / 'story.json'], [Path.cwd() / 'story.json'])


class MediaTests(unittest.TestCase):
    def setUp(self):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            self.skipTest('FFmpeg is required for real media verification.')
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd()); self.root = Path(self.temp.name)
        self.video = self.root / '01-method.mp4'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=white:s=320x180:r=30:d=2',
                        '-f', 'lavfi', '-i', 'sine=frequency=440:duration=2', '-vf', 'drawbox=x=40:y=40:w=180:h=60:color=gray:t=fill',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(self.video)], capture_output=True, check=True)
        self.story = {'projectTitle': 'Media fixture', 'googleVidsUrl': PROJECT, 'width': 320, 'height': 180,
                      'scenes': [{'id': 'method', 'script': 'Explain the method.', 'clip': self.video.name, 'clipSeconds': 2}]}
        self.timing = {'ok': True, 'status': 'measured-native-timing', 'duration': 2, 'fps': 30}
        self.story_path = self.root / 'story.json'; self.timing_path = self.root / 'timing.json'
        self.receipt = self.root / 'evidence.json'; self.report = self.root / 'delivery.json'
        atomic_json(self.story_path, self.story); atomic_json(self.timing_path, self.timing)
        atomic_json(self.receipt, fixture(self.story, self.root, {'bytes': self.video.stat().st_size}, sha(self.video)))

    def tearDown(self):
        if hasattr(self, 'temp'): self.temp.cleanup()

    def run_check(self):
        return finalize(self.story_path, self.timing_path, self.receipt, self.video, self.report)

    def test_real_decode_then_cached_check(self):
        with patch('vids_delivery.verify_export', wraps=verify_export) as verify:
            first = self.run_check(); second = self.run_check()
            self.assertTrue(first['ok']); self.assertFalse(first['mediaCheckReused']); self.assertTrue(second['mediaCheckReused'])
            self.assertEqual(verify.call_count, 1)
        text = self.report.with_suffix('.md').read_text(); self.assertIn(MOVIE, text); self.assertNotIn('C:/', text)

    def test_edit_invalidates_receipt_and_measurement_cache(self):
        self.run_check(); self.story['scenes'][0]['script'] = 'A revised explanation.'; atomic_json(self.story_path, self.story)
        self.assertFalse(self.run_check()['checks']['currentRevision'])
        self.timing['duration'] = 20; atomic_json(self.timing_path, self.timing)
        changed = self.run_check(); self.assertFalse(changed['mediaCheckReused']); self.assertFalse(changed['checks']['localExportVerified'])

    def test_missing_video_stays_incomplete(self):
        self.video.unlink(); result = self.run_check(); self.assertFalse(result['ok']); self.assertFalse(result['checks']['localExportVerified'])

    def test_corrupt_cache_recovers_and_receipt_is_preserved(self):
        original = self.receipt.read_bytes(); self.run_check(); self.report.with_name('delivery-media.json').write_text('broken')
        self.assertFalse(self.run_check()['mediaCheckReused']); self.assertEqual(original, self.receipt.read_bytes())


if __name__ == '__main__':
    unittest.main()
