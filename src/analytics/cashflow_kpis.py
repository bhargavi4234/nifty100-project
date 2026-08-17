import math
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

DB_PATH = Path("data/db/nifty100.db")

OUTPUT_XLSX = Path(
    "output/cashflow_intelligence.xlsx"
)

OUTPUT_ALERTS = Path(
    "output/distress_alerts.csv"
)


# ============================================================
# HELPERS
# ============================================================

def extract_year(value):
    """Extract year from values such as 'Mar 2024'."""

    if pd.isna(value):
        return None

    text = str(value)

    import re

    match = re.search(
        r"\b(19|20)\d{2}\b",
        text
    )

    if not match:
        return None

    return int(match.group(0))


def prepare_year_column(df):
    """Add numeric year and remove TTM/non-year rows."""

    df = df.copy()

    df["year_num"] = df["year"].apply(
        extract_year
    )

    df = df[
        df["year_num"].notna()
    ].copy()

    return df


def deduplicate_years(df):
    """
    Remove duplicate company/year records.

    The database contains duplicate records for some
    company-year combinations. Keep the last occurrence.
    """

    df = df.sort_values(
        [
            "company_id",
            "year_num",
        ]
    )

    return df.drop_duplicates(
        subset=[
            "company_id",
            "year_num",
        ],
        keep="last",
    )


def safe_float(value):
    """Convert a value to float or return NaN."""

    try:
        if pd.isna(value):
            return np.nan

        return float(value)

    except (TypeError, ValueError):
        return np.nan


# ============================================================
# CAGR
# ============================================================

def calculate_cagr(
    start_value,
    end_value,
    years,
):
    """
    Calculate CAGR.

    CAGR is not meaningful when the starting or ending
    FCF is zero/negative, so return NaN in those cases.
    """

    if (
        pd.isna(start_value)
        or pd.isna(end_value)
        or start_value <= 0
        or end_value <= 0
        or years <= 0
    ):
        return np.nan

    return (
        (
            float(end_value)
            / float(start_value)
        )
        ** (1.0 / years)
        - 1
    ) * 100


def get_fcf_cagr_5yr(
    company_fcf,
):
    """
    Calculate 5-year FCF CAGR.

    Prefer exactly five years between observations.
    """

    data = company_fcf[
        ["year_num", "free_cash_flow_cr"]
    ].dropna()

    if len(data) < 2:
        return np.nan

    data = data.sort_values(
        "year_num"
    )

    latest = data.iloc[-1]

    target_year = (
        int(latest["year_num"]) - 5
    )

    exact = data[
        data["year_num"] == target_year
    ]

    if not exact.empty:

        start = exact.iloc[-1]

        return calculate_cagr(
            start["free_cash_flow_cr"],
            latest["free_cash_flow_cr"],
            5,
        )

    # Fallback: use earliest observation that is
    # approximately five years before latest.
    candidates = data[
        data["year_num"]
        <= latest["year_num"] - 4
    ]

    if candidates.empty:
        return np.nan

    start = candidates.iloc[-1]

    years = (
        latest["year_num"]
        - start["year_num"]
    )

    return calculate_cagr(
        start["free_cash_flow_cr"],
        latest["free_cash_flow_cr"],
        years,
    )


# ============================================================
# LOAD DATABASE
# ============================================================

