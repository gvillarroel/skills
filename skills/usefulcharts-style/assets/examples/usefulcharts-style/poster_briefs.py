#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Original synthetic acceptance data for dense editorial poster compositions."""

COLORS=['#F56550','#77BDDD','#F2C529','#98BD92','#B88BC6','#F49A2C','#EBA1BA','#B7B3A1']


def base(identifier,title,mode,labels):
    return dict(id=identifier,title=title,mode=mode,design='editorial',width=1800,height=2700,font_size=12.2,
        imprint=['ORIGINAL STUDY','Synthetic source data','2026 · Editable SVG'],
        groups=[dict(id=f'g{i}',label=label,color=COLORS[i]) for i,label in enumerate(labels)],
        source_note='Original synthetic study · All people, institutions, events, dates, and relationships are invented. Vector illustrations are fictional.',
        nodes=[],edges=[],unions=[],annotations=[],insets=[])


def genealogy():
    from genealogy_brief import build_genealogy
    return build_genealogy(base)


def lineage():
    from lineage_brief import build_lineage
    return build_lineage(base)


def timeline():
    from timeline_brief import build_timeline
    return build_timeline(base)


if __name__=='__main__':
    print('Import the three fixture functions from build_examples.py.')
