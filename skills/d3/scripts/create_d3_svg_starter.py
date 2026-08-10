#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create an editable user-owned D3 SVG starter artifact."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


PALETTE = {
    "blue": "#007298",
    "orange": "#e77204",
    "green": "#45842a",
    "red": "#9e1b32",
    "purple": "#652f6c",
    "cyan": "#00ace6",
    "gold": "#f1c319",
    "ink": "#333e48",
    "muted": "#696969",
    "gray50": "#f7f7f7",
    "gray100": "#e7e7e7",
    "gray200": "#cfcfcf",
    "gray300": "#b5b5b5",
    "gray700": "#4f4f4f",
    "surface": "#ffffff",
    "line": "#cfcfcf",
}


STARTER_DATA = {
    "inline-bar-table": {
        "columns": ["Workstream", "Current", "Target", "Status"],
        "rows": [
            {"label": "Discovery", "current": 72, "target": 88, "status": "on track"},
            {"label": "Design", "current": 54, "target": 75, "status": "watch"},
            {"label": "Build", "current": 39, "target": 65, "status": "behind"},
            {"label": "QA", "current": 46, "target": 60, "status": "on track"},
            {"label": "Launch", "current": 28, "target": 52, "status": "watch"},
        ],
    },
    "context-window-matrix": {
        "unitLabel": "1K tokens",
        "segments": [
            {"name": "System", "units": 18, "color": PALETTE["blue"]},
            {"name": "Rules", "units": 22, "color": PALETTE["green"]},
            {"name": "Tools", "units": 30, "color": PALETTE["orange"]},
            {"name": "Task", "units": 14, "color": PALETTE["purple"]},
            {"name": "Files", "units": 36, "color": PALETTE["cyan"]},
            {"name": "Results", "units": 24, "color": PALETTE["gold"]},
            {"name": "Free", "units": 56, "color": PALETTE["gray100"], "unused": True},
        ],
    },
    "animated-network": {
        "nodes": [
            {"id": "Input", "x": 96, "y": 190, "group": "source"},
            {"id": "Plan", "x": 248, "y": 98, "group": "process"},
            {"id": "Tools", "x": 250, "y": 276, "group": "process"},
            {"id": "Check", "x": 410, "y": 130, "group": "review"},
            {"id": "Output", "x": 560, "y": 210, "group": "result"},
        ],
        "links": [
            {"source": "Input", "target": "Plan"},
            {"source": "Input", "target": "Tools"},
            {"source": "Plan", "target": "Check"},
            {"source": "Tools", "target": "Check"},
            {"source": "Check", "target": "Output"},
        ],
    },
    "operational-dashboard": {
        "size": {"width": 960, "height": 560},
        "updatedAt": "2026-06-22 09:00 UTC",
        "threshold": 70,
        "overallScore": 61,
        "kpis": [
            {"label": "Open incidents", "value": "18", "detail": "4 critical, 6 high", "tone": "red"},
            {"label": "Above threshold", "value": "2", "detail": "Payments, identity", "tone": "orange"},
            {"label": "Assets watched", "value": "11", "detail": "3 repeat findings", "tone": "blue"},
            {"label": "Median contain", "value": "3.8h", "detail": "-0.6h this week", "tone": "green"},
        ],
        "services": [
            {
                "service": "Payments API",
                "owner": "Core Platform",
                "score": 82,
                "delta": 6,
                "incidents": 5,
                "status": "critical",
                "history": [68, 72, 76, 79, 82],
            },
            {
                "service": "Identity Gateway",
                "owner": "Trust Engineering",
                "score": 74,
                "delta": 3,
                "incidents": 4,
                "status": "watch",
                "history": [65, 67, 70, 73, 74],
            },
            {
                "service": "Dispatch Ops",
                "owner": "Field Systems",
                "score": 66,
                "delta": -4,
                "incidents": 3,
                "status": "watch",
                "history": [73, 71, 69, 68, 66],
            },
            {
                "service": "Customer Portal",
                "owner": "Digital Experience",
                "score": 58,
                "delta": -2,
                "incidents": 2,
                "status": "stable",
                "history": [62, 61, 60, 59, 58],
            },
            {
                "service": "Device Fleet",
                "owner": "Endpoint Security",
                "score": 47,
                "delta": -5,
                "incidents": 2,
                "status": "stable",
                "history": [56, 54, 52, 50, 47],
            },
            {
                "service": "Data Warehouse",
                "owner": "Analytics Platform",
                "score": 39,
                "delta": -1,
                "incidents": 1,
                "status": "healthy",
                "history": [43, 42, 42, 40, 39],
            },
        ],
        "notes": [
            "Daily review starts at score 70.",
            "Risk is concentrated in identity and payments.",
            "Containment speed improved.",
        ],
    },
    "blank": {
        "points": [
            {"label": "A", "value": 24},
            {"label": "B", "value": 42},
            {"label": "C", "value": 31},
            {"label": "D", "value": 58},
        ],
    },
}


