#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent positive and adversarial tests for the shipped paint gates."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class PaintContracts(unittest.TestCase):
    def test_plantuml_source_normalization_preserves_literal_facts(self):
        sys.path.insert(0,str(ROOT / 'skills/plantuml-colorset-renderer/scripts'))
        from render_plantuml_directory import normalize_source_paints
        source='class Order #123456\nOrder --> Item : Literal #123456\nnote right: Fact #abcdef\nclass "Label #123456" as Label\n'
        normalized=normalize_source_paints(source,'colorset1')
        self.assertNotIn('class Order #123456',normalized)
        for fact in ('Literal #123456','Fact #abcdef','"Label #123456"'):
            self.assertIn(fact,normalized)
    def test_all_three_bundles_reject_and_normalize_without_changing_facts(self):
        for skill in ('mermaid','plantuml-colorset-renderer','echarts-animated-svg'):
            path=ROOT / 'skills' / skill / 'scripts/palette_paints.py'
            spec=importlib.util.spec_from_file_location('palette_'+skill,path)
            module=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            root=ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg"><style>#abcdef { fill: #123456; stroke: rgb(15,23,42); }</style><rect id="abcdef" width="47" fill="hsl(200,50%,40%)"/><text fill="#333e48">Exact 47</text><image href="data:image/png;base64,original"/></svg>')
            with self.assertRaises(ValueError): module.require_svg_palette(root,'colorset1')
            self.assertTrue(module.svg_paints(root,'colorset1',normalize=True))
            self.assertEqual(module.require_svg_palette(root,'colorset1'),'colorset1')
            self.assertEqual(root[1].get('id'),'abcdef')
            self.assertEqual(root[1].get('width'),'47')
            self.assertEqual(root[2].text,'Exact 47')
            self.assertEqual(root[3].get('href'),'data:image/png;base64,original')
            self.assertIn('#abcdef',root[0].text)
            reference=ET.fromstring('<svg><defs><linearGradient id="abcdef"><stop stop-color="#9e1b32"/></linearGradient></defs><path fill="url(#abcdef)"/><animate attributeName="x" values="0;10" fill="freeze"/></svg>')
            self.assertFalse(module.svg_paints(reference,'colorset1',normalize=True))
            self.assertEqual(reference[1].get('fill'),'url(#abcdef)')
            for body in ('<svg><rect fill="oklch(50% .2 230)"/></svg>','<svg><rect fill="invalidpaint"/></svg>','<svg><animate attributeName="fill" values="#9e1b32;#123456" fill="freeze"/></svg>'):
                with self.assertRaises(ValueError): module.require_svg_palette(ET.fromstring(body),'colorset1')
    def test_echarts_animator_rejects_off_palette_before_output(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'projects/colorset-audit/artifacts') as temp:
            folder=Path(temp)
            source=folder / 'source.svg'
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10" fill="#123456"/></svg>')
            output=folder / 'animated.svg'
            result=subprocess.run([sys.executable,str(ROOT / 'skills/echarts-animated-svg/scripts/animate_echarts_svg.py'),str(source),'--chart-type','bar','-o',str(output)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(output.exists())
    def test_every_published_svg_paint_fits_its_selected_set(self):
        sys.path.insert(0,str(ROOT / 'skills/mermaid/scripts'))
        from palette_paints import require_svg_palette
        checked=0
        for skill in ('mermaid','plantuml-colorset-renderer'):
            for path in (ROOT / 'skills' / skill / 'assets/examples').rglob('*.svg'):
                if 'node_modules' in path.parts: continue
                colorset='colorset1' if 'colorset1' in path.parts or 'plantuml-colorset-renderer-cs1' in path.parts else 'colorset2'
                require_svg_palette(ET.parse(path).getroot(),colorset)
                checked+=1
        self.assertGreater(checked,150)
if __name__=='__main__': unittest.main()
