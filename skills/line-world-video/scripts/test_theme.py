#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Exercise borderless item surfaces, white group shells and reversible focus."""
import os, unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
SKILL=Path(__file__).resolve().parent.parent

class ThemeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pw=sync_playwright().start();paths=sorted((Path(os.environ.get('LOCALAPPDATA',''))/'ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True);cls.browser=cls.pw.chromium.launch(executable_path=str(paths[0]) if paths else None,headless=True);cls.page=cls.browser.new_page(viewport={'width':1000,'height':600})
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop()
 def setUp(self):
  self.page.set_content('<style>body{margin:0}text{font:24px Arial;fill:#333e48}</style><svg id="stage" width="1000" height="600"><g id="a"><rect id="face" data-lw-surface="item" x="100" y="100" width="160" height="80" fill="white" stroke="#828282"/><text id="inside" x="120" y="145">Model</text><text id="outside" x="100" y="230">Context</text></g><g id="container"><rect id="shell" data-lw-surface="group" x="400" y="80" width="400" height="300"/><rect id="child" data-lw-surface="item" x="450" y="180" width="100" height="60" fill="white"/><text id="group-label" x="430" y="130">Group</text></g></svg>');self.page.add_style_tag(path=str(SKILL/'assets/runtime/theme.css'));self.page.add_script_tag(path=str(SKILL/'assets/runtime/theme.js'));self.page.evaluate('LineWorldTheme.finish(document.querySelector("#stage"))')
 def values(self,ids):return self.page.evaluate('ids=>Object.fromEntries(ids.map(id=>{const e=document.getElementById(id),s=getComputedStyle(e);return[id,{fill:s.fill,stroke:s.stroke,width:s.strokeWidth}]}))',ids)
 def test_items_are_gray_borderless_and_group_is_white(self):
  x=self.values(['face','shell']);self.assertEqual(x['face'],{'fill':'rgb(231, 231, 231)','stroke':'none','width':'0px'});self.assertEqual(x['shell']['fill'],'rgb(255, 255, 255)');self.assertEqual(x['shell']['stroke'],'rgb(130, 130, 130)');self.assertTrue(self.page.evaluate('LineWorldTheme.audit(document.querySelector("#stage")).ok'));self.page.locator('#face').evaluate("e=>{e.style.setProperty('stroke','red','important');e.style.setProperty('stroke-width','2px','important')}");self.assertFalse(self.page.evaluate('LineWorldTheme.audit(document.querySelector("#stage")).ok'))
 def test_primary_item_has_white_internal_and_red_external_text(self):
  self.page.evaluate('LineWorldTheme.focus(document.querySelector("#stage"),document.querySelector("#a"))');x=self.values(['face','inside','outside']);self.assertEqual(x['face']['fill'],'rgb(158, 27, 50)');self.assertEqual(x['face']['stroke'],'none');self.assertEqual(x['inside']['fill'],'rgb(255, 255, 255)');self.assertEqual(x['outside']['fill'],'rgb(158, 27, 50)')
 def test_group_focus_keeps_children_gray_and_shell_white(self):
  self.page.evaluate('LineWorldTheme.focus(document.querySelector("#stage"),document.querySelector("#container"))');x=self.values(['shell','child']);self.assertEqual(x['shell']['fill'],'rgb(255, 255, 255)');self.assertEqual(x['shell']['stroke'],'rgb(158, 27, 50)');self.assertEqual(x['child']['fill'],'rgb(231, 231, 231)');self.assertEqual(x['child']['stroke'],'none')
 def test_secondary_item_has_dark_gray_face_and_white_label(self):
  self.page.evaluate('LineWorldTheme.focus(document.querySelector("#stage"),document.querySelector("#a"),"secondary")');x=self.values(['face','inside','outside']);self.assertEqual(x['face']['fill'],'rgb(105, 105, 105)');self.assertEqual(x['inside']['fill'],'rgb(255, 255, 255)');self.assertEqual(x['outside']['fill'],'rgb(105, 105, 105)')
 def test_text_target_resolves_its_containing_small_face(self):
  self.page.evaluate('LineWorldTheme.focus(document.querySelector("#stage"),document.querySelector("#inside"))');x=self.values(['face','inside','outside']);self.assertEqual(x['face']['fill'],'rgb(158, 27, 50)');self.assertEqual(x['inside']['fill'],'rgb(255, 255, 255)');self.assertEqual(x['outside']['fill'],'rgb(51, 62, 72)')
 def test_shape_target_includes_its_sibling_internal_label(self):
  self.page.locator('#inside').evaluate('e=>e.innerHTML=\'<tspan style="fill:#333e48!important">Model</tspan>\'');self.page.evaluate('LineWorldTheme.focus(document.querySelector("#stage"),document.querySelector("#face"))');self.assertEqual(self.values(['inside'])['inside']['fill'],'rgb(255, 255, 255)');self.assertEqual(self.page.locator('#inside tspan').evaluate('e=>getComputedStyle(e).fill'),'rgb(255, 255, 255)');self.assertEqual(self.values(['outside'])['outside']['fill'],'rgb(51, 62, 72)')
 def test_encoded_gray_and_category_colors_are_preserved(self):
  self.page.locator('#a').evaluate('e=>e.insertAdjacentHTML("beforeend",\'<rect id="data" data-lw-surface="item" data-encoding="pixels" x="300" y="100" width="20" height="20" fill="#696969"/><rect id="category" data-lw-surface="item" data-encoding="category" x="330" y="100" width="20" height="20" fill="#007298"/>\')');self.page.evaluate('LineWorldTheme.finish(document.querySelector("#stage"));LineWorldTheme.focus(document.querySelector("#stage"),document.querySelector("#a"))');x=self.values(['data','category']);self.assertEqual(x['data']['fill'],'rgb(105, 105, 105)');self.assertEqual(x['category']['fill'],'rgb(0, 114, 152)');self.assertTrue(all(v['stroke']=='none' for v in x.values()))
 def test_nested_native_label_recovers_after_manual_repaint(self):
  self.page.locator('#inside').evaluate('e=>e.innerHTML=\'<tspan id="native-span" style="fill:#9e1b32!important">Model</tspan>\'');self.page.locator('#face').evaluate('e=>e.style.setProperty("fill","#9e1b32","important")');self.page.evaluate('LineWorldTheme.contrast(document.querySelector("#stage"))');self.assertEqual(self.values(['native-span'])['native-span']['fill'],'rgb(255, 255, 255)');self.page.locator('#face').evaluate('e=>e.style.setProperty("fill","#e7e7e7","important")');self.page.evaluate('LineWorldTheme.contrast(document.querySelector("#stage"))');self.assertEqual(self.values(['native-span'])['native-span']['fill'],'rgb(51, 62, 72)')
 def test_unbound_value_label_recovers_when_focus_moves(self):
  self.page.locator('#a').evaluate('e=>e.insertAdjacentHTML("beforeend",\'<text id="value" x="230" y="160">8</text>\')');self.page.evaluate('LineWorldTheme.focus(document.querySelector("#stage"),document.querySelector("#face"));LineWorldTheme.contrast(document.querySelector("#stage"))');self.assertEqual(self.values(['value'])['value']['fill'],'rgb(255, 255, 255)');self.page.evaluate('LineWorldTheme.focus(document.querySelector("#stage"),null);LineWorldTheme.contrast(document.querySelector("#stage"))');self.assertEqual(self.values(['value'])['value']['fill'],'rgb(51, 62, 72)')
 def test_foreign_object_html_label_uses_color_and_restores(self):
  self.page.locator('#inside').evaluate('e=>e.remove()');self.page.locator('#a').evaluate('e=>e.insertAdjacentHTML("beforeend",\'<foreignObject x="110" y="115" width="140" height="45"><div xmlns="http://www.w3.org/1999/xhtml"><span id="html-label" style="color:#333e48!important">Model</span></div></foreignObject>\')');self.page.evaluate('LineWorldTheme.finish(document.querySelector("#stage"));LineWorldTheme.focus(document.querySelector("#stage"),document.querySelector("#a"))');self.assertEqual(self.page.locator('#html-label').evaluate('e=>getComputedStyle(e).color'),'rgb(255, 255, 255)');self.page.evaluate('LineWorldTheme.focus(document.querySelector("#stage"),null)');self.assertEqual(self.page.locator('#html-label').evaluate('e=>getComputedStyle(e).color'),'rgb(51, 62, 72)')
 def test_native_css_specificity_is_overridden_and_restored(self):
  self.page.add_style_tag(content='#stage #face{fill:white!important;stroke:black!important;stroke-width:8px!important}');self.page.evaluate('LineWorldTheme.finish(document.querySelector("#stage"));LineWorldTheme.focus(document.querySelector("#stage"),document.querySelector("#a"));LineWorldTheme.focus(document.querySelector("#stage"),null)');x=self.values(['face']);self.assertEqual(x['face']['stroke'],'none');self.assertEqual(x['face']['fill'],'rgb(231, 231, 231)')
 def test_repeated_seek_restores_markup_and_geometry(self):
  result=self.page.evaluate('''()=>{const r=document.querySelector('#stage'),a=document.querySelector('#a'),b=document.querySelector('#container'),before=document.querySelector('#face').getAttribute('width');LineWorldTheme.focus(r,a);const one=r.outerHTML;LineWorldTheme.focus(r,b);LineWorldTheme.focus(r,a);return{same:one===r.outerHTML,width:before===document.querySelector('#face').getAttribute('width'),animations:document.getAnimations().length}}''');self.assertTrue(result['same']);self.assertTrue(result['width']);self.assertEqual(result['animations'],0)

if __name__=='__main__':unittest.main()
