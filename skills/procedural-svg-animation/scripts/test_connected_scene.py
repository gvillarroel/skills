#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Check connected-scene semantics, packing and moving arrow clearance."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright
from build_connected_scene import NS, build_scene, validate


def config(labels=None, **overrides):
    return {"labels": labels or ["Source", "Check", "Destination"], "palette": "colorset1", "seed": 73021, "duration_ms": 6000, "width": None, "height": None, "include_return": False, **overrides}


class SceneTests(unittest.TestCase):
    def test_content_dimensions_and_fixed_canvas(self):
        root = build_scene(config())
        self.assertEqual(root.get("height"), "72")
        self.assertLess(int(root.get("width")), 500)
        self.assertEqual(root.findall(f".//{{{NS}}}text")[0].text, "Source")
        fixed = build_scene(config(width=900, height=300))
        self.assertEqual(fixed.get("viewBox"), "0 0 900 300")
        with self.assertRaisesRegex(ValueError, "shrinking"):
            build_scene(config(width=120, height=100))

    def test_invalid_inputs_and_determinism(self):
        first = ET.tostring(build_scene(config()), encoding="unicode")
        self.assertEqual(first, ET.tostring(build_scene(config()), encoding="unicode"))
        for labels in (["A"], ["A", "A"], ["A", ""]):
            with self.assertRaises(ValueError):
                build_scene(config(labels))

    def test_validator_rejects_semantic_arrow_and_motion_mutations(self):
        with tempfile.TemporaryDirectory(prefix=".scene-test-", dir=Path.cwd()) as directory:
            path = Path(directory) / "scene.svg"
            root = build_scene(config(include_return=True))
            path.write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
            self.assertEqual(validate(path)["routes"], 3)
            for target, attribute, value in [
                (".//{svg}path[@data-source]", "marker-end", "none"),
                (".//{svg}path[@data-source]", "data-target", "Other"),
                (".//{svg}animateMotion", "keyPoints", "0;0;1;1;0"),
                (".//{svg}rect[@rx]", "width", "2"),
            ]:
                changed = build_scene(config(include_return=True))
                changed.find(target.replace("{svg}", f"{{{NS}}}")).set(attribute, value)
                path.write_text(ET.tostring(changed, encoding="unicode"), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "construction contract"):
                    validate(path)

    def test_browser_labels_routes_and_motion_envelope(self):
        with tempfile.TemporaryDirectory(prefix=".scene-browser-", dir=Path.cwd()) as directory, sync_playwright() as runtime:
            options = {} if Path(runtime.chromium.executable_path).is_file() else {"channel": "msedge"}
            browser = runtime.chromium.launch(**options)
            page = browser.new_page()
            for labels, return_route in [(["Source", "Check", "Destination"], False), (["Wide WWW stage", "Verify requested document", "Release"], True)]:
                path = Path(directory) / "scene.svg"
                path.write_text(ET.tostring(build_scene(config(labels, include_return=return_route)), encoding="unicode"), encoding="utf-8")
                page.goto(path.resolve().as_uri())
                for time in (0, .1, 1.5, 2.5, 3.5, 4.5, 5.9, 6):
                    issues = page.evaluate("""t=>{
                      const svg=document.querySelector('svg');svg.pauseAnimations();svg.setCurrentTime(t);
                      const issues=[],nodes=[...document.querySelectorAll('#scene-nodes>g')].map(g=>({label:g.dataset.label,r:g.querySelector('rect').getBoundingClientRect(),text:g.querySelector('text').getBoundingClientRect()}));
                      for(const n of nodes)if(n.text.left<n.r.left||n.text.right>n.r.right||n.text.top<n.r.top||n.text.bottom>n.r.bottom)issues.push('label '+n.label);
                      const heads=[...document.querySelectorAll('#scene-routes path')].map(p=>{const q=p.getPointAtLength(p.getTotalLength()),m=p.getScreenCTM(),v=new DOMPoint(q.x,q.y).matrixTransform(m);return v});
                      for(const token of document.querySelectorAll('circle[data-route]'))if(+getComputedStyle(token).opacity>.1){const r=token.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;for(const n of nodes)if(x+r.width/2>n.r.left&&x-r.width/2<n.r.right&&y+r.height/2>n.r.top&&y-r.height/2<n.r.bottom)issues.push('token hits '+n.label);for(const h of heads)if(Math.hypot(x-h.x,y-h.y)<14)issues.push('token hides arrow')}
                      return issues;
                    }""", time)
                    self.assertFalse(issues, (time, issues))
                page.emulate_media(reduced_motion="reduce")
                self.assertEqual(page.locator(".psvg-motion-layer").evaluate("e=>getComputedStyle(e).display"), "none")
                self.assertTrue(page.locator("#scene-nodes").is_visible())
                page.emulate_media(reduced_motion="no-preference")
            browser.close()


if __name__ == "__main__":
    unittest.main()
