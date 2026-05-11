#!/usr/bin/env python3
"""
Agora Analytics Dashboard

Usage:
    python3 analytics/dashboard.py           # generate analytics/dashboard.html once
    python3 analytics/dashboard.py --serve   # generate + serve on http://localhost:8765
"""

import json
import os
import sys
import time
import threading
from pathlib import Path
from collections import defaultdict
from statistics import mean
from http.server import HTTPServer, SimpleHTTPRequestHandler

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYTICS_DIR = REPO_ROOT / "analytics"
SESSIONS_FILE = ANALYTICS_DIR / "sessions.jsonl"
SPECIALISTS_FILE = ANALYTICS_DIR / "specialists.jsonl"
IDEAS_INDEX = REPO_ROOT / "ideas_index.md"
OUTPUT_FILE = ANALYTICS_DIR / "dashboard.html"
PORT = 8765

IDEA_COLORS = [
    ("rgba(59,130,246,1)", "rgba(59,130,246,0.15)"),
    ("rgba(245,158,11,1)", "rgba(245,158,11,0.15)"),
    ("rgba(34,197,94,1)", "rgba(34,197,94,0.15)"),
    ("rgba(236,72,153,1)", "rgba(236,72,153,0.15)"),
    ("rgba(139,92,246,1)", "rgba(139,92,246,0.15)"),
]
SPEC_COLORS = {
    "skeptic":        ("rgba(139,92,246,0.8)",  "rgba(139,92,246,0.12)"),
    "tech-lead":      ("rgba(59,130,246,0.8)",  "rgba(59,130,246,0.12)"),
    "market-analyst": ("rgba(34,197,94,0.8)",   "rgba(34,197,94,0.12)"),
    "finance":        ("rgba(245,158,11,0.8)",  "rgba(245,158,11,0.12)"),
    "ux-designer":    ("rgba(236,72,153,0.8)",  "rgba(236,72,153,0.12)"),
    "product-manager":("rgba(6,182,212,0.8)",   "rgba(6,182,212,0.12)"),
    "legal":          ("rgba(239,68,68,0.8)",   "rgba(239,68,68,0.12)"),
    "growth":         ("rgba(132,204,18,0.8)",  "rgba(132,204,18,0.12)"),
}

DIM_ORDER = [
    "problem_statement", "target_user", "core_features", "tech_stack",
    "go_to_market", "key_risks", "poc_scope", "success_metrics",
    "monetization", "budget_estimates",
]
DIM_LABELS = {
    "problem_statement": "Problem Statement",
    "target_user":       "Target User",
    "core_features":     "Core Features",
    "tech_stack":        "Tech Stack",
    "go_to_market":      "Go to Market",
    "key_risks":         "Key Risks",
    "poc_scope":         "PoC Scope",
    "success_metrics":   "Success Metrics",
    "monetization":      "Monetization",
    "budget_estimates":  "Budget Estimates",
}


# ── data loading ──────────────────────────────────────────────────────────

def load_jsonl(path):
    records = []
    if not path.exists():
        return records
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def load_ideas_index(path):
    ideas = []
    if not path.exists():
        return ideas
    with open(path) as f:
        for line in f:
            line = line.strip()
            if (
                line.startswith("|")
                and not line.startswith("|---")
                and "ID" not in line[:20]
                and "Score" not in line[:40]
            ):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 4 and parts[0] and parts[0] != "ID":
                    try:
                        score = int(parts[2].rstrip("%"))
                    except (ValueError, IndexError):
                        score = 0
                    try:
                        sessions_count = int(parts[4]) if len(parts) > 4 else 0
                    except ValueError:
                        sessions_count = 0
                    ideas.append({
                        "id": parts[0],
                        "name": parts[1],
                        "score": score,
                        "status": parts[3] if len(parts) > 3 else "active",
                        "sessions": sessions_count,
                        "last_updated": parts[5] if len(parts) > 5 else "",
                    })
    return ideas


# ── data processing ───────────────────────────────────────────────────────

