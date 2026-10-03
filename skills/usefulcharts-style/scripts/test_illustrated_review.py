#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise non-compensating review and stale-evidence boundaries."""
from pathlib import Path
import copy
import hashlib
import tempfile
import unittest
from assess_illustrated_review import assess, DIMENSIONS

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(prefix='illustrated-review-',dir=Path.cwd())
        self.base=Path(self.folder.name)
        for name in ('whole.png','detail.png','asset.png'): (self.base/name).write_bytes(b'synthetic fixture bytes; no pixel-quality claim')
        digest=hashlib.sha256((self.base/'whole.png').read_bytes()).hexdigest()
        self.review=dict(schema_version=1,reviewed_images=True,content_verified=True,technical_verified=True,
          artifacts={kind:dict(path=kind+'.png',sha256=digest) for kind in ('whole','detail')},
          required_groups=['a','b'],record_ids=['a1','b1'],minimum_body_regions=2,
          body_images=[dict(placement_id=g,asset_id=g,path='asset.png',anchors=[g+'1'],groups=[g],region=r,
                            recognized_at_placed_size=True,explanation='A verified fixture subject.') for g,r in [('a','upper'),('b','lower')]],
          discovery_invitations=[dict(question='Compare the two source mechanisms.',anchors=['a1','b1'],answer_location='Beside both illustrated specimens.')],
          dimensions={d:dict(score=3,observation='Fixture observation, not an actual visual assessment.') for d in DIMENSIONS},
          before_weaknesses=['List-like rhythm.','No subject images.','No comparison.'],repairs_observed=['Fixture repair.'],
          unresolved_defects=[],reference_density_status='pending')
    def tearDown(self): self.folder.cleanup()
    def check(self,code): self.assertIn(code,assess(self.review,self.base)['failures'])
    def test_complete_declared_evidence_preserves_pending_density(self):
        report=assess(self.review,self.base);self.assertTrue(report['declared_illustrated_brief_pass']);self.assertEqual(report['reference_density_status'],'pending')
    def test_high_scores_do_not_replace_images(self):
        self.review['body_images']=[];self.check('no-body-images')
    def test_banner_is_not_body_imagery(self):
        self.review['body_images'][0]['region']='header';self.check('image-outside-body')
    def test_weak_discovery_is_not_averaged_away(self):
        for d in self.review['dimensions'].values():d['score']=4
        self.review['dimensions']['playful_discovery']['score']=2;self.check('weak-playful_discovery')
    def test_stale_preview(self):
        (self.base/'whole.png').write_bytes(b'new revision');self.check('stale-whole')
    def test_unbound_subject(self):
        self.review['body_images'][0]['anchors']=['invented'];self.check('unbound-image')
    def test_missing_family(self):
        self.review['body_images'].pop();self.check('unillustrated-family')
    def test_duplicate_placement(self):
        self.review['body_images'].append(copy.deepcopy(self.review['body_images'][0]));self.check('duplicate-or-missing-placement')
    def test_geometry_is_not_direct_review(self):
        self.review['reviewed_images']=False;self.check('reviewed_images')
    def test_missing_actual_size_review(self):
        self.review['body_images'][0]['recognized_at_placed_size']=False;self.check('unreviewed-subject')
    def test_open_defect(self):
        self.review['unresolved_defects']=['Tiny illegible art.'];self.check('unresolved-defects')
    def test_unsupported_question(self):
        self.review['discovery_invitations'][0]['anchors']=['absent'];self.check('unsupported-invitation')

if __name__=='__main__':unittest.main()
