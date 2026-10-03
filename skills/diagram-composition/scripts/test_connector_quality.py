#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Boundary routing and browser controls for real visual failure modes."""

import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
from audit_diagram import launch_browser, run
from build_panels import build
from compose_diagram import compose, resolve_objects
from route_connectors import anchor, collision_cost, radial_anchor, route, segment_enters, validate_route
from visual_quality import QUALITY
from playwright.sync_api import sync_playwright
from test_composition import panel


class RouteTests(unittest.TestCase):
    def test_crossing_at_visibility_grid_vertex_is_not_free(self):
        previous=[[[100,50],[200,50]]]
        self.assertGreater(collision_cost([150,0],[150,50],previous),1000)
        self.assertGreater(collision_cost([150,50],[150,100],previous),1000)
        self.assertEqual(collision_cost([100,0],[100,50],previous),0)

    def test_route_goes_around_unrelated_object(self):
        objects={"source":{"box":[20,70,80,60]},"block":{"box":[140,50,120,100]},"target":{"box":[300,70,80,60]}}
        bindings=({"object":"source","side":"right"},{"object":"target","side":"left"})
        points=route([100,100],[300,100],objects,bindings,canvas=(400,200))
        validate_route(points,objects,bindings)
        self.assertGreater(len(points),2)
        self.assertFalse(any(segment_enters(a,b,objects["block"]["box"]) for a,b in zip(points,points[1:])))

    def test_wrong_side_manual_route_rejected(self):
        objects={"target":{"box":[180,70,80,60]}}
        with self.assertRaisesRegex(ValueError,"outside|enters"):
            route([50,100],[180,100],objects,(None,{"object":"target","side":"left"}),canvas=(400,200),via=[[280,100]])

    def test_nested_container_allows_entry_to_child(self):
        objects={"container":{"box":[130,20,260,160],"kind":"container"},"target":{"box":[240,70,100,60]}}
        points=route([30,100],[240,100],objects,(None,{"object":"target","side":"left"}),canvas=(420,220))
        self.assertEqual(points,[[30,100],[240,100]])

    def test_parallel_routes_do_not_coincide(self):
        first=route([50,40],[350,150],{},canvas=(400,200))
        second=route([50,60],[350,130],{},canvas=(400,200),previous=[first])
        self.assertNotEqual(first[1:-1],second[1:-1])

    def test_structured_ports_derive_from_object_bounds(self):
        objects,ports,bindings=resolve_objects({"objects":{"node":{"box":[.1,.2,.4,.3]}},"ports":{"entry":{"object":"node","side":"left"}}})
        self.assertEqual(ports["entry"],[.1,.35])
        self.assertEqual(bindings["entry"]["object"],"node")
        with self.assertRaisesRegex(ValueError,"known object"):
            resolve_objects({"ports":{"bad":{"object":"missing","side":"left"}}})

    def test_radial_contacts_rectangles_and_ellipses(self):
        box=[20,30,100,60]
        p=radial_anchor(box,[220,200])
        self.assertTrue(abs(p[0]-120)<1e-6 or abs(p[1]-90)<1e-6)
        p=radial_anchor(box,[220,200],"ellipse")
        self.assertAlmostEqual(((p[0]-70)/50)**2+((p[1]-60)/30)**2,1)

    def test_no_route_does_not_cross_a_solid_barrier(self):
        with self.assertRaisesRegex(ValueError,"No unobstructed"):
            route([30,100],[370,100],{"wall":{"box":[180,0,40,200]}},canvas=(400,200))


class QualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw=sync_playwright().start();cls.browser=launch_browser(cls.pw)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()

    def check(self,content):
        page=self.browser.new_page()
        try:
            page.set_content('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="300"><rect width="500" height="300" fill="white"/><g data-panel-id="p">'+content+'</g></svg>')
            return page.evaluate(QUALITY,{"report":{"panels":[{"id":"p"}],"semanticColors":{"source":"#007298"}}})
        finally:page.close()

    def box(self,fill="#f7f7f7",stroke="#007298",kind="node"):
        return f'<rect x="100" y="60" width="240" height="120" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2.4" data-node-id="source" data-node-kind="{kind}" data-concept-id="source" data-color-concept="source" data-color-channel="stroke"/>'

    def wire(self,d,attrs='data-open-start="Supplied upstream connection"'):
        return f'<path d="{d}" fill="none" stroke="#696969" stroke-width="2" data-connector="native" {attrs}/>'

    def test_floating_native_endpoint_fails_and_actual_rounded_contact_passes(self):
        bad=self.check(self.box()+self.wire("M20 120H94"))
        self.assertIn('connector-floating-endpoint',{i['kind'] for i in bad['issues']})
        # A bounding-box corner is outside this rounded rect's actual surface.
        bad=self.check(self.box()+self.wire("M20 60H100"))
        self.assertIn('connector-floating-endpoint',{i['kind'] for i in bad['issues']})
        good=self.check(self.box()+self.wire("M20 120H100"))
        self.assertFalse(good['issues'],good)
        self.assertEqual(len(good['internalContacts']),1)

    def test_native_owner_binding_and_named_open_terminal(self):
        good=self.check(self.box()+self.wire('M20 120H100','data-open-start="External input" data-to-node="source"'))
        self.assertFalse(good['issues'],good)
        self.assertEqual(good['openTerminals'][0]['reason'],'External input')
        bad=self.check(self.box()+self.wire('M20 120H100','data-open-start="External input" data-to-node="wrong"'))
        self.assertIn('connector-floating-endpoint',{i['kind'] for i in bad['issues']})

    def test_ellipse_contact_uses_curve_instead_of_bounding_box(self):
        node='<ellipse cx="200" cy="120" rx="80" ry="40" fill="white" stroke="#555" data-node-id="oval"/>'
        self.assertFalse(self.check(node+self.wire('M20 120H120'))['issues'])
        bad=self.check(node+self.wire('M20 90H120'))
        self.assertIn('connector-floating-endpoint',{i['kind'] for i in bad['issues']})

    def test_visible_intrusion_fails_but_hidden_background_wire_passes(self):
        wire=self.wire("M20 90H200")
        bad=self.check(self.box()+wire)
        self.assertIn("connector-object-intrusion",{i["kind"] for i in bad["issues"]})
        good=self.check(wire+self.box())
        self.assertNotIn("connector-object-intrusion",{i["kind"] for i in good["issues"]})

    def test_terminal_contact_and_nested_container_are_allowed(self):
        result=self.check(self.box()+self.wire("M20 120H100"))
        self.assertFalse(result["issues"],result)
        result=self.check(self.box(kind="container")+self.wire("M20 90H200"))
        self.assertNotIn("connector-object-intrusion",{i["kind"] for i in result["issues"]})

    def test_transparent_surface_does_not_hide_wiring(self):
        result=self.check(self.wire("M20 90H200")+self.box(fill="none"))
        self.assertIn("connector-object-intrusion",{i["kind"] for i in result["issues"]})

    def test_correct_border_cannot_cover_conflicting_fill(self):
        self.assertIn("semantic-color-conflicting-fill",{i["kind"] for i in self.check(self.box(fill="#ff9633"))["issues"]})
        self.assertFalse(self.check(self.box(fill="#cdf3ff"))["issues"])

    def test_covered_accent_fails(self):
        result=self.check(self.box()+'<rect x="96" y="56" width="248" height="128" fill="white"/>')
        self.assertIn("semantic-color-occluded",{i["kind"] for i in result["issues"]})

    def test_contrast_uses_node_background(self):
        result=self.check(self.box()+'<text x="120" y="125" font-size="18" fill="#cfcfcf">Source</text>')
        self.assertIn("text-low-contrast",{i["kind"] for i in result["issues"]})
        result=self.check(self.box(fill="#007298")+'<text x="120" y="125" font-size="18" fill="white">Source</text>')
        self.assertNotIn("text-low-contrast",{i["kind"] for i in result["issues"]})

    def test_crossings_overlap_and_internal_text_interference(self):
        for content,kind in ((self.wire("M20 120H400")+self.wire("M200 20V250"),"connector-crossing"),
                            (self.wire("M20 120H400")+self.wire("M50 120H300"),"connector-overlap"),
                            ('<text x="100" y="125" font-size="18">Source</text>'+self.wire("M20 120H400"),"connector-text-interference")):
            with self.subTest(kind=kind):self.assertIn(kind,{i["kind"] for i in self.check(content)["issues"]})


