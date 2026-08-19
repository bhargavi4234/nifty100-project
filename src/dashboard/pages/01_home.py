import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import (
    get_companies,
    get_sectors,
)

# ============================================================
# PAGE TITLE
# ============================================================

st.title("🏠 Nifty 100 Analytics")
st.markdown("### Market Overview")


# ============================================================
# LOAD DATA
# ============================================================

companies = get_companies()
sectors = get_sectors()


# ============================================================
# YEAR SELECTOR
# ============================================================

years = list(range(2019, 2025))

selected_year = st.sidebar.selectbox("Select Year", years, index=len(years) - 1)

st.sidebar.markdown("---")
st.sidebar.write(f"Selected year: **{selected_year}**")


# ============================================================
# PREPARE YEAR DATA
# ============================================================

from src.dashboard.utils.db import get_ratios


@st.cache_data(ttl=600)
def get_all_ratios_for_year(year):
    """Load ratio data for all companies for a selected year."""

    query_results = []

    for ticker in companies["ticker"]:
        data = get_ratios(ticker)

        if data.empty:
            continue

        # Extract year from values such as:
        # Dec 2019, Mar 2020, etc.
        data = data.copy()
        data["year_number"] = data["year"].astype(str).str.extract(r"(\d{4})")[0]

        data["year_number"] = pd.to_numeric(data["year_number"], errors="coerce")

        filtered = data[data["year_number"] == year]

        if not filtered.empty:
            # Use latest duplicate if duplicates exist
            filtered = filtered.tail(1)
            query_results.append(filtered)

    if not query_results:
        return pd.DataFrame()

    return pd.concat(query_results, ignore_index=True)


ratios_year = get_all_ratios_for_year(selected_year)


# ============================================================
# KPI CALCULATIONS
# ============================================================

if ratios_year.empty:

    st.warning(f"No financial ratio data available for {selected_year}.")

else:

    average_roe = ratios_year["return_on_equity_pct"].mean()

    median_pe = None

    # P/E is not present in financial_ratios.
    # Therefore we display N/A until the valuation module
    # creates the required valuation data.
    median_pe_text = "N/A"

    median_de = ratios_year["debt_to_equity"].median()

    total_companies = len(companies)

    median_revenue_cagr = ratios_year["revenue_cagr_5yr"].median()

    debt_free_count = ratios_year["debt_to_equity"].fillna(0).eq(0).sum()

    # ========================================================
    # KPI TILES
    # ========================================================

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Average ROE", f"{average_roe:.2f}%")

    with col2:
        st.metric("Median P/E", median_pe_text)

    with col3:
        st.metric("Median D/E", f"{median_de:.2f}")

    with col4:
        st.metric("Total Companies", f"{total_companies}")

    with col5:
        if pd.isna(median_revenue_cagr):
            value = "N/A"
        else:
            value = f"{median_revenue_cagr:.2f}%"

        st.metric("Median Revenue CAGR 5yr", value)

    with col6:
        st.metric("Debt-Free Companies", f"{debt_free_count}")


# ============================================================
# SECTOR BREAKDOWN
# ============================================================

st.markdown("---")
st.subheader("📊 Sector Breakdown")


sector_counts = (
    sectors.groupby("broad_sector")
    .size()
    .reset_index(name="company_count")
    .sort_values("company_count", ascending=False)
)


fig_sector = px.pie(
    sector_counts,
    names="broad_sector",
    values="company_count",
    hole=0.55,
    title=f"Nifty 100 Companies by Sector ({selected_year})",
)

fig_sector.update_traces(textposition="inside", textinfo="percent+label")

fig_sector.update_layout(height=550, legend_title="Sector")

st.plotly_chart(fig_sector, use_container_width=True)


# ============================================================
# TOP 5 COMPANIES BY COMPOSITE QUALITY SCORE
# ============================================================

st.markdown("---")
st.subheader("🏆 Top 5 Companies by Composite Quality Score")


if not ratios_year.empty:

    top5 = ratios_year[["company_id", "composite_quality_score"]].copy()

    top5 = top5.merge(
        companies[["ticker", "company_name", "sector"]],
        left_on="company_id",
        right_on="ticker",
        how="left",
    )

    top5 = top5.sort_values("composite_quality_score", ascending=False).head(5)

    top5 = top5[["company_id", "company_name", "sector", "composite_quality_score"]]

    top5.columns = ["Ticker", "Company", "Sector", "Quality Score"]

    st.dataframe(top5, use_container_width=True, hide_index=True)

else:

    st.info("No quality score data available for this year.")


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(f"Nifty 100 Analytics | Data Year: {selected_year}")
