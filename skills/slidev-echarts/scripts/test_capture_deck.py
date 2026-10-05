#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Check native graph click capture, SPA serving and resource cleanup."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
from urllib.parse import urlsplit

from capture_deck import capture


def assert_closed(report: dict) -> None:
    address = urlsplit(report['serverOrigin'])
    with socket.socket() as client:
        client.settimeout(1)
        assert client.connect_ex((address.hostname, address.port)) != 0, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    bundle = Path(__file__).resolve().parents[1]
    graph = {'nodes': [{'id': 'input', 'label': 'Input {a}'}, {'id': 'review', 'label': 'Review <raw>'}, {'id': 'archive', 'label': 'Archive & verify'}], 'edges': [{'source': 'input', 'target': 'review'}, {'source': 'review', 'target': 'archive'}, {'source': 'archive', 'target': 'review', 'kind': 'return', 'label': 'Retest {b} & validate'}]}
    (output / 'graph.json').write_text(json.dumps(graph), encoding='utf-8')
    renderer = bundle / 'scripts/render_concept_graph.py'
    result = subprocess.run([sys.executable, str(renderer), 'graph.json', '--svg', 'graph.svg', '--option', 'graph-option.json', '--review', 'graph-review.json'], cwd=output, capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, (result.stdout, result.stderr)
    geometry = json.loads((output / 'graph-review.json').read_text(encoding='utf-8'))
    dist = output / 'deck/dist'
    dist.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output / 'node_modules/echarts/dist/echarts.esm.mjs', dist / 'echarts.mjs')
    shutil.copy2(bundle / 'assets/templates/echarts-colorsets.mjs', dist / 'colorsets.mjs')
    shutil.copy2(bundle / 'assets/templates/concept-graph-labels.mjs', dist / 'captions.mjs')
    shutil.copy2(output / 'graph-option.json', dist / 'option.json')
    html = '''<!doctype html><style>body{margin:0;background:white}.slidev-page{width:960px;height:540px;padding:16px;box-sizing:border-box}</style>
<section class="slidev-page"><button id="replay">Replay</button><div id="chart"></div></section><section class="slidev-page" style="position:absolute;opacity:0"><div data-render-ready="false" style="width:40px;height:40px">Inactive slide</div></section>
<script type="module">
import * as echarts from '/echarts.mjs';
import {prepareColorsetOption,insetGraphArrowRoutes} from '/colorsets.mjs';
import {settleConceptGraphCaptions} from '/captions.mjs';
const option=await (await fetch('/option.json')).json(),el=document.getElementById('chart');
el.style.width='WIDTHpx';el.style.height='HEIGHTpx';
const chart=echarts.init(el,null,{renderer:'svg'});let step=0;
async function render(){el.dataset.renderReady='false';el.dataset.step=String(step);const next=structuredClone(option);next.series[0].links.at(-1).lineStyle.color=step?'#9e1b32':'#696969';chart.setOption(prepareColorsetOption(next,'colorset1'),true);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));insetGraphArrowRoutes(chart,3);settleConceptGraphCaptions(chart);el.dataset.renderReady='true'}
addEventListener('keydown',event=>{if(event.key==='ArrowRight'){step=Math.min(1,step+1);history.replaceState(null,'','/1?clicks='+step);render()}});
document.getElementById('replay').onclick=render;
await render();INJECT_FAILURE
</script>'''.replace('WIDTH', str(geometry['width'])).replace('HEIGHT', str(geometry['height']))
    (dist / 'index.html').write_text(html.replace('INJECT_FAILURE', ''), encoding='utf-8')
    reports = []
    for name in ['native', 'repeat']:
        target, report = capture(output / 'deck', output / name, clicks=1, settle_ms=400)
        assert target.is_file() and not report['pageErrors'] and report['serverClosed'], report
        assert_closed(report)
        assert len(report['states']) == 2 and report['replay'] == 'button'
        for state, frame in enumerate(report['states']):
            assert len(frame['roots']) == 1, frame
            assert any(record.get('step') == str(state) for record in frame['roots'][0]['readiness']), frame
            assert len(frame['roots'][0]['svgs']) == 1, frame
        for frame in [*report['states'], report['replayState'], report['resizedState'], report['reducedState']]:
            svg = frame['roots'][0]['svgs'][0]
            assert len(svg['nodes']) == 3 and len(svg['heads']) == 3, svg
            assert min(head['gap'] for head in svg['heads']) >= 2.4, svg
            labels = {label['text']: label for label in svg['labels']}
            for text in ['Input {a}', 'Review <raw>', 'Archive & verify']:
                assert labels[text]['fontSize'] >= 16, labels
            assert labels['Retest {b} & validate']['fontSize'] >= 14
        reports.append(report)
    assert [svg['nodes'] for frame in reports[0]['states'] for root in frame['roots'] for svg in root['svgs']] == [svg['nodes'] for frame in reports[1]['states'] for root in frame['roots'] for svg in root['svgs']]
    (dist / 'index.html').write_text(html.replace('INJECT_FAILURE', "throw new Error('Injected native capture failure')"), encoding='utf-8')
    target, rejected = capture(output / 'deck', output / 'page-error', clicks=0, settle_ms=400)
    assert rejected['pageErrors'] == ['Injected native capture failure'], rejected
    assert_closed(rejected)
    result = subprocess.run([sys.executable, str(bundle / 'scripts/capture_deck.py'), '--deck', 'deck', '--output-dir', 'cli-page-error', '--clicks', '0', '--settle-ms', '400'], cwd=output, capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 1 and (output / 'cli-page-error/capture.json').is_file(), (result.stdout, result.stderr)
    cli_error = json.loads((output / 'cli-page-error/capture.json').read_text(encoding='utf-8'))
    assert cli_error['pageErrors'] and cli_error['serverClosed']
    assert_closed(cli_error)
    try:
        capture(output / 'missing-deck', output / 'missing-build', clicks=0)
        raise AssertionError('A missing build must fail')
    except ValueError as error:
        assert 'Build the deck first' in str(error)
    result = subprocess.run([sys.executable, str(bundle / 'scripts/capture_deck.py'), '--deck', 'deck', '--output-dir', '../outside-workspace'], cwd=output, capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 2 and 'inside that workspace' in result.stderr
    summary = {'ok': True, 'nativeClicks': 2, 'repeatedGeometryStable': True, 'fullLiteralLabelsAndCompleteHeads': True, 'replayResizeReducedMotion': True, 'spaRouteAndQuerySupported': True, 'inactiveReadinessMarkersIgnored': True, 'serverPortsClosedAfterSuccessAndPageError': True, 'pageErrorsStillFailCli': True, 'missingBuildAndOutsideOutputRejected': True}
    (output / 'test-report.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
