#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise graph meaning, geometry, chronology, serialization, and CLI boundaries."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT=Path(__file__).with_name("render_chart.py")
spec=importlib.util.spec_from_file_location("poster_renderer",SCRIPT)
renderer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
NS={"s":"http://www.w3.org/2000/svg"}


def graph():
    return {"id":"test-family","title":"A Family Study","mode":"genealogy","width":1400,"height":1600,
        "groups":[{"id":"a","label":"Alder","color":"#77BEDB"},{"id":"b","label":"Birch","color":"#F4C948"}],
        "columns":5,"rows":["First","Second","Third"],"source_note":"Synthetic data.",
        "nodes":[{"id":"a","label":"Anna","group":"a","col":1,"row":0},{"id":"b","label":"Bram","group":"b","col":3,"row":0},
                 {"id":"c","label":"Cora","group":"a","col":1,"row":1},{"id":"d","label":"Dara","group":"b","col":3,"row":1},
                 {"id":"e","label":"Evan","group":"a","col":2,"row":2}],
        "unions":[{"id":"ab","partners":["a","b"],"children":["c","d"]},{"id":"cd","partners":["c","d"],"children":["e"]}],"edges":[]}


def timeline():
    return {"id":"test-time","title":"A Shared Century","mode":"timeline","width":1400,"height":1600,
        "groups":[{"id":"a","label":"Alpha","color":"#A6C49B"}],"source_note":"Synthetic data.",
        "time":{"start":1900,"end":2000,"step":20},"lanes":[{"id":"west","label":"West"},{"id":"east","label":"East"}],
        "periods":[{"id":"p","label":"First phase","group":"a","lane":"west","start":1900,"end":1950},
                   {"id":"q","label":"Second phase","group":"a","lane":"west","start":1950,"end":2000},
                   {"id":"r","label":"East phase","group":"a","lane":"east","start":1920,"end":1980}]}


def result(data):
    svg,report=renderer.Poster(data).render()
    root=ET.fromstring(svg)
    return root,json.loads(root.find("s:metadata[@id='chart-data']",NS).text),report


