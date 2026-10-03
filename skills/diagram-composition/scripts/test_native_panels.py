#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Native family controls, real browser layout, and text-budget rejection."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
from build_panels import Renderer, build
from compose_diagram import compose
from audit_diagram import run
from test_composition import panel
from render_diagram import render


DATA = {
    "hub": {"type":"hub","center":{"id":"workspace","label":"Shared workspace","icon":"library"},
        "peers":[{"id":"editor","label":"Editor","icon":"editor"},{"id":"assistant","label":"Assistant","icon":"assistant"},{"id":"ci","label":"CI runner","icon":"runner"}]},
    "matrix": {"type":"matrix","columns":["Tool","Source","Propose","Builds"],"columnWeights":[1.5,1,1,1],
        "rows":[{"id":"editor","label":"Editor","icon":"editor","values":["R/W","—","—"]},
                {"id":"assistant","label":"Assistant","values":["R","P","—"]},
                {"id":"ci","label":"CI runner","values":["R","—","B"]}],"note":"R read · W write · P propose · B publish"},
    "taxonomy": {"type":"taxonomy","root":"Seed library","groups":[
        {"id":"grain","label":"Grains","items":["Oats","Barley"],"color":"#007298"},
        {"id":"legume","label":"Legumes","items":["Peas","Beans"],"color":"#9e1b32"}]},
    "cycle": {"type":"cycle","closed":True,"steps":[{"id":i,"label":label,"icon":icon} for i,label,icon in [
        ("borrow","Borrow seeds","person"),("grow","Grow plants","plant"),("divide","Keep a portion","seed"),
        ("return","Return remainder","library"),("inspect","Inspect packets","inspect"),("shelve","Shelve seeds","shelf")]]},
    "boundary": {"type":"boundary","label":"Shared workspace","nodes":[
        {"id":"source","label":"Source","detail":"All peers read; editor writes"},
        {"id":"proposals","label":"Proposals","detail":"Assistant proposes","icon":"assistant"},
        {"id":"review","label":"Human review","detail":"Before source changes","icon":"review"},
        {"id":"builds","label":"Build results","detail":"CI publishes","icon":"runner"}],
        "groups":[{"id":"review-gate","label":"Review boundary","nodes":["proposals","review"]}],
        "relations":[{"from":"proposals","to":"review"},{"from":"review","to":"source"}]}}