PATTERN_CODE = {
    "inline-bar-table": r"""
function renderStarter(svg, data, palette, width, height) {
  const margin = { top: 68, right: 46, bottom: 44, left: 150 };
  const rows = data.rows;
  const y = d3.scaleBand().domain(rows.map(d => d.label)).range([margin.top, height - margin.bottom]).padding(0.32);
  const x = d3.scaleLinear().domain([0, d3.max(rows, d => Math.max(d.current, d.target))]).nice().range([margin.left, width - margin.right]);
  const statusColor = { "on track": palette.green, "watch": palette.orange, "behind": palette.red };

  svg.append("text").attr("class", "title").attr("x", 32).attr("y", 36).text(window.D3_STARTER_TITLE);
  svg.append("text").attr("class", "caption").attr("x", 32).attr("y", 58).text("Editable inline bar table starter. Change rows in data.js.");

  svg.append("g").attr("class", "grid")
    .selectAll("line").data(x.ticks(5)).join("line")
    .attr("x1", d => x(d)).attr("x2", d => x(d))
    .attr("y1", margin.top - 8).attr("y2", height - margin.bottom + 8)
    .attr("stroke", palette.gray100);

  const row = svg.append("g").selectAll("g").data(rows).join("g")
    .attr("transform", d => `translate(0,${y(d.label)})`);

  row.append("text")
    .attr("class", "mark-label")
    .attr("x", 32)
    .attr("y", y.bandwidth() / 2 + 4)
    .text(d => d.label);

  row.append("rect")
    .attr("x", margin.left)
    .attr("y", 0)
    .attr("width", d => x(d.target) - margin.left)
    .attr("height", y.bandwidth())
    .attr("rx", 5)
    .attr("fill", palette.gray100);

  row.append("rect")
    .attr("x", margin.left)
    .attr("y", 0)
    .attr("width", 0)
    .attr("height", y.bandwidth())
    .attr("rx", 5)
    .attr("fill", d => statusColor[d.status] || palette.blue)
    .append("animate")
    .attr("attributeName", "width")
    .attr("from", 0)
    .attr("to", d => x(d.current) - margin.left)
    .attr("dur", ".75s")
    .attr("begin", (d, i) => `${0.12 + i * 0.08}s`)
    .attr("fill", "freeze");

  row.append("text")
    .attr("class", "value-label")
    .attr("x", d => x(d.current) + 8)
    .attr("y", y.bandwidth() / 2 + 4)
    .text(d => `${d.current} / ${d.target}`);

  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom + 10})`)
    .call(d3.axisBottom(x).ticks(5).tickSizeOuter(0))
    .call(g => g.selectAll("text").attr("class", "caption"))
    .call(g => g.selectAll("path,line").attr("stroke", palette.line));
}
""",
    "context-window-matrix": r"""
function renderStarter(svg, data, palette, width, height) {
  const cols = 20;
  const cell = 20;
  const gap = 3;
  const origin = { x: 72, y: 82 };
  const cells = [];
  data.segments.forEach(segment => {
    d3.range(segment.units).forEach(() => cells.push(segment));
  });
  const total = cells.length;

  svg.append("text").attr("class", "title").attr("x", 32).attr("y", 36).text(window.D3_STARTER_TITLE);
  svg.append("text").attr("class", "caption").attr("x", 32).attr("y", 58).text(`Each cell represents ${data.unitLabel}. Edit segments in data.js.`);

  const cellData = cells.map((segment, index) => ({
    ...segment,
    index,
    col: index % cols,
    row: Math.floor(index / cols)
  }));

  svg.append("g").selectAll("rect").data(cellData).join("rect")
    .attr("x", d => origin.x + d.col * (cell + gap))
    .attr("y", d => origin.y + d.row * (cell + gap))
    .attr("width", cell)
    .attr("height", cell)
    .attr("rx", 4)
    .attr("fill", palette.gray100)
    .attr("stroke", palette.surface);

  const used = cellData.filter(d => !d.unused);
  svg.append("g").selectAll("rect").data(used).join("rect")
    .attr("x", d => origin.x + d.col * (cell + gap))
    .attr("y", d => origin.y + d.row * (cell + gap))
    .attr("width", cell)
    .attr("height", cell)
    .attr("rx", 4)
    .attr("fill", d => d.color)
    .attr("stroke", palette.surface)
    .attr("opacity", 0)
    .append("animate")
    .attr("attributeName", "opacity")
    .attr("from", 0)
    .attr("to", 1)
    .attr("dur", ".16s")
    .attr("begin", (d, i) => `${0.18 + i * 0.012}s`)
    .attr("fill", "freeze");

  const legend = svg.append("g").attr("transform", `translate(${width - 176},86)`);
  legend.selectAll("g").data(data.segments).join("g")
    .attr("transform", (d, i) => `translate(0,${i * 24})`)
    .call(g => {
      g.append("rect").attr("width", 13).attr("height", 13).attr("rx", 3).attr("fill", d => d.color);
      g.append("text").attr("class", "caption").attr("x", 20).attr("y", 11).text(d => `${d.name} (${d.units})`);
    });

  svg.append("text")
    .attr("class", "mark-label")
    .attr("x", origin.x + cols * (cell + gap) / 2)
    .attr("y", height - 34)
    .attr("text-anchor", "middle")
    .text(`${used.length} / ${total} cells used`);
}
""",
    "animated-network": r"""
function renderStarter(svg, data, palette, width, height) {
  const nodeById = new Map(data.nodes.map(d => [d.id, d]));
  const color = { source: palette.blue, process: palette.purple, review: palette.orange, result: palette.green };

  svg.append("text").attr("class", "title").attr("x", 32).attr("y", 36).text(window.D3_STARTER_TITLE);
  svg.append("text").attr("class", "caption").attr("x", 32).attr("y", 58).text("Fixed-position animated network starter. Edit nodes and links in data.js.");

  const link = svg.append("g").selectAll("line").data(data.links).join("line")
    .attr("x1", d => nodeById.get(d.source).x)
    .attr("y1", d => nodeById.get(d.source).y)
    .attr("x2", d => nodeById.get(d.target).x)
    .attr("y2", d => nodeById.get(d.target).y)
    .attr("stroke", palette.line)
    .attr("stroke-width", 2.5)
    .attr("stroke-dasharray", "8 8");

  link.append("animate")
    .attr("attributeName", "stroke-dashoffset")
    .attr("from", 40)
    .attr("to", 0)
    .attr("dur", "1.2s")
    .attr("begin", (d, i) => `${0.12 + i * 0.08}s`)
    .attr("fill", "freeze");

  const node = svg.append("g").selectAll("g").data(data.nodes).join("g")
    .attr("transform", d => `translate(${d.x},${d.y})`);

  node.append("circle")
    .attr("r", 0)
    .attr("fill", d => color[d.group] || palette.blue)
    .attr("fill-opacity", 0.86)
    .attr("stroke", palette.surface)
    .attr("stroke-width", 4)
    .append("animate")
    .attr("attributeName", "r")
    .attr("from", 0)
    .attr("to", 28)
    .attr("dur", ".45s")
    .attr("begin", (d, i) => `${0.2 + i * 0.1}s`)
    .attr("fill", "freeze");

  node.append("text")
    .attr("class", "reverse-label")
    .attr("text-anchor", "middle")
    .attr("dy", ".35em")
    .text(d => d.id);
}
""",
    "operational-dashboard": r"""
function renderStarter(svg, data, palette, width, height) {
  const tone = {
    critical: { fill: palette.red, soft: "#ffccd5" },
    watch: { fill: palette.orange, soft: "#ffe5cc" },
    stable: { fill: palette.blue, soft: "#cdf3ff" },
    healthy: { fill: palette.green, soft: "#dbffcc" },
    red: { fill: palette.red, soft: "#ffccd5" },
    orange: { fill: palette.orange, soft: "#ffe5cc" },
    blue: { fill: palette.blue, soft: "#cdf3ff" },
    green: { fill: palette.green, soft: "#dbffcc" }
  };

  function colorFor(value) {
    return tone[value] || tone.blue;
  }

  function shortText(value, maxLength) {
    const text = String(value);
    return text.length > maxLength ? `${text.slice(0, maxLength - 1)}...` : text;
  }

  function wrapWords(value, maxChars) {
    const words = String(value).split(/\s+/);
    const lines = [];
    let line = "";
    words.forEach(word => {
      const next = line ? `${line} ${word}` : word;
      if (next.length > maxChars && line) {
        lines.push(line);
        line = word;
      } else {
        line = next;
      }
    });
    if (line) lines.push(line);
    return lines.slice(0, 2);
  }

  svg.append("rect").attr("x", 0).attr("y", 0).attr("width", width).attr("height", height).attr("fill", palette.surface);
  svg.append("rect").attr("x", 24).attr("y", 20).attr("width", width - 48).attr("height", height - 40).attr("rx", 16).attr("fill", palette.surface).attr("stroke", palette.gray100);

  svg.append("text").attr("class", "caption").attr("x", 44).attr("y", 52).text("Operational dashboard | daily control view");
  svg.append("text").attr("class", "title dashboard-title").attr("x", 44).attr("y", 84).text(window.D3_STARTER_TITLE);
  svg.append("text").attr("class", "caption").attr("x", 44).attr("y", 106).text(`${data.updatedAt} | ${data.services.length} monitored services | escalation threshold ${data.threshold}`);

  const cardY = 126;
  const cardW = 210;
  const cardH = 76;
  svg.append("g").selectAll("g.kpi").data(data.kpis.slice(0, 4)).join("g")
    .attr("class", "kpi")
    .attr("transform", (d, i) => `translate(${44 + i * (cardW + 12)},${cardY})`)
    .call(group => {
      group.append("rect").attr("width", cardW).attr("height", cardH).attr("rx", 12).attr("fill", d => colorFor(d.tone).soft).attr("stroke", palette.gray100);
      group.append("text").attr("class", "kpi-label").attr("x", 16).attr("y", 24).text(d => shortText(d.label, 24));
      group.append("text").attr("class", "kpi-value").attr("x", 16).attr("y", 52).attr("fill", d => colorFor(d.tone).fill).text(d => d.value);
      group.append("text").attr("class", "kpi-detail").attr("x", 16).attr("y", 68).text(d => shortText(d.detail, 28));
      group.attr("opacity", 0).append("animate").attr("attributeName", "opacity").attr("from", 0).attr("to", 1).attr("dur", ".45s").attr("begin", (d, i) => `${0.1 + i * 0.08}s`).attr("fill", "freeze");
    });

  const table = { x: 44, y: 248, w: 638, rowH: 42, labelW: 184, barW: 290 };
  const barX = table.x + table.labelW;
  const scoreX = barX + table.barW + 16;
  const sparkX = scoreX + 72;
  const sparkW = 76;
  const rows = data.services.slice(0, 6);
  const x = d3.scaleLinear().domain([0, 100]).range([barX, barX + table.barW]);
  const sparkScaleX = d3.scaleLinear().domain([0, 4]).range([0, sparkW]);
  const sparkScaleY = d3.scaleLinear().domain([0, 100]).range([22, 0]);
  const thresholdX = x(data.threshold);

  svg.append("text").attr("class", "panel-title").attr("x", table.x).attr("y", 222).text("Service risk by exposure score");
  svg.append("text").attr("class", "small-label").attr("x", table.x).attr("y", table.y - 10).text("Service / owner");
  svg.append("text").attr("class", "small-label").attr("x", barX).attr("y", table.y - 10).text("Risk score");
  svg.append("text").attr("class", "small-label").attr("x", scoreX).attr("y", table.y - 10).text("Score");
  svg.append("text").attr("class", "small-label").attr("x", sparkX).attr("y", table.y - 10).text("Trend");
  svg.append("line").attr("x1", thresholdX).attr("x2", thresholdX).attr("y1", table.y - 8).attr("y2", table.y + rows.length * table.rowH - 8).attr("stroke", palette.red).attr("stroke-width", 2).attr("stroke-dasharray", "4 4");
  svg.append("text").attr("class", "small-label").attr("x", thresholdX + 7).attr("y", table.y + rows.length * table.rowH + 10).attr("fill", palette.red).text(`Threshold ${data.threshold}`);

  const row = svg.append("g").selectAll("g.row").data(rows).join("g")
    .attr("class", "row")
    .attr("transform", (d, i) => `translate(0,${table.y + i * table.rowH})`);

  row.append("rect").attr("x", table.x).attr("y", 4).attr("width", table.w).attr("height", table.rowH - 8).attr("rx", 9).attr("fill", (d, i) => i % 2 === 0 ? "#fbfbfb" : palette.surface).attr("stroke", palette.gray100);
  row.append("text").attr("class", "row-label").attr("x", table.x + 14).attr("y", 20).text(d => shortText(d.service, 24));
  row.append("text").attr("class", "row-owner").attr("x", table.x + 14).attr("y", 34).text(d => shortText(d.owner, 26));
  row.append("rect").attr("x", barX).attr("y", 12).attr("width", table.barW).attr("height", 16).attr("rx", 8).attr("fill", palette.gray100);
  row.append("rect").attr("x", barX).attr("y", 12).attr("height", 16).attr("rx", 8).attr("width", 0).attr("fill", d => colorFor(d.status).fill)
    .append("animate").attr("attributeName", "width").attr("from", 0).attr("to", d => x(d.score) - barX).attr("dur", ".7s").attr("begin", (d, i) => `${0.25 + i * 0.08}s`).attr("fill", "freeze");
  row.append("circle").attr("cx", thresholdX).attr("cy", 20).attr("r", 3.5).attr("fill", palette.surface).attr("stroke", palette.red).attr("stroke-width", 2);
  row.append("text").attr("class", "score-label").attr("x", scoreX).attr("y", 24).text(d => d.score);
  row.append("text").attr("class", "delta-label").attr("x", scoreX + 28).attr("y", 24).attr("fill", d => d.delta > 0 ? palette.red : palette.green).text(d => d.delta > 0 ? `+${d.delta}` : d.delta);
  row.append("path").attr("transform", `translate(${sparkX},10)`).attr("fill", "none").attr("stroke", d => colorFor(d.status).fill).attr("stroke-width", 2)
    .attr("d", d => d3.line().x((v, i) => sparkScaleX(i)).y(v => sparkScaleY(v)).curve(d3.curveMonotoneX)(d.history));
  row.append("circle").attr("cx", sparkX + sparkW).attr("cy", d => 10 + sparkScaleY(d.history[d.history.length - 1])).attr("r", 3).attr("fill", d => colorFor(d.status).fill);

  const side = { x: 700, y: 232, w: 216, h: 304 };
  svg.append("rect").attr("x", side.x).attr("y", side.y).attr("width", side.w).attr("height", side.h).attr("rx", 14).attr("fill", "#fcfcfc").attr("stroke", palette.gray100);
  svg.append("text").attr("class", "panel-title").attr("x", side.x + 18).attr("y", side.y + 28).text("Control posture");
  svg.append("text").attr("class", "big-score").attr("x", side.x + 18).attr("y", side.y + 110).text(data.overallScore);
  svg.append("text").attr("class", "caption").attr("x", side.x + 18).attr("y", side.y + 134).text("Weighted risk index");

  const legend = [
    { label: "0-49 healthy", fill: palette.green },
    { label: "50-69 watch", fill: palette.blue },
    { label: "70+ escalated", fill: palette.red }
  ];
  svg.append("g").selectAll("g.legend").data(legend).join("g")
    .attr("class", "legend")
    .attr("transform", (d, i) => `translate(${side.x + 18},${side.y + 158 + i * 22})`)
    .call(group => {
      group.append("circle").attr("r", 5).attr("cy", -4).attr("fill", d => d.fill);
      group.append("text").attr("class", "caption").attr("x", 14).attr("y", 0).text(d => d.label);
    });

  svg.append("text").attr("class", "panel-title").attr("x", side.x + 18).attr("y", side.y + 226).text("Analyst notes");
  const noteLines = data.notes.flatMap((note, noteIndex) => wrapWords(note, 31).map((line, lineIndex) => ({
    text: `${lineIndex === 0 ? "- " : "  "}${line}`,
    noteIndex,
    lineIndex
  }))).slice(0, 5);
  svg.append("g").selectAll("text.note").data(noteLines).join("text")
    .attr("class", "caption")
    .attr("x", side.x + 18)
    .attr("y", (d, i) => side.y + 246 + i * 14)
    .text(d => d.text);

  svg.append("text").attr("class", "small-label").attr("x", 44).attr("y", 526).text("Bars encode current exposure score; sparklines show five recent checkpoints. Edit only data.js for routine updates.");
}
""",
    "blank": r"""
function renderStarter(svg, data, palette, width, height) {
  const margin = { top: 70, right: 42, bottom: 50, left: 56 };
  const x = d3.scalePoint().domain(data.points.map(d => d.label)).range([margin.left, width - margin.right]).padding(0.4);
  const y = d3.scaleLinear().domain([0, d3.max(data.points, d => d.value)]).nice().range([height - margin.bottom, margin.top]);
  const line = d3.line().x(d => x(d.label)).y(d => y(d.value)).curve(d3.curveCatmullRom.alpha(0.5));

  svg.append("text").attr("class", "title").attr("x", 32).attr("y", 36).text(window.D3_STARTER_TITLE);
  svg.append("text").attr("class", "caption").attr("x", 32).attr("y", 58).text("Blank starter with a small editable line chart.");

  svg.append("path")
    .datum(data.points)
    .attr("fill", "none")
    .attr("stroke", palette.blue)
    .attr("stroke-width", 3)
    .attr("d", line)
    .attr("stroke-dasharray", 600)
    .attr("stroke-dashoffset", 0)
    .append("animate")
    .attr("attributeName", "stroke-dashoffset")
    .attr("from", 600)
    .attr("to", 0)
    .attr("dur", "1s")
    .attr("fill", "freeze");

  svg.append("g").selectAll("circle").data(data.points).join("circle")
    .attr("cx", d => x(d.label))
    .attr("cy", d => y(d.value))
    .attr("r", 5)
    .attr("fill", palette.orange);

  svg.append("g").attr("transform", `translate(0,${height - margin.bottom})`).call(d3.axisBottom(x));
  svg.append("g").attr("transform", `translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(4));
}
""",
}


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <link rel="stylesheet" href="styles.css">
  __D3_SCRIPT__
  <script src="data.js"></script>
