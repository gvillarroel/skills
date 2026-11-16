#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Family-specific discovery and animation planning for Mermaid SVGs."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from typing import Iterable
from mermaid_animation.common import Candidate, ancestors, class_tokens, collapsed_text, edge_endpoints, local_name, nearest_candidate, normalized, plan_staged_items_with_following_connections, translate_position
from mermaid_animation.common import Candidate, class_tokens, collapsed_text, edge_endpoints, local_name, nearest_candidate, normalized, plan_staged_items_with_following_connections, squared_distance, translate_position
from mermaid_animation.common import Candidate, class_tokens, collapsed_text, edge_endpoints, local_name, normalized, plan_staged_items_with_following_connections, squared_distance, translate_position
from mermaid_animation.common import Candidate, collapsed_text, class_tokens, edge_endpoints, local_name, nearest_candidate, normalized, parse_viewbox, plan_staged_items_with_following_connections, translate_position
from mermaid_animation.common import Candidate, class_tokens, collapsed_text, edge_endpoints, effect_for, local_name, nearest_candidate, normalized, plan_staged_items_with_following_connections
import base64
import binascii
import json
from mermaid_animation.common import Candidate, build_parent_map, class_tokens, element_bounds, dwell_for_candidate, edge_endpoints, effect_for, nearest_candidate, normalized, parse_keyed_number_entries, parse_viewbox, plan_staged_items_with_following_connections, squared_distance, translate_position
from mermaid_animation.common import Candidate, class_tokens, collapsed_text, effect_for, local_name, normalized
from mermaid_animation.common import Candidate, build_parent_map, class_tokens, edge_endpoints, effect_for, local_name, normalized
from mermaid_animation.common import Candidate, ROLE_PRIORITY, ancestor_has_class_fragment, class_tokens, collapsed_text, effect_for, has_lower_class, line_start, local_name, normalized, parse_number_list, squared_distance, translate_position, edge_endpoints
from mermaid_animation.common import Candidate, class_tokens, effect_for, local_name, normalized
from mermaid_animation.common import Candidate, ROLE_PRIORITY, effect_for, normalized, ordered_reveal_key
import math
from mermaid_animation.common import Candidate, ROLE_PRIORITY, average_position, class_number, class_tokens, numeric_id_suffix, parse_number_list, translate_position
from collections import defaultdict
from mermaid_animation.common import Candidate, class_tokens, collapsed_text, effect_for, has_lower_class, local_name, normalized, slug
from mermaid_animation.common import Candidate, class_tokens, collapsed_text, effect_for, has_lower_class, local_name, normalized
from mermaid_animation.common import Candidate, ancestors, build_parent_map, class_tokens, collapsed_text, effect_for, local_name, normalized
from mermaid_animation.common import Candidate, class_tokens, edge_endpoints, effect_for, normalized, plan_staged_items_with_following_connections, squared_distance, translate_position
from mermaid_animation.common import Candidate, ancestors, class_tokens, collapsed_text, edge_endpoints, effect_for, local_name, normalized, translate_position
from mermaid_animation.common import Candidate, ancestors, build_parent_map, class_tokens, collapsed_text, element_bounds, element_center, effect_for, local_name, normalized
from mermaid_animation.common import Candidate, ancestors, build_parent_map, class_tokens, element_bounds, element_center, edge_endpoints, effect_for, nearest_candidate, normalized, parse_keyed_number_entries, parse_viewbox, plan_staged_items_with_following_connections, squared_distance, state_dwell_for_candidate, translated_point, translate_position
from mermaid_animation.common import Candidate, ancestor_has_class_fragment, class_tokens, collapsed_text, edge_endpoints, effect_for, has_class_fragment, has_lower_class, local_name, normalized, translate_position
from dataclasses import dataclass, field
from mermaid_animation.common import Candidate, ROLE_PRIORITY, effect_for, normalized
from mermaid_animation.common import Candidate, TRANSFORM_EFFECTS, class_tokens, collapsed_text, effect_for, has_lower_class, local_name, normalized, ordered_reveal_key, slug
from mermaid_animation.common import Candidate, ancestors, build_parent_map, class_tokens, collapsed_text, element_center, effect_for, local_name, normalized, numeric_attribute

# --- architecture ---

def architecture__is_architecture_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'architecture'
def architecture__element_has_class(element: ET.Element, token: str) -> bool:
    return token.lower() in {value.lower() for value in class_tokens(element)}
def architecture__has_ancestor_class(element: ET.Element, parent_map: dict[ET.Element, ET.Element], token: str) -> bool:
    return any((architecture__element_has_class(parent, token) for parent in ancestors(element, parent_map)))
def architecture__add_classes(classes: Iterable[str], extra_classes: Iterable[str]) -> list[str]:
    result = list(classes)
    for extra_class in extra_classes:
        if extra_class not in result:
            result.append(extra_class)
    return result
def architecture__architecture_service_key(candidate: Candidate) -> str:
    prefix = 'my-svg-service-'
    if candidate.element_id.startswith(prefix):
        return candidate.element_id.removeprefix(prefix)
    return candidate.element_id
def architecture__architecture_edge_id(element: ET.Element) -> str:
    if local_name(element.tag) == 'path' and architecture__element_has_class(element, 'edge'):
        return element.get('id', '')
    for child in element.iter():
        if local_name(child.tag) == 'path' and architecture__element_has_class(child, 'edge'):
            return child.get('id', '')
    return element.get('id', '')
def architecture__architecture_edge_path(element: ET.Element) -> ET.Element | None:
    if local_name(element.tag) == 'path' and architecture__element_has_class(element, 'edge'):
        return element
    for child in element.iter():
        if local_name(child.tag) == 'path' and architecture__element_has_class(child, 'edge'):
            return child
    return None
def architecture__architecture_edge_endpoints(edge: Candidate) -> tuple[tuple[float, float], tuple[float, float]] | None:
    path = architecture__architecture_edge_path(edge.element)
    if path is None:
        return edge_endpoints(edge)
    probe = Candidate(element=path, role=edge.role, dom_index=edge.dom_index, element_id=path.get('id', ''), classes=class_tokens(path), text=collapsed_text(path))
    return edge_endpoints(probe)
