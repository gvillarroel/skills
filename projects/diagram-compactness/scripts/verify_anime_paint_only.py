#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prove the final Anime runtime repair changes paint and a paint test only."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
BEFORE = "compact-slidev-animejs-20261004-sol-release2-contract"
AFTER = "compact-slidev-animejs-20261004-painted-contract"
old_root = ROOT / "evaluations/runs" / BEFORE / "workspace/skills/slidev-animejs"
new_root = ROOT / "evaluations/runs" / AFTER / "workspace/skills/slidev-animejs"
# Match the harness snapshot policy for interpreter caches, not source files.
def runtime_files(root):
    return {str(p.relative_to(root)).replace('\\', '/'): p.read_bytes() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc', '.pyo'}}
old = runtime_files(old_root)
new = runtime_files(new_root)
assert old.keys() == new.keys(), "Runtime inventory changed"
changed = sorted(p for p in old if old[p] != new[p])
assert changed == ["scripts/scaffold_connected_flow.py", "scripts/test_connected_flow.py"], changed
scaffold = "scripts/scaffold_connected_flow.py"
assert old[scaffold].count(b'"accent": "#e8002a"') == 2
assert old[scaffold].replace(b'"accent": "#e8002a"', b'"accent": "#9e1b32"') == new[scaffold], "More than two paint defaults changed"
test = "scripts/test_connected_flow.py"
normalized_test = new[test].replace(b"parcelFill:getComputedStyle(root.querySelector('.parcel')).fill,", b'').replace(b'        assert report["parcelFill"] == "rgb(158, 27, 50)", report\r\n', b'').replace(b'        assert report["parcelFill"] == "rgb(158, 27, 50)", report\n', b'')
assert normalized_test == old[test], "Geometry or behavior test changed"
template = "assets/templates/ConnectedFlow.vue"
assert old[template] == new[template], "Measured layout, route or motion source changed"
workspace = new_root.parents[1]
component = (workspace / 'deck/components/OrderHandoff.vue').read_text(encoding='utf-8')
config_literal = re.search(r'^const config = (.+)$', component, re.MULTILINE).group(1)
config = json.loads(config_literal)
assert config['accent'] == '#9e1b32' and config['labels'] == ['Order', 'Pick', 'Pack', 'Dispatch']
assert component == new[template].decode('utf-8').replace('\r\n', '\n').replace('__FLOW_CONFIG__', config_literal), "Painted contract altered generated geometry/motion/template"
boundary_component = (ROOT / 'evaluations/runs/compact-slidev-animejs-20261004-boundary-contract/workspace/deck/components/AccessRouting.vue').read_text(encoding='utf-8')
boundary_literal = re.search(r'^const config = (.+)$', boundary_component, re.MULTILINE).group(1)
boundary_config = json.loads(boundary_literal)
assert boundary_config['accent'] == '#9e1b32' and boundary_config['labels'] == ['Request', 'Parse', 'Authorize', 'Queue', 'Run', 'Notify']
assert boundary_config['branch']['at'] == 0 and boundary_config['return']['source'] == 5 and boundary_config['return']['target'] == 0
assert boundary_component == new[template].decode('utf-8').replace('\r\n', '\n').replace('__FLOW_CONFIG__', boundary_literal), "Boundary contract altered generated geometry/motion/template"
old_report = json.loads((ROOT / "projects/diagram-compactness/artifacts/reviews/anime-complete-tests/browser.json").read_text(encoding='utf-8'))['geometry']
new_report = json.loads((ROOT / "projects/diagram-compactness/artifacts/reviews/anime-painted-tests/browser.json").read_text(encoding='utf-8'))['geometry']
assert new_report.pop('parcelFill') == 'rgb(158, 27, 50)'
# A theme's downloaded font versus its fallback can change measured text extents.
# Keep both measurements visible; exact geometry source and semantic checks match.
dimensions = {"before": [old_report.pop('width'), old_report.pop('height')], "after": [new_report.pop('width'), new_report.pop('height')]}
assert old_report == new_report, "Native label, route or collision checks changed"
manifests = [json.loads((ROOT / "evaluations/runs" / run / "run-manifest.json").read_text(encoding='utf-8')) for run in (BEFORE, AFTER)]
report = {"passed": True, "beforePayloadSha256": manifests[0]['skill']['payloadSha256'], "afterPayloadSha256": manifests[1]['skill']['payloadSha256'], "changedRuntimeFiles": changed, "unchangedTemplateSha256": hashlib.sha256(new[template]).hexdigest(), "geometrySourceByteIdentical": True, "generatedContractTemplateUnchanged": True, "generatedBoundaryTemplateUnchanged": True, "semanticGeometryChecksEqual": True, "fontMeasuredDimensions": dimensions, "parcelFill": "rgb(158, 27, 50)"}
out = ROOT / "projects/diagram-compactness/artifacts/reviews/anime-paint-comparison.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
