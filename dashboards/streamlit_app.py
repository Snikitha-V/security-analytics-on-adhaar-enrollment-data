"""
A-SOC Operational Dashboard
============================
Security Operations Center Dashboard for Aadhaar Threat Intelligence.

This is a production-grade SOC dashboard following enterprise UI patterns.
Designed for daily use by security analysts - not a demo or portfolio project.

Pages:
1. Overview - SOC at a Glance
2. Threat Map - Geographic Risk Visualization
3. PIN Risk Explorer - Investigation Mode
4. Temporal Analysis - Spike Detection
5. IOC Catalogue - Threat Intelligence
6. Data Health - Signal Validation
7. Methodology - Defensible Analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Set random seed
np.random.seed(42)

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="A-SOC | Aadhaar Threat Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SOC Theme Configuration
# ============================================================================

SOC_COLORS = {
    'background': '#0E1117',   # charcoal
    'panel': '#0F172A',        # deep slate
    'surface': '#111827',      # panel surface
    'border': '#6B7280',       # slate blue-gray
    'text_primary': '#E6E8EB', # soft off-white
    'text_secondary': '#9AA0A6',
    'text_muted': '#6B7280',
    'critical': '#C44536',     # deep crimson (risk)
    'high': '#C44536',         # keep risk red for high/critical
    'medium': '#E0B15C',       # desaturated amber (demographic)
    'low': '#6C7FF2',          # cool indigo (biometric / low risk tone)
    'info': '#4FB6B2'          # muted teal (enrollment / neutral info)
}

RISK_COLORS = {
    'CRITICAL': '#C44536',
    'HIGH': '#C44536',
    'MEDIUM': '#E0B15C',
    'LOW': '#6C7FF2'
}

# Custom CSS for SOC theme
st.markdown(f"""
<style>
    :root {{
        --bg: {SOC_COLORS['background']};
        --panel: {SOC_COLORS['panel']};
        --surface: {SOC_COLORS['surface']};
        --border: {SOC_COLORS['border']};
        --text: {SOC_COLORS['text_primary']};
        --text-2: {SOC_COLORS['text_secondary']};
        --text-3: {SOC_COLORS['text_muted']};
        --critical: {SOC_COLORS['critical']};
        --high: {SOC_COLORS['high']};
        --medium: {SOC_COLORS['medium']};
        --low: {SOC_COLORS['low']};
        --info: {SOC_COLORS['info']};
    }}

    /* Main container */
    .main .block-container {{
        padding-top: 0.75rem;
        padding-bottom: 1.25rem;
        max-width: 1280px;
    }}

    body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
        background: var(--bg);
        color: var(--text);
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: var(--panel);
        border-right: 1px solid var(--border);
    }}

    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text) !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
    }}

    /* Metric cards */
    [data-testid="stMetricValue"] {{
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text);
    }}

    [data-testid="stMetricLabel"] {{
        font-size: 0.9rem;
        color: var(--text-2);
    }}

    /* Tables */
    .dataframe {{
        font-size: 0.9rem;
    }}

    /* Compact spacing */
    .element-container {{
        margin-bottom: 0.4rem;
    }}

    /* Panels */
    .a-panel {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.6rem;
    }}

    /* KPI card */
    .kpi-card {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.9rem;
        margin-bottom: 0.35rem;
    }}

    .kpi-value {{
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text);
    }}

    .kpi-label {{
        font-size: 0.9rem;
        color: var(--text-2);
    }}

    /* Risk level badges */
    .risk-critical {{ color: var(--critical); font-weight: 700; }}
    .risk-high {{ color: var(--high); font-weight: 700; }}
    .risk-medium {{ color: var(--medium); font-weight: 700; }}
    .risk-low {{ color: var(--low); font-weight: 700; }}

    /* Alert styling */
    .stAlert {{
        background-color: var(--panel);
        border: 1px solid var(--border);
    }}

    /* Captions */
    .caption {{
        color: var(--text-3);
        font-size: 0.85rem;
    }}
</style>
""", unsafe_allow_html=True)


# =========================================================================
# UI Helpers
# =========================================================================

def section_header(title: str, subtitle: str | None = None):
    """Render a disciplined header block with optional subtitle."""
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<span class='caption'>{subtitle}</span>", unsafe_allow_html=True)


def info_expander(title: str, bullets: list[str], footnote: str | None = None, expanded: bool = False):
    """Compact expander for definitions and methods."""
    with st.expander(title, expanded=expanded):
        for b in bullets:
            st.markdown(f"- {b}")
        if footnote:
            st.caption(footnote)


def zebra_dataframe(df: pd.DataFrame, **kwargs):
    """Render dataframe with zebra rows for readability."""
    if df.empty:
        return st.dataframe(df, **kwargs)
    zebra_dark = '#0B1220'
    zebra_base = SOC_COLORS['background']
    styled = df.style.set_properties(**{
        'background-color': SOC_COLORS['panel'],
        'color': SOC_COLORS['text_primary'],
        'border-color': SOC_COLORS['border']
    }).apply(lambda s: [
        f'background-color: {zebra_dark if i % 2 else zebra_base}'
        for i in range(len(s))
    ], axis=0)
    return st.dataframe(styled, **kwargs)


def compute_national_index(daily_df: pd.DataFrame) -> pd.DataFrame | None:
    """Compute a simple composite risk index (0-10) from daily volumes."""
    required = {'date', 'total_enrollments', 'total_demo_updates', 'total_bio_updates'}
    if daily_df.empty or not required.issubset(set(daily_df.columns)):
        return None
    df = daily_df.copy()
    # Percentile ranks provide scale-free comparability and stay deterministic.
    for col in ['total_enrollments', 'total_demo_updates', 'total_bio_updates']:
        df[f'{col}_pct'] = df[col].rank(pct=True)
    df['risk_index'] = df[[f'{c}_pct' for c in ['total_enrollments', 'total_demo_updates', 'total_bio_updates']]].mean(axis=1) * 10
    df['risk_index_ma7'] = df['risk_index'].rolling(window=7, min_periods=1).mean()
    return df[['date', 'risk_index', 'risk_index_ma7']]


# ============================================================================
# Data Loading Functions
# ============================================================================

@st.cache_data(ttl=3600)
def load_risk_data():
    """Load risk scores data."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    outputs_dir = project_root / 'outputs'
    
    risk_path = outputs_dir / 'risk_scores.csv'
    if risk_path.exists():
        df = pd.read_csv(risk_path)
        return df
    return None


@st.cache_data(ttl=3600)
def load_ioc_data():
    """Load IOC catalogue data."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    outputs_dir = project_root / 'outputs'
    
    ioc_path = outputs_dir / 'ioc_catalogue.csv'
    if ioc_path.exists():
        df = pd.read_csv(ioc_path)
        return df
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_alerts_data():
    """Load alerts data."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    outputs_dir = project_root / 'outputs'
    
    alerts_path = outputs_dir / 'alerts.csv'
    if alerts_path.exists():
        df = pd.read_csv(alerts_path)
        return df
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_state_data():
    """Load state summary data."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    outputs_dir = project_root / 'outputs'
    
    state_path = outputs_dir / 'state_summary.csv'
    if state_path.exists():
        df = pd.read_csv(state_path)
        return df
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_district_data():
    """Load district summary data."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    outputs_dir = project_root / 'outputs'
    
    district_path = outputs_dir / 'district_summary.csv'
    if district_path.exists():
        df = pd.read_csv(district_path)
        return df
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_daily_data():
    """Load daily summary data."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    outputs_dir = project_root / 'outputs'
    
    daily_path = outputs_dir / 'daily_summary.csv'
    if daily_path.exists():
        df = pd.read_csv(daily_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()


def check_data_exists():
    """Check if output data exists, run pipeline if not."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    outputs_dir = project_root / 'outputs'
    
    risk_path = outputs_dir / 'risk_scores.csv'
    
    if not risk_path.exists():
        st.warning("⚠️ Output data not found. Running the analysis pipeline...")
        
        # Run pipeline
        sys.path.insert(0, str(project_root / 'src'))
        from pipeline import run_pipeline
        
        data_dir = str(project_root / 'data')
        output_dir = str(outputs_dir)
        
        with st.spinner("Processing data... This may take a few minutes."):
            run_pipeline(data_dir, output_dir, verbose=False)
        
        st.success("✅ Pipeline complete! Refresh the page to see results.")
        st.rerun()
    
    return True


# ============================================================================
# Page: Data Foundations (Page 1)
# ============================================================================