class NativeTests(unittest.TestCase):
    def test_complete_portrait_pipeline_with_elliptical_enclosed_hub(self):
        with tempfile.TemporaryDirectory(prefix='native-portrait-',dir=Path.cwd()) as tmp:
            directory=Path(tmp)
            top=panel('comparison',1,1,1,2);left=panel('connectivity',2,1,1,1);right=panel('integrated',2,2,1,1)
            peers=[{'id':'radio','label':'Radio','concept':'radio'},{'id':'optical','label':'Optical','concept':'optical'}]
            top['diagram']={'type':'matrix','columns':['Station','Produces','Stored as'],
                            'rows':[{**peers[0],'values':['spectra','FITS']},{**peers[1],'values':['images','TIFF']}]}
            left['diagram']={'type':'hub','center':{'id':'archive','label':'Archive'},'peers':peers}
            right['diagram']={'type':'hub','enclosure':{'id':'observatory','label':'Observatory'},
                              'center':{'id':'archive','label':'Archive'},'peers':[{**p,'shape':'ellipse'} for p in peers]}
            for p in (top,left,right):p.update(source='panels/'+p['id']+'.svg',ports={},concepts=['radio','optical'])
            spec={'version':1,'title':'Two stations and their archive','thesis':'Compare outputs and show actual shared connections.',
                  'canvas':{'width':900,'height':1040,'displayWidth':900,'minTextPx':15,'margin':24,'gap':48,'titleHeight':60,'footerHeight':24},
                  'grid':{'columns':[1,1],'rows':[.36,.64]},
                  'concepts':[{'id':'radio','label':'Radio','color':'#007298'},{'id':'optical','label':'Optical','color':'#9e1b32'}],
                  'panels':[top,left,right],
                  'links':[{'id':c+'-identity','from':'comparison.'+c+'-right','to':'integrated.'+c+'-left',
                            'relation':'Same station','label':'','directed':False} for c in ('radio','optical')]}
            brief=directory/'brief.json';brief.write_text(json.dumps(spec),encoding='utf-8')
            result=render(brief,directory/'out')
            self.assertTrue(result['ok'],result)
            audit=json.loads((directory/'out/audit.json').read_text())
            self.assertEqual(len(audit['visualQuality']['contacts']),4)
            self.assertEqual(len(audit['visualQuality']['internalContacts']),8)
            plan=json.loads((directory/'out/plan.json').read_text())
            self.assertEqual(plan['panels'][2]['objects']['radio']['shape'],'ellipse')
            self.assertTrue((directory/'out/preview.png').is_file())
            self.assertTrue(render(brief,directory/'out',True)['ok'])

    def test_ellipse_budget_rejects_spilling_text(self):
        r=Renderer(300,200,18,Path.cwd())
        with self.assertRaisesRegex(ValueError,'budget|height|width'):
            r.card({'id':'long','label':'A long archive label','shape':'ellipse'},10,10,90,45)

    def test_complete_pipeline_preserves_brief_and_existing_outputs(self):
        with tempfile.TemporaryDirectory(prefix='native-owned-',dir=Path.cwd()) as tmp:
            directory=Path(tmp)
            p=panel('first',1,1,1,1);p.update(source='panels/first.svg',ports={},diagram=DATA['hub'])
            spec={'version':1,'title':'Hub control','thesis':'Preserve authored inputs.',
                  'canvas':{'width':660,'height':400,'displayWidth':550,'minTextPx':14,'margin':20,'gap':20,'titleHeight':55,'footerHeight':20},
                  'grid':{'columns':[1],'rows':[1]},'concepts':[{'id':'engine','label':'Engine'}],'panels':[p]}
            brief=directory/'brief.json';brief.write_text(json.dumps(spec),encoding='utf-8')
            before=brief.read_bytes();self.assertTrue(render(brief,directory)['ok'])
            figure=(directory/'figure.svg').read_bytes()
            with self.assertRaisesRegex(ValueError,'exists'):render(brief,directory)
            self.assertEqual(brief.read_bytes(),before)
            self.assertEqual((directory/'figure.svg').read_bytes(),figure)

    def test_bright_category_colors_do_not_replace_readable_text(self):
        r=Renderer(650,260,15,Path.cwd())
        data=copy.deepcopy(DATA["matrix"])
        data["rows"][0]["values"][0]={"text":"Yellow","color":"#ffd332"}
        r.matrix(data)
        self.assertTrue(any(e.get('fill')=='#ffd332' for e in r.root.iter() if e.tag.endswith('}rect')))
        self.assertFalse(any(e.get('fill')=='#ffd332' for e in r.root.iter() if e.tag.endswith('}text')))
        t=Renderer(650,260,15,Path.cwd())
        data=copy.deepcopy(DATA["taxonomy"]);data["groups"][0]["color"]="#ffd332"
        t.taxonomy(data)
        self.assertTrue(any(e.get('fill')=='#ffd332' for e in t.root.iter() if e.tag.endswith('}rect')))
        self.assertFalse(any(e.get('fill')=='#ffd332' for e in t.root.iter() if e.tag.endswith('}text')))

    def test_all_families_at_real_size(self):
        with tempfile.TemporaryDirectory(prefix="native-panels-",dir=Path.cwd()) as tmp:
            directory=Path(tmp)
            for kind,data in DATA.items():
                with self.subTest(kind=kind):
                    height=650 if kind in {"cycle","boundary"} else 400
                    p=panel("subject",1,1,1,1);p["source"]="panel.svg";p["diagram"]=data;p["ports"]={}
                    spec={"version":1,"title":"Family geometry control","thesis":"Preserve labels and relation semantics.",
                        "canvas":{"width":660,"height":height,"displayWidth":550,"minTextPx":14,"margin":20,"gap":20,"titleHeight":55,"footerHeight":20},
                        "grid":{"columns":[1],"rows":[1]},"concepts":[{"id":"engine","label":"Engine"}],"panels":[p]}
                    prepared,assets,font=build(spec,directory)
                    self.assertEqual(font,16.8)
                    for path,svg in assets:path.write_text(svg,encoding="utf-8")
                    figure,_=compose(prepared,directory/"plan.json")
                    target=directory/"figure.svg";target.write_text(figure,encoding="utf-8")
                    report=run(SimpleNamespace(command="audit",input=target,output=None,report=directory/"audit.json",screenshot=directory/"preview.png",overwrite=True))
                    self.assertTrue(report["ok"],report["issues"])
                    self.assertFalse(report["clippedMarks"])
                    self.assertTrue(prepared["panels"][0]["ports"])

    def test_long_label_does_not_shrink(self):
        r=Renderer(250,120,18,Path.cwd())
        with self.assertRaisesRegex(ValueError,"budget|height|width"):
            r.hub(DATA["hub"])

    def test_budget_failure_publishes_diagnostics_only(self):
        with tempfile.TemporaryDirectory(prefix="native-diagnostics-",dir=Path.cwd()) as tmp:
            directory=Path(tmp)
            p=panel("subject",1,1,1,1);p["source"]="panel.svg";p["ports"]={};p["diagram"]=DATA["hub"]
            spec={"version":1,"title":"Budget failure","thesis":"Keep input and diagnostics.",
                  "canvas":{"width":250,"height":220,"displayWidth":250,"minTextPx":18,"margin":20,"gap":20,"titleHeight":55,"footerHeight":20},
                  "grid":{"columns":[1],"rows":[1]},"concepts":[{"id":"engine","label":"Engine"}],"panels":[p]}
            brief=directory/"brief.json";brief.write_text(json.dumps(spec),encoding="utf-8")
            original=brief.read_bytes()
            command=[sys.executable,str(Path(__file__).with_name("build_panels.py")),"--spec",str(brief),
                     "--output-spec",str(directory/"plan.json"),"--report",str(directory/"diagnostics.json")]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads((directory/"diagnostics.json").read_text(encoding="utf-8"))
            self.assertFalse(report["ok"])
            self.assertTrue(report["error"])
            self.assertEqual(brief.read_bytes(),original)
            self.assertFalse((directory/"plan.json").exists())
            self.assertFalse((directory/"panel.svg").exists())
            command[-1]=str(brief);command.append("--overwrite")
            subprocess.run(command,check=True,capture_output=True)
            self.assertEqual(brief.read_bytes(),original)

    def test_cycle_requires_real_recurrence(self):
        data=copy.deepcopy(DATA["cycle"]);data["closed"]=False
        with self.assertRaisesRegex(ValueError,"recurrence"):
            Renderer(700,450,15,Path.cwd()).cycle(data)

    def test_matrix_column_contract(self):
        data=copy.deepcopy(DATA["matrix"]);data["rows"][0]["values"]=["one"]
        with self.assertRaisesRegex(ValueError,"match columns"):
            Renderer(700,250,15,Path.cwd()).matrix(data)

    def test_boundary_does_not_invent_links(self):
        data=copy.deepcopy(DATA["boundary"]);data["relations"]=[]
        r=Renderer(500,500,15,Path.cwd());r.boundary(data)
        paths=[el for el in r.root if el.tag.endswith('}path')]
        self.assertEqual(paths,[])

    def test_unknown_relation(self):
        data=copy.deepcopy(DATA["boundary"]);data["relations"]=[{"from":"missing","to":"source"}]
        with self.assertRaisesRegex(ValueError,"unknown node"):
            Renderer(500,550,15,Path.cwd()).boundary(data)

    def test_review_group_is_real_containment(self):
        r=Renderer(560,620,15,Path.cwd());r.boundary(DATA["boundary"])
        self.assertIn('review-gate-top',r.ports)
        for node in ('proposals','review'):
            self.assertLess(r.ports['review-gate-top'][1],r.ports[node+'-top'][1])
            self.assertGreater(r.ports['review-gate-bottom'][1],r.ports[node+'-bottom'][1])

    def test_overlapping_groups_rejected(self):
        data=copy.deepcopy(DATA['boundary'])
        data['groups'].append({'id':'second','label':'Other','nodes':['review','builds']})
        with self.assertRaisesRegex(ValueError,'overlap'):
            Renderer(560,620,15,Path.cwd()).boundary(data)


if __name__=='__main__':
    unittest.main()
