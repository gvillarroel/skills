#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Build the synthetic Heatwave Tree acceptance brief."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def ref(value_id: str) -> dict[str, str]:
    return {"ref": value_id}


def op(name: str, *args: Any) -> dict[str, Any]:
    return {"op": name, "args": list(args)}


def module(
    module_id: str,
    question: str,
    claim: str,
    asset_type: str,
    values: list[str],
    rationale: str,
    rejected: str,
    *,
    diagram: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": module_id,
        "question": question,
        "claim": claim,
        "assetType": asset_type,
        "values": values,
        "selectionRationale": rationale,
        "rejectedAlternative": rejected,
    }
    if diagram is not None:
        result["diagram"] = diagram
    return result


def structural_diagram(
    prefix: str,
    nodes: list[tuple[str, str, str, str | None]],
    edges: list[tuple[str, str, str, str]],
    *,
    layout: str = "tree",
) -> dict[str, Any]:
    return {
        "layout": layout,
        "nodes": [
            {
                "id": node_id,
                "label": label,
                "kind": kind,
                **({"bind": binding} if binding else {}),
            }
            for node_id, label, kind, binding in nodes
        ],
        "links": [
            {
                "id": f"{prefix}-{index + 1}",
                "source": source,
                "target": target,
                "kind": kind,
                "label": label,
            }
            for index, (source, target, kind, label) in enumerate(edges)
        ],
    }