def process_data():
    sessions = load_jsonl(SESSIONS_FILE)
    specialists = load_jsonl(SPECIALISTS_FILE)
    ideas = load_ideas_index(IDEAS_INDEX)

    sessions_sorted = sorted(sessions, key=lambda x: x["date"])

    # Score progression per idea
    idea_sessions = defaultdict(list)
    for s in sessions_sorted:
        idea_sessions[s["slug"]].append(s)

    # Build score line chart datasets
    score_chart = {"datasets": []}
    for i, idea in enumerate(ideas):
        slug = idea["id"]
        color_border, color_bg = IDEA_COLORS[i % len(IDEA_COLORS)]
        sess = idea_sessions.get(slug, [])
        points = [{"x": s["date"], "y": s["score_after"]} for s in sess]
        if points:
            score_chart["datasets"].append({
                "label": idea["name"],
                "data": points,
                "borderColor": color_border,
                "backgroundColor": color_bg,
                "tension": 0.3,
                "pointRadius": 5,
                "pointHoverRadius": 7,
                "fill": True,
            })

    # KPI dimension hit rates
    dim_counts = defaultdict(lambda: {"met": 0, "partial": 0, "not_met": 0, "total": 0})
    for s in sessions:
        for dt in s.get("kpis", {}).get("dimension_targets", []):
            d = dt["dimension"]
            r = dt["result"]
            dim_counts[d]["total"] += 1
            if r in dim_counts[d]:
                dim_counts[d][r] += 1

    kpi_labels, kpi_values, kpi_colors = [], [], []
    for dim in DIM_ORDER:
        if dim in dim_counts:
            d = dim_counts[dim]
            hit_rate = round(d["met"] / d["total"] * 100) if d["total"] else 0
            kpi_labels.append(DIM_LABELS[dim])
            kpi_values.append(hit_rate)
            kpi_colors.append(
                "rgba(34,197,94,0.7)" if hit_rate >= 70
                else "rgba(245,158,11,0.7)" if hit_rate >= 40
                else "rgba(239,68,68,0.7)"
            )

    kpi_chart = {
        "labels": kpi_labels,
        "datasets": [{
            "label": "Hit Rate %",
            "data": kpi_values,
            "backgroundColor": kpi_colors,
            "borderColor": [c.replace("0.7", "1") for c in kpi_colors],
            "borderWidth": 1,
        }],
    }

    # Specialist aggregates
    spec_groups = defaultdict(list)
    for r in specialists:
        spec_groups[r["specialist"]].append(r)

    spec_summary = []
    RADAR_DIMS = ["adherence", "specificity", "novelty", "responsiveness", "impact"]

    for name, records in spec_groups.items():
        recs = sorted(records, key=lambda x: x["date"])
        overall_scores = [r["overall"] for r in recs]
        avg_overall = round(mean(overall_scores), 2)

        if len(overall_scores) >= 2:
            diff = overall_scores[-1] - overall_scores[0]
            trend = "↑" if diff > 0.2 else ("↓" if diff < -0.2 else "→")
        else:
            trend = "—"

        proposals = sum(1 for r in recs if r["proposal_written"])
        avg_dims = {d: round(mean(r["scores"][d] for r in recs), 2) for d in RADAR_DIMS}
        short_name = name.replace("specialist-", "")

        spec_summary.append({
            "name": name,
            "short_name": short_name,
            "sessions": len(recs),
            "avg_overall": avg_overall,
            "trend": trend,
            "latest_version": recs[-1]["version"],
            "proposals": proposals,
            "avg_dims": avg_dims,
        })

    spec_summary.sort(key=lambda x: x["avg_overall"], reverse=True)

    # Radar chart
    radar_chart = {
        "labels": [d.capitalize() for d in RADAR_DIMS],
        "datasets": [],
    }
    for s in spec_summary:
        sn = s["short_name"]
        border, bg = SPEC_COLORS.get(sn, ("rgba(156,163,175,0.8)", "rgba(156,163,175,0.12)"))
        radar_chart["datasets"].append({
            "label": sn,
            "data": [s["avg_dims"][d] * 20 for d in RADAR_DIMS],  # 1-5 → 20-100
            "backgroundColor": bg,
            "borderColor": border,
            "borderWidth": 2,
            "pointBackgroundColor": border,
            "pointRadius": 3,
        })

    # Ideas panel
    ideas_panel = []
    for i, idea in enumerate(ideas):
        slug = idea["id"]
        sess = idea_sessions.get(slug, [])
        delta = sess[-1]["score_after"] - sess[0]["score_before"] if sess else None
        latest_specs = [s.replace("specialist-", "") for s in (sess[-1]["specialists"] if sess else [])]
        color_border, _ = IDEA_COLORS[i % len(IDEA_COLORS)]
        ideas_panel.append({
            **idea,
            "delta": delta,
            "latest_specialists": latest_specs,
            "color": color_border,
        })

    # Summary stats
    summary = {
        "total_sessions": len(sessions),
        "avg_delta": round(mean(s["delta"] for s in sessions), 1) if sessions else 0,
        "avg_kpi": round(mean(s["kpi_score"] for s in sessions) * 100, 1) if sessions else 0,
        "ideas_tracked": len(ideas),
    }

    # Validation gates
    gates = compute_gates(sessions, spec_summary)

    return {
        "summary": summary,
        "ideas_panel": ideas_panel,
        "sessions_table": [
            {
                "session_id": s["session_id"],
                "idea_name": s["idea_name"],
                "date": s["date"],
                "rounds": s["rounds"],
                "score_before": s["score_before"],
                "score_after": s["score_after"],
                "delta": s["delta"],
                "kpi_score": s["kpi_score"],
                "ended_reason": s["ended_reason"],
            }
            for s in reversed(sessions_sorted)
        ],
        "score_chart": score_chart,
        "kpi_chart": kpi_chart,
        "spec_summary": spec_summary,
        "radar_chart": radar_chart,
        "gates": gates,
    }


