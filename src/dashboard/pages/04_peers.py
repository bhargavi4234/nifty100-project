import sqlite3

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PAGE TITLE
# ============================================================

st.title("👥 Peer Comparison")

st.markdown(
    "Compare a company with its peer group using financial "
    "metrics and a radar chart."
)


# ============================================================
# DATABASE
# ============================================================

DB_PATH = "data/db/nifty100.db"


@st.cache_data(ttl=600)
def load_peer_data():
    "Load peer data."

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        pg.peer_group_name,
        pg.company_id,
        pg.is_benchmark,

        c.company_name,

        fr.year,
        fr.net_profit_margin_pct,
        fr.operating_profit_margin_pct,
        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.interest_coverage,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.return_on_capital_employed_pct

    FROM peer_groups pg

    LEFT JOIN companies c
        ON pg.company_id = c.id

    LEFT JOIN financial_ratios fr
        ON pg.company_id = fr.company_id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


df = load_peer_data()


# ============================================================
# CHECK DATA
# ============================================================

if df.empty:

    st.warning("No peer comparison data available.")

    st.stop()


# ============================================================
# CLEAN YEAR
# ============================================================

df["year_number"] = df["year"].astype(str).str.extract(r"(\d{4})")[0]

df["year_number"] = pd.to_numeric(df["year_number"], errors="coerce")


# ============================================================
# SELECT LATEST YEAR FOR EACH COMPANY
# ============================================================

df = (
    df.sort_values(["company_id", "year_number"])
    .drop_duplicates(subset=["peer_group_name", "company_id"], keep="last")
    .reset_index(drop=True)
)


# ============================================================
# PEER GROUP DROPDOWN
# ============================================================

st.sidebar.header("Peer Group")

peer_groups = sorted(df["peer_group_name"].dropna().unique().tolist())


selected_group = st.sidebar.selectbox("Select Peer Group", peer_groups)


# ============================================================
# FILTER SELECTED PEER GROUP
# ============================================================

group_df = df[df["peer_group_name"] == selected_group].copy()


if group_df.empty:

    st.warning("No companies found in the selected peer group.")

    st.stop()


# ============================================================
# COMPANY DROPDOWN
# ============================================================

company_options = (
    group_df[["company_id", "company_name"]]
    .drop_duplicates()
    .sort_values("company_name")
)


company_labels = {
    row["company_id"]: f"{row['company_id']} — {row['company_name']}"
    for _, row in company_options.iterrows()
}


selected_company = st.selectbox(
    "Select Company",
    company_options["company_id"].tolist(),
    format_func=lambda x: company_labels.get(x, x),
)


# ============================================================
# SELECTED COMPANY DATA
# ============================================================

company_df = group_df[group_df["company_id"] == selected_company].copy()


if company_df.empty:

    st.warning("Selected company data is not available.")

    st.stop()


company_row = company_df.iloc[0]


# ============================================================
# COMPANY HEADER
# ============================================================

st.markdown("---")

st.subheader(f"{company_row['company_name']} ({selected_company})")

if company_row["is_benchmark"] == 1:

    st.success("⭐ This company is the benchmark company for this peer group.")


# ============================================================
# RADAR METRICS
# ============================================================

metric_columns = {
    "ROE": "return_on_equity_pct",
    "ROCE": "return_on_capital_employed_pct",
    "Net Profit Margin": "net_profit_margin_pct",
    "OPM": "operating_profit_margin_pct",
    "Revenue CAGR": "revenue_cagr_5yr",
    "PAT CAGR": "pat_cagr_5yr",
    "D/E": "debt_to_equity",
    "Interest Coverage": "interest_coverage",
}


# ============================================================
# CONVERT NUMERIC VALUES
# ============================================================

for column in metric_columns.values():

    group_df[column] = pd.to_numeric(group_df[column], errors="coerce")


# ============================================================
# PEER AVERAGE
# ============================================================

peer_average = {}

for metric_name, column_name in metric_columns.items():

    peer_average[metric_name] = (
        group_df[column_name].replace([np.inf, -np.inf], np.nan).mean()
    )


# ============================================================
# SELECTED COMPANY VALUES
# ============================================================

company_values = {}

for metric_name, column_name in metric_columns.items():

    company_values[metric_name] = pd.to_numeric(
        company_row[column_name], errors="coerce"
    )


# ============================================================
# RADAR CHART
# ============================================================

st.markdown("---")

st.subheader("📡 Company vs Peer Group Average")


categories = list(metric_columns.keys())


company_radar = []

peer_radar = []

for category in categories:

    company_value = company_values[category]

    peer_value = peer_average[category]

    if pd.isna(company_value):
        company_value = 0

    if pd.isna(peer_value):
        peer_value = 0

    company_radar.append(company_value)
    peer_radar.append(peer_value)


# Close the radar polygons
categories_closed = categories + [categories[0]]

company_radar_closed = company_radar + [company_radar[0]]

peer_radar_closed = peer_radar + [peer_radar[0]]


fig = go.Figure()


fig.add_trace(
    go.Scatterpolar(
        r=company_radar_closed,
        theta=categories_closed,
        fill="toself",
        name=selected_company,
    )
)


fig.add_trace(
    go.Scatterpolar(
        r=peer_radar_closed, theta=categories_closed, fill="toself", name="Peer Average"
    )
)


fig.update_layout(
    polar={"radialaxis": {"visible": True}},
    showlegend=True,
    height=600,
)

st.plotly_chart(fig, use_container_width=True)


# ============================================================
# KPI TABLE
# ============================================================

st.markdown("---")

st.subheader(f"📊 {selected_group} — Company Comparison")


table_columns = [
    "company_id",
    "company_name",
    "is_benchmark",
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "debt_to_equity",
    "interest_coverage",
]


available_columns = [column for column in table_columns if column in group_df.columns]


comparison_df = group_df[available_columns].copy()


comparison_df = comparison_df.rename(
    columns={
        "company_id": "Ticker",
        "company_name": "Company",
        "is_benchmark": "Benchmark",
        "return_on_equity_pct": "ROE %",
        "return_on_capital_employed_pct": "ROCE %",
        "net_profit_margin_pct": "Net Profit Margin %",
        "operating_profit_margin_pct": "OPM %",
        "revenue_cagr_5yr": "Revenue CAGR %",
        "pat_cagr_5yr": "PAT CAGR %",
        "debt_to_equity": "D/E",
        "interest_coverage": "Interest Coverage",
    }
)


# ============================================================
# FORMAT BENCHMARK
# ============================================================

comparison_df["Benchmark"] = comparison_df["Benchmark"].map({1: "⭐ Benchmark", 0: ""})


# ============================================================
# DISPLAY TABLE
# ============================================================


def highlight_benchmark(row):
    "Highlight benchmark."

    if row["Benchmark"] == "⭐ Benchmark":

        return ["background-color: #FFF2CC" for _ in row]

    return ["" for _ in row]


styled_df = comparison_df.style.apply(highlight_benchmark, axis=1)


st.dataframe(styled_df, use_container_width=True, hide_index=True)


# ============================================================
# PEER GROUP INFORMATION
# ============================================================

st.markdown("---")

st.caption(f"Peer group: {selected_group} | " f"Companies: {len(comparison_df)}")