def architecture__discover_architecture_candidates(root: ET.Element, parent_map: dict[ET.Element, ET.Element], dom_order: dict[ET.Element, int]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for element in root.iter():
        tag = local_name(element.tag)
        if tag == 'g' and architecture__element_has_class(element, 'architecture-service'):
            candidates.append(Candidate(element=element, role='node', dom_index=dom_order[element], element_id=element.get('id', ''), classes=architecture__add_classes(class_tokens(element), ['architecture-service']), text=collapsed_text(element)))
            continue
        if tag == 'rect' and architecture__has_ancestor_class(element, parent_map, 'architecture-groups') and (architecture__element_has_class(element, 'node-bkg') or '-group-' in element.get('id', '')):
            candidates.append(Candidate(element=element, role='cluster', dom_index=dom_order[element], element_id=element.get('id', ''), classes=architecture__add_classes(class_tokens(element), ['architecture-group']), text=collapsed_text(element)))
            continue
        if tag == 'g' and architecture__has_ancestor_class(element, parent_map, 'architecture-edges'):
            edge_id = architecture__architecture_edge_id(element)
            if not edge_id:
                continue
            candidates.append(Candidate(element=element, role='edge', dom_index=dom_order[element], element_id=edge_id, classes=architecture__add_classes(class_tokens(element), ['architecture-edge']), text=collapsed_text(element)))
    return candidates
def architecture__edge_services_from_id(edge: Candidate, service_by_key: dict[str, Candidate]) -> tuple[Candidate, Candidate] | None:
    raw_id = edge.element_id
    matches: list[tuple[int, Candidate]] = []
    for key, service in service_by_key.items():
        pattern = re.compile(f'(?:(?<=L_)|(?<=_)){re.escape(key)}(?=_|$)')
        matches.extend(((match.start(), service) for match in pattern.finditer(raw_id)))
    if len(matches) < 2:
        return None
    ordered = sorted(matches, key=lambda item: item[0])
    return (ordered[0][1], ordered[1][1])
def architecture__service_position(candidate: Candidate) -> tuple[float, float] | None:
    position = translate_position(candidate.element)
    if position is None:
        return None
    return (position[0] + 40.0, position[1] + 40.0)
def architecture__edge_services_from_geometry(edge: Candidate, services: list[Candidate], positions: dict[int, tuple[float, float]]) -> tuple[Candidate, Candidate] | None:
    endpoints = architecture__architecture_edge_endpoints(edge)
    if endpoints is None:
        return None
    source = nearest_candidate(endpoints[0], services, positions)
    target = nearest_candidate(endpoints[1], services, positions)
    if source is None or target is None:
        return None
    return (source, target)
def architecture__plan_architecture_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    service_candidates = [candidate for candidate in candidates if candidate.role == 'node' and 'architecture-service' in {token.lower() for token in candidate.classes}]
    edge_candidates = [candidate for candidate in candidates if candidate.role == 'edge' and 'architecture-edge' in {token.lower() for token in candidate.classes}]
    cluster_candidates = [candidate for candidate in candidates if candidate.role == 'cluster' and 'architecture-group' in {token.lower() for token in candidate.classes}]
    positions = {id(candidate): position for candidate in service_candidates if (position := architecture__service_position(candidate)) is not None}
    positioned_services = [candidate for candidate in service_candidates if id(candidate) in positions]
    if not positioned_services or not edge_candidates:
        return []

    def service_sort_key(candidate: Candidate) -> tuple[int, int, int]:
        return (0 if candidate.explicit_order is not None else 1, candidate.explicit_order if candidate.explicit_order is not None else 0, candidate.dom_index)
    ordered_services = sorted(positioned_services, key=service_sort_key)
    service_stage = {id(candidate): index for index, candidate in enumerate(ordered_services)}
    service_by_key = {architecture__architecture_service_key(candidate): candidate for candidate in ordered_services}
    edge_services: dict[int, tuple[Candidate, Candidate]] = {}
    for edge in edge_candidates:
        endpoints = architecture__edge_services_from_id(edge, service_by_key)
        if endpoints is None:
            endpoints = architecture__edge_services_from_geometry(edge, positioned_services, positions)
        if endpoints is None:
            continue
        edge_services[id(edge)] = endpoints
    if not edge_services:
        return []
    stage_items: dict[int, list[Candidate]] = {0: sorted(cluster_candidates, key=lambda item: item.dom_index)}
    for index, service in enumerate(ordered_services):
        stage_items.setdefault(index, []).append(service)
    for edge in sorted(edge_candidates, key=lambda item: item.dom_index):
        source, target = edge_services.get(id(edge), (None, None))
        if source is None or target is None:
            continue
        source_stage = service_stage.get(id(source), len(ordered_services))
        target_stage = service_stage.get(id(target), len(ordered_services))
        stage = max(source_stage, target_stage)
        edge.source_index = source_stage
        edge.target_index = target_stage
        stage_items.setdefault(stage, []).append(edge)
    fallback_stage = len(ordered_services)
    planned_candidate_ids = {id(candidate) for stage in stage_items.values() for candidate in stage}
    for candidate in candidates:
        if id(candidate) in planned_candidate_ids:
            continue
        stage_items.setdefault(fallback_stage, []).append(candidate)
        fallback_stage += 1
    return plan_staged_items_with_following_connections(stage_items, args, effective_animation)

# --- blockdiagram ---

def blockdiagram__is_block_root(root: ET.Element) -> bool:
    role = normalized(root.get('aria-roledescription', ''))
    classes = {token.lower() for token in class_tokens(root)}
    return role == 'block' or 'blockdiagram' in classes
def blockdiagram__add_classes(classes: Iterable[str], extra_classes: Iterable[str]) -> list[str]:
    result = list(classes)
    for extra_class in extra_classes:
        if extra_class not in result:
            result.append(extra_class)
    return result
def blockdiagram__element_has_class(element: ET.Element, token: str) -> bool:
    return token.lower() in {value.lower() for value in class_tokens(element)}
def blockdiagram__discover_block_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for element in root.iter():
        tag = local_name(element.tag)
        element_id = element.get('id', '')
        if tag == 'g' and blockdiagram__element_has_class(element, 'node'):
            candidates.append(Candidate(element=element, role='node', dom_index=dom_order[element], element_id=element_id, classes=blockdiagram__add_classes(class_tokens(element), ['block-diagram-block']), text=collapsed_text(element)))
            continue
        if tag in {'path', 'line', 'polyline'} and blockdiagram__element_has_class(element, 'flowchart-link'):
            candidates.append(Candidate(element=element, role='edge', dom_index=dom_order[element], element_id=element_id, classes=blockdiagram__add_classes(class_tokens(element), ['block-diagram-connection']), text=collapsed_text(element)))
            continue
        if tag == 'g' and blockdiagram__element_has_class(element, 'edgeLabel'):
            candidates.append(Candidate(element=element, role='label', dom_index=dom_order[element], element_id=element_id, classes=blockdiagram__add_classes(class_tokens(element), ['block-diagram-connection-label']), text=collapsed_text(element)))
    return candidates
def blockdiagram__candidate_data_id(candidate: Candidate) -> str:
    data_id = candidate.element.get('data-id', '')
    if data_id:
        return data_id
    for child in candidate.element.iter():
        data_id = child.get('data-id', '')
        if data_id:
            return data_id
    return ''
def blockdiagram__block_key(candidate: Candidate) -> str:
    element_id = candidate.element_id
    if element_id.startswith('my-svg-'):
        element_id = element_id.removeprefix('my-svg-')
    return normalized(element_id)
def blockdiagram__relation_key(candidate: Candidate) -> str:
    return normalized(blockdiagram__candidate_data_id(candidate) or candidate.element_id)
def blockdiagram__edge_blocks_from_id(edge: Candidate, block_by_key: dict[str, Candidate]) -> tuple[Candidate, Candidate] | None:
    raw_ids = [blockdiagram__candidate_data_id(edge), edge.element_id]
    for raw_id in raw_ids:
        if not raw_id:
            continue
        normalized_id = normalized(raw_id)
        if normalized_id.startswith('my-svg-'):
            normalized_id = normalized_id.removeprefix('my-svg-')
        matches: list[tuple[int, Candidate]] = []
        for key, block in block_by_key.items():
            if not key:
                continue
            pattern = re.compile(f'(?:^|[-_])({re.escape(key)})(?=$|[-_])')
            matches.extend(((match.start(1), block) for match in pattern.finditer(normalized_id)))
        if len(matches) >= 2:
            ordered = sorted(matches, key=lambda item: item[0])
            return (ordered[0][1], ordered[1][1])
    return None
def blockdiagram__edge_blocks_from_geometry(edge: Candidate, blocks: list[Candidate], positions: dict[int, tuple[float, float]]) -> tuple[Candidate, Candidate] | None:
    endpoints = edge_endpoints(edge)
    if endpoints is None:
        return None
    source = nearest_candidate(endpoints[0], blocks, positions)
    target = nearest_candidate(endpoints[1], blocks, positions)
    if source is None or target is None:
        return None
    return (source, target)
def blockdiagram__nearest_edge_for_label(label: Candidate, edges: list[Candidate], edge_blocks: dict[int, tuple[Candidate, Candidate]]) -> Candidate | None:
    position = translate_position(label.element)
    if position is None:
        return None
    best: tuple[float, Candidate] | None = None
    for edge in edges:
        if id(edge) not in edge_blocks:
            continue
        endpoints = edge_endpoints(edge)
        if endpoints is None:
            continue
        distance = min(squared_distance(position, endpoints[0]), squared_distance(position, endpoints[1]))
        if best is None or distance < best[0]:
            best = (distance, edge)
    return best[1] if best is not None else None
def blockdiagram__plan_block_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    block_candidates = [candidate for candidate in candidates if candidate.role == 'node' and 'block-diagram-block' in {token.lower() for token in candidate.classes}]
    edge_candidates = [candidate for candidate in candidates if candidate.role == 'edge' and 'block-diagram-connection' in {token.lower() for token in candidate.classes}]
    label_candidates = [candidate for candidate in candidates if candidate.role == 'label' and 'block-diagram-connection-label' in {token.lower() for token in candidate.classes}]
    positions = {id(candidate): position for candidate in block_candidates if (position := translate_position(candidate.element)) is not None}
    positioned_blocks = [candidate for candidate in block_candidates if id(candidate) in positions]
    if not positioned_blocks or not edge_candidates:
        return []

    def block_sort_key(candidate: Candidate) -> tuple[int, int, int]:
        return (0 if candidate.explicit_order is not None else 1, candidate.explicit_order if candidate.explicit_order is not None else 0, candidate.dom_index)
    ordered_blocks = sorted(positioned_blocks, key=block_sort_key)
    block_stage = {id(candidate): index for index, candidate in enumerate(ordered_blocks)}
    block_by_key = {blockdiagram__block_key(candidate): candidate for candidate in ordered_blocks}
    edge_blocks: dict[int, tuple[Candidate, Candidate]] = {}
    for edge in edge_candidates:
        endpoints = blockdiagram__edge_blocks_from_id(edge, block_by_key)
        if endpoints is None:
            endpoints = blockdiagram__edge_blocks_from_geometry(edge, positioned_blocks, positions)
        if endpoints is None:
            continue
        edge_blocks[id(edge)] = endpoints
    if not edge_blocks:
        return []
    sorted_edges = sorted(edge_candidates, key=lambda candidate: candidate.dom_index)
    edge_by_key = {blockdiagram__relation_key(edge): edge for edge in sorted_edges if id(edge) in edge_blocks}
    edge_labels: dict[int, list[Candidate]] = {}
    paired_label_ids: set[int] = set()
    fallback_edge_index = 0
    for label in sorted(label_candidates, key=lambda candidate: candidate.dom_index):
        edge: Candidate | None = None
        label_key = blockdiagram__relation_key(label)
        if label_key:
            edge = edge_by_key.get(label_key)
        if edge is None:
            edge = blockdiagram__nearest_edge_for_label(label, sorted_edges, edge_blocks)
        if edge is None:
            while fallback_edge_index < len(sorted_edges) and id(sorted_edges[fallback_edge_index]) not in edge_blocks:
                fallback_edge_index += 1
            if fallback_edge_index >= len(sorted_edges):
                continue
            edge = sorted_edges[fallback_edge_index]
            fallback_edge_index += 1
        edge_labels.setdefault(id(edge), []).append(label)
        paired_label_ids.add(id(label))
    stage_items: dict[int, list[Candidate]] = {index: [block] for index, block in enumerate(ordered_blocks)}
    for edge in sorted_edges:
        source, target = edge_blocks.get(id(edge), (None, None))
        if source is None or target is None:
            continue
        source_stage = block_stage.get(id(source), len(ordered_blocks))
        target_stage = block_stage.get(id(target), len(ordered_blocks))
        stage = max(source_stage, target_stage)
        edge.source_index = source_stage
        edge.target_index = target_stage
        stage_items.setdefault(stage, []).append(edge)
        for label in edge_labels.get(id(edge), []):
            label.source_index = source_stage
            label.target_index = target_stage
            stage_items[stage].append(label)
    fallback_stage = len(ordered_blocks)
    planned_candidate_ids = {id(candidate) for stage in stage_items.values() for candidate in stage} | paired_label_ids | set(edge_blocks)
    for candidate in candidates:
        if id(candidate) in planned_candidate_ids:
            continue
        stage_items.setdefault(fallback_stage, []).append(candidate)
        fallback_stage += 1
    return plan_staged_items_with_following_connections(stage_items, args, effective_animation)

# --- classdiagram ---

def classdiagram__is_class_root(root: ET.Element) -> bool:
    role = normalized(root.get('aria-roledescription', ''))
    classes = {token.lower() for token in class_tokens(root)}
    return role == 'class' or 'classdiagram' in classes
def classdiagram__add_classes(classes: Iterable[str], extra_classes: Iterable[str]) -> list[str]:
    result = list(classes)
    for extra_class in extra_classes:
        if extra_class not in result:
            result.append(extra_class)
    return result
def classdiagram__element_has_class(element: ET.Element, token: str) -> bool:
    return token.lower() in {value.lower() for value in class_tokens(element)}
def classdiagram__discover_class_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for element in root.iter():
        tag = local_name(element.tag)
        element_id = element.get('id', '')
        if tag == 'g' and classdiagram__element_has_class(element, 'node') and ('classId-' in element_id):
            candidates.append(Candidate(element=element, role='node', dom_index=dom_order[element], element_id=element_id, classes=classdiagram__add_classes(class_tokens(element), ['class-diagram-class']), text=collapsed_text(element)))
            continue
        if tag in {'path', 'line', 'polyline'} and classdiagram__element_has_class(element, 'relation'):
            candidates.append(Candidate(element=element, role='edge', dom_index=dom_order[element], element_id=element_id, classes=classdiagram__add_classes(class_tokens(element), ['class-diagram-relation-line']), text=collapsed_text(element)))
            continue
        if tag == 'g' and classdiagram__element_has_class(element, 'edgeLabel'):
            candidates.append(Candidate(element=element, role='label', dom_index=dom_order[element], element_id=element_id, classes=classdiagram__add_classes(class_tokens(element), ['class-diagram-relation-label']), text=collapsed_text(element)))
            continue
        if tag == 'g' and classdiagram__element_has_class(element, 'edgeTerminals'):
            candidates.append(Candidate(element=element, role='label', dom_index=dom_order[element], element_id=element_id, classes=classdiagram__add_classes(class_tokens(element), ['class-diagram-relation-terminal']), text=collapsed_text(element)))
    return candidates
def classdiagram__candidate_data_id(candidate: Candidate) -> str:
    data_id = candidate.element.get('data-id', '')
    if data_id:
        return data_id
    for child in candidate.element.iter():
        data_id = child.get('data-id', '')
        if data_id:
            return data_id
    return ''
def classdiagram__class_key(candidate: Candidate) -> str:
    match = re.search('classId-(.+)-\\d+$', candidate.element_id)
    if match:
        return match.group(1)
    first_token = candidate.text.split(maxsplit=1)[0] if candidate.text else ''
    return first_token or candidate.element_id
def classdiagram__relation_key(candidate: Candidate) -> str:
    return normalized(classdiagram__candidate_data_id(candidate) or candidate.element_id)
def classdiagram__edge_classes_from_id(edge: Candidate, class_by_key: dict[str, Candidate]) -> tuple[Candidate, Candidate] | None:
    raw_ids = [classdiagram__candidate_data_id(edge), edge.element_id]
    for raw_id in raw_ids:
        if not raw_id:
            continue
        matches: list[tuple[int, Candidate]] = []
        for key, node in class_by_key.items():
            pattern = re.compile(f'(?:(?<=id_)|(?<=_)){re.escape(key)}(?=_|$)')
            matches.extend(((match.start(), node) for match in pattern.finditer(raw_id)))
        if len(matches) >= 2:
            ordered = sorted(matches, key=lambda item: item[0])
            return (ordered[0][1], ordered[1][1])
    return None
def classdiagram__label_position(candidate: Candidate) -> tuple[float, float] | None:
    return translate_position(candidate.element)
def classdiagram__nearest_edge_for_label(label: Candidate, edges: list[Candidate], edge_nodes: dict[int, tuple[Candidate, Candidate]]) -> Candidate | None:
    position = classdiagram__label_position(label)
    if position is None:
        return None
    best: tuple[float, Candidate] | None = None
    for edge in edges:
        if id(edge) not in edge_nodes:
            continue
        endpoints = edge_endpoints(edge)
        if endpoints is None:
            continue
        distance = min(squared_distance(position, endpoints[0]), squared_distance(position, endpoints[1]))
        if best is None or distance < best[0]:
            best = (distance, edge)
    return best[1] if best is not None else None
def classdiagram__plan_class_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    node_candidates = [candidate for candidate in candidates if candidate.role == 'node' and ('class-diagram-class' in {token.lower() for token in candidate.classes} or 'classid-' in candidate.element_id.lower())]
    edge_candidates = [candidate for candidate in candidates if candidate.role == 'edge' and ('class-diagram-relation-line' in {token.lower() for token in candidate.classes} or 'relation' in {token.lower() for token in candidate.classes})]
    label_candidates = [candidate for candidate in candidates if candidate.role == 'label' and ('class-diagram-relation-label' in {token.lower() for token in candidate.classes} or 'class-diagram-relation-terminal' in {token.lower() for token in candidate.classes} or 'edgeLabel' in candidate.classes)]
    if not node_candidates or not edge_candidates:
        return []
    node_positions = {id(candidate): position for candidate in node_candidates if (position := translate_position(candidate.element)) is not None}
    if len(node_positions) >= 2:
        x_values = [position[0] for position in node_positions.values()]
        y_values = [position[1] for position in node_positions.values()]
        use_visual_vertical_order = max(y_values) - min(y_values) > max(x_values) - min(x_values)
    else:
        use_visual_vertical_order = False

    def node_sort_key(candidate: Candidate) -> tuple[float, ...]:
        position = node_positions.get(id(candidate))
        if candidate.explicit_order is None and use_visual_vertical_order and (position is not None):
            return (1, 0, int(round(position[1] * 1000)), int(round(position[0] * 1000)), candidate.dom_index)
        return (0 if candidate.explicit_order is not None else 1, candidate.explicit_order if candidate.explicit_order is not None else 0, candidate.dom_index)
    ordered_nodes = sorted(node_candidates, key=node_sort_key)
    node_stage = {id(candidate): index for index, candidate in enumerate(ordered_nodes)}
    class_by_key = {classdiagram__class_key(candidate): candidate for candidate in ordered_nodes}
    edge_nodes: dict[int, tuple[Candidate, Candidate]] = {}
    for edge in edge_candidates:
        endpoints = classdiagram__edge_classes_from_id(edge, class_by_key)
        if endpoints is None:
            continue
        edge_nodes[id(edge)] = endpoints
    if not edge_nodes:
        return []
    sorted_edges = sorted(edge_candidates, key=lambda candidate: candidate.dom_index)
    edge_by_key = {classdiagram__relation_key(edge): edge for edge in sorted_edges if id(edge) in edge_nodes}
    edge_labels: dict[int, list[Candidate]] = {}
    paired_label_ids: set[int] = set()
    fallback_edge_index = 0
    for label in sorted(label_candidates, key=lambda candidate: candidate.dom_index):
        edge: Candidate | None = None
        label_key = classdiagram__relation_key(label)
        if label_key:
            edge = edge_by_key.get(label_key)
        if edge is None and 'class-diagram-relation-terminal' in {token.lower() for token in label.classes}:
            edge = classdiagram__nearest_edge_for_label(label, sorted_edges, edge_nodes)
        if edge is None:
            while fallback_edge_index < len(sorted_edges) and id(sorted_edges[fallback_edge_index]) not in edge_nodes:
                fallback_edge_index += 1
            if fallback_edge_index >= len(sorted_edges):
                continue
            edge = sorted_edges[fallback_edge_index]
            fallback_edge_index += 1
        edge_labels.setdefault(id(edge), []).append(label)
        paired_label_ids.add(id(label))
    stage_items: dict[int, list[Candidate]] = {index: [node] for index, node in enumerate(ordered_nodes)}
    for edge in sorted_edges:
        source, target = edge_nodes.get(id(edge), (None, None))
        if source is None or target is None:
            continue
        source_stage = node_stage.get(id(source), len(ordered_nodes))
        target_stage = node_stage.get(id(target), len(ordered_nodes))
        stage = max(source_stage, target_stage)
        edge.source_index = source_stage
        edge.target_index = target_stage
        stage_items.setdefault(stage, []).append(edge)
        for label in edge_labels.get(id(edge), []):
            label.source_index = source_stage
            label.target_index = target_stage
            stage_items[stage].append(label)
    fallback_stage = len(ordered_nodes)
    planned_candidate_ids = {id(candidate) for stage in stage_items.values() for candidate in stage} | paired_label_ids | set(edge_nodes)
    for candidate in candidates:
        if id(candidate) in planned_candidate_ids:
            continue
        stage_items.setdefault(fallback_stage, []).append(candidate)
        fallback_stage += 1
    return plan_staged_items_with_following_connections(stage_items, args, effective_animation)

# --- er ---

def er__is_er_root(root: ET.Element) -> bool:
    role = normalized(root.get('aria-roledescription', ''))
    classes = {token.lower() for token in class_tokens(root)}
    return role in {'er', 'entity relationship', 'entity relationship diagram'} or 'erdiagram' in classes
def er__add_classes(classes: Iterable[str], extra_classes: Iterable[str]) -> list[str]:
    result = list(classes)
    for extra_class in extra_classes:
        if extra_class not in result:
            result.append(extra_class)
    return result
def er__element_has_class(element: ET.Element, token: str) -> bool:
    return token.lower() in {value.lower() for value in class_tokens(element)}
def er__discover_er_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for element in root.iter():
        tag = local_name(element.tag)
        if tag == 'g' and element.get('id', '').find('-entity-') >= 0 and er__element_has_class(element, 'node'):
            candidates.append(Candidate(element=element, role='node', dom_index=dom_order[element], element_id=element.get('id', ''), classes=er__add_classes(class_tokens(element), ['er-entity']), text=collapsed_text(element)))
            continue
        if tag in {'path', 'line', 'polyline'} and er__element_has_class(element, 'relationshipLine'):
            candidates.append(Candidate(element=element, role='edge', dom_index=dom_order[element], element_id=element.get('id', ''), classes=er__add_classes(class_tokens(element), ['er-relationship-line']), text=collapsed_text(element)))
            continue
        if tag == 'g' and er__element_has_class(element, 'edgeLabel'):
            candidates.append(Candidate(element=element, role='label', dom_index=dom_order[element], element_id=element.get('id', ''), classes=er__add_classes(class_tokens(element), ['er-relationship-label']), text=collapsed_text(element)))
    return candidates
def er__candidate_data_id(candidate: Candidate) -> str:
    data_id = candidate.element.get('data-id', '')
    if data_id:
        return data_id
    for child in candidate.element.iter():
        data_id = child.get('data-id', '')
        if data_id:
            return data_id
    return ''
def er__relationship_key(candidate: Candidate) -> str:
    return normalized(er__candidate_data_id(candidate) or candidate.element_id)
def er__entity_key(candidate: Candidate) -> str:
    match = re.search('entity-.+?-\\d+$', candidate.element_id)
    if match:
        return match.group(0)
    return candidate.element_id
def er__er_primary_axis(root: ET.Element) -> int:
    viewbox = parse_viewbox(root)
    if viewbox is None:
        return 1
    return 0 if viewbox[2] >= viewbox[3] else 1
def er__edge_entities_from_id(edge: Candidate, node_by_key: dict[str, Candidate]) -> tuple[Candidate, Candidate] | None:
    raw_ids = [er__candidate_data_id(edge), edge.element_id]
    for raw_id in raw_ids:
        if not raw_id:
            continue
        matches: list[tuple[int, Candidate]] = []
        for key, node in node_by_key.items():
            pattern = re.compile(f'{re.escape(key)}(?=$|_)')
            matches.extend(((match.start(), node) for match in pattern.finditer(raw_id)))
        if len(matches) >= 2:
            ordered = sorted(matches, key=lambda item: item[0])
            return (ordered[0][1], ordered[1][1])
    return None
def er__edge_entities_from_geometry(edge: Candidate, nodes: list[Candidate], positions: dict[int, tuple[float, float]]) -> tuple[Candidate, Candidate] | None:
    endpoints = edge_endpoints(edge)
    if endpoints is None:
        return None
    source = nearest_candidate(endpoints[0], nodes, positions)
    target = nearest_candidate(endpoints[1], nodes, positions)
    if source is None or target is None:
        return None
    return (source, target)
def er__plan_er_candidates(candidates: list[Candidate], root: ET.Element, args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    node_candidates = [candidate for candidate in candidates if candidate.role == 'node' and ('er-entity' in {token.lower() for token in candidate.classes} or re.search('entity-.+?-\\d+$', candidate.element_id))]
    edge_candidates = [candidate for candidate in candidates if candidate.role == 'edge' and ('relationshipline' in {token.lower() for token in candidate.classes} or 'er-relationship-line' in {token.lower() for token in candidate.classes})]
    label_candidates = [candidate for candidate in candidates if candidate.role == 'label' and ('edgeLabel' in candidate.classes or 'er-relationship-label' in {token.lower() for token in candidate.classes})]
    positions = {id(candidate): position for candidate in node_candidates if (position := translate_position(candidate.element)) is not None}
    positioned_nodes = [candidate for candidate in node_candidates if id(candidate) in positions]
    if not positioned_nodes or not edge_candidates:
        return []
    axis = er__er_primary_axis(root)
    secondary_axis = 1 - axis
    use_lane_order = args.animation == 'auto'

    def lane_index(candidate: Candidate) -> tuple[float, float]:
        position = positions[id(candidate)]
        lane_coordinate = position[secondary_axis]
        within_lane_coordinate = position[axis]
        return (lane_coordinate, within_lane_coordinate)

    def lane_map() -> dict[int, int]:
        ordered = sorted(positioned_nodes, key=lane_index)
        if len(ordered) < 3:
            return {id(candidate): index for index, candidate in enumerate(ordered)}
        lane_values = [positions[id(candidate)][secondary_axis] for candidate in ordered]
        gaps = [lane_values[index + 1] - lane_values[index] for index in range(len(lane_values) - 1)]
        largest_gap = max(gaps) if gaps else 0.0
        split_threshold = max(60.0, largest_gap / 2)
        lane = 0
        result: dict[int, int] = {}
        previous_value: float | None = None
        for candidate in ordered:
            value = positions[id(candidate)][secondary_axis]
            if previous_value is not None and value - previous_value > split_threshold:
                lane += 1
            result[id(candidate)] = lane
            previous_value = value
        return result
    visual_lanes = lane_map() if use_lane_order else {}

    def node_sort_key(candidate: Candidate) -> tuple[int, int, float, float, int]:
        position = positions[id(candidate)]
        if candidate.explicit_order is None and use_lane_order:
            return (1, 0, float(visual_lanes.get(id(candidate), 0)), position[axis], candidate.dom_index)
        return (0 if candidate.explicit_order is not None else 1, candidate.explicit_order if candidate.explicit_order is not None else 0, position[axis], position[secondary_axis], candidate.dom_index)
    ordered_nodes = sorted(positioned_nodes, key=node_sort_key)
    node_stage = {id(candidate): index for index, candidate in enumerate(ordered_nodes)}
    node_by_key = {er__entity_key(candidate): candidate for candidate in ordered_nodes}
    edge_nodes: dict[int, tuple[Candidate, Candidate]] = {}
    for edge in edge_candidates:
        endpoints = er__edge_entities_from_id(edge, node_by_key)
        if endpoints is None:
            endpoints = er__edge_entities_from_geometry(edge, positioned_nodes, positions)
        if endpoints is None:
            continue
        edge_nodes[id(edge)] = endpoints
    if not edge_nodes:
        return []
    sorted_edges = sorted(edge_candidates, key=lambda candidate: candidate.dom_index)
    edge_by_key = {er__relationship_key(edge): edge for edge in sorted_edges if id(edge) in edge_nodes}
    edge_labels: dict[int, list[Candidate]] = {}
    paired_label_ids: set[int] = set()
    fallback_edge_index = 0
    for label in sorted(label_candidates, key=lambda candidate: candidate.dom_index):
        label_key = er__relationship_key(label)
        edge = edge_by_key.get(label_key) if label_key else None
        if edge is None:
            while fallback_edge_index < len(sorted_edges) and id(sorted_edges[fallback_edge_index]) not in edge_nodes:
                fallback_edge_index += 1
            if fallback_edge_index >= len(sorted_edges):
                continue
            edge = sorted_edges[fallback_edge_index]
            fallback_edge_index += 1
        edge_labels.setdefault(id(edge), []).append(label)
        paired_label_ids.add(id(label))
    stage_items: dict[int, list[Candidate]] = {index: [node] for index, node in enumerate(ordered_nodes)}
    for edge in sorted_edges:
        source, target = edge_nodes.get(id(edge), (None, None))
        if source is None or target is None:
            continue
        source_stage = node_stage.get(id(source), len(ordered_nodes))
        target_stage = node_stage.get(id(target), len(ordered_nodes))
        stage = max(source_stage, target_stage)
        edge.source_index = source_stage
        edge.target_index = target_stage
        stage_items.setdefault(stage, []).append(edge)
        for label in edge_labels.get(id(edge), []):
            label.source_index = source_stage
            label.target_index = target_stage
            stage_items[stage].append(label)
    fallback_stage = len(ordered_nodes)
    for candidate in candidates:
        if id(candidate) in node_stage or id(candidate) in edge_nodes or id(candidate) in paired_label_ids:
            continue
        if candidate.role == 'label' and id(candidate) in paired_label_ids:
            continue
        stage_items.setdefault(fallback_stage, []).append(candidate)
        fallback_stage += 1
    return plan_staged_items_with_following_connections(stage_items, args, effective_animation)

# --- eventmodeling ---

def eventmodeling__is_event_modeling_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'eventmodeling'
def eventmodeling__numeric_attribute(element: ET.Element, name: str) -> float | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
def eventmodeling__first_rect_bounds(element: ET.Element) -> tuple[float, float, float, float] | None:
    for child in element.iter():
        if local_name(child.tag) != 'rect':
            continue
        x = eventmodeling__numeric_attribute(child, 'x')
        y = eventmodeling__numeric_attribute(child, 'y')
        width = eventmodeling__numeric_attribute(child, 'width')
        height = eventmodeling__numeric_attribute(child, 'height')
        if x is not None and y is not None and (width is not None) and (height is not None):
            return (x, y, width, height)
    return None
def eventmodeling__center_of_bounds(bounds: tuple[float, float, float, float]) -> tuple[float, float]:
    x, y, width, height = bounds
    return (x + width / 2, y + height / 2)
def eventmodeling__contains_y(bounds: tuple[float, float, float, float], y: float) -> bool:
    _, top, _, height = bounds
    return top <= y <= top + height
def eventmodeling__add_classes(classes: list[str], extra_classes: Iterable[str]) -> list[str]:
    result = [*classes]
    for extra_class in extra_classes:
        if extra_class not in result:
            result.append(extra_class)
    return result
def eventmodeling__discover_event_modeling_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    event_lane_bounds: tuple[float, float, float, float] | None = None
    for element in root.iter():
        lower_tokens = {token.lower() for token in class_tokens(element)}
        if 'em-swimlane' not in lower_tokens:
            continue
        if normalized(collapsed_text(element)) == 'events':
            event_lane_bounds = eventmodeling__first_rect_bounds(element)
            break
    candidates: list[Candidate] = []
    for element in root.iter():
        lower_tokens = {token.lower() for token in class_tokens(element)}
        classes = class_tokens(element)
        extra_classes: list[str] = []
        role: str | None = None
        if 'em-swimlane' in lower_tokens:
            role = 'row'
            extra_classes.append('eventmodeling-swimlane')
        elif 'em-box' in lower_tokens:
            role = 'node'
            extra_classes.append('eventmodeling-box')
            bounds = eventmodeling__first_rect_bounds(element)
            if bounds is not None and event_lane_bounds is not None:
                _, center_y = eventmodeling__center_of_bounds(bounds)
                if eventmodeling__contains_y(event_lane_bounds, center_y):
                    extra_classes.append('eventmodeling-event')
        elif 'em-relation' in lower_tokens:
            role = 'edge'
            extra_classes.append('eventmodeling-relation')
        if role is None:
            continue
        candidates.append(Candidate(element=element, role=role, dom_index=dom_order[element], element_id=element.get('id', ''), classes=eventmodeling__add_classes(classes, extra_classes), text=collapsed_text(element)))
    return candidates
def eventmodeling__candidate_position(candidate: Candidate) -> tuple[float, float] | None:
    if candidate.role == 'edge':
        endpoints = edge_endpoints(candidate)
        if endpoints is not None:
            return endpoints[0]
    bounds = eventmodeling__first_rect_bounds(candidate.element)
    if bounds is not None:
        return eventmodeling__center_of_bounds(bounds)
    return None
def eventmodeling__dynamic_key(candidate: Candidate) -> tuple[int, float, int, float, int]:
    position = eventmodeling__candidate_position(candidate)
    if position is None:
        return (1, 0.0, 0 if candidate.role == 'edge' else 1, 0.0, candidate.dom_index)
    x, y = position
    return (0, x, 1 if candidate.role == 'edge' else 0, y, candidate.dom_index)
def eventmodeling__candidate_has_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def eventmodeling__event_index_for_position(position_x: float, event_positions: list[float]) -> int | None:
    if not event_positions:
        return None
    for index, event_x in enumerate(event_positions):
        if position_x <= event_x:
            return index
    return len(event_positions) - 1
def eventmodeling__edge_event_index(candidate: Candidate, event_positions: list[float]) -> int | None:
    endpoints = edge_endpoints(candidate)
    if endpoints is None:
        position = eventmodeling__candidate_position(candidate)
        if position is None:
            return None
        return eventmodeling__event_index_for_position(position[0], event_positions)
    start, end = endpoints
    left = min(start[0], end[0])
    right = max(start[0], end[0])
    for index, event_x in enumerate(event_positions):
        if left <= event_x <= right:
            return index
    return eventmodeling__event_index_for_position((left + right) / 2, event_positions)
def eventmodeling__event_order_key(candidate: Candidate, event_positions: list[float]) -> tuple[int, int, float, int, float, int]:
    position = eventmodeling__candidate_position(candidate)
    if candidate.role == 'edge':
        event_index = eventmodeling__edge_event_index(candidate, event_positions)
    elif position is not None:
        event_index = eventmodeling__event_index_for_position(position[0], event_positions)
    else:
        event_index = None
    base_key = eventmodeling__dynamic_key(candidate)
    return (1 if event_index is None else 0, event_index if event_index is not None else 0, base_key[1], base_key[2], base_key[3], base_key[4])
def eventmodeling__plan_event_modeling_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    row_candidates = sorted([candidate for candidate in candidates if candidate.role == 'row'], key=lambda candidate: (eventmodeling__candidate_position(candidate) or (0.0, 0.0), candidate.dom_index))
    dynamic_candidates = [candidate for candidate in candidates if candidate.role != 'row']
    event_candidates = sorted([candidate for candidate in dynamic_candidates if eventmodeling__candidate_has_class(candidate, 'eventmodeling-event')], key=eventmodeling__dynamic_key)
    event_positions = [position[0] for candidate in event_candidates if (position := eventmodeling__candidate_position(candidate)) is not None]
    node_candidates = sorted([candidate for candidate in dynamic_candidates if candidate.role == 'node'], key=lambda candidate: eventmodeling__event_order_key(candidate, event_positions))
    edge_candidates = sorted([candidate for candidate in dynamic_candidates if candidate.role == 'edge'], key=lambda candidate: eventmodeling__event_order_key(candidate, event_positions))
    if not row_candidates and (not dynamic_candidates):
        return []
    for candidate in row_candidates:
        candidate.effect = 'none'
        candidate.delay_ms = 0.0
        candidate.duration_ms = 0.0
        candidate.stage = 0
    if not node_candidates or not edge_candidates:
        duration = float(args.duration_ms)
        minimum_stagger = duration + float(args.stagger_ms)
        if args.total_ms is not None and len(dynamic_candidates) > 1:
            available = float(args.total_ms) - float(args.initial_delay_ms) - duration
            stagger = max(minimum_stagger, available / (len(dynamic_candidates) - 1))
        else:
            stagger = minimum_stagger
        dynamic_candidates = sorted(dynamic_candidates, key=lambda candidate: eventmodeling__event_order_key(candidate, event_positions))
        for index, candidate in enumerate(dynamic_candidates):
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = float(args.initial_delay_ms) + index * stagger
            candidate.duration_ms = duration
            candidate.stage = index + 1
            position = eventmodeling__candidate_position(candidate)
            if eventmodeling__candidate_has_class(candidate, 'eventmodeling-event') and position is not None:
                candidate.branch_index = eventmodeling__event_index_for_position(position[0], event_positions)
            elif candidate.role == 'edge':
                candidate.branch_index = eventmodeling__edge_event_index(candidate, event_positions)
        return [*row_candidates, *dynamic_candidates]
    node_positions = {id(candidate): position for candidate in node_candidates if (position := eventmodeling__candidate_position(candidate)) is not None}
    positioned_nodes = [candidate for candidate in node_candidates if id(candidate) in node_positions]
    if not positioned_nodes:
        return []
    node_stage = {id(candidate): index + 1 for index, candidate in enumerate(node_candidates)}
    edge_nodes: dict[int, tuple[Candidate, Candidate]] = {}
    for edge in edge_candidates:
        endpoints = edge_endpoints(edge)
        if endpoints is None:
            continue
        source = nearest_candidate(endpoints[0], positioned_nodes, node_positions)
        target = nearest_candidate(endpoints[1], positioned_nodes, node_positions)
        if source is None or target is None:
            continue
        edge_nodes[id(edge)] = (source, target)
    if not edge_nodes:
        return [*row_candidates, *node_candidates]
    stage_items: dict[int, list[Candidate]] = {node_stage[id(candidate)]: [candidate] for candidate in node_candidates}
    for edge in edge_candidates:
        source, target = edge_nodes.get(id(edge), (None, None))
        if source is None or target is None:
            continue
        source_stage = node_stage.get(id(source), len(node_candidates))
        target_stage = node_stage.get(id(target), len(node_candidates))
        stage = max(source_stage, target_stage)
        edge.source_index = source_stage
        edge.target_index = target_stage
        stage_items.setdefault(stage, []).append(edge)
    fallback_stage = len(node_candidates) + 1
    planned_ids = {id(candidate) for stage in stage_items.values() for candidate in stage}
    for candidate in dynamic_candidates:
        if id(candidate) in planned_ids:
            continue
        stage_items.setdefault(fallback_stage, []).append(candidate)
        fallback_stage += 1
    planned_dynamic = plan_staged_items_with_following_connections(stage_items, args, effective_animation)
    for candidate in planned_dynamic:
        position = eventmodeling__candidate_position(candidate)
        if eventmodeling__candidate_has_class(candidate, 'eventmodeling-event') and position is not None:
            candidate.branch_index = eventmodeling__event_index_for_position(position[0], event_positions)
        elif candidate.role == 'edge':
            candidate.branch_index = eventmodeling__edge_event_index(candidate, event_positions)
    return [*row_candidates, *planned_dynamic]

# --- flowchart ---

def flowchart__is_flowchart_root(root: ET.Element) -> bool:
    role = normalized(root.get('aria-roledescription', ''))
    return role.startswith('flowchart') or 'flowchart' in {token.lower() for token in class_tokens(root)}
def flowchart__flowchart_primary_axis(root: ET.Element) -> int:
    viewbox = parse_viewbox(root)
    if viewbox is None:
        return 0
    return 0 if viewbox[2] >= viewbox[3] else 1
def flowchart__candidate_data_id(candidate: Candidate) -> str:
    data_id = candidate.element.get('data-id', '')
    if data_id:
        return data_id
    for child in candidate.element.iter():
        data_id = child.get('data-id', '')
        if data_id:
            return data_id
    return ''
def flowchart__flowchart_alias_key(value: str) -> str:
    normalized_value = normalized(value)
    for prefix in ('my-svg-', 'flowchart-'):
        if normalized_value.startswith(prefix):
            normalized_value = normalized_value.removeprefix(prefix)
    normalized_value = re.sub('-\\d+$', '', normalized_value)
    return re.sub('[^a-z0-9]+', '_', normalized_value).strip('_')
def flowchart__flowchart_node_aliases(candidate: Candidate) -> set[str]:
    aliases: set[str] = set()
    for value in (flowchart__candidate_data_id(candidate), candidate.element_id, candidate.text):
        key = flowchart__flowchart_alias_key(value)
        if key:
            aliases.add(key)
    return aliases
def flowchart__edge_tokens(edge: Candidate) -> set[str]:
    tokens = {token for token in [flowchart__candidate_data_id(edge), edge.element_id] if token}
    if edge.element_id.startswith('my-svg-'):
        tokens.add(edge.element_id.removeprefix('my-svg-'))
    return tokens
def flowchart__flowchart_edge_endpoints(edge: Candidate) -> tuple[tuple[float, float], tuple[float, float]] | None:
    raw_points = edge.element.get('data-points', '')
    if raw_points:
        try:
            decoded = base64.b64decode(raw_points).decode('utf-8')
            loaded = json.loads(decoded)
            points = [(float(point['x']), float(point['y'])) for point in loaded if isinstance(point, dict) and 'x' in point and ('y' in point)]
            if len(points) >= 2:
                return (points[0], points[-1])
        except (ValueError, TypeError, KeyError, json.JSONDecodeError, binascii.Error):
            pass
    return edge_endpoints(edge)
def flowchart__infer_flowchart_edge_nodes(edge: Candidate, node_by_alias: dict[str, Candidate], endpoints: tuple[tuple[float, float], tuple[float, float]] | None, positions: dict[int, tuple[float, float]]) -> tuple[Candidate, Candidate] | None:
    edge_id = flowchart__flowchart_alias_key(flowchart__candidate_data_id(edge) or edge.element_id)
    parts = edge_id.split('_')
    if len(parts) < 4 or parts[0] != 'l':
        return None
    body = parts[1:-1]
    matches: list[tuple[Candidate, Candidate]] = []
    for split_index in range(1, len(body)):
        source = node_by_alias.get('_'.join(body[:split_index]))
        target = node_by_alias.get('_'.join(body[split_index:]))
        if source is not None and target is not None:
            matches.append((source, target))
    if not matches:
        return None
    if len(matches) == 1 or endpoints is None:
        return matches[0]
    return min(matches, key=lambda match: squared_distance(endpoints[0], positions[id(match[0])]) + squared_distance(endpoints[1], positions[id(match[1])]))
def flowchart__plan_flowchart_candidates(candidates: list[Candidate], root: ET.Element, args: argparse.Namespace) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    axis = flowchart__flowchart_primary_axis(root)
    secondary_axis = 1 - axis
    duration = float(args.duration_ms)
    tolerance = 1.0
    node_candidates = [candidate for candidate in candidates if candidate.role == 'node']
    edge_candidates = [candidate for candidate in candidates if candidate.role == 'edge']
    label_candidates = [candidate for candidate in candidates if candidate.role == 'label' and 'edgeLabel' in candidate.classes]
    positions = {id(candidate): position for candidate in [*node_candidates, *label_candidates] if (position := translate_position(candidate.element)) is not None}
    positioned_nodes = [candidate for candidate in node_candidates if id(candidate) in positions]
    if not positioned_nodes or not edge_candidates:
        return []
    edge_nodes: dict[int, tuple[Candidate | None, Candidate | None]] = {}
    edge_keys: dict[int, tuple[float, float, float, int]] = {}
    node_order = {id(candidate): index for index, candidate in enumerate(sorted(positioned_nodes, key=lambda candidate: (positions[id(candidate)][axis], positions[id(candidate)][secondary_axis], candidate.dom_index)))}
    node_by_alias: dict[str, Candidate] = {}
    for node in positioned_nodes:
        for alias in flowchart__flowchart_node_aliases(node):
            node_by_alias.setdefault(alias, node)
    for edge in edge_candidates:
        endpoints = flowchart__flowchart_edge_endpoints(edge)
        if endpoints is None:
            continue
        inferred_nodes = flowchart__infer_flowchart_edge_nodes(edge, node_by_alias, endpoints, positions)
        if inferred_nodes is None:
            source = nearest_candidate(endpoints[0], positioned_nodes, positions)
            target = nearest_candidate(endpoints[1], positioned_nodes, positions)
        else:
            source, target = inferred_nodes
        if source is None or target is None:
            continue
        source_position = positions[id(source)]
        target_position = positions[id(target)]
        source_primary = source_position[axis]
        target_primary = target_position[axis]
        target_secondary = target_position[secondary_axis]
        source_secondary = source_position[secondary_axis]
        if target_primary >= source_primary - tolerance:
            key = (target_primary, target_secondary, 0.0, edge.dom_index)
        else:
            key = (source_primary, source_secondary, 2.0, edge.dom_index)
        edge_nodes[id(edge)] = (source, target)
        edge_keys[id(edge)] = key
        edge.source_index = node_order.get(id(source))
        edge.target_index = node_order.get(id(target))
    if not edge_keys:
        return []
    sorted_edges = sorted(edge_candidates, key=lambda candidate: candidate.dom_index)
    edge_by_token: dict[str, Candidate] = {}
    for edge in sorted_edges:
        if id(edge) not in edge_keys:
            continue
        for token in flowchart__edge_tokens(edge):
            edge_by_token[token] = edge
    edge_labels: dict[int, list[Candidate]] = {}
    paired_labels: set[int] = set()
    fallback_index = 0
    for label in sorted(label_candidates, key=lambda candidate: candidate.dom_index):
        label_data_id = flowchart__candidate_data_id(label)
        edge = edge_by_token.get(label_data_id) if label_data_id else None
        if edge is None:
            while fallback_index < len(sorted_edges) and id(sorted_edges[fallback_index]) not in edge_keys:
                fallback_index += 1
            if fallback_index >= len(sorted_edges):
                continue
            edge = sorted_edges[fallback_index]
            fallback_index += 1
        edge_labels.setdefault(id(edge), []).append(label)
        paired_labels.add(id(label))
    cluster_candidates = [candidate for candidate in candidates if candidate.role == 'cluster']
    if cluster_candidates:
        parent_map = build_parent_map(root)
        cluster_positions = {id(candidate): (bounds[0], bounds[1]) for candidate in cluster_candidates if (bounds := element_bounds(candidate.element, parent_map)) is not None}
        visual_items = [candidate for candidate in [*cluster_candidates, *positioned_nodes] if id(candidate) in cluster_positions or id(candidate) in positions]

        def visual_position(candidate: Candidate) -> tuple[float, float]:
            if candidate.role == 'cluster':
                return cluster_positions[id(candidate)]
            return positions[id(candidate)]
        ordered_visual_items = sorted(visual_items, key=lambda candidate: (visual_position(candidate)[axis], visual_position(candidate)[secondary_axis], 0 if candidate.role == 'cluster' else 1, candidate.dom_index))
        stage_by_id = {id(candidate): index for index, candidate in enumerate(ordered_visual_items)}
        stage_items: dict[int, list[Candidate]] = {index: [candidate] for index, candidate in enumerate(ordered_visual_items)}
        for edge in sorted_edges:
            source, target = edge_nodes.get(id(edge), (None, None))
            if source is None or target is None:
                continue
            stage = max(stage_by_id.get(id(source), 0), stage_by_id.get(id(target), 0))
            stage_items.setdefault(stage, []).append(edge)
            for label in edge_labels.get(id(edge), []):
                stage_items[stage].append(label)
        fallback_stage = len(stage_items)
        planned_ids = {id(candidate) for stage in stage_items.values() for candidate in stage} | paired_labels
        for candidate in candidates:
            if id(candidate) in planned_ids:
                continue
            stage_items.setdefault(fallback_stage, []).append(candidate)
            fallback_stage += 1
        return plan_staged_items_with_following_connections(stage_items, args, 'flowchart-flow')
    node_sort_key = {id(candidate): (positions[id(candidate)][axis], positions[id(candidate)][secondary_axis], candidate.dom_index) for candidate in positioned_nodes}
    incoming_node_ids = {id(target) for source, target in edge_nodes.values() if source is not None and target is not None and (source is not target)}
    seed_nodes = [candidate for candidate in positioned_nodes if id(candidate) not in incoming_node_ids] or [min(positioned_nodes, key=lambda candidate: node_sort_key[id(candidate)])]
    ordered_reveal_items: list[Candidate] = []
    reveal_ids: set[int] = set()
    visible_node_ids: set[int] = set()
    revealed_edge_ids: set[int] = set()

    def add_reveal(candidate: Candidate) -> None:
        if id(candidate) in reveal_ids:
            return
        ordered_reveal_items.append(candidate)
        reveal_ids.add(id(candidate))
        if candidate.role == 'node':
            visible_node_ids.add(id(candidate))
    for node in sorted(seed_nodes, key=lambda candidate: node_sort_key[id(candidate)]):
        add_reveal(node)

    def dynamic_edge_key(candidate: Candidate) -> tuple[int, float, float, float, int]:
        _source, target = edge_nodes.get(id(candidate), (None, None))
        target_is_visible = target is None or id(target) in visible_node_ids
        return (1 if target_is_visible else 0, *edge_keys[id(candidate)])
    while len(revealed_edge_ids) < len(edge_keys):
        eligible_edges = [edge for edge in edge_candidates if id(edge) in edge_keys and id(edge) not in revealed_edge_ids and (edge_nodes[id(edge)][0] is not None) and (id(edge_nodes[id(edge)][0]) in visible_node_ids)]
        if eligible_edges:
            for edge in sorted(eligible_edges, key=dynamic_edge_key):
                _source, target = edge_nodes.get(id(edge), (None, None))
                if target is not None and id(target) not in visible_node_ids:
                    add_reveal(target)
                add_reveal(edge)
                revealed_edge_ids.add(id(edge))
            continue
        unseen_nodes = [node for node in positioned_nodes if id(node) not in visible_node_ids]
        if unseen_nodes:
            add_reveal(min(unseen_nodes, key=lambda candidate: node_sort_key[id(candidate)]))
            continue
        for edge in sorted([edge for edge in edge_candidates if id(edge) in edge_keys and id(edge) not in revealed_edge_ids], key=lambda candidate: edge_keys[id(candidate)]):
            add_reveal(edge)
            revealed_edge_ids.add(id(edge))
    for candidate in candidates:
        if candidate.role == 'label' and id(candidate) in paired_labels:
            continue
        if id(candidate) in reveal_ids:
            continue
        add_reveal(candidate)
    flowchart_dwell_overrides = parse_keyed_number_entries(args.flowchart_dwell, '--flowchart-dwell')

    def flowchart_dwell(candidate: Candidate) -> float:
        if candidate.role != 'node':
            return 0.0
        return dwell_for_candidate(candidate, float(args.flowchart_dwell_ms), flowchart_dwell_overrides)
    step_gap = duration + float(args.stagger_ms)
    if args.total_ms is not None and len(ordered_reveal_items) > 1:
        dwell_before_last = sum((flowchart_dwell(candidate) for candidate in ordered_reveal_items[:-1]))
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration - dwell_before_last
        step_gap = max(step_gap, available / (len(ordered_reveal_items) - 1))
    planned: list[Candidate] = []
    cumulative_flowchart_dwell = 0.0
    for index, candidate in enumerate(ordered_reveal_items):
        candidate.effect = effect_for('flowchart-flow', candidate.role)
        candidate.delay_ms = float(args.initial_delay_ms) + index * step_gap + cumulative_flowchart_dwell
        candidate.duration_ms = duration
        candidate.stage = index
        planned.append(candidate)
        if candidate.role == 'edge':
            source, target = edge_nodes.get(id(candidate), (None, None))
            if source is not None:
                candidate.source_index = node_order.get(id(source))
            if target is not None:
                candidate.target_index = node_order.get(id(target))
            for label in edge_labels.get(id(candidate), []):
                label.effect = effect_for('flowchart-flow', label.role)
                label.delay_ms = candidate.delay_ms
                label.duration_ms = duration
                label.stage = index
                label.source_index = candidate.source_index
                label.target_index = candidate.target_index
                planned.append(label)
        cumulative_flowchart_dwell += flowchart_dwell(candidate)
    return planned

# --- gantt ---

def gantt__is_gantt_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'gantt'
def gantt__discover_gantt_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    candidates: list[Candidate] = []

    def add_candidate(element: ET.Element, role: str, extra_classes: Iterable[str]) -> None:
        classes = class_tokens(element)
        for extra_class in extra_classes:
            if extra_class not in classes:
                classes.append(extra_class)
        candidates.append(Candidate(element=element, role=role, dom_index=dom_order[element], element_id=element.get('id', ''), classes=classes, text=collapsed_text(element)))
    for element in root.iter():
        tag = local_name(element.tag)
        lower_tokens = {token.lower() for token in class_tokens(element)}
        if tag == 'rect' and 'section' in lower_tokens:
            add_candidate(element, 'row', ['gantt-row'])
            continue
        if tag == 'text' and any((token.startswith('sectiontitle') for token in lower_tokens)):
            add_candidate(element, 'label', ['gantt-row-title'])
            continue
        if tag == 'rect' and 'task' in lower_tokens:
            add_candidate(element, 'node', ['gantt-task'])
            continue
        if tag == 'text' and any((token.startswith('tasktext') for token in lower_tokens)):
            add_candidate(element, 'label', ['gantt-task-label'])
    return candidates
def gantt__numeric_attribute(element: ET.Element, name: str) -> float | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
def gantt__candidate_has_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def gantt__candidate_position(candidate: Candidate) -> tuple[float, float] | None:
    x = gantt__numeric_attribute(candidate.element, 'x')
    y = gantt__numeric_attribute(candidate.element, 'y')
    if x is not None and y is not None:
        return (x, y)
    return None
def gantt__row_key(candidate: Candidate) -> tuple[int, float, int, float, int]:
    position = gantt__candidate_position(candidate)
    if position is None:
        return (1, 0.0, 0 if candidate.role == 'row' else 1, 0.0, candidate.dom_index)
    return (0, position[1], 0 if candidate.role == 'row' else 1, position[0], candidate.dom_index)
def gantt__task_key(candidates: list[Candidate]) -> tuple[int, float, float, int]:
    task_candidates = [candidate for candidate in candidates if gantt__candidate_has_class(candidate, 'gantt-task')]
    positioned_candidates = task_candidates or candidates
    positions = [position for candidate in positioned_candidates if (position := gantt__candidate_position(candidate)) is not None]
    if not positions:
        return (1, 0.0, 0.0, min((candidate.dom_index for candidate in candidates)))
    x = min((position[0] for position in positions))
    y = min((position[1] for position in positions))
    return (0, x, y, min((candidate.dom_index for candidate in candidates)))
def gantt__task_id_for_label(candidate: Candidate) -> str:
    if candidate.element_id.endswith('-text'):
        return candidate.element_id.removesuffix('-text')
    return ''
def gantt__plan_gantt_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    row_candidates = sorted([candidate for candidate in candidates if candidate.role == 'row' or gantt__candidate_has_class(candidate, 'gantt-row-title')], key=gantt__row_key)
    task_bars = sorted([candidate for candidate in candidates if gantt__candidate_has_class(candidate, 'gantt-task')], key=lambda candidate: gantt__task_key([candidate]))
    task_labels = sorted([candidate for candidate in candidates if gantt__candidate_has_class(candidate, 'gantt-task-label')], key=lambda candidate: gantt__task_key([candidate]))
    labels_by_task_id: dict[str, list[Candidate]] = {}
    unpaired_labels: list[Candidate] = []
    for label in task_labels:
        task_id = gantt__task_id_for_label(label)
        if task_id:
            labels_by_task_id.setdefault(task_id, []).append(label)
        else:
            unpaired_labels.append(label)
    task_steps: list[list[Candidate]] = []
    for bar in task_bars:
        step = [bar, *labels_by_task_id.pop(bar.element_id, [])]
        task_steps.append(step)
    for labels in labels_by_task_id.values():
        unpaired_labels.extend(labels)
    for label in unpaired_labels:
        task_steps.append([label])
    task_steps.sort(key=gantt__task_key)
    if args.animation == 'auto':
        row_bands = sorted([candidate for candidate in row_candidates if candidate.role == 'row' and gantt__candidate_position(candidate) is not None], key=gantt__row_key)
        section_titles = [candidate for candidate in row_candidates if gantt__candidate_has_class(candidate, 'gantt-row-title')]
        visual_steps: list[list[Candidate]] = []
        used_ids: set[int] = set()
        for row in row_bands:
            row_position = gantt__candidate_position(row)
            if row_position is None:
                continue
            row_y = row_position[1]
            step: list[Candidate] = [row]
            used_ids.add(id(row))
            for title in section_titles:
                if id(title) in used_ids:
                    continue
                title_position = gantt__candidate_position(title)
                if title_position is not None and abs(title_position[1] - row_y) <= 30:
                    step.append(title)
                    used_ids.add(id(title))
            matching_task_steps: list[list[Candidate]] = []
            for task_step in task_steps:
                if any((id(candidate) in used_ids for candidate in task_step)):
                    continue
                key = gantt__task_key(task_step)
                if key[0] == 0 and abs(key[2] - row_y) <= 12:
                    matching_task_steps.append(task_step)
            for task_step in sorted(matching_task_steps, key=gantt__task_key):
                step.extend(task_step)
                used_ids.update((id(candidate) for candidate in task_step))
            visual_steps.append(step)
        for title in section_titles:
            if id(title) not in used_ids:
                visual_steps.insert(0, [title])
                used_ids.add(id(title))
        for task_step in task_steps:
            if not any((id(candidate) in used_ids for candidate in task_step)):
                visual_steps.append(task_step)
                used_ids.update((id(candidate) for candidate in task_step))
        duration = float(args.duration_ms)
        if args.total_ms is not None and len(visual_steps) > 1:
            available = float(args.total_ms) - float(args.initial_delay_ms) - duration
            step_gap = max(duration + float(args.stagger_ms), available / (len(visual_steps) - 1))
        else:
            step_gap = duration + float(args.stagger_ms)
        planned: list[Candidate] = []
        for index, step in enumerate(visual_steps):
            delay = float(args.initial_delay_ms) + index * step_gap
            for candidate in step:
                candidate.effect = effect_for(effective_animation, candidate.role)
                candidate.delay_ms = delay
                candidate.duration_ms = duration
                candidate.stage = index
                planned.append(candidate)
        return planned
    duration = float(args.duration_ms)
    initial_delay = float(args.initial_delay_ms)
    task_start_delay = initial_delay + (duration if row_candidates else 0.0)
    if args.total_ms is not None and len(task_steps) > 1:
        available = float(args.total_ms) - task_start_delay - duration
        task_stagger = max(0.0, available / (len(task_steps) - 1))
    else:
        task_stagger = float(args.stagger_ms)
    for candidate in row_candidates:
        candidate.effect = effect_for(effective_animation, candidate.role)
        candidate.delay_ms = initial_delay
        candidate.duration_ms = duration
        candidate.stage = 0
    planned: list[Candidate] = [*row_candidates]
    task_stage_offset = 1 if row_candidates else 0
    for index, step in enumerate(task_steps):
        delay = task_start_delay + index * task_stagger
        for candidate in step:
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = delay
            candidate.duration_ms = duration
            candidate.stage = task_stage_offset + index
            planned.append(candidate)
    return planned

# --- gitgraph ---

def gitgraph__is_gitgraph_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'gitgraph'
def gitgraph__candidate_has_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def gitgraph__numeric_attribute(element: ET.Element, name: str) -> float | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
def gitgraph__path_average_position(element: ET.Element) -> tuple[float, float] | None:
    numbers = [float(match.group(0)) for match in re.finditer('[-+]?(?:\\d*\\.\\d+|\\d+)(?:[eE][-+]?\\d+)?', element.get('d', ''))]
    points = list(zip(numbers[0::2], numbers[1::2]))
    if not points:
        return None
    return (sum((point[0] for point in points)) / len(points), sum((point[1] for point in points)) / len(points))
def gitgraph__gitgraph_commit_position(candidate: Candidate) -> tuple[float, float] | None:
    tag = local_name(candidate.element.tag)
    if tag == 'circle':
        x = gitgraph__numeric_attribute(candidate.element, 'cx')
        y = gitgraph__numeric_attribute(candidate.element, 'cy')
        if x is not None and y is not None:
            return (x, y)
    if tag == 'rect':
        x = gitgraph__numeric_attribute(candidate.element, 'x')
        y = gitgraph__numeric_attribute(candidate.element, 'y')
        width = gitgraph__numeric_attribute(candidate.element, 'width')
        height = gitgraph__numeric_attribute(candidate.element, 'height')
        if x is not None and y is not None and (width is not None) and (height is not None):
            return (x + width / 2, y + height / 2)
    if tag == 'path':
        return gitgraph__path_average_position(candidate.element)
    return None
def gitgraph__commit_label_position(candidate: Candidate, parent_map: dict[ET.Element, ET.Element]) -> tuple[float, float] | None:
    parent = parent_map.get(candidate.element)
    if parent is not None:
        for sibling in parent:
            if local_name(sibling.tag) != 'rect':
                continue
            if 'commit-label-bkg' not in {token.lower() for token in class_tokens(sibling)}:
                continue
            x = gitgraph__numeric_attribute(sibling, 'x')
            y = gitgraph__numeric_attribute(sibling, 'y')
            width = gitgraph__numeric_attribute(sibling, 'width')
            height = gitgraph__numeric_attribute(sibling, 'height')
            if x is not None and y is not None and (width is not None) and (height is not None):
                return (x + width / 2, y + height / 2)
    x = gitgraph__numeric_attribute(candidate.element, 'x')
    y = gitgraph__numeric_attribute(candidate.element, 'y')
    if x is not None and y is not None:
        return (x, y)
    return None
def gitgraph__edge_target_x(candidate: Candidate) -> float | None:
    endpoints = edge_endpoints(candidate)
    if endpoints is None:
        return None
    start, end = endpoints
    return max(start[0], end[0])
def gitgraph__nearest_commit_index(x: float, event_x_values: list[float], tolerance: float) -> int | None:
    if not event_x_values:
        return None
    index, nearest_x = min(enumerate(event_x_values), key=lambda item: abs(item[1] - x))
    if abs(nearest_x - x) <= tolerance:
        return index
    return None
def gitgraph__position_tolerance(event_x_values: list[float]) -> float:
    if len(event_x_values) < 2:
        return 32.0
    gaps = [second - first for first, second in zip(event_x_values, event_x_values[1:]) if second > first]
    if not gaps:
        return 32.0
    return max(16.0, min(gaps) * 0.6)
def gitgraph__plan_gitgraph_candidates(candidates: list[Candidate], root: ET.Element, args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    parent_map = build_parent_map(root)
    commit_candidates = [candidate for candidate in candidates if candidate.role == 'node' and gitgraph__candidate_has_class(candidate, 'commit')]
    edge_candidates = [candidate for candidate in candidates if candidate.role == 'edge' and gitgraph__candidate_has_class(candidate, 'arrow')]
    commit_label_candidates = [candidate for candidate in candidates if candidate.role == 'label' and gitgraph__candidate_has_class(candidate, 'commit-label')]
    static_candidates = [candidate for candidate in candidates if candidate.role == 'label' and any((token.lower().startswith('branch-label') for token in candidate.classes))]
    commit_positions = {id(candidate): position for candidate in commit_candidates if (position := gitgraph__gitgraph_commit_position(candidate)) is not None}
    if not commit_positions:
        return []
    event_x_values = sorted({round(position[0], 3) for position in commit_positions.values()})
    tolerance = gitgraph__position_tolerance(event_x_values)
    commits_by_event: dict[int, list[Candidate]] = {index: [] for index in range(len(event_x_values))}
    for candidate in sorted(commit_candidates, key=lambda item: (commit_positions.get(id(item), (0.0, 0.0)), item.dom_index)):
        position = commit_positions.get(id(candidate))
        if position is None:
            continue
        event_index = gitgraph__nearest_commit_index(position[0], event_x_values, tolerance)
        if event_index is not None:
            commits_by_event[event_index].append(candidate)
    edges_by_event: dict[int, list[Candidate]] = {index: [] for index in range(len(event_x_values))}
    for candidate in sorted(edge_candidates, key=lambda item: (gitgraph__edge_target_x(item) or 0.0, item.dom_index)):
        target_x = gitgraph__edge_target_x(candidate)
        if target_x is None:
            continue
        event_index = gitgraph__nearest_commit_index(target_x, event_x_values, tolerance)
        if event_index is not None:
            candidate.target_index = event_index
            edges_by_event[event_index].append(candidate)
    labels_by_event: dict[int, list[Candidate]] = {index: [] for index in range(len(event_x_values))}
    for candidate in sorted(commit_label_candidates, key=lambda item: (gitgraph__commit_label_position(item, parent_map) or (0.0, 0.0), item.dom_index)):
        position = gitgraph__commit_label_position(candidate, parent_map)
        if position is None:
            continue
        event_index = gitgraph__nearest_commit_index(position[0], event_x_values, tolerance)
        if event_index is not None:
            labels_by_event[event_index].append(candidate)
    stages: list[list[Candidate]] = []
    for event_index in range(len(event_x_values)):
        point_stage = [*commits_by_event[event_index], *labels_by_event[event_index]]
        if point_stage:
            stages.append(point_stage)
        if edges_by_event[event_index]:
            stages.append(edges_by_event[event_index])
    if not stages:
        return []
    for candidate in static_candidates:
        candidate.effect = 'none'
        candidate.delay_ms = 0.0
        candidate.duration_ms = 0.0
    duration = float(args.duration_ms)
    minimum_stage_gap = duration + float(args.stagger_ms)
    if args.total_ms is not None and len(stages) > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        stage_gap = max(minimum_stage_gap, available / (len(stages) - 1))
    else:
        stage_gap = minimum_stage_gap
    planned: list[Candidate] = [*static_candidates]
    for stage_index, stage in enumerate(stages):
        delay = float(args.initial_delay_ms) + stage_index * stage_gap
        for candidate in stage:
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = delay
            candidate.duration_ms = duration
            candidate.stage = stage_index
            planned.append(candidate)
    planned_ids = {id(candidate) for candidate in planned}
    for candidate in candidates:
        if id(candidate) in planned_ids:
            continue
        candidate.effect = effect_for(effective_animation, candidate.role)
        candidate.delay_ms = float(args.initial_delay_ms) + len(stages) * stage_gap
        candidate.duration_ms = duration
        candidate.stage = len(stages)
        planned.append(candidate)
    return planned

# --- ishikawa ---

def ishikawa__is_ishikawa_root(root: ET.Element) -> bool:
    role = normalized(root.get('aria-roledescription', ''))
    return role == 'ishikawa' or has_lower_class(root, 'ishikawa')
def ishikawa__discover_ishikawa_candidates(root: ET.Element, parent_map: dict[ET.Element, ET.Element], dom_order: dict[ET.Element, int]) -> list[Candidate]:
    selected: set[ET.Element] = set()
    candidates: list[Candidate] = []

    def add_candidate(element: ET.Element, role: str) -> None:
        if element in selected:
            return
        selected.add(element)
        candidates.append(Candidate(element=element, role=role, dom_index=dom_order[element], element_id=element.get('id', ''), classes=class_tokens(element), text=collapsed_text(element)))
    for element in root.iter():
        lower_tokens = {token.lower() for token in class_tokens(element)}
        if 'ishikawa-head-group' in lower_tokens:
            add_candidate(element, 'node')
        elif lower_tokens & {'ishikawa-spine', 'ishikawa-branch', 'ishikawa-sub-branch'}:
            add_candidate(element, 'edge')
        elif 'ishikawa-label-group' in lower_tokens:
            add_candidate(element, 'label')
        elif local_name(element.tag) == 'text' and 'ishikawa-label' in lower_tokens and (not ancestor_has_class_fragment(element, parent_map, 'ishikawa-label-group')):
            add_candidate(element, 'label')
    return candidates
def ishikawa__ishikawa_problem_position(head_candidates: list[Candidate], spine_candidates: list[Candidate]) -> tuple[float, float] | None:
    for candidate in head_candidates:
        position = translate_position(candidate.element)
        if position is not None:
            return position
    for candidate in spine_candidates:
        endpoints = edge_endpoints(candidate)
        if endpoints is not None:
            first, second = endpoints
            return second if second[0] >= first[0] else first
    return None
def ishikawa__ishikawa_branch_stages(pair: ET.Element, candidate_by_element: dict[ET.Element, Candidate]) -> list[list[list[Candidate]]]:
    branches: list[list[list[Candidate]]] = []
    current: list[list[Candidate]] = []

    def flush_current() -> None:
        nonlocal current
        if current:
            branches.append(current)
            current = []
    for child in list(pair):
        if has_lower_class(child, 'ishikawa-branch'):
            flush_current()
            branch_line = candidate_by_element.get(child)
            current = [[branch_line]] if branch_line is not None else []
        elif has_lower_class(child, 'ishikawa-label-group'):
            label = candidate_by_element.get(child)
            if label is not None:
                if not current:
                    current = [[label]]
                else:
                    current[0].append(label)
        elif has_lower_class(child, 'ishikawa-sub-group'):
            point_stage: list[Candidate] = []
            for point_child in child.iter():
                if point_child is child:
                    continue
                point_candidate = candidate_by_element.get(point_child)
                if point_candidate is not None:
                    point_stage.append(point_candidate)
            if point_stage:
                current.append(point_stage)
    flush_current()
    return branches
def ishikawa__ishikawa_branch_duration(branch_index: int, stage_count: int, duration: float, args: argparse.Namespace, default_branch_ms: float | None) -> float:
    branch_durations = parse_number_list(args.ishikawa_branch_durations, '--ishikawa-branch-durations')
    if branch_index < len(branch_durations):
        requested = branch_durations[branch_index]
    elif args.ishikawa_branch_ms is not None:
        requested = float(args.ishikawa_branch_ms)
    elif default_branch_ms is not None:
        requested = default_branch_ms
    else:
        requested = duration * stage_count + float(args.stagger_ms) * max(0, stage_count - 1)
    minimum = duration * stage_count
    return max(minimum, requested)
def ishikawa__assign_ishikawa_branch_stages(stages: list[list[Candidate]], branch_index: int, stage_start: int, current_delay: float, duration: float, args: argparse.Namespace, default_branch_ms: float | None, planned: list[Candidate]) -> tuple[int, float]:
    if not stages:
        return (stage_start, current_delay)
    total_branch_ms = ishikawa__ishikawa_branch_duration(branch_index, len(stages), duration, args, default_branch_ms)
    start_gap = 0.0
    if len(stages) > 1:
        start_gap = max(duration, (total_branch_ms - duration) / (len(stages) - 1))
    branch_end = current_delay
    for branch_step, stage_candidates in enumerate(stages):
        delay = current_delay + branch_step * start_gap
        for candidate in sorted(stage_candidates, key=lambda item: (ROLE_PRIORITY.get(item.role, 99), item.dom_index)):
            candidate.effect = effect_for('ishikawa', candidate.role)
            candidate.delay_ms = delay
            candidate.duration_ms = duration
            candidate.stage = stage_start + branch_step
            candidate.branch_index = branch_index
            candidate.branch_step = branch_step
            planned.append(candidate)
        branch_end = max(branch_end, delay + duration)
    return (stage_start + len(stages), branch_end)
def ishikawa__plan_ishikawa_candidates(candidates: list[Candidate], root: ET.Element, args: argparse.Namespace) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    candidate_by_element = {candidate.element: candidate for candidate in candidates}
    head_candidates = [candidate for candidate in candidates if has_lower_class(candidate.element, 'ishikawa-head-group')]
    spine_candidates = [candidate for candidate in candidates if has_lower_class(candidate.element, 'ishikawa-spine')]
    problem_position = ishikawa__ishikawa_problem_position(head_candidates, spine_candidates)
    branch_specs: list[tuple[float, int, list[list[Candidate]]]] = []
    for pair in root.iter():
        if not has_lower_class(pair, 'ishikawa-pair'):
            continue
        for stages in ishikawa__ishikawa_branch_stages(pair, candidate_by_element):
            first_edge = next((candidate for stage in stages for candidate in stage if candidate.role == 'edge'), None)
            start = line_start(first_edge) if first_edge is not None else None
            distance = squared_distance(problem_position, start) if problem_position is not None and start is not None else float('inf')
            first_dom = min((candidate.dom_index for stage in stages for candidate in stage), default=0)
            branch_specs.append((distance, first_dom, stages))
    branch_specs.sort(key=lambda item: (item[0], item[1]))
    if not head_candidates and (not spine_candidates) and (not branch_specs):
        return []
    duration = float(args.duration_ms)
    initial_delay = float(args.initial_delay_ms)
    base_candidates = sorted([*head_candidates, *spine_candidates], key=lambda candidate: (ROLE_PRIORITY.get(candidate.role, 99), candidate.dom_index))
    branch_gap = float(args.ishikawa_branch_gap_ms) if args.ishikawa_branch_gap_ms is not None else float(args.stagger_ms)
    branch_durations = parse_number_list(args.ishikawa_branch_durations, '--ishikawa-branch-durations')
    explicit_branch_timing = args.ishikawa_branch_ms is not None or bool(branch_durations)
    default_branch_ms: float | None = None
    if args.total_ms is not None and branch_specs and (not explicit_branch_timing):
        available = float(args.total_ms) - initial_delay - (duration if base_candidates else 0.0) - branch_gap * max(0, len(branch_specs) - 1)
        default_branch_ms = max(0.0, available / len(branch_specs))
    planned: list[Candidate] = []
    for candidate in base_candidates:
        candidate.effect = effect_for('ishikawa', candidate.role)
        candidate.delay_ms = initial_delay
        candidate.duration_ms = duration
        candidate.stage = 0
        planned.append(candidate)
    stage_index = 1 if base_candidates else 0
    current_delay = initial_delay + (duration if base_candidates and branch_specs else 0.0)
    for branch_index, (_distance, _dom, stages) in enumerate(branch_specs):
        stage_index, branch_end = ishikawa__assign_ishikawa_branch_stages(stages, branch_index, stage_index, current_delay, duration, args, default_branch_ms, planned)
        current_delay = branch_end + (branch_gap if branch_index < len(branch_specs) - 1 else 0.0)
    return planned

# --- journey ---

def journey__is_journey_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'journey'
def journey__has_class(element: ET.Element, token: str) -> bool:
    return token.lower() in {value.lower() for value in class_tokens(element)}
def journey__class_starts_with(element: ET.Element, prefix: str) -> bool:
    return any((value.lower().startswith(prefix.lower()) for value in class_tokens(element)))
def journey__visible_text(element: ET.Element) -> str:
    parts: list[str] = []
    seen: set[str] = set()

    def visit(node: ET.Element) -> None:
        if local_name(node.tag) in {'title', 'desc'}:
            return
        if node.text:
            add_text(node.text)
        for child in node:
            visit(child)
            if child.tail:
                add_text(child.tail)

    def add_text(value: str) -> None:
        text = re.sub('\\s+', ' ', value.strip())
        key = normalized(text)
        if text and key not in seen:
            seen.add(key)
            parts.append(text)
    visit(element)
    return ' '.join(parts)
def journey__direct_child_with_class(element: ET.Element, token: str) -> ET.Element | None:
    for child in element:
        if journey__has_class(child, token):
            return child
    return None
def journey__is_section_group(element: ET.Element) -> bool:
    return local_name(element.tag) == 'g' and journey__direct_child_with_class(element, 'journey-section') is not None
def journey__is_task_group(element: ET.Element) -> bool:
    if local_name(element.tag) != 'g':
        return False
    if journey__direct_child_with_class(element, 'task-line') is not None:
        return True
    return any((local_name(child.tag) == 'rect' and journey__has_class(child, 'task') and journey__class_starts_with(child, 'task-type-') for child in element))
def journey__inherited_classes(element: ET.Element, extra_classes: Iterable[str]) -> list[str]:
    classes = class_tokens(element)
    for child in element:
        for token in class_tokens(child):
            if (token in {'journey-section', 'task', 'task-line', 'face'} or token.startswith('section-type-') or token.startswith('task-type-')) and token not in classes:
                classes.append(token)
    for extra_class in extra_classes:
        if extra_class not in classes:
            classes.append(extra_class)
    return classes
def journey__discover_journey_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for element in root.iter():
        if journey__is_section_group(element):
            candidates.append(Candidate(element=element, role='cluster', dom_index=dom_order[element], element_id=element.get('id', ''), classes=journey__inherited_classes(element, ['journey-section-column']), text=journey__visible_text(element)))
            continue
        if journey__is_task_group(element):
            candidates.append(Candidate(element=element, role='node', dom_index=dom_order[element], element_id=element.get('id', ''), classes=journey__inherited_classes(element, ['journey-task-column']), text=journey__visible_text(element)))
    return candidates
def journey__numeric_attribute(element: ET.Element, name: str) -> float | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
def journey__candidate_has_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def journey__section_position(candidate: Candidate) -> tuple[float, float] | None:
    section = journey__direct_child_with_class(candidate.element, 'journey-section')
    if section is None:
        return None
    x = journey__numeric_attribute(section, 'x')
    y = journey__numeric_attribute(section, 'y')
    if x is None or y is None:
        return None
    return (x, y)
def journey__task_position(candidate: Candidate) -> tuple[float, float] | None:
    for child in candidate.element:
        if local_name(child.tag) == 'rect' and journey__has_class(child, 'task') and journey__class_starts_with(child, 'task-type-'):
            x = journey__numeric_attribute(child, 'x')
            y = journey__numeric_attribute(child, 'y')
            if x is not None and y is not None:
                return (x, y)
    line = journey__direct_child_with_class(candidate.element, 'task-line')
    if line is None:
        return None
    x = journey__numeric_attribute(line, 'x1')
    y = journey__numeric_attribute(line, 'y1')
    if x is None or y is None:
        return None
    return (x, y)
def journey__journey_position(candidate: Candidate) -> tuple[float, float] | None:
    if journey__candidate_has_class(candidate, 'journey-section-column'):
        return journey__section_position(candidate)
    if journey__candidate_has_class(candidate, 'journey-task-column'):
        return journey__task_position(candidate)
    return None
def journey__journey_role_rank(candidate: Candidate) -> int:
    if journey__candidate_has_class(candidate, 'journey-section-column'):
        return 0
    if journey__candidate_has_class(candidate, 'journey-task-column'):
        return 1
    return 2
def journey__column_key(candidate: Candidate) -> float:
    position = journey__journey_position(candidate)
    if position is None:
        return float('inf')
    return round(position[0], 3)
def journey__candidate_key(candidate: Candidate) -> tuple[int, float, int, float, int]:
    position = journey__journey_position(candidate)
    if position is None:
        return (1, 0.0, journey__journey_role_rank(candidate), 0.0, candidate.dom_index)
    return (0, position[0], journey__journey_role_rank(candidate), position[1], candidate.dom_index)
def journey__plan_journey_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    ordered = sorted(candidates, key=journey__candidate_key)
    if not ordered:
        return []
    stage_keys = sorted({journey__column_key(candidate) for candidate in ordered})
    stage_by_key = {key: index for index, key in enumerate(stage_keys)}
    duration = float(args.duration_ms)
    if args.total_ms is not None and len(stage_keys) > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        stagger = max(0.0, available / (len(stage_keys) - 1))
    else:
        stagger = float(args.stagger_ms)
    for candidate in ordered:
        stage = stage_by_key[journey__column_key(candidate)]
        candidate.effect = effect_for(effective_animation, candidate.role)
        candidate.delay_ms = float(args.initial_delay_ms) + stage * stagger
        candidate.duration_ms = duration
        candidate.stage = stage
    return ordered

# --- kanban ---

def kanban__is_kanban_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'kanban'
def kanban__plan_kanban_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    task_candidates = sorted([candidate for candidate in candidates if candidate.role in {'node', 'item'}], key=ordered_reveal_key)
    task_ids = {id(candidate) for candidate in task_candidates}
    board_candidates = sorted([candidate for candidate in candidates if id(candidate) not in task_ids], key=ordered_reveal_key)
    duration = float(args.duration_ms)
    initial_delay = float(args.initial_delay_ms)
    task_start_delay = initial_delay + (duration if board_candidates else 0.0)
    if args.total_ms is not None and len(task_candidates) > 1:
        last_task_delay = max(task_start_delay, float(args.total_ms) - duration)
        task_stagger = (last_task_delay - task_start_delay) / (len(task_candidates) - 1)
    else:
        task_stagger = float(args.stagger_ms)
    for candidate in board_candidates:
        candidate.effect = effect_for(effective_animation, candidate.role)
        candidate.delay_ms = initial_delay
        candidate.duration_ms = duration
    for index, candidate in enumerate(task_candidates):
        candidate.effect = effect_for(effective_animation, candidate.role)
        candidate.delay_ms = task_start_delay + index * task_stagger
        candidate.duration_ms = duration
    return sorted([*board_candidates, *task_candidates], key=lambda candidate: (candidate.delay_ms, ROLE_PRIORITY.get(candidate.role, 99), candidate.dom_index))

# --- mindmap ---

def mindmap__is_mindmap_candidates(candidates: list[Candidate]) -> bool:
    return any(('mindmap-node' in class_tokens(candidate.element) for candidate in candidates))
def mindmap__mindmap_edge_indexes(element_id: str) -> tuple[int, int] | None:
    match = re.search('edge_(\\d+)_(\\d+)$', element_id)
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)))
def mindmap__mindmap_root_indexes(nodes: dict[int, Candidate], edges: list[tuple[Candidate, int, int]]) -> list[int]:
    parents = {target for _, _, target in edges}
    explicit_roots = [index for index, candidate in nodes.items() if 'section-root' in {token.lower() for token in candidate.classes}]
    return explicit_roots or [index for index in nodes if index not in parents]