</head>
<body>
  <main class="page">
    <svg id="visual" role="img" aria-labelledby="visual-title visual-desc"></svg>
  </main>
  <script>
    const palette = __PALETTE_JSON__;
    window.D3_STARTER_TITLE = __TITLE_JSON__;
    const starterSize = window.D3_STARTER_DATA.size || { width: 720, height: 420 };
    const width = starterSize.width;
    const height = starterSize.height;

    function prepareSvg(id, title, desc) {
      const svg = d3.select(`#${id}`);
      svg.selectAll("*").remove();
      svg
        .attr("viewBox", `0 0 ${width} ${height}`)
        .attr("font-family", "Open Sans, Arial, sans-serif")
        .attr("role", "img")
        .attr("aria-labelledby", `${id}-title ${id}-desc`);
      svg.append("title").attr("id", `${id}-title`).text(title);
      svg.append("desc").attr("id", `${id}-desc`).text(desc);
      return svg;
    }

    __PATTERN_CODE__

    function main() {
      if (!window.d3) {
        document.body.innerHTML = '<p class="error">D3 failed to load. Serve this folder locally or connect to the network.</p>';
        return;
      }
      const svg = prepareSvg("visual", window.D3_STARTER_TITLE, "__DESC__");
      renderStarter(svg, window.D3_STARTER_DATA, palette, width, height);
    }

    main();
  </script>
