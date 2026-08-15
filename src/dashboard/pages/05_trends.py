import sqlite3

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE TITLE
# ============================================================

st.title("📈 Trend Analysis")

st.markdown(
    "Explore the 10-year financial trends of Nifty 100 companies."
)


# ============================================================
# DATABASE
# ============================================================

DB_PATH = "data/db/nifty100.db"


@st.cache_data(ttl=600)
def load_trend_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        fr.company_id,
        c.company_name,
        fr.year,

        fr.return_on_equity_pct,
        fr.return_on_capital_employed_pct,
        fr.net_profit_margin_pct,
        fr.operating_profit_margin_pct,
        fr.debt_to_equity,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.interest_coverage,

        pl.sales,
        pl.net_profit,

        mc.market_cap_crore

    FROM financial_ratios fr

    LEFT JOIN companies c
        ON fr.company_id = c.id

    LEFT JOIN profitandloss pl
        ON fr.company_id = pl.company_id
        AND fr.year = pl.year

    LEFT JOIN market_cap mc
        ON fr.company_id = mc.company_id
        AND SUBSTR(fr.year, -4) = CAST(mc.year AS TEXT)
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


df = load_trend_data()


# ============================================================
# CHECK DATA
# ============================================================

if df.empty:

    st.warning(
        "No trend data available."
    )

    st.stop()


# ============================================================
# CLEAN YEAR
# ============================================================

df["year_number"] = (
    df["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

df["year_number"] = pd.to_numeric(
    df["year_number"],
    errors="coerce"
)


# ============================================================
# COMPANY SEARCH
# ============================================================

st.sidebar.header("Company")

search_text = st.sidebar.text_input(
    "Search company or NSE ticker",
    placeholder="Example: TCS or Tata Consultancy"
)


# ============================================================
# COMPANY LIST
# ============================================================

companies = (
    df[
        ["company_id", "company_name"]
    ]
    .drop_duplicates()
    .sort_values("company_name")
)


if search_text.strip():

    search_lower = search_text.lower().strip()

    companies = companies[
        companies["company_id"]
        .str.lower()
        .str.contains(
            search_lower,
            na=False
        )
        |
        companies["company_name"]
        .str.lower()
        .str.contains(
            search_lower,
            na=False
        )
    ]


if companies.empty:

    st.warning(
        "Company not found — please try another ticker or company name."
    )

    st.stop()


# ============================================================
# COMPANY SELECTOR
# ============================================================

company_options = {
    row["company_id"]:
        f"{row['company_id']} — {row['company_name']}"
    for _, row in companies.iterrows()
}


selected_company = st.sidebar.selectbox(
    "Select Company",
    list(company_options.keys()),
    format_func=lambda x: company_options[x]
)


# ============================================================
# METRIC OPTIONS
# ============================================================

metric_options = {
    "Revenue / Sales": "sales",
    "Net Profit": "net_profit",
    "ROE": "return_on_equity_pct",
    "ROCE": "return_on_capital_employed_pct",
    "Net Profit Margin": "net_profit_margin_pct",
    "Operating Profit Margin": "operating_profit_margin_pct",
    "Debt to Equity": "debt_to_equity",
    "Revenue CAGR 5yr": "revenue_cagr_5yr",
    "PAT CAGR 5yr": "pat_cagr_5yr",
    "Interest Coverage": "interest_coverage",
}


selected_metrics = st.sidebar.multiselect(
    "Select up to 3 metrics",
    options=list(metric_options.keys()),
    default=[
        "Revenue / Sales",
        "Net Profit"
    ],
    max_selections=3
)


if not selected_metrics:

    st.info(
        "Select at least one metric from the sidebar."
    )

    st.stop()


# ============================================================
# FILTER COMPANY
# ============================================================

company_df = df[
    df["company_id"] == selected_company
].copy()


company_df = (
    company_df
    .sort_values("year_number")
    .drop_duplicates(
        subset=["year_number"],
        keep="last"
    )
    .tail(10)
)


if company_df.empty:

    st.warning(
        "No historical data available for this company."
    )

    st.stop()


# ============================================================
# COMPANY HEADER
# ============================================================

company_name = company_df[
    "company_name"
].iloc[0]

st.subheader(
    f"{company_name} ({selected_company})"
)


# ============================================================
# CREATE CHART
# ============================================================

fig = go.Figure()


for metric_name in selected_metrics:

    column_name = metric_options[
        metric_name
    ]

    if column_name not in company_df.columns:
        continue

    values = pd.to_numeric(
        company_df[column_name],
        errors="coerce"
    )

    if values.notna().sum() == 0:
        continue

yoy_values = values.pct_change() * 100

fig.add_trace(
    go.Scatter(
        x=company_df["year_number"],
        y=values,
        mode="lines+markers+text",
        name=metric_name,
        text=[
            ""
            if pd.isna(value)
            else (
                f"{value:.1f}<br>"
                f"YoY: {yoy_values.iloc[i]:+.2f}%"
                if not pd.isna(yoy_values.iloc[i])
                else f"{value:.1f}"
            )
            for i, value in enumerate(values)
        ],
        textposition="top center",
        hovertemplate=(
            f"<b>{metric_name}</b>"
            "<br>Year: %{x}"
            "<br>Value: %{y:.2f}"
            "<extra></extra>"
        )
    )
)


# ============================================================
# CHART LAYOUT
# ============================================================

fig.update_layout(
    title="10-Year Financial Trend",
    xaxis_title="Year",
    yaxis_title="Value",
    height=600,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# YOY % CHANGE TABLE / ANNOTATION
# ============================================================

st.markdown("---")

st.subheader(
    "📌 Year-over-Year Change"
)


yoy_df = company_df[
    ["year_number"]
].copy()


for metric_name in selected_metrics:

    column_name = metric_options[
        metric_name
    ]

    values = pd.to_numeric(
        company_df[column_name],
        errors="coerce"
    )

    yoy = values.pct_change() * 100

    yoy_df[metric_name] = yoy.round(2)


yoy_df = yoy_df.rename(
    columns={
        "year_number": "Year"
    }
)


st.dataframe(
    yoy_df,
    use_container_width=True,
    hide_index=True
)


st.caption(
    "YoY % change compares each year's value with the previous available year."
)