def mindmap__mindmap_child_edges(edges: list[tuple[Candidate, int, int]]) -> dict[int, list[tuple[Candidate, int]]]:
    children: dict[int, list[tuple[Candidate, int]]] = {}
    for candidate, source, target in edges:
        children.setdefault(source, []).append((candidate, target))
    for source in children:
        children[source].sort(key=lambda item: item[0].dom_index)
    return children
def mindmap__mindmap_levels(nodes: dict[int, Candidate], edges: list[tuple[Candidate, int, int]]) -> dict[int, int]:
    roots = mindmap__mindmap_root_indexes(nodes, edges)
    children = mindmap__mindmap_child_edges(edges)
    levels: dict[int, int] = {}
    queue: list[tuple[int, int]] = [(root, 0) for root in roots]
    while queue:
        node_index, level = queue.pop(0)
        if node_index in levels and levels[node_index] <= level:
            continue
        levels[node_index] = level
        for _, child in children.get(node_index, []):
            queue.append((child, level + 1))
    for node_index in nodes:
        levels.setdefault(node_index, 0)
    return levels
def mindmap__radial_edge_sort_key(candidate: Candidate, nodes: dict[int, Candidate], origin: tuple[float, float] | None) -> tuple[float, float, int]:
    target = nodes.get(candidate.target_index or -1)
    target_position = translate_position(target.element) if target is not None else None
    if origin is None or target_position is None:
        return (0.0, 0.0, candidate.dom_index)
    dx = target_position[0] - origin[0]
    dy = target_position[1] - origin[1]
    distance = math.hypot(dx, dy)
    angle = (math.atan2(dy, dx) + math.pi / 2) % (2 * math.pi)
    return (distance, angle, candidate.dom_index)
