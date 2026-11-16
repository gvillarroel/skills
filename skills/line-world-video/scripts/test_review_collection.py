#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise collection provenance, stale decisions and actual encoded review reuse."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from review_collection import manual_status,normalize_story,review,save,validate_entries


class CollectionTests(unittest.TestCase):
    def test_accepts_authored_scene_and_core_beat_clocks(self):
        self.assertEqual(normalize_story({'beats':[{'id':'a','duration':4}]})['scenes'][0]['clipSeconds'],4)
        self.assertEqual(normalize_story({'scenes':[{'id':'b','clipSeconds':7}]})['scenes'][0]['clipSeconds'],7)

    def test_ambiguous_current_versions_and_duplicate_ids_are_rejected(self):
        for entries in [[{'id':'a','production':'film'},{'id':'b','production':'film'}],[{'id':'a'},{'id':'a','role':'reference'}]]:
            with self.assertRaises(ValueError):validate_entries(entries)
        validate_entries([{'id':'a','production':'film'},{'id':'b','production':'film','role':'reference'}])

    def test_manual_observations_bind_movie_source_and_complete_scenes(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'manual.json';scene=[{'id':'a'}]
            self.assertEqual(manual_status(p,'movie','source',scene),'pending')
            save(p,{'videoSha256':'movie','sourceSha256':'source','scenes':[{'id':'a','reviewed':True,'notes':'Observed readable pose.'}]})
            self.assertEqual(manual_status(p,'movie','source',scene),'recorded')
            self.assertEqual(manual_status(p,'changed','source',scene),'stale')
            self.assertEqual(manual_status(p,'movie','changed',scene),'stale')
            self.assertEqual(manual_status(p,'movie','source',scene+[{'id':'b'}]),'incomplete')

    def test_actual_movies_are_reviewed_and_cached_without_certifying_history(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);movie=root/'movie.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=white:s=640x360:r=30:d=2','-vf','drawbox=x=90:y=80:w=120:h=120:color=0x9e1b32:t=fill','-an','-c:v','libx264','-pix_fmt','yuv420p',str(movie)],check=True)
            manifest=root/'collection.json';save(manifest,{'videos':[{'id':'current','video':'movie.mp4'},{'id':'old','production':'current','role':'reference','video':'movie.mp4'}]})
            first=review(manifest,root/'review',True)
            self.assertTrue(first['ok']);self.assertFalse(first['deliveryReady']);self.assertEqual(first['decodedFrames'],120)
            row=first['videos'][0];save(root/'manual.json',{'videoSha256':row['videoSha256'],'sourceSha256':None,'scenes':[{'id':'current','reviewed':True,'notes':'Observed fixture.'}]})
            data=json.loads(manifest.read_text());data['videos'][0]['manualReview']='manual.json';save(manifest,data)
            second=review(manifest,root/'review',True)
            self.assertTrue(second['deliveryReady']);self.assertEqual(second['referenceVideos'],1)
            cache=json.loads((root/'review/current/encoded/summary.json').read_text())
            self.assertEqual(cache['cache']['capturedFrames'],0)
            self.assertTrue((root/'review/index.html').is_file())


if __name__=='__main__':unittest.main()
