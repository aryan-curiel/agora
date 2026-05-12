"""
Agora Analytics Dashboard

Usage:
    cd analytics && streamlit run dashboard.py
"""

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYTICS_DIR = REPO_ROOT / "analytics"
SESSIONS_FILE = ANALYTICS_DIR / "sessions.jsonl"
SPECIALISTS_FILE = ANALYTICS_DIR / "specialists.jsonl"
BRAINSTORMS_FILE = ANALYTICS_DIR / "brainstorms.jsonl"
DREAMERS_FILE = ANALYTICS_DIR / "dreamers.jsonl"
IDEAS_INDEX = REPO_ROOT / "ideas_index.md"

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
DIM_ORDER = list(DIM_LABELS.keys())
RADAR_DIMS = ["adherence", "specificity", "novelty", "responsiveness", "impact"]
DREAMER_DIMS = ["originality", "specificity", "cross_pollination", "horizon_adherence"]
DREAMER_DIM_LABELS = {
    "originality":        "Originality",
    "specificity":        "Specificity",
    "cross_pollination":  "Cross-Pollination",
    "horizon_adherence":  "Horizon Adherence",
}
DREAMER_ROLES = {
    "dreamer-futurist":       "The Futurist",
    "dreamer-builder":        "The Builder",
    "dreamer-user-advocate":  "The User Advocate",
    "dreamer-connector":      "The Connector",
    "dreamer-narrativist":    "The Narrativist",
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
                    try:
                        brainstorms_count = int(parts[5]) if len(parts) > 5 else 0
                    except ValueError:
                        brainstorms_count = 0
                    ideas.append({
                        "id": parts[0],
                        "name": parts[1],
                        "score": score,
                        "status": parts[3] if len(parts) > 3 else "active",
                        "sessions": sessions_count,
                        "brainstorms": brainstorms_count,
                        "last_updated": parts[6] if len(parts) > 6 else "",
                    })
    return ideas


# ── validation gates ──────────────────────────────────────────────────────

def compute_gates(sessions, spec_summary):
    gates = []

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

    gates.append({
        "label": "Improvement loop signal",
        "status": "pending",
        "detail": "Need 2+ sessions per specialist to measure version bump impact",
    })

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

    gates.append({
        "label": "Control test",
        "status": "pending",
        "detail": "No control test data recorded yet",
    })

    return gates


# ── main ──────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Agora Analytics", layout="wide")
st.title("Agora Analytics")

sessions = load_jsonl(SESSIONS_FILE)
specialists = load_jsonl(SPECIALISTS_FILE)
brainstorms = load_jsonl(BRAINSTORMS_FILE)
dreamers_raw = load_jsonl(DREAMERS_FILE)
ideas = load_ideas_index(IDEAS_INDEX)

sessions_sorted = sorted(sessions, key=lambda x: x["date"])
idea_sessions = defaultdict(list)
for s in sessions_sorted:
    idea_sessions[s["slug"]].append(s)

# ── summary stats ─────────────────────────────────────────────────────────

total_proposals = sum(b["proposals_generated"] for b in brainstorms)
avg_delta = round(mean(s["delta"] for s in sessions), 1) if sessions else 0
avg_kpi = round(mean(s["kpi_score"] for s in sessions) * 100, 1) if sessions else 0

cols = st.columns(6)
cols[0].metric("Debate Sessions", len(sessions))
cols[1].metric("Avg Score Delta", f"+{avg_delta}%")
cols[2].metric("Avg KPI Score", f"{avg_kpi}%")
cols[3].metric("Ideas Tracked", len(ideas))
cols[4].metric("Brainstorm Sessions", len(brainstorms))
cols[5].metric("Proposals Generated", total_proposals)

st.divider()

# ── ideas panel ───────────────────────────────────────────────────────────

st.subheader("Ideas")
if ideas:
    idea_rows = []
    for idea in ideas:
        sess = idea_sessions.get(idea["id"], [])
        delta = sess[-1]["score_after"] - sess[0]["score_before"] if sess else None
        idea_rows.append({
            "Name": idea["name"],
            "Score": idea["score"],
            "Delta": delta,
            "Status": idea["status"],
            "Sessions": idea["sessions"],
            "Brainstorms": idea["brainstorms"],
            "Last Updated": idea["last_updated"],
        })
    st.dataframe(
        pd.DataFrame(idea_rows),
        hide_index=True,
        width='stretch',
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score", min_value=0, max_value=100, format="%d%%"
            ),
            "Delta": st.column_config.NumberColumn("Delta", format="+%d%%"),
        },
    )