def build_brief() -> dict[str, Any]:
    concepts = [
        {"id": "heat-index-anomaly", "label": "Heat-index anomaly", "unit": "°C", "default": 2, "domain": [0, 12]},
        {"id": "exposed-population", "label": "Exposed population", "unit": "people", "default": 1_000_000, "domain": [500_000, 1_500_000], "interpolation": "step"},
        {"id": "grid-firm-capacity", "label": "Firm grid capacity", "unit": "MW", "default": 1600, "domain": [800, 2200]},
        {"id": "water-available", "label": "Water available", "unit": "ML/day", "default": 620, "domain": [300, 800]},
        {"id": "canopy-cover", "label": "Canopy cover", "unit": "fraction", "default": 0.22, "domain": [0.1, 0.5]},
        {"id": "response-budget", "label": "Emergency response budget", "unit": "USD million", "default": 40, "domain": [0, 300]},
        {"id": "home-cooling-coverage", "label": "Installed home cooling", "unit": "fraction", "default": 0.72, "domain": [0.4, 0.98]},
        {"id": "vulnerable-share", "label": "Vulnerable population share", "unit": "fraction", "default": 0.28, "domain": [0.1, 0.5]},
        {"id": "base-cooling-demand", "label": "Base cooling demand", "unit": "MW", "default": 900, "domain": [600, 1400]},
        {"id": "surge-bed-capacity", "label": "Heat surge bed capacity", "unit": "beds", "default": 1200, "domain": [700, 2200], "interpolation": "step"},
        {"id": "transit-cooling-capacity", "label": "Cooling-center transit capacity", "unit": "people", "default": 80_000, "domain": [30_000, 180_000], "interpolation": "step"},
    ]
    derived = [
        {"id": "cooling-demand", "label": "Heat-adjusted cooling demand", "unit": "MW", "compute": op("add", ref("base-cooling-demand"), op("multiply", ref("heat-index-anomaly"), 90))},
        {"id": "grid-load-ratio", "label": "Grid cooling load ratio", "unit": "fraction", "compute": op("divide", ref("cooling-demand"), ref("grid-firm-capacity"))},
        {"id": "grid-overload", "label": "Grid overload above reserve threshold", "unit": "fraction", "compute": op("max", op("subtract", ref("grid-load-ratio"), 0.85), 0)},
        {"id": "grid-reliability-penalty", "label": "Grid reliability penalty", "unit": "fraction", "compute": op("min", op("multiply", ref("grid-overload"), 0.75), 0.65)},
        {"id": "grid-reliability", "label": "Grid reliability", "unit": "fraction", "compute": op("subtract", 1, ref("grid-reliability-penalty"))},
        {"id": "effective-cooling-access", "label": "Effective home cooling access", "unit": "fraction", "compute": op("multiply", ref("home-cooling-coverage"), ref("grid-reliability"))},
        {"id": "pump-served-water", "label": "Pump-served water", "unit": "ML/day", "compute": op("multiply", ref("water-available"), ref("grid-reliability"))},
        {"id": "water-service-ratio", "label": "Water service ratio", "unit": "fraction", "compute": op("divide", ref("pump-served-water"), ref("water-available"))},
        {"id": "canopy-cooling-benefit", "label": "Living canopy cooling benefit", "unit": "fraction", "compute": op("multiply", ref("canopy-cover"), ref("water-service-ratio"))},
        {"id": "surface-heat-anomaly", "label": "Surface heat anomaly", "unit": "°C", "compute": op("multiply", ref("heat-index-anomaly"), op("subtract", 1, op("multiply", ref("canopy-cover"), 0.55)))},
        {"id": "indoor-heat-exposure", "label": "Indoor heat exposure index", "unit": "index", "compute": op("multiply", ref("heat-index-anomaly"), op("subtract", 1, ref("effective-cooling-access")), op("add", 1, ref("vulnerable-share")))},
        {"id": "indoor-thermal-lag", "label": "Nighttime indoor thermal lag", "unit": "index", "compute": op("multiply", ref("indoor-heat-exposure"), 0.75)},
        {"id": "severe-heat-cases", "label": "Severe heat cases", "unit": "cases/day", "compute": op("multiply", ref("indoor-heat-exposure"), ref("vulnerable-share"), 95)},
        {"id": "emergency-arrivals", "label": "Heat emergency arrivals", "unit": "cases/day", "compute": op("multiply", ref("severe-heat-cases"), 0.62)},
        {"id": "surge-load-ratio", "label": "Care surge load ratio", "unit": "fraction", "compute": op("divide", ref("emergency-arrivals"), ref("surge-bed-capacity"))},
        {"id": "home-protected-population", "label": "People protected at home", "unit": "people", "compute": op("multiply", ref("exposed-population"), ref("effective-cooling-access"))},
        {"id": "population-needing-centers", "label": "People needing shared cooling", "unit": "people", "compute": op("subtract", ref("exposed-population"), ref("home-protected-population"))},
        {"id": "center-served-population", "label": "People served by cooling centers", "unit": "people", "compute": op("min", ref("population-needing-centers"), ref("transit-cooling-capacity"))},
        {"id": "unprotected-population", "label": "People without effective cooling", "unit": "people", "compute": op("subtract", ref("exposed-population"), ref("home-protected-population"), ref("center-served-population"))},
        {"id": "stabilized-cases", "label": "Cases stabilized", "unit": "cases/day", "compute": op("multiply", ref("emergency-arrivals"), 0.82)},
        {"id": "escalated-cases", "label": "Cases requiring escalation", "unit": "cases/day", "compute": op("subtract", ref("emergency-arrivals"), ref("stabilized-cases"))},
        {"id": "drinking-water-allocation", "label": "Drinking water allocation", "unit": "ML/day", "compute": op("multiply", ref("water-available"), 0.55)},
        {"id": "canopy-water-allocation", "label": "Canopy water allocation", "unit": "ML/day", "compute": op("multiply", ref("water-available"), 0.25)},
        {"id": "water-reserve-allocation", "label": "Emergency water reserve", "unit": "ML/day", "compute": op("subtract", ref("water-available"), ref("drinking-water-allocation"), ref("canopy-water-allocation"))},
        {"id": "grid-budget", "label": "Grid response allocation", "unit": "USD million", "compute": op("multiply", ref("response-budget"), 0.30)},
        {"id": "water-budget", "label": "Water response allocation", "unit": "USD million", "compute": op("multiply", ref("response-budget"), 0.20)},
        {"id": "household-budget", "label": "Household response allocation", "unit": "USD million", "compute": op("multiply", ref("response-budget"), 0.25)},
        {"id": "care-budget", "label": "Care response allocation", "unit": "USD million", "compute": op("subtract", ref("response-budget"), ref("grid-budget"), ref("water-budget"), ref("household-budget"))},
        {"id": "adaptation-score", "label": "Whole-city adaptation score", "unit": "fraction", "compute": op("divide", op("add", ref("grid-reliability"), ref("effective-cooling-access"), ref("water-service-ratio"), ref("canopy-cover")), 4)},
    ]

    ordinary = {
        "heat-index-anomaly": 2,
        "exposed-population": 1_000_000,
        "grid-firm-capacity": 1600,
        "water-available": 620,
        "canopy-cover": 0.22,
        "response-budget": 40,
        "home-cooling-coverage": 0.72,
        "vulnerable-share": 0.28,
        "base-cooling-demand": 900,
        "surge-bed-capacity": 1200,
        "transit-cooling-capacity": 80_000,
    }
    heat_dome = {**ordinary, "heat-index-anomaly": 8, "water-available": 520, "response-budget": 85, "base-cooling-demand": 1050}
    compound = {**heat_dome, "grid-firm-capacity": 1100, "water-available": 420, "response-budget": 130, "surge-bed-capacity": 1050, "transit-cooling-capacity": 62_000}
    adapted = {**heat_dome, "grid-firm-capacity": 1900, "water-available": 610, "canopy-cover": 0.36, "response-budget": 220, "home-cooling-coverage": 0.90, "surge-bed-capacity": 1700, "transit-cooling-capacity": 140_000}
    scenarios = [
        {"id": "ordinary-summer", "label": "Ordinary summer", "values": ordinary},
        {"id": "heat-dome", "label": "Heat dome", "values": heat_dome},
        {"id": "compound-outage", "label": "Compound outage", "values": compound},
        {"id": "adapted-city", "label": "Adapted city", "values": adapted},
    ]

    modules: list[dict[str, Any]] = []
    modules.append(
        module(
            "city-pulse-hub",
            "Which canonical conditions govern the entire heatwave response tree?",
            "Eleven shared sources form the city pulse that every distant branch inherits.",
            "radial-structural-skill-tree",
            [item["id"] for item in concepts],
            "A radial structural tree makes the shared ancestry explicit without inventing arithmetic between peer inputs.",
            "A dashboard summary was rejected because it would not establish the lineage that binds distant districts.",
            diagram=structural_diagram(
                "pulse",
                [("pulse", "CITY PULSE", "root", None)]
                + [
                    (f"pulse-{index + 1}", item["label"], "notable" if index < 8 else "leaf", item["id"])
                    for index, item in enumerate(concepts)
                ],
                [("pulse", f"pulse-{index + 1}", "dependency", "Shared city condition") for index in range(len(concepts))],
                layout="radial",
            ),
        )
    )

    modules.extend(
        [
            module("heat-anomaly-series", "How intense is the initiating thermal signal?", "The heat-index anomaly is the initiating signal inherited by every exposure branch.", "heat-anomaly-line-series", ["heat-index-anomaly"], "A line-like signal trace foregrounds magnitude and scenario change.", "A radial gauge was rejected because the anomaly has no natural 100 percent ceiling."),
            module("heat-dome-lineage", "How does a heat signal become a citywide warning?", "The warning lineage joins the thermal signal with exposed population and vulnerability.", "heat-dome-structural-tree", ["heat-index-anomaly", "exposed-population", "vulnerable-share"], "A structural genealogy shows prerequisite ancestry without asserting a false numeric sum.", "A Sankey was rejected because people and temperature are not conserved branches of one quantity.", diagram=structural_diagram("heat-lineage", [("signal", "Thermal signal", "root", "heat-index-anomaly"), ("reach", "Population reached", "notable", "exposed-population"), ("vulnerability", "Vulnerability lens", "gate", "vulnerable-share"), ("warning", "City warning", "merge", None)], [("signal", "warning", "prerequisite", "Heat initiates warning"), ("reach", "warning", "dependency", "Population sets reach"), ("vulnerability", "warning", "dependency", "Vulnerability sets urgency")], layout="tree")),
            module("heat-exposure-field", "Where does the initiating signal meet unequal vulnerability?", "A spatial exposure field combines heat intensity, population, and vulnerability without conflating their units.", "heat-exposure-spatial-map", ["heat-index-anomaly", "exposed-population", "vulnerable-share"], "A spatial field is suited to co-located but differently scaled risk factors.", "Aligned bars were rejected because the three measures use incompatible units."),
            module("nocturnal-cooling-ledger", "What exact signals predict dangerous overnight retention?", "The ledger reconciles outdoor anomaly, indoor exposure, and nighttime lag as distinct exact measures.", "nocturnal-cooling-table", ["heat-index-anomaly", "indoor-heat-exposure", "indoor-thermal-lag"], "An exact table preserves unlike units while exposing the derived chain.", "A line chart was rejected because these are modeled states rather than sampled clock times."),
            module("warning-threshold", "How far has heat intensity crossed the warning threshold?", "The heat anomaly moves across a visible threshold without pretending to be bounded utilization.", "warning-threshold-bullet", ["heat-index-anomaly"], "A bullet track supports an unbounded threshold comparison.", "A semicircular gauge was rejected because the anomaly can legitimately exceed any nominal target."),
        ]
    )

    modules.extend(
        [
            module("land-cover-mosaic", "How do people and canopy occupy the built landscape?", "Population exposure and canopy cover share one spatial mosaic while retaining distinct scales.", "land-cover-spatial-map", ["exposed-population", "canopy-cover"], "A spatial mosaic makes co-location and protective cover visible.", "A pie chart was rejected because canopy and population are not parts of one whole."),
            module("surface-heat-ledger", "How much outdoor heat remains after canopy moderation?", "Surface heat remains high when canopy protection is sparse.", "surface-heat-table", ["heat-index-anomaly", "canopy-cover", "surface-heat-anomaly"], "A table states the exact moderation relationship across unlike units.", "A waterfall was rejected because canopy cover is not itself a temperature deduction."),
            module("shade-lineage", "Which built-fabric traits inherit or interrupt heat?", "Canopy and installed cooling become two distinct protective lineages around the heat signal.", "shade-structural-tree", ["heat-index-anomaly", "canopy-cover", "home-cooling-coverage", "surface-heat-anomaly"], "A branching tree makes protective ancestry legible.", "A flow band was rejected because the values do not conserve one shared unit.", diagram=structural_diagram("shade", [("heat", "Heat inheritance", "root", "heat-index-anomaly"), ("canopy", "Living shade", "notable", "canopy-cover"), ("cooling", "Installed cooling", "notable", "home-cooling-coverage"), ("surface", "Surface heat", "merge", "surface-heat-anomaly")], [("heat", "surface", "parent", "Heat enters the fabric"), ("canopy", "surface", "dependency", "Canopy moderates surface heat"), ("cooling", "surface", "dependency", "Cooling changes indoor protection")], layout="tree")),
            module("building-vulnerability-matrix", "Which household conditions shape indoor protection?", "Installed cooling and vulnerability expose the unequal starting conditions of buildings.", "building-vulnerability-matrix", ["home-cooling-coverage", "vulnerable-share", "effective-cooling-access"], "A matrix supports exact comparison of related fractions.", "A gauge was rejected because the task compares three related states rather than one target."),
            module("indoor-thermal-lag", "How strongly does heat persist indoors overnight?", "Indoor thermal lag rises when anomaly grows and effective cooling access falls.", "indoor-lag-line-series", ["indoor-thermal-lag"], "A signal line makes the modeled lag responsive across scenarios.", "A static card was rejected because the trajectory between scenarios is part of the explanation."),
        ]
    )

    modules.extend(
        [
            module("cooling-demand-series", "How much electrical demand does the heat signal add?", "Cooling demand grows from one base load plus the canonical heat anomaly.", "cooling-demand-line-series", ["cooling-demand"], "A line-like demand trace gives the branch a clear changing signal.", "A pie was rejected because demand is not a composition of categories here."),
            module("demand-capacity-bars", "Can firm capacity cover heat-adjusted cooling demand?", "Cooling demand and firm capacity share one zero-anchored MW scale.", "demand-capacity-bar-chart", ["cooling-demand", "grid-firm-capacity"], "Aligned bars provide the most truthful magnitude comparison in one unit.", "Independent gauges were rejected because they could normalize the peers differently."),
            module("substation-lineage", "How does firm capacity become reliable service?", "Firm capacity passes through load and overload gates before it becomes reliable service.", "substation-structural-tree", ["grid-firm-capacity", "cooling-demand", "grid-load-ratio", "grid-reliability"], "A prerequisite tree exposes capacity, pressure, and reliability as a causal lineage.", "A Sankey was rejected because MW and fractions cannot form conserved bands.", diagram=structural_diagram("grid", [("capacity", "Firm capacity", "root", "grid-firm-capacity"), ("demand", "Cooling demand", "root", "cooling-demand"), ("load", "Load gate", "merge", "grid-load-ratio"), ("reliability", "Reliable service", "notable", "grid-reliability")], [("capacity", "load", "dependency", "Capacity sets denominator"), ("demand", "load", "dependency", "Demand sets pressure"), ("load", "reliability", "dependency", "Overload reduces reliability")], layout="tree")),
            module("grid-reliability-bullet", "How much reliable grid service survives the heat load?", "Grid reliability falls as cooling demand crosses the reserve threshold.", "grid-reliability-bullet", ["grid-reliability"], "A bullet view shows one bounded service fraction against a full-service target.", "A decorative dial was rejected because threshold distance matters more than angle."),
            module("outage-cascade-tree", "Which protections fail downstream when the grid overloads?", "Grid overload propagates into water pumping and effective home cooling.", "outage-cascade-structural-tree", ["grid-overload", "grid-reliability", "pump-served-water", "effective-cooling-access"], "A structural fault tree exposes downstream inheritance without false conservation.", "A flow diagram was rejected because overload, water, and access use different units.", diagram=structural_diagram("outage", [("overload", "Overload", "root", "grid-overload"), ("reliability", "Grid reliability", "gate", "grid-reliability"), ("pumps", "Pump service", "leaf", "pump-served-water"), ("homes", "Home cooling", "leaf", "effective-cooling-access")], [("overload", "reliability", "dependency", "Overload erodes service"), ("reliability", "pumps", "dependency", "Power enables pumping"), ("reliability", "homes", "dependency", "Power enables cooling")], layout="tree")),
        ]
    )

    modules.extend(
        [
            module("reservoir-allocation-flow", "Where does the available water go during the response?", "Available water conserves across drinking, canopy, and emergency reserve allocations.", "reservoir-allocation-sankey-flow", ["water-available", "drinking-water-allocation", "canopy-water-allocation", "water-reserve-allocation"], "A conserved flow makes the allocation and shared source explicit.", "Grouped bars were rejected because they would hide the one-source partition."),
            module("pump-service-bullet", "What fraction of water service survives grid pressure?", "The pump-served share inherits grid reliability exactly.", "pump-service-bullet", ["water-service-ratio"], "A bounded bullet makes lost service and the full target visible.", "A radial decoration was rejected because the exact service gap is the primary task."),
            module("canopy-water-tree", "How do water and living canopy combine into neighborhood cooling?", "Pump-served water and canopy cover merge into one living-cooling benefit.", "canopy-water-structural-tree", ["water-available", "pump-served-water", "canopy-cover", "canopy-cooling-benefit"], "A merge tree makes the two-parent ecological lineage explicit.", "A flow was rejected because canopy cover is not an allocation branch of water.", diagram=structural_diagram("canopy", [("water", "Available water", "root", "water-available"), ("pumped", "Pump-served water", "gate", "pump-served-water"), ("canopy", "Canopy cover", "root", "canopy-cover"), ("benefit", "Cooling benefit", "merge", "canopy-cooling-benefit")], [("water", "pumped", "dependency", "Grid-powered pumps serve water"), ("pumped", "benefit", "dependency", "Served water sustains cooling"), ("canopy", "benefit", "dependency", "Canopy converts water into shade")], layout="tree")),
            module("cooling-ecology-map", "Where does the cooling ecology remain effective?", "Water service, canopy cover, and heat intensity form one spatial ecology.", "cooling-ecology-spatial-map", ["water-service-ratio", "canopy-cover", "heat-index-anomaly"], "A spatial view shows protective capacity and hazard in the same territory.", "A bar chart was rejected because the important question is co-location, not ranking."),
            module("cooling-island-ledger", "What exact ecological values explain cooling islands?", "The exact water, canopy, and benefit values audit the spatial cooling claim.", "cooling-island-table", ["water-available", "pump-served-water", "canopy-cover", "canopy-cooling-benefit"], "A ledger provides the precise evidence behind the map.", "Another map was rejected because this module's task is exact lookup."),
        ]
    )

    modules.extend(
        [
            module("cooling-access-lineage", "How does installed equipment become effective household protection?", "Installed cooling passes through grid reliability before it becomes effective access.", "cooling-access-structural-tree", ["home-cooling-coverage", "grid-reliability", "effective-cooling-access"], "A gate tree exposes why installed equipment and effective service diverge.", "A gauge was rejected because it would conceal the grid prerequisite.", diagram=structural_diagram("access", [("installed", "Installed cooling", "root", "home-cooling-coverage"), ("grid", "Reliable power", "gate", "grid-reliability"), ("effective", "Effective access", "notable", "effective-cooling-access")], [("installed", "effective", "parent", "Equipment creates potential"), ("grid", "effective", "dependency", "Power makes equipment usable")], layout="tree")),
            module("household-protection-ledger", "How many people are protected at home versus still seeking cooling?", "Effective access partitions the exposed population before transit capacity is applied.", "household-protection-table", ["exposed-population", "home-protected-population", "population-needing-centers"], "A table states the exact population hierarchy without pretending the subtotal is a peer.", "A stack was rejected because the next transit step changes only the unprotected branch."),
            module("vulnerability-access-matrix", "Does effective cooling reach the vulnerable share?", "Vulnerability and effective access remain separately inspectable while changing together across scenarios.", "vulnerability-access-matrix", ["vulnerable-share", "home-cooling-coverage", "effective-cooling-access"], "A matrix contrasts installed, effective, and vulnerable fractions.", "A single gauge was rejected because it would erase the access gap."),
            module("transit-cooling-network", "Which prerequisites determine cooling-center reach?", "Transit capacity connects the population needing centers to the people actually served.", "transit-cooling-structural-network", ["population-needing-centers", "transit-cooling-capacity", "center-served-population"], "A structural network exposes the capacity gate and served outcome.", "A Sankey was rejected here because the detailed prerequisite is more important than band width.", diagram=structural_diagram("transit", [("need", "Need shared cooling", "root", "population-needing-centers"), ("transit", "Transit capacity", "gate", "transit-cooling-capacity"), ("served", "Center served", "notable", "center-served-population")], [("need", "served", "parent", "Need creates demand"), ("transit", "served", "dependency", "Transit caps reach")], layout="lanes")),
            module("cooling-center-flow", "Where does every exposed resident find protection?", "The exposed population conserves across home protection, center service, and no effective cooling.", "cooling-center-sankey-flow", ["exposed-population", "home-protected-population", "center-served-population", "unprotected-population"], "A conserved flow makes the three mutually exclusive outcomes visible.", "A treemap was rejected because the causal access gates matter alongside composition."),
        ]
    )

    modules.extend(
        [
            module("cohort-exposure-tree", "How does the citywide hazard become unequal human exposure?", "Heat, vulnerability, and failed cooling merge into the exposed cohort at greatest risk.", "cohort-exposure-structural-tree", ["heat-index-anomaly", "vulnerable-share", "unprotected-population", "indoor-heat-exposure"], "A multi-parent genealogy clarifies the ancestry of exposure.", "A flow was rejected because heat and vulnerability are not population branches.", diagram=structural_diagram("cohort", [("heat", "Heat signal", "root", "heat-index-anomaly"), ("vulnerable", "Vulnerable share", "root", "vulnerable-share"), ("unprotected", "No effective cooling", "gate", "unprotected-population"), ("exposure", "Indoor exposure", "merge", "indoor-heat-exposure")], [("heat", "exposure", "parent", "Heat initiates exposure"), ("vulnerable", "exposure", "dependency", "Vulnerability amplifies harm"), ("unprotected", "exposure", "dependency", "Failed cooling increases exposure")], layout="tree")),
            module("exposure-illness-process", "How does indoor exposure become severe illness?", "Indoor exposure passes through vulnerability into severe cases and emergency arrivals.", "illness-structural-tree", ["indoor-heat-exposure", "vulnerable-share", "severe-heat-cases", "emergency-arrivals"], "A process tree shows the ordered causal handoff.", "A line was rejected because this is a dependency chain, not sampled time data.", diagram=structural_diagram("illness", [("exposure", "Indoor exposure", "root", "indoor-heat-exposure"), ("vulnerable", "Vulnerability", "gate", "vulnerable-share"), ("severe", "Severe cases", "notable", "severe-heat-cases"), ("arrivals", "Emergency arrivals", "leaf", "emergency-arrivals")], [("exposure", "severe", "parent", "Exposure creates cases"), ("vulnerable", "severe", "dependency", "Vulnerability amplifies cases"), ("severe", "arrivals", "flow", "Cases reach emergency care")], layout="tree")),
            module("emergency-arrivals-series", "How strongly do heat emergencies rise across scenarios?", "Emergency arrivals respond to the complete exposure lineage.", "emergency-arrivals-line-series", ["emergency-arrivals"], "A signal series makes the scenario trajectory visible.", "A static number was rejected because the change across states is the key message."),
            module("surge-bed-bullet", "Does care demand exceed the available surge capacity?", "The care load ratio crosses 100 percent when arrivals exceed surge beds.", "surge-bed-bullet", ["surge-load-ratio"], "A bullet view makes the 100 percent overload threshold explicit.", "A bounded utilization gauge was rejected because the load can exceed 100 percent."),
            module("care-outcomes-flow", "Where do heat emergency arrivals go after triage?", "Emergency arrivals conserve across stabilized and escalated care outcomes.", "care-outcomes-sankey-flow", ["emergency-arrivals", "stabilized-cases", "escalated-cases"], "A conserved flow ties the exact outcomes to one source total.", "Independent bars were rejected because they would hide the one-source partition."),
        ]
    )

    modules.extend(
        [
            module("emergency-budget-flow", "Where does the emergency response budget go?", "The response budget conserves across grid, water, household, and care interventions.", "emergency-budget-sankey-flow", ["response-budget", "grid-budget", "water-budget", "household-budget", "care-budget"], "A conserved flow makes allocation and downstream intervention paths explicit.", "A pie was rejected because the downstream routes and feedback role matter."),
            module("intervention-lineage", "Which interventions inherit the response budget?", "Budget allocations branch into grid, water, household, and care capabilities that alter later scenarios.", "intervention-structural-tree", ["response-budget", "grid-budget", "water-budget", "household-budget", "care-budget"], "A lineage tree emphasizes prerequisite funding and later actuation.", "A second flow was rejected because this module explains ancestry rather than quantity transfer.", diagram=structural_diagram("intervention", [("budget", "Response budget", "root", "response-budget"), ("grid", "Grid intervention", "notable", "grid-budget"), ("water", "Water intervention", "notable", "water-budget"), ("households", "Household intervention", "notable", "household-budget"), ("care", "Care intervention", "notable", "care-budget")], [("budget", "grid", "parent", "Fund grid resilience"), ("budget", "water", "parent", "Fund water resilience"), ("budget", "households", "parent", "Fund household access"), ("budget", "care", "parent", "Fund care surge")], layout="radial")),
            module("deployment-timeline", "How strongly does the intervention envelope expand?", "The response budget signal grows from ordinary summer through adaptation.", "deployment-line-series", ["response-budget"], "A line-like trajectory makes the expanding intervention envelope visible.", "A static ledger was rejected because the ordered scenario progression matters."),
            module("equity-allocation-matrix", "How are household and care protections funded relative to infrastructure?", "The allocation matrix keeps all four response branches exactly inspectable.", "equity-allocation-matrix", ["grid-budget", "water-budget", "household-budget", "care-budget"], "A matrix supports exact peer comparison in one unit.", "A stacked bar was rejected because exact cross-branch lookup is the primary task here."),
            module("policy-learning-feedback", "How does observed harm change the next preparedness state?", "Severe cases inform the response budget, while the adapted scenario raises the citywide adaptation score.", "policy-learning-structural-network", ["severe-heat-cases", "response-budget", "adaptation-score"], "A feedback network distinguishes observed harm from later scenario-supported actuation.", "A cyclic computation was rejected because the canonical state must remain acyclic.", diagram=structural_diagram("policy", [("harm", "Observed severe cases", "root", "severe-heat-cases"), ("budget", "Later response budget", "gate", "response-budget"), ("adaptation", "Adaptation score", "notable", "adaptation-score")], [("harm", "budget", "feedback", "Observed harm escalates the next response"), ("budget", "adaptation", "parent", "Deployed funding improves preparedness")], layout="tree")),
        ]
    )

    district_modules = {
        "city-pulse": ["city-pulse-hub"],
        "atmosphere-signal": ["heat-anomaly-series", "heat-dome-lineage", "heat-exposure-field", "nocturnal-cooling-ledger", "warning-threshold"],
        "built-fabric": ["land-cover-mosaic", "surface-heat-ledger", "shade-lineage", "building-vulnerability-matrix", "indoor-thermal-lag"],
        "power-grid": ["cooling-demand-series", "demand-capacity-bars", "substation-lineage", "grid-reliability-bullet", "outage-cascade-tree"],
        "water-canopy": ["reservoir-allocation-flow", "pump-service-bullet", "canopy-water-tree", "cooling-ecology-map", "cooling-island-ledger"],
        "households-mobility": ["cooling-access-lineage", "household-protection-ledger", "vulnerability-access-matrix", "transit-cooling-network", "cooling-center-flow"],
        "health-care": ["cohort-exposure-tree", "exposure-illness-process", "emergency-arrivals-series", "surge-bed-bullet", "care-outcomes-flow"],
        "governance-adaptation": ["emergency-budget-flow", "intervention-lineage", "deployment-timeline", "equity-allocation-matrix", "policy-learning-feedback"],
    }
    focus_groups = [
        {"id": district_id, "label": label, "moduleIds": module_ids}
        for district_id, label, module_ids in [
            ("pulse-story", "City pulse", district_modules["city-pulse"]),
            ("atmosphere-story", "Atmosphere and signal", district_modules["atmosphere-signal"]),
            ("fabric-story", "Built fabric", district_modules["built-fabric"]),
            ("grid-story", "Power grid", district_modules["power-grid"]),
            ("water-story", "Water and living canopy", district_modules["water-canopy"]),
            ("access-story", "Households and mobility", district_modules["households-mobility"]),
            ("care-story", "Health and care", district_modules["health-care"]),
            ("governance-story", "Governance and adaptation", district_modules["governance-adaptation"]),
            ("cross-district-proof", "Cross-district heat proof", ["heat-anomaly-series", "surface-heat-ledger", "cooling-demand-series", "cooling-ecology-map", "cohort-exposure-tree", "policy-learning-feedback"]),
        ]
    ]
    districts = [
        {"id": "city-pulse", "label": "City Pulse", "summary": "The canonical conditions inherited by every distant branch.", "role": "Root nexus", "localArmature": "radial", "moduleIds": district_modules["city-pulse"]},
        {"id": "atmosphere-signal", "label": "Atmosphere & Signal", "summary": "The initiating ancestry: heat, reach, warning, and overnight retention.", "role": "Initiating lineage", "localArmature": "branch", "moduleIds": district_modules["atmosphere-signal"]},
        {"id": "built-fabric", "label": "Built Fabric", "summary": "How climate, canopy, buildings, and installed cooling become indoor exposure.", "role": "Exposure transformer", "localArmature": "lanes", "moduleIds": district_modules["built-fabric"]},
        {"id": "power-grid", "label": "Power Grid", "summary": "The capacity inheritance from cooling demand to reliable service and outage.", "role": "Capacity gate", "localArmature": "radial", "moduleIds": district_modules["power-grid"]},
        {"id": "water-canopy", "label": "Water & Living Canopy", "summary": "The cooling ecology linking grid-powered pumps, water, canopy, and shade.", "role": "Ecological branch", "localArmature": "orbit", "moduleIds": district_modules["water-canopy"]},
        {"id": "households-mobility", "label": "Households & Mobility", "summary": "How installed protection becomes effective access, transit, and cooling-center reach.", "role": "Access branch", "localArmature": "branch", "moduleIds": district_modules["households-mobility"]},
        {"id": "health-care", "label": "Health & Care", "summary": "How unequal exposure becomes severe cases, surge pressure, and care outcomes.", "role": "Consequence branch", "localArmature": "lanes", "moduleIds": district_modules["health-care"]},
        {"id": "governance-adaptation", "label": "Governance & Adaptation", "summary": "How observed harm becomes funded intervention and a later prepared state.", "role": "Feedback and learning", "localArmature": "radial", "moduleIds": district_modules["governance-adaptation"]},
    ]
    world_links = [
        ("pulse-to-atmosphere", "city-pulse", "atmosphere-signal", "dependency", "Shared conditions initiate the heat signal"),
        ("atmosphere-to-fabric", "atmosphere-signal", "built-fabric", "flow", "Heat enters streets and buildings"),
        ("atmosphere-to-grid", "atmosphere-signal", "power-grid", "dependency", "Heat raises cooling demand"),
        ("fabric-to-households", "built-fabric", "households-mobility", "dependency", "Building conditions shape household protection"),
        ("grid-to-water", "power-grid", "water-canopy", "dependency", "Grid reliability powers water pumping"),
        ("grid-to-households", "power-grid", "households-mobility", "dependency", "Grid reliability enables home cooling"),
        ("water-to-fabric", "water-canopy", "built-fabric", "feedback", "Living canopy moderates later surface heat"),
        ("water-to-health", "water-canopy", "health-care", "dependency", "Cooling ecology lowers exposure"),
        ("households-to-health", "households-mobility", "health-care", "flow", "Failed access becomes health exposure"),
        ("health-to-governance", "health-care", "governance-adaptation", "dependency", "Emergency arrivals escalate response"),
        ("governance-to-grid", "governance-adaptation", "power-grid", "feedback", "Later funding raises grid resilience"),
        ("governance-to-water", "governance-adaptation", "water-canopy", "feedback", "Later funding raises water resilience"),
        ("governance-to-households", "governance-adaptation", "households-mobility", "feedback", "Later funding expands cooling access"),
        ("governance-to-care", "governance-adaptation", "health-care", "feedback", "Later funding expands surge capacity"),
        ("governance-to-pulse", "governance-adaptation", "city-pulse", "feedback", "Learning updates the next city pulse"),
    ]
    route_targets = [
        ("whole-atlas", "Whole heatwave tree", "world", 0, 3200, "pulse-story", None),
        ("city-pulse", "The canonical city pulse", "city-pulse", 1600, 3000, "pulse-story", "Begin at the root nexus"),
        ("atmosphere", "The initiating heat ancestry", "atmosphere-signal", 1700, 3200, "atmosphere-story", "Follow the initiating signal branch"),
        ("built-fabric", "Heat enters the built fabric", "built-fabric", 1700, 3200, "fabric-story", "Follow heat into streets and buildings"),
        ("power-grid", "Cooling demand pressures the grid", "power-grid", 1700, 3200, "grid-story", "Trace the heat-to-demand dependency"),
        ("water-canopy", "Power loss weakens the cooling ecology", "water-canopy", 1700, 3200, "water-story", "Follow grid reliability into water pumping"),
        ("households", "Protection becomes unequal access", "households-mobility", 1700, 3200, "access-story", "Follow reliable service into household access"),
        ("health-care", "Exposure becomes care pressure", "health-care", 1700, 3200, "care-story", "Follow failed protection into health outcomes"),
        ("governance", "Observed harm becomes later intervention", "governance-adaptation", 1700, 3200, "governance-story", "Follow arrivals into response escalation"),
        ("cross-district", "One heat value across distant encodings", "cohort-exposure-tree", 1700, 3000, "cross-district-proof", "Trace the recurring heat identity across the world"),
        ("adapted-world", "The adapted city returns as one whole", "world", 1900, 3800, "cross-district-proof", "Return through the feedback ring"),
    ]
    timeline_targets = [
        ("ordinary-pulse", "Ordinary summer", "pulse-story", ordinary),
        ("heat-signal", "Heat dome signal", "atmosphere-story", heat_dome),
        ("heat-in-fabric", "Heat enters buildings", "fabric-story", heat_dome),
        ("compound-grid", "Compound grid outage", "grid-story", compound),
        ("compound-water", "Cooling ecology weakens", "water-story", compound),
        ("compound-access", "Household access falls", "access-story", compound),
        ("compound-care", "Care pressure rises", "care-story", compound),
        ("adaptation-response", "Adapted intervention", "governance-story", adapted),
        ("adapted-proof", "Cross-district adapted state", "cross-district-proof", adapted),
        ("return-to-start", "Return to ordinary summer", "pulse-story", ordinary),
    ]
    return {
        "compositionId": "heatwave-city-skill-tree",
        "title": "The Heatwave Tree",
        "subtitle": "How one citywide signal branches through infrastructure, access, care, and adaptation",
        "provenance": "Synthetic city model for visual-system validation; no values represent an observed city.",
        "locale": "en-US",
        "initialScenario": "ordinary-summer",
        "armature": "radial-genealogical-world",
        "concepts": concepts,
        "derived": derived,
        "scenarios": scenarios,
        "modules": modules,
        "relationships": [],
        "focusGroups": focus_groups,
        "world": {
            "mode": "navigable-atlas",
            "armature": "radial-skill-tree",
            "rootDistrictId": "city-pulse",
            "districts": districts,
            "links": [
                {"id": link_id, "source": source, "target": target, "kind": kind, "label": label}
                for link_id, source, target, kind, label in world_links
            ],
            "navigation": {
                "initialTarget": "world",
                "route": {
                    "loop": True,
                    "autoplay": False,
                    "stops": [
                        {
                            "id": stop_id,
                            "label": label,
                            "target": target,
                            "travelMs": travel,
                            "holdMs": hold,
                            "focusId": focus,
                            **({"handoff": handoff} if handoff else {}),
                        }
                        for stop_id, label, target, travel, hold, focus, handoff in route_targets
                    ],
                },
            },
        },
        "timeline": {
            "durationMs": 40_000,
            "loop": True,
            "baseScenario": "ordinary-summer",
            "interpolation": "smooth",
            "autoplay": False,
            "phases": [
                {"id": phase_id, "label": label, "focusId": focus, "values": values}
                for phase_id, label, focus, values in timeline_targets
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Heatwave Tree compact SVG brief.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_brief(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote Heatwave Tree brief: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