</body>
</html>
"""


STYLE_CSS = """html,
body {
  margin: 0;
  min-height: 100%;
  background: #f7f7f7;
  color: #333e48;
  font-family: "Open Sans", Arial, sans-serif;
}

.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

svg {
  width: min(100%, 960px);
  height: auto;
  background: #ffffff;
  border: 1px solid #cfcfcf;
}

.title {
  fill: #333e48;
  font-size: 18px;
  font-weight: 750;
}

.caption {
  fill: #4f4f4f;
  font-size: 12px;
  paint-order: stroke;
  stroke: #ffffff;
  stroke-width: 3px;
  stroke-linejoin: round;
}

.mark-label {
  fill: #333e48;
  font-size: 12px;
  font-weight: 650;
  paint-order: stroke;
  stroke: #ffffff;
  stroke-width: 3px;
  stroke-linejoin: round;
}

.reverse-label {
  fill: #ffffff;
  font-size: 12px;
  font-weight: 750;
  paint-order: stroke;
  stroke: #333e48;
  stroke-width: 2px;
  stroke-linejoin: round;
}

.value-label {
  fill: #333e48;
  font-size: 12px;
  font-weight: 650;
}

.dashboard-title {
  font-size: 26px;
  font-weight: 800;
}

.panel-title,
.row-label,
.score-label {
  fill: #333e48;
  font-size: 13px;
  font-weight: 750;
}