else:
    st.info("No ideas found in ideas_index.md.")

st.divider()

# ── score progression ─────────────────────────────────────────────────────

st.subheader("Score Progression")
score_rows = []
for idea in ideas:
    for s in idea_sessions.get(idea["id"], []):
        score_rows.append({"date": s["date"], "score": s["score_after"], "idea": idea["name"]})

if score_rows:
    df_scores = pd.DataFrame(score_rows)
    df_scores["date"] = pd.to_datetime(df_scores["date"])
    fig = px.line(df_scores, x="date", y="score", color="idea", markers=True,
                  range_y=[0, 100], labels={"score": "Score (%)", "date": "Date", "idea": "Idea"})
    fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig, width='stretch')
else:
    st.info("No session data yet.")

# ── KPI hit rates + specialist table ─────────────────────────────────────

left, right = st.columns(2)

with left:
    st.subheader("KPI Dimension Hit Rates")
    dim_counts = defaultdict(lambda: {"met": 0, "total": 0})
    for s in sessions:
        for dt in s.get("kpis", {}).get("dimension_targets", []):
            d = dt["dimension"]
            dim_counts[d]["total"] += 1
            if dt["result"] == "met":
                dim_counts[d]["met"] += 1

    kpi_rows = []
    for dim in DIM_ORDER:
        if dim in dim_counts:
            d = dim_counts[dim]
            hit = round(d["met"] / d["total"] * 100) if d["total"] else 0
            kpi_rows.append({"dimension": DIM_LABELS[dim], "hit_rate": hit})

    if kpi_rows:
        df_kpi = pd.DataFrame(kpi_rows)
        fig = px.bar(df_kpi, x="hit_rate", y="dimension", orientation="h",
                     range_x=[0, 100], labels={"hit_rate": "Hit Rate (%)", "dimension": ""})
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No KPI target data yet.")

with right:
    st.subheader("Specialist Performance")
    spec_groups = defaultdict(list)
    for r in specialists:
        spec_groups[r["specialist"]].append(r)

    spec_summary = []
    for name, records in spec_groups.items():
        recs = sorted(records, key=lambda x: x["date"])
        overall_scores = [r["overall"] for r in recs]
        avg_overall = round(mean(overall_scores), 2)
        diff = overall_scores[-1] - overall_scores[0] if len(overall_scores) >= 2 else 0
        trend = "↑" if diff > 0.2 else ("↓" if diff < -0.2 else "→")
        avg_dims = {d: round(mean(r["scores"][d] for r in recs), 2) for d in RADAR_DIMS}
        spec_summary.append({
            "name": name,
            "short_name": name.replace("specialist-", ""),
            "sessions": len(recs),
            "avg_overall": avg_overall,
            "trend": trend,
            "latest_version": recs[-1]["version"],
            "proposals": sum(1 for r in recs if r["proposal_written"]),
            "avg_dims": avg_dims,
        })
    spec_summary.sort(key=lambda x: x["avg_overall"], reverse=True)

    if spec_summary:
        df_spec = pd.DataFrame([{
            "Specialist": s["short_name"],
            "Sessions": s["sessions"],
            "Avg Score": f"{s['avg_overall']:.1f}/5",
            "Trend": s["trend"],
            "Version": s["latest_version"],
            "Proposals": s["proposals"],
        } for s in spec_summary])
        st.dataframe(df_spec, hide_index=True, width='stretch')
    else:
        st.info("No specialist data yet.")