def mindmap__assign_mindmap_delays(planned: list[Candidate], nodes: dict[int, Candidate], args: argparse.Namespace) -> None:
    stage_values = sorted({candidate.stage for candidate in planned if candidate.stage is not None})
    origin = average_position((candidate for candidate in nodes.values() if candidate.level == 0))
    raw_delays: dict[int, float] = {}
    current_delay = float(args.initial_delay_ms)
    inter_stage_gap = float(args.stagger_ms)
    wave_gap = float(args.mindmap_radial_wave_ms)
    for stage in stage_values:
        stage_candidates = [candidate for candidate in planned if candidate.stage == stage]
        edge_candidates = [candidate for candidate in stage_candidates if candidate.effect == 'radial-arrow']
        edge_order = {id(candidate): index for index, candidate in enumerate(sorted(edge_candidates, key=lambda candidate: mindmap__radial_edge_sort_key(candidate, nodes, origin)))}
        stage_span = 0.0
        for candidate in stage_candidates:
            wave_index = edge_order.get(id(candidate), 0)
            if candidate.effect == 'radial-arrow':
                candidate.wave_index = wave_index
            offset = wave_index * wave_gap
            raw_delays[id(candidate)] = current_delay + offset
            stage_span = max(stage_span, offset)
        current_delay += stage_span + float(args.duration_ms) + inter_stage_gap
    if args.total_ms is not None and planned:
        raw_last_delay = max(raw_delays.values())
        target_last_delay = max(float(args.initial_delay_ms), float(args.total_ms) - float(args.duration_ms))
        span = raw_last_delay - float(args.initial_delay_ms)
        scale = 0.0 if span <= 0 else (target_last_delay - float(args.initial_delay_ms)) / span
    else:
        scale = 1.0
    for candidate in planned:
        raw_delay = raw_delays[id(candidate)]
        candidate.delay_ms = float(args.initial_delay_ms) + (raw_delay - float(args.initial_delay_ms)) * scale