def load_data():

    con = sqlite3.connect(
        DB_PATH
    )

    companies = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        """,
        con,
    )

    sectors = pd.read_sql_query(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        con,
    )

    cashflow = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity,
            net_cash_flow
        FROM cashflow
        """,
        con,
    )

    ratios = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            free_cash_flow_cr,
            cash_from_operations_cr
        FROM financial_ratios
        """,
        con,
    )

    pnl = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            sales,
            net_profit
        FROM profitandloss
        """,
        con,
    )

    balance = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            borrowings
        FROM balancesheet
        """,
        con,
    )

    con.close()

    return (
        companies,
        sectors,
        cashflow,
        ratios,
        pnl,
        balance,
    )


# ============================================================
# CFO QUALITY
# ============================================================

def calculate_cfo_quality(
    company_id,
    ratios,
    pnl,
):
    """
    CFO Quality Score = average CFO/PAT over available
    five annual observations.

    Labels:
        > 1.0       High Quality
        0.5 - 1.0   Moderate
        < 0.5       Accrual Risk
    """

    cfo = ratios[
        ratios["company_id"] == company_id
    ][
        [
            "year_num",
            "cash_from_operations_cr",
        ]
    ].copy()

    pat = pnl[
        pnl["company_id"] == company_id
    ][
        [
            "year_num",
            "net_profit",
        ]
    ].copy()

    merged = pd.merge(
        cfo,
        pat,
        on="year_num",
        how="inner",
    )

    merged = merged.dropna()

    merged = merged[
        merged["net_profit"] != 0
    ]

    if merged.empty:
        return np.nan, "Insufficient Data"

    merged = merged.sort_values(
        "year_num"
    ).tail(5)

    merged["cfo_pat_ratio"] = (
        merged["cash_from_operations_cr"]
        / merged["net_profit"]
    )

    score = merged[
        "cfo_pat_ratio"
    ].mean()

    if pd.isna(score):
        return np.nan, "Insufficient Data"

    if score > 1.0:
        label = "High Quality"

    elif score >= 0.5:
        label = "Moderate"

    else:
        label = "Accrual Risk"

    return score, label


# ============================================================
# CAPEX INTENSITY
# ============================================================

def calculate_capex_intensity(
    company_id,
    cashflow,
    pnl,
):
    """
    CapEx intensity =
        abs(investing_activity) / sales * 100

    Uses the latest annual year.
    """

    cf = cashflow[
        cashflow["company_id"] == company_id
    ].copy()

    sales = pnl[
        pnl["company_id"] == company_id
    ].copy()

    merged = pd.merge(
        cf[
            [
                "year_num",
                "investing_activity",
            ]
        ],
        sales[
            [
                "year_num",
                "sales",
            ]
        ],
        on="year_num",
        how="inner",
    )

    merged = merged.dropna()

    if merged.empty:
        return np.nan, "Insufficient Data"

    latest = merged.sort_values(
        "year_num"
    ).iloc[-1]

    if latest["sales"] == 0:
        return np.nan, "Insufficient Data"

    intensity = (
        abs(latest["investing_activity"])
        / abs(latest["sales"])
    ) * 100

    if intensity < 3:
        label = "Asset Light"

    elif intensity <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return intensity, label


# ============================================================
# FCF CONVERSION
# ============================================================

def calculate_fcf_conversion(
    company_id,
    ratios,
    pnl,
):
    """
    FCF conversion =
        FCF / PAT * 100

    Uses latest annual FCF and PAT.
    """

    fcf = ratios[
        ratios["company_id"] == company_id
    ][
        [
            "year_num",
            "free_cash_flow_cr",
        ]
    ]

    pat = pnl[
        pnl["company_id"] == company_id
    ][
        [
            "year_num",
            "net_profit",
        ]
    ]

    merged = pd.merge(
        fcf,
        pat,
        on="year_num",
        how="inner",
    ).dropna()

    if merged.empty:
        return np.nan

    latest = merged.sort_values(
        "year_num"
    ).iloc[-1]

    if latest["net_profit"] == 0:
        return np.nan

    return (
        latest["free_cash_flow_cr"]
        / latest["net_profit"]
    ) * 100


# ============================================================
# DISTRESS SIGNAL
# ============================================================

def calculate_distress(
    company_id,
    cashflow,
    pnl,
):
    """
    Distress signal:

        CFO < 0
        AND
        CFF > 0

    Uses latest annual cash-flow year.
    """

    cf = cashflow[
        cashflow["company_id"] == company_id
    ].copy()

    if cf.empty:
        return False, None

    latest = cf.sort_values(
        "year_num"
    ).iloc[-1]

    cfo = latest[
        "operating_activity"
    ]

    cff = latest[
        "financing_activity"
    ]

    flag = (
        pd.notna(cfo)
        and pd.notna(cff)
        and cfo < 0
        and cff > 0
    )

    return bool(flag), latest


# ============================================================
# DELEVERAGING
# ============================================================

def calculate_deleveraging(
    company_id,
    cashflow,
    balance,
):
    """
    Deleveraging:

        CFF < 0
        AND
        borrowings declining year-over-year

    Uses the latest annual year.
    """

    cf = cashflow[
        cashflow["company_id"] == company_id
    ].copy()

    bs = balance[
        balance["company_id"] == company_id
    ].copy()

    merged = pd.merge(
        cf[
            [
                "year_num",
                "financing_activity",
            ]
        ],
        bs[
            [
                "year_num",
                "borrowings",
            ]
        ],
        on="year_num",
        how="inner",
    ).dropna()

    if len(merged) < 2:
        return False

    merged = merged.sort_values(
        "year_num"
    )

    latest = merged.iloc[-1]
    previous = merged.iloc[-2]

    return bool(
        latest["financing_activity"] < 0
        and latest["borrowings"]
        < previous["borrowings"]
    )


# ============================================================
# CAPITAL ALLOCATION
# ============================================================

def calculate_capital_allocation(
    company_id,
    cashflow,
    balance,
    pnl,
):
    """
    Classify latest capital allocation pattern.

    Priority:
        1. Deleveraging
        2. Shareholder Returns
        3. Growth Investment
        4. Cash Accumulation
        5. Balanced

    This classification is based on the available
    financing/investing cash-flow signals.
    """

    cf = cashflow[
        cashflow["company_id"] == company_id
    ].copy()

    if cf.empty:
        return "Insufficient Data"

    latest = cf.sort_values(
        "year_num"
    ).iloc[-1]

    cff = latest[
        "financing_activity"
    ]

    investing = latest[
        "investing_activity"
    ]

    deleveraging = calculate_deleveraging(
        company_id,
        cashflow,
        balance,
    )

    if deleveraging:
        return "Deleveraging"

    # Positive financing activity means capital is being
    # raised. Negative financing activity means capital
    # is being returned/repaid.
    if (
        pd.notna(cff)
        and cff < 0
    ):
        return "Shareholder Returns / Debt Repayment"

    if (
        pd.notna(investing)
        and investing < 0
    ):
        return "Growth Investment"

    if (
        pd.notna(cff)
        and cff > 0
    ):
        return "External Financing"

    return "Balanced"


# ============================================================
# MAIN
# ============================================================

def generate():

    print("=" * 75)
    print("DAY 31 - CASH FLOW INTELLIGENCE")
    print("=" * 75)

    (
        companies,
        sectors,
        cashflow,
        ratios,
        pnl,
        balance,
    ) = load_data()

    print(
        f"Companies loaded : {len(companies)}"
    )

    # --------------------------------------------------------
    # Prepare data
    # --------------------------------------------------------

    cashflow = prepare_year_column(
        cashflow
    )

    ratios = prepare_year_column(
        ratios
    )

    pnl = prepare_year_column(
        pnl
    )

    balance = prepare_year_column(
        balance
    )

    cashflow = deduplicate_years(
        cashflow
    )

    ratios = deduplicate_years(
        ratios
    )

    pnl = deduplicate_years(
        pnl
    )

    balance = deduplicate_years(
        balance
    )

    # --------------------------------------------------------
    # Sector lookup
    # --------------------------------------------------------

    sector_map = (
        sectors
        .drop_duplicates(
            "company_id"
        )
        .set_index(
            "company_id"
        )["broad_sector"]
        .to_dict()
    )

    # --------------------------------------------------------
    # Generate intelligence
    # --------------------------------------------------------

    rows = []

    distress_rows = []

    for company_id in companies[
        "company_id"
    ].astype(str):

        sector = sector_map.get(
            company_id,
            "Unknown",
        )

        # ------------------------------
        # CFO Quality
        # ------------------------------

        cfo_quality_score, cfo_quality_label = (
            calculate_cfo_quality(
                company_id,
                ratios,
                pnl,
            )
        )

        # ------------------------------
        # CapEx Intensity
        # ------------------------------

        capex_intensity, capex_label = (
            calculate_capex_intensity(
                company_id,
                cashflow,
                pnl,
            )
        )

        # ------------------------------
        # FCF CAGR
        # ------------------------------

        company_fcf = ratios[
            ratios["company_id"]
            == company_id
        ].copy()

        fcf_cagr = get_fcf_cagr_5yr(
            company_fcf
        )

        # ------------------------------
        # FCF Conversion
        # ------------------------------

        fcf_conversion = (
            calculate_fcf_conversion(
                company_id,
                ratios,
                pnl,
            )
        )

        # ------------------------------
        # Distress
        # ------------------------------

        distress_flag, latest_cf = (
            calculate_distress(
                company_id,
                cashflow,
                pnl,
            )
        )

        # ------------------------------
        # Deleveraging
        # ------------------------------

        deleveraging_flag = (
            calculate_deleveraging(
                company_id,
                cashflow,
                balance,
            )
        )

        # ------------------------------
        # Capital Allocation
        # ------------------------------

        capital_allocation = (
            calculate_capital_allocation(
                company_id,
                cashflow,
                balance,
                pnl,
            )
        )

        rows.append(
            {
                "company_id": company_id,
                "sector": sector,
                "cfo_quality_score": (
                    round(
                        cfo_quality_score,
                        4,
                    )
                    if pd.notna(
                        cfo_quality_score
                    )
                    else np.nan
                ),
                "cfo_quality_label": (
                    cfo_quality_label
                ),
                "capex_intensity_pct": (
                    round(
                        capex_intensity,
                        4,
                    )
                    if pd.notna(
                        capex_intensity
                    )
                    else np.nan
                ),
                "capex_label": capex_label,
                "fcf_cagr_5yr": (
                    round(
                        fcf_cagr,
                        4,
                    )
                    if pd.notna(fcf_cagr)
                    else np.nan
                ),
                "fcf_conversion_pct": (
                    round(
                        fcf_conversion,
                        4,
                    )
                    if pd.notna(
                        fcf_conversion
                    )
                    else np.nan
                ),
                "distress_flag": (
                    distress_flag
                ),
                "deleveraging_flag": (
                    deleveraging_flag
                ),
                "capital_allocation_label": (
                    capital_allocation
                ),
            }
        )

        # ------------------------------
        # Distress alert
        # ------------------------------

        if (
            distress_flag
            and latest_cf is not None
        ):

            year = latest_cf[
                "year_num"
            ]

            cfo = latest_cf[
                "operating_activity"
            ]

            cff = latest_cf[
                "financing_activity"
            ]

            # Find PAT for same/latest year.
            company_pnl = pnl[
                pnl["company_id"]
                == company_id
            ]

            company_pnl = company_pnl[
                company_pnl["year_num"]
                == year
            ]

            if company_pnl.empty:
                latest_pat = np.nan
            else:
                latest_pat = company_pnl.iloc[0][
                    "net_profit"
                ]

            distress_rows.append(
                {
                    "company_id": company_id,
                    "year": int(year),
                    "cfo_value": cfo,
                    "cff_value": cff,
                    "latest_net_profit": latest_pat,
                }
            )

    # ========================================================
    # OUTPUT DATAFRAME
    # ========================================================

    intelligence = pd.DataFrame(
        rows,
        columns=[
            "company_id",
            "sector",
            "cfo_quality_score",
            "cfo_quality_label",
            "capex_intensity_pct",
            "capex_label",
            "fcf_cagr_5yr",
            "fcf_conversion_pct",
            "distress_flag",
            "deleveraging_flag",
            "capital_allocation_label",
        ],
    )

    alerts = pd.DataFrame(
        distress_rows,
        columns=[
            "company_id",
            "year",
            "cfo_value",
            "cff_value",
            "latest_net_profit",
        ],
    )

    # ========================================================
    # SAVE OUTPUTS
    # ========================================================

    OUTPUT_XLSX.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    intelligence.to_excel(
        OUTPUT_XLSX,
        index=False,
    )

    alerts.to_csv(
        OUTPUT_ALERTS,
        index=False,
    )

    # ========================================================
    # VERIFICATION
    # ========================================================

    print()
    print("=" * 75)
    print("DAY 31 VERIFICATION")
    print("=" * 75)

    print(
        f"Companies expected : {len(companies)}"
    )

    print(
        f"Companies output   : {len(intelligence)}"
    )

    print(
        f"Distress alerts    : {len(alerts)}"
    )

    print(
        "CFO quality labels:"
    )

    print(
        intelligence[
            "cfo_quality_label"
        ].value_counts(
            dropna=False
        ).to_string()
    )

    print()
    print(
        "CapEx labels:"
    )

    print(
        intelligence[
            "capex_label"
        ].value_counts(
            dropna=False
        ).to_string()
    )

    print()
    print(
        "Distress flags:",
        int(
            intelligence[
                "distress_flag"
            ].sum()
        ),
    )

    print(
        "Deleveraging flags:",
        int(
            intelligence[
                "deleveraging_flag"
            ].sum()
        ),
    )

    print()
    print(
        "Capital allocation:"
    )

    print(
        intelligence[
            "capital_allocation_label"
        ].value_counts(
            dropna=False
        ).to_string()
    )

    print()
    print(
        f"Excel output : {OUTPUT_XLSX}"
    )

    print(
        f"Alerts output: {OUTPUT_ALERTS}"
    )

    # --------------------------------------------------------
    # Missing-data report
    # --------------------------------------------------------

    print()
    print(
        "Missing CFO quality:",
        int(
            intelligence[
                "cfo_quality_score"
            ].isna().sum()
        ),
    )

    print(
        "Missing CapEx intensity:",
        int(
            intelligence[
                "capex_intensity_pct"
            ].isna().sum()
        ),
    )

    print(
        "Missing FCF CAGR:",
        int(
            intelligence[
                "fcf_cagr_5yr"
            ].isna().sum()
        ),
    )

    print(
        "Missing FCF conversion:",
        int(
            intelligence[
                "fcf_conversion_pct"
            ].isna().sum()
        ),
    )

    print()
    print(
        "STATUS: Day 31 cash-flow intelligence generated."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    generate()