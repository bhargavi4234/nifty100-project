import os

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# PAGE TITLE
# ============================================================

st.title("💰 Capital Allocation Map")

st.markdown(
    "Explore the Nifty 100 companies by their capital allocation "
    "patterns based on operating, investing and financing cash flows."
)


# ============================================================
# FILE PATH
# ============================================================

CAPITAL_FILE = "output/capital_allocation.csv"


# ============================================================
# LOAD CAPITAL ALLOCATION DATA
# ============================================================


@st.cache_data(ttl=600)
def load_capital_data():
    "Load capital data."

    if not os.path.exists(CAPITAL_FILE):
        return pd.DataFrame()

    df = pd.read_csv(CAPITAL_FILE)

    return df


df = load_capital_data()


# ============================================================
# CHECK DATA
# ============================================================

if df.empty:

    st.error("Capital allocation data is not available.")

    st.stop()


required_columns = [
    "company_id",
    "year",
    "cfo_sign",
    "cfi_sign",
    "cff_sign",
    "pattern_label",
]


missing_columns = [column for column in required_columns if column not in df.columns]


if missing_columns:

    st.error("Missing columns: " + ", ".join(missing_columns))

    st.stop()


# ============================================================
# CLEAN YEAR
# ============================================================

df["year_number"] = df["year"].astype(str).str.extract(r"(\d{4})")[0]

df["year_number"] = pd.to_numeric(df["year_number"], errors="coerce")


# ============================================================
# LATEST PATTERN FOR EACH COMPANY
# ============================================================

latest_df = (
    df.sort_values(["company_id", "year_number"])
    .drop_duplicates(subset=["company_id"], keep="last")
    .reset_index(drop=True)
)


# ============================================================
# CHECK COMPANY COUNT
# ============================================================

company_count = latest_df["company_id"].nunique()

pattern_count = latest_df["pattern_label"].nunique()


# ============================================================
# SUMMARY KPIs
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.metric("Companies", company_count)

with col2:

    st.metric("Capital Allocation Patterns", pattern_count)


# ============================================================
# TREEMAP
# ============================================================

st.markdown("---")

st.subheader("🌳 Capital Allocation Pattern Map")

st.caption(
    "Each rectangle represents a company. "
    "Companies are grouped by their latest capital allocation pattern."
)


# Give every company equal weight.
latest_df["company_value"] = 1


fig = px.treemap(
    latest_df,
    path=[px.Constant("Nifty 100"), "pattern_label", "company_id"],
    values="company_value",
    color="pattern_label",
    hover_data={
        "company_id": True,
        "pattern_label": True,
        "year": True,
        "cfo_sign": True,
        "cfi_sign": True,
        "cff_sign": True,
        "company_value": False,
    },
    title="Companies by Capital Allocation Pattern",
)


fig.update_layout(height=700)


fig.update_traces(textinfo="label+value")


# ============================================================
# DISPLAY TREEMAP
# ============================================================

selection = st.plotly_chart(
    fig, use_container_width=True, on_select="rerun", selection_mode="points"
)


# ============================================================
# SELECTED PATTERN
# ============================================================

selected_pattern = None


try:

    points = selection.selection.points

    if points:

        point_index = points[0].get("point_index")

        if point_index is not None:

            selected_row = latest_df.iloc[point_index]

            selected_pattern = selected_row["pattern_label"]

except (AttributeError, IndexError, KeyError, TypeError):
    selected_pattern = None


# ============================================================
# PATTERN SELECTOR FALLBACK
# ============================================================

st.markdown("---")

st.subheader("🔎 View Companies by Pattern")

pattern_options = sorted(latest_df["pattern_label"].dropna().unique().tolist())


selected_pattern_dropdown = st.selectbox(
    "Select a capital allocation pattern", pattern_options
)


# Use clicked pattern when available.
pattern_to_show = (
    selected_pattern
    if selected_pattern in pattern_options
    else selected_pattern_dropdown
)


# ============================================================
# COMPANY LIST
# ============================================================

pattern_df = latest_df[latest_df["pattern_label"] == pattern_to_show].copy()


st.subheader(f"Companies — {pattern_to_show}")


st.caption(
    f"{len(pattern_df)} companies follow this pattern "
    "in their latest available year."
)


display_df = pattern_df[
    ["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"]
].copy()


display_df = display_df.rename(
    columns={
        "company_id": "Ticker",
        "year": "Latest Year",
        "cfo_sign": "CFO",
        "cfi_sign": "CFI",
        "cff_sign": "CFF",
        "pattern_label": "Pattern",
    }
)


st.dataframe(display_df, use_container_width=True, hide_index=True)


# ============================================================
# PATTERN SUMMARY
# ============================================================

st.markdown("---")

st.subheader("Pattern Distribution")


pattern_summary = latest_df["pattern_label"].value_counts().reset_index()


pattern_summary.columns = ["Pattern", "Companies"]


fig_summary = px.bar(
    pattern_summary,
    x="Pattern",
    y="Companies",
    text="Companies",
    title="Nifty 100 Capital Allocation Patterns",
)


fig_summary.update_traces(textposition="outside")


fig_summary.update_layout(
    height=450,
    xaxis_title="Capital Allocation Pattern",
    yaxis_title="Number of Companies",
)


st.plotly_chart(fig_summary, use_container_width=True)