def mindmap__extract_mindmap_graph(candidates: list[Candidate]) -> tuple[dict[int, Candidate], list[tuple[Candidate, int, int]]]:
    nodes: dict[int, Candidate] = {}
    edges: list[tuple[Candidate, int, int]] = []
    for candidate in candidates:
        if 'mindmap-node' in candidate.classes:
            node_index = numeric_id_suffix(candidate.element_id, 'node_')
            if node_index is not None:
                nodes[node_index] = candidate
        elif candidate.role == 'edge':
            edge_indexes = mindmap__mindmap_edge_indexes(candidate.element_id)
            if edge_indexes is not None:
                edges.append((candidate, edge_indexes[0], edge_indexes[1]))
    edges.sort(key=lambda edge: edge[0].dom_index)
    return (nodes, edges)
def mindmap__assign_mindmap_branch_delays(planned: list[Candidate], args: argparse.Namespace) -> None:
    if not planned:
        return
    duration = float(args.duration_ms)
    branch_durations = parse_number_list(args.mindmap_branch_durations, '--mindmap-branch-durations')
    branch_gap = float(args.mindmap_branch_gap_ms) if args.mindmap_branch_gap_ms is not None else float(args.stagger_ms)
    branch_budget = args.mindmap_branch_ms
    branch_timing_enabled = branch_budget is not None or bool(branch_durations)
    if not branch_timing_enabled and args.total_ms is not None and (len(planned) > 1):
        available_gap = float(args.total_ms) - duration * len(planned) - float(args.initial_delay_ms)
        step_gap = max(0.0, available_gap / (len(planned) - 1))
    elif not branch_timing_enabled:
        step_gap = float(args.stagger_ms)
    if not branch_timing_enabled:
        for index, candidate in enumerate(planned):
            candidate.delay_ms = float(args.initial_delay_ms) + index * (duration + step_gap)
            candidate.duration_ms = duration
            candidate.stage = index
        return
    root_candidates = [candidate for candidate in planned if candidate.branch_index is None]
    branch_indexes = sorted({candidate.branch_index for candidate in planned if candidate.branch_index is not None})
    current_delay = float(args.initial_delay_ms)
    for candidate in root_candidates:
        candidate.delay_ms = current_delay
        candidate.duration_ms = duration
        current_delay += duration + branch_gap
    for branch_index in branch_indexes:
        branch_candidates = sorted([candidate for candidate in planned if candidate.branch_index == branch_index], key=lambda candidate: candidate.branch_step if candidate.branch_step is not None else 999)
        if not branch_candidates:
            continue
        if branch_index < len(branch_durations):
            total_branch_ms = branch_durations[branch_index]
        elif branch_budget is not None:
            total_branch_ms = float(branch_budget)
        else:
            total_branch_ms = duration * len(branch_candidates) + float(args.stagger_ms) * max(0, len(branch_candidates) - 1)
        start_gap = 0.0
        if len(branch_candidates) > 1:
            start_gap = max(0.0, (total_branch_ms - duration) / (len(branch_candidates) - 1))
        branch_end = current_delay
        for index, candidate in enumerate(branch_candidates):
            candidate.delay_ms = current_delay + index * start_gap
            candidate.duration_ms = duration
            branch_end = max(branch_end, candidate.delay_ms + duration)
        current_delay = branch_end + branch_gap
    for stage, candidate in enumerate(sorted(planned, key=lambda item: (item.delay_ms, item.dom_index))):
        candidate.stage = stage
def mindmap__plan_mindmap_branch_candidates(candidates: list[Candidate], args: argparse.Namespace) -> list[Candidate]:
    nodes, edges = mindmap__extract_mindmap_graph(candidates)
    if not nodes:
        return []
    levels = mindmap__mindmap_levels(nodes, edges)
    roots = mindmap__mindmap_root_indexes(nodes, edges)
    children = mindmap__mindmap_child_edges(edges)
    planned: list[Candidate] = []
    planned_elements: set[ET.Element] = set()
    branch_index = 0

    def add_candidate(candidate: Candidate, effect: str, branch: int | None, step: int | None) -> None:
        if candidate.element in planned_elements:
            return
        candidate.effect = effect
        candidate.branch_index = branch
        candidate.branch_step = step
        candidate.duration_ms = float(args.duration_ms)
        planned_elements.add(candidate.element)
        planned.append(candidate)

    def visit_child(edge: Candidate, source: int, target: int, branch: int, step: int) -> int:
        node = nodes.get(target)
        if node is not None:
            node.level = levels.get(target, 0)
            add_candidate(node, 'pop', branch, step)
            step += 1
        edge.level = levels.get(source, 0)
        edge.source_index = source
        edge.target_index = target
        edge.wave_index = step
        add_candidate(edge, 'radial-arrow', branch, step)
        step += 1
        for child_edge, child_target in children.get(target, []):
            step = visit_child(child_edge, target, child_target, branch, step)
        return step
    for root_index in sorted(roots, key=lambda index: nodes[index].dom_index):
        root = nodes[root_index]
        root.level = levels.get(root_index, 0)
        add_candidate(root, 'pop', None, None)
        for edge, target in children.get(root_index, []):
            visit_child(edge, root_index, target, branch_index, 0)
            branch_index += 1
    for candidate in sorted(nodes.values(), key=lambda item: item.dom_index):
        candidate.level = levels.get(numeric_id_suffix(candidate.element_id, 'node_') or 0, 0)
        add_candidate(candidate, 'pop', None, None)
    for edge, source, target in edges:
        edge.level = levels.get(source, 0)
        edge.source_index = source
        edge.target_index = target
        add_candidate(edge, 'radial-arrow', None, None)
    mindmap__assign_mindmap_branch_delays(planned, args)
    return planned