st.divider()

# ── radar + session history ───────────────────────────────────────────────

left, right = st.columns(2)

with left:
    st.subheader("Specialist Skill Radar")
    if spec_summary:
        fig = go.Figure()
        categories = [d.capitalize() for d in RADAR_DIMS]
        for s in spec_summary:
            vals = [s["avg_dims"][d] * 20 for d in RADAR_DIMS]
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=categories + [categories[0]],
                name=s["short_name"],
                fill="toself",
                opacity=0.6,
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=30, b=60),
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No specialist data yet.")

with right:
    st.subheader("Session History")
    if sessions_sorted:
        df_sess = pd.DataFrame([{
            "Idea": s["idea_name"],
            "Date": s["date"],
            "Rounds": s["rounds"],
            "Before": f"{s['score_before']}%",
            "After": f"{s['score_after']}%",
            "Delta": f"+{s['delta']}%",
            "KPI": f"{round(s['kpi_score'] * 100)}%",
            "End": s["ended_reason"],
        } for s in reversed(sessions_sorted)])
        st.dataframe(df_sess, hide_index=True, width='stretch')
    else:
        st.info("No session data yet.")

st.divider()

# ── validation gates ──────────────────────────────────────────────────────

st.subheader("Validation Gates")
gates = compute_gates(sessions, spec_summary)
STATUS_LABEL = {"pass": "✅ Pass", "fail": "❌ Fail", "pending": "⏳ Pending"}
st.dataframe(
    pd.DataFrame([{
        "Gate": g["label"],
        "Status": STATUS_LABEL[g["status"]],
        "Detail": g["detail"],
    } for g in gates]),
    hide_index=True,
    width='stretch',
)

st.divider()

# ── brainstorm section ────────────────────────────────────────────────────

# dreamer summary (built once, used in multiple sub-sections)
dreamer_groups = defaultdict(list)
for r in dreamers_raw:
    dreamer_groups[r["dreamer"]].append(r)

dreamer_summary = []
for name, records in dreamer_groups.items():
    recs = sorted(records, key=lambda x: x["date"])
    overall_scores = [r["overall"] for r in recs]
    avg_overall = round(mean(overall_scores), 2)
    diff = overall_scores[-1] - overall_scores[0] if len(overall_scores) >= 2 else 0
    trend = "↑" if diff > 0.2 else ("↓" if diff < -0.2 else "→")
    avg_dims = {d: round(mean(r["scores"][d] for r in recs if d in r["scores"]), 2) for d in DREAMER_DIMS}
    total_proposals = sum(r["proposals_count"] for r in recs)
    total_flagged = sum(r["flagged_count"] for r in recs)
    flag_rate = round(total_flagged / total_proposals * 100, 1) if total_proposals else 0
    dreamer_summary.append({
        "name": name,
        "display_name": DREAMER_ROLES.get(name, name),
        "short_name": name.replace("dreamer-", ""),
        "sessions": len(recs),
        "avg_overall": avg_overall,
        "trend": trend,
        "latest_version": recs[-1]["version"],
        "total_proposals": total_proposals,
        "total_flagged": total_flagged,
        "flag_rate": flag_rate,
        "avg_dims": avg_dims,
    })
dreamer_summary.sort(key=lambda x: x["avg_overall"], reverse=True)

left, right = st.columns(2)

with left:
    st.subheader("Brainstorm Sessions")
    horizon_totals = {"quick_win": 0, "growth_feature": 0, "moonshot": 0}
    for b in brainstorms:
        for h, count in b.get("proposals_by_horizon", {}).items():
            if h in horizon_totals:
                horizon_totals[h] += count

    if any(horizon_totals.values()):
        df_horizon = pd.DataFrame([
            {"Horizon": "Quick Wins", "Proposals": horizon_totals["quick_win"]},
            {"Horizon": "Growth Features", "Proposals": horizon_totals["growth_feature"]},
            {"Horizon": "Moonshots", "Proposals": horizon_totals["moonshot"]},
        ])
        fig = px.bar(df_horizon, x="Horizon", y="Proposals")
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No brainstorm data yet.")