.row-owner,
.small-label,
.delta-label {
  fill: #696969;
  font-size: 11px;
}

.kpi-label {
  fill: #696969;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.kpi-value {
  fill: #333e48;
  font-size: 28px;
  font-weight: 800;
}

.kpi-detail {
  fill: #333e48;
  font-size: 12px;
}

.big-score {
  fill: #333e48;
  font-size: 64px;
  font-weight: 800;
}

.error {
  max-width: 620px;
  margin: 32px auto;
  padding: 16px;
  background: #ffffff;
  border: 1px solid #cfcfcf;
}
"""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "d3-svg-starter"


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def local_d3_source() -> Path | None:
    candidate = skill_root() / "assets" / "examples" / "d3-animated-svg" / "node_modules" / "d3" / "dist" / "d3.min.js"
    if candidate.exists():
        return candidate
    return None


def d3_script_tag(out_dir: Path) -> str:
    source = local_d3_source()
    if source:
        vendor_dir = out_dir / "vendor"
        vendor_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, vendor_dir / "d3.min.js")
        return '<script src="vendor/d3.min.js"></script>'
    return '<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>'


def write_starter(out_dir: Path, pattern: str, title: str, force: bool, allow_skill_dir: bool) -> dict:
    resolved_out = out_dir.resolve()
    if is_inside(resolved_out, skill_root()) and not allow_skill_dir:
        raise SystemExit(
            f"Refusing to write inside the skill directory: {resolved_out}. "
            "Choose a user output path or pass --allow-skill-dir for intentional skill maintenance."
        )
    if resolved_out.exists() and any(resolved_out.iterdir()) and not force:
        raise SystemExit(f"Output directory is not empty: {resolved_out}. Pass --force to overwrite starter files.")
    resolved_out.mkdir(parents=True, exist_ok=True)

    data = STARTER_DATA[pattern]
    desc = f"Editable D3 starter using the {pattern} pattern."
    script_tag = d3_script_tag(resolved_out)
    html = (
        HTML_TEMPLATE.replace("__TITLE__", title)
        .replace("__TITLE_JSON__", json.dumps(title))
        .replace("__DESC__", desc)
        .replace("__PALETTE_JSON__", json.dumps(PALETTE, indent=2))
        .replace("__D3_SCRIPT__", script_tag)
        .replace("__PATTERN_CODE__", PATTERN_CODE[pattern].strip())
    )

    (resolved_out / "index.html").write_text(html, encoding="utf-8")
    (resolved_out / "styles.css").write_text(STYLE_CSS, encoding="utf-8")
    (resolved_out / "data.js").write_text(
        "window.D3_STARTER_DATA = "
        + json.dumps(data, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    notes = f"""# D3 SVG Starter

