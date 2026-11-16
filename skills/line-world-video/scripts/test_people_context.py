#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Reject portraits without a narrated, visible and sourced contribution."""
import copy
import unittest
from people_context import review


class PeopleTests(unittest.TestCase):
    def setUp(self):
        self.person = {'id': 'ada', 'name': 'Ada Example', 'caption': ['Built the method'], 'narrationRole': 'built the method', 'target': 'person-ada', 'sources': ['https://example.org/paper']}
        self.story = {'scenes': [{'id': 'method', 'script': 'Ada Example built the method with a larger team.', 'people': [self.person], 'cues': [{'target': 'person-ada', 'phrase': 'Ada Example'}]}]}
        self.media = {'assets': [{'id': 'ada', 'kind': 'portrait', 'stage': 'method'}]}
        self.cues = {'status': 'aligned-to-audio', 'scenes': [{'id': 'method', 'cues': [{'target': 'person-ada', 'phrase': 'Ada Example', 'at': 2, 'end': 3, 'audioStart': 2, 'audioEnd': 3, 'evidence': 'Actual fixture word timestamps.'}]}]}
        self.visible = {'observed': True, 'evidence': 'Synthetic browser fixture.', 'scenes': [{'id': 'method', 'people': [{'id': 'ada', 'name': 'Ada Example', 'caption': ['Built the method'], 'legible': True}]}]}

    def check(self, **kwargs): return review(self.story, self.media, **kwargs)
    def kinds(self, **kwargs): return {f['kind'] for f in self.check(**kwargs)['findings']}

    def test_complete_introduction(self): self.assertTrue(self.check(cues=self.cues, visible=self.visible, require_observed=True)['ok'])
    def test_script_preflight_reports_pending_observation(self): self.assertEqual(len(self.check()['pending']), 2)
    def test_anonymous_existing_portrait_is_rejected(self):
        self.story['scenes'][0]['people'] = []; self.assertIn('unintroduced-portrait', self.kinds())
    def test_a_name_only_does_not_explain_a_contribution(self):
        self.story['scenes'][0]['script'] = 'Ada Example is here.'; self.assertIn('missing-spoken-contribution', self.kinds())
    def test_unnamed_contribution_is_rejected(self):
        self.story['scenes'][0]['script'] = 'The team built the method.'; self.assertIn('missing-spoken-name', self.kinds())
    def test_sources_and_caption_are_required(self):
        self.person['sources'] = []; self.person['caption'] = []; self.assertTrue({'missing-contribution-source','missing-contribution-caption'} <= self.kinds())
    def test_stale_rendered_caption_is_rejected(self):
        self.visible['scenes'][0]['people'][0]['caption'] = ['Old role']; self.assertIn('visible-contribution-mismatch', self.kinds(visible=self.visible))
    def test_draft_timing_does_not_prove_spoken_name(self):
        self.cues['status'] = 'estimated'; self.assertIn('missing-measured-name-cue', self.kinds(cues=self.cues))
    def test_generic_focus_cue_cannot_substitute_for_a_name(self):
        self.cues['scenes'][0]['cues'][0]['phrase'] = 'the method'; self.assertIn('wrong-name-cue', self.kinds(cues=self.cues))
    def test_legibility_and_unknown_rendered_people(self):
        self.visible['scenes'][0]['people'][0]['legible'] = False
        self.visible['scenes'][0]['people'].append({'id':'unknown'}); self.assertTrue({'illegible-person-context','unintroduced-visible-person'} <= self.kinds(visible=self.visible))
    def test_delivery_requires_actual_observations(self): self.assertIn('incomplete-observation', self.kinds(require_observed=True))
    def test_optional_asset_stage_and_name_normalization(self):
        self.media['assets'][0].pop('stage'); self.person['name'] = 'Ada-Example'; self.assertTrue(self.check()['ok'])


if __name__ == '__main__': unittest.main()
