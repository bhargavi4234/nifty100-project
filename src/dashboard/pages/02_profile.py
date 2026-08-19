import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.utils.db import (
    get_companies,
    get_pl,
    get_pros_cons,
    get_ratios,
)

# ============================================================
# PAGE TITLE
# ============================================================

st.title("🏢 Company Profile")


# ============================================================
# LOAD COMPANIES
# ============================================================

companies = get_companies()


# ============================================================
# COMPANY SEARCH
# ============================================================

st.subheader("Search Company")

search_text = st.text_input(
    "Type company name or NSE ticker", placeholder="Example: TCS or Tata Consultancy"
)


# ============================================================
# SEARCH / AUTOCOMPLETE
# ============================================================

if search_text:

    search_lower = search_text.lower().strip()

    matches = companies[
        companies["ticker"].str.lower().str.contains(search_lower, na=False)
        | companies["company_name"].str.lower().str.contains(search_lower, na=False)
    ].copy()

else:

    matches = companies.copy()


# ============================================================
# NO MATCH
# ============================================================

if search_text and matches.empty:

    st.warning("Ticker not found — please try another.")

    st.stop()


# ============================================================
# AUTOCOMPLETE DROPDOWN
# ============================================================

if search_text:

    options = matches["ticker"].tolist()

    selected_ticker = st.selectbox(
        "Select company",
        options,
        format_func=lambda ticker: (
            f"{ticker} — "
            f"{companies.loc[companies['ticker'] == ticker, 'company_name'].iloc[0]}"
        ),
    )

else:

    selected_ticker = st.selectbox(
        "Select company",
        companies["ticker"].tolist(),
        format_func=lambda ticker: (
            f"{ticker} — "
            f"{companies.loc[companies['ticker'] == ticker, 'company_name'].iloc[0]}"
        ),
    )


# ============================================================
# SELECTED COMPANY
# ============================================================

company_row = companies[companies["ticker"] == selected_ticker]

if company_row.empty:

    st.warning("Ticker not found — please try another.")

    st.stop()


company = company_row.iloc[0]


# ============================================================
# COMPANY CARD
# ============================================================

st.markdown("---")
st.subheader("Company Information")

col1, col2 = st.columns([1, 2])

with col1:

    st.markdown(f"""
        ### {company['company_name']}

        **NSE Ticker:** `{company['ticker']}`

        **Sector:** {company['sector']}

        **Sub-sector:** {company['sub_sector']}
        """)

with col2:

    st.markdown("### About")

    about = company["about_company"]

    if pd.isna(about) or not str(about).strip():
        about = "Company description not available."

    st.write(about)


# ============================================================
# LOAD FINANCIAL DATA
# ============================================================

ratios = get_ratios(selected_ticker)
pl = get_pl(selected_ticker)


# ============================================================
# CLEAN YEAR
# ============================================================

if not ratios.empty:

    ratios = ratios.copy()

    ratios["year_number"] = ratios["year"].astype(str).str.extract(r"(\d{4})")[0]

    ratios["year_number"] = pd.to_numeric(ratios["year_number"], errors="coerce")


if not pl.empty:

    pl = pl.copy()

    pl["year_number"] = pl["year"].astype(str).str.extract(r"(\d{4})")[0]

    pl["year_number"] = pd.to_numeric(pl["year_number"], errors="coerce")


if not pl.empty:

    pl = pl.copy()

    pl["year_number"] = pl["year"].astype(str).str.extract(r"(\d{4})")[0]

    pl["year_number"] = pd.to_numeric(pl["year_number"], errors="coerce")


# ============================================================
# DATA AVAILABILITY NOTE
# ============================================================

if not ratios.empty:

    available_years = ratios["year_number"].dropna().astype(int).nunique()

    if available_years < 10:

        st.info(
            f"ℹ️ Data available for {available_years} years. "
            "Some historical financial data may be unavailable."
        )


# ============================================================
# LATEST RATIO DATA
# ============================================================


latest_ratio = pd.DataFrame()

if not ratios.empty:

    valid_ratios = ratios.dropna(subset=["year_number"]).sort_values("year_number")

    if not valid_ratios.empty:
        latest_ratio = valid_ratios.tail(1)


# ============================================================
# KPI VALUES
# ============================================================

