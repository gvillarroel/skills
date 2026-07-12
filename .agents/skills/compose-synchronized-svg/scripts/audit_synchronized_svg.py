#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

"""Audit the browser runtime of a standalone synchronized SVG."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

from audit_worker_supervisor import (
    configure_utf8_standard_streams,
    supervise_worker,
)
from compact_audit_report import compact_report
from urllib.parse import urlparse

configure_utf8_standard_streams()


INTERNAL_WORKER_FLAG = "--internal-worker"


if __name__ == "__main__" and INTERNAL_WORKER_FLAG not in sys.argv:
    raise SystemExit(
        supervise_worker(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                *sys.argv[1:],
                INTERNAL_WORKER_FLAG,
            ]
        )
    )

from playwright.sync_api import (  # noqa: E402
    Browser,
    BrowserContext,
    Error as PlaywrightError,
    Page,
    sync_playwright,
)

from scaffold_synchronized_svg import validate_plan  # noqa: E402


REQUIRED_METHODS = {
    "getPlan",
    "getState",
    "setState",
    "applyScenario",
    "setFocus",
    "seek",
    "play",
    "pause",
    "reset",
    "snapshot",
    "serializeSnapshot",
}

CAPTURE_JS = r"""
() => {
  const api = window.svgSync;
  const root = document.documentElement;
  const plan = api.getPlan();
  const bindings = [];
  for (const module of plan.modules) {
    const group = root.querySelector(`[data-module-id="${CSS.escape(module.id)}"]`);
    if (!group) continue;
    for (const binding of module.bindings) {
      const targets = [...group.querySelectorAll(binding.selector)];
      targets.forEach((element, index) => {
        const attribute = binding.channel === "path" ? "d" : binding.channel;
        let rendered;
        if (binding.channel === "text") rendered = element.textContent;
        else if (binding.channel === "class") rendered = element.getAttribute("data-sync-class");
        else if (binding.channel === "aria-value") rendered = element.getAttribute("aria-valuenow");
        else rendered = element.getAttribute(attribute);
        bindings.push({
          key: `${module.id}|${binding.selector}|${binding.channel}|${index}`,
          moduleId: module.id,
          valueId: binding.value,
          selector: binding.selector,
          channel: binding.channel,
          currentValue: element.getAttribute("data-current-value"),
          revision: element.getAttribute("data-sync-revision"),
          rendered,
          syncValue: element.style.getPropertyValue("--sync-value"),
          syncRendered: element.style.getPropertyValue("--sync-rendered")
        });
      });
    }
  }
  bindings.sort((a, b) => a.key.localeCompare(b.key));
  const modules = {};
  root.querySelectorAll("[data-module-id]").forEach((element) => {
    const focusControls = [...element.querySelectorAll("[data-module-focus-id]")].map((focusControl) => ({
      focusId: focusControl.getAttribute("data-module-focus-id"),
      role: focusControl.getAttribute("role"),
      label: focusControl.getAttribute("aria-label") || "",
      pressed: focusControl.getAttribute("aria-pressed"),
      tabIndex: focusControl.tabIndex
    }));
    modules[element.getAttribute("data-module-id")] = {
      focused: element.getAttribute("data-focused"),
      assetType: element.getAttribute("data-asset-type"),
      focusControls
    };
  });
  const controls = {};
  root.querySelectorAll("[data-action]").forEach((element) => {
    controls[element.id || `${element.dataset.action}-${element.dataset.scenarioId || ""}`] = {
      action: element.dataset.action || "",
      text: (element.querySelector("text")?.textContent || "").trim(),
      label: element.getAttribute("aria-label") || "",
      pressed: element.getAttribute("aria-pressed"),
      disabled: element.getAttribute("aria-disabled"),
      tabIndex: element.tabIndex
    };
  });
  return {
    snapshot: api.snapshot(),
    serialized: api.serializeSnapshot(),
    state: api.getState(),
    root: {
      revision: root.getAttribute("data-state-revision"),
      scenarioId: root.getAttribute("data-current-scenario"),
      focusId: root.getAttribute("data-focus-id"),
      timeMs: root.getAttribute("data-time-ms"),
      phaseId: root.getAttribute("data-phase-id"),
      phaseProgress: root.getAttribute("data-phase-progress"),
      ready: root.getAttribute("data-sync-ready")
    },
    bindings,
    modules,
    controls
  };
}
"""

INSTALL_EVENT_PROBE_JS = r"""
() => {
  const root = document.documentElement;
  window.__svgSyncAuditEvents = [];
  root.addEventListener("svg-sync-change", (event) => {
    const detail = JSON.parse(JSON.stringify(event.detail));
    const values = {...detail.sourceValues, ...detail.derivedValues};
    const bindingRevisions = new Set();
    const valueMismatches = [];
    root.querySelectorAll("[data-bind]").forEach((element) => {
      bindingRevisions.add(element.getAttribute("data-sync-revision"));
      const id = element.getAttribute("data-bind");
      const actual = Number(element.getAttribute("data-current-value"));
      const expected = Number(values[id]);
      if (!Number.isFinite(actual) || !Number.isFinite(expected) || actual !== expected) {
        valueMismatches.push(id);
      }
    });
    window.__svgSyncAuditEvents.push({
      detail,
      rootRevision: root.getAttribute("data-state-revision"),
      bindingRevisions: [...bindingRevisions].sort(),
      valueMismatches: [...new Set(valueMismatches)].sort()
    });
  });
}
"""

INVOKE_JS = r"""
({method, args}) => {
  const api = window.svgSync;
  window.__svgSyncAuditEvents.length = 0;
  const before = api.serializeSnapshot();
  const result = api[method](...args);
  const after = api.serializeSnapshot();
  return {
    before,
    after,
    result: JSON.parse(JSON.stringify(result)),
    events: window.__svgSyncAuditEvents.splice(0)
  };
}
"""

GEOMETRY_AUDIT_JS = r"""
({tolerancePx, overlapRatioThreshold, overlapMinPx}) => {
  const root = document.documentElement;
  const rootRect = root.getBoundingClientRect();
  const viewBox = root.viewBox?.baseVal;
  const screenMatrix = root.getScreenCTM();
  let contentRect = rootRect;
  if (viewBox && screenMatrix && viewBox.width > 0 && viewBox.height > 0) {
    const corners = [
      new DOMPoint(viewBox.x, viewBox.y),
      new DOMPoint(viewBox.x + viewBox.width, viewBox.y),
      new DOMPoint(viewBox.x, viewBox.y + viewBox.height),
      new DOMPoint(viewBox.x + viewBox.width, viewBox.y + viewBox.height)
    ].map((point) => point.matrixTransform(screenMatrix));
    const left = Math.min(...corners.map((point) => point.x));
    const top = Math.min(...corners.map((point) => point.y));
    const right = Math.max(...corners.map((point) => point.x));
    const bottom = Math.max(...corners.map((point) => point.y));
    contentRect = {left, top, right, bottom, width: right - left, height: bottom - top};
  }
  const issues = [];
  const moduleResults = [];
  const frameRects = [];
  const decorativeTextPattern = /(?:^|[-_\s])(?:text-)?(?:background|backdrop|halo|outline|shadow)(?:$|[-_\s])/i;
  const unresolvedTemplatePattern = /\{\{[^{}]*\}\}|\$\{[^{}]*\}|<%[^%]*%>|\[\[[^\[\]]+\]\]/;
  const invalidTokenPattern = /\b(?:nan|undefined)\b/i;

  function compactRect(rect) {
    return {
      left: Number(rect.left.toFixed(2)),
      top: Number(rect.top.toFixed(2)),
      right: Number(rect.right.toFixed(2)),
      bottom: Number(rect.bottom.toFixed(2)),
      width: Number(rect.width.toFixed(2)),
      height: Number(rect.height.toFixed(2))
    };
  }

  function styleVisible(element, boundary) {
    let current = element;
    while (current && current !== boundary.parentElement) {
      const style = getComputedStyle(current);
      if (
        style.display === "none" ||
        style.visibility === "hidden" ||
        style.visibility === "collapse" ||
        Number.parseFloat(style.opacity || "1") <= 0.01
      ) return false;
      if (current === boundary) break;
      current = current.parentElement;
    }
    return true;
  }

  function visibleBox(element, boundary) {
    if (!styleVisible(element, boundary)) return null;
    const rect = element.getBoundingClientRect();
    return rect.width > 0.5 && rect.height > 0.5 ? rect : null;
  }

  function normalizedText(element) {
    return (element.textContent || "").replace(/\s+/g, " ").trim();
  }

  function elementLabel(element) {
    const identity =
      element.id ||
      element.getAttribute("data-role") ||
      element.getAttribute("aria-label") ||
      element.tagName.toLowerCase();
    const text = normalizedText(element);
    return text ? `${identity} (${text.slice(0, 72)})` : identity;
  }

  function isDecorativeText(element) {
    if (element.getAttribute("aria-hidden") === "true") return true;
    if (element.closest('[data-text-background="true"], [data-allow-text-overlap="true"]')) return true;
    const marker = [
      element.getAttribute("class") || "",
      element.getAttribute("data-role") || ""
    ].join(" ");
    return decorativeTextPattern.test(marker);
  }

  function escapeDistances(frame, rect) {
    return {
      left: Math.max(0, frame.left - rect.left),
      top: Math.max(0, frame.top - rect.top),
      right: Math.max(0, rect.right - frame.right),
      bottom: Math.max(0, rect.bottom - frame.bottom)
    };
  }

  function escapesFrame(distances) {
    return Math.max(distances.left, distances.top, distances.right, distances.bottom) > tolerancePx;
  }

  function sameAllowedOverlapGroup(first, second) {
    const firstGroup = first.getAttribute("data-overlap-group");
    return Boolean(firstGroup && firstGroup === second.getAttribute("data-overlap-group"));
  }

  const modules = [...root.querySelectorAll(".sync-module[data-module-id]")].filter(
    (module) => visibleBox(module, root)
  );
  for (const module of modules) {
    const moduleId = module.getAttribute("data-module-id") || module.id || "unknown-module";
    const frame = module.querySelector(":scope > .module-frame") || module.querySelector(".module-frame");
    const frameRect = frame ? visibleBox(frame, module) : null;
    const moduleIssues = [];
    if (!frameRect) {
      const issue = {type: "missing-frame", moduleId, element: ".module-frame"};
      issues.push(issue);
      moduleIssues.push(issue);
      moduleResults.push({
        moduleId,
        frame: null,
        visibleTextCount: 0,
        visibleBoundMarkCount: 0,
        escapeCount: 0,
        overlapCount: 0,
        invalidTextCount: 0
      });
      continue;
    }
    frameRects.push(frameRect);

    const textElements = [...module.querySelectorAll("text")].filter(
      (element) => !isDecorativeText(element) && visibleBox(element, module)
    );
    const boundTextElements = [...module.querySelectorAll('[data-bind][data-channel="text"]')].filter(
      (element) => styleVisible(element, module)
    );
    const visibleBoundMarks = [...module.querySelectorAll("[data-bind]")].filter(
      (element) => visibleBox(element, module)
    );

    const contentTop = Number(module.getAttribute("data-content-top"));
    const body = module.querySelector(`:scope > [data-module-content-for="${CSS.escape(moduleId)}"]`);
    if (body && Number.isFinite(contentTop)) {
      const matrix = module.getScreenCTM();
      const boundary = matrix ? new DOMPoint(0, contentTop).matrixTransform(matrix).y : null;
      if (Number.isFinite(boundary)) {
        const bodyMarks = [...body.querySelectorAll("text, rect, circle, ellipse, line, path, polygon, polyline, image, use")];
        for (const element of bodyMarks) {
          if (element.closest("defs") || element.getAttribute("data-allow-header-overlap") === "true") continue;
          const rect = visibleBox(element, module);
          if (!rect || rect.top >= boundary - tolerancePx) continue;
          const issue = {
            type: "header-body-overlap",
            moduleId,
            element: elementLabel(element),
            contentTop,
            overlapPx: Number((boundary - rect.top).toFixed(2))
          };
          issues.push(issue);
          moduleIssues.push(issue);
        }
      }
    }

    const invalidSeen = new Set();
    for (const element of textElements) {
      const text = normalizedText(element);
      let reason = null;
      if (text === "--") reason = "placeholder dashes";
      else if (invalidTokenPattern.test(text)) reason = "non-finite or undefined token";
      else if (unresolvedTemplatePattern.test(text)) reason = "unresolved template syntax";
      if (reason) {
        const issue = {
          type: "invalid-text",
          moduleId,
          element: elementLabel(element),
          text: text.slice(0, 120),
          reason
        };
        issues.push(issue);
        moduleIssues.push(issue);
        invalidSeen.add(element);
      }
    }
    for (const element of boundTextElements) {
      if (!normalizedText(element) && !invalidSeen.has(element)) {
        const issue = {
          type: "invalid-text",
          moduleId,
          element: elementLabel(element),
          text: "",
          reason: "blank data-bound text"
        };
        issues.push(issue);
        moduleIssues.push(issue);
        invalidSeen.add(element);
      }
    }

    const measured = new Set();
    for (const element of [...textElements, ...visibleBoundMarks]) {
      if (measured.has(element)) continue;
      measured.add(element);
      const rect = visibleBox(element, module);
      if (!rect) continue;
      const outside = escapeDistances(frameRect, rect);
      if (escapesFrame(outside)) {
        const issue = {
          type: "frame-escape",
          moduleId,
          kind: element.tagName.toLowerCase() === "text" ? "text" : "bound-mark",
          element: elementLabel(element),
          outside: Object.fromEntries(
            Object.entries(outside).map(([key, value]) => [key, Number(value.toFixed(2))])
          )
        };
        issues.push(issue);
        moduleIssues.push(issue);
      }
    }

    for (let firstIndex = 0; firstIndex < textElements.length; firstIndex += 1) {
      const first = textElements[firstIndex];
      const firstRect = first.getBoundingClientRect();
      for (let secondIndex = firstIndex + 1; secondIndex < textElements.length; secondIndex += 1) {
        const second = textElements[secondIndex];
        if (
          first.contains(second) ||
          second.contains(first) ||
          sameAllowedOverlapGroup(first, second)
        ) continue;
        const secondRect = second.getBoundingClientRect();
        const width = Math.max(0, Math.min(firstRect.right, secondRect.right) - Math.max(firstRect.left, secondRect.left));
        const height = Math.max(0, Math.min(firstRect.bottom, secondRect.bottom) - Math.max(firstRect.top, secondRect.top));
        if (width <= overlapMinPx || height <= overlapMinPx) continue;
        const area = width * height;
        const smallerArea = Math.max(1, Math.min(firstRect.width * firstRect.height, secondRect.width * secondRect.height));
        const ratio = area / smallerArea;
        if (ratio < overlapRatioThreshold) continue;
        const issue = {
          type: "text-overlap",
          moduleId,
          first: elementLabel(first),
          second: elementLabel(second),
          intersectionWidth: Number(width.toFixed(2)),
          intersectionHeight: Number(height.toFixed(2)),
          overlapRatio: Number(ratio.toFixed(3))
        };
        issues.push(issue);
        moduleIssues.push(issue);
      }
    }

    moduleResults.push({
      moduleId,
      frame: compactRect(frameRect),
      visibleTextCount: textElements.length,
      visibleBoundMarkCount: visibleBoundMarks.length,
      escapeCount: moduleIssues.filter((issue) => issue.type === "frame-escape").length,
      overlapCount: moduleIssues.filter((issue) => issue.type === "text-overlap").length,
      headerBodyOverlapCount: moduleIssues.filter((issue) => issue.type === "header-body-overlap").length,
      invalidTextCount: moduleIssues.filter((issue) => issue.type === "invalid-text").length
    });
  }

  let footprint = null;
  if (frameRects.length && contentRect.width > 0 && contentRect.height > 0) {
    const left = Math.min(...frameRects.map((rect) => rect.left));
    const top = Math.min(...frameRects.map((rect) => rect.top));
    const right = Math.max(...frameRects.map((rect) => rect.right));
    const bottom = Math.max(...frameRects.map((rect) => rect.bottom));
    const frameArea = frameRects.reduce((total, rect) => total + rect.width * rect.height, 0);
    footprint = {
      widthRatio: Number(((right - left) / contentRect.width).toFixed(4)),
      heightRatio: Number(((bottom - top) / contentRect.height).toFixed(4)),
      areaRatio: Number((frameArea / (contentRect.width * contentRect.height)).toFixed(4)),
      bounds: compactRect({left, top, right, bottom, width: right - left, height: bottom - top})
    };
  }

  return {
    root: compactRect(rootRect),
    rootContent: compactRect(contentRect),
    visibleModuleCount: modules.length,
    visibleTextCount: moduleResults.reduce((total, item) => total + item.visibleTextCount, 0),
    visibleBoundMarkCount: moduleResults.reduce((total, item) => total + item.visibleBoundMarkCount, 0),
    footprint,
    modules: moduleResults,
    issues
  };
}
"""

QUANTITATIVE_SEMANTICS_JS = r"""
() => {
  const issues = [];
  const flows = [];
  for (const plot of document.querySelectorAll('[data-sync-layout="flow"]')) {
    const module = plot.closest(".sync-module[data-module-id]");
    const sourceLabel = plot.querySelector("[data-flow-source-label]");
    const sourceMark = plot.querySelector("[data-flow-source-bound] [data-bind]");
    if (!sourceLabel || !sourceMark) continue;
    const base = sourceLabel.getAttribute("data-base-label") || "Source";
    const accessibleValue = sourceMark.getAttribute("data-accessible-value") || sourceMark.getAttribute("data-current-value") || "";
    const visibleValue = (sourceLabel.textContent || "").trim();
    const expectedValue = accessibleValue ? `${base} · ${accessibleValue}` : base;
    if (visibleValue !== expectedValue) {
      issues.push({
        moduleId: module?.dataset.moduleId || "unknown",
        role: sourceMark.getAttribute("data-role") || "unknown",
        accessibleValue,
        visibleValue,
        reason: "flow source label must mirror the current accessible value"
      });
    }
    const sourceValue = Number(sourceMark.getAttribute("data-current-value"));
    const sourceUnit = sourceMark.getAttribute("data-value-unit") || "";
    const branchRecords = [...plot.querySelectorAll('[data-sync-layout-item="flow"]')].map((item) => {
      const role = item.getAttribute("data-layout-bound-role") || "unknown";
      const mark = module ? module.querySelector(`[data-role="${CSS.escape(role)}"]`) : null;
      return {
        role,
        value: mark ? Number(mark.getAttribute("data-current-value")) : NaN,
        unit: mark?.getAttribute("data-value-unit") || ""
      };
    });
    const branchTotal = branchRecords.reduce((total, record) => total + record.value, 0);
    const units = new Set([sourceUnit, ...branchRecords.map((record) => record.unit)]);
    const reconciliationScale = Math.max(
      Math.abs(sourceValue),
      ...branchRecords.map((record) => Math.abs(record.value)),
      0
    );
    const tolerance = Math.max(
      Number.MIN_VALUE,
      64 * Number.EPSILON * reconciliationScale * Math.max(1, branchRecords.length + 1)
    );
    const difference = sourceValue - branchTotal;
    if (!Number.isFinite(sourceValue) || branchRecords.some((record) => !Number.isFinite(record.value)) ||
        !Number.isFinite(branchTotal) || !Number.isFinite(difference) || !Number.isFinite(tolerance)) {
      issues.push({
        moduleId: module?.dataset.moduleId || "unknown",
        sourceValue,
        branches: branchRecords,
        reason: "flow conservation values must be finite"
      });
    } else if (units.size !== 1) {
      issues.push({
        moduleId: module?.dataset.moduleId || "unknown",
        sourceUnit,
        branches: branchRecords,
        reason: "flow source and branches must share one unit"
      });
    } else if (Math.abs(difference) > tolerance) {
      issues.push({
        moduleId: module?.dataset.moduleId || "unknown",
        sourceValue,
        branchTotal,
        branches: branchRecords,
        reason: "flow branches must conserve the current source value"
      });
    }
  }
  for (const item of document.querySelectorAll('[data-sync-layout-item="flow"]')) {
    const role = item.getAttribute("data-layout-bound-role") || "unknown";
    const module = item.closest(".sync-module[data-module-id]");
    const mark = module ? module.querySelector(`[data-role="${CSS.escape(role)}"]`) : null;
    const path = item.querySelector("[data-sync-flow-path]");
    const value = mark ? Number(mark.getAttribute("data-current-value")) : NaN;
    const direction = item.getAttribute("data-flow-direction") || "";
    const strokeWidth = path ? Number(path.getAttribute("stroke-width")) : NaN;
    const dashed = Boolean(path && (path.getAttribute("stroke-dasharray") || "").trim());
    const reverseMarker = Boolean(path && (path.getAttribute("marker-end") || "").trim());
    const signLabel = (item.querySelector("[data-flow-sign-label]")?.textContent || "").trim();
    const accessibleValue = mark?.getAttribute("data-accessible-value") || mark?.getAttribute("data-current-value") || "";
    const visibleValue = (item.querySelector("[data-flow-value-label]")?.textContent || "").trim();
    const record = {moduleId: module?.dataset.moduleId || "unknown", role, value, direction, strokeWidth, dashed, reverseMarker, signLabel, accessibleValue, visibleValue};
    flows.push(record);
    if (visibleValue !== accessibleValue) {
      issues.push({...record, reason: "flow branch label must mirror the current accessible value"});
    } else if (!Number.isFinite(value) || !Number.isFinite(strokeWidth)) {
      issues.push({...record, reason: "flow value or stroke width is not finite"});
    } else if (value === 0) {
      if (strokeWidth > 0.01 || direction !== "zero" || dashed || reverseMarker || signLabel) {
        issues.push({...record, reason: "zero flow must have zero thickness, zero direction, and no deficit cues"});
      }
    } else if (value < 0) {
      if (direction !== "reverse" || !dashed || !reverseMarker || signLabel !== "DEFICIT") {
        issues.push({...record, reason: "negative flow must be reverse, dashed, arrowed, and labeled DEFICIT"});
      }
    } else if (direction !== "forward" || dashed || reverseMarker || signLabel) {
      issues.push({...record, reason: "positive flow must be forward without deficit cues"});
    }
  }

  const bars = [];
  for (const plot of document.querySelectorAll('[data-sync-layout="bar-comparison"]')) {
    const module = plot.closest(".sync-module[data-module-id]");
    const records = [];
    for (const mark of plot.querySelectorAll('[data-bind][data-channel="width"]')) {
      const value = Number(mark.getAttribute("data-current-value"));
      const pixelWidth = mark.getBoundingClientRect().width;
      const unit = mark.getAttribute("data-value-unit") || "";
      const record = {
        moduleId: module?.dataset.moduleId || "unknown",
        role: mark.dataset.role || "unknown",
        value,
        unit,
        pixelWidth,
        pixelsPerUnit: Number.isFinite(value) && value > 0 ? pixelWidth / value : null
      };
      records.push(record);
      if (!Number.isFinite(value) || !Number.isFinite(pixelWidth)) {
        issues.push({...record, reason: "bar value or pixel width is not finite"});
      } else if (value < 0) {
        issues.push({...record, reason: "comparative bars require nonnegative values on one zero baseline"});
      } else if (value === 0 && pixelWidth > 0.75) {
        issues.push({...record, reason: "zero comparative-bar value must have zero visual width"});
      }
    }
    const units = [...new Set(records.map((record) => record.unit))];
    if (units.length > 1) {
      issues.push({
        moduleId: module?.dataset.moduleId || "unknown",
        role: "bar-shared-unit",
        value: null,
        units,
        reason: "comparative bars do not share one canonical unit"
      });
    }
    const ratios = records.map((record) => record.pixelsPerUnit).filter(Number.isFinite);
    if (ratios.length > 1) {
      const minimum = Math.min(...ratios);
      const maximum = Math.max(...ratios);
      if (maximum - minimum > Math.max(0.000001, maximum * 0.03)) {
        issues.push({
          moduleId: module?.dataset.moduleId || "unknown",
          role: "bar-shared-scale",
          value: null,
          minimumPixelsPerUnit: minimum,
          maximumPixelsPerUnit: maximum,
          reason: "comparative bars do not share one absolute unit scale"
        });
      }
    }
    bars.push({moduleId: module?.dataset.moduleId || "unknown", records});
  }

  const stacks = [];
  const state = window.svgSync?.snapshot?.() || {};
  const canonicalValues = {...(state.sourceValues || {}), ...(state.derivedValues || {})};
  for (const plot of document.querySelectorAll('[data-sync-layout="stack"]')) {
    const module = plot.closest(".sync-module[data-module-id]");
    const records = [];
    for (const item of plot.querySelectorAll('[data-sync-layout-item="stack"]')) {
      const mark = item.querySelector("[data-bind]");
      const value = mark ? Number(mark.getAttribute("data-current-value")) : NaN;
      const pixelWidth = mark ? mark.getBoundingClientRect().width : NaN;
      const clamped = item.getAttribute("data-visual-clamped") === "true";
      const record = {
        moduleId: module?.dataset.moduleId || "unknown",
        role: mark?.dataset.role || "unknown",
        value,
        pixelWidth,
        clamped,
        pixelsPerUnit: Number.isFinite(value) && value > 0 ? pixelWidth / value : null
      };
      records.push(record);
      if (!Number.isFinite(value) || !Number.isFinite(pixelWidth)) {
        issues.push({...record, reason: "stack value or pixel width is not finite"});
      } else if (value < 0) {
        issues.push({...record, reason: "generated stack parts must stay nonnegative"});
      } else if (clamped) {
        issues.push({...record, reason: "stack part is visually clamped before the declared total"});
      } else if (value === 0 && pixelWidth > 0.75) {
        issues.push({...record, reason: "zero stack part must have zero visual width"});
      }
    }
    const ratios = records.map((record) => record.pixelsPerUnit).filter(Number.isFinite);
    if (ratios.length > 1 && Math.max(...ratios) - Math.min(...ratios) > Math.max(0.000001, Math.max(...ratios) * 0.03)) {
      issues.push({
        moduleId: module?.dataset.moduleId || "unknown",
        role: "stack-shared-scale",
        value: null,
        reason: "stack parts do not share one absolute unit scale"
      });
    }
    const totalId = plot.dataset.stackTotal || "";
    const total = Number(canonicalValues[totalId]);
    const partSum = records.reduce((sum, record) => sum + Number(record.value || 0), 0);
    const tolerance = Math.max(1e-7, Math.max(Math.abs(total), Math.abs(partSum)) * 1e-7);
    if (!totalId || !Number.isFinite(total) || Math.abs(partSum - total) > tolerance) {
      issues.push({
        moduleId: module?.dataset.moduleId || "unknown",
        role: "stack-reconciliation",
        value: partSum,
        totalId,
        total,
        reason: "stack parts do not reconcile to the declared canonical total"
      });
    }
    stacks.push({moduleId: module?.dataset.moduleId || "unknown", totalId, total, partSum, records});
  }

  const waterfalls = [];
  for (const plot of document.querySelectorAll('[data-sync-layout="waterfall"]')) {
    const module = plot.closest(".sync-module[data-module-id]");
    const records = [];
    for (const item of [...plot.querySelectorAll('[data-sync-layout-item="waterfall"]')]
      .sort((a, b) => Number(a.dataset.layoutIndex) - Number(b.dataset.layoutIndex))) {
      const mark = item.querySelector("[data-bind]");
      const value = mark ? Number(mark.getAttribute("data-current-value")) : NaN;
      const pixelHeight = mark ? mark.getBoundingClientRect().height : NaN;
      const clamped = item.getAttribute("data-visual-clamped") === "true";
      const record = {
        moduleId: module?.dataset.moduleId || "unknown",
        role: mark?.dataset.role || "unknown",
        value,
        pixelHeight,
        clamped,
        pixelsPerUnit: Number.isFinite(value) && value !== 0
          ? pixelHeight / Math.abs(value)
          : null
      };
      records.push(record);
      if (!Number.isFinite(value) || !Number.isFinite(pixelHeight)) {
        issues.push({...record, reason: "waterfall value or pixel height is not finite"});
      } else if (clamped) {
        issues.push({...record, reason: "waterfall canonical value is visually clamped"});
      } else if (value === 0 && pixelHeight > 0.75) {
        issues.push({...record, reason: "zero waterfall value must have zero visual height"});
      }
    }
    const ratios = records
      .map((record) => record.pixelsPerUnit)
      .filter((value) => Number.isFinite(value));
    if (ratios.length > 1) {
      const minimum = Math.min(...ratios);
      const maximum = Math.max(...ratios);
      if (maximum - minimum > Math.max(0.000001, maximum * 0.03)) {
        issues.push({
          moduleId: module?.dataset.moduleId || "unknown",
          role: "waterfall-shared-scale",
          value: null,
          minimumPixelsPerUnit: minimum,
          maximumPixelsPerUnit: maximum,
          reason: "waterfall steps do not share one absolute unit scale"
        });
      }
    }
    if (records.length >= 2 && records.every((record) => Number.isFinite(record.value))) {
      const opening = Math.abs(records[0].value);
      const deductions = records.slice(1, -1).reduce((total, record) => total + Math.abs(record.value), 0);
      const ending = Math.abs(records[records.length - 1].value);
      const tolerance = Math.max(1e-7, Math.max(opening, deductions, ending) * 1e-7);
      if (Math.abs(opening - deductions - ending) > tolerance) {
        issues.push({
          moduleId: module?.dataset.moduleId || "unknown",
          role: "waterfall-reconciliation",
          value: opening,
          opening,
          deductions,
          ending,
          reason: "waterfall opening minus deductions does not equal its ending"
        });
      }
    }
    waterfalls.push({moduleId: module?.dataset.moduleId || "unknown", records});
  }

  const progress = [];
  for (const plot of document.querySelectorAll('[data-sync-layout="progress"]')) {
    const role = plot.getAttribute("data-layout-bound-role") || "unknown";
    const module = plot.closest(".sync-module[data-module-id]");
    const mark = module ? module.querySelector(`[data-role="${CSS.escape(role)}"]`) : null;
    const readout = plot.querySelector("[data-progress-current]");
    const value = mark ? Number(mark.getAttribute("data-current-value")) : NaN;
    const text = (readout?.textContent || "").trim();
    const match = text.match(/-?\d+(?:\.\d+)?/);
    const shownPercent = match ? Number(match[0]) : NaN;
    const unit = mark?.dataset.valueUnit || "";
    const expectedPercent = unit === "percent" || unit === "%" ? value : value * 100;
    const targetValue = Number(plot.dataset.layoutTargetValue);
    const maximumValue = Number(plot.dataset.layoutMaxValue);
    const track = plot.querySelector(":scope > rect");
    const targetLine = plot.querySelector('[data-target-ratio="1"]');
    const markRect = mark?.getBoundingClientRect();
    const targetRect = targetLine?.getBoundingClientRect();
    const targetDistance = markRect && targetRect ? targetRect.left - markRect.left : NaN;
    const actualVisualRatio = markRect && targetDistance > 0 ? markRect.width / targetDistance : NaN;
    const expectedVisualRatio = Number.isFinite(value) && Number.isFinite(targetValue) && targetValue > 0 && Number.isFinite(maximumValue)
      ? Math.min(Math.max(value, 0), maximumValue) / targetValue
      : NaN;
    const record = {
      moduleId: module?.dataset.moduleId || "unknown", role, value, unit, text,
      shownPercent, expectedPercent, targetValue, maximumValue,
      actualVisualRatio, expectedVisualRatio,
      trackWidth: track?.getBoundingClientRect().width ?? null
    };
    progress.push(record);
    if (!Number.isFinite(value) || !Number.isFinite(shownPercent)) {
      issues.push({...record, reason: "progress value or current readout is not finite"});
    } else if (Math.abs(shownPercent - expectedPercent) > 0.11) {
      issues.push({...record, reason: "progress readout reports the clamped mark instead of the canonical value"});
    } else if (!Number.isFinite(actualVisualRatio) || !Number.isFinite(expectedVisualRatio)) {
      issues.push({...record, reason: "progress geometry or target ratio is not finite"});
    } else if (Math.abs(actualVisualRatio - expectedVisualRatio) > 0.03) {
      issues.push({...record, reason: "progress mark position contradicts its canonical distance to target"});
    }
  }

  const accessibility = [];
  const negativeZero = /(^|\s)-(?:[$€£¥]\s*)?0(?:[.,]0+)?(?=\s|$|[%$€£¥])/;
  for (const element of document.querySelectorAll("[data-bind]")) {
    const module = element.closest(".sync-module[data-module-id]");
    const valueId = element.getAttribute("data-bind") || "";
    const role = element.getAttribute("data-role") || "unknown";
    const label = element.getAttribute("data-accessible-label") || "";
    const accessibleValue = element.getAttribute("data-accessible-value") || "";
    const ariaLabel = element.getAttribute("aria-label") || "";
    const ariaValueText = element.getAttribute("aria-valuetext") || "";
    const accessibleRole = element.getAttribute("role") || "";
    const record = {
      moduleId: module?.dataset.moduleId || "unknown",
      role, valueId, accessibleRole, label, accessibleValue, ariaLabel, ariaValueText
    };
    accessibility.push(record);
    if (!label || !accessibleValue || !ariaLabel) {
      issues.push({...record, reason: "bound value lacks a complete synchronized accessible label/value"});
    } else if (valueId.includes("-") && ariaLabel.includes(valueId)) {
      issues.push({...record, reason: "accessible label exposes an internal canonical ID"});
    } else if (!ariaLabel.includes(label) || !ariaLabel.includes(accessibleValue)) {
      issues.push({...record, reason: "accessible label and value text do not match the synchronized human-readable value"});
    } else if (negativeZero.test(accessibleValue)) {
      issues.push({...record, reason: "accessible value exposes a misleading negative zero"});
    } else if (accessibleRole === "img" && ariaValueText) {
      issues.push({...record, reason: "role img must carry its value in the accessible name, not ignored aria-valuetext"});
    } else if (accessibleRole === "meter") {
      const now = Number(element.getAttribute("aria-valuenow"));
      const min = Number(element.getAttribute("aria-valuemin"));
      const max = Number(element.getAttribute("aria-valuemax"));
      if (ariaValueText !== accessibleValue || !Number.isFinite(now) || !Number.isFinite(min) || !Number.isFinite(max)) {
        issues.push({...record, reason: "meter lacks synchronized value text or finite range semantics"});
      }
    }
  }
  return {flows, bars, stacks, waterfalls, progress, accessibility, issues};
}
"""

RELATIONSHIP_CONTRAST_JS = r"""
() => {
  const root = document.documentElement;
  const parseColor = (raw) => {
    const value = String(raw || "").trim();
    const hex = value.match(/^#([0-9a-f]{6})$/i);
    if (hex) return [0, 2, 4].map((offset) => parseInt(hex[1].slice(offset, offset + 2), 16));
    const rgb = value.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/i);
    return rgb ? [Number(rgb[1]), Number(rgb[2]), Number(rgb[3])] : null;
  };
  const linear = (channel) => {
    const value = channel / 255;
    return value <= 0.04045 ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);
  };
  const luminance = (rgb) => 0.2126 * linear(rgb[0]) + 0.7152 * linear(rgb[1]) + 0.0722 * linear(rgb[2]);
  const ratio = (first, second) => {
    const a = luminance(first);
    const b = luminance(second);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  };
  const composite = (foreground, background, alpha) => foreground.map(
    (channel, index) => channel * alpha + background[index] * (1 - alpha)
  );
  const canvas = parseColor(getComputedStyle(root).getPropertyValue("--canvas"));
  const surface = parseColor(getComputedStyle(root).getPropertyValue("--surface"));
  const paths = [];
  const issues = [];
  for (const path of root.querySelectorAll(".relationship-path")) {
    const style = getComputedStyle(path);
    const stroke = parseColor(style.stroke);
    const opacity = Number(style.opacity);
    const strokeOpacity = Number(style.strokeOpacity);
    const alpha = Math.min(1, Math.max(0, opacity * strokeOpacity));
    const group = path.closest("[data-relationship-id]");
    const record = {
      id: group?.getAttribute("data-relationship-id") || path.id || "unknown",
      kind: group?.getAttribute("data-kind") || "",
      stroke: style.stroke,
      opacity,
      strokeOpacity,
      canvasRatio: null,
      surfaceRatio: null
    };
    if (!stroke || !canvas || !surface || !Number.isFinite(alpha)) {
      issues.push({...record, reason: "relationship color or opacity could not be resolved"});
    } else {
      record.canvasRatio = ratio(composite(stroke, canvas, alpha), canvas);
      record.surfaceRatio = ratio(composite(stroke, surface, alpha), surface);
      if (Math.min(record.canvasRatio, record.surfaceRatio) < 3) {
        issues.push({...record, reason: "resting relationship contrast is below 3:1"});
      }
    }
    paths.push(record);
  }
  return {paths, issues};
}
"""

RELATIONSHIP_CLEARANCE_JS = r"""
() => {
  const issues = [];
  let protectedCrossingCount = 0;
  const paintAlpha = (value) => {
    const normalized = String(value || "").trim().toLowerCase();
    if (!normalized || normalized === "none" || normalized === "transparent") return 0;
    const rgba = normalized.match(/^rgba\([^,]+,[^,]+,[^,]+,\s*([0-9.]+)\s*\)$/);
    if (rgba) return Number(rgba[1]);
    const slash = normalized.match(/\/\s*([0-9.]+)(%)?\s*\)$/);
    if (slash) return slash[2] ? Number(slash[1]) / 100 : Number(slash[1]);
    return 1;
  };
  const labels = [...document.querySelectorAll(".focus-region-label, .relationship-key-label")]
    .filter((element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity) > 0.01 && rect.width > 0 && rect.height > 0;
    })
    .map((element) => {
      const rect = element.getBoundingClientRect();
      const plaque = element.dataset.clearanceMask === "true"
        ? element.previousElementSibling
        : null;
      const plaqueRect = plaque?.matches?.(".focus-region-label-plaque")
        ? plaque.getBoundingClientRect()
        : null;
      const plaqueStyle = plaqueRect ? getComputedStyle(plaque) : null;
      const maskValid = Boolean(
        plaqueRect && plaqueStyle && plaqueStyle.display !== "none" &&
        plaqueStyle.visibility !== "hidden" && paintAlpha(plaqueStyle.fill) >= 0.99 &&
        Number(plaqueStyle.fillOpacity) >= 0.99 && Number(plaqueStyle.opacity) >= 0.99 &&
        plaqueRect.width > 0 && plaqueRect.height > 0 &&
        plaqueRect.left <= rect.left - 2 && plaqueRect.right >= rect.right + 2 &&
        plaqueRect.top <= rect.top - 2 && plaqueRect.bottom >= rect.bottom + 2
      );
      return {
        text: (element.textContent || "").trim(),
        rect,
        maskExpected: element.dataset.clearanceMask === "true",
        plaque,
        plaqueRect,
        maskValid
      };
    });
  const maskIssues = labels
    .filter((label) => label.maskExpected && !label.maskValid)
    .map((label) => ({label: label.text, reason: "clearance plaque does not fully and opaquely cover the label"}));
  for (const relationship of document.querySelectorAll("[data-relationship-id]")) {
    const path = relationship.querySelector(".relationship-path");
    if (!path || typeof path.getTotalLength !== "function") continue;
    const matrix = path.getScreenCTM();
    if (!matrix) continue;
    const length = path.getTotalLength();
    for (let distance = 0; distance <= length; distance += 3) {
      const local = path.getPointAtLength(Math.min(distance, length));
      const point = new DOMPoint(local.x, local.y).matrixTransform(matrix);
      for (const label of labels) {
        const rect = label.rect;
        if (
          point.x >= rect.left - 2 && point.x <= rect.right + 2 &&
          point.y >= rect.top - 2 && point.y <= rect.bottom + 2
        ) {
          const maskPaintedAfterPath = label.maskValid && Boolean(
            path.compareDocumentPosition(label.plaque) & Node.DOCUMENT_POSITION_FOLLOWING
          );
          if (maskPaintedAfterPath) {
            protectedCrossingCount += 1;
            continue;
          }
          issues.push({
            relationshipId: relationship.dataset.relationshipId || "unknown",
            label: label.text,
            x: Number(point.x.toFixed(2)),
            y: Number(point.y.toFixed(2))
          });
          distance = length + 1;
          break;
        }
      }
    }
  }
  return {
    labelCount: labels.length,
    relationshipCount: document.querySelectorAll("[data-relationship-id]").length,
    protectedCrossingCount,
    maskIssues,
    issues
  };
}
"""

GEOMETRY_TOLERANCE_PX = 3.0
TEXT_OVERLAP_RATIO = 0.20
TEXT_OVERLAP_MIN_PX = 4.0
MIN_MODULE_FOOTPRINT_WIDTH_RATIO = 0.70
MIN_MODULE_FOOTPRINT_HEIGHT_RATIO = 0.70


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit deterministic synchronization behavior in a standalone SVG with Chromium."
    )
    parser.add_argument("svg", type=Path, help="Standalone SVG artifact")
    parser.add_argument("--report", "--output", dest="report", type=Path, help="Optional JSON report path")
    parser.add_argument("--screenshot", type=Path, help="Optional initial-state overview screenshot")
    parser.add_argument("--timeout-ms", type=int, default=15_000, help="Navigation and runtime timeout")
    parser.add_argument("--viewport-width", type=int, default=1600)
    parser.add_argument("--viewport-height", type=int, default=1000)
    parser.add_argument("--chromium-executable", type=Path, help="Optional Chromium-compatible executable")
    parser.add_argument("--headed", action="store_true", help="Show the browser while auditing")
    parser.add_argument(
        "--compact-report",
        action="store_true",
        help="Write counts, pass IDs, and complete failures instead of successful check details",
    )
    parser.add_argument("--json", action="store_true", help="Print the selected JSON report")
    parser.add_argument(INTERNAL_WORKER_FLAG, action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


class Audit:
    def __init__(self, artifact: Path) -> None:
        self.artifact = artifact
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.checks: list[dict[str, Any]] = []
        self.snapshots: dict[str, Any] = {
            "initial": None,
            "scenarios": {},
            "sources": {},
            "zeroFlows": {},
            "zeroFlowDiagnostics": {},
            "focus": {},
            "timeline": [],
            "reducedMotion": None,
        }
        self.metrics: dict[str, Any] = {
            "scenarioCount": 0,
            "sourcePerturbationCount": 0,
            "zeroFlowBoundaryCount": 0,
            "focusGroupCount": 0,
            "focusReadabilityCheckCount": 0,
            "focusReadabilityIssueCount": 0,
            "timelineSampleCount": 0,
            "bindingCount": 0,
            "negativeControlComparisons": 0,
            "sharedRevisionCases": 0,
            "geometryCheckCount": 0,
            "quantitativeSemanticsCheckCount": 0,
            "quantitativeSemanticsIssueCount": 0,
            "accessibilityTreeCheckCount": 0,
            "accessibilityTreeIssueCount": 0,
            "relationshipContrastCheckCount": 0,
            "relationshipContrastIssueCount": 0,
            "relationshipStateCheckCount": 0,
            "relationshipStateIssueCount": 0,
            "relationshipClearanceCheckCount": 0,
            "relationshipClearanceIssueCount": 0,
            "realInputCheckCount": 0,
            "accessibleBindingCount": 0,
            "visibleModuleCount": 0,
            "visibleTextCount": 0,
            "visibleBoundMarkCount": 0,
            "geometryEscapeCount": 0,
            "textOverlapCount": 0,
            "headerBodyOverlapCount": 0,
            "invalidTextCount": 0,
            "moduleFootprintWidthRatio": None,
            "moduleFootprintHeightRatio": None,
            "moduleFootprintAreaRatio": None,
        }
        self.browser_errors: dict[str, list[str]] = {
            "console": [],
            "page": [],
            "request": [],
        }

    def finish_check(
        self,
        check_id: str,
        errors: list[str],
        details: dict[str, Any] | None = None,
    ) -> None:
        entry: dict[str, Any] = {"id": check_id, "ok": not errors}
        if details:
            entry["details"] = details
        if errors:
            entry["errors"] = errors
            self.failures.extend(f"{check_id}: {message}" for message in errors)
        self.checks.append(entry)

    def fail(self, check_id: str, message: str) -> None:
        self.finish_check(check_id, [message])

    def report(self, screenshot: Path | None, report_path: Path | None) -> dict[str, Any]:
        return {
            "ok": not self.failures,
            "artifact": str(self.artifact),
            "report": str(report_path) if report_path else None,
            "screenshot": str(screenshot) if screenshot else None,
            "failures": self.failures,
            "warnings": self.warnings,
            "browserErrors": self.browser_errors,
            "metrics": self.metrics,
            "checks": self.checks,
            "snapshots": self.snapshots,
        }


def close_number(actual: Any, expected: Any, tolerance: float = 1e-8) -> bool:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return False
    try:
        left = float(actual)
        right = float(expected)
    except (TypeError, ValueError):
        return False
    if not math.isfinite(left) or not math.isfinite(right):
        return False
    scale = max(abs(left), abs(right))
    absolute_tolerance = max(math.ulp(scale) * 32, math.ulp(0.0))
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=absolute_tolerance)


def same_semantic_number(actual: Any, expected: Any) -> bool:
    """Compare canonical state exactly while treating signed zero as zero."""

    if isinstance(actual, bool) or isinstance(expected, bool):
        return False
    try:
        left = float(actual)
        right = float(expected)
    except (TypeError, ValueError):
        return False
    return math.isfinite(left) and math.isfinite(right) and left == right


def numeric_map_errors(actual: Any, expected: dict[str, float], label: str) -> list[str]:
    if not isinstance(actual, dict):
        return [f"{label} is not an object"]
    errors: list[str] = []
    if set(actual) != set(expected):
        errors.append(
            f"{label} keys differ; missing={sorted(set(expected) - set(actual))}, "
            f"extra={sorted(set(actual) - set(expected))}"
        )
    for key in sorted(set(actual) & set(expected)):
        if not same_semantic_number(actual[key], expected[key]):
            errors.append(f"{label}.{key} is {actual[key]!r}, expected {expected[key]!r}")
    return errors


def eval_compute(node: Any, values: dict[str, float]) -> float:
    if isinstance(node, (int, float)) and not isinstance(node, bool):
        return float(node)
    if isinstance(node, dict) and set(node) == {"ref"}:
        return float(values[node["ref"]])
    if not isinstance(node, dict) or not isinstance(node.get("args"), list):
        raise ValueError("invalid compute node")
    args = [eval_compute(item, values) for item in node["args"]]
    op = node.get("op")
    if op == "add":
        result = 0.0
        for value in args:
            result += value
    elif op == "subtract":
        remainder = 0.0
        for value in args[1:]:
            remainder += value
        result = args[0] - remainder
    elif op == "multiply":
        result = 1.0
        for value in args:
            result *= value
    elif op == "divide":
        if args[1] == 0:
            raise ValueError("division by zero")
        result = args[0] / args[1]
    elif op == "min":
        result = min(args)
    elif op == "max":
        result = max(args)
    elif op == "clamp":
        result = min(max(args[0], args[1]), args[2])
    elif op == "round":
        places = math.trunc(args[1]) if len(args) > 1 else 0
        factor = 10**places
        result = math.floor((args[0] + sys.float_info.epsilon) * factor + 0.5) / factor
    else:
        raise ValueError(f"unsupported operation: {op}")
    if not math.isfinite(result):
        raise ValueError("derived computation produced a non-finite result")
    return result


def compute_state(plan: dict[str, Any], source: dict[str, float]) -> tuple[dict[str, float], dict[str, float]]:
    source_values = {item["id"]: float(source[item["id"]]) for item in plan["concepts"]}
    values = dict(source_values)
    derived: dict[str, float] = {}
    pending = {item["id"]: item for item in plan.get("derived", [])}
    while pending:
        progressed = False
        for item_id, item in list(pending.items()):
            if set(item["dependsOn"]) <= set(values):
                value = eval_compute(item["compute"], values)
                values[item_id] = value
                derived[item_id] = value
                del pending[item_id]
                progressed = True
        if not progressed:
            raise ValueError("derived dependency graph cannot be resolved")
    return source_values, derived


def scenario_state(plan: dict[str, Any], scenario_id: str) -> tuple[dict[str, float], dict[str, float]]:
    source = {item["id"]: float(item["default"]) for item in plan["concepts"]}
    scenario = next(item for item in plan["scenarios"] if item["id"] == scenario_id)
    source.update({key: float(value) for key, value in scenario["values"].items()})
    return compute_state(plan, source)


def all_values(capture: dict[str, Any]) -> dict[str, float]:
    snapshot = capture["snapshot"]
    return {**snapshot["sourceValues"], **snapshot["derivedValues"]}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def has_canonical_key_order(value: Any) -> bool:
    """Check recursive key order without imposing Python's float spelling on JS JSON."""

    if isinstance(value, dict):
        keys = list(value)
        return keys == sorted(keys) and all(has_canonical_key_order(item) for item in value.values())
    if isinstance(value, list):
        return all(has_canonical_key_order(item) for item in value)
    return True


