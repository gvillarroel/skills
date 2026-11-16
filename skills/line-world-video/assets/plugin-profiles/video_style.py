#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Native Mermaid video finish, copied beside the producer's renderer in the plugin."""
import re

SVG="{http://www.w3.org/2000/svg}"


def native_video_presentation(root, colorset):
    """Keep native geometry; replace standalone card aesthetics for video use."""
    if colorset=="colorset2":
        # The caller explicitly selected semantic category color. Retain contrast.
        from mermaid_animation.solid import native_solid_presentation
        native_solid_presentation(root,colorset)
    parent={child:node for node in root.iter() for child in node}
    seen={}
    for node in list(root.iter()):
        tag=node.tag.rsplit('}',1)[-1]
        eid=node.get('id')
        if eid:
            seen[eid]=seen.get(eid,0)+1
            if seen[eid]>1:node.set('id',eid+'-video-'+str(seen[eid]))
        classes=node.get('class','')
        if tag=='text' and re.search(r'(?:^|\s)(?:pieTitleText|titleText|mermaidTitle)(?:\s|$)',classes) and root.get('data-line-world-context-title')!='true':
            if node in parent:parent[node].remove(node)
            continue
        style=re.sub(r'(?:^|;)\s*filter\s*:[^;]*','',node.get('style',''))
        node.attrib.pop('filter',None)
        if colorset=="colorset1":
            if tag in {'text','tspan'}:
                style+=';fill:#333e48!important;color:#333e48!important;stroke:none!important;'
            fills=re.findall(r'(?:^|;)\s*fill\s*:\s*([^;]+)',style)
            fill=fills[-1].replace('!important','').strip() if fills else node.get('fill','')
            parent_class=parent.get(node).get('class','') if parent.get(node) is not None else ''
            surface=tag in {'rect','circle','ellipse','polygon'} or (tag=='path' and (fill not in {'','none'} or re.search(r'node-bkg|label-container|section|state',classes,re.I) or re.search(r'node|section|state',parent_class,re.I)))
            if surface:
                ancestors=[];current=node
                while current in parent:
                    current=parent[current];ancestors.append(current.get('class',''))
                nested_node=any(re.search(r'(?:^|\s)node(?:\s|$)',value) for value in ancestors)
                group=node.get('data-lw-surface')=='group' or bool(re.search(r'entityBox|classBox',classes,re.I)) or (not nested_node and bool(re.search(r'cluster',classes+' '+' '.join(ancestors),re.I)))
                node.set('data-lw-surface','group' if group else 'item')
                if group:style+=';fill:#ffffff!important;fill-opacity:1!important;stroke:#828282!important;stroke-width:2px!important;'
                elif node.get('data-encoding') or node.get('data-lw-preserve')=='paint':style+=';stroke:none!important;stroke-width:0!important;'
                else:style+=';fill:#e7e7e7!important;fill-opacity:1!important;stroke:none!important;stroke-width:0!important;'
            if 'radarCurve' in classes:
                style+=';fill:none!important;stroke:#333e48!important;'
                if 'radarCurve-0' in classes:style+='stroke-dasharray:6 5!important;'
            if tag=='circle' and root.get('aria-roledescription','').lower().startswith('radar'):
                style+=';fill:none!important;stroke:#cfcfcf!important;'
            if tag=='path' and root.get('aria-roledescription','').lower().startswith('sankey'):
                style+=';fill:none!important;stroke:#cfcfcf!important;stroke-opacity:1!important;mix-blend-mode:normal!important;'
        if colorset=="colorset2" and tag in {'rect','circle','ellipse','polygon'}:
            ancestors=[];current=node
            while current in parent:
                current=parent[current];ancestors.append(current.get('class',''))
            nested_node=any(re.search(r'(?:^|\s)node(?:\s|$)',value) for value in ancestors)
            group=node.get('data-lw-surface')=='group' or (not nested_node and bool(re.search(r'cluster',classes+' '+' '.join(ancestors),re.I)))
            node.set('data-lw-surface','group' if group else 'item')
            style+=';fill:#ffffff!important;stroke:#828282!important;stroke-width:2px!important;' if group else ';stroke:none!important;stroke-width:0!important;'
        if style:node.set('style',style)
    root.set('data-video-style','line-world')
    root.set('data-video-title-policy','explicit-context-only')
