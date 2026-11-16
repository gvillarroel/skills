#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise editorial candidates and boundaries using quoted narration fixtures."""
import json
import tempfile
import unittest
from pathlib import Path
from narration_review import inspect, read_story


def story(text):
    return {'scenes': [{'id': 'mechanism', 'script': text}]}


class NarrationReviewTests(unittest.TestCase):
    def test_spanish_representation_commentary(self):
        result = inspect(story('La animación representa el mecanismo; no mide una aceleración concreta.'))
        self.assertEqual(result['candidates'][0]['code'], 'representation-disclaimer')

    def test_english_map_commentary(self):
        self.assertEqual(inspect(story('The diagram is only a map of reality.'))['candidateCount'], 1)

    def test_pointer_and_redundant_translation(self):
        result = inspect(story('El punto rojo identifica la operación. El gráfico de la derecha traduce exactamente esas filas.'))
        self.assertEqual({x['code'] for x in result['candidates']}, {'guide-commentary', 'presentation-commentary'})

    def test_scope_limit_and_navigation_are_not_banned(self):
        text = 'Figure 2 explains weight updates. Only eight selected tasks were tested. This does not establish performance on all ARC tasks.'
        self.assertEqual(inspect(story(text))['candidateCount'], 0)

    def test_material_measurement_note_requires_judgment(self):
        result = inspect(story('Esta curva es un esquema del mecanismo, no una medición de nuestra regresión.'))
        self.assertGreater(result['candidateCount'], 0)
        self.assertEqual(result['candidates'][0]['decision'], 'pending')
        self.assertEqual(result['status'], 'editorial-review-required')

    def test_changed_scripts_use_stable_ids_not_order(self):
        old = {'scenes': [{'id': 'b', 'script': 'Same.'}, {'id': 'a', 'script': 'Old.'}]}
        new = {'scenes': [{'id': 'a', 'script': 'New.'}, {'id': 'b', 'script': 'Same.'}]}
        self.assertEqual([s['id'] for s in inspect(new, old)['changedScripts']], ['a'])
        self.assertEqual(inspect(new, old)['changedScripts'][0]['nativeAudioTiming'], 'must-be-measured')

    def test_unmatched_scene_still_needs_editorial_review(self):
        result = inspect(story('Threads compute independent matrix entries.'))
        self.assertEqual(result['candidateCount'], 0)
        self.assertEqual(result['scenes'][0]['editorialReview'], 'pending')

    def test_duplicate_ids_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'story.json'
            path.write_text(json.dumps({'scenes': [story('A.')['scenes'][0]] * 2}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'unique'):
                read_story(path)


if __name__ == '__main__':
    unittest.main()
