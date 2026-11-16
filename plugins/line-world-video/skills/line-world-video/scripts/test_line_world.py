#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise meaningful source, timing and rejection invariants."""
import copy
import json
import unittest
import tempfile
from pathlib import Path

from line_world import DEFAULT, validate, local_svg
from atlas_story import DEFAULT_ATLAS, partition_check, validate_atlas, coverage


class StoryContract(unittest.TestCase):
    def test_video_palettes_put_red_first_and_black_last(self):
        palettes=json.loads((Path(__file__).resolve().parent.parent/'assets/palettes/video-colors.json').read_text())
        for palette in palettes['colorsets'].values():
            for key in ('sequence','solidSequence'):
                sequence=palette[key]
                self.assertEqual(sequence[0],'#9e1b32')
                self.assertEqual(sequence[-1],'#000000')
                self.assertNotIn('#1c1c1c',sequence[:8])
                for token in sequence[1:8]:
                    channels=[int(token[i:i+2],16) for i in (1,3,5)]
                    self.assertEqual(len(set(channels)),1)
                    self.assertGreaterEqual(channels[0],130)

    def test_contiguous_timing_and_total(self):
        result = validate(DEFAULT)
        self.assertEqual(result["duration"], 56)
        self.assertTrue(all(a["end"] == b["start"] for a, b in zip(result["beats"], result["beats"][1:])))

    def test_retime_preserves_values_and_shifts_later_beats(self):
        raw = copy.deepcopy(DEFAULT)
        raw["timing"]["compare"] += 6
        result = validate(raw)
        self.assertEqual(result["duration"], 62)
        self.assertEqual(result["beats"][4]["start"], 39)
        self.assertEqual(result["rows"], DEFAULT["rows"])

    def test_invalid_values(self):
        for value in (-1, float("nan"), float("inf"), True, "8"):
            with self.subTest(value=value):
                raw = copy.deepcopy(DEFAULT)
                raw["rows"][0]["before"] = value
                with self.assertRaises(ValueError):
                    validate(raw)

    def test_duplicate_ids(self):
        raw = copy.deepcopy(DEFAULT)
        raw["rows"][1]["id"] = raw["rows"][0]["id"]
        with self.assertRaises(ValueError):
            validate(raw)

    def test_short_reading_budget(self):
        raw = copy.deepcopy(DEFAULT)
        raw["timing"]["compare"] = 7
        with self.assertRaises(ValueError):
            validate(raw)

    def test_history_alignment(self):
        raw = copy.deepcopy(DEFAULT)
        raw["rows"][0]["trend"].append(8)
        with self.assertRaises(ValueError):
            validate(raw)

    def test_no_input_mutation(self):
        original = copy.deepcopy(DEFAULT)
        validate(DEFAULT)
        self.assertEqual(original, DEFAULT)

    def test_default_red_neutral_and_extended_reason(self):
        self.assertEqual(validate(DEFAULT)["palette"], "colorset1")
        raw = copy.deepcopy(DEFAULT)
        raw.update(palette="colorset2", paletteReason="")
        with self.assertRaises(ValueError):
            validate(raw)

    def test_non_169_rejected_before_layout(self):
        raw = copy.deepcopy(DEFAULT)
        raw.update(width=1080, height=1920)
        with self.assertRaises(ValueError):
            validate(raw)

    def test_context_is_absent_by_default_and_explicit_when_requested(self):
        self.assertEqual(validate(DEFAULT)["presentation"]["contextLabels"], {})
        raw = copy.deepcopy(DEFAULT)
        raw["presentation"]["contextLabels"] = {"compare": "Queue times"}
        self.assertEqual(validate(raw)["presentation"]["contextLabels"], {"compare": "Queue times"})

    def test_context_cannot_become_an_unbounded_headline(self):
        for labels in ({"unknown": "Title"}, {"compare": "One two three four five six seven"}, {"compare": ""}):
            raw = copy.deepcopy(DEFAULT)
            raw["presentation"]["contextLabels"] = labels
            with self.assertRaises(ValueError):
                validate(raw)