def compute_gates(sessions, spec_summary):
    gates = []

    # Gate 1: KPI avg >= 0.60 (3+ sessions)
    if len(sessions) >= 3:
        avg = mean(s["kpi_score"] for s in sessions)
        gates.append({
            "label": "KPI score avg ≥ 60%",
            "status": "pass" if avg >= 0.60 else "fail",
            "detail": f"Avg: {avg * 100:.0f}% across {len(sessions)} sessions",
        })
    else:
        gates.append({
            "label": "KPI score avg ≥ 60%",
            "status": "pending",
            "detail": f"Need 3+ sessions — have {len(sessions)}",
        })

    # Gate 2: delta >= 10% on ideas < 70%
    low = [s for s in sessions if s["score_before"] < 70]
    if low:
        avg_d = mean(s["delta"] for s in low)
        gates.append({
            "label": "Score delta ≥ 10% (ideas < 70%)",
            "status": "pass" if avg_d >= 10 else "fail",
            "detail": f"Avg delta: +{avg_d:.0f}% across {len(low)} sessions",
        })
    else:
        gates.append({
            "label": "Score delta ≥ 10% (ideas < 70%)",
            "status": "pending",
            "detail": "No sessions on ideas below 70%",
        })

    # Gate 3: improvement loop
    gates.append({
        "label": "Improvement loop signal",
        "status": "pending",
        "detail": "Need 2+ sessions per specialist to measure version bump impact",
    })

    # Gate 4: specialist stability
    unstable = [s["short_name"] for s in spec_summary if s["sessions"] >= 3 and s["avg_overall"] < 3.0]
    measured = any(s["sessions"] >= 3 for s in spec_summary)
    if measured:
        gates.append({
            "label": "Specialist stability (avg ≥ 3.0)",
            "status": "fail" if unstable else "pass",
            "detail": f"Failing: {', '.join(unstable)}" if unstable else "All specialists above threshold",
        })
    else:
        gates.append({
            "label": "Specialist stability (avg ≥ 3.0)",
            "status": "pending",
            "detail": "Need 3+ sessions per specialist",
        })

    # Gate 5: control test
    gates.append({
        "label": "Control test",
        "status": "pending",
        "detail": "No control test data recorded yet",
    })

    return gates


# ── HTML generation ───────────────────────────────────────────────────────

