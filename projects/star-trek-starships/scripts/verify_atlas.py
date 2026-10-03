#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.58", "pymupdf>=1.25", "pillow>=11"]
# ///
"""Independently verify the delivered spacecraft atlas and offline interactions."""
from pathlib import Path
from collections import Counter
from urllib.parse import unquote, urlsplit
import csv
import argparse
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
import pymupdf
from PIL import Image
from playwright.sync_api import sync_playwright

PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / "artifacts"
REVIEW = OUT / "reviews/final"
NS = {"s": "http://www.w3.org/2000/svg"}
SCALES = {"early": (2060,2170), "classic": (2240,2300),
          "modern": (2320,2405), "neighbors": (2360,2405), "future": (3188,3200)}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm_url(url):
    u = urlsplit(unquote(url))
    return (u.netloc + u.path).lower().rstrip("/")


def norm_text(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def main():
    global OUT,REVIEW
    parser=argparse.ArgumentParser()
    parser.add_argument('--space',action='store_true',help='Verify the separate space edition')
    args=parser.parse_args()
    if args.space:OUT=PROJECT/'artifacts/space-edition';REVIEW=OUT/'reviews/final'
    data = read(PROJECT / "data/ships.json")
    delivered = read(OUT / "data/ships.json")
    layout = read(OUT / "reviews/layout.json")
    assert data == delivered, "The delivered data differs from the authored source"
    ships = {s["id"]: s for s in data["ships"]}
    assert len(ships) == len(data["ships"]) == 79
    svg_path = OUT / "svgs/star-trek-starships.svg"
    assert layout["svg_sha256"] == hashlib.sha256(svg_path.read_bytes()).hexdigest()
    assert layout["source_sha256"] == hashlib.sha256((PROJECT / "data/ships.json").read_bytes()).hexdigest()
    tree = ET.fromstring(svg_path.read_text(encoding="utf-8"))
    nodes = {g.attrib["data-id"]: g for g in tree.findall('.//s:g[@class="record"]', NS)}
    assert set(nodes) == set(ships)
    assert len(tree.findall('.//s:g[@class="record"]', NS)) == 79
    assert len(tree.findall('.//s:g[@class="identity-story"]', NS)) == 8
    if args.space:
        assert len(tree.findall('.//s:use[@class="ship-art"]', NS)) == 7
        assert len(tree.findall('.//s:symbol', NS)) == 6
    else:assert len(tree.findall('.//s:g[@class="vessel-art"]', NS)) == 9
    retrieved = {norm_url(u) for u in read(PROJECT / "data/retrieved-source-urls.json")["urls"]}
    uncovered = [s["id"] for s in ships.values() if norm_url(data["sources"][s["source"]]["url"]) not in retrieved]
    assert not uncovered, f"Sources not recorded in research retrieval: {uncovered}"
    for s in ships.values():
        assert s["source"] in data["sources"] and s["credit"] and s["note"]
        assert s["observations"] == sorted(set(s["observations"]))
        assert nodes[s["id"]].attrib["data-source"] == data["sources"][s["source"]]["url"]
    # Explicit regression cases distinguish ship identity and different date meanings.
    assert ships["horizon"]["launch"] == 2102 and ships["horizon"]["launch_kind"] == "commission"
    assert ships["constellation"]["launch"] == 2245 and ships["excelsior"]["launch"] == 2285
    assert ships["enterprise-d"]["service"] == [2363,2371]
    assert {q["year"] for q in ships["enterprise-d"]["special"] if q["kind"] == "reactivated"} == {2401}
    assert ships["discovery"]["service"] is None
    assert ships["enterprise-f"]["launch"] is None
    assert ships["titan-a-g"]["launch"] is None
    assert ships["d-kyr"]["observations"] == [2152]
    assert ships["groth"]["observations"] == [2268]
    assert ships["nx-delta"]["uncertain_range"] == [2144,2145]
    assert ships["athena"]["uncertain_range"] == [3190,3199]
    assert len([s for s in ships.values() if s["id"] in {"defiant-first","defiant-second"}]) == 2
    assert len([s for s in ships.values() if s["id"] in {"delta-flyer-1","delta-flyer-2"}]) == 2
    audit = read(REVIEW / "browser-audit.json")
    assert not audit["outside"] and not audit["overlaps"] and not audit["envelope_overflow"]
    assert audit["font_barlow"] and audit["record_count"] == 79
    with (OUT / "data/ships.csv").open(encoding="utf-8-sig", newline="") as f:
        csv_rows = list(csv.DictReader(f))
    assert {s["id"] for s in csv_rows} == set(ships)
    ledger = (OUT / "documents/sources.html").read_text(encoding="utf-8")
    assert all(f'<article id="{id}">' in ledger for id in ships)
    assert Image.open(OUT / "images/star-trek-starships.png").size == (layout["width"],layout["height"])
    pdf = pymupdf.open(OUT / "documents/star-trek-starships.pdf")
    assert len(pdf) == 1
    page = pdf[0]
    pdf_text = norm_text(page.get_text())
    missing_pdf = [s["name"] for s in ships.values() if norm_text(s["name"]) not in pdf_text]
    assert not missing_pdf, f"Missing PDF names: {missing_pdf}"
    for s in ships.values():
        row_text=norm_text(' '.join(t.text or '' for t in nodes[s['id']].findall('.//s:text',NS)))
        for field in ['note','credit','registry']:
            assert norm_text(s[field]) in row_text, (s['id'],field,'SVG text')
            assert norm_text(s[field]) in pdf_text, (s['id'],field,'PDF text')
    links = page.get_links()
    assert Counter(l["uri"] for l in links) == Counter(data["sources"][s["source"]]["url"] for s in ships.values())
    sx,sy = page.rect.width/layout["width"],page.rect.height/layout["height"]
    for box in layout["boxes"]:
        point = pymupdf.Point((box["x"]+box["w"]/2)*sx,(box["y"]+box["h"]/2)*sy)
        matches = [l for l in links if l["from"].contains(point)]
        assert len(matches) == 1 and matches[0]["uri"] == data["sources"][ships[box["id"]]["source"]]["url"]
    for f in page.get_fonts():
        if f[2]=='Type3':
            # Type 3 fonts embed glyph drawing programs rather than a font file.
            kind,value=pdf.xref_get_key(f[0],'CharProcs')
            if kind=='xref':value=pdf.xref_object(int(value.split()[0]))
            glyphs=re.findall(r'(\d+) 0 R',value)
            assert glyphs and all(pdf.xref_is_stream(int(g)) and pdf.xref_stream(int(g)) for g in glyphs)
        else:assert pdf.extract_font(f[0])[3], 'A PDF font is not embedded'
    browser_errors = []
    network_requests = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome",headless=True)
        context = browser.new_context(viewport={"width":1440,"height":1000},offline=True)
        tab = context.new_page()
        tab.on("pageerror",lambda e: browser_errors.append(str(e)))
        tab.on("console",lambda m: browser_errors.append(m.text) if m.type == "error" else None)
        tab.on("request",lambda r: network_requests.append(r.url) if r.url.startswith("http") else None)
        tab.goto((OUT / "viewer/index.html").as_uri())
        tab.evaluate("document.fonts.ready")
        assert tab.locator(".record").count() == 79
        assert tab.locator("#count").inner_text() == "79 of 79 spacecraft"
        actual_marks = tab.evaluate('''() => [...document.querySelectorAll('.record')].map(e=>({
          id:e.dataset.id,box:{x:e.querySelector('.hit-area').getBBox().x},
          marks:[...e.querySelectorAll('.date-mark[data-year]')].map(m=>{const b=m.getBBox();return {year:+m.dataset.year,kind:m.dataset.kind,x:b.x+b.width/2}}),
          spans:[...e.querySelectorAll('.service-span,.uncertain-span,.observations-span')].map(g=>{const b=g.querySelector('rect,.wake-core').getBBox();return {kind:g.classList.contains('service-span')?'service':g.classList.contains('observations-span')?'observations':'uncertain',start:+g.dataset.start,end:+g.dataset.end,x:b.x,w:b.width,dash:g.querySelector('.wake-core')?.getAttribute('stroke-dasharray')||null}}),
          art:[...e.querySelectorAll('.ship-art')].map(a=>({year:+a.dataset.endYear,x:+a.getAttribute('x'),ship:a.dataset.ship}))
        }))''')
        date_marks, date_spans = 0, 0
        for record in actual_marks:
            s = ships[record["id"]]
            lo,hi = SCALES[s["chapter"]]
            # Read actual row origin, then independently calculate the declared scale.
            x0 = record["box"]["x"] + (590 if args.space else 525)
            px = lambda year: x0 + (year-lo)/(hi-lo)*(795 if args.space else 555)
            expected = []
            if not s.get("uncertain_range"):
                for year in sorted(set(s["observations"]+([s["launch"]] if s["launch"] is not None else []))):
                    kind = s["launch_kind"] if year == s["launch"] else (s["endpoint"] if year == s["observations"][-1] and s["endpoint"] else "active")
                    if year == s["launch"] and s["endpoint"] and year == s["observations"][-1]:
                        kind = "launch"
                    expected.append((year,kind))
                if s["endpoint"] and s["launch"] == s["observations"][-1]:
                    expected.append((s["observations"][-1],s["endpoint"]))
                expected += [(q["year"],q["kind"]) for q in s["special"] if q["kind"] in {"reactivated","active","time-arrival"} and lo <= q["year"] <= hi]
            assert Counter((m["year"],m["kind"]) for m in record["marks"]) == Counter(expected), record["id"]
            for mark in record["marks"]:
                assert lo <= mark["year"] <= hi
                assert abs(mark["x"]-px(mark["year"])) < .025, (s["id"],mark)
                date_marks += 1
            expected_spans = []
            if s.get("uncertain_range"):
                expected_spans.append(("uncertain",*s["uncertain_range"]))
            elif s["service"]:
                expected_spans.append(("service",*s["service"]))
            elif args.space:
                years=sorted(set(s['observations']+([s['launch']] if s['launch'] is not None else [])))
                if len(years)>1:expected_spans.append(('observations',years[0],years[-1]))
            assert [(q["kind"],q["start"],q["end"]) for q in record["spans"]] == expected_spans
            for span in record["spans"]:
                assert abs(span["x"]-px(span["start"])) < .02
                assert abs(span["x"]+span["w"]-px(span["end"])) < .02
                if args.space and span['kind']=='observations':assert span['dash']=='9 9'
                if args.space and span['kind']=='service':assert span['dash'] is None
                date_spans += 1
            for art in record['art']:
                years=s['observations']+([s['launch']] if s['launch'] is not None else [])
                assert art['ship']==s['id'] and art['year']==max(years)
                assert abs(art['x']-13-px(art['year']))<.02
        tab.screenshot(path=str(REVIEW / "viewer-overview.png"))
        tab.locator("#search").fill("NX-74205")
        assert tab.locator("#results button").count() == 2
        assert tab.locator(".record:not(.dim)").count() == 2
        tab.locator("#search").fill("")
        tab.locator("#operator").select_option("Klingon")
        assert tab.locator("#results button").count() == sum(s["operator"] == "Klingon" for s in ships.values())
        tab.locator("#operator").select_option("")
        tab.locator("#evidence").select_option("launch")
        launch_count = sum(s["launch"] is not None for s in ships.values())
        assert tab.locator("#results button").count() == launch_count
        tab.locator("#evidence").select_option("unknown")
        assert tab.locator("#results button").count() == 79-launch_count
        tab.locator("#evidence").select_option("")
        tab.locator("#search").fill("NCC-1701-D")
        assert tab.locator("#results button").count() == 1
        tab.locator("#results button").click()
        assert tab.locator("#detail > h2:first-child").inner_text() == "USS Enterprise-D"
        detail = tab.locator("#detail").inner_text()
        assert "2363–2371" in detail and "2401" in detail and "2402" in detail
        assert tab.locator(".record.selected").get_attribute("data-id") == "enterprise-d"
        assert tab.locator("#zoom").inner_text() == "72%"
        tab.screenshot(path=str(REVIEW / "viewer-enterprise-d.png"))
        assert tab.locator('#detail [data-ship-link="enterprise-e"]').count() == 1
        tab.locator('#detail [data-ship-link="enterprise-e"]').click()
        assert tab.locator("#detail > h2:first-child").inner_text() == "USS Enterprise-E"
        assert tab.locator(".record:not(.dim)").count() == 79
        tab.locator("#plus").click()
        assert tab.locator("#zoom").inner_text() == "86%"
        tab.locator("#minus").click()
        assert tab.locator("#zoom").inner_text() == "72%"
        tab.locator("#search").fill("")
        tab.locator("#section").select_option("identities")
        assert tab.locator("#zoom").inner_text() == "62%"
        assert tab.evaluate("document.getElementById('stage').scrollTop") > 2500
        tab.locator("#fit").click()
        assert tab.evaluate("document.getElementById('sizer').clientWidth <= document.getElementById('stage').clientWidth")
        tab.locator("#record-phoenix").focus()
        tab.keyboard.press("Enter")
        assert tab.locator("#detail > h2:first-child").inner_text() == "Phoenix"
        # All offline companion paths must resolve; external citations are explicit links.
        hrefs = tab.locator('a[href]').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
        for href in hrefs:
            if not href.startswith(("http","#")):
                assert (OUT / "viewer" / href.split("#")[0]).resolve().is_file(), href
        tab.set_viewport_size({"width":900,"height":900})
        tab.locator("#fit").click()
        assert tab.evaluate("document.documentElement.scrollWidth <= innerWidth")
        tab.screenshot(path=str(REVIEW / "viewer-compact.png"))
        assert not browser_errors, browser_errors
        assert not network_requests, network_requests
        browser.close()
    report = dict(status="pass",records=79,operator_groups=len({s["operator"] for s in ships.values()}),
                  known_launch_commission_build=launch_count,unknown_launch=79-launch_count,
                  construction_observations=sum(bool(s["construction"]) for s in ships.values()),
                  exact_date_marks=date_marks,verified_date_spans=date_spans,
                  solid_service_spans=sum(bool(s["service"]) for s in ships.values()),
                  uncertain_ranges=sum(bool(s.get("uncertain_range")) for s in ships.values()),
                  visible_identity_diagrams=8,original_ship_identifiers=0 if args.space else 9,
                  generated_ship_illustrations=6 if args.space else 0,
                  retrieved_record_sources=79,pdf_pages=1,pdf_source_links=len(links),
                  pdf_embedded_fonts=len(page.get_fonts()),svg_text_nodes=audit["text_count"],
                  text_overlaps=0,outside_bounds=0,record_envelope_overflow=0,
                  viewer_checks=["offline load","registry search","operator filter","known and unknown date filters",
                                 "record selection","date qualifications","related-ship navigation","zoom","section navigation","keyboard selection","compact layout","relative downloads"],
                  browser_errors=browser_errors,network_requests=network_requests,
                  svg_sha256=layout["svg_sha256"],source_sha256=layout["source_sha256"],
                  limitations=["Search-index retrieval does not certify HTTP health or every source claim.",
                               "Technical checks do not certify UsefulCharts aesthetic or knowledge-density parity."])
    (REVIEW / "verification.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
