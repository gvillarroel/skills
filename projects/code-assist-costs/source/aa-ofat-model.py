#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Offline, exact request-ledger and completion model. No target execution."""
import math
import platform

MODEL_METADATA = {"modelId":"aa-anchored-ofat-ledger", "modelVersion":"1.0.0",
    "engine":"python-standard-library", "engineVersion":platform.python_version(),
    "rng":"none-exact-expectations", "rngVersion":platform.python_version(),
    "reproducibility":"exact-within-locked-environment"}

def retry(p, cap, rho):
    independent = sum((1-p)**j for j in range(cap))
    return (rho*p+(1-rho)*(1-(1-p)**cap),
            rho*(p+cap*(1-p))+(1-rho)*independent)

def ledger(p):
    stable = p['system_tokens']+p['schema_tokens']
    context = stable+p['background_tokens']+p['user_delta']
    cached = 0.0
    tools = int(p['base_tools']+p['tool_delta'])
    batch = int(p['batch_size'])
    groups = [min(batch,tools-i) for i in range(0,tools,batch)]+[0]
    # Total task output is frozen for the tool-count and batching experiments.
    output = p['base_output']*p['output_factor']/len(groups)
    rows, main_contexts, fidelities = [], [], []
    compactions = 0
    def record(kind, total, eligible, out, write_new):
        hit = min(total,eligible)*p['cache_hit'] if p['cache_enabled'] else 0
        write = (total-hit)*write_new if p['cache_enabled'] else 0
        uncached = total-hit-write
        high = total>p['tier_threshold']
        fi = p['long_input_factor'] if high else 1
        fo = p['long_output_factor'] if high else 1
        components = [uncached*p['input_price']*fi/1e6, hit*p['read_price']*fi/1e6,
                      write*p['write_price']*fi/1e6, out*p['output_price']*fo/1e6]
        rows.append(dict(kind=kind,input=total,read=hit,write=write,uncached=uncached,
            output=out,usd=sum(components),input_usd=components[0]+components[1]+components[2],
            output_usd=components[3],long_tier=high))
    for group in groups:
        if p['compact_cap']>0 and context>p['compact_cap']:
            record('compact',context,cached*p['compactor_cache'],p['summary_tokens'],0)
            context = stable+p['summary_tokens']
            cached = stable*p['retain_prefix']
            compactions += 1
        record('main',context,cached,output,1)
        main_contexts.append(context)
        fidelities.append(p['summary_fidelity']**compactions)
        cached = context
        context += output*(1-p['reasoning_share']) + group*p['tool_payload']*p['payload_factor']
    exposure = sum(max(x-p['rot_onset'],0)/1e5 for x in main_contexts)/len(main_contexts)
    if p['quality_link']=='cliff':
        penalty = p['rot_beta']*float(max(main_contexts)>p['rot_onset'])
    else:
        penalty = p['rot_beta']*exposure
    fidelity = sum(fidelities)/len(fidelities)
    if p['fidelity_link']=='critical':
        fidelity = p['summary_fidelity']**(p['critical_facts']*compactions)
    q0 = p['success_probability']
    q = 0 if q0==0 or fidelity==0 else (1 if q0==1 and penalty==0 and fidelity==1 else
        1/(1+math.exp(-(math.log(min(q0,1-1e-12)/(1-min(q0,1-1e-12)))-penalty+math.log(fidelity)))))
    complete, attempts = retry(q,int(p['attempt_cap']),p['failure_rho'])
    cost = sum(r['usd'] for r in rows)+tools*p['tool_fee']
    spend = cost*attempts
    return rows, dict(attempt_usd=cost,submitted_usd=spend,completion=complete,
        correct_usd=spend/complete if complete else 0, completion_defined=float(complete>0),
        attempts=attempts,month_1k_usd=1000*spend,month_1m_usd=1e6*spend,
        loss_usd=spend+(1-complete)*p['failure_loss'],
        input_usd=sum(r['input_usd'] for r in rows),output_usd=sum(r['output_usd'] for r in rows),
        max_context=max(main_contexts),compactions=compactions,main_calls=len(groups),
        exposure=exposure,fidelity=fidelity,tool_calls=tools)

def simulate(run):
    rows,out=ledger(run['parameters'])
    ok=all(r['input']>=0 and min(r['read'],r['write'],r['uncached'])>=-1e-8
        and abs(r['input']-r['read']-r['write']-r['uncached'])<1e-7 for r in rows)
    ok = ok and 0<=out['completion']<=1 and all(math.isfinite(x) for x in out.values())
    return {'outcomes':out,'diagnostics':[{'check_id':'exclusive-token-ledger','status':'pass' if ok else 'fail',
        'invalidates_hypotheses':not ok,'message':'Independent input partition, nonnegative cost and bounded completion checks.'}]}
