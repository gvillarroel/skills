#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2", "pypdf>=5,<7"]
# ///
"""Compose three illustrated knowledge posters from the public blog source pool."""
import json
import math
import sys
import xml.etree.ElementTree as ET
from atlas_core import *


def connector(p, a, b, color=TEAL, label=None, y=None, kind='feeds', dash=None):
    cy = y if y is not None else min(a['y'] + a['h'] / 2, b['y'] + b['h'] / 2)
    p.line([(a['x'] + a['w'] + 8, cy), (b['x'] - 10, cy)], color, 2.6, source=a['id'], target=b['id'], kind=kind, arrow=True, dash=dash)
    if label:
        cx = (a['x'] + a['w'] + b['x']) / 2
        for i, line in enumerate(wrap(label, b['x'] - a['x'] - a['w'] - 14, 16)):
            p.text(p.body, cx - measure(line, 16) / 2, cy - 12 - (len(wrap(label, b['x'] - a['x'] - a['w'] - 14, 16)) - 1 - i) * 20, line, 16, color=color)


def history():
    import random
    p = Poster('01-history', 'HOW AI SYSTEMS CAME TOGETHER', '60 source-linked milestones share one numerical calendar. Read the dates across; use color to compare architectural mechanisms with LLM-system ideas.', '01 / 03', 6000)
    milestones = json.loads((OUT / 'data/milestones.json').read_text(encoding='utf-8'))
    segments = [(1943, 2000, 80, 1850), (2000, 2016, 1950, 1950), (2016, 2026, 3920, 1980)]
    def xyear(year):
        s = next(s for s in reversed(segments) if s[0] <= year <= s[1])
        return s[2] + (year - s[0]) / (s[1] - s[0]) * s[3]
    p.heading(65, 275, 'A SHARED NUMERICAL CALENDAR', 'A date is a selected publication or named proposal; chronological adjacency does not establish causal descent.', 2700)
    p.text(p.body, 4680, 275, 'ARCHITECTURE  /  29', 22, True, TEAL)
    p.text(p.body, 5250, 275, 'LLM SYSTEMS  /  31', 22, True, CORAL)
    for start, end, xx, span in segments:
        p.line([(xx, 370), (xx + span, 370)], INK, 2.2, track=False)
        ticks = [1943, 1960, 1980, 1990] if start == 1943 else list(range(start, end, 4)) if start == 2000 else list(range(start, end + 1, 2))
        for year in ticks:
            x = xyear(year)
            p.line([(x, 360), (x, 381)], INK, 1.5, track=False)
            p.text(p.body, x - measure(str(year), 23, True) / 2, 352, str(year), 23, True)
        label = f'{start}–{end}: {span / (end - start):.1f} horizontal units per year'
        p.text(p.body, xx + span / 2 - measure(label, 16) / 2, 413, label, 16, color=MUTED)
    for xx in [1940, 3910]:
        p.line([(xx - 7, 361), (xx - 2, 378), (xx + 3, 361), (xx + 8, 378)], INK, 1.5, track=False)
        p.text(p.body, xx - 62, 445, 'SCALE CHANGE', 14, True, MUTED)
    items = []
    illustrated={'history-30':2,'history-03':3,'history-06':10,'history-32':0,'history-17':5,'history-27':7,'history-47':0,'history-59':1,'history-58':9}
    for n in milestones:
        w = 405
        h = 67 + len(wrap(n['title'], w - 28, 28, True, True)) * 28 * 1.28 + len(wrap(n['note'], w - 28, 18)) * 18 * 1.28
        if n['id'] in illustrated:h+=222
        items.append(dict(n=n,w=w,h=h,xx=xyear(n['year'])))
    frequency = {n['year']:sum(r['year']==n['year'] for r in milestones) for n in milestones}
    def layout(order):
        occupied=[]; placed=[]
        for item in order:
            n,w,h,xx = item['n'],item['w'],item['h'],item['xx']
            options=[]
            for tx in sorted(set(max(65,min(p.width-w-65,t)) for t in [xx+18,xx-w-38,xx-w/2])):
                port=max(tx+12,min(tx+w-12,xx))
                parts=[dict(x=tx,y=32,w=w,h=h),dict(x=xx-6,y=-2,w=12,h=13),dict(x=min(xx,port)-1,y=14,w=max(3,abs(xx-port)+2),h=18)]
                ys={490}
                for part in parts:
                    for b in occupied:
                        if part['x']<b['x']+b['w']+8 and part['x']+part['w']+8>b['x']:
                            ys.add(max(490,b['y']+b['h']+10-part['y']))
                for y in sorted(ys):
                    actual=[dict(q,y=q['y']+y) for q in parts]
                    if all(not overlap(q,b,7) for q in actual for b in occupied):
                        options.append((y+h,abs(tx-xx),tx,y,actual));break
            _,_,tx,y,parts=min(options)
            occupied.extend(parts);placed.append(dict(item,tx=tx,y=y))
        return max(b['y']+b['h'] for b in occupied),placed
    orders=[sorted(items,key=lambda r:(-frequency[r['n']['year']],-r['h'],r['n']['year'])),sorted(items,key=lambda r:-r['n']['year']),sorted(items,key=lambda r:(-r['h'],r['n']['year']))]
    for seed in range(12):
        order=items.copy();random.Random(310+seed).shuffle(order);orders.append(order)
    height,placed=min((layout(order) for order in orders),key=lambda pair:pair[0])
    for year in [1960,1980,1990,2000,2004,2008,2012,2016,2018,2020,2022,2024,2026]:
        xx=xyear(year)
        p.line([(xx,470),(xx,height+15)],'#E5DDD0',1,track=False,dash='3 9')
    for r in placed:
        n,tx,y,xx=r['n'],r['tx'],r['y'],r['xx']
        color=TEAL if n['domain']=='Architecture' else CORAL
        p.record(n['id'],tx,y+32,r['w'],n['title'],n['note'],color,f"{n['year']}  ·  {n['kind'].upper()}"+('  /  CONCEPTUAL SPECIMEN' if n['id'] in illustrated else ''),size=18,title_size=28,url=n['url'],source='architecture',image=illustrated.get(n['id']))
        g=p.body.find(f".//*[@data-record-id='{n['id']}']")
        ET.SubElement(g,tag('circle'),cx=str(xx),cy=str(y+4),r='5',fill=color,**{'data-date-owner':n['id'],'data-year':str(n['year'])})
        port=max(tx+12,min(tx+r['w']-12,xx))
        p.line([(xx,y+4),(xx,y+17),(port,y+17),(port,y+32)],color,1.4,source=n['id'],target=n['id'],kind='dated-at')
        p.marks.append(dict(owner=n['id'],year=n['year'],x=xx,y=y+4))
    comparison_top=height+90
    p.heading(65,comparison_top,'WHAT RETURNS UNDER A NEW NAME?', 'Six comparisons from the article, outside the calendar.',1350,GOLD)
    for i,row in enumerate(TABLES['architecture'][0]['rows']):
        x=65+i*980;y=comparison_top+70
        ident=f'comparison-{i+1:02d}'
        p.art([3,0,1,10,5,7][i],x+12,y+45,220,200,ident,row['cells'][0])
        p.record(ident,x+250,y,680,row['cells'][0],row['cells'][1]+'\nMODEL CHANGES: '+row['cells'][2],GOLD,'CONCEPTUAL COMPARISON',size=20,title_size=31,source_line=row['line'])
    novel_top=max(r['y']+r['h'] for r in p.records if r['id'].startswith('comparison-'))+115
    p.heading(65,novel_top,'WHAT IS ACTUALLY DIFFERENT?', 'The article’s four sources of probabilistic pressure.',2000,PURPLE)
    changes=[('Probabilistic control plane','The model can construct plans, arguments and stopping conditions. Validate the resulting control flow.',2),('Language as an interface','Instructions and data share a medium. Version interfaces, validate schemas and make trust boundaries explicit.',3),('Learned system structure','Behavior depends partly on weights and training data. Architectural reasoning needs empirical evaluation.',9),('Shared model, coupled failures','One model can fill many roles. Different agent names do not establish independent failure modes.',10)]
    for i,(title,note,art) in enumerate(changes):
        xx=65+i*1470;yy=novel_top+65
        ident=f'pressure-{i+1:02d}'
        p.art(art,xx+12,yy,180,150,ident,title)
        p.record(ident,xx+230,yy,1140,title,note,PURPLE,'CONCEPTUAL SPECIMEN',size=23,title_size=32)
    bottom=max(r['y']+r['h'] for r in p.records)+35
    p.finish(math.ceil(bottom+155),'Source: Guillermo Villarroel, “AI architecture: old systems ideas under probabilistic pressure”, 2 Aug 2026. All 60 milestone notes and primary-source links are retained. 1986 backpropagation marks a landmark demonstration, not a priority claim. Images are conceptual specimens, not historical hardware.',[3800,475,2120,1180])
    path=OUT/p.case/'manifest.json';m=json.loads(path.read_text(encoding='utf-8'))
    m['time_segments']=[dict(start=s[0],end=s[1],x=s[2],width=s[3]) for s in segments]
    m['source_milestones']=milestones;m['packing_candidates']=len(orders)
    path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def agent():
    p = Poster('02-agent', 'INSIDE A RELIABLE AGENT', 'A field guide to context, authority, tools and evidence — follow one bounded step, then inspect the machinery that makes it dependable.', '02 / 03')
    p.heading(65, 273, 'CONTEXT IS ASSEMBLED, NOT JUST REMEMBERED', 'Eleven entry points, grouped by when they affect a run. Each mechanism has a distinct failure mode.', 2250, TEAL)
    categories = [
        ('BEFORE A STEP', [0, 1, 2], TEAL),
        ('WHEN NEEDED', [3, 4], GOLD),
        ('ACROSS STEPS', [5, 6, 7], BLUE),
        ('AT A BOUNDARY', [8, 9, 10], PURPLE),
    ]
    context = [
        ('Privileged instructions', 'System, developer and repository rules.\nRISK: stale policy or conflicting precedence.'),
        ('Tool contracts', 'Schemas, permissions, errors and results.\nRISK: ambiguous tools or injected output.'),
        ('Pre-call retrieval', 'Ranked chunks, examples and user data.\nRISK: misses, noise or weak provenance.'),
        ('Just-in-time discovery', 'Load files, resources or tool catalogs as needed.\nRISK: wrong source or stopping too soon.'),
        ('Progressive skills', 'Catalog → instructions → needed resources.\nRISK: wrong trigger or stale version.'),
        ('Trajectory', 'Messages, calls, observations and errors.\nRISK: growth, duplicates and stale evidence.'),
        ('External working state', 'Files, ledgers, plans and checkpoints.\nRISK: state drifts out of sync.'),
        ('Long-term memory', 'Episodes, facts, preferences and outcomes.\nRISK: polluted or falsely promoted memory.'),
        ('Compaction / restart', 'A summary plus valuable current state.\nRISK: omitted constraints and repeated work.'),
        ('Handoff', 'A bounded brief plus returned evidence.\nRISK: lost constraints or unverifiable synthesis.'),
        ('Evolved context', 'Persistent prompt, skill or memory-policy changes.\nRISK: overfitting and regression.'),
    ]
    for ci, (title, indices, color) in enumerate(categories):
        gx = 65 + ci * 735
        p.text(p.body, gx + 8, 365, title, 23, True, color)
        cw = (700 - (len(indices) - 1) * 18) / len(indices)
        for j, idx in enumerate(indices):
            xx = gx + j * (cw + 18)
            r = p.record(f'context-{idx + 1:02d}', xx, 400, cw, context[idx][0], context[idx][1], color, f'C{idx + 1:02d}', size=18, title_size=27, url='https://github.com/gvillarroel/blog/blob/main/knowledge/public/agent-systems/context.md#L'+str(TABLES['agent-context'][0]['rows'][idx]['line']), source='agent-context', source_line=TABLES['agent-context'][0]['rows'][idx]['line'])
            p.line([(xx + cw / 2, r['y'] + r['h'] + 8), (xx + cw / 2, 695), (gx + 340, 695)], color, 1.3, source=r['id'], target='run-context', kind='supplies-context')
        p.line([(gx + 340, 695), (gx + 340, 726)], color, 1.2, source=f'context-{indices[0] + 1:02d}', target='run-context', kind='assembly-group')
    p.line([(405,726),(2610,726)],MUTED,1.5,source='context-01',target='run-context',kind='selected-context-bus')
    p.line([(925,726),(925,825)],TEAL,2,source='context-05',target='run-context',kind='assembled-context',arrow=True)

    p.heading(65, 787, 'ONE BOUNDED STEP', width=550, color=INK)
    stages = [
        ('run-authority', 'Authority gate', 'Check policy, identity and budget. A model naming a capability does not acquire permission to use it.', CORAL, 4),
        ('run-context', 'Context + orchestration', 'Select evidence and instructions, route the step and keep completion criteria explicit.', TEAL, 0),
        ('run-model', 'Model proposal', 'Interpret the context; propose an answer or a tool call. Generated intent still needs validation.', PURPLE, 2),
        ('run-tools', 'Authorized tools', 'Validate arguments and permissions, execute through adapters, then return observable results.', GOLD, 1),
        ('run-verifier', 'Verified outcome', 'Check the answer or changed world. Pass, repair within budget, or stop with a recorded failure.', SAGE, 7),
    ]
    stage_records = []
    for i, (ident, title, detail, color, image) in enumerate(stages):
        xx = 65 + i * 590
        r = p.record(ident, xx, 838, 460, title, detail, color, f'STEP {i + 1}  /  CONCEPTUAL SPECIMEN', size=22, title_size=39, image=image)
        stage_records.append(r)
    for i in range(4):
        connector(p, stage_records[i], stage_records[i + 1], stages[i][3], ['permits', 'conditions', 'proposes\na call', 'outcome +\nevidence'][i], y=1020, kind=['authorizes', 'conditions', 'proposes', 'verifies'][i])
    # A model may propose an answer without calling a tool. This bypass is explicit.
    p.line([(1475, 828), (1475, 792), (2660, 792), (2660, 828)], PURPLE, 1.5, source='run-model', target='run-verifier', kind='answer-without-tool', dash='7 6', arrow=True)
    p.text(p.body, 1790, 778, 'ANSWER WITHOUT A TOOL CALL', 16, True, PURPLE)
    loop_y = 1346
    run = stage_records[3]
    p.line([(run['x'] + 200, run['y'] + run['h'] + 8), (2035, 1298), (1445, 1298), (1445, stage_records[2]['y'] + stage_records[2]['h'] + 8)], GOLD, 2, source='run-tools', target='run-model', kind='observation', arrow=True)
    p.text(p.body, 1625, 1285, 'OBSERVATIONS UPDATE THE NEXT PROPOSAL', 16, True, GOLD)
    p.line([(2660, stage_records[4]['y'] + stage_records[4]['h'] + 8), (2660, loop_y), (840, loop_y), (840, stage_records[1]['y'] + stage_records[1]['h'] + 8)], SAGE, 2, source='run-verifier', target='run-context', kind='bounded-repair', arrow=True)
    p.text(p.body, 1110, loop_y + 30, 'REPAIR LOOP  ·  EXPLICIT STEP, TIME AND COST LIMITS  ·  NO UNBOUNDED RETRIES', 18, True, SAGE)

    p.heading(65, 1464, 'FIVE GRAPHS, FIVE DIFFERENT KINDS OF TRUTH', 'The article proposes “graph engineering” as an architectural discipline. These edge meanings are not interchangeable.', 2500, INK)
    graph_by_name = {r['cells'][0]: r for r in TABLES['architecture'][1]['rows']}
    graph_order = [('Control', CORAL, 4, 'run-authority'), ('Knowledge', TEAL, 0, 'run-context'), ('Evidence', PURPLE, 9, 'run-model'), ('Execution', GOLD, 5, 'run-tools'), ('Evaluation', SAGE, 6, 'run-verifier')]
    for i, (name, color, art, owner) in enumerate(graph_order):
        x = 65 + i * 590
        row = graph_by_name[name]
        nodes, edges, invariant = row['cells'][1:]
        ident='graph-'+name.lower()
        p.art(art, x+6, 1580, 155, 145, ident, name+' graph')
        p.text(p.body, x+14, 1568, name.upper(), 34, True, color, True)
        p.text(p.body, x+8, 1745, 'Conceptual specimen', 15, color=MUTED)
        sample=[('Principal','Capability','may-call'),('Claim','Document','derived-from'),('Observation','Answer span','entails'),('Tool call','Event','produced'),('Test','Requirement','measures')][i]
        for j,label in enumerate(sample[:2]):
            yy=1587+j*100
            p.rect(p.body,x+186,yy,262,44,pale(color),color,5)
            p.text(p.body,x+317-measure(label,21,True)/2,yy+29,label,21,True,color)
        p.line([(x+205,1635),(x+205,1680)],color,2,ident='sample-'+name.lower(),source=ident,target=ident,kind=sample[2],arrow=True)
        p.text(p.body,x+223,1665,sample[2],18,True,color)
        p.record(ident, x, 1780, 460, 'Relations & invariant', nodes + '\nRELATIONS: ' + edges + '\nINVARIANT: ' + invariant, color, size=20, title_size=28, source_line=row['line'])
    p.heading(65, 2072, 'EIGHT OLDER IDEAS THAT KEEP THE LOOP HONEST', 'The architectural toolkit below addresses specific production failures.', 1800, TEAL)
    resilience = [
        ('Information hiding', 'Use stable adapters; absorb vendor and tool churn.'),
        ('Bulkheads + breakers', 'Isolate failures; cap repeated calls to a troubled dependency.'),
        ('Event sourcing', 'Keep durable events so runs can be reconstructed and replayed.'),
        ('Sagas', 'Pair long actions with compensations for partial completion.'),
        ('Fitness functions', 'Continuously check the architectural properties that matter.'),
        ('Backpressure', 'Limit admitted work when downstream resources saturate.'),
        ('Least authority', 'Grant narrow capabilities; separate proposals from permission.'),
        ('Ownership boundaries', 'Give prompts, data, tools and policies accountable owners.'),
    ]
    for i, (title, note) in enumerate(resilience):
        row = TABLES['architecture'][2]['rows'][i]
        p.record(f'resilience-{i + 1:02d}', 65 + (i % 4) * 735, 2130 + (i // 4) * 158, 695, title, note, COLORS[i % 6], f'R{i + 1:02d}', size=20, title_size=28, source_line=row['line'])
    p.finish(2570, 'Sources: the blog architecture article (2 Aug 2026) and public agent-systems collection (13 Aug 2026); Agent Skills specification and Anthropic agent-design guide checked 13 Sep 2026. The central loop is an editorial synthesis. Every illustration is a conceptual specimen; it is not a literal machine.', [620, 740, 2290, 670])


def evaluation():
    p = Poster('03-evaluation', 'FROM EVALUATION TO SKILL EVOLUTION', 'Make one causal comparison, keep the evidence, then earn the right to release — a map of the blog’s evaluation protocol.', '03 / 03')
    p.heading(65, 273, 'FREEZE THE EXPERIMENT BEFORE YOU START', 'A score belongs to a model + harness + skill + protocol configuration. The intended treatment is skill availability.', 2300, INK)
    fixed = [
        ('identity-model', 'Model', 'Identity, version, context limit and decoding settings.', BLUE, 'FIXED'),
        ('identity-harness', 'Harness', 'Commit, configuration, tool permissions, resources and budgets.', TEAL, 'FIXED'),
        ('identity-skill', 'Skill bundle', 'The complete versioned directory; hash instructions, resources and scripts.', CORAL, 'THE DECLARED TREATMENT'),
        ('identity-protocol', 'Evaluation protocol', 'Tasks, worlds, scorers, repetitions, budgets and promotion rules.', PURPLE, 'FIXED'),
    ]
    for i, (ident, title, note, color, kicker) in enumerate(fixed):
        p.record(ident, 65 + i * 735, 345, 695, title, note, color, kicker, size=22, title_size=37, url=EVAL_URL, source='evaluation', source_line=TABLES['evaluation'][0]['rows'][i]['line'], fill=ident == 'identity-skill')
    p.text(p.body, 65, 555, 'P01 ONE TREATMENT   ·   P03 COMPLETE IDENTITIES   ·   P02 RESET WORKSPACES, CACHES AND MEMORY BETWEEN TRIALS', 19, True, MUTED)

    p.heading(65, 636, 'PAIR THE SAME TASK IN TWO WORLDS', 'Availability includes discovery: a skill that is never found can have zero practical lift.', 1650, TEAL)
    task = p.record('paired-task', 65, 844, 310, 'Same task i', 'The same task, scoring rules and resource budget feed both arms.', BLUE, 'PAIRED DESIGN', size=22, title_size=35, url=EVAL_URL, source='evaluation')
    arms = []
    for i, (title, color, status) in enumerate([('Skill withheld', BLUE, 'BASELINE'), ('Skill available', CORAL, 'CANDIDATE')]):
        yy = 710 + i * 340
        ident = 'arm-' + str(i)
        p.art(8, 465, yy, 160, 170, ident, 'The same isolated workspace in both arms')
        if i==1:
            p.art(3,631,yy+34,76,111,ident,'Skill available in the same workspace')
        r = p.record(ident, 710, yy + 8, 410, title, 'Same model + harness.\nRepeat attempts within this task.\nRecord the outcome even if it fails.', color, status + '  /  CONCEPTUAL SPECIMEN', size=21, title_size=35, url=EVAL_URL, source='evaluation')
        arms.append(r)
        cy = yy + 105
        p.line([(385, 950), (430, 950), (430, cy), (454, cy)], color, 2, source='paired-task', target=ident, kind='paired-input', arrow=True)
        p.line([(1132, yy + 105), (1185, yy + 105), (1185, 983), (1250, 983)], color, 2, source=ident, target='task-lift', kind='paired-outcome', arrow=True)
    p.art(6, 1315, 709, 265, 212, 'task-lift', 'Paired task lift')
    lift = p.record('task-lift', 1260, 936, 515, 'Compare within each task', 'Lift(i) = mean score with the skill\n− mean score without the skill.\nAggregate paired task differences using declared weights.', GOLD, 'P08  /  CONCEPTUAL SPECIMEN', size=23, title_size=34, url=EVAL_URL, source='evaluation')
    p.record('task-uncertainty', 1260, 1200, 515, 'Tasks are the statistical unit', 'Attempts are nested observations. Use task- or cluster-level uncertainty; do not pool every attempt as independent.', GOLD, size=20, title_size=28, url=EVAL_URL, source='evaluation')
    p.record('availability-effect', 65, 1300, 1040, 'Do not change the question after treatment', 'Availability lift includes failure to discover, read or follow the skill. Triggered-only performance is a diagnostic. Forced injection does not test discoverability. Include both positive and negative trigger cases.', TEAL, size=19, title_size=28, url=EVAL_URL, source='evaluation')

    p.heading(1880, 636, 'KEEP RAW EVIDENCE; LAYER THE JUDGMENT', 'P06 immutable traces  /  P04 layered scoring', 1050, PURPLE)
    p.art(5, 1895, 690, 220, 200, 'raw-evidence', 'Immutable raw evidence')
    p.record('raw-evidence', 2130, 714, 760, 'Preserve the original run', 'Outcomes, complete trajectories, artifacts, errors, time, tokens and cost. A regrade creates a new view; it does not rewrite raw evidence.', PURPLE, 'CONCEPTUAL SPECIMEN', size=22, title_size=35, url=EVAL_URL, source='evaluation')
    grade = [
        ('grade-tests', '1  Deterministic checks', 'Inspect files, APIs and the changed world with executable tests.', TEAL),
        ('grade-semantic', '2  Calibrated semantic review', 'Version the judge and rubric; cite evidence; compare with blinded human judgments.', PURPLE),
        ('grade-policy', '3  Policy + release gates', 'Reject safety or contract violations; keep critical strata visible.', CORAL),
    ]
    for i, (ident, title, note, color) in enumerate(grade):
        p.record(ident, 1900, 944 + i * 139, 990, title, note, color, size=21, title_size=30, url=EVAL_URL, source='evaluation', fill=True)
    p.line([(1185,983),(1185,681),(2010,681)],PURPLE,1.5,source='arm-0',target='raw-evidence',kind='retain-both-arms')
    p.line([(2010,902),(1830,902),(1830,1280)],PURPLE,1.5,source='raw-evidence',target='grade-policy',kind='evidence-for-grading')
    for i,(ident,title,note,color) in enumerate(grade):
        p.line([(1830,1000+i*139),(1890,1000+i*139)],color,1.5,source='raw-evidence',target=ident,kind='graded-view',arrow=True)

    p.heading(65, 1465, 'EVOLVE ON DEVELOPMENT DATA; RELEASE THROUGH A SEALED GATE', 'P05 disjoint data roles  /  P07 hard gates before trade-offs  /  P10 independent release authority', 2850, INK)
    partitions = [
        ('split-discovery', 'Discovery', 'Diagnose failure cases. Define task families, target behavior and the evaluation population.', BLUE),
        ('split-development', 'Development', 'Mutate under a declared budget. Retain every candidate and its evidence; do not hide failed attempts.', TEAL),
        ('split-validation', 'Validation', 'Select a frozen finalist using held-aside tasks. Stop when the predeclared rule says to stop.', GOLD),
        ('split-holdout', 'Sealed holdout', 'One-way final verification. Keep tasks and feedback away from the mutator; retire exposed holdouts.', PURPLE),
        ('split-release', 'Independent release', 'An independent authority checks identities, hard gates, uncertainty and important task strata.', SAGE),
    ]
    splitrecs = []
    for i, (ident, title, note, color) in enumerate(partitions):
        x = 65 + i * 590
        r = p.record(ident, x, 1560, 455, title, note, color, f'{i + 1:02d}  /  SEPARATE ROLE', size=22, title_size=37, url=EVAL_URL, source='evaluation')
        splitrecs.append(r)
        if i < 4:
            p.line([(x + 463, 1620), (x + 573, 1620)], color, 2.6, source=ident, target=partitions[i + 1][0], kind='gate', arrow=True)
    p.art(11, 1930, 1820, 215, 170, 'split-holdout', 'Sealed holdout: conceptual specimen')
    p.text(p.body, 1930, 2020, 'SEALED HOLDOUT', 22, True, PURPLE)
    p.text(p.body, 1930, 2045, 'Conceptual specimen', 16, color=MUTED)
    p.record('gate-rejection', 75, 1870, 1700, 'Failed gate → archive the candidate and all evidence', 'Semantic failure and exhausted task budgets are outcomes. Retry only verified external failures under symmetric, capped rules, retaining the original attempt. A release failure is not a license to tune against the holdout.', CORAL, 'P09  /  FAILURE TAXONOMY', size=23, title_size=35, url=EVAL_URL, source='evaluation', fill=True)
    p.line([(1465, splitrecs[2]['y'] + splitrecs[2]['h'] + 8), (1465, 1850), (1350, 1850), (1350, 1860)], CORAL, 1.6, source='split-validation', target='gate-rejection', kind='failed-gate', arrow=True)
    p.record('release-objectives', 2400, 1850, 490, 'Keep trade-offs visible', 'Averages can conceal regressions. Report quality, cost and latency together; enforce hard gates and critical-stratum limits first.', SAGE, size=21, title_size=31, url=EVAL_URL, source='evaluation')

    p.heading(65, 2177, 'SIX QUESTIONS THAT MAKE A PROMOTION CLAIM CREDIBLE', 'A compact validity ledger. Each answer needs retained evidence.', 1850, INK)
    validity = [
        ('Construct', 'Did the tasks measure the capability you intended?'),
        ('Attribution', 'Was skill availability the only declared treatment?'),
        ('Statistical', 'Are task-level uncertainty and missing results explicit?'),
        ('Evaluator', 'Are scorers calibrated, versioned and evidence-based?'),
        ('External', 'Which task families and deployment conditions does this cover?'),
        ('Security', 'Can inputs, artifacts or a mutator influence the grader or holdout?'),
    ]
    for i, (title, detail) in enumerate(validity):
        p.record('validity-' + title.lower(), 65 + (i % 3) * 650, 2240 + (i // 3) * 152, 610, title, detail, COLORS[i], size=21, title_size=30, url=EVAL_URL, source='evaluation', source_line=TABLES['evaluation'][2]['rows'][i]['line'])
    p.heading(2090, 2177, 'CHOOSE BY THE THING YOU OBSERVE', 'Illustrative roles from the article’s Aug 2026 snapshot.', 850, TEAL)
    roles = [
        ('Changed world', 'Harbor · isolated task execution', 'evaluation', 3),
        ('Output or trace', 'Inspect AI · Promptfoo · OpenAI Evals', 'evaluation', 3),
        ('Lifecycle evidence', 'MLflow · Langfuse · Phoenix', 'evaluation', 9),
        ('Candidate evolution', 'GEPA · Trace2Skill · WikiSkill', 'evaluation', 11),
    ]
    for i, (title, detail, source, table) in enumerate(roles):
        p.record('role-' + str(i + 1), 2090, 2240 + i * 85, 800, title, detail, TEAL, size=19, title_size=25, url=EVAL_URL, source=source, source_line=TABLES[source][table]['line'])
    p.finish(2720, 'Source: Gerardo Villarroel, “From benchmarks to skill evolution”, published 24 Aug 2026, updated 30 Aug 2026. Framework names indicate selected roles, not a current ranking or a complete stack. This is a protocol map, not an empirical experiment; no performance results are fabricated.', [50, 670, 1735, 685])


if __name__ == '__main__':
    choices = {'history': history, 'agent': agent, 'evaluation': evaluation}
    for case in sys.argv[1:] or choices:
        choices[case]()