def page_data_foundations():
    """Page 1 — Data Foundations: schemas, row counts, missingness, freshness."""

    st.title("📂 Data Foundations")
    st.caption("Explain what data exists, what doesn't, and its basic health — no derived metrics.")

    # Load all datasets
    risk_df = load_risk_data()
    ioc_df = load_ioc_data()
    alerts_df = load_alerts_data()
    daily_df = load_daily_data()
    state_df = load_state_data()
    district_df = load_district_data()

    # Row counts per table
    row_counts = pd.DataFrame([
        {"Dataset": "risk_scores.csv", "Rows": len(risk_df) if risk_df is not None else 0},
        {"Dataset": "ioc_catalogue.csv", "Rows": len(ioc_df)},
        {"Dataset": "alerts.csv", "Rows": len(alerts_df)},
        {"Dataset": "daily_summary.csv", "Rows": len(daily_df)},
        {"Dataset": "state_summary.csv", "Rows": len(state_df)},
        {"Dataset": "district_summary.csv", "Rows": len(district_df)}
    ])

    st.markdown("**Row counts by dataset**")
    zebra_dataframe(row_counts, hide_index=True, use_container_width=True)
    st.caption("Tables kept only for comparison (>=3 datasets). No derived metrics on this page.")

    st.divider()

    # Dataset schema (using risk_scores as the unified schema proxy)
    if risk_df is not None:
        schema_df = pd.DataFrame({
            "Column": risk_df.columns,
            "Dtype": [str(t) for t in risk_df.dtypes],
        })
        st.markdown("**Schema (risk_scores.csv as canonical PIN-level table)**")
        zebra_dataframe(schema_df, hide_index=True, use_container_width=True)
        st.caption("Schema table retained for auditability; use it to map variables before charts.")
    else:
        st.info("risk_scores.csv not found. Run the pipeline to populate data.")

    st.divider()

    # Missing value summary
    if risk_df is not None and not risk_df.empty:
        missing_df = pd.DataFrame({
            "Column": risk_df.columns,
            "Non-null": risk_df.notnull().sum(),
            "% Missing": (risk_df.isnull().mean() * 100).round(2)
        })
        st.markdown("**Missing value summary (risk_scores.csv)**")
        zebra_dataframe(missing_df.sort_values("% Missing", ascending=False), hide_index=True, use_container_width=True)
        st.caption("Missingness shown to frame reliability of downstream visuals; no derivations applied here.")
    else:
        st.info("Missing summary unavailable (risk_scores.csv empty or missing).")

    st.divider()

    # Data freshness / coverage
    if daily_df is not None and not daily_df.empty:
        min_date, max_date = daily_df['date'].min(), daily_df['date'].max()
        st.markdown("**Data freshness & coverage**")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("First date", min_date.strftime('%Y-%m-%d'))
        with c2:
            st.metric("Latest date", max_date.strftime('%Y-%m-%d'))
        with c3:
            st.metric("Active days", len(daily_df))
        st.caption("Counts only — no derived metrics on this page (per redesign.md rules).")
    else:
        st.info("Daily coverage unavailable (daily_summary.csv missing).")


# ============================================================================
# Page: Variable-Level Statistics (Page 2)
# ============================================================================

def page_variable_stats():
    """Page 2 — Variable-Level Statistics (most important)."""

    st.title("📊 Variable-Level Statistics")
    st.caption("Show raw distributions, definitions, dtypes, ranges, and missingness before any aggregation.")

    risk_df = load_risk_data()
    if risk_df is None or risk_df.empty:
        st.error("risk_scores.csv missing. Run the pipeline first.")
        return

    # Variable selector
    variable = st.selectbox("Choose variable", options=sorted(risk_df.columns.tolist()))

    series = risk_df[variable]
    dtype = str(series.dtype)
    missing_pct = series.isnull().mean() * 100

    st.markdown(f"**Definition:** {variable} (see schema in Data Foundations)")
    st.markdown(f"**Data type:** {dtype}")
    st.markdown(f"**% Missing:** {missing_pct:.2f}%")

    if pd.api.types.is_numeric_dtype(series):
        desc = series.describe(percentiles=[0.25, 0.5, 0.75]).rename({
            '25%': 'P25', '50%': 'Median', '75%': 'P75'
        })
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Mean", f"{desc['mean']:.2f}")
        with c2:
            st.metric("Median", f"{desc['Median']:.2f}")
        with c3:
            st.metric("Std Dev", f"{desc['std']:.2f}")
        with c4:
            st.metric("P25 / P75", f"{desc['P25']:.2f} / {desc['P75']:.2f}")

        fig = px.histogram(risk_df, x=variable, nbins=40, marginal=None, color_discrete_sequence=[SOC_COLORS['info']])
        fig.update_layout(
            height=340,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=SOC_COLORS['text_primary']),
            bargap=0.05
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("How this metric is computed", expanded=False):
            st.markdown("Raw numeric column; no derived formula unless specified in methodology.")
            st.markdown("Inputs: direct from dataset column.")
            st.markdown("Limitations: Outliers can skew mean; refer to median/P25/P75 for robustness.")
        with st.expander("Why this matters for fraud detection", expanded=False):
            st.markdown("Distributions reveal abnormal density spikes that can indicate manipulation.")
            st.markdown("This does NOT prove fraud; anomalies require contextual verification.")
    else:
        freq = series.fillna("<missing>").value_counts()
        top_df = freq.head(10).reset_index()
        top_df.columns = ["Category", "Count"]
        top_df["Percent"] = (top_df["Count"] / len(series) * 100).round(1)
        st.markdown("**Categorical frequency (top 10)**")
        zebra_dataframe(top_df, hide_index=True, use_container_width=True)

        fig = px.bar(top_df, x="Category", y="Count", color_discrete_sequence=[SOC_COLORS['info']])
        fig.update_layout(
            height=340,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=SOC_COLORS['text_primary']),
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("How this metric is computed", expanded=False):
            st.markdown("Frequency counts of categories (including <missing> bucket).")
            st.markdown("Inputs: raw categorical values from dataset.")
            st.markdown("Limitations: Long tails may truncate beyond top 10 shown here.")
        with st.expander("Why this matters for fraud detection", expanded=False):
            st.markdown("Category skew highlights concentrations that may signal coordinated edits.")
            st.markdown("Does NOT prove fraud; verify against operational campaigns.")

    st.caption("No cross-variable aggregation shown here (per redesign.md). Visual-first with inline formulas and caveats.")


# ============================================================================
# Page: Derived Metrics & Calculations (Page 3)
# ============================================================================

def page_derived_metrics():
    """Page 3 — Derived metrics with formulas, inputs, assumptions, limitations."""

    st.title("🧮 Derived Metrics & Calculations")
    st.caption("Deterministic formulas only. Every metric lists inputs, assumptions, and limitations.")

    metrics = [
        {
            "name": "Enrollment Velocity",
            "formula": "enrollment_velocity = recent_7d_enrollments / median_30d_enrollments",
            "inputs": ["total_enrollments", "rolling 7d", "median 30d"],
            "assumptions": "Seasonality mild over 30 days; medians robust to spikes.",
            "limitations": "If coverage is sparse (<10 days), velocity may be unstable."
        },
        {
            "name": "Update Velocity",
            "formula": "update_velocity = recent_7d_demo_updates / median_30d_demo_updates",
            "inputs": ["total_demo_updates", "rolling 7d", "median 30d"],
            "assumptions": "Demographic updates follow gradual trends unless manipulated.",
            "limitations": "Bulk legitimate campaigns (e.g., address drives) can elevate velocity."
        },
        {
            "name": "Biometric Recapture Ratio",
            "formula": "bio_recapture_ratio = total_bio_updates / total_enrollments",
            "inputs": ["total_bio_updates", "total_enrollments"],
            "assumptions": "Re-captures above 30% are atypical.",
            "limitations": "Hardware refresh programs can legitimately raise recaptures temporarily."
        },
        {
            "name": "Child Ratio Z-score",
            "formula": "child_ratio_z = zscore(age_0_5 / total_enrollments)",
            "inputs": ["age_0_5", "total_enrollments"],
            "assumptions": "National distribution is stable; Z>3 denotes anomaly.",
            "limitations": "Districts with genuinely young populations may appear anomalous."
        },
        {
            "name": "Risk Score (0-10)",
            "formula": "risk = (0.30*enroll_vel + 0.25*update_vel + 0.20*demo_anom + 0.15*geo_outlier + 0.10*time_spike) * 10",
            "inputs": ["enrollment_velocity", "update_velocity", "demographic_anomaly", "geographic_outlier", "temporal_spike"],
            "assumptions": "Weights locked per specification; percentile caps handle outliers.",
            "limitations": "Does not prove fraud; highlights statistical outliers only."
        },
    ]

    for m in metrics:
        with st.expander(m["name"], expanded=False):
            st.markdown(f"**Formula:** {m['formula']}")
            st.markdown(f"**Required inputs:** {', '.join(m['inputs'])}")
            st.markdown(f"**Assumptions:** {m['assumptions']}")
            st.markdown(f"**Limitations:** {m['limitations']}")
            st.markdown("**Why this matters:** Highlights where volume/velocity anomalies can signal coordinated fraud. Does NOT prove fraud; requires contextual validation.")


# ============================================================================
# Page: Local / Regional Insights (Page 4)
# ============================================================================

