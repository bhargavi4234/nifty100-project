import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE TITLE
# ============================================================

st.title("🏭 Sector Analysis")

st.markdown(
    "Explore Nifty 100 companies by sector using revenue, "
    "ROE and market capitalization."
)


# ============================================================
# DATABASE
# ============================================================

DB_PATH = "data/db/nifty100.db"


@st.cache_data(ttl=600)
def load_sector_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        c.id AS company_id,
        c.company_name,

        s.broad_sector,
        s.sub_sector,

        fr.year,
        fr.return_on_equity_pct,

        pl.sales,

        mc.market_cap_crore

    FROM companies c

    LEFT JOIN sectors s
        ON c.id = s.company_id

    LEFT JOIN financial_ratios fr
        ON c.id = fr.company_id

    LEFT JOIN profitandloss pl
        ON c.id = pl.company_id
        AND fr.year = pl.year

    LEFT JOIN market_cap mc
        ON c.id = mc.company_id
        AND SUBSTR(fr.year, -4) = CAST(mc.year AS TEXT)
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


df = load_sector_data()


# ============================================================
# CHECK DATA
# ============================================================

if df.empty:

    st.warning(
        "No sector data available."
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
# KEEP LATEST YEAR FOR EACH COMPANY
# ============================================================

df = (
    df
    .sort_values(
        ["company_id", "year_number"]
    )
    .drop_duplicates(
        subset=["company_id"],
        keep="last"
    )
    .reset_index(drop=True)
)


# ============================================================
# REMOVE INVALID ROWS
# ============================================================

df["sales"] = pd.to_numeric(
    df["sales"],
    errors="coerce"
)

df["return_on_equity_pct"] = pd.to_numeric(
    df["return_on_equity_pct"],
    errors="coerce"
)

df["market_cap_crore"] = pd.to_numeric(
    df["market_cap_crore"],
    errors="coerce"
)


# ============================================================
# SECTOR DROPDOWN
# ============================================================

st.sidebar.header("Sector")

sector_options = sorted(
    df["broad_sector"]
    .dropna()
    .unique()
    .tolist()
)

selected_sector = st.sidebar.selectbox(
    "Select Sector",
    sector_options
)


# ============================================================
# FILTER SELECTED SECTOR
# ============================================================

sector_df = df[
    df["broad_sector"] == selected_sector
].copy()


if sector_df.empty:

    st.warning(
        "No companies found for this sector."
    )

    st.stop()


# ============================================================
# SECTOR HEADER
# ============================================================

st.subheader(
    f"{selected_sector} — Company Analysis"
)

st.caption(
    f"{len(sector_df)} companies in this sector"
)


# ============================================================
# BUBBLE CHART
# ============================================================

st.markdown("---")

st.subheader(
    "📊 Revenue vs ROE — Market Cap"
)


bubble_df = sector_df.dropna(
    subset=[
        "sales",
        "return_on_equity_pct",
        "market_cap_crore",
        "sub_sector"
    ]
).copy()

# Cap extreme ROE values only for visualization.
# Original database values are not modified.
bubble_df["roe_display"] = bubble_df[
    "return_on_equity_pct"
].clip(lower=-100, upper=100)


if bubble_df.empty:

    st.info(
        "Not enough data available to create the bubble chart."
    )

else:

    fig = px.scatter(
        bubble_df,
        x="sales",
        y="roe_display",
        size="market_cap_crore",
        color="sub_sector",
        hover_name="company_name",
        hover_data={
            "company_id": True,
            "sales": ":,.0f",
            "roe_display": ":.2f",
            "market_cap_crore": ":,.0f",
            "sub_sector": True
        },
        labels={
            "sales": "Revenue / Sales (₹ Cr)",
            "roe_display": "ROE (%)",
            "market_cap_crore": "Market Cap (₹ Cr)",
            "sub_sector": "Sub-sector"
        },
        title=(
            f"{selected_sector}: Revenue vs ROE"
        ),
        size_max=60
    )

    fig.update_layout(
        height=650
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# SECTOR MEDIAN KPI
# ============================================================

st.markdown("---")

st.subheader(
    "📈 Sector Median KPIs"
)


median_columns = {
    "Revenue / Sales": "sales",
    "ROE": "return_on_equity_pct",
    "Market Cap": "market_cap_crore"
}


median_values = {}

for label, column in median_columns.items():

    median_values[label] = sector_df[
        column
    ].median()


median_df = pd.DataFrame(
    {
        "KPI": list(
            median_values.keys()
        ),
        "Median": list(
            median_values.values()
        )
    }
)


# ============================================================
# MEDIAN BAR CHART
# ============================================================

fig_median = px.bar(
    median_df,
    x="KPI",
    y="Median",
    text="Median",
    title=(
        f"{selected_sector}: Median KPIs"
    )
)

fig_median.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig_median.update_layout(
    height=450,
    yaxis_title="Median Value",
    xaxis_title=""
)

st.plotly_chart(
    fig_median,
    use_container_width=True
)


# ============================================================
# COMPANY TABLE
# ============================================================

st.markdown("---")

st.subheader(
    "Companies in Selected Sector"
)


table_df = sector_df[
    [
        "company_id",
        "company_name",
        "sub_sector",
        "sales",
        "return_on_equity_pct",
        "market_cap_crore"
    ]
].copy()


table_df = table_df.rename(
    columns={
        "company_id": "Ticker",
        "company_name": "Company",
        "sub_sector": "Sub-sector",
        "sales": "Revenue / Sales",
        "return_on_equity_pct": "ROE %",
        "market_cap_crore": "Market Cap (₹ Cr)"
    }
)


st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)