def generate_html(data, live=False):
    refresh_tag = '<meta http-equiv="refresh" content="5">' if live else ""
    generated = time.strftime("%Y-%m-%d %H:%M:%S")
    live_badge = (
        '<span class="text-xs bg-green-900 text-green-400 border border-green-700 '
        'px-2 py-0.5 rounded-full ml-2">● LIVE</span>'
        if live else ""
    )

    score_chart_json = json.dumps(data["score_chart"])
    kpi_chart_json = json.dumps(data["kpi_chart"])
    radar_chart_json = json.dumps(data["radar_chart"])

    s = data["summary"]

    # Stat cards
    stat_cards = f"""
        <div class="stat-card">
            <div class="stat-value">{s['total_sessions']}</div>
            <div class="stat-label">Total Sessions</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">+{s['avg_delta']}%</div>
            <div class="stat-label">Avg Score Delta</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{s['avg_kpi']}%</div>
            <div class="stat-label">Avg KPI Score</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{s['ideas_tracked']}</div>
            <div class="stat-label">Ideas Tracked</div>
        </div>
    """

    # Ideas panel
    idea_cards_html = ""
    for idea in data["ideas_panel"]:
        delta_html = ""
        if idea["delta"] is not None:
            color = "text-green-400" if idea["delta"] > 0 else "text-gray-400"
            delta_html = f'<span class="text-sm {color} ml-2">+{idea["delta"]}%</span>'

        specs_html = " ".join(
            f'<span class="spec-tag">{sp}</span>'
            for sp in idea["latest_specialists"]
        ) if idea["latest_specialists"] else '<span class="text-gray-600 text-xs">no sessions yet</span>'

        idea_cards_html += f"""
        <div class="idea-card" style="border-color: {idea['color']}20; box-shadow: 0 0 0 1px {idea['color']}30">
            <div class="flex items-baseline justify-between mb-1">
                <div class="idea-name">{idea['name']}</div>
                <div class="flex items-baseline">
                    <span class="text-4xl font-mono font-bold" style="color:{idea['color']}">{idea['score']}%</span>
                    {delta_html}
                </div>
            </div>
            <div class="text-xs text-gray-500 mb-2">{idea['sessions']} session{'s' if idea['sessions'] != 1 else ''} · {idea['status']} · {idea['last_updated']}</div>
            <div class="flex flex-wrap gap-1">{specs_html}</div>
        </div>
        """

    # Sessions table
    sessions_rows = ""
    for s in data["sessions_table"]:
        delta_color = "text-green-400" if s["delta"] > 0 else "text-gray-400"
        kpi_pct = round(s["kpi_score"] * 100)
        kpi_color = "text-green-400" if kpi_pct >= 60 else "text-yellow-400" if kpi_pct >= 40 else "text-red-400"
        sessions_rows += f"""
            <tr class="border-t border-gray-800 hover:bg-gray-800/30">
                <td class="py-2 px-3 text-gray-300 font-mono text-xs">{s['session_id']}</td>
                <td class="py-2 px-3 text-gray-400 text-sm">{s['date']}</td>
                <td class="py-2 px-3 text-gray-400 text-sm text-center">{s['rounds']}</td>
                <td class="py-2 px-3 text-gray-400 text-sm text-center">{s['score_before']}%</td>
                <td class="py-2 px-3 text-gray-400 text-sm text-center">{s['score_after']}%</td>
                <td class="py-2 px-3 text-sm text-center {delta_color}">+{s['delta']}%</td>
                <td class="py-2 px-3 text-sm text-center {kpi_color}">{kpi_pct}%</td>
                <td class="py-2 px-3 text-gray-500 text-xs">{s['ended_reason']}</td>
            </tr>
        """

    # Specialist table
    spec_rows = ""
    for sp in data["spec_summary"]:
        avg = sp["avg_overall"]
        color = "text-green-400" if avg >= 4.0 else "text-yellow-400" if avg >= 3.0 else "text-red-400"
        trend_color = "text-green-400" if sp["trend"] == "↑" else "text-red-400" if sp["trend"] == "↓" else "text-gray-500"
        prop_html = (
            f'<span class="text-yellow-400">{sp["proposals"]}</span>'
            if sp["proposals"] > 0 else
            '<span class="text-gray-600">0</span>'
        )
        border, _ = SPEC_COLORS.get(sp["short_name"], ("rgba(156,163,175,0.8)", ""))
        spec_rows += f"""
            <tr class="border-t border-gray-800 hover:bg-gray-800/30">
                <td class="py-2 px-3">
                    <span class="text-sm font-medium" style="color:{border}">{sp['short_name']}</span>
                </td>
                <td class="py-2 px-3 text-gray-400 text-sm text-center">{sp['sessions']}</td>
                <td class="py-2 px-3 text-sm text-center font-mono {color}">{avg:.1f}/5</td>
                <td class="py-2 px-3 text-sm text-center {trend_color}">{sp['trend']}</td>
                <td class="py-2 px-3 text-gray-500 text-xs text-center font-mono">{sp['latest_version']}</td>
                <td class="py-2 px-3 text-sm text-center">{prop_html}</td>
            </tr>
        """

    # Validation gates
    gates_html = ""
    for gate in data["gates"]:
        st = gate["status"]
        if st == "pass":
            icon, color, bg = "✓", "text-green-400", "bg-green-900/20 border-green-800"
        elif st == "fail":
            icon, color, bg = "✗", "text-red-400", "bg-red-900/20 border-red-800"
        else:
            icon, color, bg = "—", "text-gray-500", "bg-gray-800/30 border-gray-700"

        gates_html += f"""
        <div class="flex items-start gap-3 p-3 rounded border {bg}">
            <span class="text-lg font-bold {color} w-5 shrink-0">{icon}</span>
            <div>
                <div class="text-sm font-medium {color}">{gate['label']}</div>
                <div class="text-xs text-gray-500 mt-0.5">{gate['detail']}</div>
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {refresh_tag}
  <title>Agora Analytics</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{ background: #0f172a; color: #f8fafc; font-family: ui-monospace, monospace; }}
    .stat-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px 20px; text-align: center; }}
    .stat-value {{ font-size: 2rem; font-weight: 700; color: #f8fafc; font-family: ui-monospace, monospace; }}
    .stat-label {{ font-size: 0.75rem; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }}
    .idea-card {{ background: #1e293b; border-radius: 10px; padding: 16px 20px; }}
    .idea-name {{ font-size: 1rem; font-weight: 600; color: #e2e8f0; }}
    .section {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 20px; }}
    .section-title {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #64748b; margin-bottom: 16px; }}
    .spec-tag {{ background: #334155; color: #94a3b8; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; }}
    canvas {{ max-height: 300px; }}
  </style>
</head>
<body class="min-h-screen p-6">

  <div class="max-w-7xl mx-auto">

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <h1 class="text-2xl font-bold text-white">Agora Analytics</h1>
        {live_badge}
      </div>
      <div class="text-xs text-gray-600">Generated {generated}</div>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-4 gap-4 mb-6">
      {stat_cards}
    </div>

    <!-- Ideas panel -->
    <div class="section mb-6">
      <div class="section-title">Ideas</div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {idea_cards_html}
      </div>
    </div>

    <!-- Score progression chart -->
    <div class="section mb-6">
      <div class="section-title">Score Progression</div>
      <canvas id="scoreChart"></canvas>
    </div>

    <!-- KPI + Specialist table row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

      <div class="section">
        <div class="section-title">KPI Dimension Hit Rates</div>
        <canvas id="kpiChart"></canvas>
      </div>

      <div class="section">
        <div class="section-title">Specialist Performance</div>
        <table class="w-full text-left">
          <thead>
            <tr class="text-gray-600 text-xs uppercase">
              <th class="pb-2 px-3">Specialist</th>
              <th class="pb-2 px-3 text-center">Sessions</th>
              <th class="pb-2 px-3 text-center">Avg</th>
              <th class="pb-2 px-3 text-center">Trend</th>
              <th class="pb-2 px-3 text-center">Version</th>
              <th class="pb-2 px-3 text-center">Props</th>
            </tr>
          </thead>
          <tbody>
            {spec_rows}
          </tbody>
        </table>
      </div>

    </div>

    <!-- Radar + Sessions row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

      <div class="section">
        <div class="section-title">Specialist Skill Radar</div>
        <canvas id="radarChart"></canvas>
      </div>

      <div class="section">
        <div class="section-title">Session History</div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="text-gray-600 uppercase">
                <th class="pb-2 px-3">Session</th>
                <th class="pb-2 px-3">Date</th>
                <th class="pb-2 px-3 text-center">Rnds</th>
                <th class="pb-2 px-3 text-center">Before</th>
                <th class="pb-2 px-3 text-center">After</th>
                <th class="pb-2 px-3 text-center">Delta</th>
                <th class="pb-2 px-3 text-center">KPI</th>
                <th class="pb-2 px-3">End</th>
              </tr>
            </thead>
            <tbody>
              {sessions_rows}
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Validation gates -->
    <div class="section mb-6">
      <div class="section-title">Validation Gates</div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {gates_html}
      </div>
    </div>

  </div>

  <script>
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = '#1e293b';
    Chart.defaults.backgroundColor = 'rgba(255,255,255,0.05)';

    const scoreData = {score_chart_json};
    const kpiData = {kpi_chart_json};
    const radarData = {radar_chart_json};

    // Score progression (time series line chart)
    if (scoreData.datasets.length) {{
      new Chart(document.getElementById('scoreChart'), {{
        type: 'line',
        data: scoreData,
        options: {{
          responsive: true,
          maintainAspectRatio: true,
          scales: {{
            x: {{
              type: 'time',
              time: {{ unit: 'day', tooltipFormat: 'MMM d, yyyy' }},
              grid: {{ color: '#1e293b' }},
              ticks: {{ color: '#64748b' }},
            }},
            y: {{
              min: 0, max: 100,
              grid: {{ color: '#1e293b' }},
              ticks: {{ color: '#64748b', callback: v => v + '%' }},
            }},
          }},
          plugins: {{ legend: {{ labels: {{ color: '#94a3b8', boxWidth: 12 }} }} }},
        }},
      }});
    }} else {{
      document.getElementById('scoreChart').parentElement.innerHTML +=
        '<p class="text-gray-600 text-sm text-center py-4">No session data yet</p>';
      document.getElementById('scoreChart').remove();
    }}

    // KPI hit rates (horizontal bar)
    if (kpiData.labels.length) {{
      new Chart(document.getElementById('kpiChart'), {{
        type: 'bar',
        data: kpiData,
        options: {{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: true,
          scales: {{
            x: {{
              min: 0, max: 100,
              grid: {{ color: '#1e293b' }},
              ticks: {{ color: '#64748b', callback: v => v + '%' }},
            }},
            y: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
          }},
          plugins: {{ legend: {{ display: false }} }},
        }},
      }});
    }} else {{
      document.getElementById('kpiChart').parentElement.innerHTML +=
        '<p class="text-gray-600 text-sm text-center py-4">No KPI target data yet</p>';
      document.getElementById('kpiChart').remove();
    }}

    // Specialist radar
    if (radarData.datasets.length) {{
      new Chart(document.getElementById('radarChart'), {{
        type: 'radar',
        data: radarData,
        options: {{
          responsive: true,
          maintainAspectRatio: true,
          scales: {{
            r: {{
              min: 0, max: 100,
              grid: {{ color: '#334155' }},
              angleLines: {{ color: '#334155' }},
              pointLabels: {{ color: '#94a3b8', font: {{ size: 11 }} }},
              ticks: {{ display: false }},
            }},
          }},
          plugins: {{ legend: {{ labels: {{ color: '#94a3b8', boxWidth: 12 }} }} }},
        }},
      }});
    }}
  </script>

</body>
</html>"""