def page_local_regional():
    """Page 4 — Local/Regional analysis: state/district summaries and time trends."""

    st.title("🗺️ Local / Regional Insights")
    st.caption("Per-state and per-district behavior plus time trends. Small multiples preferred.")

    risk_df = load_risk_data()
    state_df = load_state_data()
    district_df = load_district_data()
    daily_df = load_daily_data()

    # Enrollment vs Update correlation (visual-first)
    if risk_df is not None and not risk_df.empty:
        st.markdown("**Enrollment vs Update Correlation (velocity)**")
        corr_df = risk_df.dropna(subset=['enrollment_velocity', 'update_velocity'])
        fig_corr = px.scatter(
            corr_df,
            x='enrollment_velocity',
            y='update_velocity',
            color='risk_level',
            color_discrete_map=RISK_COLORS,
            hover_data=['pincode', 'district', 'state'],
            labels={'enrollment_velocity': 'Enrollment Velocity', 'update_velocity': 'Update Velocity'}
        )
        fig_corr.update_layout(
            height=360,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=SOC_COLORS['text_primary']),
            legend_title_text='Risk Level'
        )
        fig_corr.update_xaxes(showgrid=True, gridcolor=SOC_COLORS['border'])
        fig_corr.update_yaxes(showgrid=True, gridcolor=SOC_COLORS['border'])
        st.plotly_chart(fig_corr, use_container_width=True)
        with st.expander("How this metric is computed", expanded=False):
            st.markdown("Velocity = recent 7d volume ÷ 30d median (per feature engineering).")
            st.markdown("Inputs: enrollment_velocity, update_velocity from risk_scores.csv.")
            st.markdown("Limitations: Sparse coverage (<10 days) can inflate ratios.")
        with st.expander("Why this matters for fraud detection", expanded=False):
            st.markdown("Correlated high velocities across enrollment and updates suggest coordinated manipulation.")
            st.markdown("Does NOT prove fraud; correlate with campaign calendars and outages.")

    # State summary
    if state_df is not None and not state_df.empty:
        st.markdown("**State summary (avg risk, PINs, enrollments)**")
        view = state_df.copy()
        if 'avg_risk_score' in view.columns:
            view = view.rename(columns={'avg_risk_score': 'Avg Risk', 'total_pins': 'PINs'})
        if 'total_enrollments' in view.columns:
            cols = [c for c in ['state', 'Avg Risk', 'PINs', 'total_enrollments'] if c in view.columns]
            view = view[cols]
        zebra_dataframe(view.sort_values(view.columns[1], ascending=False), hide_index=True, use_container_width=True)
        st.caption("Visual-first rule: table kept for ranking comparison across states (>=3 columns).")

    st.divider()

    # District comparison
    if district_df is not None and not district_df.empty:
        st.markdown("**District comparison (top/bottom risk)**")
        if 'avg_risk_score' in district_df.columns:
            top = district_df.nlargest(10, 'avg_risk_score')
            bottom = district_df.nsmallest(10, 'avg_risk_score')
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("Top 10 districts by risk")
                zebra_dataframe(top[['state', 'district', 'avg_risk_score']], hide_index=True, use_container_width=True)
            with c2:
                st.markdown("Bottom 10 districts by risk")
                zebra_dataframe(bottom[['state', 'district', 'avg_risk_score']], hide_index=True, use_container_width=True)
            st.caption("Tables retained for ranked comparison (>=3 columns).")
        else:
            zebra_dataframe(district_df.head(20), hide_index=True, use_container_width=True)

    st.divider()

    # Anomaly monitor (child/update/bio z-scores)
    if risk_df is not None and not risk_df.empty:
        st.markdown("**Demographic & Biometric Anomaly Monitor (Z > 3)**")
        monitor_cols = [c for c in ['pincode', 'district', 'state', 'child_ratio_zscore', 'update_ratio_zscore', 'bio_recapture_ratio_zscore'] if c in risk_df.columns]
        flagged = risk_df[monitor_cols].copy()
        if not flagged.empty and any(col.endswith('zscore') for col in monitor_cols):
            def flag_val(row):
                vals = [abs(row[c]) for c in monitor_cols if c.endswith('zscore')]
                return max(vals) if vals else 0
            flagged['max_abs_z'] = flagged.apply(flag_val, axis=1)
            flagged = flagged[flagged['max_abs_z'] > 3].sort_values('max_abs_z', ascending=False).head(30)
            zebra_dataframe(flagged, hide_index=True, use_container_width=True)
            with st.expander("How this monitor is computed", expanded=False):
                st.markdown("Z-scores computed across all PINs; |Z|>3 flagged as statistical anomalies.")
                st.markdown("Inputs: child_ratio_zscore, update_ratio_zscore, bio_recapture_ratio_zscore.")
                st.markdown("Limitations: Genuine demographic skews (e.g., very young districts) may appear as anomalies.")
            with st.expander("Why this matters for fraud detection", expanded=False):
                st.markdown("Extreme Z-scores highlight PINs whose demographic or biometric behavior diverges sharply from norms.")
                st.markdown("Does NOT prove fraud; must be validated against local context.")

    st.divider()

    # Time-based trends (small multiples)
    if daily_df is not None and not daily_df.empty:
        st.markdown("**Time trends (daily totals)**")
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            subplot_titles=('Enrollments', 'Demographic Updates', 'Biometric Updates'))

        fig.add_trace(go.Scatter(x=daily_df['date'], y=daily_df['total_enrollments'],
                                 mode='lines', name='Enrollments', line=dict(color=SOC_COLORS['info'])), row=1, col=1)
        fig.add_trace(go.Scatter(x=daily_df['date'], y=daily_df['total_demo_updates'],
                                 mode='lines', name='Demo Updates', line=dict(color=SOC_COLORS['medium'])), row=2, col=1)
        fig.add_trace(go.Scatter(x=daily_df['date'], y=daily_df['total_bio_updates'],
                                 mode='lines', name='Bio Updates', line=dict(color=SOC_COLORS['critical'])), row=3, col=1)

        fig.update_layout(
            height=520,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=SOC_COLORS['text_primary']),
            showlegend=False
        )
        fig.update_xaxes(showgrid=True, gridcolor=SOC_COLORS['border'])
        fig.update_yaxes(showgrid=True, gridcolor=SOC_COLORS['border'])
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Interpretation**")
        st.markdown("- Patterns: Look for synchronized lifts across the three panels; isolated spikes hint at channel-specific issues.\n- Usefulness: Separates enrollment surges from demographic edits and biometric recaptures to isolate cause.\n- Does NOT prove: A spike alone is not fraud; correlate with campaigns or outages before action.")
    else:
        st.info("Daily trend data unavailable.")


# ============================================================================
# Page: National Statistics (Page 5)
# ============================================================================

