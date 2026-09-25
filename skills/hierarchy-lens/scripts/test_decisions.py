#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent decision-order, topology, policy-effect, and trace checks."""

import copy
import math
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from build_explorer import demo, normalize
from decision_layout import decision_layout, demo_composition
from organic_layout import shape_quality


def fixture():
    rows = [("root",None,1,"R"),("a","root",10,"R"),("b","root",40,"B"),
            ("c","a",100,"R"),("d","a",None,"B"),("e","b",5,"R"),("f","b",0,"B"),("g","b",40,"B")]
    return {"title":"Research portfolio","provenance":"Synthetic decision contract","dimensions":[
        {"key":"role","label":"Role","type":"categorical","categories":["R","B"]},
        {"key":"tokens","label":"Usage","type":"numeric","unit":"tokens","period":"2026-09"}],
        "nodes":[{"id":i,"parentId":p,"label":i,"values":{"tokens":v,"role":r}} for i,p,v,r in rows]}


def policy():
    return {"priority":{"key":"tokens","direction":"descending"},"affinity":"role","eligibility":"generation",
            "weights":{"parent":2,"affinity":6,"compactness":2,"radial":1},"frontierWindow":4}


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.data=normalize(fixture())

    def order(self, layout):
        return [self.data["nodes"][d["node"]]["id"] for d in layout["decisions"]]

    def test_generation_numeric_order_and_missing_last(self):
        self.assertEqual(self.order(decision_layout(self.data,policy())),["root","b","a","c","g","e","f","d"])

    def test_parent_ready_queue_has_different_order(self):
        config=policy();config["eligibility"]="parent"
        self.assertEqual(self.order(decision_layout(self.data,config)),["root","b","g","a","c","e","f","d"])

    def test_explicit_category_order(self):
        config=policy();config["priority"]={"key":"role","order":["R","B"]}
        self.assertEqual(self.order(decision_layout(self.data,config)),["root","a","b","c","e","d","f","g"])

    def test_one_pixel_and_determinism(self):
        a=decision_layout(self.data,policy(),1)
        b=decision_layout(self.data,policy(),1)
        self.assertEqual(a,b)
        self.assertEqual(a["coverage"],[1]*8)
        root=a["cells"][0];self.assertEqual([root["x"],root["y"]],[a["size"]//2]*2)
        self.assertEqual(a["decisions"],decision_layout(self.data,policy(),4)["decisions"])

    def test_priority_and_affinity_change_actual_geometry(self):
        source=demo(180);data=normalize(source);config=demo_composition(source)
        baseline=decision_layout(data,config)
        altered=copy.deepcopy(config);altered["priority"]["order"].reverse()
        changed=decision_layout(data,altered)
        self.assertNotEqual(baseline["decisions"],changed["decisions"])
        self.assertNotEqual(baseline["cells"],changed["cells"])
        altered=copy.deepcopy(config);altered["affinity"]="contract"
        self.assertNotEqual([(c["tileX"],c["tileY"]) for c in baseline["cells"]],[(c["tileX"],c["tileY"]) for c in decision_layout(data,altered)["cells"]])

    def test_every_prefix_connected_hole_free_and_trace_truthful(self):
        source=demo(120);data=normalize(source);config=demo_composition(source)
        layout=decision_layout(data,config)
        occupied={};placed=set();positions={};groups={}
        for decision in layout["decisions"]:
            node=data["nodes"][decision["node"]];x,y=decision["x"],decision["y"]
            self.assertNotIn((x,y),occupied)
            if placed:
                eligible=[n for n in data["nodes"] if n["id"] not in placed and n["parentId"] in placed]
                depth=min(n["depth"] for n in eligible);eligible=[n for n in eligible if n["depth"]==depth]
                expected=min(eligible,key=lambda n:(config["priority"]["order"].index(n["values"]["role"]) if n["values"]["role"] is not None else math.inf,n["id"]))
                self.assertEqual(node["id"],expected["id"])
                self.assertEqual(decision["eligible"],len(eligible))
                neighbors=[occupied[p] for p in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)] if p in occupied]
                self.assertTrue(neighbors)
                parent=positions[node["parentId"]]
                affinity=groups.get(node["values"]["role"],[])
                matching=sum(n["values"]["role"]==node["values"]["role"] for n in neighbors)
                terms={"parent":1/(1+abs(x-parent[0])+abs(y-parent[1])),"compactness":len(neighbors)/4,"radial":1/(1+math.hypot(x,y)),
                       "affinity":.65/(1+abs(x-sum(p[0] for p in affinity)/len(affinity))+abs(y-sum(p[1] for p in affinity)/len(affinity)))+.35*matching/4 if affinity else 0}
                for name,value in terms.items():self.assertAlmostEqual(value,decision["terms"][name])
                self.assertAlmostEqual(decision["score"],sum(config["weights"][k]*v for k,v in terms.items()))
                for alternative in decision["alternatives"]:
                    self.assertNotIn((alternative["x"],alternative["y"]),occupied)
                    self.assertGreaterEqual(decision["score"],alternative["score"])
            occupied[x,y]=node;placed.add(node["id"]);positions[node["id"]]=(x,y)
            groups.setdefault(node["values"]["role"],[]).append((x,y))
            self.assertEqual(shape_quality(occupied),(True,0))

    def test_singleton_and_scale(self):
        data=normalize({**fixture(),"nodes":fixture()["nodes"][:1]})
        self.assertEqual(len(decision_layout(data,policy())["decisions"]),1)
        source=demo(5000);layout=decision_layout(normalize(source),demo_composition(source))
        self.assertEqual(len(layout["cells"]),5000)
        self.assertEqual(shape_quality((c["tileX"],c["tileY"]) for c in layout["cells"]),(True,0))

    def test_winner_beats_every_admissible_vacancy(self):
        config=policy();layout=decision_layout(self.data,config);occupied={};positions={}
        for record in layout["decisions"]:
            node=self.data["nodes"][record["node"]]
            if occupied:
                frontier={(x+dx,y+dy) for x,y in occupied for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]}-occupied.keys()
                minimum=min(math.hypot(x,y) for x,y in frontier)
                frontier={p for p in frontier if math.hypot(*p)<=minimum+config["frontierWindow"]}
                self.assertEqual(len(frontier),record["candidates"])
                scores=[];parent=positions[node["parentId"]]
                matching=[p for p,n in occupied.items() if n["values"]["role"]==node["values"]["role"]]
                for x,y in frontier:
                    if shape_quality(set(occupied)|{(x,y)})!=(True,0):continue
                    neighbors=[occupied[p] for p in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)] if p in occupied]
                    terms={"parent":1/(1+abs(x-parent[0])+abs(y-parent[1])),"compactness":len(neighbors)/4,"radial":1/(1+math.hypot(x,y)),
                           "affinity":.65/(1+abs(x-sum(p[0] for p in matching)/len(matching))+abs(y-sum(p[1] for p in matching)/len(matching)))+.35*sum(n["values"]["role"]==node["values"]["role"] for n in neighbors)/4 if matching else 0}
                    scores.append(sum(config["weights"][k]*v for k,v in terms.items()))
                self.assertAlmostEqual(max(scores),record["score"])
            occupied[record["x"],record["y"]]=node;positions[node["id"]]=(record["x"],record["y"])

    def test_policy_rejects_implicit_or_invalid_priorities(self):
        invalid=[None,{**policy(),"priority":{"key":"role"}},{**policy(),"priority":{"key":"role","order":["R","R"]}},
                 {**policy(),"affinity":"tokens"},{**policy(),"eligibility":"guess"},{**policy(),"frontierWindow":0},
                 {**policy(),"weights":{**policy()["weights"],"affinity":-1}}]
        for config in invalid:
            with self.subTest(config=config),self.assertRaises(ValueError):decision_layout(self.data,config)

    def test_cli_numeric_overrides_and_one_pixel_input(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            root=Path(folder);source=root/'input.json';source.write_text(json.dumps(fixture()),encoding='utf-8');before=source.read_bytes()
            command=[sys.executable,str(Path(__file__).with_name('build_explorer.py')),'--input',str(source),'--view','decision','--priority','tokens','--priority-direction','descending','--affinity','role','--eligibility','parent','--weights','4','3','2','1','--frontier-window','2','--cell-pixels','1','--output',str(root/'map.html'),'--report',str(root/'build.json')]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads((root/'build.json').read_text())
            self.assertEqual(report['minPixelsPerRecord'],1)
            self.assertEqual(report['maxPixelsPerRecord'],1)
            self.assertEqual(report['composition'],{'priority':{'key':'tokens','direction':'descending'},'affinity':'role','eligibility':'parent','weights':{'parent':4,'affinity':3,'compactness':2,'radial':1},'frontierWindow':2})
            self.assertEqual(source.read_bytes(),before)

    def test_cli_demo_priority_replaces_role_default(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            root=Path(folder)
            result=subprocess.run([sys.executable,str(Path(__file__).with_name('build_explorer.py')),'--demo','--demo-size','20','--view','decision','--priority','tokens','--priority-direction','descending','--cell-pixels','2','--output',str(root/'map.html'),'--data-output',str(root/'source.json')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads(result.stdout);source=json.loads((root/'source.json').read_text())
            self.assertEqual(report['composition']['priority'],{'key':'tokens','direction':'descending'})
            self.assertEqual(source['composition'],report['composition'])


if __name__ == "__main__":
    unittest.main()