# ── serving ───────────────────────────────────────────────────────────────

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def log_request(self, *_):
        pass


def watcher(interval=3):
    last_mtimes = {}

    def get_mtimes():
        mtimes = {}
        for f in [SESSIONS_FILE, SPECIALISTS_FILE, IDEAS_INDEX]:
            try:
                mtimes[str(f)] = os.path.getmtime(f)
            except FileNotFoundError:
                pass
        return mtimes

    last_mtimes = get_mtimes()

    while True:
        time.sleep(interval)
        current = get_mtimes()
        if current != last_mtimes:
            last_mtimes = current
            try:
                build(live=True)
                print(f"[{time.strftime('%H:%M:%S')}] Regenerated dashboard.html")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Regeneration error: {e}")


def build(live=False):
    data = process_data()
    html = generate_html(data, live=live)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    return data


# ── entry point ───────────────────────────────────────────────────────────

def main():
    serve = "--serve" in sys.argv

    data = build(live=serve)
    s = data["summary"]
    print(f"Generated: {OUTPUT_FILE}")
    print(f"  {s['total_sessions']} sessions · {s['ideas_tracked']} ideas · avg delta +{s['avg_delta']}% · avg KPI {s['avg_kpi']}%")

    if serve:
        t = threading.Thread(target=watcher, daemon=True)
        t.start()

        os.chdir(ANALYTICS_DIR)
        server = HTTPServer(("", PORT), QuietHandler)
        print(f"\nDashboard: http://localhost:{PORT}/dashboard.html")
        print("Auto-refreshes every 5s. Press Ctrl+C to stop.\n")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