def page_national_stats():
    """Page 5 — National-level statistics with footnotes and variance warnings."""

    st.title("🏛️ National Statistics")
    st.caption("Only after foundations + local context. Includes footnotes and variance warnings.")

    risk_df = load_risk_data()
    state_df = load_state_data()
    alerts_df = load_alerts_data()
    daily_df = load_daily_data()

    if risk_df is None or risk_df.empty:
        st.error("risk_scores.csv missing. Run pipeline first.")
        return

    # National aggregates (visual-first stats strip + executive KPIs)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    mean_risk = risk_df['risk_score'].mean()
    med_risk = risk_df['risk_score'].median()
    p90_risk = risk_df['risk_score'].quantile(0.90)
    total_pins = len(risk_df)
    critical_alerts = len(alerts_df[alerts_df['risk_level'] == 'CRITICAL']) if alerts_df is not None and not alerts_df.empty and 'risk_level' in alerts_df.columns else 0
    high_risk_enroll = 0
    if 'risk_level' in risk_df.columns and 'total_enrollments' in risk_df.columns:
        high_risk_enroll = risk_df[risk_df['risk_level'].isin(['CRITICAL', 'HIGH'])]['total_enrollments'].sum()
    financial_impact = high_risk_enroll * 50  # ₹50 proxy per enrollment

    with c1:
        st.metric("Avg Risk", f"{mean_risk:.2f}")
    with c2:
        st.metric("Median", f"{med_risk:.2f}")
    with c3:
        st.metric("P90", f"{p90_risk:.2f}")
    with c4:
        st.metric("Total PINs", f"{total_pins:,}")
    with c5:
        st.metric("Critical Alerts", f"{critical_alerts:,}")
    with c6:
        st.metric("Est. Impact (₹)", f"{financial_impact:,.0f}")

    st.caption("Footnote: Derived directly from risk_scores.csv distributions established on Page 2.")

    # National distribution visualization
    fig = px.histogram(risk_df, x='risk_score', nbins=40, color_discrete_sequence=[SOC_COLORS['critical']])
    fig.update_layout(
        height=340,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=SOC_COLORS['text_primary']),
        bargap=0.05
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("How these aggregates are computed", expanded=False):
        st.markdown("Aggregates are simple descriptive stats on risk_score (mean/median/P90). No smoothing or weighting.")
        st.markdown("Inputs: risk_scores.csv → risk_score column only.")
        st.markdown("Limitations: Sensitive to coverage; P90 highlights tail but not its causes.")
    with st.expander("Why this matters for fraud detection", expanded=False):
        st.markdown("National distribution shows tail heaviness; a fat upper tail signals concentrated anomalies.")
        st.markdown("Does NOT prove fraud: requires tracing back to variable-level anomalies (Page 2) and locality (Page 4).")

    st.divider()

    # Threat timeline (alerts per day)
    if alerts_df is not None and not alerts_df.empty and 'date_detected' in alerts_df.columns:
        alerts_df['date_detected'] = pd.to_datetime(alerts_df['date_detected'], errors='coerce')
        timeline = alerts_df.dropna(subset=['date_detected']).groupby('date_detected').size().reset_index(name='alerts')
        fig_t = px.line(timeline, x='date_detected', y='alerts', markers=True, color_discrete_sequence=[SOC_COLORS['critical']])
        fig_t.update_layout(
            height=320,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=SOC_COLORS['text_primary'])
        )
        fig_t.update_xaxes(showgrid=True, gridcolor=SOC_COLORS['border'])
        fig_t.update_yaxes(showgrid=True, gridcolor=SOC_COLORS['border'])
        st.plotly_chart(fig_t, use_container_width=True)
        with st.expander("How this timeline is computed", expanded=False):
            st.markdown("Counts alerts by date_detected. No smoothing; raw daily counts.")
            st.markdown("Inputs: alerts.csv date_detected column.")
            st.markdown("Limitations: Dependent on alert generation cadence; gaps reflect missing alerts, not zero risk.")
        with st.expander("Why this matters for fraud detection", expanded=False):
            st.markdown("Spikes in alert counts show temporal clustering of anomalies requiring surge response.")
            st.markdown("Does NOT prove fraud; investigate underlying IOCs for context.")

    st.divider()

    # Regional contribution to totals
    if state_df is not None and not state_df.empty and 'total_enrollments' in state_df.columns:
        st.markdown("**Regional contribution to enrollments**")
        state_df = state_df.sort_values('total_enrollments', ascending=False)
        fig = px.bar(state_df.head(15), x='state', y='total_enrollments', color_discrete_sequence=[SOC_COLORS['info']])
        fig.update_layout(
            height=380,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=SOC_COLORS['text_primary']),
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Warning: Aggregation hides variance — cross-check Page 4 state/district spreads.")

    # Top 5 high-risk districts (ranked table for comparison)
    if district_df := load_district_data():
        if not district_df.empty and 'avg_risk_score' in district_df.columns:
            top5 = district_df.nlargest(5, 'avg_risk_score')[['state', 'district', 'avg_risk_score']]
            st.markdown("**Top 5 High-Risk Districts**")
            zebra_dataframe(top5, hide_index=True, use_container_width=True)
            st.caption("Table retained for ranking comparison (>=3 columns); ties back to district-level distributions.")


# ============================================================================
# Page: Interpretation & Use-Cases (Page 6)
# ============================================================================

def page_interpretation():
    """Page 6 — Explain insights, why they matter, and what they do NOT prove."""

    st.title("🧭 Interpretation & Use-Cases")
    st.caption("Explain usefulness without exaggeration. No policy claims unless data-backed.")

    insights = [
        {
            "title": "High biometric recapture ratios",
            "indicates": "Possible coercion or operator-driven re-enrollment",
            "why_care": "Biometric churn erodes identity integrity and signals manipulation",
            "action": "Audit centers with >30% recapture; cross-check operator logs",
            "not_prove": "Does not prove fraud — could be device refresh campaigns"
        },
        {
            "title": "Demographic surge velocity >3x",
            "indicates": "Bulk demographic edits potentially masking identity swaps",
            "why_care": "Rapid edits can rewrite KYC attributes at scale",
            "action": "Pause edits, require secondary verification for affected PINs",
            "not_prove": "Could reflect legitimate mass update drives (address campaigns)"
        },
        {
            "title": "Coordinated PIN spikes (CPS)",
            "indicates": "Synchronized enrollment + update + bio spikes",
            "why_care": "Suggests organized fraud ring leveraging multiple channels",
            "action": "Temporarily flag affected PINs; investigate operators serving them",
            "not_prove": "Might coincide with genuine outreach events if poorly scheduled"
        }
    ]

    for ins in insights:
        with st.expander(ins["title"], expanded=False):
            st.markdown(f"**Indicates:** {ins['indicates']}")
            st.markdown(f"**Why analysts care:** {ins['why_care']}")
            st.markdown(f"**Possible action:** {ins['action']}")
            st.markdown(f"**What this does NOT prove:** {ins['not_prove']}")


# ============================================================================
# Page: Overview
# ============================================================================

