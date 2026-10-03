#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check evidence completeness and declared illustrated-review gates, not image quality."""
from pathlib import Path
import argparse
import hashlib
import json

DIMENSIONS = ('composition', 'image_usefulness', 'image_integration', 'playful_discovery', 'legibility')

def assess(data, base):
    failures=[]
    def need(condition, code):
        if not condition: failures.append(code)
    need(data.get('schema_version') == 1, 'schema-version')
    for field in ('reviewed_images','content_verified','technical_verified'):
        need(data.get(field) is True, field)
    for kind in ('whole','detail'):
        record=data.get('artifacts',{}).get(kind,{})
        path=base/record.get('path','')
        need(path.is_file(), 'missing-'+kind)
        if path.is_file():
            need(hashlib.sha256(path.read_bytes()).hexdigest()==record.get('sha256'), 'stale-'+kind)
    groups=set(data.get('required_groups',[]));records=set(data.get('record_ids',[]))
    need(bool(groups) and bool(records), 'missing-inventory')
    images=data.get('body_images',[]);seen=set();covered=set();regions=set()
    for item in images:
        identifier=item.get('placement_id')
        need(bool(identifier) and identifier not in seen, 'duplicate-or-missing-placement')
        seen.add(identifier)
        need(bool(item.get('asset_id')), 'missing-asset-identity')
        need((base/item.get('path','')).is_file(), 'missing-image-file')
        anchors=set(item.get('anchors',[]))
        need(bool(anchors) and anchors <= records, 'unbound-image')
        image_groups=set(item.get('groups',[]))
        need(bool(image_groups) and image_groups <= groups, 'unknown-image-group')
        covered.update(image_groups)
        region=item.get('region')
        need(region in ('upper','middle','lower'), 'image-outside-body')
        regions.add(region)
        need(item.get('recognized_at_placed_size') is True, 'unreviewed-subject')
        need(bool(str(item.get('explanation','')).strip()), 'missing-image-purpose')
    need(bool(images), 'no-body-images')
    need(groups <= covered, 'unillustrated-family')
    minimum=data.get('minimum_body_regions',2)
    need(type(minimum) is int and 1 <= minimum <= 3, 'invalid-region-minimum')
    if type(minimum) is int: need(len(regions & {'upper','middle','lower'}) >= minimum, 'concentrated-imagery')
    invitations=data.get('discovery_invitations',[])
    need(bool(invitations), 'no-discovery-invitation')
    for invitation in invitations:
        anchors=set(invitation.get('anchors',[]))
        need(bool(anchors) and anchors <= records and bool(invitation.get('question')) and bool(invitation.get('answer_location')), 'unsupported-invitation')
    for name in DIMENSIONS:
        dimension=data.get('dimensions',{}).get(name,{})
        score=dimension.get('score')
        need(type(score) in (int,float) and 3 <= score <= 4, 'weak-'+name)
        need(bool(str(dimension.get('observation','')).strip()), 'unexplained-'+name)
    need(len(data.get('before_weaknesses',[])) >= 3, 'missing-before-critique')
    need(bool(data.get('repairs_observed')), 'missing-observed-repair')
    need(not data.get('unresolved_defects'), 'unresolved-defects')
    need(data.get('reference_density_status') in ('pending','verified','failed'), 'missing-density-boundary')
    return dict(schema_version=1, declared_illustrated_brief_pass=not failures, failures=sorted(set(failures)),
                body_placements=len(images), illustrated_groups=sorted(covered), body_regions=sorted(regions),
                reference_density_status=data.get('reference_density_status','pending'),
                evidence_boundary='This validates artifact hashes and declared review completeness. It does not inspect pixels, certify reviewer claims, measure reference density, or establish stylistic parity.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review',type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();data=json.loads(args.review.read_text(encoding='utf-8-sig'))
    result=assess(data,args.review.parent)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result));return 0 if result['declared_illustrated_brief_pass'] else 1

if __name__=='__main__': raise SystemExit(main())
