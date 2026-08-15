import sqlite3

import numpy as np
import pandas as pd
import streamlit as st

from src.screener.engine import apply_filters
from src.screener.presets import PRESETS


# ============================================================
# PAGE TITLE
# ============================================================

st.title("🔎 Stock Screener")

st.markdown(
    "Filter Nifty 100 companies using financial quality, "
    "growth, valuation and leverage metrics."
)


# ============================================================
# LOAD SCREENING DATA
# ============================================================

DB_PATH = "data/db/nifty100.db"


@st.cache_data(ttl=600)
def load_screener_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        fr.*,

        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct,

        pl.sales,
        pl.net_profit,

        s.broad_sector,

        c.company_name

    FROM financial_ratios fr

    LEFT JOIN market_cap mc
        ON fr.company_id = mc.company_id
        AND SUBSTR(fr.year, -4) = CAST(mc.year AS TEXT)

    LEFT JOIN profitandloss pl
        ON fr.company_id = pl.company_id
        AND fr.year = pl.year

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id

    LEFT JOIN companies c
        ON fr.company_id = c.id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


df = load_screener_data()


# ============================================================
# KEEP LATEST YEAR FOR EACH COMPANY
# ============================================================

df = df.copy()

df["year_number"] = (
    df["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

df["year_number"] = pd.to_numeric(
    df["year_number"],
    errors="coerce"
)

df = (
    df
    .sort_values(["company_id", "year_number"])
    .drop_duplicates(
        subset=["company_id"],
        keep="last"
    )
    .reset_index(drop=True)
)


# ============================================================
# DEFAULT SLIDER VALUES
# ============================================================

def numeric_min(column, default=0):
    values = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    if values.empty:
        return default

    return float(values.min())


def numeric_max(column, default=100):
    values = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    if values.empty:
        return default

    return float(values.max())


# ============================================================
# SLIDER RANGES
# ============================================================

roe_min_value = numeric_min(
    "return_on_equity_pct"
)

roe_max_value = numeric_max(
    "return_on_equity_pct"
)

de_min_value = numeric_min(
    "debt_to_equity"
)

de_max_value = numeric_max(
    "debt_to_equity"
)

fcf_min_value = numeric_min(
    "free_cash_flow_cr"
)

fcf_max_value = numeric_max(
    "free_cash_flow_cr"
)

revenue_cagr_min_value = numeric_min(
    "revenue_cagr_5yr"
)

revenue_cagr_max_value = numeric_max(
    "revenue_cagr_5yr"
)

pat_cagr_min_value = numeric_min(
    "pat_cagr_5yr"
)

pat_cagr_max_value = numeric_max(
    "pat_cagr_5yr"
)

opm_min_value = numeric_min(
    "operating_profit_margin_pct"
)

opm_max_value = numeric_max(
    "operating_profit_margin_pct"
)

pe_min_value = numeric_min(
    "pe_ratio"
)

pe_max_value = numeric_max(
    "pe_ratio"
)

pb_min_value = numeric_min(
    "pb_ratio"
)

pb_max_value = numeric_max(
    "pb_ratio"
)

dividend_min_value = numeric_min(
    "dividend_yield_pct"
)

dividend_max_value = numeric_max(
    "dividend_yield_pct"
)

icr_min_value = numeric_min(
    "interest_coverage"
)

icr_max_value = numeric_max(
    "interest_coverage"
)


# ============================================================
# SESSION STATE DEFAULTS
# ============================================================

defaults = {
    "roe_slider": roe_min_value,
    "de_slider": de_max_value,
    "fcf_slider": fcf_min_value,
    "revenue_slider": revenue_cagr_min_value,
    "pat_slider": pat_cagr_min_value,
    "opm_slider": opm_min_value,
    "pe_slider": pe_max_value,
    "pb_slider": pb_max_value,
    "dividend_slider": dividend_min_value,
    "icr_slider": icr_min_value,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# PRESET FUNCTION
# ============================================================

def apply_preset(preset_name):

    preset = PRESETS[preset_name]

    # Reset every slider to its least restrictive value first

    st.session_state["roe_slider"] = (
        preset.get(
            "roe_min",
            roe_min_value
        )
    )

    st.session_state["de_slider"] = (
        preset.get(
            "debt_equity_max",
            de_max_value
        )
    )

    st.session_state["fcf_slider"] = (
        preset.get(
            "fcf_min",
            fcf_min_value
        )
    )

    st.session_state["revenue_slider"] = (
        preset.get(
            "revenue_cagr_5yr_min",
            revenue_cagr_min_value
        )
    )

    st.session_state["pat_slider"] = (
        preset.get(
            "pat_cagr_5yr_min",
            pat_cagr_min_value
        )
    )

    st.session_state["opm_slider"] = (
        preset.get(
            "opm_min",
            opm_min_value
        )
    )

    st.session_state["pe_slider"] = (
        preset.get(
            "pe_max",
            pe_max_value
        )
    )

    st.session_state["pb_slider"] = (
        preset.get(
            "pb_max",
            pb_max_value
        )
    )

    st.session_state["dividend_slider"] = (
        preset.get(
            "dividend_yield_min",
            dividend_min_value
        )
    )

    st.session_state["icr_slider"] = (
        preset.get(
            "icr_min",
            icr_min_value
        )
    )


# ============================================================
# PRESET BUTTONS
# ============================================================

st.sidebar.header("Preset Strategies")

preset_names = [
    ("Quality", "quality_compounder"),
    ("Value", "value_pick"),
    ("Growth", "growth_accelerator"),
    ("Dividend", "dividend_champion"),
    ("Debt-Free", "debt_free_blue_chip"),
    ("Turnaround", "turnaround_watch"),
]

for i in range(0, len(preset_names), 2):

    col1, col2 = st.sidebar.columns(2)

    label1, preset1 = preset_names[i]

    with col1:
        if st.button(
            label1,
            key=f"preset_{preset1}",
            use_container_width=True
        ):
            apply_preset(preset1)
            st.rerun()

    if i + 1 < len(preset_names):

        label2, preset2 = preset_names[i + 1]

        with col2:
            if st.button(
                label2,
                key=f"preset_{preset2}",
                use_container_width=True
            ):
                apply_preset(preset2)
                st.rerun()


st.sidebar.markdown("---")


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Screening Filters")


roe_value = st.sidebar.slider(
    "ROE minimum (%)",
    min_value=float(roe_min_value),
    max_value=float(roe_max_value),
    value=float(st.session_state["roe_slider"]),
    step=0.5,
    key="roe_slider"
)


de_value = st.sidebar.slider(
    "D/E maximum",
    min_value=float(de_min_value),
    max_value=float(de_max_value),
    value=float(st.session_state["de_slider"]),
    step=0.1,
    key="de_slider"
)


fcf_value = st.sidebar.slider(
    "FCF minimum (₹ Cr)",
    min_value=float(fcf_min_value),
    max_value=float(fcf_max_value),
    value=float(st.session_state["fcf_slider"]),
    step=100.0,
    key="fcf_slider"
)


revenue_value = st.sidebar.slider(
    "Revenue CAGR minimum (%)",
    min_value=float(revenue_cagr_min_value),
    max_value=float(revenue_cagr_max_value),
    value=float(st.session_state["revenue_slider"]),
    step=1.0,
    key="revenue_slider"
)


pat_value = st.sidebar.slider(
    "PAT CAGR minimum (%)",
    min_value=float(pat_cagr_min_value),
    max_value=float(pat_cagr_max_value),
    value=float(st.session_state["pat_slider"]),
    step=1.0,
    key="pat_slider"
)


opm_value = st.sidebar.slider(
    "OPM minimum (%)",
    min_value=float(opm_min_value),
    max_value=float(opm_max_value),
    value=float(st.session_state["opm_slider"]),
    step=1.0,
    key="opm_slider"
)


pe_value = st.sidebar.slider(
    "P/E maximum",
    min_value=float(pe_min_value),
    max_value=float(pe_max_value),
    value=float(st.session_state["pe_slider"]),
    step=1.0,
    key="pe_slider"
)


pb_value = st.sidebar.slider(
    "P/B maximum",
    min_value=float(pb_min_value),
    max_value=float(pb_max_value),
    value=float(st.session_state["pb_slider"]),
    step=0.5,
    key="pb_slider"
)


dividend_value = st.sidebar.slider(
    "Dividend Yield minimum (%)",
    min_value=float(dividend_min_value),
    max_value=float(dividend_max_value),
    value=float(st.session_state["dividend_slider"]),
    step=0.5,
    key="dividend_slider"
)


icr_value = st.sidebar.slider(
    "ICR minimum",
    min_value=float(icr_min_value),
    max_value=float(icr_max_value),
    value=float(st.session_state["icr_slider"]),
    step=1.0,
    key="icr_slider"
)


# ============================================================
# BUILD FILTER DICTIONARY
# ============================================================

filters = {
    "roe_min": roe_value,
    "debt_equity_max": de_value,
    "fcf_min": fcf_value,
    "revenue_cagr_5yr_min": revenue_value,
    "pat_cagr_5yr_min": pat_value,
    "opm_min": opm_value,
    "pe_max": pe_value,
    "pb_max": pb_value,
    "dividend_yield_min": dividend_value,
    "icr_min": icr_value,
}


# ============================================================
# APPLY FILTERS
# ============================================================

try:

    results = apply_filters(
        df,
        filters
    )

except Exception as e:

    st.error(
        f"Unable to apply screener filters: {e}"
    )

    st.stop()


# ============================================================
# RESULT COUNT
# ============================================================

st.markdown("---")

st.subheader(
    f"{len(results)} companies match your filters"
)


# ============================================================
# RESULT TABLE
# ============================================================

display_columns = [
    "company_id",
    "company_name",
    "broad_sector",
    "composite_quality_score",
    "return_on_equity_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "operating_profit_margin_pct",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
    "interest_coverage",
]


available_columns = [
    column
    for column in display_columns
    if column in results.columns
]


display_df = results[available_columns].copy()


display_df = display_df.rename(
    columns={
        "company_id": "Ticker",
        "company_name": "Company",
        "broad_sector": "Sector",
        "composite_quality_score": "Quality Score",
        "return_on_equity_pct": "ROE %",
        "debt_to_equity": "D/E",
        "free_cash_flow_cr": "FCF (₹ Cr)",
        "revenue_cagr_5yr": "Revenue CAGR 5yr %",
        "pat_cagr_5yr": "PAT CAGR 5yr %",
        "operating_profit_margin_pct": "OPM %",
        "pe_ratio": "P/E",
        "pb_ratio": "P/B",
        "dividend_yield_pct": "Dividend Yield %",
        "interest_coverage": "ICR",
    }
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CSV DOWNLOAD
# ============================================================

csv_data = display_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Results as CSV",
    data=csv_data,
    file_name="screener_results.csv",
    mime="text/csv",
    use_container_width=True
)