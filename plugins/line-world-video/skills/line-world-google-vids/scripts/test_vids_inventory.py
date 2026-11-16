#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise extra blank scenes, stale announcements, ordered clips and timing."""
import unittest
from vids_inventory import inspect,parse_announcement

def scene(order,total,seconds,name=None):
    media=f' Alt text title: {name}.mp4 Has speaker notes 1 objects on the page 1 audio clip starts in the scene (Voice - Nyla)' if name else ' 0 objects on the page'
    return {'order':order,'announcement':f'Scene {order} of {total}, duration {seconds} seconds'+media+' Selected'}

class InventoryTests(unittest.TestCase):
    def setUp(self):self.story={'scenes':[{'id':'a','clipSeconds':1},{'id':'b','clipSeconds':2}]}
    def test_correct_fresh_inventory(self):
        report=inspect(self.story,{'sceneButtonCount':2,'scenes':[scene(1,2,1,'a'),scene(2,2,2,'b')]});self.assertTrue(report['ok']);self.assertEqual(report['totalSceneSeconds'],3)
    def test_inserted_blank_scene_is_found_without_cascading_order_noise(self):
        report=inspect(self.story,{'sceneButtonCount':3,'scenes':[scene(1,3,1,'a'),scene(2,3,5),scene(3,3,2,'b')]});self.assertFalse(report['ok']);self.assertEqual(report['emptyVisualScenes'],1);self.assertEqual([f['kind'] for f in report['findings']],['scene-count-mismatch','empty-visual-scene'])
    def test_stale_ten_of_ten_cannot_validate_eleven_buttons(self):
        report=inspect(self.story,{'sceneButtonCount':3,'scenes':[scene(1,2,1,'a'),scene(2,2,2,'b')]});self.assertTrue(any(f['kind']=='stale-or-mismatched-announcement' for f in report['findings']))
    def test_wrong_media_and_scene_extent_are_rejected(self):
        wrong=inspect(self.story,{'sceneButtonCount':2,'scenes':[scene(1,2,1,'b'),scene(2,2,2,'a')]});self.assertTrue(any(f['kind']=='ordered-media-mismatch' for f in wrong['findings']))
        extent=inspect(self.story,{'sceneButtonCount':2,'scenes':[scene(1,2,1,'a'),scene(2,2,7,'b')]});self.assertTrue(any(f['kind']=='scene-extent-mismatch' for f in extent['findings']))
    def test_actual_native_minutes_and_milliseconds(self):
        record=parse_announcement('Scene 1 of 1, duration 1 minute 2 seconds 400 milliseconds Alt text title: clip.mp4 Has speaker notes 1 objects on the page Selected');self.assertEqual(record['sceneSeconds'],62.4)
        with self.assertRaisesRegex(ValueError,'fresh English'):parse_announcement('Scene 1 of 1 Selected')

if __name__=='__main__':unittest.main()