if not latest_ratio.empty:

    row = latest_ratio.iloc[0]

    roe = row["return_on_equity_pct"]

    roce = row["return_on_capital_employed_pct"]

    npm = row["net_profit_margin_pct"]

    debt_equity = row["debt_to_equity"]

    revenue_cagr = row["revenue_cagr_5yr"]

    fcf = row["free_cash_flow_cr"]

else:

    roe = roce = npm = debt_equity = revenue_cagr = fcf = None


# ============================================================
# KPI DISPLAY
# ============================================================

st.markdown("---")
st.subheader("Key Financial Metrics")

k1, k2, k3 = st.columns(3)
k4, k5, k6 = st.columns(3)


def format_percent(value):
    "Format percent."
    if pd.isna(value):
        return "N/A"
    return f"{value:.2f}%"


def format_number(value):
    "Format number."
    if pd.isna(value):
        return "N/A"
    return f"{value:.2f}"


with k1:
    st.metric("ROE", format_percent(roe))

with k2:
    st.metric("ROCE", format_percent(roce))

with k3:
    st.metric("Net Profit Margin", format_percent(npm))

with k4:
    st.metric("D/E", format_number(debt_equity))

with k5:
    st.metric("Revenue CAGR 5yr", format_percent(revenue_cagr))

with k6:
    st.metric("FCF (Latest Year)", format_number(fcf))


# ============================================================
# REVENUE & NET PROFIT CHART
# ============================================================

st.markdown("---")
st.subheader("Revenue and Net Profit — 10 Year Trend")


if not pl.empty:

    chart_pl = pl.dropna(subset=["year_number"]).sort_values("year_number").tail(10)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(x=chart_pl["year_number"], y=chart_pl["sales"], name="Revenue")
    )

    fig.add_trace(
        go.Bar(x=chart_pl["year_number"], y=chart_pl["net_profit"], name="Net Profit")
    )

    fig.update_layout(
        xaxis_title="Year", yaxis_title="Amount", barmode="group", height=500
    )

    st.plotly_chart(fig, use_container_width=True)

else:

    st.info("Revenue and Net Profit data not available.")

# ============================================================
# ROE AND ROCE DUAL-AXIS CHART
# ============================================================

st.markdown("---")
st.subheader("ROE and ROCE — 10 Year Trend")


if not ratios.empty:

    chart_ratios = (
        ratios.dropna(subset=["year_number"]).sort_values("year_number").tail(10)
    )

    # Convert years to categorical labels
    chart_years = chart_ratios["year_number"].astype(int).astype(str)

    # Create dual-axis chart
    fig2 = go.Figure()

    # ROE - left axis
    fig2.add_trace(
        go.Scatter(
            x=chart_years,
            y=chart_ratios["return_on_equity_pct"],
            mode="lines+markers",
            name="ROE",
            yaxis="y1",
        )
    )

    # ROCE - right axis
    fig2.add_trace(
        go.Scatter(
            x=chart_years,
            y=chart_ratios["return_on_capital_employed_pct"],
            mode="lines+markers",
            name="ROCE",
            yaxis="y2",
        )
    )

    fig2.update_layout(
        xaxis={"title": "Year", "type": "category"},
        yaxis={"title": "ROE (%)", "side": "left"},
        yaxis2={"title": "ROCE (%)", "side": "right", "overlaying": "y"},
        height=500,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        margin={"l": 70, "r": 70, "t": 80, "b": 60},
    )

    st.plotly_chart(fig2, use_container_width=True)

else:

    st.info("ROE and ROCE data not available.")

# ============================================================
# PROS AND CONS
# ============================================================

st.markdown("---")
st.subheader("Pros and Cons")

pros_cons = get_pros_cons(selected_ticker)


if not pros_cons.empty:

    pros = pros_cons["pros"].dropna().tolist()
    cons = pros_cons["cons"].dropna().tolist()

    col_pros, col_cons = st.columns(2)

    with col_pros:

        st.markdown("### ✅ Pros")

        if pros:

            for item in pros:
                st.success(item)

        else:

            st.info("No pros available.")

    with col_cons:

        st.markdown("### ❌ Cons")

        if cons:

            for item in cons:
                st.error(item)

        else:

            st.info("No cons available.")

else:

    st.info("Pros and cons information not available.")
