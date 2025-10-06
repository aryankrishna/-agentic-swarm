import streamlit as st
import pandas as pd
import json
from pathlib import Path
import altair as alt  # optional; safe to keep

st.set_page_config(page_title="Router Dashboard", page_icon="📊")

st.title("📊 Router Performance Dashboard")

log_path = Path("data/logs/route_log.csv")
model_path = Path("data/models/router_bandit.json")

# --- Load data ---
if not log_path.exists():
    st.warning("No route log file found yet! Run some queries in Auto mode first.")
else:
    df = pd.read_csv(log_path)

    st.subheader("Log Overview")

    # Decision filter (graph/vector/math)
    dec = st.multiselect(
        "Filter decisions",
        ["graph", "vector", "math"],
        default=["graph", "vector", "math"]
    )
    df_show = df[df["decision"].isin(dec)]

    # Show filtered data (last 10 rows)
    st.dataframe(df_show.tail(10), use_container_width=True)

    # Download filtered CSV
    st.download_button(
        "⬇️ Download logs CSV",
        df_show.to_csv(index=False),
        "route_log.csv",
        "text/csv"
    )

    # Quick KPIs
    st.metric("Total Queries", len(df_show))
    st.metric("Unique Decisions", df_show["decision"].nunique())

    # Charts (computed from the filtered view)
    st.subheader("Decisions Breakdown")
    st.bar_chart(df_show["decision"].value_counts())

    st.subheader("Average Latency (ms) by Decision")
    avg_latency = df_show.groupby("decision")["latency_ms"].mean().sort_values()
    st.bar_chart(avg_latency)

    st.subheader("Success Rate by Decision")
    success = df_show.groupby("decision")["had_answer"].mean().round(2)
    st.bar_chart(success)

# --- Bandit Model ---
if not model_path.exists():
    st.warning("No router_bandit.json found! Run a few queries in Auto mode.")
else:
    st.subheader("Bandit Learning State")
    with open(model_path) as f:
        data = json.load(f)

    counts = data.get("counts", {})
    values = data.get("values", {})

    col1, col2 = st.columns(2)
    with col1:
        st.write("Counts (how many times each tool was used):")
        st.json(counts)
    with col2:
        st.write("Values (estimated success rate per tool):")
        st.json(values)

    st.caption(f"Exploration rate (epsilon): {data.get('epsilon', 0.0)}")