class ChartTests(unittest.TestCase):
    def test_narrow_corridor_remains_reachable_without_reducing_clearance(self):
        # Reduced from a full genealogy: the previous visibility grid could not
        # leave the parental gap, although a clear route existed below it.
        boxes=[(291.385,505.7635,76.242,36.299),(287.44,560.0625,76.242,36.299),
               (383.682,561.536,57,33.352),(364.842,615.835,57,33.352)]
        start=(373.682,588.212);end=(477.342,643.682)
        path=renderer.route(start,end,boxes,(283.682,498.212,567.342,733.682),[])
        self.assertEqual(path[0],start);self.assertEqual(path[-1],end)
        self.assertFalse(any(renderer.segment_hits(a,b,box,7) for a,b in zip(path,path[1:]) for box in boxes))
        self.assertLess(sum(abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in zip(path,path[1:])),180)

    def test_exact_semantic_inventory_and_union_origin(self):
        root,meta,report=result(graph())
        self.assertEqual(set(meta["node_ids"]),{"a","b","c","d","e"})
        self.assertEqual(set(meta["edge_ids"]),{"ab-c","ab-d","cd-e"})
        self.assertEqual(report["union_count"],2)
        a,b=meta["boxes"]["a"],meta["boxes"]["b"]
        midpoint=((a[0]+a[2]+b[0])/2,a[1]+a[3]/2)
        for edge in meta["routes"][:2]:
            self.assertEqual(tuple(edge["points"][0]),midpoint)

    def test_escaping_is_text_not_markup(self):
        data=graph();data["nodes"][0]["label"]='A & B <C>'
        root,meta,_=result(data)
        self.assertFalse(root.findall(".//s:C",NS))
        self.assertIn("A & B <C>",meta["expected_text"])

    def test_deterministic_output(self):
        self.assertEqual(renderer.Poster(graph()).render(),renderer.Poster(graph()).render())

    def test_required_provenance(self):
        data=graph();del data["source_note"]
        with self.assertRaisesRegex(ValueError,"source_note"):result(data)

    def test_duplicate_node_rejected(self):
        data=graph();data["nodes"].append(copy.deepcopy(data["nodes"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicate node"):result(data)

    def test_unknown_parent_rejected(self):
        data=graph();data["unions"][0]["partners"][0]="missing"
        with self.assertRaisesRegex(ValueError,"known partners"):result(data)

    def test_backwards_parentage_rejected(self):
        data=graph();data["edges"]=[{"id":"backward","source":"e","target":"a","kind":"descent"}]
        with self.assertRaisesRegex(ValueError,"later row"):result(data)

    def test_unknown_child_rejected(self):
        data=graph();data["unions"][0]["children"].append("missing")
        with self.assertRaisesRegex(ValueError,"Unresolved"):result(data)

    def test_partner_must_not_cross_intervening_person(self):
        data=graph();data["nodes"].append({"id":"obstacle","label":"Orin","group":"a","row":0,"col":2})
        with self.assertRaisesRegex(ValueError,"crosses another person"):result(data)

    def test_overlapping_people_rejected(self):
        data=graph();data["nodes"][4].update(col=1,row=1);data["unions"]=[]
        with self.assertRaisesRegex(ValueError,"overlap"):result(data)

    def test_uncertain_and_adopted_keep_distinct_semantics(self):
        data=graph();data["unions"][0]["children"]=[]
        data["edges"]=[{"id":"uncertain","source":"ab","target":"c","kind":"uncertain"},
                       {"id":"adopted","source":"ab","target":"d","kind":"adopted"}]
        root,meta,_=result(data)
        paths=root.findall(".//s:path[@data-edge-id]",NS)
        byid={p.attrib["data-edge-id"]:p for p in paths}
        self.assertNotEqual(byid["uncertain"].attrib["stroke-dasharray"],byid["adopted"].attrib["stroke-dasharray"])
        self.assertEqual([e["kind"] for e in meta["routes"][:2]],["uncertain","adopted"])

    def test_multiple_ports_do_not_hide_branch_trunks(self):
        data=graph();data["unions"]=[]
        data["edges"]=[{"id":"ac","source":"a","target":"c","kind":"branch"},{"id":"ad","source":"a","target":"d","kind":"branch"}]
        _,meta,_=result(data)
        self.assertNotEqual(meta["routes"][0]["points"][0],meta["routes"][1]["points"][0])

    def test_dense_names_fit_without_unnecessary_type_reduction(self):
        data=graph();data.update(width=1600,columns=12,rows=["Origins","Developmental schools","Institutional colleges"])
        data["nodes"][4]["label"]="Spectrum Lab"
        root,meta,_=result(data)
        self.assertIn("Spectrum",meta["expected_text"])
        self.assertGreaterEqual(meta["boxes"]["e"][2],100)

    def test_automatic_lineage_preserves_entities_and_topology(self):
        data=graph();data.update(mode="lineage",layout="auto",unions=[])
        for key in ("columns","rows","width","height"):data.pop(key)
        data["edges"]=[{"id":"a_c","source":"a","target":"c","kind":"branch"},{"id":"b_d","source":"b","target":"d","kind":"branch"},{"id":"c_e","source":"c","target":"e","kind":"branch"},{"id":"d_e","source":"d","target":"e","kind":"influence"}]
        for node in data["nodes"]:node.pop("row");node.pop("col")
        original=copy.deepcopy(data)
        _,meta,report=result(data)
        self.assertEqual(data,original)
        self.assertEqual(set(meta["node_ids"]),{"a","b","c","d","e"})
        self.assertEqual(len(meta["routes"]),4)
        placements={n["id"]:n for n in report["resolved_layout"]["nodes"]}
        self.assertEqual(placements["e"]["row"],2)
        self.assertEqual(placements["d"]["row"],1)

    def test_automatic_lineage_rejects_cycles(self):
        data=graph();data.update(mode="lineage",layout="auto",unions=[])
        data["edges"]=[{"id":"ac","source":"a","target":"c","kind":"branch"},{"id":"ca","source":"c","target":"a","kind":"branch"}]
        with self.assertRaisesRegex(ValueError,"cycle"):result(data)

    def test_time_positions_are_metric(self):
        _,meta,_=result(timeline())
        y0,y1=meta["time_y"]
        box=meta["boxes"]["r"]
        self.assertAlmostEqual(box[1],y0+.2*(y1-y0))
        self.assertAlmostEqual(box[3],.6*(y1-y0))

    def test_touching_periods_allowed_overlapping_rejected(self):
        result(timeline())
        data=timeline();data["periods"][1]["start"]=1940
        with self.assertRaisesRegex(ValueError,"overlap"):result(data)

    def test_reversed_dates_rejected(self):
        data=timeline();data["periods"][0].update(start=1950,end=1900)
        with self.assertRaisesRegex(ValueError,"reversed"):result(data)

    def test_short_interval_not_stretched(self):
        data=timeline();data["periods"][0]["end"]=1901
        with self.assertRaisesRegex(ValueError,"too short"):result(data)

    def test_historical_scale_expresses_no_year_zero(self):
        data=timeline();data["time"].update(start=-99,end=101,step=50,notation="historical")
        data["periods"]=[{"id":"p","label":"A phase","group":"a","lane":"west","start":-99,"end":101}]
        poster=renderer.Poster(data)
        self.assertEqual(poster.year_label(0),"1 BCE")
        self.assertEqual(poster.year_label(1),"1 CE")
        result(data)

    def test_all_default_and_dark_paints_have_readable_text(self):
        for paint in ["#77BEDB","#F4C948","#A6C49B","#813B37","#666666","#000000","#FFFFFF","#FF0000"]:
            self.assertGreaterEqual(renderer.contrast(paint,renderer.text_color(paint)),4.5)

    def test_duplicate_group_colors_rejected(self):
        data=graph();data["groups"][1]["color"]=data["groups"][0]["color"]
        with self.assertRaisesRegex(ValueError,"distinct"):result(data)

    def test_nan_coordinate_rejected(self):
        data=graph();data["nodes"][0]["col"]=float("nan")
        with self.assertRaisesRegex(ValueError,"finite"):result(data)

    def test_font_and_license_embedded(self):
        root,_,_=result(graph())
        self.assertIn("data:font/ttf;base64",root.find("s:style",NS).text)
        self.assertIn("SIL OPEN FONT LICENSE",root.find("s:metadata[@id='font-license']",NS).text)

    def test_cli_preserves_outputs_on_invalid_input(self):
        with tempfile.TemporaryDirectory(prefix="poster-check-",dir=Path.cwd()) as directory:
            source,output=Path(directory)/"bad.json",Path(directory)/"poster.svg"
            source.write_text('{"id":"bad"}',encoding="utf-8")
            output.write_text("KEEP",encoding="utf-8")
            run=subprocess.run([sys.executable,str(SCRIPT),str(source),"--svg",str(output)],capture_output=True,text=True)
            self.assertEqual(run.returncode,2)
            self.assertEqual(output.read_text(),"KEEP")

    def test_cli_does_not_overwrite_input(self):
        with tempfile.TemporaryDirectory(prefix="poster-path-",dir=Path.cwd()) as directory:
            source=Path(directory)/"brief.json";raw=json.dumps(graph());source.write_text(raw,encoding="utf-8")
            run=subprocess.run([sys.executable,str(SCRIPT),str(source),"--svg",str(source)],capture_output=True,text=True)
            self.assertEqual(run.returncode,2)
            self.assertEqual(source.read_text(),raw)


if __name__=="__main__":
    unittest.main(verbosity=2)