def mindmap__plan_mindmap_candidates(candidates: list[Candidate], args: argparse.Namespace) -> list[Candidate]:
    if getattr(args, 'effective_animation', args.animation) == 'mindmap-branch':
        return mindmap__plan_mindmap_branch_candidates(candidates, args)
    nodes, edges = mindmap__extract_mindmap_graph(candidates)
    if not nodes:
        return []
    levels = mindmap__mindmap_levels(nodes, edges)
    planned: list[Candidate] = []
    for node_index, candidate in nodes.items():
        level = levels[node_index]
        candidate.level = level
        candidate.stage = level * 2
        candidate.effect = 'pop'
        candidate.duration_ms = float(args.duration_ms)
        planned.append(candidate)
    for candidate, source, _target in edges:
        source_level = levels.get(source)
        if source_level is None:
            edge_depth = class_number(candidate, 'edge-depth-')
            source_level = max(0, (edge_depth - 1) // 2) if edge_depth is not None else 0
        target_level = levels.get(_target, source_level + 1)
        candidate.level = source_level
        candidate.stage = target_level * 2 + 1
        candidate.source_index = source
        candidate.target_index = _target
        candidate.effect = 'radial-arrow'
        candidate.duration_ms = float(args.duration_ms)
        planned.append(candidate)
    mindmap__assign_mindmap_delays(planned, nodes, args)
    return sorted(planned, key=lambda candidate: (candidate.delay_ms, ROLE_PRIORITY.get(candidate.role, 99), candidate.dom_index))

# --- pie ---

pie__BRACKETED_NUMBER_RE = re.compile('\\[\\s*([-+]?(?:\\d*\\.\\d+|\\d+))\\s*\\]')
pie__PERCENT_RE = re.compile('([-+]?(?:\\d*\\.\\d+|\\d+))\\s*%')
def pie__is_pie_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'pie'
def pie__add_classes(classes: list[str], extra_classes: Iterable[str]) -> list[str]:
    result = [*classes]
    for extra_class in extra_classes:
        if extra_class and extra_class not in result:
            result.append(extra_class)
    return result
def pie__segment_value(*texts: str) -> float | None:
    for text in texts:
        match = pie__BRACKETED_NUMBER_RE.search(text)
        if match:
            return float(match.group(1))
    for text in texts:
        match = pie__PERCENT_RE.search(text)
        if match:
            return float(match.group(1))
    return None
def pie__value_token(value: float | None) -> str | None:
    if value is None:
        return None
    return slug(f'value {value:g}')
def pie__legend_label(text: str, index: int) -> str:
    label = pie__BRACKETED_NUMBER_RE.sub('', text).strip()
    return label or f'segment {index + 1}'
def pie__segment_text(legend_text: str, slice_text: str) -> str:
    parts: list[str] = []
    for text in (legend_text, slice_text):
        if text and text not in parts:
            parts.append(text)
    return ' '.join(parts)
def pie__segment_classes(index: int, legend_text: str, value: float | None) -> list[str]:
    classes = ['pie-segment', f'pie-segment-{index}']
    label_slug = slug(pie__legend_label(legend_text, index))
    if label_slug:
        classes.append(f'pie-label-{label_slug}')
    if (value_slug := pie__value_token(value)):
        classes.append(f'pie-{value_slug}')
    return classes
def pie__discover_pie_chart_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    wedges: list[ET.Element] = []
    percentages: list[ET.Element] = []
    legends: list[ET.Element] = []
    for element in root.iter():
        if local_name(element.tag) == 'path' and has_lower_class(element, 'piecircle'):
            wedges.append(element)
        elif local_name(element.tag) == 'text' and has_lower_class(element, 'slice'):
            percentages.append(element)
        elif local_name(element.tag) == 'g' and has_lower_class(element, 'legend'):
            legends.append(element)
    segment_count = max(len(wedges), len(percentages), len(legends))
    if segment_count == 0:
        return []
    candidates: list[Candidate] = []
    for index in range(segment_count):
        wedge = wedges[index] if index < len(wedges) else None
        percentage = percentages[index] if index < len(percentages) else None
        legend = legends[index] if index < len(legends) else None
        legend_text = collapsed_text(legend) if legend is not None else ''
        percentage_text = collapsed_text(percentage) if percentage is not None else ''
        value = pie__segment_value(legend_text, percentage_text)
        text = pie__segment_text(legend_text, percentage_text)
        extra_classes = pie__segment_classes(index, legend_text, value)
        for element, role in ((wedge, 'node'), (percentage, 'label'), (legend, 'label')):
            if element is None:
                continue
            candidates.append(Candidate(element=element, role=role, dom_index=dom_order[element], element_id=element.get('id', ''), classes=pie__add_classes(class_tokens(element), extra_classes), text=text, branch_index=index))
    return candidates
def pie__candidate_segment_index(candidate: Candidate) -> int:
    return candidate.branch_index if candidate.branch_index is not None else candidate.dom_index
def pie__candidate_piece_order(candidate: Candidate) -> tuple[int, int]:
    lower_classes = {value.lower() for value in candidate.classes}
    if 'piecircle' in lower_classes:
        return (0, candidate.dom_index)
    if 'slice' in lower_classes:
        return (1, candidate.dom_index)
    if 'legend' in lower_classes:
        return (2, candidate.dom_index)
    return (3, candidate.dom_index)
def pie__candidate_value(candidate: Candidate) -> float | None:
    return pie__segment_value(candidate.text)
def pie__plan_pie_chart_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    grouped: dict[int, list[Candidate]] = defaultdict(list)
    for candidate in candidates:
        grouped[pie__candidate_segment_index(candidate)].append(candidate)
    segments = [sorted(group, key=pie__candidate_piece_order) for _, group in sorted(grouped.items())]
    if not segments:
        return []
    any_explicit_order = any((candidate.explicit_order is not None for candidate in candidates))

    def segment_order_key(segment: list[Candidate]) -> tuple[int, float, int]:
        segment_index = pie__candidate_segment_index(segment[0])
        explicit_orders = [candidate.explicit_order for candidate in segment if candidate.explicit_order is not None]
        if any_explicit_order:
            if explicit_orders:
                return (0, float(min(explicit_orders)), segment_index)
            return (1, 0.0, segment_index)
        values = [value for candidate in segment if (value := pie__candidate_value(candidate)) is not None]
        if values:
            return (0, min(values), segment_index)
        return (1, 0.0, segment_index)
    ordered_segments = sorted(segments, key=segment_order_key)
    animation = 'sequence' if effective_animation == 'pie-segments' else effective_animation
    duration = float(args.duration_ms)
    step_gap = duration + float(args.stagger_ms)
    if args.total_ms is not None and len(ordered_segments) > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        step_gap = max(step_gap, available / (len(ordered_segments) - 1))
    ordered: list[Candidate] = []
    for stage, segment in enumerate(ordered_segments):
        delay = float(args.initial_delay_ms) + stage * step_gap
        for piece_index, candidate in enumerate(segment):
            candidate.effect = effect_for(animation, candidate.role)
            candidate.delay_ms = delay
            candidate.duration_ms = duration
            candidate.stage = stage
            candidate.branch_step = piece_index
            ordered.append(candidate)
    return ordered

# --- quadrant ---

def quadrant__is_quadrant_chart_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'quadrantchart'
def quadrant__numeric_attribute(element: ET.Element, name: str) -> float | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
def quadrant__add_classes(classes: list[str], extra_classes: Iterable[str]) -> list[str]:
    result = [*classes]
    for extra_class in extra_classes:
        if extra_class not in result:
            result.append(extra_class)
    return result
def quadrant__first_circle_position(element: ET.Element) -> tuple[float, float] | None:
    for child in element.iter():
        if local_name(child.tag) != 'circle':
            continue
        x = quadrant__numeric_attribute(child, 'cx')
        y = quadrant__numeric_attribute(child, 'cy')
        if x is not None and y is not None:
            return (x, y)
    return None
def quadrant__quadrant_rect_bounds(root: ET.Element) -> tuple[float, float, float, float] | None:
    rect_bounds: list[tuple[float, float, float, float]] = []
    for element in root.iter():
        if local_name(element.tag) != 'g' or not has_lower_class(element, 'quadrant'):
            continue
        for child in element:
            if local_name(child.tag) != 'rect':
                continue
            x = quadrant__numeric_attribute(child, 'x')
            y = quadrant__numeric_attribute(child, 'y')
            width = quadrant__numeric_attribute(child, 'width')
            height = quadrant__numeric_attribute(child, 'height')
            if x is not None and y is not None and (width is not None) and (height is not None):
                rect_bounds.append((x, y, width, height))
                break
    if len(rect_bounds) < 4:
        return None
    min_x = min((x for x, _, _, _ in rect_bounds))
    min_y = min((y for _, y, _, _ in rect_bounds))
    max_x = max((x + width for x, _, width, _ in rect_bounds))
    max_y = max((y + height for _, y, _, height in rect_bounds))
    return (min_x, min_y, max_x, max_y)
def quadrant__quadrant_for_position(position: tuple[float, float], bounds: tuple[float, float, float, float] | None) -> int | None:
    if bounds is None:
        return None
    min_x, min_y, max_x, max_y = bounds
    x, y = position
    mid_x = min_x + (max_x - min_x) / 2
    mid_y = min_y + (max_y - min_y) / 2
    if x >= mid_x and y < mid_y:
        return 1
    if x < mid_x and y < mid_y:
        return 2
    if x < mid_x and y >= mid_y:
        return 3
    return 4
def quadrant__discover_quadrant_chart_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    candidates: list[Candidate] = []
    bounds = quadrant__quadrant_rect_bounds(root)
    for element in root.iter():
        if local_name(element.tag) != 'g' or not has_lower_class(element, 'data-point'):
            continue
        position = quadrant__first_circle_position(element)
        quadrant = quadrant__quadrant_for_position(position, bounds) if position is not None else None
        extra_classes = ['quadrant-chart-point']
        if quadrant is not None:
            extra_classes.append(f'quadrant-{quadrant}')
        candidates.append(Candidate(element=element, role='node', dom_index=dom_order[element], element_id=element.get('id', ''), classes=quadrant__add_classes(class_tokens(element), extra_classes), text=collapsed_text(element), branch_index=quadrant - 1 if quadrant is not None else None))
    return candidates
def quadrant__candidate_has_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def quadrant__point_position(candidate: Candidate) -> tuple[float, float] | None:
    return quadrant__first_circle_position(candidate.element)
def quadrant__quadrant_index(candidate: Candidate) -> int:
    for index in range(1, 5):
        if quadrant__candidate_has_class(candidate, f'quadrant-{index}'):
            return index
    return 99
def quadrant__point_order_key(candidate: Candidate) -> tuple[int, float, float, int]:
    position = quadrant__point_position(candidate)
    if position is None:
        return (quadrant__quadrant_index(candidate), 0.0, 0.0, candidate.dom_index)
    x, y = position
    return (quadrant__quadrant_index(candidate), y, x, candidate.dom_index)
def quadrant__reading_point_order_key(candidate: Candidate) -> tuple[int, float, float, int]:
    position = quadrant__point_position(candidate)
    quadrant_order = {2: 0, 1: 1, 3: 2, 4: 3}
    quadrant = quadrant__quadrant_index(candidate)
    if position is None:
        return (quadrant_order.get(quadrant, 99), 0.0, 0.0, candidate.dom_index)
    x, y = position
    return (quadrant_order.get(quadrant, 99), y, x, candidate.dom_index)
def quadrant__plan_quadrant_chart_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    ordered = sorted(candidates, key=quadrant__reading_point_order_key if effective_animation == 'quadrant-points' else quadrant__point_order_key)
    if not ordered:
        return []
    animation = 'sequence' if effective_animation == 'quadrant-points' else effective_animation
    duration = float(args.duration_ms)
    if args.total_ms is not None and len(ordered) > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        stagger = max(0.0, available / (len(ordered) - 1))
    else:
        stagger = float(args.stagger_ms)
    for index, candidate in enumerate(ordered):
        quadrant = quadrant__quadrant_index(candidate)
        candidate.effect = effect_for(animation, candidate.role)
        candidate.delay_ms = float(args.initial_delay_ms) + index * stagger
        candidate.duration_ms = duration
        candidate.stage = index
        candidate.branch_index = quadrant - 1 if quadrant <= 4 else None
    return ordered

# --- radar ---

radar__RADAR_BASE_CLASSES = {'radargraticule', 'radaraxisline', 'radaraxislabel', 'radarlegendtext', 'radartitle'}
def radar__is_radar_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'radar'
def radar__add_classes(classes: list[str], extra_classes: Iterable[str]) -> list[str]:
    result = [*classes]
    for extra_class in extra_classes:
        if extra_class not in result:
            result.append(extra_class)
    return result
def radar__lower_classes(element: ET.Element) -> set[str]:
    return {token.lower() for token in class_tokens(element)}
def radar__class_prefix_number(classes: Iterable[str], prefix: str) -> int | None:
    prefix = prefix.lower()
    for token in classes:
        lower_token = token.lower()
        if not lower_token.startswith(prefix):
            continue
        suffix = lower_token[len(prefix):]
        if re.fullmatch('\\d+', suffix):
            return int(suffix)
    return None
def radar__is_radar_curve(element: ET.Element) -> bool:
    return radar__class_prefix_number(class_tokens(element), 'radarcurve-') is not None
def radar__is_radar_legend_box(element: ET.Element) -> bool:
    return radar__class_prefix_number(class_tokens(element), 'radarlegendbox-') is not None
def radar__is_radar_base_element(element: ET.Element) -> bool:
    classes = radar__lower_classes(element)
    return bool(classes & radar__RADAR_BASE_CLASSES) or radar__is_radar_legend_box(element)
def radar__descendant_classes(element: ET.Element) -> list[str]:
    seen: set[str] = set()
    classes: list[str] = []
    for child in element.iter():
        for token in class_tokens(child):
            if token not in seen:
                seen.add(token)
                classes.append(token)
    return classes
def radar__is_legend_group(element: ET.Element) -> bool:
    if local_name(element.tag) != 'g':
        return False
    if any((child is not element and radar__is_radar_curve(child) for child in element.iter())):
        return False
    return any((child is not element and ('radarlegendtext' in radar__lower_classes(child) or radar__is_radar_legend_box(child)) for child in element.iter()))
def radar__has_ancestor_in(element: ET.Element, selected: set[ET.Element], parent_map: dict[ET.Element, ET.Element]) -> bool:
    return any((parent in selected for parent in ancestors(element, parent_map)))
def radar__legend_series_index(element: ET.Element) -> int | None:
    return radar__class_prefix_number(radar__descendant_classes(element), 'radarlegendbox-')
def radar__radar_base_role(element: ET.Element) -> str:
    classes = radar__lower_classes(element)
    if local_name(element.tag) == 'text' or 'radartitle' in classes or 'radaraxislabel' in classes:
        return 'label'
    if 'radarlegendtext' in classes or radar__is_radar_legend_box(element) or radar__is_legend_group(element):
        return 'label'
    return 'item'
def radar__discover_radar_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    parent_map = build_parent_map(root)
    candidates: list[Candidate] = []
    selected_legend_groups: set[ET.Element] = set()
    for element in root.iter():
        if radar__is_legend_group(element):
            series_index = radar__legend_series_index(element)
            extra_classes = ['radar-legend']
            if series_index is not None:
                extra_classes.append(f'radar-series-{series_index}')
            selected_legend_groups.add(element)
            candidates.append(Candidate(element=element, role='label', dom_index=dom_order[element], element_id=element.get('id', ''), classes=radar__add_classes(radar__descendant_classes(element), extra_classes), text=collapsed_text(element), branch_index=series_index))
    for element in root.iter():
        if radar__has_ancestor_in(element, selected_legend_groups, parent_map):
            continue
        series_index = radar__class_prefix_number(class_tokens(element), 'radarcurve-')
        if series_index is not None:
            candidates.append(Candidate(element=element, role='node', dom_index=dom_order[element], element_id=element.get('id', ''), classes=radar__add_classes(class_tokens(element), ['radar-curve', f'radar-series-{series_index}', 'radar-z-layer']), text=collapsed_text(element), branch_index=series_index))
            continue
        if not radar__is_radar_base_element(element):
            continue
        candidates.append(Candidate(element=element, role=radar__radar_base_role(element), dom_index=dom_order[element], element_id=element.get('id', ''), classes=class_tokens(element), text=collapsed_text(element)))
    return candidates
def radar__is_radar_curve_candidate(candidate: Candidate) -> bool:
    return any((token.lower() == 'radar-curve' for token in candidate.classes))
def radar__is_circle_graticule_candidate(candidate: Candidate) -> bool:
    return local_name(candidate.element.tag) == 'circle' and 'radargraticule' in {token.lower() for token in candidate.classes}
def radar__radar_base_group(candidate: Candidate) -> int:
    classes = {token.lower() for token in candidate.classes}
    if 'radartitle' in classes or 'radargraticule' in classes:
        return 0
    if 'radaraxisline' in classes or 'radaraxislabel' in classes:
        return 1
    if 'radar-legend' in classes or 'radarlegendtext' in classes or any((token.startswith('radarlegendbox-') for token in classes)):
        return 2
    return 1
def radar__radar_curve_order_key(candidate: Candidate) -> tuple[int, int]:
    return (candidate.dom_index, candidate.branch_index if candidate.branch_index is not None else 999)
def radar__plan_radar_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    base_candidates = sorted([candidate for candidate in candidates if not radar__is_radar_curve_candidate(candidate)], key=lambda candidate: candidate.dom_index)
    curve_candidates = sorted([candidate for candidate in candidates if radar__is_radar_curve_candidate(candidate)], key=radar__radar_curve_order_key)
    ordered = [*base_candidates, *curve_candidates]
    if not ordered:
        return []
    duration = float(args.duration_ms)
    stage_count = (1 if base_candidates else 0) + len(curve_candidates)
    if args.total_ms is not None and stage_count > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        stage_gap = max(0.0, available / (stage_count - 1))
    else:
        stage_gap = duration + float(args.stagger_ms)
    stagger_base = effective_animation == 'radar-layers' and any((radar__is_circle_graticule_candidate(candidate) for candidate in base_candidates))
    if stagger_base:
        base_stage_count = 3 if base_candidates else 0
        for candidate in base_candidates:
            stage = radar__radar_base_group(candidate)
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = float(args.initial_delay_ms) + stage * float(args.stagger_ms)
            candidate.duration_ms = duration
            candidate.stage = stage
        first_curve_stage = base_stage_count
    else:
        first_curve_stage = 1 if base_candidates else 0
        for candidate in base_candidates:
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = float(args.initial_delay_ms)
            candidate.duration_ms = duration
            candidate.stage = 0
    for index, candidate in enumerate(curve_candidates):
        stage = first_curve_stage + index
        candidate.effect = effect_for(effective_animation, candidate.role)
        candidate.delay_ms = float(args.initial_delay_ms) + stage * stage_gap
        candidate.duration_ms = duration
        candidate.stage = stage
    return ordered

# --- requirement ---

def requirement__is_requirement_root(root: ET.Element) -> bool:
    role = normalized(root.get('aria-roledescription', ''))
    return role == 'requirement' or role == 'requirementdiagram'
def requirement__requirement_key(candidate: Candidate) -> str:
    value = candidate.element_id
    if value.startswith('my-svg-'):
        value = value.removeprefix('my-svg-')
    return normalized(value).replace('-', '_')
def requirement__relationship_parts(candidate: Candidate) -> tuple[str, str] | None:
    value = candidate.element.get('data-id', '') or candidate.element_id
    if value.startswith('my-svg-'):
        value = value.removeprefix('my-svg-')
    value = re.sub('-\\d+$', '', value)
    parts = value.split('-')
    if len(parts) < 2:
        return None
    return (normalized(parts[0]).replace('-', '_'), normalized(parts[1]).replace('-', '_'))
def requirement__nearest_node(point: tuple[float, float], nodes: list[Candidate], positions: dict[int, tuple[float, float]]) -> Candidate | None:
    if not nodes:
        return None
    return min(nodes, key=lambda candidate: squared_distance(point, positions[id(candidate)]))
def requirement__plan_requirement_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if args.animation != 'auto' or any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    node_candidates = [candidate for candidate in candidates if candidate.role == 'node']
    edge_candidates = [candidate for candidate in candidates if candidate.role == 'edge' and 'relationshipline' in {token.lower() for token in candidate.classes}]
    label_candidates = [candidate for candidate in candidates if candidate.role == 'label' and 'edgeLabel' in candidate.classes]
    positions = {id(candidate): position for candidate in node_candidates if (position := translate_position(candidate.element)) is not None}
    positioned_nodes = [candidate for candidate in node_candidates if id(candidate) in positions]
    if len(positioned_nodes) < 3 or not edge_candidates:
        return []
    node_by_key = {requirement__requirement_key(candidate): candidate for candidate in positioned_nodes}
    ordered_nodes = sorted(positioned_nodes, key=lambda candidate: (positions[id(candidate)][1], positions[id(candidate)][0], candidate.dom_index))
    node_stage = {id(candidate): index for index, candidate in enumerate(ordered_nodes)}
    edge_nodes: dict[int, tuple[Candidate, Candidate]] = {}
    for edge in edge_candidates:
        parts = requirement__relationship_parts(edge)
        endpoints: tuple[Candidate, Candidate] | None = None
        if parts is not None:
            source = node_by_key.get(parts[0])
            target = node_by_key.get(parts[1])
            if source is not None and target is not None:
                endpoints = (source, target)
        if endpoints is None:
            line_points = edge_endpoints(edge)
            if line_points is not None:
                source = requirement__nearest_node(line_points[0], positioned_nodes, positions)
                target = requirement__nearest_node(line_points[1], positioned_nodes, positions)
                if source is not None and target is not None:
                    endpoints = (source, target)
        if endpoints is not None:
            edge_nodes[id(edge)] = endpoints
    if not edge_nodes:
        return []
    sorted_edges = sorted(edge_candidates, key=lambda candidate: candidate.dom_index)
    edge_labels: dict[int, list[Candidate]] = {}
    paired_label_ids: set[int] = set()
    for label, edge in zip(sorted(label_candidates, key=lambda candidate: candidate.dom_index), sorted_edges):
        if id(edge) not in edge_nodes:
            continue
        edge_labels.setdefault(id(edge), []).append(label)
        paired_label_ids.add(id(label))
    stage_items: dict[int, list[Candidate]] = {index: [candidate] for index, candidate in enumerate(ordered_nodes)}
    for edge in sorted_edges:
        endpoints = edge_nodes.get(id(edge))
        if endpoints is None:
            continue
        source, target = endpoints
        source_stage = node_stage[id(source)]
        target_stage = node_stage[id(target)]
        stage = max(source_stage, target_stage)
        edge.source_index = source_stage
        edge.target_index = target_stage
        stage_items.setdefault(stage, []).append(edge)
        for label in edge_labels.get(id(edge), []):
            label.source_index = source_stage
            label.target_index = target_stage
            stage_items[stage].append(label)
    planned_ids = {id(candidate) for values in stage_items.values() for candidate in values} | paired_label_ids
    fallback_stage = len(stage_items)
    for candidate in candidates:
        if id(candidate) in planned_ids:
            continue
        candidate.effect = effect_for(effective_animation, candidate.role)
        stage_items.setdefault(fallback_stage, []).append(candidate)
        fallback_stage += 1
    return plan_staged_items_with_following_connections(stage_items, args, effective_animation)

# --- sankey ---

def sankey__is_sankey_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'sankey'
def sankey__has_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def sankey__element_has_class(element: ET.Element, token: str) -> bool:
    return token.lower() in {value.lower() for value in class_tokens(element)}
def sankey__has_ancestor_class(element: ET.Element, parent_map: dict[ET.Element, ET.Element], token: str) -> bool:
    return any((sankey__element_has_class(parent, token) for parent in ancestors(element, parent_map)))
def sankey__add_candidate(candidates: list[Candidate], element: ET.Element, role: str, dom_order: dict[ET.Element, int], extra_classes: Iterable[str]) -> None:
    classes = class_tokens(element)
    for extra_class in extra_classes:
        if extra_class not in classes:
            classes.append(extra_class)
    candidates.append(Candidate(element=element, role=role, dom_index=dom_order[element], element_id=element.get('id', ''), classes=classes, text=collapsed_text(element)))
def sankey__discover_sankey_candidates(root: ET.Element, parent_map: dict[ET.Element, ET.Element], dom_order: dict[ET.Element, int]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for element in root.iter():
        tag = local_name(element.tag)
        if tag == 'g' and sankey__element_has_class(element, 'node') and sankey__has_ancestor_class(element, parent_map, 'nodes'):
            sankey__add_candidate(candidates, element, 'node', dom_order, ['sankey-node'])
            continue
        if tag == 'path' and sankey__has_ancestor_class(element, parent_map, 'links'):
            sankey__add_candidate(candidates, element, 'edge', dom_order, ['sankey-link'])
            continue
        if tag == 'text' and sankey__has_ancestor_class(element, parent_map, 'node-labels'):
            sankey__add_candidate(candidates, element, 'label', dom_order, ['sankey-label'])
    return candidates
def sankey__numeric_attribute(element: ET.Element, name: str) -> float | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
def sankey__node_position(candidate: Candidate) -> tuple[float, float] | None:
    translated = translate_position(candidate.element)
    if translated is not None:
        return translated
    x = sankey__numeric_attribute(candidate.element, 'x')
    y = sankey__numeric_attribute(candidate.element, 'y')
    if x is not None and y is not None:
        return (x, y)
    return None
def sankey__label_position(candidate: Candidate) -> tuple[float, float] | None:
    x = sankey__numeric_attribute(candidate.element, 'x')
    y = sankey__numeric_attribute(candidate.element, 'y')
    if x is not None and y is not None:
        return (x, y)
    return sankey__node_position(candidate)
def sankey__link_start(candidate: Candidate) -> tuple[float, float] | None:
    endpoints = edge_endpoints(candidate)
    if endpoints is None:
        return None
    start, end = endpoints
    return start if start[0] <= end[0] else end
def sankey__link_columns(candidate: Candidate, column_x_values: list[float]) -> tuple[int, int] | None:
    endpoints = edge_endpoints(candidate)
    if endpoints is None:
        start = sankey__link_start(candidate)
        if start is None:
            return None
        column_index = sankey__nearest_column(start[0], column_x_values)
        return (column_index, column_index)
    start, end = endpoints
    source, target = (start, end) if start[0] <= end[0] else (end, start)
    return (sankey__nearest_column(source[0], column_x_values), sankey__nearest_column(target[0], column_x_values))
def sankey__nearest_column(x: float, column_x_values: list[float]) -> int:
    return min(range(len(column_x_values)), key=lambda index: abs(column_x_values[index] - x))
def sankey__plan_sankey_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    node_candidates = [candidate for candidate in candidates if sankey__has_class(candidate, 'sankey-node')]
    link_candidates = [candidate for candidate in candidates if sankey__has_class(candidate, 'sankey-link')]
    label_candidates = [candidate for candidate in candidates if sankey__has_class(candidate, 'sankey-label')]
    node_positions = {id(candidate): position for candidate in node_candidates if (position := sankey__node_position(candidate)) is not None}
    if not node_positions or not link_candidates:
        return []
    column_x_values = sorted({round(position[0], 3) for position in node_positions.values()})
    nodes_by_column: dict[int, list[Candidate]] = {index: [] for index in range(len(column_x_values))}
    for candidate in node_candidates:
        position = node_positions.get(id(candidate))
        if position is None:
            continue
        column_index = sankey__nearest_column(position[0], column_x_values)
        candidate.source_index = column_index
        nodes_by_column[column_index].append(candidate)
    labels_by_column: dict[int, list[Candidate]] = {index: [] for index in range(len(column_x_values))}
    for candidate in label_candidates:
        position = sankey__label_position(candidate)
        if position is None:
            continue
        column_index = sankey__nearest_column(position[0], column_x_values)
        candidate.source_index = column_index
        labels_by_column[column_index].append(candidate)
    links_by_column: dict[int, list[Candidate]] = {index: [] for index in range(len(column_x_values))}
    for candidate in link_candidates:
        columns = sankey__link_columns(candidate, column_x_values)
        if columns is None:
            continue
        source_column, target_column = columns
        candidate.source_index = source_column
        candidate.target_index = target_column
        link_column = source_column if args.animation == 'auto' else max(source_column, target_column)
        links_by_column[link_column].append(candidate)
    stages: list[list[Candidate]] = []
    for column_index in range(len(column_x_values)):
        column_nodes = sorted([*nodes_by_column[column_index], *labels_by_column[column_index]], key=lambda candidate: ((sankey__node_position(candidate) if candidate.role == 'node' else sankey__label_position(candidate)) or (0.0, 0.0), 0 if candidate.role == 'node' else 1, candidate.dom_index))
        if column_nodes:
            stages.append(column_nodes)
        column_links = sorted(links_by_column[column_index], key=lambda candidate: candidate.dom_index)
        if column_links:
            stages.append(column_links)
    if not stages:
        return []
    duration = float(args.duration_ms)
    minimum_stage_gap = duration + float(args.stagger_ms)
    if args.total_ms is not None and len(stages) > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        stage_gap = max(minimum_stage_gap, available / (len(stages) - 1))
    else:
        stage_gap = minimum_stage_gap
    planned: list[Candidate] = []
    for stage_index, stage in enumerate(stages):
        delay = float(args.initial_delay_ms) + stage_index * stage_gap
        for candidate in stage:
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = delay
            candidate.duration_ms = duration
            candidate.stage = stage_index
            planned.append(candidate)
    planned_ids = {id(candidate) for candidate in planned}
    for candidate in candidates:
        if id(candidate) in planned_ids:
            continue
        candidate.effect = effect_for(effective_animation, candidate.role)
        candidate.delay_ms = float(args.initial_delay_ms) + len(stages) * stage_gap
        candidate.duration_ms = duration
        candidate.stage = len(stages)
        planned.append(candidate)
    return planned

# --- sequence ---

def sequence__is_sequence_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'sequence'
def sequence__add_classes(classes: Iterable[str], extra_classes: Iterable[str]) -> list[str]:
    result = list(classes)
    for extra_class in extra_classes:
        if extra_class not in result:
            result.append(extra_class)
    return result
def sequence__has_class(element: ET.Element, token: str) -> bool:
    return token.lower() in {value.lower() for value in class_tokens(element)}
def sequence__discover_sequence_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    if not any((element.get('data-et', '') == 'control-structure' for element in root.iter())):
        return []
    parent_map = build_parent_map(root)
    selected: set[ET.Element] = set()
    candidates: list[Candidate] = []

    def already_selected(element: ET.Element) -> bool:
        return any((parent in selected for parent in ancestors(element, parent_map)))

    def add_candidate(element: ET.Element, role: str, extra_classes: Iterable[str]) -> None:
        if element in selected or already_selected(element):
            return
        selected.add(element)
        candidates.append(Candidate(element=element, role=role, dom_index=dom_order[element], element_id=element.get('id', ''), classes=sequence__add_classes(class_tokens(element), extra_classes), text=collapsed_text(element)))
    for element in root.iter():
        tag = local_name(element.tag)
        data_et = element.get('data-et', '')
        tokens = {token.lower() for token in class_tokens(element)}
        text = collapsed_text(element)
        if data_et == 'participant':
            add_candidate(element, 'actor', ['sequence-participant'])
            continue
        if tag == 'g' and 'actor-man' in tokens and ('actor-bottom' in tokens):
            add_candidate(element, 'actor', ['sequence-bottom-actor'])
            continue
        if tag in {'rect', 'text'} and 'actor-bottom' in tokens:
            add_candidate(element, 'actor', ['sequence-bottom-actor'])
            continue
        if tag == 'text' and 'actor-box' in tokens:
            center = element_center(element, parent_map)
            if center is not None and center[1] > 200:
                add_candidate(element, 'actor', ['sequence-bottom-actor'])
            continue
        if data_et == 'control-structure':
            add_candidate(element, 'cluster', ['sequence-control'])
            continue
        if tag == 'g' and text in {'Front door', 'Platform'}:
            add_candidate(element, 'cluster', ['sequence-box'])
            continue
        if data_et == 'message' or 'messageline0' in tokens or 'messageline1' in tokens:
            add_candidate(element, 'edge', ['sequence-message-line'])
            continue
        if 'messagetext' in tokens:
            add_candidate(element, 'label', ['sequence-message-text'])
            continue
        if 'sequencenumber' in tokens:
            add_candidate(element, 'label', ['sequence-number'])
            continue
        if any((token.startswith('activation') for token in tokens)):
            add_candidate(element, 'item', ['sequence-activation'])
    return candidates
def sequence__candidate_center(candidate: Candidate, parent_map: dict[ET.Element, ET.Element]) -> tuple[float, float] | None:
    return element_center(candidate.element, parent_map)
def sequence__candidate_bounds(candidate: Candidate, parent_map: dict[ET.Element, ET.Element]) -> tuple[float, float, float, float] | None:
    return element_bounds(candidate.element, parent_map)
def sequence__has_candidate_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def sequence__plan_sequence_candidates(candidates: list[Candidate], root: ET.Element, args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if args.animation != 'auto' or any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    parent_map = build_parent_map(root)
    actor_candidates = [candidate for candidate in candidates if candidate.role == 'actor']
    box_candidates = [candidate for candidate in candidates if candidate.role == 'cluster' and sequence__has_candidate_class(candidate, 'sequence-box')]
    control_candidates = [candidate for candidate in candidates if candidate.role == 'cluster' and sequence__has_candidate_class(candidate, 'sequence-control')]
    message_lines = [candidate for candidate in candidates if candidate.role == 'edge' and sequence__has_candidate_class(candidate, 'sequence-message-line')]
    message_labels = [candidate for candidate in candidates if candidate.role == 'label' and sequence__has_candidate_class(candidate, 'sequence-message-text')]
    number_labels = [candidate for candidate in candidates if candidate.role == 'label' and sequence__has_candidate_class(candidate, 'sequence-number')]
    activation_candidates = [candidate for candidate in candidates if sequence__has_candidate_class(candidate, 'sequence-activation')]
    line_positions = {id(candidate): center for candidate in message_lines if (center := sequence__candidate_center(candidate, parent_map)) is not None}
    if not actor_candidates or not line_positions:
        return []
    actor_positions = {id(candidate): center for candidate in actor_candidates if (center := sequence__candidate_center(candidate, parent_map)) is not None}
    if not actor_positions:
        return []
    top_y = min((position[1] for position in actor_positions.values()))
    actor_row_tolerance = 90.0
    first_stage = sorted([*box_candidates, *actor_candidates], key=lambda candidate: (1 if sequence__has_candidate_class(candidate, 'sequence-bottom-actor') else 0, abs((actor_positions.get(id(candidate)) or sequence__candidate_center(candidate, parent_map) or (0, 0))[1] - top_y) > actor_row_tolerance, (sequence__candidate_center(candidate, parent_map) or (0.0, 0.0))[0], candidate.dom_index))
    sorted_lines = sorted(message_lines, key=lambda candidate: (line_positions[id(candidate)][1], candidate.dom_index))

    def paired_line(candidate: Candidate) -> Candidate | None:
        center = sequence__candidate_center(candidate, parent_map)
        if center is None:
            return None
        if sequence__has_candidate_class(candidate, 'sequence-message-text'):
            following_lines = [line for line in sorted_lines if line_positions[id(line)][1] >= center[1] - 1.0]
            if following_lines:
                return min(following_lines, key=lambda line: (line_positions[id(line)][1], abs(line_positions[id(line)][0] - center[0]), line.dom_index))
        return min(sorted_lines, key=lambda line: abs(line_positions[id(line)][1] - center[1]))
    labels_by_line: dict[int, list[Candidate]] = {}
    paired_label_ids: set[int] = set()
    for label in [*message_labels, *number_labels]:
        line = paired_line(label)
        if line is None:
            continue
        labels_by_line.setdefault(id(line), []).append(label)
        paired_label_ids.add(id(label))
    control_bounds = {id(candidate): bounds for candidate in control_candidates if (bounds := sequence__candidate_bounds(candidate, parent_map)) is not None}
    control_first_line: dict[int, int] = {}
    for control in control_candidates:
        bounds = control_bounds.get(id(control))
        if bounds is None:
            continue
        _min_x, min_y, _max_x, max_y = bounds
        contained = [index for index, line in enumerate(sorted_lines) if min_y - 8 <= line_positions[id(line)][1] <= max_y + 8]
        if contained:
            control_first_line[id(control)] = min(contained)
    stages: list[list[Candidate]] = []
    if first_stage:
        stages.append(first_stage)
    activation_added = False
    added_control_ids: set[int] = set()
    for line_index, line in enumerate(sorted_lines):
        controls = [control for control in control_candidates if control_first_line.get(id(control)) == line_index and id(control) not in added_control_ids]
        if controls:
            stages.append(sorted(controls, key=lambda candidate: candidate.dom_index))
            added_control_ids.update((id(candidate) for candidate in controls))
        step = [line, *sorted(labels_by_line.get(id(line), []), key=lambda candidate: candidate.dom_index)]
        if not activation_added and activation_candidates:
            step = [*activation_candidates, *step]
            activation_added = True
        stages.append(step)
    leftovers = [candidate for candidate in candidates if id(candidate) not in {id(item) for stage in stages for item in stage} and id(candidate) not in paired_label_ids]
    if leftovers:
        stages.append(sorted(leftovers, key=lambda candidate: candidate.dom_index))
    duration = float(args.duration_ms)
    if args.total_ms is not None and len(stages) > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        stage_gap = max(duration + float(args.stagger_ms), available / (len(stages) - 1))
    else:
        stage_gap = duration + float(args.stagger_ms)
    planned: list[Candidate] = []
    for index, stage in enumerate(stages):
        delay = float(args.initial_delay_ms) + index * stage_gap
        for candidate in stage:
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = delay
            candidate.duration_ms = duration
            candidate.stage = index
            planned.append(candidate)
    return planned

# --- state ---

def state__is_state_root(root: ET.Element) -> bool:
    role = normalized(root.get('aria-roledescription', ''))
    return role == 'statediagram' or 'statediagram' in {token.lower() for token in class_tokens(root)}
def state__state_primary_axis(root: ET.Element) -> int:
    viewbox = parse_viewbox(root)
    if viewbox is None:
        return 0
    return 0 if viewbox[2] >= viewbox[3] else 1
def state__plan_state_candidates(candidates: list[Candidate], root: ET.Element, args: argparse.Namespace) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    axis = state__state_primary_axis(root)
    secondary_axis = 1 - axis
    duration = float(args.duration_ms)
    tolerance = 1.0
    node_candidates = [candidate for candidate in candidates if candidate.role == 'node']
    edge_candidates = [candidate for candidate in candidates if candidate.role == 'edge']
    label_candidates = [candidate for candidate in candidates if candidate.role == 'label' and 'edgeLabel' in candidate.classes]
    cluster_candidates = [candidate for candidate in candidates if candidate.role == 'item' and 'statediagram-cluster' in {token.lower() for token in candidate.classes}]
    if cluster_candidates:
        parent_map = build_parent_map(root)
        visual_candidates = [*cluster_candidates, *node_candidates]

        def visual_bounds_for(candidate: Candidate) -> tuple[float, float, float, float] | None:
            return element_bounds(candidate.element, parent_map, include_path_points=True)

        def visual_center_for(candidate: Candidate) -> tuple[float, float] | None:
            bounds = visual_bounds_for(candidate)
            if bounds is None:
                return element_center(candidate.element, parent_map)
            min_x, min_y, max_x, max_y = bounds
            return (min_x + (max_x - min_x) / 2, min_y + (max_y - min_y) / 2)
        node_position_cache = {id(candidate): position for candidate in node_candidates if (position := visual_center_for(candidate)) is not None}

        def cluster_position(candidate: Candidate) -> tuple[float, float] | None:
            bounds = visual_bounds_for(candidate)
            descendants = [node_position_cache[id(node)] for node in node_candidates if id(node) in node_position_cache and any((parent is candidate.element for parent in ancestors(node.element, parent_map)))]
            if descendants and bounds is not None:
                x = sum((point[0] for point in descendants)) / len(descendants)
                return (x, bounds[1])
            if bounds is not None:
                return (bounds[0] + (bounds[2] - bounds[0]) / 2, bounds[1])
            return element_center(candidate.element, parent_map)
        visual_positions: dict[int, tuple[float, float]] = {}
        visual_bounds: dict[int, tuple[float, float, float, float]] = {}
        for candidate in visual_candidates:
            bounds = visual_bounds_for(candidate)
            if bounds is not None:
                visual_bounds[id(candidate)] = bounds
            if candidate.role == 'item':
                position = cluster_position(candidate)
            else:
                position = node_position_cache.get(id(candidate))
            if position is not None:
                visual_positions[id(candidate)] = position
        positioned_visual = [candidate for candidate in visual_candidates if id(candidate) in visual_positions]
        if positioned_visual and edge_candidates:

            def root_start_rank(candidate: Candidate) -> int:
                return -1 if 'root_start' in candidate.element_id else 0

            def primary_bucket(candidate: Candidate) -> int:
                return round(visual_positions[id(candidate)][axis] / 32.0)
            ordered_visual = sorted(positioned_visual, key=lambda candidate: (root_start_rank(candidate), primary_bucket(candidate), visual_positions[id(candidate)][secondary_axis], visual_positions[id(candidate)][axis], 0 if candidate.role == 'item' else 1, candidate.dom_index))
            visual_stage = {id(candidate): index for index, candidate in enumerate(ordered_visual)}

            def bounds_distance(point: tuple[float, float], bounds: tuple[float, float, float, float]) -> float:
                min_x, min_y, max_x, max_y = bounds
                dx = max(min_x - point[0], 0.0, point[0] - max_x)
                dy = max(min_y - point[1], 0.0, point[1] - max_y)
                return dx * dx + dy * dy

            def bounds_area(bounds: tuple[float, float, float, float]) -> float:
                min_x, min_y, max_x, max_y = bounds
                return max(0.0, max_x - min_x) * max(0.0, max_y - min_y)

            def nearest_visual_candidate(point: tuple[float, float], options: list[Candidate]) -> Candidate | None:
                if not options:
                    return None
                close_distance = 16.0

                def visual_distance_key(candidate: Candidate) -> tuple[float, float, float, int]:
                    distance = bounds_distance(point, visual_bounds[id(candidate)]) if id(candidate) in visual_bounds else squared_distance(point, visual_positions[id(candidate)])
                    distance_bucket = 0.0 if distance <= close_distance else distance
                    return (distance_bucket, bounds_area(visual_bounds[id(candidate)]) if id(candidate) in visual_bounds else float('inf'), squared_distance(point, visual_positions[id(candidate)]), candidate.dom_index)
                return min(options, key=visual_distance_key)
            edge_visual_nodes: dict[int, tuple[Candidate, Candidate]] = {}
            for edge in edge_candidates:
                endpoints = edge_endpoints(edge)
                if endpoints is None:
                    continue
                start = translated_point(edge.element, parent_map, endpoints[0])
                end = translated_point(edge.element, parent_map, endpoints[1])
                source = nearest_visual_candidate(start, positioned_visual)
                target = nearest_visual_candidate(end, positioned_visual)
                if source is not None and target is source:
                    alternatives = [candidate for candidate in positioned_visual if candidate is not source]
                    replacement = nearest_visual_candidate(end, alternatives)
                    if replacement is not None:
                        target = replacement
                if source is None or target is None:
                    continue
                edge_visual_nodes[id(edge)] = (source, target)
            if edge_visual_nodes:
                sorted_edges = sorted(edge_candidates, key=lambda candidate: candidate.dom_index)
                sorted_labels = sorted(label_candidates, key=lambda candidate: candidate.dom_index)
                edge_labels: dict[int, list[Candidate]] = {}
                paired_labels: set[int] = set()
                for index, label in enumerate(sorted_labels):
                    if index >= len(sorted_edges):
                        break
                    edge = sorted_edges[index]
                    if id(edge) not in edge_visual_nodes:
                        continue
                    edge_labels.setdefault(id(edge), []).append(label)
                    paired_labels.add(id(label))
                stage_items: dict[int, list[Candidate]] = {index: [candidate] for index, candidate in enumerate(ordered_visual)}
                for edge in sorted_edges:
                    endpoints = edge_visual_nodes.get(id(edge))
                    if endpoints is None:
                        continue
                    source, target = endpoints
                    source_stage = visual_stage[id(source)]
                    target_stage = visual_stage[id(target)]
                    stage = max(source_stage, target_stage)
                    edge.source_index = source_stage
                    edge.target_index = target_stage
                    stage_items.setdefault(stage, []).append(edge)
                    for label in edge_labels.get(id(edge), []):
                        label.source_index = source_stage
                        label.target_index = target_stage
                        stage_items[stage].append(label)
                planned_ids = {id(candidate) for values in stage_items.values() for candidate in values} | paired_labels
                fallback_stage = len(stage_items)
                for candidate in candidates:
                    if id(candidate) in planned_ids:
                        continue
                    stage_items.setdefault(fallback_stage, []).append(candidate)
                    fallback_stage += 1
                return plan_staged_items_with_following_connections(stage_items, args, 'state-flow')
    positions = {id(candidate): position for candidate in [*node_candidates, *label_candidates] if (position := translate_position(candidate.element)) is not None}
    positioned_nodes = [candidate for candidate in node_candidates if id(candidate) in positions]
    if not positioned_nodes or not edge_candidates:
        return []
    edge_nodes: dict[int, tuple[Candidate | None, Candidate | None]] = {}
    edge_keys: dict[int, tuple[float, float, float, int]] = {}
    node_order = {id(candidate): index for index, candidate in enumerate(sorted(positioned_nodes, key=lambda candidate: (positions[id(candidate)][axis], positions[id(candidate)][secondary_axis], candidate.dom_index)))}
    for edge in edge_candidates:
        endpoints = edge_endpoints(edge)
        if endpoints is None:
            continue
        source = nearest_candidate(endpoints[0], positioned_nodes, positions)
        target = nearest_candidate(endpoints[1], positioned_nodes, positions)
        if source is None or target is None:
            continue
        source_position = positions[id(source)]
        target_position = positions[id(target)]
        source_primary = source_position[axis]
        target_primary = target_position[axis]
        target_secondary = target_position[secondary_axis]
        source_secondary = source_position[secondary_axis]
        if target_primary >= source_primary - tolerance:
            key = (target_primary, target_secondary, 0.0, edge.dom_index)
        else:
            key = (source_primary, source_secondary, 2.0, edge.dom_index)
        edge_nodes[id(edge)] = (source, target)
        edge_keys[id(edge)] = key
        edge.source_index = node_order.get(id(source))
        edge.target_index = node_order.get(id(target))
    if not edge_keys:
        return []
    sorted_edges = sorted(edge_candidates, key=lambda candidate: candidate.dom_index)
    sorted_labels = sorted(label_candidates, key=lambda candidate: candidate.dom_index)
    edge_labels: dict[int, list[Candidate]] = {}
    paired_labels: set[int] = set()
    for index, label in enumerate(sorted_labels):
        if index >= len(sorted_edges):
            break
        edge = sorted_edges[index]
        if id(edge) not in edge_keys:
            continue
        edge_labels.setdefault(id(edge), []).append(label)
        paired_labels.add(id(label))
    node_sort_key = {id(candidate): (positions[id(candidate)][axis], positions[id(candidate)][secondary_axis], candidate.dom_index) for candidate in positioned_nodes}
    incoming_node_ids = {id(target) for source, target in edge_nodes.values() if source is not None and target is not None and (source is not target)}
    seed_nodes = [candidate for candidate in positioned_nodes if id(candidate) not in incoming_node_ids] or [min(positioned_nodes, key=lambda candidate: node_sort_key[id(candidate)])]
    ordered_reveal_items: list[Candidate] = []
    reveal_ids: set[int] = set()
    visible_node_ids: set[int] = set()
    revealed_edge_ids: set[int] = set()

    def add_reveal(candidate: Candidate) -> None:
        if id(candidate) in reveal_ids:
            return
        ordered_reveal_items.append(candidate)
        reveal_ids.add(id(candidate))
        if candidate.role == 'node':
            visible_node_ids.add(id(candidate))
    for node in sorted(seed_nodes, key=lambda candidate: node_sort_key[id(candidate)]):
        add_reveal(node)

    def dynamic_edge_key(candidate: Candidate) -> tuple[int, float, float, float, int]:
        _source, target = edge_nodes.get(id(candidate), (None, None))
        target_is_visible = target is None or id(target) in visible_node_ids
        return (1 if target_is_visible else 0, *edge_keys[id(candidate)])
    while len(revealed_edge_ids) < len(edge_keys):
        eligible_edges = [edge for edge in edge_candidates if id(edge) in edge_keys and id(edge) not in revealed_edge_ids and (edge_nodes[id(edge)][0] is not None) and (id(edge_nodes[id(edge)][0]) in visible_node_ids)]
        if eligible_edges:
            for edge in sorted(eligible_edges, key=dynamic_edge_key):
                _source, target = edge_nodes.get(id(edge), (None, None))
                if target is not None and id(target) not in visible_node_ids:
                    add_reveal(target)
                add_reveal(edge)
                revealed_edge_ids.add(id(edge))
            continue
        unseen_nodes = [node for node in positioned_nodes if id(node) not in visible_node_ids]
        if unseen_nodes:
            add_reveal(min(unseen_nodes, key=lambda candidate: node_sort_key[id(candidate)]))
            continue
        for edge in sorted([edge for edge in edge_candidates if id(edge) in edge_keys and id(edge) not in revealed_edge_ids], key=lambda candidate: edge_keys[id(candidate)]):
            add_reveal(edge)
            revealed_edge_ids.add(id(edge))
    for candidate in candidates:
        if candidate.role == 'label' and id(candidate) in paired_labels:
            continue
        if id(candidate) in reveal_ids:
            continue
        add_reveal(candidate)
    state_dwell_overrides = parse_keyed_number_entries(args.state_dwell, '--state-dwell')

    def state_dwell(candidate: Candidate) -> float:
        if candidate.role != 'node':
            return 0.0
        return state_dwell_for_candidate(candidate, float(args.state_dwell_ms), state_dwell_overrides)
    step_gap = duration + float(args.stagger_ms)
    if args.total_ms is not None and len(ordered_reveal_items) > 1:
        dwell_before_last = sum((state_dwell(candidate) for candidate in ordered_reveal_items[:-1]))
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration - dwell_before_last
        step_gap = max(step_gap, available / (len(ordered_reveal_items) - 1))
    planned: list[Candidate] = []
    cumulative_state_dwell = 0.0
    for index, candidate in enumerate(ordered_reveal_items):
        candidate.effect = effect_for('state-flow', candidate.role)
        candidate.delay_ms = float(args.initial_delay_ms) + index * step_gap + cumulative_state_dwell
        candidate.duration_ms = duration
        candidate.stage = index
        planned.append(candidate)
        if candidate.role == 'edge':
            source, target = edge_nodes.get(id(candidate), (None, None))
            if source is not None:
                candidate.source_index = node_order.get(id(source))
            if target is not None:
                candidate.target_index = node_order.get(id(target))
            for label in edge_labels.get(id(candidate), []):
                label.effect = effect_for('state-flow', label.role)
                label.delay_ms = candidate.delay_ms
                label.duration_ms = duration
                label.stage = index
                label.source_index = candidate.source_index
                label.target_index = candidate.target_index
                planned.append(label)
        cumulative_state_dwell += state_dwell(candidate)
    return planned

# --- timeline ---

def timeline__is_timeline_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'timeline'
def timeline__discover_timeline_candidates(root: ET.Element, parent_map: dict[ET.Element, ET.Element], dom_order: dict[ET.Element, int]) -> list[Candidate]:
    selected: set[ET.Element] = set()
    candidates: list[Candidate] = []

    def add_candidate(element: ET.Element, role: str, extra_classes: Iterable[str]=()) -> None:
        if element in selected:
            return
        selected.add(element)
        classes = class_tokens(element)
        for extra_class in extra_classes:
            if extra_class not in classes:
                classes.append(extra_class)
        candidates.append(Candidate(element=element, role=role, dom_index=dom_order[element], element_id=element.get('id', ''), classes=classes, text=collapsed_text(element)))
    for element in root.iter():
        tag = local_name(element.tag)
        lower_tokens = {token.lower() for token in class_tokens(element)}
        if 'taskwrapper' in lower_tokens:
            add_candidate(element, 'label', ['timeline-date'])
            continue
        if 'eventwrapper' in lower_tokens:
            add_candidate(element, 'item', ['timeline-event'])
            continue
        if 'linewrapper' in lower_tokens:
            for child in element:
                if local_name(child.tag) == 'line':
                    add_candidate(child, 'edge', ['lineWrapper', 'timeline-line'])
            continue
        if tag == 'text' and collapsed_text(element):
            if not ancestor_has_class_fragment(element, parent_map, 'timeline-node'):
                add_candidate(element, 'label', ['timeline-title'])
            continue
        if tag != 'g' or 'timeline-node' in lower_tokens or lower_tokens:
            continue
        if ancestor_has_class_fragment(element, parent_map, 'taskWrapper') or ancestor_has_class_fragment(element, parent_map, 'eventWrapper'):
            continue
        if collapsed_text(element) and any((has_lower_class(child, 'timeline-node') for child in element)):
            add_candidate(element, 'label', ['timeline-section-title'])
    return candidates
def timeline__numeric_attribute(element: ET.Element, name: str) -> float | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
def timeline__candidate_has_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def timeline__first_node_line_center_x(element: ET.Element) -> float | None:
    for child in element.iter():
        if local_name(child.tag) != 'line' or not has_class_fragment(child, 'node-line'):
            continue
        x1 = timeline__numeric_attribute(child, 'x1')
        x2 = timeline__numeric_attribute(child, 'x2')
        if x1 is not None and x2 is not None:
            return (x1 + x2) / 2
    return None
def timeline__first_text_position(element: ET.Element) -> tuple[float, float] | None:
    for child in element.iter():
        if local_name(child.tag) != 'text':
            continue
        x = timeline__numeric_attribute(child, 'x')
        y = timeline__numeric_attribute(child, 'y')
        if x is not None and y is not None:
            return (x, y)
    return None
def timeline__timeline_candidate_position(candidate: Candidate) -> tuple[float, float] | None:
    if candidate.role == 'edge':
        endpoints = edge_endpoints(candidate)
        if endpoints is None:
            return None
        start, end = endpoints
        return (min(start[0], end[0]), min(start[1], end[1]))
    translated = translate_position(candidate.element)
    if translated is not None:
        center_x = timeline__first_node_line_center_x(candidate.element)
        if center_x is not None:
            return (translated[0] + center_x, translated[1])
        return translated
    if local_name(candidate.element.tag) == 'text':
        x = timeline__numeric_attribute(candidate.element, 'x')
        y = timeline__numeric_attribute(candidate.element, 'y')
        if x is not None and y is not None:
            return (x, y)
    return timeline__first_text_position(candidate.element)
def timeline__timeline_dynamic_key(candidate: Candidate) -> tuple[int, float, int, float, int]:
    position = timeline__timeline_candidate_position(candidate)
    if position is None:
        return (1, 0.0, 0 if candidate.role == 'edge' else 1, 0.0, candidate.dom_index)
    return (0, position[0], 0 if candidate.role == 'edge' else 1, position[1], candidate.dom_index)
def timeline__plan_timeline_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    if args.animation == 'auto':
        static_labels = sorted([candidate for candidate in candidates if timeline__candidate_has_class(candidate, 'timeline-title')], key=lambda candidate: candidate.dom_index)
        static_ids = {id(candidate) for candidate in static_labels}

        def auto_dynamic_key(candidate: Candidate) -> tuple[int, float, int, float, int]:
            position = timeline__timeline_candidate_position(candidate)
            if position is None:
                return (1, 0.0, 99, 0.0, candidate.dom_index)
            if timeline__candidate_has_class(candidate, 'timeline-section-title'):
                role_rank = 0
                effective_x = position[0] - 200.0
            elif timeline__candidate_has_class(candidate, 'timeline-date'):
                role_rank = 1
                effective_x = position[0]
            elif candidate.role == 'edge':
                role_rank = 2
                effective_x = position[0]
            else:
                role_rank = 3
                effective_x = position[0]
            return (0, effective_x, role_rank, position[1], candidate.dom_index)
        dynamic_candidates = sorted([candidate for candidate in candidates if id(candidate) not in static_ids], key=auto_dynamic_key)
        if not static_labels and (not dynamic_candidates):
            return []
        for candidate in static_labels:
            candidate.effect = 'none'
            candidate.delay_ms = 0.0
            candidate.duration_ms = 0.0
        duration = float(args.duration_ms)
        if args.total_ms is not None and len(dynamic_candidates) > 1:
            available = float(args.total_ms) - float(args.initial_delay_ms) - duration
            stagger = max(duration + float(args.stagger_ms), available / (len(dynamic_candidates) - 1))
        else:
            stagger = float(args.stagger_ms)
        for index, candidate in enumerate(dynamic_candidates):
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = float(args.initial_delay_ms) + index * stagger
            candidate.duration_ms = duration
            candidate.stage = index
        return [*static_labels, *dynamic_candidates]
    static_labels = sorted([candidate for candidate in candidates if timeline__candidate_has_class(candidate, 'timeline-title') or timeline__candidate_has_class(candidate, 'timeline-section-title') or timeline__candidate_has_class(candidate, 'timeline-date')], key=lambda candidate: (timeline__timeline_candidate_position(candidate) or (0.0, 0.0), candidate.dom_index))
    static_ids = {id(candidate) for candidate in static_labels}
    dynamic_candidates = sorted([candidate for candidate in candidates if id(candidate) not in static_ids], key=timeline__timeline_dynamic_key)
    if not static_labels and (not dynamic_candidates):
        return []
    for candidate in static_labels:
        candidate.effect = 'none'
        candidate.delay_ms = 0.0
        candidate.duration_ms = 0.0
    duration = float(args.duration_ms)
    if args.total_ms is not None and len(dynamic_candidates) > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        stagger = max(0.0, available / (len(dynamic_candidates) - 1))
    else:
        stagger = float(args.stagger_ms)
    for index, candidate in enumerate(dynamic_candidates):
        candidate.effect = effect_for(effective_animation, candidate.role)
        candidate.delay_ms = float(args.initial_delay_ms) + index * stagger
        candidate.duration_ms = duration
        candidate.stage = index
    return [*static_labels, *dynamic_candidates]

# --- treeview ---

treeview__POSITION_TOLERANCE = 0.01
@dataclass
class treeview__TreeViewStep:
    depth: int
    y: float
    order: int
    connection_only: bool = False
    candidates: list[Candidate] = field(default_factory=list)
def treeview__is_treeview_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'treeview'
def treeview__numeric_attribute(element: ET.Element, name: str) -> float | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
def treeview__candidate_has_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def treeview__label_position(candidate: Candidate) -> tuple[float, float] | None:
    x = treeview__numeric_attribute(candidate.element, 'x')
    y = treeview__numeric_attribute(candidate.element, 'y')
    if x is None or y is None:
        return None
    return (x, y)
def treeview__line_coordinates(candidate: Candidate) -> tuple[float, float, float, float] | None:
    x1 = treeview__numeric_attribute(candidate.element, 'x1')
    y1 = treeview__numeric_attribute(candidate.element, 'y1')
    x2 = treeview__numeric_attribute(candidate.element, 'x2')
    y2 = treeview__numeric_attribute(candidate.element, 'y2')
    if x1 is None or y1 is None or x2 is None or (y2 is None):
        return None
    return (x1, y1, x2, y2)
def treeview__same_position(first: float, second: float) -> bool:
    return abs(first - second) <= treeview__POSITION_TOLERANCE
def treeview__depth_for_x(x: float, label_x_positions: list[float]) -> int:
    if not label_x_positions:
        return 0
    return min(range(len(label_x_positions)), key=lambda index: abs(label_x_positions[index] - x))
def treeview__nearest_label_by_y(y: float, labels: list[Candidate], positions: dict[int, tuple[float, float]]) -> Candidate | None:
    same_row = [label for label in labels if treeview__same_position(positions[id(label)][1], y)]
    if not same_row:
        return None
    return min(same_row, key=lambda label: abs(positions[id(label)][1] - y))
def treeview__treeview_steps(candidates: list[Candidate]) -> list[treeview__TreeViewStep]:
    labels = [candidate for candidate in candidates if treeview__candidate_has_class(candidate, 'treeView-node-label')]
    lines = [candidate for candidate in candidates if treeview__candidate_has_class(candidate, 'treeView-node-line')]
    label_positions = {id(candidate): position for candidate in labels if (position := treeview__label_position(candidate)) is not None}
    if len(label_positions) != len(labels):
        return []
    label_x_positions = sorted({position[0] for position in label_positions.values()})
    steps_by_label: dict[int, treeview__TreeViewStep] = {}
    assigned: set[int] = set()
    for label in labels:
        x, y = label_positions[id(label)]
        depth = treeview__depth_for_x(x, label_x_positions)
        step = treeview__TreeViewStep(depth=depth, y=y, order=label.dom_index, candidates=[label])
        steps_by_label[id(label)] = step
        assigned.add(id(label))
    extra_steps: list[treeview__TreeViewStep] = []
    for line in lines:
        coordinates = treeview__line_coordinates(line)
        if coordinates is None:
            continue
        x1, y1, x2, y2 = coordinates
        assigned.add(id(line))
        if treeview__same_position(y1, y2):
            label = treeview__nearest_label_by_y(y1, labels, label_positions)
            if label is not None:
                steps_by_label[id(label)].candidates.insert(0, line)
                continue
            depth = treeview__depth_for_x(max(x1, x2), label_x_positions)
            extra_steps.append(treeview__TreeViewStep(depth=depth, y=y1, order=line.dom_index, candidates=[line]))
            continue
        if treeview__same_position(x1, x2):
            parent_depth = treeview__depth_for_x(x1, label_x_positions)
            child_depth = min(parent_depth + 1, max(len(label_x_positions) - 1, 0))
            extra_steps.append(treeview__TreeViewStep(depth=child_depth, y=min(y1, y2), order=line.dom_index, connection_only=True, candidates=[line]))
            continue
        extra_steps.append(treeview__TreeViewStep(depth=0, y=min(y1, y2), order=line.dom_index, connection_only=True, candidates=[line]))
    fallback_steps = [treeview__TreeViewStep(depth=len(label_x_positions), y=0.0, order=candidate.dom_index, candidates=[candidate]) for candidate in candidates if id(candidate) not in assigned]
    return sorted([*steps_by_label.values(), *extra_steps, *fallback_steps], key=lambda step: (step.depth, 1 if step.connection_only else 0, step.y, step.order))
def treeview__plan_treeview_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    steps = treeview__treeview_steps(candidates)
    if not steps:
        return []
    duration = float(args.duration_ms)
    stagger = float(args.stagger_ms)
    planned: list[Candidate] = []
    current_delay = float(args.initial_delay_ms)
    for stage, step in enumerate(steps):
        ordered_candidates = sorted(step.candidates, key=lambda item: (1 if item.role == 'edge' else 0, ROLE_PRIORITY.get(item.role, 99), item.dom_index))
        has_entity = any((candidate.role != 'edge' for candidate in ordered_candidates))
        has_edge = any((candidate.role == 'edge' for candidate in ordered_candidates))
        edge_delay = current_delay + duration + stagger if has_entity and has_edge else current_delay
        for candidate in ordered_candidates:
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = edge_delay if candidate.role == 'edge' else current_delay
            candidate.duration_ms = duration
            candidate.level = step.depth
            candidate.stage = stage
            planned.append(candidate)
        current_delay += (duration + stagger + duration if has_entity and has_edge else duration) + stagger
    return sorted(planned, key=lambda candidate: (candidate.delay_ms, ROLE_PRIORITY.get(candidate.role, 99), candidate.dom_index))

# --- venn ---

def venn__is_venn_root(root: ET.Element) -> bool:
    role = normalized(root.get('aria-roledescription', ''))
    return role == 'venn' or has_lower_class(root, 'venn')
def venn__discover_venn_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for element in root.iter():
        if local_name(element.tag) != 'g':
            continue
        lower_tokens = {token.lower() for token in class_tokens(element)}
        if 'venn-area' not in lower_tokens:
            continue
        classes = class_tokens(element)
        data_sets = element.get('data-venn-sets', '')
        if data_sets:
            classes.append(f"venn-sets-{slug(data_sets.replace('_', ' '))}")
        if 'venn-circle' in lower_tokens:
            role = 'node'
        elif 'venn-intersection' in lower_tokens:
            role = 'label'
        else:
            role = 'item'
        candidates.append(Candidate(element=element, role=role, dom_index=dom_order[element], element_id=element.get('id', ''), classes=classes, text=collapsed_text(element)))
    return candidates
def venn__numeric_attribute(element: ET.Element, name: str) -> float | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
def venn__first_path_move_position(element: ET.Element) -> tuple[float, float] | None:
    number = '[-+]?(?:\\d*\\.\\d+|\\d+)(?:[eE][-+]?\\d+)?'
    for child in element.iter():
        if local_name(child.tag) != 'path':
            continue
        match = re.search(f'[Mm]\\s*({number})(?:[,\\s]+)({number})', child.get('d', ''))
        if match:
            return (float(match.group(1)), float(match.group(2)))
    return None
def venn__first_text_position(element: ET.Element) -> tuple[float, float] | None:
    for child in element.iter():
        if local_name(child.tag) != 'text':
            continue
        x = venn__numeric_attribute(child, 'x')
        y = venn__numeric_attribute(child, 'y')
        if x is not None and y is not None:
            return (x, y)
    return None
def venn__venn_candidate_position(candidate: Candidate) -> tuple[float, float] | None:
    if 'venn-circle' in {token.lower() for token in candidate.classes}:
        return venn__first_path_move_position(candidate.element) or venn__first_text_position(candidate.element)
    return venn__first_text_position(candidate.element) or venn__first_path_move_position(candidate.element)
def venn__venn_set_count(candidate: Candidate) -> int:
    raw_sets = candidate.element.get('data-venn-sets', '')
    if not raw_sets:
        return 1
    return len([name for name in raw_sets.split('_') if name])
def venn__effect_for_venn_candidate(animation: str, candidate: Candidate) -> str:
    effect = effect_for(animation, candidate.role)
    if 'venn-circle' in {token.lower() for token in candidate.classes} and effect in TRANSFORM_EFFECTS:
        return 'fade'
    return effect
def venn__plan_venn_candidates(candidates: list[Candidate], args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    set_candidates = [candidate for candidate in candidates if 'venn-circle' in {token.lower() for token in candidate.classes}]
    union_candidates = [candidate for candidate in candidates if 'venn-intersection' in {token.lower() for token in candidate.classes}]
    special_ids = {id(candidate) for candidate in [*set_candidates, *union_candidates]}
    other_candidates = [candidate for candidate in candidates if id(candidate) not in special_ids]
    if not set_candidates and (not union_candidates):
        return []

    def set_key(candidate: Candidate) -> tuple[int, float, int]:
        position = venn__venn_candidate_position(candidate)
        if position is None:
            return (1, 0.0, candidate.dom_index)
        return (0, -position[1], candidate.dom_index)
    ordered = [*sorted(set_candidates, key=set_key), *sorted(other_candidates, key=ordered_reveal_key), *sorted(union_candidates, key=lambda candidate: (venn__venn_set_count(candidate), candidate.dom_index))]
    duration = float(args.duration_ms)
    step_gap = duration + float(args.stagger_ms)
    if args.total_ms is not None and len(ordered) > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        step_gap = max(step_gap, available / (len(ordered) - 1))
    for index, candidate in enumerate(ordered):
        candidate.effect = venn__effect_for_venn_candidate(effective_animation, candidate)
        candidate.delay_ms = float(args.initial_delay_ms) + index * step_gap
        candidate.duration_ms = duration
        candidate.stage = index
    return ordered

# --- xychart ---

def xychart__is_xychart_root(root: ET.Element) -> bool:
    return normalized(root.get('aria-roledescription', '')) == 'xychart'
def xychart__xy_chart_needs_specialized_discovery(root: ET.Element) -> bool:
    has_negative_tick = any(((text := collapsed_text(element)).startswith('-') and text[1:].split(maxsplit=1)[0].isdigit() for element in root.iter() if local_name(element.tag) == 'text'))
    line_plot_count = sum((1 for element in root.iter() if any((token.lower().startswith('line-plot-') for token in class_tokens(element)))))
    return has_negative_tick or line_plot_count > 1
def xychart__add_classes(classes: Iterable[str], extra_classes: Iterable[str]) -> list[str]:
    result = list(classes)
    for extra_class in extra_classes:
        if extra_class not in result:
            result.append(extra_class)
    return result
def xychart__has_class_prefix(element: ET.Element, prefix: str) -> bool:
    return any((token.lower().startswith(prefix) for token in class_tokens(element)))
def xychart__has_ancestor_class_prefix(element: ET.Element, parent_map: dict[ET.Element, ET.Element], prefix: str) -> bool:
    return any((xychart__has_class_prefix(parent, prefix) for parent in ancestors(element, parent_map)))
def xychart__discover_xychart_candidates(root: ET.Element, dom_order: dict[ET.Element, int]) -> list[Candidate]:
    if not xychart__xy_chart_needs_specialized_discovery(root):
        return []
    parent_map = build_parent_map(root)
    selected: set[ET.Element] = set()
    candidates: list[Candidate] = []

    def add_candidate(element: ET.Element, role: str, extra_classes: Iterable[str]) -> None:
        if element in selected or any((parent in selected for parent in ancestors(element, parent_map))):
            return
        selected.add(element)
        candidates.append(Candidate(element=element, role=role, dom_index=dom_order[element], element_id=element.get('id', ''), classes=xychart__add_classes(class_tokens(element), extra_classes), text=collapsed_text(element)))
    for element in root.iter():
        tag = local_name(element.tag)
        tokens = {token.lower() for token in class_tokens(element)}
        if tag == 'g' and tokens & {'chart-title', 'bottom-axis', 'left-axis'}:
            add_candidate(element, 'label', ['xychart-base'])
            continue
        if tag == 'rect' and xychart__has_ancestor_class_prefix(element, parent_map, 'bar-plot-'):
            add_candidate(element, 'node', ['xychart-bar'])
            continue
        if tag == 'text' and xychart__has_ancestor_class_prefix(element, parent_map, 'bar-plot-'):
            add_candidate(element, 'label', ['xychart-bar-label'])
            continue
        if tag == 'path' and xychart__has_ancestor_class_prefix(element, parent_map, 'line-plot-'):
            add_candidate(element, 'edge', ['xychart-line'])
    return candidates
def xychart__candidate_has_class(candidate: Candidate, token: str) -> bool:
    return token.lower() in {value.lower() for value in candidate.classes}
def xychart__candidate_x(candidate: Candidate, parent_map: dict[ET.Element, ET.Element]) -> float:
    x = numeric_attribute(candidate.element, 'x')
    if x is not None:
        return x
    center = element_center(candidate.element, parent_map)
    return center[0] if center is not None else 0.0
def xychart__candidate_y(candidate: Candidate, parent_map: dict[ET.Element, ET.Element]) -> float:
    y = numeric_attribute(candidate.element, 'y')
    if y is not None:
        return y
    center = element_center(candidate.element, parent_map)
    return center[1] if center is not None else 0.0
def xychart__line_series_index(candidate: Candidate) -> int:
    for token in candidate.classes:
        match = re.fullmatch('line-plot-(\\d+)', token.lower())
        if match:
            return int(match.group(1))
    return candidate.dom_index
def xychart__plan_xychart_candidates(candidates: list[Candidate], root: ET.Element, args: argparse.Namespace, effective_animation: str) -> list[Candidate]:
    if args.animation != 'auto' or any((candidate.explicit_order is not None for candidate in candidates)):
        return []
    parent_map = build_parent_map(root)
    base_candidates = [candidate for candidate in candidates if xychart__candidate_has_class(candidate, 'xychart-base')]
    bar_candidates = [candidate for candidate in candidates if xychart__candidate_has_class(candidate, 'xychart-bar')]
    bar_label_candidates = [candidate for candidate in candidates if xychart__candidate_has_class(candidate, 'xychart-bar-label')]
    line_candidates = [candidate for candidate in candidates if xychart__candidate_has_class(candidate, 'xychart-line')]
    if not bar_candidates and (not line_candidates):
        return []
    labels_by_bar: dict[int, list[Candidate]] = {}
    for label in bar_label_candidates:
        nearest_bar = min(bar_candidates, key=lambda bar: abs(xychart__candidate_x(bar, parent_map) - xychart__candidate_x(label, parent_map)), default=None)
        if nearest_bar is not None:
            labels_by_bar.setdefault(id(nearest_bar), []).append(label)
    stages: list[list[Candidate]] = []
    if base_candidates:
        stages.append(sorted(base_candidates, key=lambda candidate: candidate.dom_index))
    for bar in sorted(bar_candidates, key=lambda candidate: (xychart__candidate_x(candidate, parent_map), candidate.dom_index)):
        stages.append([bar, *sorted(labels_by_bar.get(id(bar), []), key=lambda candidate: candidate.dom_index)])
    for line in sorted(line_candidates, key=lambda candidate: (xychart__line_series_index(candidate), candidate.dom_index)):
        stages.append([line])
    planned_ids = {id(candidate) for stage in stages for candidate in stage}
    leftovers = [candidate for candidate in candidates if id(candidate) not in planned_ids]
    if leftovers:
        stages.append(sorted(leftovers, key=lambda candidate: (xychart__candidate_y(candidate, parent_map), candidate.dom_index)))
    duration = float(args.duration_ms)
    if args.total_ms is not None and len(stages) > 1:
        available = float(args.total_ms) - float(args.initial_delay_ms) - duration
        stage_gap = max(duration + float(args.stagger_ms), available / (len(stages) - 1))
    else:
        stage_gap = duration + float(args.stagger_ms)
    planned: list[Candidate] = []
    for index, stage in enumerate(stages):
        delay = float(args.initial_delay_ms) + index * stage_gap
        for candidate in stage:
            candidate.effect = effect_for(effective_animation, candidate.role)
            candidate.delay_ms = delay
            candidate.duration_ms = duration
            candidate.stage = index
            planned.append(candidate)
    return planned

# Public API consumed by discovery.py and planning.py.

discover_architecture_candidates = architecture__discover_architecture_candidates
discover_block_candidates = blockdiagram__discover_block_candidates
discover_class_candidates = classdiagram__discover_class_candidates
discover_er_candidates = er__discover_er_candidates
discover_event_modeling_candidates = eventmodeling__discover_event_modeling_candidates
discover_gantt_candidates = gantt__discover_gantt_candidates
discover_ishikawa_candidates = ishikawa__discover_ishikawa_candidates
discover_journey_candidates = journey__discover_journey_candidates
discover_pie_chart_candidates = pie__discover_pie_chart_candidates
discover_quadrant_chart_candidates = quadrant__discover_quadrant_chart_candidates
discover_radar_candidates = radar__discover_radar_candidates
discover_sankey_candidates = sankey__discover_sankey_candidates
discover_sequence_candidates = sequence__discover_sequence_candidates
discover_timeline_candidates = timeline__discover_timeline_candidates
discover_venn_candidates = venn__discover_venn_candidates
discover_xychart_candidates = xychart__discover_xychart_candidates
is_architecture_root = architecture__is_architecture_root
is_block_root = blockdiagram__is_block_root
is_class_root = classdiagram__is_class_root
is_er_root = er__is_er_root
is_event_modeling_root = eventmodeling__is_event_modeling_root
is_flowchart_root = flowchart__is_flowchart_root
is_gantt_root = gantt__is_gantt_root
is_gitgraph_root = gitgraph__is_gitgraph_root
is_ishikawa_root = ishikawa__is_ishikawa_root
is_journey_root = journey__is_journey_root
is_kanban_root = kanban__is_kanban_root
is_mindmap_candidates = mindmap__is_mindmap_candidates
is_pie_root = pie__is_pie_root
is_quadrant_chart_root = quadrant__is_quadrant_chart_root
is_radar_root = radar__is_radar_root
is_requirement_root = requirement__is_requirement_root
is_sankey_root = sankey__is_sankey_root
is_sequence_root = sequence__is_sequence_root
is_state_root = state__is_state_root
is_timeline_root = timeline__is_timeline_root
is_treeview_root = treeview__is_treeview_root
is_venn_root = venn__is_venn_root
is_xychart_root = xychart__is_xychart_root
plan_architecture_candidates = architecture__plan_architecture_candidates
plan_block_candidates = blockdiagram__plan_block_candidates
plan_class_candidates = classdiagram__plan_class_candidates
plan_er_candidates = er__plan_er_candidates
plan_event_modeling_candidates = eventmodeling__plan_event_modeling_candidates
plan_flowchart_candidates = flowchart__plan_flowchart_candidates
plan_gantt_candidates = gantt__plan_gantt_candidates
plan_gitgraph_candidates = gitgraph__plan_gitgraph_candidates
plan_ishikawa_candidates = ishikawa__plan_ishikawa_candidates
plan_journey_candidates = journey__plan_journey_candidates
plan_kanban_candidates = kanban__plan_kanban_candidates
plan_mindmap_candidates = mindmap__plan_mindmap_candidates
plan_pie_chart_candidates = pie__plan_pie_chart_candidates
plan_quadrant_chart_candidates = quadrant__plan_quadrant_chart_candidates
plan_radar_candidates = radar__plan_radar_candidates
plan_requirement_candidates = requirement__plan_requirement_candidates
plan_sankey_candidates = sankey__plan_sankey_candidates
plan_sequence_candidates = sequence__plan_sequence_candidates
plan_state_candidates = state__plan_state_candidates
plan_timeline_candidates = timeline__plan_timeline_candidates
plan_treeview_candidates = treeview__plan_treeview_candidates
plan_venn_candidates = venn__plan_venn_candidates
plan_xychart_candidates = xychart__plan_xychart_candidates
