"""
ImpactTracker - MEL Dashboard
Interactive Streamlit dashboard for real-time indicator monitoring.
Author: Serge Nyamsin | MSc Data Science & AI, DSTI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.ingestion.kobo_connector import MockKoboConnector
from src.indicators.calculator import LogframeEngine
from src.alerts.threshold_monitor import ThresholdMonitor

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="ImpactTracker MEL Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Header ────────────────────────────────────────────────────
st.title("🎯 ImpactTracker — MEL Dashboard")
st.markdown("*Automated Monitoring, Evaluation & Learning System*")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    program = st.selectbox(
        "Program",
        ["Kosovo Education Support", "CAR Food Security", "Senegal WASH"]
    )
    period = st.selectbox(
        "Reporting Period",
        ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"]
    )
    st.button("🔄 Refresh Data", use_container_width=True)
    st.divider()
    st.info("Data Source: KoboToolbox API\nLast sync: 2025-03-04 09:00")

# ── Load Data ─────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    connector = MockKoboConnector()
    return connector.pull_data("mock_form_001")

@st.cache_data(ttl=300)
def get_indicator_results():
    data = load_data()
    engine = LogframeEngine("config/indicators_config.yaml")
    results = engine.calculate(data)
    return engine.to_dataframe(results), results

try:
    df_indicators, raw_results = get_indicator_results()
    df_data = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ── KPI Cards ─────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

on_track = len(df_indicators[df_indicators["Status"].str.contains("On Track")])
at_risk  = len(df_indicators[df_indicators["Status"].str.contains("At Risk")])
critical = len(df_indicators[df_indicators["Status"].str.contains("Critical")])

col1.metric("👥 Beneficiaries Reached", f"{len(df_data):,}", "+12% vs last period")
col2.metric("✅ Indicators On Track",   on_track, f"{on_track}/{len(df_indicators)}")
col3.metric("⚠️ Indicators At Risk",    at_risk)
col4.metric("🔴 Critical Indicators",   critical)

st.divider()

# ── Indicator Progress Bar Chart ──────────────────────────────
st.subheader("📊 Indicator Achievement vs Targets")

fig = go.Figure()
fig.add_trace(go.Bar(
    name="Achievement Rate (%)",
    x=df_indicators["Code"],
    y=df_indicators["Achievement Rate (%)"],
    marker_color=df_indicators["Achievement Rate (%)"].apply(
        lambda x: "#2ecc71" if x >= 85 else "#f39c12" if x >= 60 else "#e74c3c"
    ),
    text=df_indicators["Achievement Rate (%)"].apply(lambda x: f"{x}%"),
    textposition="outside"
))
fig.add_hline(
    y=85, line_dash="dash", line_color="orange",
    annotation_text="On Track (85%)"
)
fig.add_hline(
    y=60, line_dash="dash", line_color="red",
    annotation_text="Critical (60%)"
)
fig.update_layout(height=400, showlegend=False, yaxis_range=[0, 130])
st.plotly_chart(fig, use_container_width=True)

# ── Indicator Table ───────────────────────────────────────────
st.subheader("📋 Logframe Indicator Tracker")
st.dataframe(
    df_indicators.style.map(
        lambda v: "background-color: #d5f5e3" if "On Track" in str(v)
        else "background-color: #fdebd0" if "At Risk" in str(v)
        else "background-color: #fadbd8" if "Critical" in str(v) else "",
        subset=["Status"]
    ),
    use_container_width=True,
    hide_index=True
)

st.divider()

# ── Disaggregation Charts ─────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("👥 Beneficiaries by Gender")
    gender_counts = df_data["gender"].value_counts().reset_index()
    fig_gender = px.pie(
        gender_counts, values="count", names="gender",
        color_discrete_map={"Female": "#9b59b6", "Male": "#3498db"}
    )
    st.plotly_chart(fig_gender, use_container_width=True)

with col_right:
    st.subheader("📍 Coverage by Location")
    loc_counts = df_data["location"].value_counts().reset_index()
    fig_loc = px.bar(
        loc_counts, x="location", y="count",
        color="count", color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_loc, use_container_width=True)

st.divider()

# ── Alerts Panel ──────────────────────────────────────────────
st.subheader("🔔 Active Alerts")
monitor = ThresholdMonitor("config/thresholds.yaml")
alerts = monitor.check_indicators(raw_results)

if alerts:
    for alert in alerts:
        if alert.severity == "critical":
            st.error(alert.message)
        else:
            st.warning(alert.message)
else:
    st.success("✅ All indicators performing on track — No alerts.")

st.divider()
st.caption(
    "ImpactTracker v1.0 | Built by Tresor | "
    "MSc Data Science & AI, DSTI | Innovation Center Kosovo"
)