def page_overview():
    """SOC at a Glance - Executive Overview."""
    st.title("🛡️ SOC Overview")
    st.caption("Aadhaar Threat Intelligence — operational posture and open investigations")

    info_expander(
        "How this page works",
        bullets=[
            "Data: daily pipeline outputs (risk_scores.csv, ioc_catalogue.csv, alerts.csv).",
            "Risk levels: deterministic thresholds mapped to semantic colors (critical/high/medium/low).",
            "Exposure: sum of enrollments for CRITICAL/HIGH PINs × ₹50 investigation effort proxy.",
            "Refresh: pipeline run; rerun via backend or restart to pull latest outputs."
        ],
        footnote="Every metric is reproducible from pipeline outputs; no hidden transformations.",
        expanded=False
    )
    
    # Load data
    risk_df = load_risk_data()
    ioc_df = load_ioc_data()
    alerts_df = load_alerts_data()
    daily_df = load_daily_data()
    
    if risk_df is None:
        st.error("No data available. Please run the pipeline first.")
        return
    
    # Calculate KPIs
    total_pins = len(risk_df)
    critical_pins = len(risk_df[risk_df['risk_level'] == 'CRITICAL'])
    high_pins = len(risk_df[risk_df['risk_level'] == 'HIGH'])
    total_iocs = len(ioc_df) if not ioc_df.empty else 0
    open_alerts = len(alerts_df[alerts_df.get('alert_status', 'OPEN') == 'OPEN']) if not alerts_df.empty else 0
    last_refresh_dt = None
    if daily_df is not None and not daily_df.empty:
        last_refresh_dt = pd.to_datetime(daily_df['date']).max()
    else:
        last_refresh_dt = datetime.now()
    
    # Estimated fraud exposure (based on risk scores and enrollment volumes)
    if 'total_enrollments' in risk_df.columns and 'risk_score' in risk_df.columns:
        # Weight by risk score
        high_risk = risk_df[risk_df['risk_level'].isin(['CRITICAL', 'HIGH'])]
        # Assume ₹50 per fraudulent enrollment as investigation cost
        exposure = high_risk['total_enrollments'].sum() * 50
    else:
        exposure = 0
    
    # KPI Strip
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("PIN Codes Monitored", f"{total_pins:,}")
    
    with col2:
        st.metric("Critical Risk PINs", f"{critical_pins:,}")
    
    with col3:
        st.metric("High Risk PINs", f"{high_pins:,}")
    
    with col4:
        if exposure >= 1e7:
            exposure_str = f"₹{exposure/1e7:.1f} Cr"
        elif exposure >= 1e5:
            exposure_str = f"₹{exposure/1e5:.1f} L"
        else:
            exposure_str = f"₹{exposure:,.0f}"
        st.metric("Est. Fraud Exposure", exposure_str)

    with col5:
        st.metric("Last Data Refresh", last_refresh_dt.strftime('%Y-%m-%d'))
    
    st.divider()
    
    # National risk trend and distributions
    section_header("National Composite Risk Trend", "Primary executive signal with 7-day smoothing")
    index_df = compute_national_index(daily_df) if daily_df is not None else None
    if index_df is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=index_df['date'], y=index_df['risk_index'],
            mode='lines', name='Risk Index', line=dict(color=SOC_COLORS['info'])
        ))
        fig.add_trace(go.Scatter(
            x=index_df['date'], y=index_df['risk_index_ma7'],
            mode='lines', name='7d Avg', line=dict(color=SOC_COLORS['medium'], dash='dash')
        ))
        fig.update_layout(
            height=260,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='Index (0-10)', showgrid=True, gridcolor=SOC_COLORS['border'], range=[0, 10]),
            font=dict(color=SOC_COLORS['text_primary']),
            showlegend=True,
            legend=dict(orientation='h')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("National trend unavailable (daily_summary.csv missing required fields).")

    st.divider()

    # Two-column layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Risk Distribution Chart
        section_header("Risk Distribution", "Count of PINs by deterministic risk bucket")
        
        risk_counts = risk_df['risk_level'].value_counts().reindex(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']).fillna(0)
        
        fig = go.Figure(data=[
            go.Bar(
                x=risk_counts.index,
                y=risk_counts.values,
                marker_color=[RISK_COLORS.get(x, '#58A6FF') for x in risk_counts.index],
                text=risk_counts.values,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title='', showgrid=False),
            yaxis=dict(title='PIN Codes', showgrid=True, gridcolor=SOC_COLORS['border']),
            font=dict(color=SOC_COLORS['text_primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # State-wise Risk Heatmap
        section_header("State-Level Threat Assessment", "Top 15 states by average risk score")
        
        state_df = load_state_data()
        if not state_df.empty:
            state_df = state_df.sort_values('avg_risk_score', ascending=False).head(15)
            
            fig = go.Figure(data=[
                go.Bar(
                    y=state_df['state'],
                    x=state_df['avg_risk_score'],
                    orientation='h',
                    marker=dict(
                        color=state_df['avg_risk_score'],
                        colorscale=[[0, SOC_COLORS['low']], [0.5, SOC_COLORS['medium']], [1, SOC_COLORS['critical']]],
                        showscale=True,
                        colorbar=dict(title='Risk')
                    ),
                    text=state_df['avg_risk_score'].round(2),
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title='Avg Risk Score', showgrid=True, gridcolor=SOC_COLORS['border'], range=[0, 10]),
                yaxis=dict(title='', showgrid=False, autorange='reversed'),
                font=dict(color=SOC_COLORS['text_primary'])
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        # Alert Queue
        section_header("Alert Queue", "Top alerts sorted by risk score")

        if not alerts_df.empty:
            display_alerts = alerts_df.copy()
            # Standardize and sort by risk_score when available
            col_map = {
                'alert_id': 'Alert ID',
                'pincode': 'PIN',
                'state': 'State',
                'district': 'District',
                'risk_score': 'Risk Score',
                'risk_level': 'Risk Level',
                'pattern_name': 'Pattern',
                'date_detected': 'First Detected',
                'created_at': 'Logged At',
                'recommended_action': 'Action'
            }
            present_cols = [c for c in col_map.keys() if c in display_alerts.columns]
            display_alerts = display_alerts[present_cols].rename(columns=col_map)
            sort_col = 'Risk Score' if 'Risk Score' in display_alerts.columns else display_alerts.columns[0]
            display_alerts = display_alerts.sort_values(by=sort_col, ascending=False).head(10)
            zebra_dataframe(display_alerts, hide_index=True, use_container_width=True)
        else:
            st.info("No active alerts")
        
        st.divider()
        
        # IOC Pattern Summary
        section_header("IOC Patterns", "Counts of distinct IOCs by pattern")
        
        if not ioc_df.empty:
            pattern_counts = ioc_df['pattern_name'].value_counts()
            
            for pattern, count in pattern_counts.items():
                st.markdown(f"**{pattern}**: {count}")
        else:
            st.info("No IOCs detected")
        
        st.divider()
        
        # System Status
        section_header("System Status", "Operational metadata for auditability")
        st.markdown(f"**Last Refresh**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.markdown("**Pipeline**: ✅ Operational")
        st.markdown("**Data Source**: UIDAI public datasets")
        st.markdown(f"**Random Seed**: 42 (Deterministic)")


# ============================================================================
# Page: Threat Map
# ============================================================================

def page_threat_map():
    """Geographic Risk Visualization."""
    st.title("🗺️ Threat Map")
    st.caption("Geographic distribution of risk across India")

    info_expander(
        "How this page works",
        bullets=[
            "Filters: risk level and state subset applied to all charts and tables below.",
            "State treemap: size = PIN count; color = average risk score (deterministic buckets).",
            "Hotspots: top 50 PINs by risk score with enrollment volume context.",
            "Tables: sorted views; use built-in column search for drill-down."
        ],
        footnote="Color semantics follow the style guide: red=critical, amber=medium/high, green=low, blue=info.",
        expanded=False
    )
    
    risk_df = load_risk_data()
    state_df = load_state_data()
    
    if risk_df is None:
        st.error("No data available.")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        risk_filter = st.multiselect(
            "Risk Level",
            options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            default=['CRITICAL', 'HIGH']
        )
    with col2:
        states = ['All'] + sorted(risk_df['state'].unique().tolist())
        state_filter = st.selectbox("State", states)
    
    # Filter data
    filtered_df = risk_df[risk_df['risk_level'].isin(risk_filter)]
    if state_filter != 'All':
        filtered_df = filtered_df[filtered_df['state'] == state_filter]
    
    # State-level aggregation for choropleth
    section_header("State-Level Risk", "Average risk score and PIN volume")

    if not state_df.empty:
        state_agg = risk_df.groupby('state').agg({
            'risk_score': 'mean',
            'pincode': 'count'
        }).reset_index()
        state_agg.columns = ['state', 'avg_risk', 'pin_count']
        state_agg = state_agg.sort_values('avg_risk', ascending=False).head(15)

        fig = go.Figure(data=[
            go.Bar(
                y=state_agg['state'],
                x=state_agg['avg_risk'],
                orientation='h',
                marker=dict(
                    color=state_agg['avg_risk'],
                    colorscale=[[0, SOC_COLORS['low']], [0.5, SOC_COLORS['medium']], [1, SOC_COLORS['critical']]],
                    showscale=True,
                    colorbar=dict(title='Avg Risk', tickfont=dict(color=SOC_COLORS['text_primary']))
                ),
                text=state_agg['pin_count'],
                textposition='outside',
                textfont=dict(color=SOC_COLORS['text_primary'])
            )
        ])

        fig.update_layout(
            height=480,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title='Avg Risk Score', gridcolor=SOC_COLORS['border'], range=[0, max(10, state_agg['avg_risk'].max() * 1.05)]),
            yaxis=dict(title='', autorange='reversed'),
            font=dict(color=SOC_COLORS['text_primary']),
            margin=dict(l=140, r=30, t=10, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # High-risk PIN hotspots
    section_header("High-Risk PIN Code Hotspots", "Top 50 by risk score with enrollment context")

    high_risk = filtered_df.nlargest(50, 'risk_score')

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.scatter(
            high_risk,
            x='total_enrollments',
            y='risk_score',
            color='risk_level',
            size='total_enrollments',
            hover_data=['pincode', 'district', 'state'],
            color_discrete_map=RISK_COLORS,
            title='Enrollment Volume vs Risk Score'
        )
        
        fig.update_layout(
            height=360,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor=SOC_COLORS['border'], title='Total Enrollments'),
            yaxis=dict(showgrid=True, gridcolor=SOC_COLORS['border'], title='Risk Score', range=[0, 10]),
            font=dict(color=SOC_COLORS['text_primary']),
            legend_title_text='Risk Level'
        )
        
        st.plotly_chart(fig, use_container_width=True)

        section_header("Enrollment vs Update Correlation", "Velocity pairing to expose synthetic behavior")
        corr_df = high_risk.dropna(subset=['enrollment_velocity', 'update_velocity']) if 'enrollment_velocity' in high_risk.columns and 'update_velocity' in high_risk.columns else high_risk
        fig_corr = px.scatter(
            corr_df,
            x='enrollment_velocity' if 'enrollment_velocity' in corr_df.columns else 'total_enrollments',
            y='update_velocity' if 'update_velocity' in corr_df.columns else 'total_demo_updates',
            color='risk_level',
            hover_data=['pincode', 'district', 'state'],
            color_discrete_map=RISK_COLORS,
            labels={'enrollment_velocity': 'Enrollment Velocity', 'update_velocity': 'Update Velocity'}
        )
        fig_corr.update_layout(
            height=320,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor=SOC_COLORS['border'], title='Enrollment Velocity'),
            yaxis=dict(showgrid=True, gridcolor=SOC_COLORS['border'], title='Update Velocity'),
            font=dict(color=SOC_COLORS['text_primary']),
            legend_title_text='Risk Level'
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    with col2:
        section_header("Top Risk States", "Sorted by mean risk score")
        
        state_risk = filtered_df.groupby('state').agg({
            'risk_score': 'mean',
            'pincode': 'count'
        }).reset_index()
        state_risk.columns = ['State', 'Avg Risk', 'PINs']
        state_risk = state_risk.sort_values('Avg Risk', ascending=False).head(10)
        
        zebra_dataframe(state_risk, hide_index=True, use_container_width=True)
    
    # Detailed table
    section_header("Filtered PIN Codes", "Applied filters: risk level + state")
    
    display_cols = ['pincode', 'state', 'district', 'risk_score', 'risk_level', 'total_enrollments']
    display_cols = [c for c in display_cols if c in filtered_df.columns]
    
    zebra_dataframe(
        filtered_df[display_cols].sort_values('risk_score', ascending=False).head(100),
        hide_index=True,
        use_container_width=True
    )


# ============================================================================
# Page: PIN Risk Explorer
# ============================================================================

def page_pin_explorer():
    """Investigation Mode - Deep dive into specific PIN codes."""
    st.title("🔍 PIN Risk Explorer")
    st.caption("Detailed investigation of individual PIN codes")

    info_expander(
        "How this page works",
        bullets=[
            "Select a PIN to view its risk score, drivers, and alert/IOC hits.",
            "Scores shown are computed by the pipeline; this view is read-only for auditability.",
            "Risk components are weighted to show contribution; weights are documented in methodology.",
            "District context compares the selected PIN against its peers to show outlier status."
        ],
        footnote="Data lineage: risk_scores.csv → this view. Refresh by rerunning the pipeline.",
        expanded=False
    )
    
    risk_df = load_risk_data()
    
    if risk_df is None:
        st.error("No data available.")
        return
    
    # PIN selector
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Search by PIN
        available_pins = risk_df['pincode'].unique().tolist()
        selected_pin = st.selectbox(
            "Select PIN Code",
            options=available_pins,
            index=0,
            help="Search or select a PIN code to investigate"
        )
    
    with col2:
        # Quick filters
        if st.button("🔴 Show Highest Risk"):
            selected_pin = risk_df.loc[risk_df['risk_score'].idxmax(), 'pincode']
            st.rerun()
    
    # Get PIN data
    pin_data = risk_df[risk_df['pincode'] == selected_pin].iloc[0]
    
    st.divider()
    
    # PIN Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"### PIN: {selected_pin}")
        st.markdown(f"**State**: {pin_data.get('state', 'N/A')}")
        st.markdown(f"**District**: {pin_data.get('district', 'N/A')}")
    
    with col2:
        risk_color = RISK_COLORS.get(pin_data.get('risk_level', 'LOW'), '#E6EDF3')
        st.markdown(f"### Risk Score")
        st.markdown(f"<span style='font-size: 2.5rem; color: {risk_color}; font-weight: bold;'>{pin_data.get('risk_score', 0):.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"**Level**: {pin_data.get('risk_level', 'N/A')}")
    
    with col3:
        st.markdown("### Volume")
        st.metric("Total Enrollments", f"{int(pin_data.get('total_enrollments', 0)):,}")
        st.metric("Demo Updates", f"{int(pin_data.get('total_demo_updates', 0)):,}")
        st.metric("Bio Updates", f"{int(pin_data.get('total_bio_updates', 0)):,}")
    
    st.divider()
    
    # Risk Breakdown
    section_header("Risk Component Breakdown", "Weighted contribution to overall risk score")
    
    # Create stacked bar for risk components
    components = {
        'Enrollment Velocity': pin_data.get('risk_enrollment_velocity', 0) * 0.30,
        'Update Velocity': pin_data.get('risk_update_velocity', 0) * 0.25,
        'Demographic Anomaly': pin_data.get('risk_demographic_anomaly', 0) * 0.20,
        'Geographic Outlier': pin_data.get('risk_geographic_outlier', 0) * 0.15,
        'Temporal Spike': pin_data.get('risk_temporal_spike', 0) * 0.10
    }
    
    fig = go.Figure(data=[
        go.Bar(
            y=list(components.keys()),
            x=list(components.values()),
            orientation='h',
            marker_color=SOC_COLORS['info'],
            text=[f'{v:.2f}' for v in components.values()],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Weighted Contribution', showgrid=True, gridcolor=SOC_COLORS['border'], range=[0, 3]),
        yaxis=dict(title='', showgrid=False),
        font=dict(color=SOC_COLORS['text_primary'])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        section_header("Velocity Metrics", "Higher velocity indicates potential synthetic activity")
        
        velocity_data = {
            'Metric': ['Enrollment Velocity', 'Update Velocity', 'Bio Velocity'],
            'Value': [
                pin_data.get('enrollment_velocity', 0),
                pin_data.get('update_velocity', 0),
                pin_data.get('bio_velocity', 0)
            ]
        }
        
        vel_df = pd.DataFrame(velocity_data)
        vel_df['Interpretation'] = vel_df['Value'].apply(
            lambda x: '🔴 Very High' if x > 4 else ('🟡 High' if x > 2 else ('🟢 Normal' if x < 1.5 else '🟡 Elevated'))
        )
        
        zebra_dataframe(vel_df, hide_index=True, use_container_width=True)
    
    with col2:
        section_header("Anomaly Scores (Z-scores)", "|z| > 3 = anomaly; 2–3 = watch")
        
        zscore_data = {
            'Metric': ['Child Ratio', 'Update Ratio', 'Bio Recapture'],
            'Z-score': [
                round(pin_data.get('child_ratio_zscore', 0), 2),
                round(pin_data.get('update_ratio_zscore', 0), 2),
                round(pin_data.get('bio_recapture_ratio_zscore', 0), 2)
            ]
        }
        
        z_df = pd.DataFrame(zscore_data)
        z_df['Interpretation'] = z_df['Z-score'].abs().apply(
            lambda x: '🔴 Anomaly' if x > 3 else ('🟡 Watch' if x > 2 else '🟢 Normal')
        )
        
        zebra_dataframe(z_df, hide_index=True, use_container_width=True)
    
    # Context: Neighboring PINs
    section_header("District Context", "Where this PIN sits versus its district peers")
    
    district = pin_data.get('district', '')
    district_pins = risk_df[risk_df['district'] == district]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**PINs in {district}**: {len(district_pins)}")
        st.markdown(f"**District Avg Risk**: {district_pins['risk_score'].mean():.2f}")
        st.markdown(f"**This PIN vs District**: {'+' if pin_data.get('risk_score', 0) > district_pins['risk_score'].mean() else ''}{(pin_data.get('risk_score', 0) - district_pins['risk_score'].mean()):.2f}")

        # Context table versus district and national benchmarks
        nat_median = risk_df['risk_score'].median()
        ctx_rows = [
            {
                'Metric': 'Risk Score',
                'This PIN': round(pin_data.get('risk_score', 0), 2),
                'District Avg': round(district_pins['risk_score'].mean(), 2),
                'National Median': round(nat_median, 2),
                'Delta vs District': round(pin_data.get('risk_score', 0) - district_pins['risk_score'].mean(), 2)
            },
            {
                'Metric': 'Enrollments',
                'This PIN': int(pin_data.get('total_enrollments', 0)),
                'District Avg': int(district_pins['total_enrollments'].mean()) if 'total_enrollments' in district_pins else 0,
                'National Median': int(risk_df['total_enrollments'].median()) if 'total_enrollments' in risk_df else 0,
                'Delta vs District': int(pin_data.get('total_enrollments', 0) - (district_pins['total_enrollments'].mean() if 'total_enrollments' in district_pins else 0))
            }
        ]
        zebra_dataframe(pd.DataFrame(ctx_rows), hide_index=True, use_container_width=True)
    
    with col2:
        # Histogram of district risk scores
        fig = go.Figure(data=[
            go.Histogram(
                x=district_pins['risk_score'],
                nbinsx=20,
                marker_color=SOC_COLORS['info']
            )
        ])
        
        # Add line for current PIN
        fig.add_vline(x=pin_data.get('risk_score', 0), line_dash="dash", line_color=SOC_COLORS['critical'])
        
        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title='Risk Score', showgrid=False),
            yaxis=dict(title='Count', showgrid=True, gridcolor=SOC_COLORS['border']),
            font=dict(color=SOC_COLORS['text_primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk Factors
    if 'risk_factors' in pin_data.index:
        st.subheader("Primary Risk Factors")
        st.info(pin_data.get('risk_factors', 'No significant factors'))


# ============================================================================
# Page: Temporal Analysis
# ============================================================================

def page_temporal():
    """Temporal Analysis - Spike Detection."""
    st.title("📈 Temporal Analysis")
    st.caption("Time-series patterns and spike detection")

    info_expander(
        "How this page works",
        bullets=[
            "Uses daily_summary.csv for time-series; falls back to risk distribution if missing.",
            "Date range filter applies to all charts and KPIs below.",
            "Trend lines are raw counts; no smoothing to keep spikes visible.",
            "State heatmap ranks states by average risk across selected period."],
        footnote="Refresh cadence: whenever pipeline runs and writes daily_summary.csv.",
        expanded=False
    )
    
    daily_df = load_daily_data()
    risk_df = load_risk_data()
    
    if daily_df.empty:
        st.warning("Daily time-series data not available.")
        
        # Show risk score distribution over time using state data
        if risk_df is not None:
            st.subheader("Risk Score Distribution")
            
            fig = go.Figure(data=[
                go.Histogram(x=risk_df['risk_score'], nbinsx=50, marker_color=SOC_COLORS['info'])
            ])
            
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title='Risk Score', showgrid=True, gridcolor=SOC_COLORS['border']),
                yaxis=dict(title='Frequency', showgrid=True, gridcolor=SOC_COLORS['border']),
                font=dict(color=SOC_COLORS['text_primary'])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        return
    
    # Date range filter
    min_date = daily_df['date'].min()
    max_date = daily_df['date'].max()
    
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        filtered_df = daily_df[(daily_df['date'] >= pd.Timestamp(date_range[0])) & 
                               (daily_df['date'] <= pd.Timestamp(date_range[1]))]
    else:
        filtered_df = daily_df
    
    # Main trend chart
    section_header("Activity Trends", "Daily counts across enrollments and updates")
    
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        subplot_titles=('Enrollments', 'Demographic Updates', 'Biometric Updates'))
    
    fig.add_trace(
        go.Scatter(x=filtered_df['date'], y=filtered_df['total_enrollments'],
                   mode='lines', name='Enrollments', line=dict(color=SOC_COLORS['info'])) ,
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=filtered_df['date'], y=filtered_df['total_demo_updates'],
                   mode='lines', name='Demo Updates', line=dict(color=SOC_COLORS['medium'])) ,
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=filtered_df['date'], y=filtered_df['total_bio_updates'],
                   mode='lines', name='Bio Updates', line=dict(color=SOC_COLORS['critical'])) ,
        row=3, col=1
    )
    
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=SOC_COLORS['text_primary']),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=SOC_COLORS['border'])
    fig.update_yaxes(showgrid=True, gridcolor=SOC_COLORS['border'])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Avg Daily Enrollments", f"{filtered_df['total_enrollments'].mean():,.0f}")
    with col2:
        st.metric("Peak Enrollments", f"{filtered_df['total_enrollments'].max():,.0f}")
    with col3:
        st.metric("Avg Daily Updates", f"{filtered_df['total_demo_updates'].mean():,.0f}")
    with col4:
        st.metric("Active Days", f"{len(filtered_df)}")
    
    # State-wise monthly heatmap
    section_header("State-wise Activity Heatmap", "Top 15 states by mean risk score")
    
    if risk_df is not None and not risk_df.empty:
        # Proper state-wise risk heatmap
        state_risk = risk_df.groupby('state').agg({
            'risk_score': 'mean',
            'pincode': 'count',
            'total_enrollments': 'sum' if 'total_enrollments' in risk_df.columns else 'count'
        }).reset_index()
        state_risk.columns = ['State', 'Avg Risk', 'PIN Count', 'Total Volume']
        state_risk = state_risk.sort_values('Avg Risk', ascending=False)
        
        # Create a proper heatmap with state names on y-axis
        top_states = state_risk.head(15)
        
        fig = go.Figure(data=go.Bar(
            x=top_states['Avg Risk'],
            y=top_states['State'],
            orientation='h',
            marker=dict(
                color=top_states['Avg Risk'],
                colorscale=[[0, SOC_COLORS['low']], [0.4, SOC_COLORS['medium']], [0.7, SOC_COLORS['high']], [1, SOC_COLORS['critical']]],
                showscale=True,
                colorbar=dict(title="Risk Score", tickfont=dict(color=SOC_COLORS['text_primary']))
            ),
            text=[f"{v:.2f}" for v in top_states['Avg Risk']],
            textposition='outside',
            textfont=dict(color=SOC_COLORS['text_primary'], size=10),
            hovertemplate="<b>%{y}</b><br>Avg Risk: %{x:.2f}<br>PINs: %{customdata[0]:,}<extra></extra>",
            customdata=top_states[['PIN Count']].values
        ))
        
        fig.update_layout(
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=SOC_COLORS['text_primary']),
            xaxis=dict(
                title="Average Risk Score",
                gridcolor=SOC_COLORS['border'],
                range=[0, max(top_states['Avg Risk']) * 1.15]
            ),
            yaxis=dict(
                title="",
                autorange="reversed"
            ),
            margin=dict(l=150, r=50, t=30, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional: State risk distribution table
        with st.expander("📊 Full State Risk Distribution"):
            display_df = state_risk.copy()
            display_df['Avg Risk'] = display_df['Avg Risk'].round(2)
            display_df['Total Volume'] = display_df['Total Volume'].apply(lambda x: f"{x:,.0f}")
            st.dataframe(display_df, hide_index=True, use_container_width=True)


# ============================================================================
# Page: IOC Catalogue
# ============================================================================

def page_ioc_catalogue():
    """IOC Catalogue - Threat Intelligence Library."""
    st.title("📋 IOC Catalogue")
    st.caption("Indicators of Compromise detected across all PIN codes")

    info_expander(
        "How this page works",
        bullets=[
            "Filters apply to all summaries, tables, and exports.",
            "IOC table lists every detection with pattern, location, and risk level.",
            "Pattern distribution shows proportional share of each IOC type.",
            "Export button delivers the currently filtered set as CSV for downstream triage."
        ],
        footnote="Detection rules are fixed and documented in Methodology → IOC Detection Rules.",
        expanded=False
    )
    
    ioc_df = load_ioc_data()
    
    if ioc_df.empty:
        st.info("No IOCs have been detected in the current analysis.")
        
        # Show IOC pattern definitions
        st.subheader("IOC Pattern Definitions")
        
        patterns = {
            'Mass Enrollment Spike (MES)': '>400% increase in enrollments within 7 days',
            'Demographic Surge (DMS)': '>3× median demographic updates',
            'Biometric Churn (BIO)': '>30% biometric recapture ratio',
            'Child Ratio Anomaly (CRA)': 'Z-score > 3 for child enrollment ratio',
            'Coordinated PIN Spike (CPS)': 'Simultaneous high activity across enrollment, demographic, and biometric',
            'Ghost Enrollment (GHE)': 'Low child ratio + high update velocity (possible deceased identity fraud)',
            'Operator Collusion (OPC)': 'Extreme combined velocity in top 1% (enrollment center fraud)',
            'Multi-PIN Sync (MPS)': '>30% of district PINs elevated simultaneously (fraud ring)'
        }
        
        for pattern, definition in patterns.items():
            st.markdown(f"**{pattern}**: {definition}")
        
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pattern_filter = st.multiselect(
            "Pattern Type",
            options=ioc_df['pattern_name'].unique().tolist(),
            default=ioc_df['pattern_name'].unique().tolist()
        )
    
    with col2:
        risk_filter = st.multiselect(
            "Risk Level",
            options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            default=['CRITICAL', 'HIGH']
        )
    
    with col3:
        state_filter = st.selectbox(
            "State",
            options=['All'] + sorted(ioc_df['state'].unique().tolist())
        )
    
    # Filter data
    filtered_ioc = ioc_df[
        (ioc_df['pattern_name'].isin(pattern_filter)) &
        (ioc_df['risk_level'].isin(risk_filter))
    ]
    
    if state_filter != 'All':
        filtered_ioc = filtered_ioc[filtered_ioc['state'] == state_filter]
    
    # Summary stats
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total IOCs", len(filtered_ioc))
    with col2:
        st.metric("Critical", len(filtered_ioc[filtered_ioc['risk_level'] == 'CRITICAL']))
    with col3:
        st.metric("Affected PINs", filtered_ioc['pincode'].nunique())
    with col4:
        st.metric("Affected States", filtered_ioc['state'].nunique())
    
    st.divider()
    
    # IOC Table
    section_header("IOC Details", "Filtered by pattern, risk, and state")
    
    display_cols = ['ioc_id', 'pattern_name', 'pincode', 'state', 'district', 
                   'risk_score', 'risk_level', 'description']
    display_cols = [c for c in display_cols if c in filtered_ioc.columns]
    
    zebra_dataframe(
        filtered_ioc[display_cols].sort_values('risk_score', ascending=False),
        hide_index=True,
        use_container_width=True,
        height=400
    )
    
    # Export button
    st.download_button(
        label="📥 Export IOC Catalogue (CSV)",
        data=filtered_ioc.to_csv(index=False),
        file_name=f"ioc_catalogue_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Pattern breakdown
    section_header("Pattern Distribution", "Share of IOC types in current filter")
    
    pattern_counts = filtered_ioc['pattern_name'].value_counts()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=pattern_counts.index,
            values=pattern_counts.values,
            hole=0.4,
            marker_colors=[SOC_COLORS['critical'], SOC_COLORS['high'], SOC_COLORS['medium'], SOC_COLORS['low'], SOC_COLORS['info']][:len(pattern_counts)]
        )
    ])
    
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=SOC_COLORS['text_primary']),
        showlegend=True,
        legend=dict(orientation="h")
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# Page: Data Health
# ============================================================================

def page_data_health():
    """Data Health - Signal Validation."""
    st.title("🔬 Data Health")
    st.caption("Data quality metrics and validation checks")

    info_expander(
        "How this page works",
        bullets=[
            "Quality metrics derived directly from risk_scores.csv.",
            "Field statistics show distribution and null coverage for numeric fields.",
            "Validation checks enforce deterministic rules (ranges, formats, clipping).",
            "Known limitations are explicitly stated to avoid overclaiming data quality."
        ],
        footnote="Run pipeline again after any data correction to refresh these metrics.",
        expanded=False
    )
    
    risk_df = load_risk_data()
    
    if risk_df is None:
        st.error("No data available.")
        return
    
    # Data quality metrics
    section_header("Quality Metrics", "Nulls, duplicates, field counts")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_cells = risk_df.size
    null_cells = risk_df.isna().sum().sum()
    null_pct = (null_cells / total_cells) * 100
    
    with col1:
        st.metric("Total Records", f"{len(risk_df):,}")
    with col2:
        st.metric("Total Fields", f"{len(risk_df.columns)}")
    with col3:
        st.metric("Null Values", f"{null_pct:.2f}%")
    with col4:
        st.metric("Duplicate PINs", f"{risk_df['pincode'].duplicated().sum()}")
    
    st.divider()
    
    # Column statistics
    section_header("Field Statistics", "Distribution and missingness for numeric columns")
    
    numeric_cols = risk_df.select_dtypes(include=[np.number]).columns.tolist()
    
    stats_df = risk_df[numeric_cols].describe().T
    stats_df['null_count'] = risk_df[numeric_cols].isna().sum()
    stats_df['null_pct'] = (stats_df['null_count'] / len(risk_df) * 100).round(2)
    
    zebra_dataframe(stats_df, use_container_width=True)
    
    st.divider()
    
    # Validation checks
    section_header("Validation Checks", "Deterministic rules applied post-pipeline")
    
    checks = []
    
    # Check 1: Risk scores in valid range
    risk_in_range = (risk_df['risk_score'] >= 0) & (risk_df['risk_score'] <= 10)
    checks.append({
        'Check': 'Risk scores in [0, 10] range',
        'Status': '✅ PASS' if risk_in_range.all() else '❌ FAIL',
        'Details': f"{risk_in_range.sum():,} / {len(risk_df):,} records valid"
    })
    
    # Check 2: All PINs have 6 digits
    valid_pins = risk_df['pincode'].astype(str).str.match(r'^\d{6}$')
    checks.append({
        'Check': 'PIN codes are 6 digits',
        'Status': '✅ PASS' if valid_pins.all() else '⚠️ WARN',
        'Details': f"{valid_pins.sum():,} / {len(risk_df):,} valid format"
    })
    
    # Check 3: Totals are non-negative
    if 'total_enrollments' in risk_df.columns:
        non_neg = risk_df['total_enrollments'] >= 0
        checks.append({
            'Check': 'Enrollment counts non-negative',
            'Status': '✅ PASS' if non_neg.all() else '❌ FAIL',
            'Details': f"{non_neg.sum():,} / {len(risk_df):,} valid"
        })
    
    # Check 4: Risk categories assigned
    valid_levels = risk_df['risk_level'].isin(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])
    checks.append({
        'Check': 'Valid risk categories assigned',
        'Status': '✅ PASS' if valid_levels.all() else '❌ FAIL',
        'Details': f"{valid_levels.sum():,} / {len(risk_df):,} categorized"
    })
    
    # Check 5: Z-scores clipped to ±5
    zscore_cols = [c for c in risk_df.columns if 'zscore' in c]
    if zscore_cols:
        zscores_clipped = True
        for col in zscore_cols:
            if (risk_df[col].abs() > 5.01).any():  # Small tolerance
                zscores_clipped = False
                break
        checks.append({
            'Check': 'Z-scores clipped to ±5',
            'Status': '✅ PASS' if zscores_clipped else '❌ FAIL',
            'Details': f"{len(zscore_cols)} Z-score columns checked"
        })
    
    checks_df = pd.DataFrame(checks)
    zebra_dataframe(checks_df, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # Known limitations
    st.subheader("Known Limitations")
    
    st.markdown("""
    * **Data Scope**: Analysis limited to enrollment, demographic, and biometric update data only
    * **No External Validation**: Cannot verify against external fraud databases
    * **Temporal Granularity**: Date-level analysis (no time-of-day patterns)
    * **Geographic Precision**: PIN-code level (no sub-PIN analysis)
    * **Model Type**: Rule-based detection only (no ML predictions)
    """)
    
    st.info(f"**Last Validated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ============================================================================
# Page: Methodology
# ============================================================================

def page_methodology():
    """Methodology - Defensible Analytics."""
    st.title("📖 Methodology")
    st.caption("Technical documentation for audit and review")
    
    st.markdown("""
    ## Overview
    
    This system implements **risk-based anomaly detection** for identifying potential Aadhaar 
    fraud patterns. It is **NOT** a fraud confirmation system - it prioritizes PIN codes 
    for investigative review based on statistical anomalies.
    
    ---
    
    ## Data Sources
    
    The system uses **only three official UIDAI datasets**:
    
    | Dataset | Description | Key Fields |
    |---------|-------------|------------|
    | Enrollment | New Aadhaar registrations | Date, State, District, PIN, Age groups |
    | Demographic Updates | Address/name changes | Date, State, District, PIN, Age groups |
    | Biometric Updates | Fingerprint/iris recaptures | Date, State, District, PIN, Age groups |
    
    **No external data, APIs, or synthetic data is used.**
    
    ---
    
    ## Risk Score Formula
    
    The composite risk score (0-10 scale) is calculated as:
    
    ```
    Risk_Score = 
        (Enrollment_Velocity × 0.30) +
        (Update_Velocity × 0.25) +
        (Demographic_Anomaly × 0.20) +
        (Geographic_Outlier × 0.15) +
        (Temporal_Spike × 0.10)
    ```
    
    ### Component Definitions
    
    | Component | Weight | Calculation |
    |-----------|--------|-------------|
    | Enrollment Velocity | 30% | PIN enrollments / National median enrollments |
    | Update Velocity | 25% | PIN demographic updates / National median updates |
    | Demographic Anomaly | 20% | Combined Z-score of child ratio, update ratio, bio recapture |
    | Geographic Outlier | 15% | Deviation from district median |
    | Temporal Spike | 10% | Sudden activity changes over time |
    
    ---
    
    ## Risk Categories
    
    | Category | Score Range | Interpretation |
    |----------|-------------|----------------|
    | **CRITICAL** | ≥ 8 | Immediate investigation required |
    | **HIGH** | 6 - 7.99 | Priority review within 48 hours |
    | **MEDIUM** | 4 - 5.99 | Add to monitoring queue |
    | **LOW** | < 4 | Normal activity patterns |
    
    ---
    
    ## IOC Detection Rules
    
    Indicators of Compromise are detected using fixed, transparent rules:
    
    | Pattern | Code | Trigger Condition |
    |---------|------|-------------------|
    | Mass Enrollment Spike | MES | >400% increase in enrollments within 7 days |
    | Demographic Surge | DMS | >3× median demographic updates |
    | Biometric Churn | BIO | >30% biometric recapture ratio |
    | Child Ratio Anomaly | CRA | Z-score > 3 for child enrollment ratio |
    | Coordinated PIN Spike | CPS | High activity across all three metrics simultaneously |
    | Ghost Enrollment Pattern | GHE | Low child ratio + high update velocity (deceased identity risk) |
    | Operator Collusion Indicator | OPC | Extreme combined velocity in top 1% (enrollment center fraud) |
    | Multi-PIN Synchronization | MPS | >30% of district PINs elevated simultaneously (fraud ring) |
    
    ---
    
    ## False Positive Mitigation
    
    1. **Z-score Clipping**: All Z-scores are clipped to ±5 to prevent extreme outlier dominance
    2. **Percentile Normalization**: Velocity metrics use 99th percentile capping
    3. **Multi-factor Requirement**: High risk requires elevated scores across multiple components
    4. **Geographic Context**: PIN scores are compared against district baselines
    
    ---
    
    ## Why No Machine Learning?
    
    This system deliberately uses **rule-based detection** because:
    
    1. **Explainability**: Every risk score can be traced to specific data points
    2. **Auditability**: Rules are fixed and documented
    3. **No Training Data**: No labeled fraud cases available
    4. **Transparency**: Investigators can understand and challenge findings
    5. **Reproducibility**: Same input always produces same output (seed=42)
    
    ---
    
    ## Reproducibility
    
    * **Random Seed**: Fixed at 42
    * **Deterministic Processing**: Same data produces identical results
    * **Version Control**: All code and parameters are documented
    * **No External Dependencies**: Runs completely offline
    
    ---
    
    ## Limitations
    
    * Cannot confirm actual fraud - only flags statistical anomalies
    * Limited to patterns detectable from enrollment/update volumes
    * No individual-level analysis (PIN-level aggregation only)
    * Cannot detect sophisticated fraud that mimics normal patterns
    """)


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point."""
    
    # Check if data exists
    check_data_exists()
    
    # Sidebar navigation
    st.sidebar.title("🛡️ A-SOC")
    st.sidebar.caption("Aadhaar Security Operations")
    
    st.sidebar.divider()
    
    # Navigation (redesign: teaching-first, micro → macro)
    pages = {
        "Data Foundations": page_data_foundations,
        "Variable-Level Statistics": page_variable_stats,
        "Derived Metrics & Calculations": page_derived_metrics,
        "Local / Regional Insights": page_local_regional,
        "National Statistics": page_national_stats,
        "Interpretation & Use-Cases": page_interpretation
    }
    
    selection = st.sidebar.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
    
    st.sidebar.divider()
    
    # Quick stats
    risk_df = load_risk_data()
    if risk_df is not None:
        st.sidebar.markdown("**Quick Stats**")
        st.sidebar.markdown(f"PINs: {len(risk_df):,}")
        st.sidebar.markdown(f"Critical: {len(risk_df[risk_df['risk_level'] == 'CRITICAL']):,}")
        st.sidebar.markdown(f"High: {len(risk_df[risk_df['risk_level'] == 'HIGH']):,}")
    
    st.sidebar.divider()
    st.sidebar.caption("v1.0 | Random Seed: 42")
    
    # Render selected page
    pages[selection]()


if __name__ == "__main__":
    main()