Pattern: `{pattern}`
Title: `{title}`

Edit `data.js` first, then adjust `index.html` when the geometry or labels need to change.
This artifact is user-owned and intentionally separate from the unified D3 skill's legacy gallery fixture.

Suggested validation:

```powershell
uv run --script skills/d3/scripts/render_d3_svg.py {resolved_out / "index.html"} --selector "svg" -o {resolved_out / "rendered.svg"} --screenshot {resolved_out / "rendered.png"} --wait-ms 1200
```
"""
    (resolved_out / "NOTES.md").write_text(notes, encoding="utf-8")
    manifest = {
        "pattern": pattern,
        "title": title,
        "files": ["index.html", "styles.css", "data.js", "NOTES.md"],
        "usesLocalD3": (resolved_out / "vendor" / "d3.min.js").exists(),
    }
    (resolved_out / "starter-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", choices=sorted(STARTER_DATA), default="inline-bar-table")
    parser.add_argument("--out", type=Path, required=True, help="User-owned output directory for the starter files.")
    parser.add_argument("--title", default="Editable D3 SVG starter")
    parser.add_argument("--force", action="store_true", help="Overwrite starter files in a non-empty output directory.")
    parser.add_argument(
        "--allow-skill-dir",
        action="store_true",
        help="Allow writing inside the skill directory for intentional skill maintenance.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = write_starter(args.out, args.pattern, args.title, args.force, args.allow_skill_dir)
    print(f"Created D3 starter: {args.out.resolve()}")
    print(f"Pattern: {manifest['pattern']}")
    print("Files: " + ", ".join(manifest["files"]))
    if manifest["usesLocalD3"]:
        print("D3 runtime: copied local vendor/d3.min.js")
    else:
        print("D3 runtime: CDN fallback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
