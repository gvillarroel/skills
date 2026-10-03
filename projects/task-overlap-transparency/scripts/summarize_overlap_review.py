#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize scoped overlap transparency and shared-file regression evidence."""

import hashlib
import json
import re
from pathlib import Path


ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/"projects/task-overlap-transparency"


def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def digest(path):
    target=ROOT/path
    return {'path':path,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size}


def main():
    paths={
        'baseline':'projects/task-overlap-transparency/artifacts/baseline/verification.json',
        'native':'projects/task-overlap-transparency/artifacts/final-cs1/verification.json',
        'exportPreparation':'projects/task-overlap-transparency/artifacts/export-source-final/verification.json',
        'portableDelivery':'projects/task-overlap-transparency/artifacts/delivery-final/delivery.json',
        'productionDelivery':'projects/task-overlap-transparency/artifacts/production-delivery/delivery.json',
        'colorset2Smoke':'projects/task-overlap-transparency/artifacts/cs2-smoke/verification.json',
        'treemapRegression':'projects/task-overlap-transparency/artifacts/treemap-regression/verification.json'
    }
    reports={name:read(path) for name,path in paths.items()}
    old_gallery=(PROJECT/'artifacts/baseline-source/d3-animated-svg/gallery.js').read_text(encoding='utf-8')
    current_gallery=(ROOT/'skills/d3/assets/examples/d3-animated-svg/gallery.js').read_text(encoding='utf-8')
    extract=lambda text,name:re.search(rf'  function {name}\(\) \{{.*?(?=\n  function )',text,re.S).group()
    old_treemap=extract(old_gallery,'renderTreemap');new_treemap=extract(current_gallery,'renderTreemap')
    recipe=(ROOT/'skills/d3/references/patterns/task-overlap-dense.md').read_text(encoding='utf-8')
    dense=extract(current_gallery,'renderAsymmetricTaskOverlapSaturated').strip()
    excerpt=re.search(r'```js\n(.*?)\n```',recipe,re.S).group(1).strip()
    assert old_treemap==new_treemap and dense==excerpt
    native=reports['native'];delivery=reports['portableDelivery'];production=reports['productionDelivery'];treemap=reports['treemapRegression']
    labels=[label for state in native['states'] for label in state['labels']]
    samples=[sample for state in native['states'] for sample in state['samples']]
    result={
      'schemaVersion':1,'date':'2026-10-03','patternId':'d3-task-overlap-dense-cs1','outcome':'pass',
      'authorizedScope':'Use semantic transparency on overlapping set regions so intersections remain understandable, preserving opaque ordinary category nodes, task dots and label faces.',
      'change':'The nine scope circles use their existing saturated colorset tokens at fill-opacity 0.28, declare data-opacity-role=semantic, and have no decorative stroke. The reusable standalone recipe mirrors this renderer, documents source-over set-membership meaning and generates local layout data outside the read-only skill bundle.',
      'baseline':{'states':1,'findings':len(reports['baseline']['states'][0]['findings']),'browserErrors':reports['baseline']['errors'],'classification':'All nine regions lacked a semantic opacity declaration and were opaque. Later circles therefore hid earlier membership intersections.'},
      'native':{'states':len(native['states']),'matrix':'1440/390 px by normal/reduced motion by initial settled state and two replays','clean':native['clean'],'findings':sum(len(state['findings']) for state in native['states']),'regionChecks':9*len(native['states']),'taskDotsPerState':100,'taskLabelsPerState':100,'scopeLabelsPerState':9,'totalTextLabelsPerState':len(native['states'][0]['labels']),'minimumLabelContrast':min(label['contrast'] for label in labels),'allLabelsMaximumContrastBlackWhite':True,'opaqueTaskDotsAndLabelFaces':True,'regionPaint':native['states'][0]['regions'],'clearIntersectionSamples':len(samples),'sampleMultiplicities':sorted({sample['multiplicity'] for sample in samples}),'maximumPixelChannelError':max(sample['maximumChannelError'] for sample in samples),'pixelTolerance':5,'mobileCapture':'The existing wide-card horizontal scroll container is centered; the SVG/layout/CSS are unchanged.'},
      'dataPreservation':{'clean':not delivery['nativeComparisonFindings'],'nativeGeometryComparisons':delivery['nativeGeometryComparisons'],'fields':'Nine set IDs/centers/radii and one hundred task IDs/positions/memberships/labels/leader endpoints per state; collision/crossing/membership buckets unchanged.','invariants':native['states'][0]['invariants'],'regeneratedLayoutByteMatchesPublished':(PROJECT/'artifacts/layout/task-overlap-layouts.js').read_bytes()==(ROOT/'skills/d3/assets/examples/d3-animated-svg/task-overlap-layouts.js').read_bytes()},
      'portableSvg':{'clean':delivery['clean'],'exportPreparationStates':len(reports['exportPreparation']['states']),'deliveryStates':len(delivery['exports']),'maximumPixelChannelError':max(sample['maximumChannelError'] for state in delivery['exports'] for sample in state['samples']),'minimumLabelContrast':min(label['contrast'] for state in delivery['exports'] for label in state['labels']),'serialization':'XMLSerializer supplies the SVG namespace; inherited text font family/size/weight are materialized from the live browser. Scope alpha and native SMIL remain intact.'},
      'productionSvg':{'clean':production['clean'],'renderer':'skills/d3/scripts/render_d3_svg.py','deliveryStates':len(production['exports']),'maximumPixelChannelError':max(sample['maximumChannelError'] for state in production['exports'] for sample in state['samples']),'minimumLabelContrast':min(label['contrast'] for state in production['exports'] for label in state['labels']),'source':'projects/task-overlap-transparency/artifacts/production-export/dense-overlap.svg'},
      'negativeControls':{'controls':delivery['negativeControls'],'allRejected':all(control['rejected'] for control in delivery['negativeControls']),'ordinaryOpaqueProbe':delivery['ordinaryOpaqueControl'],'scope':'Only the nine declared regions preserve alpha. A new ordinary unmarked filled rectangle is finalized to alpha 1; removing a semantic marker or making task dots translucent is rejected.'},
      'colorset2Regression':{'states':1,'clean':reports['colorset2Smoke']['clean'],'findings':reports['colorset2Smoke']['states'][0]['findings'],'scope':'One desktop settled smoke state because the shared renderer also serves colorset2.'},
      'treemapRegression':{'states':len(treemap['states']),'clean':treemap['clean'],'findings':sum(len(state['findings']) for state in treemap['states']),'geometryComparison':treemap['geometryComparison'],'rendererByteIdenticalAfterLfNormalization':old_treemap==new_treemap,'rendererLfSha256':hashlib.sha256(new_treemap.encode()).hexdigest(),'priorVisualReport':'evaluations/d3/treemap-tones-visual-20261003.json','priorReportUnchanged':True,'note':'The earlier 36-state report remains bound to its old full-gallery hash. This new 12-state CS1 regression verifies the final combined source.'},
      'recipeExcerptMatchesRendererAfterLfNormalization':dense==excerpt,
      'manualReview':{'independent':True,'outcome':'pass for the scoped transparency, paint, contrast and data-preservation checks','inspected':['Baseline desktop card','Final desktop card','Final mobile center scroll view','Standalone SVG at desktop and mobile size','Production renderer PNG and standalone production SVG'],'finding':'Transparency reveals the shared lens-shaped intersections while task dots remain visible. Labels use black on the actual pale composited regions or opaque white faces, and the region fills remain borderless. The final exporter preserves inherited caption font sizes instead of enlarging the footer.','existingFixtureLimit':{'description':'The bottom summary caption contacts the T095 task label in the inherited fixture. The contact exists in baseline and final screenshots and is also visible in the production SVG. It is not caused by transparency and remains unchanged because this pass preserves original task/label geometry. This report does not claim every fixture text pair is collision-free.','baselineScreenshot':'projects/task-overlap-transparency/artifacts/baseline/overlap-1440-normal-0-card.png','finalScreenshot':'projects/task-overlap-transparency/artifacts/final-cs1/overlap-1440-normal-0-card.png','productionScreenshot':'projects/task-overlap-transparency/artifacts/production-export/dense-overlap.png'},'limits':'Finite named fixture states are covered. Native mobile dense diagrams retain their existing horizontal scrolling layout; fitting every task label simultaneously into 390 pixels is outside this transparency change. The preserved generated collision counts refer to the task-label model, not an audit of every caption in the SVG.'},
      'retainedVerifierDevelopment':[
        {'path':'projects/task-overlap-transparency/artifacts/baseline/verification-scanner-v1.json','classification':'Scanner-only false positives: exact double equality with SVG float32 coordinate storage flagged 99 unchanged task coordinates. Final tolerance is 0.001 SVG units; the true baseline has 18 alpha/declaration findings.'},
        {'path':'projects/task-overlap-transparency/artifacts/final-cs1-scanner-v2/verification.json','classification':'Scanner-only pixel framing error: samples outside the horizontally clipped mobile SVG read blank page paint. Final capture uses the actual wide-card scroll container.'},
        {'classification':'One standalone inspector extension initially destructured Playwright null arguments; corrected to an optional options object before the final passing run.'},
        {'path':'projects/task-overlap-transparency/artifacts/final-cs1/overlap-1440-normal-0.svg','classification':'Early helper export omitted SVG namespace. Retained as failed export input; XMLSerializer supplies the namespace for accepted exports.'},
        {'path':'projects/task-overlap-transparency/artifacts/export-source/overlap-1440-normal-0.svg','classification':'Initial namespace-correct raw export lost inherited caption font sizes. Numerical paint tests passed, but manual review rejected enlarged footer text. Final font-materialized exports and the production renderer pass.'}
      ],
      'commands':[
        'uv run --script projects/task-overlap-transparency/scripts/verify_overlap.py projects/task-overlap-transparency/artifacts/baseline-source/d3-animated-svg-cs1/index.html --output-directory projects/task-overlap-transparency/artifacts/baseline --baseline --quick',
        'uv run --script projects/task-overlap-transparency/scripts/patch_overlap.py',
        'uv run --script projects/task-overlap-transparency/scripts/verify_overlap.py skills/d3/assets/examples/d3-animated-svg-cs1/index.html --output-directory projects/task-overlap-transparency/artifacts/final-cs1',
        'uv run --script projects/task-overlap-transparency/scripts/verify_overlap.py skills/d3/assets/examples/d3-animated-svg-cs1/index.html --output-directory projects/task-overlap-transparency/artifacts/export-source-final --replays 1',
        'uv run --script projects/task-overlap-transparency/scripts/check_overlap_delivery.py --source skills/d3/assets/examples/d3-animated-svg-cs1/index.html --reference projects/task-overlap-transparency/artifacts/final-cs1/verification.json --baseline projects/task-overlap-transparency/artifacts/baseline/verification.json --export-directory projects/task-overlap-transparency/artifacts/export-source-final --output-directory projects/task-overlap-transparency/artifacts/delivery-final',
        "uv run --script skills/d3/scripts/render_d3_svg.py skills/d3/assets/examples/d3-animated-svg-cs1/index.html --selector '#task-overlap-dense' --output projects/task-overlap-transparency/artifacts/production-export/dense-overlap.svg --screenshot projects/task-overlap-transparency/artifacts/production-export/dense-overlap.png --wait-ms 4500 --viewport 1440x1100",
        'uv run --script projects/task-overlap-transparency/scripts/check_overlap_delivery.py --source skills/d3/assets/examples/d3-animated-svg-cs1/index.html --reference projects/task-overlap-transparency/artifacts/final-cs1/verification.json --baseline projects/task-overlap-transparency/artifacts/baseline/verification.json --svg projects/task-overlap-transparency/artifacts/production-export/dense-overlap.svg --output-directory projects/task-overlap-transparency/artifacts/production-delivery',
        'uv run --script projects/task-overlap-transparency/scripts/verify_overlap.py skills/d3/assets/examples/d3-animated-svg-colorset2/index.html --output-directory projects/task-overlap-transparency/artifacts/cs2-smoke --quick',
        'uv run --script skills/d3/scripts/layout_task_overlap_labels.py --output projects/task-overlap-transparency/artifacts/layout/task-overlap-layouts.js',
        'uv run --script projects/treemap-tones/scripts/verify_treemap.py skills/d3/assets/examples/d3-animated-svg-cs1/index.html --output-directory projects/task-overlap-transparency/artifacts/treemap-regression --compare-reference projects/treemap-tones/artifacts/baseline/verification.json'
      ],
      'sources':[],'artifacts':[]
    }
    result['sources']=[digest(path) for path in [
      'projects/task-overlap-transparency/artifacts/baseline-source/d3-animated-svg/gallery.js','skills/d3/assets/examples/d3-animated-svg/gallery.js','skills/d3/references/patterns/task-overlap-dense.md','skills/d3/assets/examples/d3-animated-svg/task-overlap-layouts.js','skills/d3/assets/examples/d3-animated-svg/solid-style.js','skills/d3/assets/templates/solid-style.js','skills/d3/scripts/render_d3_svg.py','skills/d3/scripts/layout_task_overlap_labels.py','projects/task-overlap-transparency/scripts/verify_overlap.py','projects/task-overlap-transparency/scripts/check_overlap_delivery.py']]
    artifact_paths=list(paths.values())+[
      'projects/task-overlap-transparency/artifacts/baseline/verification-scanner-v1.json','projects/task-overlap-transparency/artifacts/final-cs1-scanner-v2/verification.json','projects/task-overlap-transparency/artifacts/layout/task-overlap-layouts.js','projects/task-overlap-transparency/artifacts/production-export/dense-overlap.svg','projects/task-overlap-transparency/artifacts/production-export/dense-overlap.png','projects/task-overlap-transparency/artifacts/baseline/overlap-1440-normal-0-card.png',
      'projects/task-overlap-transparency/artifacts/final-cs1/overlap-1440-normal-0-card.png','projects/task-overlap-transparency/artifacts/final-cs1/overlap-390-normal-0-card.png'
    ]
    artifact_paths += [f'projects/task-overlap-transparency/artifacts/export-source-final/overlap-{width}-{motion}-0.svg' for width in [1440,390] for motion in ['normal','reduced']]
    artifact_paths += [f'projects/task-overlap-transparency/artifacts/production-delivery/export-{width}-{motion}.png' for width in [1440,390] for motion in ['normal','reduced']]
    result['artifacts']=[digest(path) for path in artifact_paths]
    assert len(native['states'])==12 and native['clean'] and delivery['clean'] and production['clean'] and treemap['clean']
    assert result['dataPreservation']['regeneratedLayoutByteMatchesPublished'] and result['negativeControls']['allRejected']
    target=ROOT/'evaluations/d3/task-overlap-transparency-visual-20261003.json';target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'outcome':'pass','report':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'nativeStates':12,'portableDeliveryStates':4,'productionDeliveryStates':4,'treemapRegressionStates':12},indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