with right:
    st.subheader("Brainstorm History")
    if brainstorms:
        df_brainstorms = pd.DataFrame([{
            "Idea": b["idea_name"],
            "Date": b["date"],
            "Rounds": b["rounds"],
            "Quick Wins": b.get("proposals_by_horizon", {}).get("quick_win", 0),
            "Growth": b.get("proposals_by_horizon", {}).get("growth_feature", 0),
            "Moonshots": b.get("proposals_by_horizon", {}).get("moonshot", 0),
            "Total": b["proposals_generated"],
            "Flagged": b.get("flagged_proposals", 0),
        } for b in reversed(sorted(brainstorms, key=lambda x: x["date"]))])
        st.dataframe(df_brainstorms, hide_index=True, width='stretch')
    else:
        st.info("No brainstorm data yet.")

st.divider()

# ── dreamer performance ───────────────────────────────────────────────────

left, right = st.columns(2)

with left:
    st.subheader("Dreamer Performance")
    if dreamer_summary:
        df_dreamer = pd.DataFrame([{
            "Dreamer": d["display_name"],
            "Sessions": d["sessions"],
            "Avg Score": f"{d['avg_overall']:.2f}/5",
            "Proposals": d["total_proposals"],
            "Flagged": d["total_flagged"],
            "Flag Rate": f"{d['flag_rate']:.0f}%",
            "Trend": d["trend"],
            "Version": d["latest_version"],
        } for d in dreamer_summary])
        st.dataframe(df_dreamer, hide_index=True, width='stretch')
    else:
        st.info("No dreamer data yet.")

with right:
    st.subheader("Dreamer Skill Radar")
    if dreamer_summary:
        fig = go.Figure()
        categories = [DREAMER_DIM_LABELS[d] for d in DREAMER_DIMS]
        for d in dreamer_summary:
            vals = [d["avg_dims"].get(dim, 0) * 20 for dim in DREAMER_DIMS]
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=categories + [categories[0]],
                name=d["display_name"],
                fill="toself",
                opacity=0.6,
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            margin=dict(t=30, b=80),
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No dreamer data yet.")

# ── proposals by dreamer ──────────────────────────────────────────────────

left, right = st.columns(2)

with left:
    st.subheader("Proposals by Dreamer")
    if dreamer_summary:
        dreamer_proposal_rows = []
        for d in dreamer_summary:
            dreamer_proposal_rows.append({
                "Dreamer": d["display_name"],
                "Proposals": d["total_proposals"],
                "Type": "Generated",
            })
            dreamer_proposal_rows.append({
                "Dreamer": d["display_name"],
                "Proposals": d["total_flagged"],
                "Type": "Flagged by Skeptic",
            })
        df_dp = pd.DataFrame(dreamer_proposal_rows)
        fig = px.bar(
            df_dp, x="Dreamer", y="Proposals", color="Type", barmode="overlay",
            color_discrete_map={"Generated": "#4C78A8", "Flagged by Skeptic": "#E45756"},
        )
        fig.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No dreamer data yet.")

with right:
    st.subheader("Dreamer Dimension Breakdown")
    if dreamer_summary:
        dim_rows = []
        for d in dreamer_summary:
            for dim in DREAMER_DIMS:
                dim_rows.append({
                    "Dreamer": d["display_name"],
                    "Dimension": DREAMER_DIM_LABELS[dim],
                    "Score": d["avg_dims"].get(dim, 0),
                })
        df_dims = pd.DataFrame(dim_rows)
        fig = px.bar(
            df_dims, x="Dimension", y="Score", color="Dreamer", barmode="group",
            range_y=[0, 5],
            labels={"Score": "Avg Score (1–5)"},
        )
        fig.update_layout(
            margin=dict(t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No dreamer data yet.")
