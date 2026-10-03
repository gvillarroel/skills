#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Conservative quality rewards with explicit bounds for unresolved dimensions."""
from svg_art_direction import DIMENSIONS


def aggregate(decisions,candidate_side):
    required=set(DIMENSIONS)|{"overall","brief_A","brief_B"}
    if candidate_side not in {"A","B"} or set(decisions)!=required:
        raise ValueError("Incomplete decisions or invalid candidate binding")
    choices={k:v["raw"]["choice"] for k,v in decisions.items()}
    confidences={k:v["raw"]["confidence"] for k,v in decisions.items()}
    other="B" if candidate_side=="A" else "A"
    points={candidate_side+"_clear":100,candidate_side+"_slight":95,"parity":90,other+"_slight":75,other+"_clear":50}
    uncertain=[k for k in DIMENSIONS if choices[k]=="unknown"]
    fit=choices["brief_"+candidate_side]
    if fit=="unknown":
        low=high=None
    elif fit=="wrong":
        low=high=0.0
    else:
        cap={"fulfilled":100,"minor_gap":79,"major_missing":49}[fit]
        low=min(cap,sum(weight*(50 if choices[key]=="unknown" else points[choices[key]])/100 for key,(weight,*_) in DIMENSIONS.items()))
        high=min(cap,sum(weight*(100 if choices[key]=="unknown" else points[choices[key]])/100 for key,(weight,*_) in DIMENSIONS.items()))
    return {
        "curated_design_quality":None if low is None else low/100,
        "score_100":low,"score_interval_100":[low,high],
        "point_score_100":low if low==high else None,
        "uncertain_dimensions":uncertain,
        "overall_preference_unresolved":choices["overall"]=="unknown",
        "choices":choices,"confidence":confidences,
        "review_recommended":low is None or bool(uncertain) or choices["overall"]=="unknown" or min(confidences.values())<.3,
        "score_meaning":"Conservative anchor-relative reward: parity=90 by convention. Unresolved dimensions retain their full possible 50–100 band, not a fabricated point estimate. Reward is the lower bound. Overall preference is a separate diagnostic; absent subject judgment yields no reward.",
    }