class ComposedRouteTests(unittest.TestCase):
    def test_draft_compose_saves_failure_without_publishing_a_stale_figure(self):
        with tempfile.TemporaryDirectory(prefix='compose-inspect-',dir=Path.cwd()) as tmp:
            directory=Path(tmp)
            spec={'version':1,'title':'Missing source','thesis':'Persist the draft finding.',
                  'canvas':{'width':1000,'height':440,'displayWidth':1000,'minTextPx':14,'margin':24,'gap':48,'titleHeight':60,'footerHeight':24},
                  'grid':{'columns':[1],'rows':[1]},'concepts':[], 'panels':[panel('missing',1,1,1,1)],'links':[]}
            (directory/'plan.json').write_text(json.dumps(spec),encoding='utf-8')
            command=[sys.executable,str(Path(__file__).with_name('compose_diagram.py')),'compose','--spec',str(directory/'plan.json'),
                     '--output',str(directory/'figure.svg'),'--report',str(directory/'report.json')]
            draft=subprocess.run([*command,'--inspect'],capture_output=True,text=True)
            self.assertEqual(draft.returncode,0,draft.stdout+draft.stderr)
            self.assertFalse(json.loads((directory/'report.json').read_text())['ok'])
            self.assertFalse((directory/'figure.svg').exists())
            final=subprocess.run([*command,'--overwrite'],capture_output=True,text=True)
            self.assertEqual(final.returncode,1)

    def test_measure_imported_shapes_with_offset_viewbox(self):
        with tempfile.TemporaryDirectory(prefix="measured-objects-",dir=Path.cwd()) as tmp:
            directory=Path(tmp)
            source=directory/'source.svg'
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="10 20 400 240">'
                '<rect x="50" y="60" width="180" height="72" rx="6" data-node-id="card"/>'
                '<ellipse cx="330" cy="140" rx="50" ry="30" data-node-id="archive"/></svg>',encoding='utf-8')
            result=run(SimpleNamespace(command='measure',input=source,output=None,report=directory/'objects.json',overwrite=False))
            self.assertTrue(result['ok'])
            self.assertEqual(result['objects']['archive']['shape'],'ellipse')
            for actual,expected in zip(result['objects']['card']['box'],[.1,1/6,.45,.3]):self.assertAlmostEqual(actual,expected)
            self.assertEqual(result['ports']['archive-left'],{'object':'archive','side':'left'})

    def test_native_bound_ports_survive_composition_and_browser_audit(self):
        with tempfile.TemporaryDirectory(prefix="connector-quality-",dir=Path.cwd()) as tmp:
            directory=Path(tmp)
            panels=[]
            for name,column in (("first",1),("second",2)):
                p=panel(name,1,column,1,1);p["source"]=name+'.svg';p["ports"]={}
                p["diagram"]={"type":"boundary","id":"room","label":"Archive","nodes":[{"id":"source","label":"Source","concept":"engine"}]}
                panels.append(p)
            spec={"version":1,"title":"Same source in two views","thesis":"Connect one semantic identity.",
                "canvas":{"width":1000,"height":440,"displayWidth":1000,"minTextPx":14,"margin":24,"gap":48,"titleHeight":60,"footerHeight":24},
                "grid":{"columns":[1,1],"rows":[1]},"concepts":[{"id":"engine","label":"Source","color":"#007298"}],"panels":panels,
                "links":[{"id":"same-source","from":"first.source-right","to":"second.source-left","relation":"same source","label":"","directed":False}]}
            plan,assets,_=build(spec,directory)
            for path,content in assets:path.write_text(content,encoding="utf-8")
            svg,report=compose(plan,directory/'plan.json')
            (directory/'figure.svg').write_text(svg,encoding="utf-8")
            result=run(SimpleNamespace(command="audit",input=directory/'figure.svg',output=None,report=directory/'audit.json',screenshot=directory/'preview.png',overwrite=True))
            self.assertTrue(result['ok'],result['issues'])
            self.assertEqual(len(result['visualQuality']['contacts']),2)
            self.assertTrue(all(c['error']<.01 and c['outward']>0 for c in result['visualQuality']['contacts']))


if __name__=='__main__':unittest.main()
