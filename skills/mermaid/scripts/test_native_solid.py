#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Portable native Mermaid family regressions using native DOM contracts."""
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parent))
from palette_paints import readable_text, solid_colors
from mermaid_animation.solid import native_solid_presentation
from style_mermaid_directory import theme_variables


def paint(element, key):
    for declaration in reversed(element.get('style', '').split(';')):
        if ':' in declaration:
            name, value = declaration.split(':', 1)
            if name.strip() == key:
                return value.strip().removesuffix(' !important')
    return element.get(key)


def svg(family):
    return ET.Element('svg', {'aria-roledescription': family})


def box(group, classes='', **attributes):
    return ET.SubElement(group, 'rect', {'class': classes, 'fill': '#f7f7f7', 'stroke': '#333e48', 'stroke-width': '2', **attributes})


def text(group, content='Label', **attributes):
    element=ET.SubElement(group, 'text', {'fill': '#333e48', **attributes})
    element.text=content
    return element


class NativeFamilies(unittest.TestCase):
    def test_relationship_labels_use_own_backing_not_node_text(self):
        for family in ['flowchart', 'stateDiagram', 'classDiagram', 'swimlane']:
            for surface, expected in [('#ffffff', '#000000'), ('#333e48', '#ffffff')]:
                root = svg(family)
                ET.SubElement(root, 'style').text = '.label{color:#ffffff;}.edgeLabel{background-color:' + surface + ';}'
                group = ET.SubElement(root, 'g', {'class': 'edgeLabel', 'transform': 'translate(30,40)'})
                caption = text(group, 'Approved', **{'class': 'label', 'x': '4', 'y': '5'})
                foreign = ET.SubElement(group, 'foreignObject', {'width': '80', 'height': '24'})
                span = ET.SubElement(foreign, '{http://www.w3.org/1999/xhtml}span', {'class': 'edgeLabel'})
                span.text = 'Rejected'
                before = dict(group.attrib), dict(foreign.attrib), caption.get('x'), caption.get('y')
                native_solid_presentation(root, 'colorset1')
                self.assertEqual(paint(caption, 'fill'), expected)
                self.assertEqual(paint(span, 'color'), expected)
                self.assertEqual((dict(group.attrib), dict(foreign.attrib), caption.get('x'), caption.get('y')), before)

    def test_relationship_svg_label_uses_explicit_surface(self):
        root = svg('stateDiagram')
        group = ET.SubElement(root, 'g', {'class': 'edgeLabel'})
        backing = box(group, fill='#333e48', **{'fill-opacity': '1'})
        caption = text(group, 'Continue')
        before = dict(backing.attrib)
        native_solid_presentation(root, 'colorset1')
        self.assertEqual(paint(caption, 'fill'), '#ffffff')
        self.assertEqual(backing.attrib, before)

    def test_cs1_primary_theme_bodies_and_secondary_status_priority(self):
        for family, key in [('flowchart', 'primaryColor'), ('classDiagram', 'mainBkg'),
                            ('sequenceDiagram', 'actorBkg'), ('stateDiagram', 'stateBkg'),
                            ('gantt', 'taskBkgColor')]:
            self.assertEqual(theme_variables('colorset1', family)[key], '#9e1b32')
        variables = theme_variables('colorset1', 'gantt')
        self.assertEqual(variables['activeTaskBkgColor'], '#333e48')
        self.assertEqual(variables['doneTaskBkgColor'], '#4f4f4f')
        root = svg('gantt')
        for index, status in enumerate(['task0', 'active0', 'done0']):
            body = box(root, f'task {status}', id=f'task-{index}')
            caption = text(root, status, id=f'task-{index}-text', **{'class': 'taskText'})
        native_solid_presentation(root, 'colorset1')
        for index in range(3):
            body, caption = list(root)[index*2:index*2+2]
            self.assertEqual(paint(body, 'fill'), ['#9e1b32', '#333e48', '#4f4f4f'][index])
            self.assertEqual(paint(caption, 'fill'), '#ffffff')
            self.assertEqual(paint(body, 'stroke'), 'none')

    def assert_solid(self, shape, label=None):
        fill=paint(shape,'fill')
        self.assertIn(fill, solid_colors('colorset2'))
        self.assertEqual(paint(shape,'fill-opacity'),'1')
        self.assertEqual(paint(shape,'stroke'),'none')
        self.assertEqual(paint(shape,'stroke-width'),'0')
        if label is not None:
            self.assertEqual(paint(label,'fill'),readable_text(fill))

    def test_c4_types_seam_icon_and_relationship(self):
        root=svg('c4')
        for name in ['<<person>>','<<system>>','<<external_system>>']:
            group=ET.SubElement(root,'g',{'class':'person-man'})
            body=box(group,x='0',y='0',width='100',height='60')
            caption=text(group,name)
            seam=ET.SubElement(group,'path',{'fill':'none','stroke':'#828282','d':'M0 10L100 10'})
            icon=ET.SubElement(group,'image',{'href':'data:image/png;base64,source-icon'})
        connector=ET.SubElement(root,'path',{'class':'relation','stroke':'#333e48','d':'M0 0L10 10'})
        native_solid_presentation(root,'colorset2')
        for group in list(root)[:-1]:
            self.assert_solid(group[0],group[1])
            self.assertEqual(paint(group[2],'stroke'),readable_text(paint(group[0],'fill')))
            self.assertEqual(group[3].get('href'),'data:image/png;base64,source-icon')
        self.assertEqual(connector.get('stroke'),'#333e48')

    def test_block_state_labels_use_node_fill(self):
        for family in ['block','stateDiagram']:
            root=svg(family);group=ET.SubElement(root,'g',{'class':'node csMuted'})
            body=box(group);backing_group=ET.SubElement(group,'g',{'class':'label'})
            backing=box(backing_group);caption=text(backing_group)
            native_solid_presentation(root,'colorset2')
            self.assert_solid(body,caption);self.assert_solid(backing,caption)

    def test_kanban_nested_backing(self):
        root=svg('kanban');group=ET.SubElement(root,'g',{'class':'node card'})
        body=box(group);label_group=ET.SubElement(group,'g',{'class':'label'})
        backing=box(label_group);caption=text(label_group)
        native_solid_presentation(root,'colorset2')
        self.assert_solid(body,caption);self.assert_solid(backing,caption)

    def test_swimlane_header_and_canvas(self):
        root=svg('swimlane');group=ET.SubElement(root,'g',{'class':'cluster swimlane','id':'lane-a'})
        body=box(group,'swimlane-body');header=box(group,'swimlane-title')
        label_group=ET.SubElement(group,'g',{'class':'swimlane-label'});caption=text(label_group)
        native_solid_presentation(root,'colorset2')
        self.assertEqual(paint(body,'fill'),'none');self.assertEqual(paint(body,'stroke'),'none')
        self.assert_solid(header,caption)

    def test_journey_beyond_native_seven_slot_wrap(self):
        root=svg('journey');pairs=[]
        for index in range(9):
            for classes,y in [('journey-section section-type-0','50'),('task task-type-0','110')]:
                group=ET.SubElement(root,'g');shape=box(group,classes,x=str(index*100),y=y,width='100')
                label_group=ET.SubElement(group,'switch');caption=text(label_group)
                pairs.append((shape,caption))
        face=ET.SubElement(root,'circle',{'class':'face','stroke':'#828282'})
        native_solid_presentation(root,'colorset2')
        for shape,caption in pairs:self.assert_solid(shape,caption)
        self.assertEqual(len({paint(shape,'fill') for shape,_ in pairs}),9)
        self.assertEqual(face.get('stroke'),'#828282')

    def test_gantt_inside_status_text_preserves_critical_boundary(self):
        root=svg('gantt')
        shape=box(root,'task activeCrit0',id='task-a')
        caption=text(root,'Active critical',id='task-a-text',**{'class':'taskText activeCritText0'})
        native_solid_presentation(root,'colorset2')
        self.assertEqual(paint(shape,'fill'),solid_colors('colorset2')[2])
        self.assertEqual(shape.get('stroke'),'#333e48')
        self.assertEqual(paint(caption,'fill'),readable_text(paint(shape,'fill')))

    def test_treemap_opaque_full_capacity_then_overflow(self):
        root=svg('treemap');capacity=len(solid_colors('colorset1'));bodies=[]
        for index in range(capacity+1):
            group=ET.SubElement(root,'g',{'class':'treemapSection'})
            shape=box(group,'treemapSection section1',**{'fill-opacity':'0.6'})
            caption=text(group);bodies.append((shape,caption))
        native_solid_presentation(root,'colorset1')
        self.assertEqual(len({paint(s,'fill') for s,_ in bodies[:capacity]}),capacity)
        for shape,caption in bodies:
            self.assertEqual(paint(shape,'fill-opacity'),'1')
            self.assertEqual(paint(caption,'fill'),readable_text(paint(shape,'fill')))
        self.assertTrue(all(paint(s,'stroke')=='none' for s,_ in bodies[:capacity]))
        self.assertEqual(bodies[-1][0].get('data-colorset-overflow'),'true')

    def test_zenuml_participant_occurrence_and_lifeline(self):
        root=svg('zenuml');group=ET.SubElement(root,'g',{'class':'participant'})
        body=box(group,'participant-box',x='20',width='100');caption=text(group)
        occurrence=box(root,'occurrence',x='65',width='10')
        lifeline=ET.SubElement(root,'line',{'class':'lifeline','stroke':'#696969'})
        native_solid_presentation(root,'colorset2')
        self.assert_solid(body,caption);self.assert_solid(occurrence)
        self.assertEqual(lifeline.get('stroke'),'#696969')

    def test_railroad_terminal_nonterminal_and_paths(self):
        root=svg('railroadEbnf');fills=[]
        for kind in ['terminal','nonterminal']:
            group=ET.SubElement(root,'g',{'class':'railroad-'+kind})
            body=box(group);caption=text(group)
            line=ET.SubElement(group,'path',{'class':'railroad-line','fill':'none','stroke':'#696969'})
            native_solid_presentation(root,'colorset2')
            self.assert_solid(body,caption);fills.append(paint(body,'fill'))
            self.assertEqual(line.get('stroke'),'#696969')
        self.assertEqual(len(set(fills)),2)

    def test_wardley_procurement_overlay(self):
        root=svg('wardley');group=ET.SubElement(root,'g',{'class':'wardley-node wardley-node--component'})
        overlay=ET.SubElement(group,'circle',{'class':'wardley-build-overlay','fill':'#e7e7e7','stroke':'#000000'})
        body=ET.SubElement(group,'circle',{'fill':'#ffffff','stroke':'#9e1b32'})
        native_solid_presentation(root,'colorset2')
        self.assert_solid(body);self.assertEqual(overlay.get('stroke'),'#000000')

    def test_cynefin_item_card(self):
        root=svg('cynefin');group=ET.SubElement(root,'g')
        body=box(group,'cynefinItem');caption=text(group,**{'class':'cynefinItemText'})
        native_solid_presentation(root,'colorset2');self.assert_solid(body,caption)

    def test_quadrant_point_label(self):
        root=svg('quadrantChart');group=ET.SubElement(root,'g',{'class':'quadrant'})
        body=box(group,x='0',y='0',width='100',height='100')
        point_group=ET.SubElement(root,'g',{'class':'data-point'})
        ET.SubElement(point_group,'circle',{'cx':'20','cy':'20','r':'3'})
        caption=text(point_group)
        native_solid_presentation(root,'colorset2')
        self.assertEqual(paint(caption,'fill'),readable_text(paint(body,'fill')))

    def test_sequence_condition_canvas_keeps_region(self):
        root=svg('sequence');region=box(root,'rect',fill='rgba(255,204,213,0.18)')
        caption=text(root,'[Condition]',**{'class':'loopText'})
        native_solid_presentation(root,'colorset2')
        self.assertEqual(region.get('fill'),'rgba(255,204,213,0.18)')
        self.assertEqual(paint(caption,'fill'),'#000000')

    def test_sequence_control_captions_actor_and_referenced_number(self):
        root=svg('sequence')
        ET.SubElement(root,'style').text='svg [id$="-sequencenumber"]{fill:#696969;}'
        region=box(root,'rect',fill='rgba(255,204,213,0.18)')
        captions=[text(root,c,**{'class':c}) for c in ['sectionTitle','messageText','actor actor-man']]
        number=text(root,'1',**{'class':'sequenceNumber'})
        tab=box(root,'labelBox',fill='#9e1b32')
        tab_caption=text(root,'alt',fill='#ffffff',**{'class':'labelText'})
        native_solid_presentation(root,'colorset2')
        self.assertTrue(all(paint(c,'fill')=='#000000' for c in captions))
        self.assertEqual(paint(number,'fill'),'#ffffff')
        self.assertEqual(region.get('fill'),'rgba(255,204,213,0.18)')
        self.assertEqual(tab.get('fill'),'#9e1b32')
        self.assertEqual(paint(tab_caption,'fill'),'#ffffff')

    def test_venn_translucent_path_backing_keeps_overlap_geometry(self):
        root=svg('venn');group=ET.SubElement(root,'g')
        path=ET.SubElement(group,'path',{'d':'M10 10m-5 0a5 5 0 1 0 10 0a5 5 0 1 0-10 0','style':'fill:rgba(158,27,50,1);fill-opacity:0.1;stroke:#9e1b32;stroke-width:2.5;'})
        caption=text(group,'Set',**{'class':'label'})
        before=dict(path.attrib)
        native_solid_presentation(root,'colorset2')
        self.assertEqual(paint(caption,'fill'),'#000000')
        self.assertEqual(path.attrib,before)

    def test_cynefin_center_and_edge_label_actual_path(self):
        root=svg('cynefin')
        for x,y in [('0','0'),('400','0'),('0','300'),('400','300')]:
            box(root,'cynefinDomain',x=x,y=y,width='400',height='300')
        center=ET.SubElement(root,'path',{'class':'cynefinConfusion','d':'M280,300 A120,90 0 1,1 520,300 A120,90 0 1,1 280,300 Z'})
        disorder=text(root,'Disorder',x='400',y='308',**{'class':'cynefinSubtitle'})
        analyze=text(root,'Analyze',x='400',y='204',**{'class':'cynefinArrowLabel'})
        native_solid_presentation(root,'colorset2')
        self.assertEqual(paint(disorder,'fill'),readable_text(paint(center,'fill')))
        self.assertEqual(paint(disorder,'fill'),'#ffffff')
        self.assertEqual(paint(analyze,'fill'),'#ffffff')
        self.assertEqual(center.get('d'),'M280,300 A120,90 0 1,1 520,300 A120,90 0 1,1 280,300 Z')

    def test_radar_opaque_swatches_preserve_curve_alpha_and_identity(self):
        root=svg('radar')
        ET.SubElement(root,'style').text='.radarLegendBox-1{fill:#007298;fill-opacity:0.5;stroke:#007298;}.radarLegendBox-10{fill:#431f47;fill-opacity:0.5;stroke:#431f47;}'
        curve=ET.SubElement(root,'path',{'class':'radarCurve-1','fill':'#007298','fill-opacity':'0.5','stroke':'#007298'})
        swatch=box(root,'radarLegendBox-1');other=box(root,'radarLegendBox-10')
        before=dict(curve.attrib)
        native_solid_presentation(root,'colorset2')
        self.assert_solid(swatch);self.assertEqual(paint(swatch,'fill'),'#007298')
        self.assertEqual(paint(other,'fill'),'#431f47')
        self.assertEqual(curve.attrib,before)


if __name__=='__main__':unittest.main()
