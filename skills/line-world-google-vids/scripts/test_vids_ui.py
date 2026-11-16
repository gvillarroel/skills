#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise pure UI recommendations with synthetic fresh and delayed observations."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

PROJECT = 'https://docs.google.com/videos/d/fixture-project/edit'
AX = ('0 document Example Value: ' + PROJECT + '\n'
      '10 button Scene 1 of 2\n11 button Scene 2 of 2\n'
      '12 text Scene 1 of 2, duration 2 seconds Alt text title: old.mp4 1 objects on the page Selected\n'
      '13 button Insert\n14 menu item Upload u\n15 text Document status: Saved to Drive')


class UITests(unittest.TestCase):
    def call(self, **patch):
        if not shutil.which('node'):
            self.skipTest('Node is required for the pure JS parser.')
        data = {'ax': AX, 'fullState': True, 'foreground': True, 'phase': 'select',
                'target': {'projectUrl': PROJECT, 'sceneOrder': 1, 'file': 'C:/film/01-method.mp4'}}
        data.update(patch)
        runtime = Path(__file__).resolve().parent.parent / 'assets/runtime/vids-ui.js'
        js = "const p=require(process.argv[1]);process.stdout.write(JSON.stringify(p.uploadNext(JSON.parse(require('node:fs').readFileSync(0,'utf8')))))"
        result = subprocess.run(['node', '-e', js, str(runtime)], input=json.dumps(data), capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def test_diff_needs_full_state(self):
        self.assertEqual(self.call(fullState=False)['kind'], 'read-full-state')

    def test_wrong_project_never_uploads(self):
        self.assertEqual(self.call(ax=AX.replace('fixture-project', 'other-project'))['kind'], 'verify-project')

    def test_background_tab_must_be_observed_foreground(self):
        self.assertEqual(self.call(foreground=False)['kind'], 'foreground-tab')

    def test_current_selection_is_required(self):
        result = self.call(target={'projectUrl': PROJECT, 'sceneOrder': 2, 'file': 'C:/film/02.mp4'})
        self.assertEqual((result['kind'], result['index']), ('select-scene', 11))

    def test_selected_scene_can_open_observed_upload(self):
        self.assertEqual(self.call()['kind'], 'open-upload')

    def test_native_open_dialog_uses_keyboard_not_cached_index(self):
        result = self.call(phase='await-dialog', nativeOpenDialogObserved=True)
        self.assertEqual(result['kind'], 'fill-native-filename'); self.assertNotIn('index', result)
        self.assertEqual(result['keys'][0], 'Alt_L+n')

    def test_delayed_dialog_and_media_do_not_double_insert(self):
        for phase in ('await-dialog', 'await-insertion'):
            self.assertEqual(self.call(phase=phase)['kind'], 'observe-upload-result')

    def test_inserted_media_from_selected_scene_triggers_pixel_and_audio_review(self):
        result = self.call(phase='await-insertion', ax=AX.replace('old.mp4', '01-method.mp4'))
        self.assertEqual(result['kind'], 'verify-inserted-scene'); self.assertEqual(len(result['checks']), 3)
    def test_filename_elsewhere_in_timeline_does_not_validate_selected_media(self):
        result = self.call(phase='await-insertion', ax=AX+'\n99 container Alt text title: 01-method.mp4')
        self.assertEqual(result['kind'], 'observe-upload-result')

    def test_policy_stop_takes_priority(self):
        self.assertEqual(self.call(policyStopped=True, fullState=False)['kind'], 'stop')

    def test_unknown_selection_does_not_guess_from_playhead(self):
        self.assertEqual(self.call(ax=AX.replace(' Selected', ''))['kind'], 'select-scene')


if __name__ == '__main__':
    unittest.main()
