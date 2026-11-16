#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Render diagram defaults and check readable geometry and visible terminals."""
import json
from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright
import build_contract_artifact as builder


class CompactDiagramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = sync_playwright().start()
        executable = cls.runtime.chromium.executable_path
        options = {} if Path(executable).is_file() else {"channel": "msedge"}
        cls.browser = cls.runtime.chromium.launch(**options)
        cls.directory = tempfile.TemporaryDirectory(prefix=".d3-compact-test-", dir=Path.cwd())

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.runtime.stop()
        cls.directory.cleanup()

    def render(self, kind, extra):
        args = builder.make_parser().parse_args([
            "--kind", kind, "--output", "diagram.html", "--decision-output", "decision.json",
            "--title", "Workflow", "--description", "Synthetic test relationships",
            "--route", "diagram", "--colorset", "colorset1", "--pattern-id", "d3-test",
            "--svg-id", "diagram", "--reason", "Geometry verification", *extra,
        ])
        html, _ = builder.build(args)
        source = Path(self.directory.name) / "diagram.html"
        source.write_text(html, encoding="utf-8")
        page = self.browser.new_page(viewport={"width": 1100, "height": 900})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(source.resolve().as_uri())
        page.wait_for_timeout(1200)
        self.assertFalse(errors, errors)
        return page

    def geometry(self, page):
        return page.evaluate("""() => {
          const svg=document.querySelector('svg'),vb=svg.viewBox.baseVal;
          const nodes=[...svg.querySelectorAll('.flow-node,.node')].filter(e=>e.tagName.toLowerCase()==='g').map(group=>{
            const text=group.querySelector('text'),shape=group.querySelector('rect,circle');
            const t=text.getBBox(),s=shape.getBBox(),m=group.transform.baseVal.consolidate().matrix;
            const move=b=>({x:b.x+m.e,y:b.y+m.f,w:b.width,h:b.height});
            return {id:text.textContent,text:move(t),shape:move(s),font:parseFloat(getComputedStyle(text).fontSize),r:shape.tagName==='circle'?+shape.getAttribute('r'):null,cx:m.e,cy:m.f};
          });
          const links=[...svg.querySelectorAll('path.link')].map(path=>{
            const length=path.getTotalLength(),point=k=>{const p=path.getPointAtLength(k*length);return {x:p.x,y:p.y}};
            return {source:path.dataset.source,target:path.dataset.target,d:path.getAttribute('d'),marker:path.getAttribute('marker-end'),start:point(0),end:point(1),samples:Array.from({length:51},(_,i)=>point(i/50)),length};
          });
          return {width:vb.width,height:vb.height,nodes,links};
        }""")

    def assert_readable(self, data):
        self.assertTrue(data["nodes"])
        for node in data["nodes"]:
            self.assertGreaterEqual(node["font"], 16)
            t, s = node["text"], node["shape"]
            self.assertGreaterEqual(t["x"], s["x"])
            self.assertGreaterEqual(t["y"], s["y"])
            self.assertLessEqual(t["x"] + t["w"], s["x"] + s["w"])
            self.assertLessEqual(t["y"] + t["h"], s["y"] + s["h"])
        for i, a in enumerate(data["nodes"]):
            for b in data["nodes"][i+1:]:
                if a["r"] and b["r"]:
                    distance = ((a["cx"]-b["cx"])**2+(a["cy"]-b["cy"])**2)**.5
                    self.assertGreater(distance, a["r"] + b["r"])
                else:
                    x, y = a["shape"], b["shape"]
                    self.assertTrue(x["x"]+x["w"]<y["x"] or y["x"]+y["w"]<x["x"] or x["y"]+x["h"]<y["y"] or y["y"]+y["h"]<x["y"])
        by_id = {node["id"]: node for node in data["nodes"]}
        for link in data["links"]:
            self.assertTrue(link["marker"])
            self.assertGreater(link["length"], 10)
            for side, endpoint in (("source", "start"), ("target", "end")):
                node, point = by_id[link[side]], link[endpoint]
                if node["r"]:
                    distance=((point["x"]-node["cx"])**2+(point["y"]-node["cy"])**2)**.5
                    self.assertGreaterEqual(distance, node["r"]+3.9)
                else:
                    s=node["shape"]
                    self.assertFalse(s["x"]<=point["x"]<=s["x"]+s["w"] and s["y"]<=point["y"]<=s["y"]+s["h"])
            for node in data["nodes"]:
                if node["id"] in (link["source"],link["target"]):
                    continue
                for point in link["samples"]:
                    if node["r"]:
                        distance=((point["x"]-node["cx"])**2+(point["y"]-node["cy"])**2)**.5
                        self.assertGreater(distance,node["r"]+2)
                    else:
                        s=node["shape"]
                        self.assertFalse(s["x"]<=point["x"]<=s["x"]+s["w"] and s["y"]<=point["y"]<=s["y"]+s["h"])

    def test_flow_content_bounds_and_fixed_canvas(self):
        flags=["--flow-node","A","--flow-node","Review details","--flow-node","C","--link","A->Review details","--link-value","4","--link","Review details->C","--link-value","9"]
        page=self.render("flow",flags)
        data=self.geometry(page)
        self.assert_readable(data)
        self.assertLess(data["width"],500)
        self.assertLess(data["height"],180)
        page.set_viewport_size({"width":360,"height":720})
        self.assertGreaterEqual(page.locator("svg").bounding_box()["width"],data["width"])
        page.close()
        page=self.render("flow",[*flags,"--width","900","--height","300"])
        data=self.geometry(page)
        self.assertEqual((data["width"],data["height"]),(900,300))
        self.assert_readable(data)
        page.close()

    def test_flow_skip_return_parallel_and_self_routes(self):
        flags=["--flow-node","A","--flow-node","B","--flow-node","C"]
        for source,target in [("A","B"),("A","C"),("C","A"),("A","B"),("B","B")]:
            flags += ["--link",f"{source}->{target}","--link-value","3"]
        page=self.render("flow",flags)
        data=self.geometry(page)
        self.assert_readable(data)
        self.assertEqual(len({link["d"] for link in data["links"]}),5)
        page.close()

    def test_network_terminal_clearance_and_label_fit(self):
        flags=["--node","Gateway=primary","--node","Queue=muted","--node","Long service name=neutral"]
        for source,target in [("Gateway","Queue"),("Queue","Gateway"),("Queue","Long service name"),("Gateway","Gateway")]:
            flags += ["--link",f"{source}->{target}"]
        page=self.render("network",flags)
        data=self.geometry(page)
        self.assert_readable(data)
        self.assertLess(data["width"]*data["height"],900*520)
        self.assertEqual(len({link["d"] for link in data["links"]}),4)
        page.close()

    def test_chart_dimensions_remain_unchanged(self):
        page=self.render("bar",["--item","Alpha=12","--item","Beta=8"])
        vb=page.locator("svg").get_attribute("viewBox")
        self.assertEqual(vb,"0 0 900 520")
        page.close()

    def test_single_and_two_node_networks(self):
        for flags in [
            ["--node","Solo=primary","--link","Solo->Solo"],
            ["--node","Input=primary","--node","Output=muted","--link","Input->Output","--link","Output->Input","--link","Input->Output"],
        ]:
            page=self.render("network",flags)
            data=self.geometry(page)
            self.assert_readable(data)
            self.assertEqual(len({link["d"] for link in data["links"]}),len(data["links"]))
            page.close()


if __name__ == "__main__":
    unittest.main()