def binding_semantics(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "currentValue": record.get("currentValue"),
        "rendered": record.get("rendered"),
        "syncValue": record.get("syncValue"),
        "syncRendered": record.get("syncRendered"),
    }


def capture(page: Page) -> dict[str, Any]:
    return page.evaluate(CAPTURE_JS)


def invoke(page: Page, method: str, *args: Any) -> dict[str, Any]:
    return page.evaluate(INVOKE_JS, {"method": method, "args": list(args)})


def invocation_errors(outcome: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    changed = outcome["before"] != outcome["after"]
    events = outcome.get("events", [])
    expected_count = 1 if changed else 0
    if len(events) != expected_count:
        errors.append(f"expected {expected_count} svg-sync-change event(s), observed {len(events)}")
    try:
        after_snapshot = json.loads(outcome["after"])
    except json.JSONDecodeError as exc:
        return errors + [f"serializeSnapshot returned invalid JSON: {exc}"]
    if outcome.get("result") != after_snapshot:
        errors.append("method return value differs from the post-call snapshot")
    if changed and events:
        event = events[0]
        if event.get("detail") != after_snapshot:
            errors.append("event detail differs from the committed snapshot")
        revision = str(after_snapshot.get("revision"))
        if event.get("rootRevision") != revision:
            errors.append("root revision was not committed before the event")
        if event.get("valueMismatches"):
            errors.append(f"event observed stale bound values: {event['valueMismatches']}")
    return errors


def validate_capture(
    audit: Audit,
    check_id: str,
    capture_data: dict[str, Any],
    plan: dict[str, Any],
    expected_source: dict[str, float],
    expected_derived: dict[str, float],
    scenario_id: str | None,
    focus_id: str | None,
    time_ms: float,
    phase_id: str | None,
    phase_progress: float,
    motion: str,
) -> None:
    errors: list[str] = []
    snapshot = capture_data.get("snapshot", {})
    errors.extend(numeric_map_errors(snapshot.get("sourceValues"), expected_source, "sourceValues"))
    errors.extend(numeric_map_errors(snapshot.get("derivedValues"), expected_derived, "derivedValues"))
    if snapshot.get("version") != 1:
        errors.append("snapshot version must equal 1")
    if snapshot.get("compositionId") != plan["compositionId"]:
        errors.append("snapshot compositionId differs from the plan")
    if snapshot.get("scenarioId") != scenario_id:
        errors.append(f"scenarioId is {snapshot.get('scenarioId')!r}, expected {scenario_id!r}")
    if snapshot.get("focusId") != focus_id:
        errors.append(f"focusId is {snapshot.get('focusId')!r}, expected {focus_id!r}")
    if not close_number(snapshot.get("timeMs"), time_ms):
        errors.append(f"timeMs is {snapshot.get('timeMs')!r}, expected {time_ms!r}")
    if snapshot.get("phaseId") != phase_id:
        errors.append(f"phaseId is {snapshot.get('phaseId')!r}, expected {phase_id!r}")
    if not close_number(snapshot.get("phaseProgress"), phase_progress):
        errors.append(
            f"phaseProgress is {snapshot.get('phaseProgress')!r}, expected {phase_progress!r}"
        )
    if snapshot.get("motion") != motion:
        errors.append(f"motion is {snapshot.get('motion')!r}, expected {motion!r}")
    if not isinstance(snapshot.get("revision"), int) or snapshot["revision"] < 0:
        errors.append("snapshot revision must be a non-negative integer")

    serialized = capture_data.get("serialized")
    try:
        parsed = json.loads(serialized)
        if parsed != snapshot:
            errors.append("serializeSnapshot differs from snapshot()")
        if not has_canonical_key_order(parsed):
            errors.append("serializeSnapshot is not canonical key-sorted JSON")
    except (TypeError, json.JSONDecodeError) as exc:
        errors.append(f"serializeSnapshot is invalid JSON: {exc}")

    state = capture_data.get("state", {})
    errors.extend(numeric_map_errors(state.get("sourceValues"), expected_source, "getState.sourceValues"))
    errors.extend(numeric_map_errors(state.get("derivedValues"), expected_derived, "getState.derivedValues"))

    root = capture_data.get("root", {})
    expected_revision = str(snapshot.get("revision"))
    if root.get("revision") != expected_revision:
        errors.append("root data-state-revision differs from the snapshot")
    if root.get("scenarioId") != (scenario_id or "custom"):
        errors.append("root data-current-scenario differs from the snapshot")
    if root.get("focusId") != (focus_id or ""):
        errors.append("root data-focus-id differs from the snapshot")
    try:
        root_time = float(root.get("timeMs"))
    except (TypeError, ValueError):
        errors.append("root data-time-ms is not numeric")
    else:
        if not close_number(root_time, time_ms):
            errors.append("root data-time-ms differs from the snapshot")
    if root.get("phaseId") != (phase_id or ""):
        errors.append("root data-phase-id differs from the snapshot")
    try:
        root_phase_progress = float(root.get("phaseProgress"))
    except (TypeError, ValueError):
        errors.append("root data-phase-progress is not numeric")
    else:
        if not close_number(root_phase_progress, phase_progress):
            errors.append(
                f"root data-phase-progress is {root_phase_progress!r}, expected {phase_progress!r}"
            )
    if root.get("ready") != "true":
        errors.append("root data-sync-ready is not true")

    expected_values = {**expected_source, **expected_derived}
    expected_binding_count = sum(len(module["bindings"]) for module in plan["modules"])
    records = capture_data.get("bindings", [])
    if len(records) < expected_binding_count:
        errors.append(f"only {len(records)} binding targets exist; expected at least {expected_binding_count}")
    for record in records:
        value_id = record.get("valueId")
        if value_id not in expected_values:
            errors.append(f"binding {record.get('key')} references unknown value {value_id!r}")
            continue
        if not same_semantic_number(record.get("currentValue"), expected_values[value_id]):
            errors.append(
                f"binding {record.get('key')} has data-current-value={record.get('currentValue')!r}, "
                f"expected {expected_values[value_id]!r}"
            )
        if record.get("channel") in {"width", "height", "x", "y", "r", "opacity"} and not close_number(
            record.get("rendered"), record.get("syncRendered")
        ):
            errors.append(
                f"binding {record.get('key')} rendered attribute was overwritten by layout: "
                f"{record.get('rendered')!r} differs from canonical {record.get('syncRendered')!r}"
            )
        try:
            binding_revision = int(record.get("revision"))
        except (TypeError, ValueError):
            errors.append(f"binding {record.get('key')} has a non-integer revision")
        else:
            if binding_revision < 0 or binding_revision > int(snapshot.get("revision", -1)):
                errors.append(
                    f"binding {record.get('key')} has invalid revision {binding_revision}; "
                    f"root revision is {expected_revision}"
                )

    focused_modules = set()
    if focus_id is not None:
        focus = next((item for item in plan.get("focusGroups", []) if item["id"] == focus_id), None)
        if focus is None:
            errors.append(f"expected focus group {focus_id!r} is absent from the plan")
        else:
            focused_modules = set(focus["moduleIds"])
    modules = capture_data.get("modules", {})
    for module in plan["modules"]:
        dom = modules.get(module["id"])
        if dom is None:
            errors.append(f"module {module['id']!r} is absent from the DOM")
            continue
        expected_focused = "true" if focus_id is None or module["id"] in focused_modules else "false"
        if dom.get("focused") != expected_focused:
            errors.append(
                f"module {module['id']!r} data-focused is {dom.get('focused')!r}, expected {expected_focused!r}"
            )
        if dom.get("assetType") != module["assetType"]:
            errors.append(f"module {module['id']!r} asset type differs from the plan")
        declared_focus = module.get("focusGroups", [])
        controls = dom.get("focusControls")
        if declared_focus:
            if not isinstance(controls, list):
                errors.append(f"module {module['id']!r} lacks its separate focus toggle buttons")
            else:
                actual_targets = [control.get("focusId") for control in controls if isinstance(control, dict)]
                if actual_targets != declared_focus:
                    errors.append(
                        f"module {module['id']!r} focus control targets {actual_targets!r}, "
                        f"expected every membership {declared_focus!r}"
                    )
                for control in controls:
                    if not isinstance(control, dict):
                        continue
                    control_focus = control.get("focusId")
                    if control.get("role") != "button" or control.get("tabIndex") != 0:
                        errors.append(f"module {module['id']!r} focus control is not a keyboard-reachable button")
                    if not control.get("label"):
                        errors.append(f"module {module['id']!r} focus control lacks an accessible name")
                    expected_pressed = "true" if focus_id == control_focus else "false"
                    if control.get("pressed") != expected_pressed:
                        errors.append(
                            f"module {module['id']!r} focus control for {control_focus!r} aria-pressed is "
                            f"{control.get('pressed')!r}, expected {expected_pressed!r}"
                        )
        elif controls:
            errors.append(f"module {module['id']!r} has undeclared focus toggle buttons")

    audit.finish_check(
        check_id,
        errors,
        {
            "revision": snapshot.get("revision"),
            "scenarioId": scenario_id,
            "focusId": focus_id,
            "timeMs": time_ms,
            "phaseId": phase_id,
        },
    )


def compare_transition(
    audit: Audit,
    check_id: str,
    before: dict[str, Any],
    after: dict[str, Any],
    require_changed_binding: bool = False,
) -> None:
    errors: list[str] = []
    before_values = all_values(before)
    after_values = all_values(after)
    changed_values = {
        key
        for key in set(before_values) | set(after_values)
        if key not in before_values
        or key not in after_values
        or not same_semantic_number(before_values[key], after_values[key])
    }
    before_records = {item["key"]: item for item in before["bindings"]}
    after_records = {item["key"]: item for item in after["bindings"]}
    if set(before_records) != set(after_records):
        errors.append("the binding target set changed during a state transaction")
    changed_records: list[dict[str, Any]] = []
    unaffected_count = 0
    for key in sorted(set(before_records) & set(after_records)):
        old = before_records[key]
        new = after_records[key]
        changed = binding_semantics(old) != binding_semantics(new)
        should_change = new["valueId"] in changed_values
        if should_change and not changed:
            errors.append(f"affected binding {key} did not update")
        if not should_change and changed:
            errors.append(f"unaffected binding {key} changed")
        if changed:
            changed_records.append(new)
        else:
            unaffected_count += 1
    if require_changed_binding and not changed_records:
        errors.append("the perturbation changed no bound representation")
    if changed_records:
        expected_revision = str(after["snapshot"]["revision"])
        revisions = sorted({item.get("revision") for item in changed_records})
        if revisions != [expected_revision]:
            errors.append(f"changed bindings do not share revision {expected_revision}: {revisions}")
        changed_modules = {item["moduleId"] for item in changed_records}
        if len(changed_modules) >= 2:
            audit.metrics["sharedRevisionCases"] += 1
    audit.metrics["negativeControlComparisons"] += unaffected_count
    audit.finish_check(
        check_id,
        errors,
        {
            "changedValueIds": sorted(changed_values),
            "changedBindingCount": len(changed_records),
            "unaffectedBindingCount": unaffected_count,
        },
    )


def idempotence_errors(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if before["serialized"] != after["serialized"]:
        errors.append("the repeated call changed the serialized snapshot")
    if before["root"] != after["root"]:
        errors.append("the repeated call changed root state attributes")
    if before["bindings"] != after["bindings"]:
        errors.append("the repeated call drifted bound DOM state")
    if before["modules"] != after["modules"]:
        errors.append("the repeated call drifted module focus state")
    if before.get("controls") != after.get("controls"):
        errors.append("the repeated call drifted control labels or states")
    return errors


def candidate_values(definition: dict[str, Any], current: float) -> list[float]:
    domain = definition.get("domain")
    if isinstance(domain, list) and len(domain) == 2:
        low, high = float(domain[0]), float(domain[1])
        values = [low, high, low + 0.2 * (high - low), low + 0.5 * (high - low), low + 0.8 * (high - low)]
    else:
        delta = max(abs(current) * 0.25, 1.0)
        values = [current + delta, current - delta]
    return [value for value in values if math.isfinite(value) and not same_semantic_number(value, current)]


def choose_perturbation(
    plan: dict[str, Any],
    definition: dict[str, Any],
    baseline_source: dict[str, float],
    baseline_derived: dict[str, float],
) -> tuple[float, dict[str, float], dict[str, float]]:
    baseline_values = {**baseline_source, **baseline_derived}
    binding_modules: dict[str, set[str]] = {}
    for module in plan["modules"]:
        for binding in module["bindings"]:
            binding_modules.setdefault(binding["value"], set()).add(module["id"])
    best: tuple[tuple[int, int, float], float, dict[str, float], dict[str, float]] | None = None
    current = baseline_source[definition["id"]]
    for candidate in candidate_values(definition, current):
        source = dict(baseline_source)
        source[definition["id"]] = candidate
        next_source, next_derived = compute_state(plan, source)
        next_values = {**next_source, **next_derived}
        changed_bound_ids = {
            value_id
            for value_id in binding_modules
            if not same_semantic_number(baseline_values[value_id], next_values[value_id])
        }
        changed_modules = set().union(*(binding_modules[value_id] for value_id in changed_bound_ids)) if changed_bound_ids else set()
        score = (len(changed_modules), len(changed_bound_ids), abs(candidate - current))
        item = (score, candidate, next_source, next_derived)
        if best is None or item[0] > best[0]:
            best = item
    if best is None:
        raise ValueError(f"no legal perturbation exists for {definition['id']!r}")
    return best[1], best[2], best[3]


def attach_error_collectors(page: Page, audit: Audit, label: str) -> None:
    def on_console(message: Any) -> None:
        if message.type == "error":
            audit.browser_errors["console"].append(f"{label}: {message.text}")

    def on_page_error(error: Any) -> None:
        audit.browser_errors["page"].append(f"{label}: {error}")

    def on_request(request: Any) -> None:
        if urlparse(request.url).scheme.lower() in {"http", "https", "ws", "wss"}:
            audit.browser_errors["request"].append(f"{label}: unexpected network request {request.url}")

    def on_request_failed(request: Any) -> None:
        audit.browser_errors["request"].append(
            f"{label}: request failed {request.url}: {request.failure or 'unknown error'}"
        )

    def on_response(response: Any) -> None:
        if urlparse(response.url).scheme.lower() in {"http", "https"} and response.status >= 400:
            audit.browser_errors["request"].append(
                f"{label}: HTTP {response.status} for {response.url}"
            )

    page.on("console", on_console)
    page.on("pageerror", on_page_error)
    page.on("request", on_request)
    page.on("requestfailed", on_request_failed)
    page.on("response", on_response)


def geometry_issue_message(issue: dict[str, Any]) -> str:
    issue_type = issue.get("type")
    module_id = issue.get("moduleId", "unknown-module")
    if issue_type == "missing-frame":
        return f"module {module_id!r} has no visible .module-frame"
    if issue_type == "invalid-text":
        return (
            f"module {module_id!r} text {issue.get('element')!r} is invalid: "
            f"{issue.get('reason')} ({issue.get('text')!r})"
        )
    if issue_type == "frame-escape":
        outside = issue.get("outside", {})
        sides = ", ".join(
            f"{side}={value}px"
            for side, value in outside.items()
            if isinstance(value, (int, float)) and value > GEOMETRY_TOLERANCE_PX
        )
        return (
            f"module {module_id!r} visible {issue.get('kind')} {issue.get('element')!r} "
            f"escapes .module-frame ({sides or 'outside frame'})"
        )
    if issue_type == "text-overlap":
        return (
            f"module {module_id!r} text {issue.get('first')!r} overlaps "
            f"{issue.get('second')!r} by {issue.get('overlapRatio')!r} of the smaller box "
            f"({issue.get('intersectionWidth')}x{issue.get('intersectionHeight')}px)"
        )
    if issue_type == "header-body-overlap":
        return (
            f"module {module_id!r} body element {issue.get('element')!r} crosses above "
            f"data-content-top={issue.get('contentTop')!r} by {issue.get('overlapPx')!r}px"
        )
    return f"module {module_id!r} has an unknown geometry issue: {issue!r}"


def audit_visual_geometry(page: Page, audit: Audit, check_id: str = "visual-geometry") -> None:
    details = page.evaluate(
        GEOMETRY_AUDIT_JS,
        {
            "tolerancePx": GEOMETRY_TOLERANCE_PX,
            "overlapRatioThreshold": TEXT_OVERLAP_RATIO,
            "overlapMinPx": TEXT_OVERLAP_MIN_PX,
        },
    )
    issues = details.get("issues", []) if isinstance(details, dict) else []
    errors = [geometry_issue_message(issue) for issue in issues if isinstance(issue, dict)]
    footprint = details.get("footprint") if isinstance(details, dict) else None
    visible_modules = details.get("visibleModuleCount", 0) if isinstance(details, dict) else 0
    if not isinstance(visible_modules, int) or visible_modules < 1:
        errors.append("no visible .sync-module[data-module-id] elements were found")
    if not isinstance(footprint, dict):
        errors.append("module footprint could not be measured")
        width_ratio = None
        height_ratio = None
        area_ratio = None
    else:
        width_ratio = footprint.get("widthRatio")
        height_ratio = footprint.get("heightRatio")
        area_ratio = footprint.get("areaRatio")
        if not isinstance(width_ratio, (int, float)) or width_ratio < MIN_MODULE_FOOTPRINT_WIDTH_RATIO:
            errors.append(
                f"module footprint spans only {width_ratio!r} of the SVG width; "
                f"required at least {MIN_MODULE_FOOTPRINT_WIDTH_RATIO}"
            )
        if not isinstance(height_ratio, (int, float)) or height_ratio < MIN_MODULE_FOOTPRINT_HEIGHT_RATIO:
            errors.append(
                f"module footprint spans only {height_ratio!r} of the SVG height; "
                f"required at least {MIN_MODULE_FOOTPRINT_HEIGHT_RATIO}"
            )

    issue_types = [issue.get("type") for issue in issues if isinstance(issue, dict)]
    prior_width = audit.metrics.get("moduleFootprintWidthRatio")
    prior_height = audit.metrics.get("moduleFootprintHeightRatio")
    prior_area = audit.metrics.get("moduleFootprintAreaRatio")
    audit.metrics.update(
        {
            "geometryCheckCount": audit.metrics["geometryCheckCount"] + 1,
            "visibleModuleCount": max(audit.metrics.get("visibleModuleCount", 0), visible_modules),
            "visibleTextCount": max(
                audit.metrics.get("visibleTextCount", 0),
                details.get("visibleTextCount", 0) if isinstance(details, dict) else 0,
            ),
            "visibleBoundMarkCount": max(
                audit.metrics.get("visibleBoundMarkCount", 0),
                details.get("visibleBoundMarkCount", 0) if isinstance(details, dict) else 0,
            ),
            "geometryEscapeCount": audit.metrics.get("geometryEscapeCount", 0)
            + issue_types.count("frame-escape"),
            "textOverlapCount": audit.metrics.get("textOverlapCount", 0)
            + issue_types.count("text-overlap"),
            "headerBodyOverlapCount": audit.metrics.get("headerBodyOverlapCount", 0)
            + issue_types.count("header-body-overlap"),
            "invalidTextCount": audit.metrics.get("invalidTextCount", 0)
            + issue_types.count("invalid-text"),
            "moduleFootprintWidthRatio": min(
                value for value in (prior_width, width_ratio) if isinstance(value, (int, float))
            )
            if any(isinstance(value, (int, float)) for value in (prior_width, width_ratio))
            else None,
            "moduleFootprintHeightRatio": min(
                value for value in (prior_height, height_ratio) if isinstance(value, (int, float))
            )
            if any(isinstance(value, (int, float)) for value in (prior_height, height_ratio))
            else None,
            "moduleFootprintAreaRatio": min(
                value for value in (prior_area, area_ratio) if isinstance(value, (int, float))
            )
            if any(isinstance(value, (int, float)) for value in (prior_area, area_ratio))
            else None,
        }
    )
    audit.finish_check(
        check_id,
        errors,
        {
            "thresholds": {
                "frameTolerancePx": GEOMETRY_TOLERANCE_PX,
                "textOverlapRatio": TEXT_OVERLAP_RATIO,
                "textOverlapMinPx": TEXT_OVERLAP_MIN_PX,
                "minimumFootprintWidthRatio": MIN_MODULE_FOOTPRINT_WIDTH_RATIO,
                "minimumFootprintHeightRatio": MIN_MODULE_FOOTPRINT_HEIGHT_RATIO,
            },
            "root": details.get("root") if isinstance(details, dict) else None,
            "rootContent": details.get("rootContent") if isinstance(details, dict) else None,
            "footprint": footprint,
            "visibleModuleCount": visible_modules,
            "visibleTextCount": details.get("visibleTextCount", 0) if isinstance(details, dict) else 0,
            "visibleBoundMarkCount": details.get("visibleBoundMarkCount", 0) if isinstance(details, dict) else 0,
            "modules": details.get("modules", []) if isinstance(details, dict) else [],
            "issues": issues,
        },
    )


def audit_quantitative_semantics(page: Page, audit: Audit, check_id: str) -> None:
    details = page.evaluate(QUANTITATIVE_SEMANTICS_JS)
    issues = details.get("issues", []) if isinstance(details, dict) else []
    errors = [
        (
            f"module {issue.get('moduleId')!r} role {issue.get('role')!r}: "
            f"{issue.get('reason')} (value={issue.get('value')}, direction={issue.get('direction')!r}, "
            f"strokeWidth={issue.get('strokeWidth')}, text={issue.get('text')!r})"
        )
        for issue in issues
        if isinstance(issue, dict)
    ]
    audit.metrics["quantitativeSemanticsCheckCount"] += 1
    audit.metrics["quantitativeSemanticsIssueCount"] += len(errors)
    audit.finish_check(
        check_id,
        errors,
        {
            "flowCount": len(details.get("flows", [])) if isinstance(details, dict) else 0,
            "barCount": len(details.get("bars", [])) if isinstance(details, dict) else 0,
            "stackCount": len(details.get("stacks", [])) if isinstance(details, dict) else 0,
            "waterfallCount": len(details.get("waterfalls", [])) if isinstance(details, dict) else 0,
            "progressCount": len(details.get("progress", [])) if isinstance(details, dict) else 0,
            "accessibleBindingCount": len(details.get("accessibility", [])) if isinstance(details, dict) else 0,
            "flows": details.get("flows", []) if isinstance(details, dict) else [],
            "bars": details.get("bars", []) if isinstance(details, dict) else [],
            "stacks": details.get("stacks", []) if isinstance(details, dict) else [],
            "waterfalls": details.get("waterfalls", []) if isinstance(details, dict) else [],
            "progress": details.get("progress", []) if isinstance(details, dict) else [],
            "accessibility": details.get("accessibility", []) if isinstance(details, dict) else [],
            "issues": issues,
        },
    )


def audit_relationship_contrast(page: Page, audit: Audit, check_id: str) -> None:
    details = page.evaluate(RELATIONSHIP_CONTRAST_JS)
    issues = details.get("issues", []) if isinstance(details, dict) else []
    errors = [
        (
            f"relationship {issue.get('id')!r}: {issue.get('reason')} "
            f"(stroke={issue.get('stroke')!r}, opacity={issue.get('opacity')}, "
            f"canvasRatio={issue.get('canvasRatio')}, surfaceRatio={issue.get('surfaceRatio')})"
        )
        for issue in issues
        if isinstance(issue, dict)
    ]
    audit.metrics["relationshipContrastCheckCount"] += 1
    audit.metrics["relationshipContrastIssueCount"] += len(errors)
    audit.finish_check(
        check_id,
        errors,
        {
            "pathCount": len(details.get("paths", [])) if isinstance(details, dict) else 0,
            "minimumContrast": 3.0,
            "paths": details.get("paths", []) if isinstance(details, dict) else [],
            "issues": issues,
        },
    )


def audit_relationship_clearance(page: Page, audit: Audit, check_id: str) -> None:
    details = page.evaluate(RELATIONSHIP_CLEARANCE_JS)
    issues = details.get("issues", []) if isinstance(details, dict) else []
    mask_issues = details.get("maskIssues", []) if isinstance(details, dict) else []
    errors = [
        (
            f"relationship {issue.get('relationshipId')!r} crosses visible label "
            f"{issue.get('label')!r} near ({issue.get('x')}, {issue.get('y')})"
        )
        for issue in issues
        if isinstance(issue, dict)
    ]
    errors.extend(
        f"focus label {issue.get('label')!r}: {issue.get('reason')}"
        for issue in mask_issues
        if isinstance(issue, dict)
    )
    audit.metrics["relationshipClearanceCheckCount"] += 1
    audit.metrics["relationshipClearanceIssueCount"] += len(errors)
    audit.finish_check(check_id, errors, details if isinstance(details, dict) else {})


def audit_relationship_state(
    page: Page,
    audit: Audit,
    plan: dict[str, Any],
    focus_id: str | None,
    check_id: str,
    *,
    reduced_motion: bool = False,
) -> None:
    records = page.evaluate(
        r"""
        () => {
          const root = document.documentElement;
          const progress = Number(root.getAttribute("data-phase-progress") || 0);
          return [...root.querySelectorAll("[data-relationship-id]")].map((group) => {
            const path = group.querySelector(".relationship-path");
            const pulse = group.querySelector("[data-relationship-pulse]");
            let distance = null;
            if (path && pulse && path.getTotalLength) {
              const length = path.getTotalLength();
              const expected = path.getPointAtLength(length * Math.min(Math.max(progress, 0), 1));
              const actualX = Number(pulse.getAttribute("cx"));
              const actualY = Number(pulse.getAttribute("cy"));
              if (Number.isFinite(actualX) && Number.isFinite(actualY)) {
                distance = Math.hypot(actualX - expected.x, actualY - expected.y);
              }
            }
            return {
              id: group.getAttribute("data-relationship-id"),
              source: group.getAttribute("data-source-module"),
              target: group.getAttribute("data-target-module"),
              kind: group.getAttribute("data-kind"),
              label: group.getAttribute("aria-label") || "",
              active: group.getAttribute("data-active") === "true",
              pulseOpacity: pulse ? Number(getComputedStyle(pulse).opacity) : null,
              pulseDistance: distance
            };
          });
        }
        """
    )
    declared = {item["id"]: item for item in plan.get("relationships", [])}
    actual = {
        item.get("id"): item
        for item in records
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    errors: list[str] = []
    if set(actual) != set(declared):
        errors.append(
            f"relationship IDs differ; missing={sorted(set(declared) - set(actual))}, "
            f"extra={sorted(set(actual) - set(declared))}"
        )
    focus_modules = set()
    if focus_id is not None:
        focus = next((item for item in plan.get("focusGroups", []) if item["id"] == focus_id), None)
        if focus is None:
            errors.append(f"unknown focus group {focus_id!r} while checking relationships")
        else:
            focus_modules = set(focus["moduleIds"])
    for relationship_id in sorted(set(actual) & set(declared)):
        record = actual[relationship_id]
        expected = declared[relationship_id]
        for field in ("source", "target", "kind", "label"):
            if record.get(field) != expected[field]:
                errors.append(
                    f"relationship {relationship_id!r} {field} is {record.get(field)!r}, "
                    f"expected {expected[field]!r}"
                )
        expected_active = False
        if focus_modules:
            if len(focus_modules) == 1:
                expected_active = bool(
                    expected["source"] in focus_modules or expected["target"] in focus_modules
                )
            else:
                expected_active = bool(
                    expected["source"] in focus_modules and expected["target"] in focus_modules
                )
        if record.get("active") is not expected_active:
            errors.append(
                f"relationship {relationship_id!r} active={record.get('active')!r}, "
                f"expected {expected_active!r} for focus {focus_id!r}"
            )
        opacity = record.get("pulseOpacity")
        pulse_should_show = bool(expected_active and plan.get("timeline") and not reduced_motion)
        if pulse_should_show:
            if not isinstance(opacity, (int, float)) or opacity < 0.99:
                errors.append(f"active relationship {relationship_id!r} pulse is not visible")
            distance = record.get("pulseDistance")
            if not isinstance(distance, (int, float)) or distance > 0.75:
                errors.append(
                    f"relationship {relationship_id!r} pulse is not on the master progress point"
                )
        elif isinstance(opacity, (int, float)) and opacity > 0.01:
            errors.append(f"inactive or reduced-motion relationship {relationship_id!r} pulse is visible")
    audit.metrics["relationshipStateCheckCount"] += 1
    audit.metrics["relationshipStateIssueCount"] += len(errors)
    audit.finish_check(
        check_id,
        errors,
        {
            "relationshipCount": len(records),
            "focusId": focus_id,
            "reducedMotion": reduced_motion,
            "activeRelationshipIds": sorted(
                item["id"] for item in records if isinstance(item, dict) and item.get("active")
            ),
        },
    )


def audit_accessibility_tree(page: Page, audit: Audit, check_id: str) -> None:
    expected = page.evaluate(
        r"""
        () => {
          const root = document.documentElement;
          const plan = window.svgSync.getPlan();
          const normalize = (value) => String(value || "").replace(/\s+/g, " ").trim();
          const referencedText = (element, attribute) => normalize(
            (element.getAttribute(attribute) || "")
              .split(/\s+/)
              .filter(Boolean)
              .map((id) => document.getElementById(id)?.textContent || "")
              .join(" ")
          );
          return {
            readingOrder: plan.layout.readingOrder,
            root: {
              id: root.id,
              role: root.getAttribute("role"),
              name: referencedText(root, "aria-labelledby"),
              description: referencedText(root, "aria-describedby")
            },
            modules: [...root.querySelectorAll(".sync-module[data-module-id]")].map((element) => ({
              id: element.getAttribute("data-module-id"),
              domId: element.id,
              role: element.getAttribute("role"),
              name: referencedText(element, "aria-labelledby"),
              description: referencedText(element, "aria-describedby"),
              bindingIds: [...element.querySelectorAll("[data-bind]")].map((binding) => binding.id)
            })),
            bindings: [...root.querySelectorAll("[data-bind]")].map((element) => ({
              id: element.id,
              moduleId: element.closest(".sync-module[data-module-id]")?.getAttribute("data-module-id") || "",
              dataRole: element.getAttribute("data-role"),
              valueId: element.getAttribute("data-bind"),
              role: element.getAttribute("role"),
              name: normalize(element.getAttribute("aria-label")),
              valueText: normalize(element.getAttribute("aria-valuetext")),
              valueNow: normalize(element.getAttribute("aria-valuenow")),
              valueMin: normalize(element.getAttribute("aria-valuemin")),
              valueMax: normalize(element.getAttribute("aria-valuemax")),
              accessibleLabel: normalize(element.getAttribute("data-accessible-label")),
              accessibleValue: normalize(element.getAttribute("data-accessible-value")),
              hasChildTitle: Boolean([...element.children].find((child) => child.localName === "title"))
            })),
            controls: [...root.querySelectorAll("[data-action], [data-module-focus-id]")].map((element) => ({
              id: element.id,
              action: element.getAttribute("data-action") || "module-focus",
              role: element.getAttribute("role"),
              name: normalize(element.getAttribute("aria-label")),
              pressed: normalize(element.getAttribute("aria-pressed")),
              tabIndex: element.tabIndex
            }))
          };
        }
        """
    )
    session = page.context.new_cdp_session(page)
    try:
        dom_response = session.send("DOM.getDocument", {"depth": -1, "pierce": True})
        response = session.send("Accessibility.getFullAXTree")
    finally:
        session.detach()

    nodes = response.get("nodes", []) if isinstance(response, dict) else []
    node_by_id = {
        str(node.get("nodeId")): node
        for node in nodes
        if isinstance(node, dict) and node.get("nodeId") is not None
    }
    ax_by_backend: dict[int, list[dict[str, Any]]] = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("backendDOMNodeId"), int):
            continue
        ax_by_backend.setdefault(int(node["backendDOMNodeId"]), []).append(node)

    dom_id_to_backend: dict[str, int] = {}

    def collect_dom_ids(node: Any) -> None:
        if not isinstance(node, dict):
            return
        raw_attributes = node.get("attributes", [])
        attributes = {
            str(raw_attributes[index]): str(raw_attributes[index + 1])
            for index in range(0, len(raw_attributes) - 1, 2)
        } if isinstance(raw_attributes, list) else {}
        dom_id = attributes.get("id")
        backend_id = node.get("backendNodeId")
        if dom_id and isinstance(backend_id, int):
            dom_id_to_backend[dom_id] = backend_id
        for key in ("children", "shadowRoots", "pseudoElements"):
            for child in node.get(key, []) if isinstance(node.get(key), list) else []:
                collect_dom_ids(child)
        collect_dom_ids(node.get("contentDocument"))

    collect_dom_ids(dom_response.get("root") if isinstance(dom_response, dict) else None)

    errors: list[str] = []

    def ax_role(dom_role: str) -> str:
        return {"img": "image"}.get(dom_role, dom_role)

    def field_value(node: dict[str, Any], field: str) -> Any:
        raw = node.get(field)
        if isinstance(raw, dict):
            return raw.get("value")
        for item in node.get("properties", []):
            if isinstance(item, dict) and item.get("name") == field:
                value = item.get("value")
                return value.get("value") if isinstance(value, dict) else value
        return None

    def node_ancestors(node: dict[str, Any]) -> set[str]:
        result: set[str] = set()
        parent_id = node.get("parentId")
        while parent_id is not None and str(parent_id) not in result:
            key = str(parent_id)
            result.add(key)
            parent = node_by_id.get(key)
            parent_id = parent.get("parentId") if isinstance(parent, dict) else None
        return result

    def normalized_ax_text(value: Any) -> str:
        """Match DOM and Chromium names across equivalent Unicode whitespace."""

        return " ".join(str(value or "").split())

    def correlated_node(dom_id: str, expected_role: str, expected_name: str, label: str) -> dict[str, Any] | None:
        backend_id = dom_id_to_backend.get(dom_id)
        if backend_id is None:
            errors.append(f"{label} has no CDP backend DOM node")
            return None
        candidates = [node for node in ax_by_backend.get(backend_id, []) if node.get("ignored") is not True]
        exact = [
            node for node in candidates
            if str(field_value(node, "role") or "") == expected_role
            and normalized_ax_text(field_value(node, "name")) == normalized_ax_text(expected_name)
        ]
        if len(exact) != 1:
            observed = [
                {
                    "role": str(field_value(node, "role") or ""),
                    "name": str(field_value(node, "name") or ""),
                    "ignored": bool(node.get("ignored")),
                }
                for node in ax_by_backend.get(backend_id, [])
            ]
            errors.append(
                f"{label} maps to {len(exact)} exact Chromium AX nodes; expected one "
                f"role={expected_role!r}, name={expected_name!r}, observed={observed!r}"
            )
            return None
        return exact[0]

    def descendants_in_order(start_node_id: str) -> list[str]:
        ordered: list[str] = []

        def visit(node_id: str) -> None:
            node = node_by_id.get(node_id)
            if not isinstance(node, dict):
                return
            for child_id in node.get("childIds", []) or []:
                key = str(child_id)
                ordered.append(key)
                visit(key)

        visit(start_node_id)
        return ordered

    root = expected.get("root", {}) if isinstance(expected, dict) else {}
    if root.get("role") != "group":
        errors.append("root SVG does not use role='group'")
    if not root.get("name") or not root.get("description"):
        errors.append("root SVG lacks distinct name and description sources")
    root_node = correlated_node(
        str(root.get("id", "")), "group", str(root.get("name", "")), "root SVG"
    )
    if root_node is not None and str(field_value(root_node, "description") or "") != root.get("description"):
        errors.append("root SVG AX description differs from aria-describedby")

    modules = expected.get("modules", []) if isinstance(expected, dict) else []
    if not modules:
        errors.append("no labeled SVG module groups were found")
    module_nodes: dict[str, dict[str, Any]] = {}
    for module in modules:
        if module.get("role") != "group":
            errors.append(f"module {module.get('id')!r} does not use role='group'")
        if not module.get("name") or not module.get("description"):
            errors.append(f"module {module.get('id')!r} lacks a distinct accessible name or description")
        module_node = correlated_node(
            str(module.get("domId", "")), "group", str(module.get("name", "")),
            f"module {module.get('id')!r}",
        )
        if module_node is None:
            continue
        module_nodes[str(module.get("id", ""))] = module_node
        if str(field_value(module_node, "description") or "") != module.get("description"):
            errors.append(f"module {module.get('id')!r} AX description differs from aria-describedby")
        if root_node is not None and str(root_node.get("nodeId")) not in node_ancestors(module_node):
            errors.append(f"module {module.get('id')!r} is not an AX descendant of the root SVG")

    reading_order = expected.get("readingOrder", []) if isinstance(expected, dict) else []
    dom_module_order = [str(module.get("id", "")) for module in modules]
    if dom_module_order != reading_order:
        errors.append(
            f"DOM module order {dom_module_order!r} differs from layout.readingOrder {reading_order!r}"
        )
    if root_node is not None and reading_order:
        root_subtree_order = descendants_in_order(str(root_node.get("nodeId")))
        root_positions = {node_id: index for index, node_id in enumerate(root_subtree_order)}
        ax_positions = [
            root_positions.get(str(module_nodes[module_id].get("nodeId")))
            for module_id in reading_order
            if module_id in module_nodes
        ]
        if len(ax_positions) != len(reading_order) or any(position is None for position in ax_positions):
            errors.append("not every planned module is exposed in the root Chromium AX reading order")
        elif ax_positions != sorted(ax_positions):
            errors.append("Chromium AX module traversal differs from layout.readingOrder")

    bindings = expected.get("bindings", []) if isinstance(expected, dict) else []
    bound_nodes: dict[str, dict[str, Any]] = {}
    for binding in bindings:
        value_id = binding.get("valueId")
        role = binding.get("role")
        name = binding.get("name")
        accessible_label = binding.get("accessibleLabel")
        accessible_value = binding.get("accessibleValue")
        if role not in {"img", "meter"}:
            errors.append(f"binding {value_id!r} has unsupported accessibility role {role!r}")
        if not name or not accessible_label or not accessible_value:
            errors.append(f"binding {value_id!r} lacks a complete human-readable accessible name")
        elif value_id and "-" in str(value_id) and str(value_id) in str(name):
            errors.append(f"binding {value_id!r} DOM name exposes its internal canonical ID")
        elif accessible_label not in name or accessible_value not in name:
            errors.append(f"binding {value_id!r} accessible name is inconsistent with its label/value")
        if binding.get("hasChildTitle"):
            errors.append(f"binding {value_id!r} has a redundant child title")
        if role == "img" and binding.get("valueText"):
            errors.append(f"binding {value_id!r} puts ignored aria-valuetext on role='img'")
        if role == "meter" and binding.get("valueText") != accessible_value:
            errors.append(f"binding {value_id!r} meter aria-valuetext is stale")
        bound_node = correlated_node(
            str(binding.get("id", "")), ax_role(str(role or "")), str(name or ""),
            f"binding ({binding.get('moduleId')!r}, {binding.get('dataRole')!r}, {value_id!r})",
        )
        if bound_node is None:
            continue
        bound_nodes[str(binding.get("id", ""))] = bound_node
        ax_name = str(field_value(bound_node, "name") or "")
        if value_id and "-" in str(value_id) and str(value_id) in ax_name:
            errors.append(f"binding {value_id!r} Chromium AX name exposes its internal canonical ID")
        if str(field_value(bound_node, "description") or ""):
            errors.append(f"binding {value_id!r} has a redundant Chromium AX description")
        module_node = module_nodes.get(str(binding.get("moduleId", "")))
        if module_node is not None and str(module_node.get("nodeId")) not in node_ancestors(bound_node):
            errors.append(
                f"binding ({binding.get('moduleId')!r}, {binding.get('dataRole')!r}) is outside its module AX subtree"
            )
        if role == "meter":
            try:
                expected_now = float(binding.get("valueNow"))
                actual_now = float(field_value(bound_node, "value"))
                expected_min = float(binding.get("valueMin"))
                actual_min = float(field_value(bound_node, "valuemin"))
                expected_max = float(binding.get("valueMax"))
                actual_max = float(field_value(bound_node, "valuemax"))
            except (TypeError, ValueError):
                errors.append(f"binding {value_id!r} meter lacks numeric DOM or Chromium AX range values")
            else:
                if not all(
                    close_number(actual, expected)
                    for actual, expected in (
                        (actual_now, expected_now), (actual_min, expected_min), (actual_max, expected_max)
                    )
                ):
                    errors.append(f"binding {value_id!r} meter Chromium AX range differs from the DOM")

    for module in modules:
        module_id = str(module.get("id", ""))
        module_node = module_nodes.get(module_id)
        if module_node is None:
            continue
        subtree_order = descendants_in_order(str(module_node.get("nodeId")))
        positions = {node_id: index for index, node_id in enumerate(subtree_order)}
        observed_positions = [
            positions.get(str(bound_nodes[binding_id].get("nodeId")))
            for binding_id in module.get("bindingIds", [])
            if binding_id in bound_nodes
        ]
        if any(position is None for position in observed_positions) or observed_positions != sorted(observed_positions):
            errors.append(f"module {module_id!r} bound nodes do not preserve DOM reading order in its AX subtree")

    controls = expected.get("controls", []) if isinstance(expected, dict) else []
    for control in controls:
        if control.get("role") != "button" or not control.get("name") or control.get("tabIndex") != 0:
            errors.append(f"control {control.get('action')!r} lacks a named button role")
        control_node = correlated_node(
            str(control.get("id", "")), "button", str(control.get("name", "")),
            f"control {control.get('id')!r}",
        )
        if control_node is None:
            continue
        if field_value(control_node, "focusable") is not True:
            errors.append(f"control {control.get('id')!r} is not focusable in Chromium AX")
        if root_node is not None and str(root_node.get("nodeId")) not in node_ancestors(control_node):
            errors.append(f"control {control.get('id')!r} is outside the root SVG AX subtree")
        if control.get("pressed"):
            actual_pressed = str(field_value(control_node, "pressed")).lower()
            if actual_pressed != str(control.get("pressed")).lower():
                errors.append(f"control {control.get('id')!r} Chromium AX pressed state is stale")

    exposed_binding_count = len(bound_nodes)
    audit.metrics["accessibilityTreeCheckCount"] += 1
    audit.metrics["accessibilityTreeIssueCount"] += len(errors)
    audit.metrics["accessibleBindingCount"] = max(
        audit.metrics["accessibleBindingCount"], exposed_binding_count
    )
    audit.finish_check(
        check_id,
        errors,
        {
            "rootRole": root.get("role"),
            "rootName": root.get("name"),
            "moduleCount": len(modules),
            "expectedBindingCount": len(bindings),
            "exposedBindingCount": exposed_binding_count,
            "controlCount": len(controls),
            "correlatedModuleCount": len(module_nodes),
            "correlatedDomIdCount": len(dom_id_to_backend),
            "exposedNodeCount": sum(1 for node in nodes if isinstance(node, dict) and node.get("ignored") is not True),
        },
    )


def open_svg(page: Page, svg_path: Path, timeout_ms: int) -> None:
    page.goto(svg_path.as_uri(), wait_until="load", timeout=timeout_ms)
    page.wait_for_function(
        "() => window.svgSync && window.svgSync.ready && typeof window.svgSync.ready.then === 'function'",
        timeout=timeout_ms,
    )
    page.evaluate("async () => { await window.svgSync.ready; }")
    page.evaluate(INSTALL_EVENT_PROBE_JS)


def check_api(page: Page, audit: Audit) -> dict[str, Any]:
    details = page.evaluate(
        """
        () => ({
          version: window.svgSync.version,
          frozen: Object.isFrozen(window.svgSync),
          methods: Object.fromEntries(
            Object.keys(window.svgSync).map((key) => [key, typeof window.svgSync[key]])
          ),
          plan: window.svgSync.getPlan()
        })
        """
    )
    errors: list[str] = []
    if details.get("version") != "1.0":
        errors.append("window.svgSync.version must equal '1.0'")
    if not details.get("frozen"):
        errors.append("window.svgSync must be frozen")
    missing = sorted(method for method in REQUIRED_METHODS if details.get("methods", {}).get(method) != "function")
    if missing:
        errors.append(f"window.svgSync is missing methods: {missing}")
    plan = details.get("plan")
    try:
        validate_plan(plan)
    except (TypeError, ValueError) as exc:
        errors.append(f"runtime plan is invalid: {exc}")
    audit.finish_check(
        "runtime-api",
        errors,
        {"version": details.get("version"), "methodCount": len(details.get("methods", {}))},
    )
    if errors or not isinstance(plan, dict):
        raise RuntimeError("runtime API or embedded plan is invalid")
    return plan


def audit_scenarios(page: Page, audit: Audit, plan: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    for scenario in plan["scenarios"]:
        scenario_id = scenario["id"]
        expected_source, expected_derived = scenario_state(plan, scenario_id)
        before = current
        outcome = invoke(page, "applyScenario", scenario_id)
        audit.finish_check(f"scenario-{scenario_id}-transaction", invocation_errors(outcome))
        after = capture(page)
        validate_capture(
            audit,
            f"scenario-{scenario_id}-state",
            after,
            plan,
            expected_source,
            expected_derived,
            scenario_id,
            before["snapshot"]["focusId"],
            before["snapshot"]["timeMs"],
            before["snapshot"]["phaseId"],
            float(before["snapshot"].get("phaseProgress", 0)),
            "full",
        )
        compare_transition(audit, f"scenario-{scenario_id}-propagation", before, after)
        repeated = invoke(page, "applyScenario", scenario_id)
        audit.finish_check(f"scenario-{scenario_id}-repeat-transaction", invocation_errors(repeated))
        repeated_capture = capture(page)
        audit.finish_check(
            f"scenario-{scenario_id}-idempotence",
            idempotence_errors(after, repeated_capture),
        )
        audit_visual_geometry(page, audit, f"scenario-{scenario_id}-visual-geometry")
        audit_quantitative_semantics(page, audit, f"scenario-{scenario_id}-quantitative-semantics")
        audit_accessibility_tree(page, audit, f"scenario-{scenario_id}-accessibility-tree")
        audit.snapshots["scenarios"][scenario_id] = repeated_capture["snapshot"]
        current = repeated_capture
    audit.metrics["scenarioCount"] = len(plan["scenarios"])
    return current


def audit_source_perturbations(page: Page, audit: Audit, plan: dict[str, Any]) -> None:
    baseline_source, baseline_derived = scenario_state(plan, plan["initialScenario"])
    for definition in plan["concepts"]:
        reset_outcome = invoke(page, "reset")
        audit.finish_check(f"source-{definition['id']}-reset", invocation_errors(reset_outcome))
        baseline = capture(page)
        validate_capture(
            audit,
            f"source-{definition['id']}-baseline",
            baseline,
            plan,
            baseline_source,
            baseline_derived,
            plan["initialScenario"],
            None,
            0,
            None,
            0,
            "full",
        )
        try:
            candidate, expected_source, expected_derived = choose_perturbation(
                plan, definition, baseline_source, baseline_derived
            )
        except ValueError as exc:
            audit.fail(f"source-{definition['id']}-candidate", str(exc))
            continue
        outcome = invoke(page, "setState", {definition["id"]: candidate})
        audit.finish_check(f"source-{definition['id']}-transaction", invocation_errors(outcome))
        changed = capture(page)
        validate_capture(
            audit,
            f"source-{definition['id']}-state",
            changed,
            plan,
            expected_source,
            expected_derived,
            None,
            None,
            0,
            None,
            0,
            "full",
        )
        compare_transition(
            audit,
            f"source-{definition['id']}-propagation",
            baseline,
            changed,
            require_changed_binding=True,
        )
        repeated = invoke(page, "setState", {definition["id"]: candidate})
        audit.finish_check(f"source-{definition['id']}-repeat-transaction", invocation_errors(repeated))
        repeated_capture = capture(page)
        audit.finish_check(
            f"source-{definition['id']}-idempotence",
            idempotence_errors(changed, repeated_capture),
        )
        audit_visual_geometry(
            page,
            audit,
            f"source-{definition['id']}-visual-geometry",
        )
        audit_quantitative_semantics(
            page,
            audit,
            f"source-{definition['id']}-quantitative-semantics",
        )
        audit_accessibility_tree(
            page,
            audit,
            f"source-{definition['id']}-accessibility-tree",
        )
        audit.snapshots["sources"][definition["id"]] = {
            "input": candidate,
            "snapshot": repeated_capture["snapshot"],
        }
    audit.metrics["sourcePerturbationCount"] = len(plan["concepts"])


def zero_flow_candidate(
    plan: dict[str, Any],
    value_id: str,
    baseline_source: dict[str, float],
    diagnostics: dict[str, Any] | None = None,
) -> tuple[str, float, dict[str, float], dict[str, float]] | None:
    """Find a legal one-source state that places a bound flow exactly at zero."""

    source_ids = {str(item["id"]) for item in plan["concepts"]}
    derived_by_id = {str(item["id"]): item for item in plan.get("derived", [])}

    def source_dependencies(target_id: str, seen: set[str] | None = None) -> set[str]:
        if target_id in source_ids:
            return {target_id}
        if target_id not in derived_by_id:
            return set()
        visited = set() if seen is None else set(seen)
        if target_id in visited:
            return set()
        visited.add(target_id)
        result: set[str] = set()
        for dependency in derived_by_id[target_id].get("dependsOn", []):
            result.update(source_dependencies(str(dependency), visited))
        return result

    relevant_sources = source_dependencies(value_id)

    def expression_seed_values(target_id: str, varied_source: str) -> set[float]:
        seeds: set[float] = set()
        visited: set[str] = set()

        def walk_node(node: Any) -> None:
            if isinstance(node, (int, float)) and not isinstance(node, bool):
                value = float(node)
                if math.isfinite(value):
                    seeds.add(value)
                return
            if not isinstance(node, dict):
                return
            if set(node) == {"ref"}:
                ref = str(node["ref"])
                if ref in derived_by_id and ref not in visited:
                    visited.add(ref)
                    walk_node(derived_by_id[ref].get("compute"))
                elif ref != varied_source and ref in baseline_source:
                    value = float(baseline_source[ref])
                    if math.isfinite(value):
                        seeds.add(value)
                return
            for argument in node.get("args", []):
                walk_node(argument)

        if target_id in derived_by_id:
            visited.add(target_id)
            walk_node(derived_by_id[target_id].get("compute"))
        return seeds

    best: tuple[float, str, float, dict[str, float], dict[str, float]] | None = None
    saw_sign_crossing = False
    saw_near_root = False
    for definition in plan["concepts"]:
        if str(definition["id"]) not in relevant_sources:
            continue
        domain = definition.get("domain")
        if not isinstance(domain, list) or len(domain) != 2:
            continue
        low, high = sorted((float(domain[0]), float(domain[1])))
        if low == high:
            continue

        def evaluate(candidate: float) -> tuple[float, dict[str, float], dict[str, float]] | None:
            source = dict(baseline_source)
            source[definition["id"]] = candidate
            try:
                next_source, next_derived = compute_state(plan, source)
            except ValueError:
                return None
            values = {**next_source, **next_derived}
            target = values.get(value_id)
            if target is None or not math.isfinite(float(target)):
                return None
            return float(target), next_source, next_derived

        candidates: list[tuple[float, dict[str, float], dict[str, float]]] = []
        evaluated_cache: dict[float, tuple[float, dict[str, float], dict[str, float]] | None] = {}

        def cached_evaluate(candidate: float) -> tuple[float, dict[str, float], dict[str, float]] | None:
            if candidate not in evaluated_cache:
                evaluated_cache[candidate] = evaluate(candidate)
            return evaluated_cache[candidate]

        def scan_states(
            states: list[tuple[float, float, dict[str, float], dict[str, float]]],
        ) -> None:
            nonlocal saw_sign_crossing
            for sample, value, source_state, derived_state in states:
                if value == 0.0:
                    candidates.append((sample, source_state, derived_state))
            for left_state, right_state in zip(states, states[1:]):
                left, left_value = left_state[0], left_state[1]
                right, right_value = right_state[0], right_state[1]
                opposite_signs = (left_value < 0 < right_value) or (right_value < 0 < left_value)
                if not opposite_signs:
                    continue
                saw_sign_crossing = True
                exact_candidate = None
                for _ in range(256):
                    middle = (left + right) / 2
                    if middle == left or middle == right:
                        break
                    middle_state = cached_evaluate(middle)
                    if middle_state is None:
                        break
                    middle_value, middle_source, middle_derived = middle_state
                    if middle_value == 0.0:
                        exact_candidate = (middle, middle_source, middle_derived)
                        break
                    if (left_value < 0 < middle_value) or (middle_value < 0 < left_value):
                        right = middle
                        right_value = middle_value
                    else:
                        left = middle
                        left_value = middle_value
                if exact_candidate is not None:
                    candidates.append(exact_candidate)
                    continue
                for probe in {
                    left,
                    right,
                    math.nextafter(left, right),
                    math.nextafter(right, left),
                }:
                    probe_state = cached_evaluate(probe)
                    if probe_state is not None and probe_state[0] == 0.0:
                        candidates.append((probe, probe_state[1], probe_state[2]))

        seed_values = expression_seed_values(value_id, str(definition["id"]))
        seed_atoms = sorted(seed_values, key=lambda value: (abs(value), value))[:16]
        expanded_seeds = set(seed_atoms)
        for first in seed_atoms:
            expanded_seeds.add(-first)
            if first != 0.0:
                reciprocal = 1.0 / first
                if math.isfinite(reciprocal):
                    expanded_seeds.add(reciprocal)
        for first in seed_atoms:
            for second in seed_atoms:
                for value in (first + second, first - second, first * second):
                    if math.isfinite(value):
                        expanded_seeds.add(value)
                if second != 0.0:
                    value = first / second
                    if math.isfinite(value):
                        expanded_seeds.add(value)
        for seed in sorted(expanded_seeds):
            if not low <= seed <= high:
                continue
            seed_state = cached_evaluate(seed)
            if seed_state is not None and seed_state[0] == 0.0:
                candidates.append((seed, seed_state[1], seed_state[2]))

        samples: list[tuple[float, float, dict[str, float], dict[str, float]]] = []
        for sample_index in range(65):
            sample = low + (high - low) * sample_index / 64
            state = cached_evaluate(sample)
            if state is not None:
                samples.append((sample, state[0], state[1], state[2]))
        scan_states(samples)

        local_minima = [
            index
            for index in range(1, len(samples) - 1)
            if abs(samples[index][1]) <= abs(samples[index - 1][1])
            and abs(samples[index][1]) <= abs(samples[index + 1][1])
        ]
        local_minima.sort(key=lambda index: (abs(samples[index][1]), samples[index][0]))
        for index in local_minima[:4]:
            window_low = samples[index - 1][0]
            window_high = samples[index + 1][0]
            dense_states: list[tuple[float, float, dict[str, float], dict[str, float]]] = []
            for dense_index in range(513):
                sample = window_low + (window_high - window_low) * dense_index / 512
                state = cached_evaluate(sample)
                if state is not None:
                    dense_states.append((sample, state[0], state[1], state[2]))
            scan_states(dense_states)
            smallest_dense = min((abs(state[1]) for state in dense_states), default=math.inf)
            surrounding = max(abs(samples[index - 1][1]), abs(samples[index + 1][1]))
            if math.isfinite(smallest_dense) and smallest_dense < surrounding:
                saw_near_root = True

            left = window_low
            right = window_high
            for _ in range(192):
                if math.nextafter(left, right) >= right:
                    break
                third = (right - left) / 3
                first_probe = left + third
                second_probe = right - third
                first_state = cached_evaluate(first_probe)
                second_state = cached_evaluate(second_probe)
                if first_state is None or second_state is None:
                    break
                if first_state[0] == 0.0:
                    candidates.append((first_probe, first_state[1], first_state[2]))
                    break
                if second_state[0] == 0.0:
                    candidates.append((second_probe, second_state[1], second_state[2]))
                    break
                if abs(first_state[0]) <= abs(second_state[0]):
                    right = second_probe
                else:
                    left = first_probe
            for probe in {
                left,
                right,
                (left + right) / 2,
                math.nextafter(left, right),
                math.nextafter(right, left),
            }:
                probe_state = cached_evaluate(probe)
                if probe_state is not None and probe_state[0] == 0.0:
                    candidates.append((probe, probe_state[1], probe_state[2]))

        for candidate in candidates:
            if candidate[0] == baseline_source[definition["id"]]:
                continue
            distance = abs(candidate[0] - baseline_source[definition["id"]]) / (high - low)
            record = (distance, definition["id"], candidate[0], candidate[1], candidate[2])
            if best is None or record[:3] < best[:3]:
                best = record
    if best is None:
        if diagnostics is not None:
            diagnostics["reason"] = (
                "noExactRepresentableRoot"
                if saw_sign_crossing or saw_near_root
                else "noLegalZeroCrossing"
            )
        return None
    return best[1], best[2], best[3], best[4]


def audit_zero_flow_boundaries(page: Page, audit: Audit, plan: dict[str, Any]) -> None:
    flow_value_ids = page.evaluate(
        r"""
        () => [...new Set([...document.querySelectorAll('[data-sync-layout-item="flow"]')]
          .map((item) => {
            const role = item.getAttribute("data-layout-bound-role") || "";
            const module = item.closest(".sync-module[data-module-id]");
            return module?.querySelector(`[data-role="${CSS.escape(role)}"]`)?.getAttribute("data-bind") || "";
          })
          .filter(Boolean))].sort()
        """
    )
    if not isinstance(flow_value_ids, list):
        audit.fail("zero-flow-discovery", "flow binding discovery returned an invalid result")
        return
    scenario_sources = [
        (scenario["id"], scenario_state(plan, scenario["id"])[0])
        for scenario in plan["scenarios"]
    ]
    tested = 0
    for value_id in flow_value_ids:
        selected = None
        search_details = []
        for scenario_id, source in scenario_sources:
            diagnostics: dict[str, Any] = {}
            candidate = zero_flow_candidate(plan, str(value_id), source, diagnostics)
            search_details.append({"scenarioId": scenario_id, **diagnostics})
            if candidate is not None:
                selected = (scenario_id, candidate)
                break
        if selected is None:
            reasons = {item.get("reason") for item in search_details}
            reason = (
                "noExactRepresentableRoot"
                if "noExactRepresentableRoot" in reasons
                else "noLegalZeroCrossing"
            )
            audit.snapshots["zeroFlowDiagnostics"][str(value_id)] = {
                "reason": reason,
                "searches": search_details,
            }
            continue
        scenario_id, candidate = selected
        source_id, source_value, expected_source, expected_derived = candidate
        reset_outcome = invoke(page, "reset")
        audit.finish_check(f"zero-flow-{value_id}-reset", invocation_errors(reset_outcome))
        if scenario_id != plan["initialScenario"]:
            scenario_outcome = invoke(page, "applyScenario", scenario_id)
            audit.finish_check(
                f"zero-flow-{value_id}-scenario",
                invocation_errors(scenario_outcome),
                {"scenarioId": scenario_id},
            )
        outcome = invoke(page, "setState", {source_id: source_value})
        audit.finish_check(f"zero-flow-{value_id}-transaction", invocation_errors(outcome))
        changed = capture(page)
        validate_capture(
            audit,
            f"zero-flow-{value_id}-state",
            changed,
            plan,
            expected_source,
            expected_derived,
            None,
            None,
            0,
            None,
            0,
            "full",
        )
        actual_value = all_values(changed).get(str(value_id))
        boundary_errors = []
        if actual_value is None or float(actual_value) != 0.0:
            boundary_errors.append(
                f"computed boundary leaves {value_id!r} at {actual_value!r} instead of zero"
            )
        audit.finish_check(
            f"zero-flow-{value_id}-boundary",
            boundary_errors,
            {"sourceId": source_id, "sourceValue": source_value, "flowValue": actual_value},
        )
        audit_visual_geometry(page, audit, f"zero-flow-{value_id}-visual-geometry")
        audit_quantitative_semantics(page, audit, f"zero-flow-{value_id}-quantitative-semantics")
        audit_accessibility_tree(page, audit, f"zero-flow-{value_id}-accessibility-tree")
        audit.snapshots["zeroFlows"][str(value_id)] = {
            "scenarioId": scenario_id,
            "sourceId": source_id,
            "sourceValue": source_value,
            "snapshot": changed["snapshot"],
        }
        tested += 1
    audit.metrics["zeroFlowBoundaryCount"] = tested
    audit.finish_check(
        "zero-flow-coverage",
        [],
        {
            "flowValueCount": len(flow_value_ids),
            "testedBoundaryCount": tested,
            "untestedValueIds": sorted(set(map(str, flow_value_ids)) - set(audit.snapshots["zeroFlows"])),
            "untestedReasons": audit.snapshots["zeroFlowDiagnostics"],
        },
    )
    invoke(page, "reset")


def audit_focus_readability(page: Page, audit: Audit, check_id: str) -> None:
    details = page.evaluate(
        r"""
        () => {
          const parseColor = (value) => {
            const match = String(value).match(/rgba?\((\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)/);
            return match ? match.slice(1, 4).map(Number) : null;
          };
          const linear = (channel) => {
            const value = channel / 255;
            return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
          };
          const luminance = (rgb) => 0.2126 * linear(rgb[0]) + 0.7152 * linear(rgb[1]) + 0.0722 * linear(rgb[2]);
          const contrast = (first, second) => {
            const light = Math.max(luminance(first), luminance(second));
            const dark = Math.min(luminance(first), luminance(second));
            return (light + 0.05) / (dark + 0.05);
          };
          const modules = [];
          const issues = [];
          for (const group of document.querySelectorAll('.sync-module[data-focused="false"]')) {
            const moduleId = group.getAttribute("data-module-id") || "unknown";
            const groupStyle = getComputedStyle(group);
            const frame = group.querySelector(":scope > .module-frame");
            const background = parseColor(frame ? getComputedStyle(frame).fill : "rgb(255,255,255)") || [255,255,255];
            const textRecords = [];
            if (Number(groupStyle.opacity) < 0.999 || groupStyle.filter !== "none") {
              issues.push({moduleId, reason: "focus treatment dims or filters the whole module container"});
            }
            for (const text of group.querySelectorAll("text")) {
              let opacity = 1;
              let current = text;
              while (current) {
                opacity *= Number.parseFloat(getComputedStyle(current).opacity || "1");
                if (current === group) break;
                current = current.parentElement;
              }
              const foreground = parseColor(getComputedStyle(text).fill);
              const ratio = foreground ? contrast(foreground, background) : 0;
              const record = {
                text: (text.textContent || "").replace(/\s+/g, " ").trim(),
                opacity: Number(opacity.toFixed(3)),
                contrast: Number(ratio.toFixed(2))
              };
              textRecords.push(record);
              if (opacity < 0.999) issues.push({...record, moduleId, reason: "non-focused text is opacity-dimmed"});
              if (ratio < 4.5) issues.push({...record, moduleId, reason: "non-focused text contrast is below 4.5:1"});
            }
            modules.push({moduleId, groupOpacity: groupStyle.opacity, groupFilter: groupStyle.filter, textRecords});
          }
          return {modules, issues};
        }
        """
    )
    issues = details.get("issues", []) if isinstance(details, dict) else []
    errors = [
        f"module {issue.get('moduleId')!r}: {issue.get('reason')} "
        f"(text={issue.get('text')!r}, opacity={issue.get('opacity')}, contrast={issue.get('contrast')})"
        for issue in issues
        if isinstance(issue, dict)
    ]
    audit.metrics["focusReadabilityCheckCount"] += 1
    audit.metrics["focusReadabilityIssueCount"] += len(errors)
    audit.finish_check(
        check_id,
        errors,
        {
            "moduleCount": len(details.get("modules", [])) if isinstance(details, dict) else 0,
            "modules": details.get("modules", []) if isinstance(details, dict) else [],
            "issues": issues,
        },
    )


def audit_focus(page: Page, audit: Audit, plan: dict[str, Any]) -> None:
    focus_groups = plan.get("focusGroups", [])
    if not focus_groups:
        audit.fail("focus-groups", "the plan declares no focus groups to audit")
        return
    baseline_source, baseline_derived = scenario_state(plan, plan["initialScenario"])
    for focus in focus_groups:
        reset = invoke(page, "reset")
        audit.finish_check(f"focus-{focus['id']}-prepare", invocation_errors(reset))
        before = capture(page)
        outcome = invoke(page, "setFocus", focus["id"])
        audit.finish_check(f"focus-{focus['id']}-transaction", invocation_errors(outcome))
        focused = capture(page)
        validate_capture(
            audit,
            f"focus-{focus['id']}-state",
            focused,
            plan,
            baseline_source,
            baseline_derived,
            plan["initialScenario"],
            focus["id"],
            0,
            None,
            0,
            "full",
        )
        compare_transition(audit, f"focus-{focus['id']}-semantic-isolation", before, focused)
        audit_relationship_state(
            page,
            audit,
            plan,
            focus["id"],
            f"focus-{focus['id']}-relationships",
        )
        audit_accessibility_tree(page, audit, f"focus-{focus['id']}-accessibility-tree")
        repeated = invoke(page, "setFocus", focus["id"])
        audit.finish_check(f"focus-{focus['id']}-repeat-transaction", invocation_errors(repeated))
        repeated_capture = capture(page)
        audit.finish_check(
            f"focus-{focus['id']}-idempotence",
            idempotence_errors(focused, repeated_capture),
        )
        audit_focus_readability(page, audit, f"focus-{focus['id']}-readability")
        audit.snapshots["focus"][focus["id"]] = repeated_capture["snapshot"]

        reset_after_focus = invoke(page, "reset")
        audit.finish_check(f"focus-{focus['id']}-reset-transaction", invocation_errors(reset_after_focus))
        reset_capture = capture(page)
        validate_capture(
            audit,
            f"focus-{focus['id']}-reset-state",
            reset_capture,
            plan,
            baseline_source,
            baseline_derived,
            plan["initialScenario"],
            None,
            0,
            None,
            0,
            "full",
        )
    audit.metrics["focusGroupCount"] = len(focus_groups)


def audit_real_input_controls(page: Page, audit: Audit, plan: dict[str, Any]) -> None:
    errors: list[str] = []
    details: dict[str, Any] = {}
    invoke(page, "pause")
    invoke(page, "reset")

    focus_controls = page.locator("[data-module-focus-id]")
    focus_control_count = focus_controls.count()
    if focus_control_count < 1:
        errors.append("no module focus control is available for pointer and keyboard testing")
    else:
        focus_records: list[dict[str, Any]] = []
        for control_index in range(focus_control_count):
            invoke(page, "reset")
            control = focus_controls.nth(control_index)
            focus_id = control.get_attribute("data-module-focus-id")
            module_id = control.evaluate(
                "element => element.closest('[data-module-id]')?.getAttribute('data-module-id') || 'unknown'"
            )
            control.click()
            pointer_focus = page.evaluate("() => window.svgSync.snapshot().focusId")
            pointer_pressed = page.evaluate(
                """
                (activeId) => [...document.querySelectorAll('[data-module-focus-id]')].map((element) => ({
                  target: element.getAttribute('data-module-focus-id'),
                  pressed: element.getAttribute('aria-pressed'),
                  expected: element.getAttribute('data-module-focus-id') === activeId ? 'true' : 'false'
                }))
                """,
                focus_id,
            )
            if pointer_focus != focus_id or any(
                item.get("pressed") != item.get("expected") for item in pointer_pressed
            ):
                errors.append(
                    f"pointer focus control {module_id!r}/{focus_id!r} did not synchronize focus and aria-pressed"
                )
            control.click()
            if page.evaluate("() => window.svgSync.snapshot().focusId") is not None:
                errors.append(
                    f"second pointer activation did not toggle focus off for {module_id!r}/{focus_id!r}"
                )
            control.focus()
            activation_key = "Space" if control_index % 2 == 0 else "Enter"
            page.keyboard.press(activation_key)
            keyboard_focus = page.evaluate("() => window.svgSync.snapshot().focusId")
            keyboard_pressed = page.evaluate(
                """
                (activeId) => [...document.querySelectorAll('[data-module-focus-id]')].map((element) => ({
                  target: element.getAttribute('data-module-focus-id'),
                  pressed: element.getAttribute('aria-pressed'),
                  expected: element.getAttribute('data-module-focus-id') === activeId ? 'true' : 'false'
                }))
                """,
                focus_id,
            )
            if keyboard_focus != focus_id or any(
                item.get("pressed") != item.get("expected") for item in keyboard_pressed
            ):
                errors.append(
                    f"{activation_key} focus control {module_id!r}/{focus_id!r} did not synchronize focus and aria-pressed"
                )
            page.keyboard.press("Escape")
            escape_snapshot = page.evaluate("() => window.svgSync.snapshot()")
            if escape_snapshot.get("focusId") is not None:
                errors.append(
                    f"Escape did not clear module focus after {module_id!r}/{focus_id!r}"
                )
            play_control = page.locator("#control-play")
            if play_control.count() and play_control.get_attribute("aria-pressed") != "false":
                errors.append("Escape did not leave timeline playback paused")
            focus_records.append(
                {
                    "moduleId": module_id,
                    "focusId": focus_id,
                    "activationKey": activation_key,
                    "pointerFocus": pointer_focus,
                    "keyboardFocus": keyboard_focus,
                    "escapeFocus": escape_snapshot.get("focusId"),
                }
            )
        details["focusControls"] = focus_records

    scenarios = plan.get("scenarios", [])
    if scenarios:
        scenario = scenarios[-1]
        scenario_control = page.locator(
            f'[data-action="scenario"][data-scenario-id="{scenario["id"]}"]'
        )
        if scenario_control.count() != 1:
            errors.append(f"scenario control for {scenario['id']!r} is missing or duplicated")
        else:
            scenario_control.click()
            actual_scenario = page.evaluate("() => window.svgSync.snapshot().scenarioId")
            if actual_scenario != scenario["id"]:
                errors.append(
                    f"scenario pointer control produced {actual_scenario!r}, expected {scenario['id']!r}"
                )
            details["scenarioId"] = actual_scenario

    timeline = plan.get("timeline")
    if timeline is not None:
        invoke(page, "pause")
        invoke(page, "reset")
        rail = page.locator("[data-timeline-rail]")
        if rail.count() != 1:
            errors.append("timeline slider is missing or duplicated")
        else:
            duration = float(timeline["durationMs"])
            rail.focus()
            page.keyboard.press("End")
            end_time = float(page.evaluate("() => window.svgSync.snapshot().timeMs"))
            page.keyboard.press("Home")
            home_time = float(page.evaluate("() => window.svgSync.snapshot().timeMs"))
            page.keyboard.press("ArrowRight")
            arrow_time = float(page.evaluate("() => window.svgSync.snapshot().timeMs"))
            expected_end = 0.0 if timeline.get("loop") else duration
            if not close_number(end_time, expected_end) or not close_number(home_time, 0):
                errors.append(
                    f"timeline Home/End produced home={home_time}, end={end_time}, "
                    f"expectedEnd={expected_end}, duration={duration}"
                )
            if arrow_time <= home_time:
                errors.append("timeline ArrowRight did not advance time")
            track_box = page.locator(".timeline-track").bounding_box()
            pointer_time = None
            if track_box is None:
                errors.append("timeline track has no pointer geometry")
            else:
                page.mouse.click(
                    track_box["x"] + track_box["width"] * 0.75,
                    track_box["y"] + track_box["height"] / 2,
                )
                pointer_time = float(page.evaluate("() => window.svgSync.snapshot().timeMs"))
                if abs(pointer_time - duration * 0.75) > duration * 0.03:
                    errors.append(
                        f"timeline pointer seek produced {pointer_time}, expected approximately {duration * 0.75}"
                    )
            play = page.locator("#control-play")
            if play.count() != 1:
                errors.append("Play/Pause control is missing or duplicated")
            else:
                play.click()
                play_before = float(page.evaluate("() => window.svgSync.snapshot().timeMs"))
                page.wait_for_timeout(150)
                play_after = float(page.evaluate("() => window.svgSync.snapshot().timeMs"))
                play.click()
                pause_before = float(page.evaluate("() => window.svgSync.snapshot().timeMs"))
                page.wait_for_timeout(80)
                pause_after = float(page.evaluate("() => window.svgSync.snapshot().timeMs"))
                if play_after <= play_before:
                    errors.append("Play pointer activation did not advance the master time")
                if not close_number(pause_after, pause_before, tolerance=1e-6):
                    errors.append("Pause pointer activation did not stabilize the master time")
                details["playback"] = {
                    "before": play_before,
                    "after": play_after,
                    "pausedAt": pause_after,
                }
            details["timeline"] = {
                "homeTimeMs": home_time,
                "endTimeMs": end_time,
                "arrowTimeMs": arrow_time,
                "pointerTimeMs": pointer_time,
            }

    invoke(page, "pause")
    invoke(page, "reset")
    audit.metrics["realInputCheckCount"] += 1
    audit.finish_check("real-input-controls", errors, details)


def normalize_time(timeline: dict[str, Any], raw_time: float) -> float:
    duration = float(timeline["durationMs"])
    value = raw_time
    if timeline.get("loop") and value > 0 and value >= duration:
        value %= duration
    return min(max(value, 0.0), duration)


def phase_at(timeline: dict[str, Any], time_ms: float) -> dict[str, Any]:
    duration = float(timeline["durationMs"])
    if timeline.get("loop") and time_ms == duration:
        time_ms = 0.0
    if time_ms == duration:
        return timeline["phases"][-1]
    for phase in timeline["phases"]:
        if time_ms >= float(phase["startMs"]) and time_ms < float(phase["endMs"]):
            return phase
    return timeline["phases"][-1]


def audit_timeline(page: Page, audit: Audit, plan: dict[str, Any]) -> None:
    timeline = plan.get("timeline")
    baseline_source, baseline_derived = scenario_state(plan, plan["initialScenario"])
    if timeline is None:
        invoke(page, "reset")
        before = capture(page)
        errors: list[str] = []
        for method, args in (("seek", [1234]), ("play", []), ("pause", [])):
            outcome = invoke(page, method, *args)
            errors.extend(f"{method}: {item}" for item in invocation_errors(outcome))
            after = capture(page)
            errors.extend(f"{method}: {item}" for item in idempotence_errors(before, after))
        audit.finish_check("timeline-absent-noops", errors)
        return

    timeline_base_id = str(timeline.get("baseScenario", plan["initialScenario"]))
    timeline_base_source, _ = scenario_state(plan, timeline_base_id)

    invoke(page, "reset")
    initial_control = page.evaluate(
        """
        () => {
          const control = document.getElementById("control-play");
          return control ? {
            text: (control.querySelector("text")?.textContent || "").trim(),
            label: control.getAttribute("aria-label"),
            pressed: control.getAttribute("aria-pressed"),
            disabled: control.getAttribute("aria-disabled"),
            tabIndex: control.tabIndex
          } : null;
        }
        """
    )
    play_outcome = invoke(page, "play")
    play_errors = invocation_errors(play_outcome)
    playing_control = page.evaluate(
        """
        () => {
          const control = document.getElementById("control-play");
          return control ? {
            text: (control.querySelector("text")?.textContent || "").trim(),
            label: control.getAttribute("aria-label"),
            pressed: control.getAttribute("aria-pressed"),
            disabled: control.getAttribute("aria-disabled"),
            tabIndex: control.tabIndex
          } : null;
        }
        """
    )
    pause_outcome = invoke(page, "pause")
    play_errors.extend(invocation_errors(pause_outcome))
    paused_control = page.evaluate(
        """
        () => {
          const control = document.getElementById("control-play");
          return control ? {
            text: (control.querySelector("text")?.textContent || "").trim(),
            label: control.getAttribute("aria-label"),
            pressed: control.getAttribute("aria-pressed"),
            disabled: control.getAttribute("aria-disabled"),
            tabIndex: control.tabIndex
          } : null;
        }
        """
    )
    expected_initial = {
        "text": "Play",
        "label": "Play the master timeline",
        "pressed": "false",
        "disabled": "false",
        "tabIndex": 0,
    }
    expected_playing = {
        "text": "Pause",
        "label": "Pause the master timeline",
        "pressed": "true",
        "disabled": "false",
        "tabIndex": 0,
    }
    if initial_control != expected_initial:
        play_errors.append(f"initial playback control is {initial_control!r}, expected {expected_initial!r}")
    if playing_control != expected_playing:
        play_errors.append(f"playing control is {playing_control!r}, expected {expected_playing!r}")
    if paused_control != expected_initial:
        play_errors.append(f"paused control is {paused_control!r}, expected {expected_initial!r}")
    audit.finish_check(
        "timeline-playback-control",
        play_errors,
        {"initial": initial_control, "playing": playing_control, "paused": paused_control},
    )

    samples: list[tuple[str, float]] = []
    for phase in timeline["phases"]:
        start = float(phase["startMs"])
        end = float(phase["endMs"])
        samples.extend(
            [
                (f"{phase['id']}-start", start),
                (f"{phase['id']}-midpoint", (start + end) / 2),
                (f"{phase['id']}-end", end),
            ]
        )
    duration = float(timeline["durationMs"])
    samples.extend(
        [
            ("negative-clamp", -100.0),
            ("duration-boundary", duration),
            ("after-duration", duration + duration / 2),
        ]
    )

    for label, raw_time in samples:
        reset = invoke(page, "reset")
        audit.finish_check(f"timeline-{label}-reset", invocation_errors(reset))
        invoke(page, "pause")
        before = capture(page)
        outcome = invoke(page, "seek", raw_time)
        audit.finish_check(f"timeline-{label}-transaction", invocation_errors(outcome))
        sought = capture(page)
        expected_time = normalize_time(timeline, raw_time)
        phase = phase_at(timeline, expected_time)
        phase_index = timeline["phases"].index(phase)
        start_source = dict(timeline_base_source)
        if phase_index > 0:
            start_source.update(
                {
                    key: float(value)
                    for key, value in timeline["phases"][phase_index - 1].get("values", {}).items()
                }
            )
        target_source = dict(timeline_base_source)
        target_source.update({key: float(value) for key, value in phase.get("values", {}).items()})
        span = max(1.0, float(phase["endMs"]) - float(phase["startMs"]))
        raw_progress = 1.0 if expected_time == duration else (
            expected_time - float(phase["startMs"])
        ) / span
        raw_progress = min(max(raw_progress, 0.0), 1.0)
        mode = timeline.get("interpolation", "step")
        if mode == "step":
            mix = 1.0
        elif mode == "linear":
            mix = raw_progress
        else:
            mix = raw_progress * raw_progress * (3.0 - 2.0 * raw_progress)
        concept_modes = {
            item["id"]: item.get("interpolation", "linear") for item in plan["concepts"]
        }
        expected_source = {}
        for key in start_source:
            key_mix = 1.0 if mode == "step" or concept_modes.get(key) == "step" else mix
            expected_source[key] = start_source[key] + (
                target_source[key] - start_source[key]
            ) * key_mix
        expected_source, expected_derived = compute_state(plan, expected_source)
        validate_capture(
            audit,
            f"timeline-{label}-state",
            sought,
            plan,
            expected_source,
            expected_derived,
            None,
            phase.get("focusId"),
            expected_time,
            phase["id"],
            raw_progress,
            "full",
        )
        audit_quantitative_semantics(
            page,
            audit,
            f"timeline-{label}-quantitative-semantics",
        )
        audit_relationship_state(
            page,
            audit,
            plan,
            phase.get("focusId"),
            f"timeline-{label}-relationships",
        )
        compare_transition(audit, f"timeline-{label}-propagation", before, sought)
        repeated = invoke(page, "seek", raw_time)
        audit.finish_check(f"timeline-{label}-repeat-transaction", invocation_errors(repeated))
        repeated_capture = capture(page)
        audit.finish_check(
            f"timeline-{label}-idempotence",
            idempotence_errors(sought, repeated_capture),
        )
        invoke(page, "pause")
        page.wait_for_timeout(60)
        settled = capture(page)
        audit.finish_check(
            f"timeline-{label}-paused-stability",
            idempotence_errors(repeated_capture, settled),
        )
        audit.snapshots["timeline"].append(
            {"sample": label, "requestedTimeMs": raw_time, "snapshot": settled["snapshot"]}
        )

    def timeline_semantic_signature(record: dict[str, Any]) -> str:
        payload = {
            "sourceValues": record["snapshot"]["sourceValues"],
            "derivedValues": record["snapshot"]["derivedValues"],
            "timeMs": record["snapshot"]["timeMs"],
            "phaseId": record["snapshot"]["phaseId"],
            "bindings": {
                item["key"]: binding_semantics(item) for item in record["bindings"]
            },
        }
        return canonical(payload)

    history_time = duration * 0.37
    other_time = duration * 0.73
    invoke(page, "reset")
    invoke(page, "pause")
    invoke(page, "seek", history_time)
    history_first = capture(page)
    invoke(page, "seek", other_time)
    invoke(page, "seek", history_time)
    history_second = capture(page)
    audit.finish_check(
        "timeline-history-independent-seek",
        []
        if timeline_semantic_signature(history_first)
        == timeline_semantic_signature(history_second)
        else ["seeking A→B→A produced a different semantic or rendered state at A"],
        {"timeA": history_time, "timeB": other_time},
    )

    invoke(page, "seek", 0)
    seam_start = capture(page)
    invoke(page, "seek", duration)
    seam_end = capture(page)
    seam_start_payload = {
        "sourceValues": seam_start["snapshot"]["sourceValues"],
        "derivedValues": seam_start["snapshot"]["derivedValues"],
        "bindings": {
            item["key"]: binding_semantics(item) for item in seam_start["bindings"]
        },
    }
    seam_end_payload = {
        "sourceValues": seam_end["snapshot"]["sourceValues"],
        "derivedValues": seam_end["snapshot"]["derivedValues"],
        "bindings": {
            item["key"]: binding_semantics(item) for item in seam_end["bindings"]
        },
    }
    audit.finish_check(
        "timeline-loop-seam",
        []
        if canonical(seam_start_payload) == canonical(seam_end_payload)
        else ["the semantic and rendered state at durationMs differs from time zero"],
        {"durationMs": duration},
    )
    audit.metrics["timelineSampleCount"] = len(samples)


def css_time_is_zero(value: str) -> bool:
    parts = [item.strip() for item in value.split(",") if item.strip()]
    return bool(parts) and all(item in {"0s", "0ms"} for item in parts)


def audit_reduced_motion(
    browser: Browser,
    audit: Audit,
    plan: dict[str, Any],
    svg_path: Path,
    timeout_ms: int,
    viewport: dict[str, int],
) -> None:
    context = browser.new_context(viewport=viewport, reduced_motion="reduce")
    page = context.new_page()
    attach_error_collectors(page, audit, "reduced-motion")
    try:
        open_svg(page, svg_path, timeout_ms)
        reduced_plan = page.evaluate("() => window.svgSync.getPlan()")
        if reduced_plan != plan:
            audit.fail("reduced-motion-plan", "reduced-motion load returned a different plan")
        initial_source, initial_derived = scenario_state(plan, plan["initialScenario"])
        initial = capture(page)
        validate_capture(
            audit,
            "reduced-motion-initial",
            initial,
            plan,
            initial_source,
            initial_derived,
            plan["initialScenario"],
            None,
            0,
            None,
            0,
            "reduced",
        )
        play_outcome = invoke(page, "play")
        audit.finish_check("reduced-motion-play-transaction", invocation_errors(play_outcome))
        page.wait_for_timeout(180)
        after_play = capture(page)
        audit.finish_check(
            "reduced-motion-no-autoplay",
            idempotence_errors(initial, after_play),
        )
        reduced_control = page.evaluate(
            """
            () => {
              const control = document.getElementById("control-play");
              return control ? {
                text: (control.querySelector("text")?.textContent || "").trim(),
                label: control.getAttribute("aria-label"),
                pressed: control.getAttribute("aria-pressed"),
                disabled: control.getAttribute("aria-disabled"),
                tabIndex: control.tabIndex
              } : null;
            }
            """
        )
        expected_reduced_control = {
            "text": "Motion disabled",
            "label": "Timeline playback disabled by reduced motion preference",
            "pressed": "false",
            "disabled": "true",
            "tabIndex": -1,
        }
        audit.finish_check(
            "reduced-motion-playback-control",
            [] if reduced_control == expected_reduced_control else [
                f"reduced-motion playback control is {reduced_control!r}, expected {expected_reduced_control!r}"
            ],
            {"control": reduced_control},
        )

        css_state = page.evaluate(
            """
            () => {
              const element = document.querySelector("[data-module-id]");
              const style = getComputedStyle(element);
              return {
                transitionDuration: style.transitionDuration,
                animationDuration: style.animationDuration,
                animationName: style.animationName
              };
            }
            """
        )
        css_errors: list[str] = []
        if not css_time_is_zero(css_state["transitionDuration"]):
            css_errors.append(f"transitionDuration is {css_state['transitionDuration']!r}")
        if not css_time_is_zero(css_state["animationDuration"]):
            css_errors.append(f"animationDuration is {css_state['animationDuration']!r}")
        if css_state["animationName"] != "none":
            css_errors.append(f"animationName is {css_state['animationName']!r}")
        audit.finish_check("reduced-motion-css", css_errors, css_state)

        different = next(
            (item for item in plan["scenarios"] if item["id"] != plan["initialScenario"]),
            plan["scenarios"][0],
        )
        scenario_outcome = invoke(page, "applyScenario", different["id"])
        audit.finish_check("reduced-motion-scenario-transaction", invocation_errors(scenario_outcome))
        scenario_source, scenario_derived = scenario_state(plan, different["id"])
        scenario_capture = capture(page)
        validate_capture(
            audit,
            "reduced-motion-scenario",
            scenario_capture,
            plan,
            scenario_source,
            scenario_derived,
            different["id"],
            None,
            0,
            None,
            0,
            "reduced",
        )
        if plan.get("focusGroups"):
            focus = plan["focusGroups"][0]
            focus_outcome = invoke(page, "setFocus", focus["id"])
            audit.finish_check("reduced-motion-focus-transaction", invocation_errors(focus_outcome))
            focus_capture = capture(page)
            validate_capture(
                audit,
                "reduced-motion-focus",
                focus_capture,
                plan,
                scenario_source,
                scenario_derived,
                different["id"],
                focus["id"],
                0,
                None,
                0,
                "reduced",
            )
            audit_relationship_state(
                page,
                audit,
                plan,
                focus["id"],
                "reduced-motion-relationships",
                reduced_motion=True,
            )
        audit.snapshots["reducedMotion"] = capture(page)["snapshot"]
    finally:
        context.close()


def audit_script_free(
    browser: Browser,
    audit: Audit,
    plan: dict[str, Any],
    svg_path: Path,
    timeout_ms: int,
    viewport: dict[str, int],
) -> None:
    context = browser.new_context(viewport=viewport, java_script_enabled=False)
    page = context.new_page()
    attach_error_collectors(page, audit, "script-free")
    try:
        page.goto(svg_path.as_uri(), wait_until="load", timeout=timeout_ms)
        details = page.evaluate(
            r"""
            () => {
              const root = document.documentElement;
              const visible = (element) => {
                const style = getComputedStyle(element);
                const rect = element.getBoundingClientRect();
                return style.display !== "none" && style.visibility !== "hidden" &&
                  Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
              };
              const relationshipPaths = [...root.querySelectorAll(".relationship-path")];
              const boundMarks = [...root.querySelectorAll("[data-bind]")];
              const hiddenBoundMarks = boundMarks.filter((element) => !visible(element));
              const invalidHiddenBoundMarks = hiddenBoundMarks
                .filter((element) => {
                  const channel = element.getAttribute("data-channel") || "";
                  const value = Number(element.getAttribute("data-current-value"));
                  return channel === "text" || !Number.isFinite(value) || value !== 0;
                })
                .map((element) => ({
                  id: element.id || element.getAttribute("data-role") || element.getAttribute("data-bind"),
                  channel: element.getAttribute("data-channel"),
                  value: element.getAttribute("data-current-value")
                }));
              const visibleRelationshipPath = (path) => {
                const style = getComputedStyle(path);
                return style.display !== "none" && style.visibility !== "hidden" &&
                  Number(style.opacity) > 0 && style.stroke !== "none" && path.getTotalLength() > 0;
              };
              return {
                syncReady: root.getAttribute("data-sync-ready"),
                staticState: root.getAttribute("data-static-state"),
                hasReadyClass: root.classList.contains("svg-sync-ready"),
                runtimePublished: typeof window.svgSync !== "undefined",
                moduleCount: [...root.querySelectorAll("[data-module-id]")].filter(visible).length,
                claimCount: [...root.querySelectorAll(".module-claim")].filter(visible).length,
                boundMarkCount: boundMarks.filter(visible).length,
                zeroHiddenBoundMarkCount: hiddenBoundMarks.length - invalidHiddenBoundMarks.length,
                invalidHiddenBoundMarks,
                interactiveControlCount: root.querySelectorAll(".interactive-control").length,
                visibleInteractiveControlCount: [...root.querySelectorAll(".interactive-control")].filter(visible).length,
                relationshipCount: root.querySelectorAll("[data-relationship-id]").length,
                visibleRelationshipPathCount: relationshipPaths.filter(visibleRelationshipPath).length,
                visiblePulseCount: [...root.querySelectorAll("[data-relationship-pulse]")].filter(visible).length,
                invalidCurrentValues: [...root.querySelectorAll("[data-bind]")]
                  .filter((element) => !Number.isFinite(Number(element.getAttribute("data-current-value"))))
                  .map((element) => element.id || element.getAttribute("data-bind"))
              };
            }
            """
        )
        errors: list[str] = []
        if details.get("syncReady") != "false" or details.get("hasReadyClass"):
            errors.append("script-free root incorrectly reports initialized runtime state")
        if details.get("runtimePublished"):
            errors.append("script-free load unexpectedly published window.svgSync")
        if details.get("staticState") != plan["initialScenario"]:
            errors.append("script-free data-static-state differs from the initial scenario")
        if details.get("moduleCount") != len(plan["modules"]):
            errors.append(
                f"script-free load shows {details.get('moduleCount')} modules, expected {len(plan['modules'])}"
            )
        if details.get("claimCount") != len(plan["modules"]):
            errors.append("script-free load does not show one claim per module")
        if details.get("invalidHiddenBoundMarks"):
            errors.append(
                "script-free load hides nonzero or textual bound marks: "
                f"{details['invalidHiddenBoundMarks']}"
            )
        if details.get("visibleInteractiveControlCount") != 0:
            errors.append("script-free load exposes controls that cannot operate")
        if details.get("relationshipCount") != len(plan.get("relationships", [])):
            errors.append("script-free relationship count differs from the plan")
        if details.get("visibleRelationshipPathCount") != len(plan.get("relationships", [])):
            errors.append("script-free load hides one or more relationship paths")
        if details.get("visiblePulseCount") != 0:
            errors.append("script-free load exposes animated relationship pulses")
        if details.get("invalidCurrentValues"):
            errors.append(
                f"script-free bound marks have invalid literal values: {details['invalidCurrentValues']}"
            )
        audit.finish_check("script-free-fallback", errors, details)
    finally:
        context.close()


def launch_chromium(playwright: Any, args: argparse.Namespace, audit: Audit) -> Browser:
    options = {"headless": not args.headed}
    if args.chromium_executable:
        executable = args.chromium_executable.resolve()
        if not executable.is_file():
            raise RuntimeError(f"Chromium executable does not exist: {executable}")
        return playwright.chromium.launch(executable_path=str(executable), **options)

    attempts: list[str] = []
    try:
        return playwright.chromium.launch(**options)
    except PlaywrightError as exc:
        attempts.append(f"bundled Chromium: {exc}")
    for channel in ("chrome", "msedge"):
        try:
            browser = playwright.chromium.launch(channel=channel, **options)
            audit.warnings.append(f"Bundled Chromium was unavailable; used installed {channel} channel.")
            return browser
        except PlaywrightError as exc:
            attempts.append(f"{channel}: {exc}")
    concise = " | ".join(item.splitlines()[0] for item in attempts)
    raise RuntimeError(
        "Chromium could not be launched. Install it with `uv run playwright install chromium` "
        f"or pass --chromium-executable. Attempts: {concise}"
    )


def audit_normal_page(
    browser: Browser,
    audit: Audit,
    svg_path: Path,
    args: argparse.Namespace,
    screenshot_path: Path | None,
) -> dict[str, Any]:
    viewport = {"width": args.viewport_width, "height": args.viewport_height}
    context: BrowserContext = browser.new_context(viewport=viewport, reduced_motion="no-preference")
    page = context.new_page()
    attach_error_collectors(page, audit, "normal")
    try:
        open_svg(page, svg_path, args.timeout_ms)
        plan = check_api(page, audit)
        if plan.get("timeline", {}).get("autoplay"):
            autoplay_before = capture(page)
            page.wait_for_timeout(120)
            autoplay_after = capture(page)
            autoplay_errors: list[str] = []
            if float(autoplay_after["snapshot"]["timeMs"]) <= float(
                autoplay_before["snapshot"]["timeMs"]
            ):
                autoplay_errors.append("autoplay did not advance the master time")
            captured_controls = autoplay_after.get("controls", {})
            control_items = (
                captured_controls.values()
                if isinstance(captured_controls, dict)
                else captured_controls
            )
            play_control = next(
                (item for item in control_items if item.get("action") == "play"),
                None,
            )
            if not play_control or play_control.get("pressed") != "true":
                autoplay_errors.append("autoplay did not expose a pressed Pause control")
            audit.finish_check(
                "timeline-autoplay",
                autoplay_errors,
                {
                    "beforeTimeMs": autoplay_before["snapshot"]["timeMs"],
                    "afterTimeMs": autoplay_after["snapshot"]["timeMs"],
                },
            )
        invoke(page, "pause")
        invoke(page, "reset")
        audit_visual_geometry(page, audit)
        audit_quantitative_semantics(page, audit, "initial-quantitative-semantics")
        audit_accessibility_tree(page, audit, "initial-accessibility-tree")
        audit_relationship_contrast(page, audit, "initial-relationship-contrast")
        audit_relationship_clearance(page, audit, "initial-relationship-clearance")
        audit_relationship_state(page, audit, plan, None, "initial-relationship-state")
        current = capture(page)
        initial_source, initial_derived = scenario_state(plan, plan["initialScenario"])
        validate_capture(
            audit,
            "initial-snapshot",
            current,
            plan,
            initial_source,
            initial_derived,
            plan["initialScenario"],
            None,
            0,
            None,
            0,
            "full",
        )
        repeated_serialized = page.evaluate("() => window.svgSync.serializeSnapshot()")
        audit.finish_check(
            "initial-snapshot-stability",
            [] if repeated_serialized == current["serialized"] else ["two initial serializations differ"],
        )
        audit.snapshots["initial"] = current["snapshot"]
        audit.metrics["bindingCount"] = len(current["bindings"])

        audit_real_input_controls(page, audit, plan)
        current = capture(page)
        current = audit_scenarios(page, audit, plan, current)
        _ = current
        audit_source_perturbations(page, audit, plan)
        audit_zero_flow_boundaries(page, audit, plan)
        audit_focus(page, audit, plan)
        audit_timeline(page, audit, plan)

        if audit.metrics["negativeControlComparisons"] == 0:
            audit.fail("negative-controls", "no unaffected binding was available for a negative control")
        if audit.metrics["sharedRevisionCases"] == 0:
            audit.fail("shared-revision", "no change updated bindings in at least two modules under one revision")

        if screenshot_path:
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            invoke(page, "reset")
            invoke(page, "pause")
            page.screenshot(path=str(screenshot_path), animations="disabled", timeout=args.timeout_ms)
            audit.finish_check("overview-screenshot", [], {"path": str(screenshot_path)})
        return plan
    finally:
        context.close()


def main() -> int:
    args = parse_args()
    svg_path = args.svg.resolve()
    report_path = args.report.resolve() if args.report else None
    screenshot_path = args.screenshot.resolve() if args.screenshot else None
    audit = Audit(svg_path)

    if args.timeout_ms <= 0:
        audit.fail("arguments", "--timeout-ms must be positive")
    if args.viewport_width < 320 or args.viewport_height < 240:
        audit.fail("arguments", "viewport must be at least 320x240")
    if not svg_path.is_file():
        audit.fail("artifact", f"SVG file does not exist: {svg_path}")
    if report_path == svg_path:
        audit.fail("arguments", "browser report path must not overwrite the input SVG")
        report_path = None
    if screenshot_path == svg_path:
        audit.fail("arguments", "browser screenshot path must not overwrite the input SVG")
        screenshot_path = None
    if report_path is not None and report_path == screenshot_path:
        audit.fail("arguments", "browser report and screenshot paths must be distinct")
        report_path = None
        screenshot_path = None

    if not audit.failures:
        try:
            with sync_playwright() as playwright:
                browser = launch_chromium(playwright, args, audit)
                try:
                    plan = audit_normal_page(browser, audit, svg_path, args, screenshot_path)
                    audit_reduced_motion(
                        browser,
                        audit,
                        plan,
                        svg_path,
                        args.timeout_ms,
                        {"width": args.viewport_width, "height": args.viewport_height},
                    )
                    audit_script_free(
                        browser,
                        audit,
                        plan,
                        svg_path,
                        args.timeout_ms,
                        {"width": args.viewport_width, "height": args.viewport_height},
                    )
                finally:
                    browser.close()
        except (OSError, PlaywrightError, RuntimeError, TypeError, ValueError) as exc:
            audit.fail("browser-audit", str(exc))

    for category, messages in audit.browser_errors.items():
        unique = list(dict.fromkeys(messages))
        audit.browser_errors[category] = unique
        if unique:
            audit.fail(f"browser-{category}-errors", f"observed {len(unique)} error(s)")

    report = audit.report(screenshot_path, report_path)
    if args.compact_report:
        report = compact_report(report)
    if report_path:
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        except OSError as exc:
            audit.fail("report-write", str(exc))
            report = audit.report(screenshot_path, report_path)
            if args.compact_report:
                report = compact_report(report)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Synchronized SVG browser audit: {'PASS' if report['ok'] else 'FAIL'}")
        print(f"Artifact: {svg_path}")
        if report_path:
            print(f"Report: {report_path}")
        if screenshot_path:
            print(f"Screenshot: {screenshot_path}")
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
        for warning in report["warnings"]:
            print(f"WARN: {warning}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
