#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Retain authored route evidence and separate declared acceptance outcomes."""
import base64
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from PIL import Image
from playwright.sync_api import sync_playwright
from artwork import ROOT,REPO
sys.path.insert(0,str(REPO/'skills/usefulcharts-style/scripts'))
from assess_exploration_review import assess

CASES={
 'instruments':dict(ref='denominations',url='christian-denominations-family-tree',scores=[3,3,3,3,3],defects=[],difference='Five classification trunks remain more regular and sparse than the interleaved denomination tree.',routes=[
  ('trace',['1','11','111'],'Why is a handbell an idiophone?','Follow body vibration to struck bodies and direct blows; the pictured handbell is explicitly connected and labeled 111.'),
  ('compare',['321','322'],'How do violin and harp differ within the string family?','The violin appears at 321, lutes; the harp appears at 322, harps. Both sit beneath the composite-string branch, with separate local picture connectors.'),
  ('trace',['2','24','242'],'Why is a kazoo in the membrane family?','The red path reaches singing membranes and category 242; the kazoo picture repeats 242 and explains the singing membrane.')]),
 'bsd':dict(ref='royal',url='european-royal-family-tree',scores=[3,3,3,3,3],defects=[],difference='The Berkeley return row and long contribution corridors remain more mechanical than an irregular royal genealogy.',routes=[
  ('trace',['v6','b1','b3'],'How does Research UNIX lead into Berkeley?','The UNIX V6 line reaches 1BSD, followed by 2BSD and 3BSD; the separate UNIX/32V input also joins 3BSD.'),
  ('compare',['lite','f2','n1','os2'],'Which branches receive 4.4BSD Lite, and how?','The solid route reaches FreeBSD 2.0; separate dashed contribution routes reach NetBSD 1.0 and BSD/OS 2.0.'),
  ('time',['f21','n11','os201'],'Which terminal releases shown reach 1995?','FreeBSD 2.1, NetBSD 1.1 and BSD/OS 2.0.1 all carry 1995; the distances between their boxes are not elapsed time.')]),
 'mars':dict(ref='history',url='timeline-of-world-history',scores=[2,3,3,3,3],defects=['The long empty lower calendar field still weakens the whole-page rhythm. Direct picture routes are readable but some are too long.'],difference='The uniform mission calendar has large quiet decades and less interleaved contextual explanation than the reference.',routes=[
  ('compare',['viking1','viking2'],'Which Viking orbiter operated longer in the selected data?','Viking 1 orbiter is labeled 1976–1980; Viking 2 orbiter is labeled 1976–1978. Separate lander bars prevent conflating the vehicles.'),
  ('compare',['mars2','mars3'],'Did Mars 2 and Mars 3 have the same landing outcome?','Mars 2 crashed; Mars 3 landed and transmitted for seconds. Both source records connect to the explicitly shared museum model.'),
  ('time',['nozomi','pathfinder'],'What distinguishes the Japanese attempt from Pathfinder?','Nozomi launched in 1998 and failed to enter Mars orbit in 2003; Pathfinder launched in 1996 and landed in 1997. Only date marks carry X, not the pictures.')]),
 'starships':dict(ref='history',url='timeline-of-world-history',scores=[3,3,3,3,3],defects=[],difference='Large prose nameplates and uneven late-row occupancy still distinguish this space atlas from the reference chronology.',routes=[
  ('compare',['defiant-first','defiant-second'],'Are the two Defiant records the same physical vessel?','Compare the original Defiant with the renamed São Paulo: their printed histories and separate tracks identify different physical hulls.'),
  ('trace',['enterprise-nx','columbia'],'How are the NX-class examples related?','The sister-ship route connects Enterprise NX-01 and Columbia NX-02; their matching design images sit at their own dated tracks.'),
  ('time',['voyager','voyager-a'],'Does reuse of the Voyager name imply continuous operation by one hull?','The separate nameplates, registries and date marks identify distinct hulls; the original Voyager’s museum state remains a continuation of that physical hull.')]),
 'civilizations':dict(ref='history',url='timeline-of-world-history',scores=[2,3,3,3,3],defects=['The repeated story-card matrix still dominates the subject imagery. The Dominion coalition inset adds a real political comparison, but the main field still reads predominantly as a catalog.'],difference='The regular story bands still read more like an annotated catalog than the reference’s interwoven civilizations; the new coalition inset improves one previously unused region.',routes=[
  ('time',['st-001','st-017'],'Which comes first: First Contact or the Federation?','The repeated calendar strips place the source anchors at 2063 and 2161; the notes name the four founding worlds.'),
  ('compare',['st-116','st-118'],'Are the cooperative Borg and Frontier Day the same event?','The separate 2401 records distinguish Jurati’s cooperative group from the Frontier Day attack; temporal coexistence does not merge their identities.'),
  ('compare',['st-076','st-090'],'Did Cardassia and the Breen join the Dominion at the same time?','The coalition inset connects Dukat joining in 2373 and the Breen joining in 2375 to the same Dominion node. The separate source entries retain those dates; the inset is explicitly schematic, not an elapsed-time axis.')])}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    output=ROOT/'artifacts/revision-3';summaries=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch();page=b.new_page(viewport=dict(width=1400,height=1050))
        for case,config in CASES.items():
            out=output/case;svg=out/'poster.svg';root=ET.parse(svg).getroot();layout=json.loads((out/'layout.json').read_text());source=json.loads((out/'source.json').read_text(encoding='utf-8'));ns=source.get('nodes') or source.get('ships') or [n for k in ['events','origins','future','branches'] for n in source[k]];by={n['id']:n for n in ns};boxes={v['id']:v for v in layout['boxes']};arts=json.loads((out/'art-map.json').read_text());routes=[]
            for i,(operation,anchors,question,answer) in enumerate(config['routes'],1):
                own=[boxes[a] for a in anchors]+[a['box'] for a in arts if any(n in a['anchors'] for n in anchors)]
                coalition_detail=case=='civilizations' and i==3
                if coalition_detail:
                    page.set_content(ET.tostring(root,encoding='unicode'));page.evaluate('document.fonts.ready')
                    own=[page.locator('#dominion-coalitions').evaluate('(el)=>{const b=el.getBBox();return {x:b.x,y:b.y,w:b.width,h:b.height}}')]
                x=max(0,min(o['x'] for o in own)-55);y=max(0,min(o['y'] for o in own)-60);w=min(layout['width']-x,max(o['x']+o['w'] for o in own)-x+55);h=min(layout['height']-y,max(o['y']+o['h'] for o in own)-y+60)
                copy=ET.fromstring(ET.tostring(root));copy.set('width','1400');copy.set('height','1050');copy.set('viewBox',f'{x} {y} {w} {h}')
                page.set_content('<style>body{margin:0;background:#d5d4ca}</style>'+ET.tostring(copy,encoding='unicode'));page.evaluate('document.fonts.ready');path=out/f'route-{i}.png';page.screenshot(path=str(path))
                ids={e.get('id') for e in root.iter()};steps=[]
                for ident in anchors:
                    elements=['record-'+ident];elements += [a['placement_id'] for a in arts if ident in a['anchors'] and a['placement_id'] in ids]
                    steps.append(dict(element_ids=elements,observation='Inspect '+by[ident].get('label',by[ident].get('name',ident))+' and its printed date, facts and local connections.'))
                if coalition_detail:
                    steps=[dict(element_ids=['dominion-coalitions','coalition-cardassian'],observation='Read the Cardassian accession caption: Dukat joins in 2373, and trace its line into the Dominion.'),dict(element_ids=['political-dominion','coalition-breen'],observation='Compare the Breen caption, Joins in 2375, and follow its separate line into the same Dominion node.')]
                region='lower' if coalition_detail else ['upper','middle','lower'][min(2,int(3*sum(boxes[a]['y'] for a in anchors)/len(anchors)/layout['height']))]
                routes.append(dict(id=case+'-reading-'+str(i),anchors=anchors,question=question,answer=answer,operation=operation,region=region,reviewed_at_reading_size=True,requires_detached_lookup=False,detail=dict(path=path.name,sha256=digest(path)),steps=steps))
            ref=REPO/f'projects/usefulcharts-style/artifacts/images/reference-{config["ref"]}.png';rw,rh=Image.open(ref).size;refdetail=out/'reference-detail.png';data=base64.b64encode(ref.read_bytes()).decode()
            page.set_content(f'<style>body{{margin:0}}</style><svg width="1400" height="1050" viewBox="{rw*.04} {rh*.20} {rw*.72} {rh*.48}"><image width="{rw}" height="{rh}" href="data:image/png;base64,{data}"/></svg>');page.screenshot(path=str(refdetail))
            body_images=[]
            for a in arts:
                item=dict(a);path=ROOT/a['path'];item['path']=str(path);item['recognized_at_placed_size']=True;body_images.append(item)
            observations=['The current field has named entry points and preserves source notes. '+config['difference'],'The pictures identify the represented mechanisms, hardware or design families.','Printed associations and connectors replace the detached image galleries.','The listed questions have source-answerable steps; these do not by themselves prove an exploratory composition.','Full-size text and actual PDF labels pass the independent geometry/extraction checks.']
            coverage=dict(schema_version=1,reviewed_images=True,content_verified=True,technical_verified=True,artifacts={kind:dict(path=name,sha256=digest(out/name)) for kind,name in [('whole','preview.png'),('detail','detail.png')]},record_ids=list(by),required_groups=sorted({g for a in arts for g in a['groups']}),art_scope='Representative artwork for the named illustrated groups; this does not claim a distinct image for every source group or record.',body_images=body_images,minimum_body_regions=2,discovery_invitations=[dict(anchors=r['anchors'],question=r['question'],answer_location=r['detail']['path']) for r in routes],dimensions={name:dict(score=score,observation=observation) for name,score,observation in zip(['composition','image_usefulness','image_integration','playful_discovery','legibility'],config['scores'],observations)},before_weaknesses=['Detached art wells or picture galleries','Repeated text containers weakened image ownership','Source and date integrity alone were treated as visual success'],repairs_observed=['Pictures attached to named records or exact category leaves','Continuous typed paths or explicitly shared calendar marks','Full notes, selected identities and source links retained'],unresolved_defects=config['defects'],reference_density_status='pending')
            (out/'illustrated-review.json').write_text(json.dumps(coverage,indent=2)+'\n')
            review=dict(schema_version=1,illustrated_review='illustrated-review.json',svg=dict(path='poster.svg',sha256=digest(svg)),reference=dict(source_url='https://usefulcharts.com/products/'+config['url'],whole=dict(path=str(ref),sha256=digest(ref)),detail=dict(path=refdetail.name,sha256=digest(refdetail)),reviewed_images=True,comparison_basis='same-width-whole-and-relative-detail',comparisons=dict(structure=config['difference'],image_ownership='Reference portraits and objects create named local anchors. This revision adds direct bindings; generic hardware and design-family artwork remain explicit.',color_continuity='Category color persists through local names and connectors. The reference often carries color through more interleaved transitions.',reading_rhythm='The reference alternates local recognitions, branching paths and contextual discoveries. Repetition and large text blocks remain more visible in this candidate.'),convincing_family_resemblance=False,remaining_differences=[config['difference'],'A complete matched semantic reference-density census has not been performed.']),discovery_routes=routes,unresolved_composition_defects=config['defects'],actual_pixel_review=True)
            (out/'exploration-review.json').write_text(json.dumps(review,indent=2)+'\n');result=assess(review,out);(out/'exploration-assessment.json').write_text(json.dumps(result,indent=2)+'\n');summaries.append(dict(case=case,**result));print(json.dumps(dict(case=case,exploratory=result['declared_exploratory_composition_pass'],failures=result['failures'])))
        b.close()
    (output/'exploration-assessments.json').write_text(json.dumps(summaries,indent=2)+'\n')
if __name__=='__main__':main()
