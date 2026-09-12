#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure source-bound territorial and institutional landmarks."""

from render_chart import number, require, wrap, text_width as measure_text


def landmark_content(annotation,node):
    field=annotation.get('field')
    require(isinstance(field,str) and field in node,'A landmark requires an existing source field on its named node.')
    label=node[field]
    require(isinstance(label,str) and label.strip(),'A landmark source field must contain a nonempty text value.')
    require('label' not in annotation or annotation['label']==label,'A landmark label must match its named source field exactly.')
    width=number(annotation.get('width',130),'landmark.width')
    size=number(annotation.get('size',18),'landmark.size')
    art=number(annotation.get('art_size',32 if annotation.get('icon') else 0),'landmark.art_size')
    require(width>=40 and size>=10 and 0<=art<=width,'Use a readable landmark with artwork contained inside its width.')
    require(not art or isinstance(annotation.get('icon'),str),'Landmark artwork requires an icon identifier.')
    position=annotation.get('art_position','above')
    require(position in ('above','beside'),'Landmark art_position must be above or beside.')
    text_width=width-12-(art+6 if art and position=='beside' else 0)
    require(text_width>=30,'Leave a readable text column beside landmark artwork.')
    lines=wrap(label,text_width,size,False)
    eyebrow=str(annotation.get('eyebrow',''))
    small=number(annotation.get('eyebrow_size',9),'landmark.eyebrow_size')
    require(small>=8,'A landmark eyebrow must be at least eight units.')
    eyebrows=wrap(eyebrow,text_width,small,True)
    art_height=art+6 if art and position=='above' else 0
    eyebrow_height=len(eyebrows)*small*1.2+3 if eyebrows else 0
    text_height=eyebrow_height+len(lines)*size*1.2
    ink_width=min(text_width,max([measure_text(line,size) for line in lines]+[measure_text(line,small,True) for line in eyebrows])+6)
    height=(max(art,text_height) if position=='beside' else art_height+text_height)+10
    return dict(label=label,field=field,width=width,size=size,art=art,art_height=art_height,
        eyebrow_size=small,eyebrows=eyebrows,eyebrow_height=eyebrow_height,lines=lines,height=height,
        art_position=position,text_height=text_height,ink_width=ink_width)


if __name__=='__main__':print('Use kind: landmark with an existing node field in an editorial poster.')