class AtlasContract(unittest.TestCase):
    def test_primary_red_and_attention_ranges(self):
        raw=copy.deepcopy(DEFAULT_ATLAS)
        self.assertEqual(validate(raw)['attention']['guideColor'],'#9e1b32')
        for change in ({'guideColor':'#e8002a'},{'baseRadius':-2},{'emitRadius':float('nan')},{'travelRadius':40}):
            candidate=copy.deepcopy(raw);candidate['attention'].update(change)
            with self.assertRaises(ValueError):validate(candidate)

    def test_semantic_colors_require_extended_palette_and_existing_ids(self):
        raw=copy.deepcopy(DEFAULT_ATLAS);raw['attention']['categoryColors']={'intake':'#007298'}
        with self.assertRaises(ValueError):validate(raw)
        raw.update(palette='colorset2',paletteReason='Stage identities in emitted quantity points.')
        self.assertEqual(validate(raw)['attention']['categoryColors']['intake'],'#007298')
        raw['attention']['categoryColors']={'missing':'#007298'}
        with self.assertRaises(ValueError):validate(raw)

    def test_quantity_unit_cannot_silently_drop_points(self):
        raw=copy.deepcopy(DEFAULT_ATLAS);raw['attention']['unitPerPoint']=.01
        with self.assertRaises(ValueError):validate(raw)

    def test_all_frames_have_exact_complete_partitions(self):
        atlas=validate_atlas(DEFAULT_ATLAS)
        self.assertEqual(atlas["duration"],185)
        self.assertEqual(len(coverage(atlas)["mermaidFamilies"]),20)
        self.assertEqual(len(coverage(atlas)["d3Forms"]),26)
        for scene in atlas["scenePlan"]:
            self.assertAlmostEqual(partition_check(scene["panels"])["coveredArea"],1)

    def test_area_sum_cannot_hide_overlap_and_gap(self):
        with self.assertRaises(ValueError):
            partition_check([{"rect":[0,0,.5,1]},{"rect":[.25,0,.5,1]}])

    def test_tiny_gap_is_rejected(self):
        with self.assertRaises(ValueError):
            partition_check([{"rect":[0,0,.49999,1]},{"rect":[.5,0,.5,1]}])

    def test_alternative_full_width_and_asymmetric_partitions(self):
        self.assertEqual(partition_check([{"rect":[0,0,1,.3]},{"rect":[0,.3,.4,.7]},{"rect":[.4,.3,.6,.7]}])["gaps"],0)

    def test_invalid_panel_coordinates(self):
        for rect in ([0,0,1.1,1],[0,0,0,1],[True,0,1,1],[0,0,float('nan'),1]):
            with self.subTest(rect=rect),self.assertRaises(ValueError):
                partition_check([{"rect":rect}])

    def test_retime_updates_later_beats_without_data_mutation(self):
        raw=copy.deepcopy(DEFAULT_ATLAS);raw['scenePlan'][0]['seconds']=14
        result=validate_atlas(raw)
        self.assertEqual(result['beats'][1]['start'],14)
        self.assertEqual(result['duration'],189)
        self.assertEqual(result['rows'],DEFAULT_ATLAS['rows'])

    def test_short_reading_hold_and_nan_are_rejected(self):
        for seconds in (3,float('nan'),True):
            raw=copy.deepcopy(DEFAULT_ATLAS);raw['scenePlan'][0]['seconds']=seconds
            with self.assertRaises(ValueError):validate_atlas(raw)

    def test_subset_reorders_cells_and_preserves_complete_frames(self):
        raw=copy.deepcopy(DEFAULT_ATLAS);raw['scenePlan']=[raw['scenePlan'][6],raw['scenePlan'][0]]
        result=validate_atlas(raw)
        self.assertEqual([b['id'] for b in result['beats']],['records','process','overview'])
        self.assertEqual(result['duration'],31)

    def test_native_diagrams_cannot_silently_keep_stale_numbers(self):
        raw=copy.deepcopy(DEFAULT_ATLAS);raw['rows'][0]['after']=99
        with self.assertRaises(ValueError):validate_atlas(raw)

    def test_svg_import_preserves_outer_root_and_namespaces_references(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            project=Path(folder)
            (project/'native.svg').write_text('<svg id="outer" aria-labelledby="title"><title id="title">Name</title><style>#outer .x{fill:url(#paint)}</style><defs><linearGradient id="paint"/></defs><g><svg id="icon"><path id="p"/></svg></g></svg>',encoding='utf-8')
            svg=local_svg(project,'native.svg','scene')
            self.assertTrue(svg.startswith('<svg id="scene-outer"'))
            self.assertIn('aria-labelledby="scene-title"',svg)
            self.assertIn('url(#scene-paint)',svg)
            self.assertIn('<svg id="scene-icon"',svg)
            self.assertEqual(svg.count('<svg'),2)

    def test_safe_svg_rejects_script_external_reference_and_outside_path(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            project=Path(folder)
            for source in ('<svg><script/></svg>','<svg><foreignObject/></svg>','<svg><image href="https://example.com/a.png"/></svg>'):
                (project/'bad.svg').write_text(source,encoding='utf-8')
                with self.assertRaises(ValueError):local_svg(project,'bad.svg','x')
            with self.assertRaises(ValueError):local_svg(project,'../bad.svg','x')


if __name__ == "__main__":
    unittest.main()
