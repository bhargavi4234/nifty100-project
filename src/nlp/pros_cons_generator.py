import re
import sqlite3
from pathlib import Path

import pandas as pd

# ============================================================
# PATHS / SETTINGS
# ============================================================

DB_PATH = Path("data/db/nifty100.db")
OUTPUT_PATH = Path("output/pros_cons_generated.csv")

CONFIDENCE_THRESHOLD = 60.0


# ============================================================
# REQUIRED TEXT
# ============================================================

PRO_TEXT = {
    "PRO_01": (
        "Consistently high return on equity above 20% "
        "demonstrates exceptional capital efficiency"
    ),
    "PRO_02": (
        "Strong free cash flow generation over 5 years "
        "signals healthy business fundamentals"
    ),
    "PRO_03": (
        "Debt-free balance sheet provides financial flexibility "
        "and eliminates interest burden"
    ),
    "PRO_04": (
        "Revenue growing at above 15% CAGR over 5 years "
        "reflects strong business momentum"
    ),
    "PRO_05": (
        "Operating profit margin above 25% indicates strong "
        "pricing power and cost discipline"
    ),
    "PRO_06": (
        "Net profit compounding at above 20% over 5 years "
        "creates significant shareholder value"
    ),
    "PRO_07": (
        "Very high interest coverage ratio reflects negligible "
        "financial stress from debt servicing"
    ),
    "PRO_08": (
        "Consistent dividend yield above 2% backed by positive " "free cash flow"
    ),
    "PRO_09": (
        "Earnings per share growing above 15% CAGR indicates "
        "strong earnings quality and compounding"
    ),
    "PRO_10": (
        "Return on equity improving for 3 consecutive years "
        "shows strengthening business quality"
    ),
    "PRO_11": (
        "Revenue growing slower than profits shows improving "
        "operating leverage and scale benefits"
    ),
    "PRO_12": (
        "Growing asset base funded by internal accruals "
        "reflects self-sustaining growth"
    ),
}


CON_TEXT = {
    "CON_01": (
        "Debt-to-equity ratio of {value:.2f} is elevated for "
        "a non-financial company and warrants monitoring"
    ),
    "CON_02": (
        "Free cash flow negative for 3 consecutive years "
        "raises concern about cash generation quality"
    ),
    "CON_03": (
        "Operating margins declining for 3 consecutive years "
        "suggest pricing or cost pressure"
    ),
    "CON_04": ("Company reported a net loss in the most recent " "financial year"),
    "CON_05": (
        "Revenue contraction over 2 consecutive years "
        "indicates demand weakness or market share loss"
    ),
    "CON_06": (
        "Interest coverage ratio below 1.5x indicates the "
        "company is at risk of not meeting its debt obligations"
    ),
    "CON_07": (
        "Dividend payout ratio above 100% means the company "
        "is paying dividends from reserves, which is unsustainable"
    ),
    "CON_08": (
        "Rising debt-to-equity ratio over 3 years suggests "
        "increasing financial leverage risk"
    ),
    "CON_09": (
        "Earnings per share declining for 3 consecutive years "
        "reflects deteriorating profitability"
    ),
    "CON_10": (
        "Return on capital employed below 10% suggests the "
        "business is not generating sufficient returns on invested capital"
    ),
    "CON_11": (
        "Net debt exceeding 3 times EBITDA is a high leverage "
        "ratio and limits financial flexibility"
    ),
    "CON_12": (
        "Revenue growing at below 5% over 5 years lags "
        "inflation and suggests limited business momentum"
    ),
}


# ============================================================
# DATABASE
# ============================================================


def load_data():
    """Load all tables required by the NLP rules."""

    con = sqlite3.connect(DB_PATH)

    companies = pd.read_sql_query(
        "SELECT * FROM companies",
        con,
    )

    ratios = pd.read_sql_query(
        "SELECT * FROM financial_ratios",
        con,
    )

    pnl = pd.read_sql_query(
        "SELECT * FROM profitandloss",
        con,
    )

    balance = pd.read_sql_query(
        "SELECT * FROM balancesheet",
        con,
    )

    cashflow = pd.read_sql_query(
        "SELECT * FROM cashflow",
        con,
    )

    sectors = pd.read_sql_query(
        "SELECT * FROM sectors",
        con,
    )

    stock_prices = pd.read_sql_query(
        "SELECT * FROM stock_prices",
        con,
    )

    con.close()

    return (
        companies,
        ratios,
        pnl,
        balance,
        cashflow,
        sectors,
        stock_prices,
    )


# ============================================================
# YEAR HELPERS
# ============================================================


def extract_year(value):
    """
    Extract a calendar year from strings such as:
        Mar 2024
        Dec 2023
        TTM

    TTM returns None.
    """

    if pd.isna(value):
        return None

    text = str(value)

    match = re.search(r"\b(19|20)\d{2}\b", text)

    if not match:
        return None

    return int(match.group(0))


def prepare_history(df):
    """Prepare historical financial data."""

    df = df.copy()

    if "year" in df.columns:
        df["year_num"] = df["year"].apply(extract_year)
    else:
        df["year_num"] = None

    df = df.drop_duplicates()

    return df.sort_values(
        ["company_id", "year_num"],
        na_position="last",
    )


def latest_annual(df, company_id):
    """
    Get latest annual record.

    TTM is deliberately excluded because the rules refer
    to financial years/latest year rather than TTM.
    """

    company = df[df["company_id"].astype(str) == str(company_id)].copy()

    company = company[company["year_num"].notna()]

    if company.empty:
        return None

    company = company.sort_values("year_num")

    return company.iloc[-1]


def historical_annual(df, company_id):
    """Return annual records only, excluding TTM."""

    company = df[df["company_id"].astype(str) == str(company_id)].copy()

    company = company[company["year_num"].notna()]

    company = company.sort_values("year_num")

    company = company.drop_duplicates(
        subset=["year_num"],
        keep="last",
    )

    return company


# ============================================================
# CAGR
# ============================================================


def calculate_cagr(start_value, end_value, years):
    """Calculate CAGR percentage."""

    if (
        pd.isna(start_value)
        or pd.isna(end_value)
        or start_value <= 0
        or end_value <= 0
        or years <= 0
    ):
        return None

    return ((float(end_value) / float(start_value)) ** (1.0 / years) - 1.0) * 100.0


def calculate_5yr_cagr(
    df,
    company_id,
    column,
):
    """
    Calculate 5-year CAGR from the earliest/latest
    annual observations available within a 5-year span.

    For example:
        Mar 2019 -> Mar 2024
    """

    hist = historical_annual(
        df,
        company_id,
    )

    hist = hist.dropna(subset=["year_num", column])

    if len(hist) < 2:
        return None

    rows = hist[["year_num", column]].dropna()

    latest = rows.iloc[-1]

    # Prefer exactly five years before latest.
    target_year = int(latest["year_num"]) - 5

    exact = rows[rows["year_num"] == target_year]

    if not exact.empty:
        start = exact.iloc[-1]

        return calculate_cagr(
            start[column],
            latest[column],
            5,
        )

    # Otherwise find the closest observation at least
    # four years before the latest.
    candidates = rows[rows["year_num"] <= latest["year_num"] - 4]

    if candidates.empty:
        return None

    start = candidates.iloc[-1]

    actual_years = latest["year_num"] - start["year_num"]

    return calculate_cagr(
        start[column],
        latest[column],
        actual_years,
    )


# ============================================================
# CONFIDENCE
# ============================================================


def confidence_above(
    value,
    threshold,
    max_extra,
):
    """Confidence for values above a threshold."""

    if value is None or pd.isna(value):
        return 0.0

    value = float(value)

    if value <= threshold:
        return 0.0

    extra = value - threshold

    return round(
        min(
            100.0,
            65.0 + (extra / max_extra) * 35.0,
        ),
        2,
    )


def confidence_below(
    value,
    threshold,
    max_extra,
):
    """Confidence for values below a threshold."""

    if value is None or pd.isna(value):
        return 0.0

    value = float(value)

    if value >= threshold:
        return 0.0

    extra = threshold - value

    return round(
        min(
            100.0,
            65.0 + (extra / max_extra) * 35.0,
        ),
        2,
    )


def add_signal(
    results,
    company_id,
    signal_type,
    rule_id,
    text,
    confidence,
):
    """
    Add only signals with confidence >60%.
    """

    if confidence is None:
        return

    confidence = float(confidence)

    if confidence <= CONFIDENCE_THRESHOLD:
        return

    results.append(
        {
            "company_id": company_id,
            "type": signal_type,
            "rule_id": rule_id,
            "text": text,
            "confidence_pct": round(
                confidence,
                2,
            ),
        }
    )


# ============================================================
# TREND HELPERS
# ============================================================


def consecutive_condition(
    df,
    company_id,
    column,
    condition,
    count,
):
    """
    Check a condition for N consecutive annual observations.
    """

    hist = historical_annual(
        df,
        company_id,
    )

    hist = hist.dropna(subset=["year_num", column])

    if len(hist) < count:
        return False

    years = hist["year_num"].tolist()
    values = hist[column].tolist()

    for i in range(len(hist) - count + 1):

        window_years = years[i : i + count]

        window_values = values[i : i + count]

        # Require consecutive calendar years.
        consecutive_years = all(
            window_years[j] + 1 == window_years[j + 1] for j in range(count - 1)
        )

        if not consecutive_years:
            continue

        if all(condition(value) for value in window_values):
            return True

    return False


def improving_trend(
    df,
    company_id,
    column,
    count=3,
):
    """Strictly increasing for N consecutive years."""

    hist = historical_annual(
        df,
        company_id,
    )

    hist = hist.dropna(subset=["year_num", column])

    if len(hist) < count:
        return False

    years = hist["year_num"].tolist()
    values = hist[column].tolist()

    for i in range(len(hist) - count + 1):

        y = years[i : i + count]

        v = values[i : i + count]

        if not all(y[j] + 1 == y[j + 1] for j in range(count - 1)):
            continue

        if all(v[j] < v[j + 1] for j in range(count - 1)):
            return True

    return False


def declining_trend(
    df,
    company_id,
    column,
    count=3,
):
    """Strictly declining for N consecutive years."""

    hist = historical_annual(
        df,
        company_id,
    )

    hist = hist.dropna(subset=["year_num", column])

    if len(hist) < count:
        return False

    years = hist["year_num"].tolist()
    values = hist[column].tolist()

    for i in range(len(hist) - count + 1):

        y = years[i : i + count]

        v = values[i : i + count]

        if not all(y[j] + 1 == y[j + 1] for j in range(count - 1)):
            continue

        if all(v[j] > v[j + 1] for j in range(count - 1)):
            return True

    return False


# ============================================================
# FALLBACK METRICS
# ============================================================


def get_latest_ratio(
    ratio_row,
    column,
):
    """Read a metric from latest financial_ratios row."""

    if ratio_row is None:
        return None

    if column not in ratio_row.index:
        return None

    value = ratio_row[column]

    if pd.isna(value):
        return None

    return float(value)


def get_company_metric(
    companies,
    company_id,
    column,
):
    """Fallback to companies table."""

    row = companies[companies["id"].astype(str) == str(company_id)]

    if row.empty:
        return None

    value = row.iloc[0][column]

    if pd.isna(value):
        return None

    return float(value)


# ============================================================
# STOCK PRICE
# ============================================================


def latest_stock_price(
    stock_prices,
    company_id,
):
    """Return latest adjusted close."""

    company = stock_prices[
        stock_prices["company_id"].astype(str) == str(company_id)
    ].copy()

    if company.empty:
        return None

    company["date"] = pd.to_datetime(
        company["date"],
        errors="coerce",
    )

    company = company.sort_values("date")

    value = company.iloc[-1]["adjusted_close"]

    if pd.isna(value):
        return None

    return float(value)


# ============================================================
# MAIN GENERATOR
# ============================================================


def generate():
    "Generate."

    print("=" * 70)
    print("DAY 30 - NLP AUTO PROS / CONS GENERATOR")
    print("=" * 70)

    (
        companies,
        ratios,
        pnl,
        balance,
        cashflow,
        sectors,
        stock_prices,
    ) = load_data()

    print(f"Companies loaded: {len(companies)}")

    ratios = prepare_history(ratios)
    pnl = prepare_history(pnl)
    balance = prepare_history(balance)
    cashflow = prepare_history(cashflow)

    results = []

    # --------------------------------------------------------
    # Financial companies
    # --------------------------------------------------------

    financial_companies = set(
        sectors[
            sectors["broad_sector"]
            .astype(str)
            .str.contains(
                "Financial",
                case=False,
                na=False,
            )
        ]["company_id"].astype(str)
    )

    # ========================================================
    # COMPANY LOOP
    # ========================================================

    for company_id in companies["id"].astype(str):

        ratio_row = latest_annual(
            ratios,
            company_id,
        )

        pnl_row = latest_annual(
            pnl,
            company_id,
        )

        # ====================================================
        # FALLBACK / DERIVED METRICS
        # ====================================================

        roe = get_latest_ratio(
            ratio_row,
            "return_on_equity_pct",
        )

        if roe is None:
            roe = get_company_metric(
                companies,
                company_id,
                "roe_percentage",
            )

        roce = get_latest_ratio(
            ratio_row,
            "return_on_capital_employed_pct",
        )

        if roce is None:
            roce = get_company_metric(
                companies,
                company_id,
                "roce_percentage",
            )

        de = get_latest_ratio(
            ratio_row,
            "debt_to_equity",
        )

        fcf = get_latest_ratio(
            ratio_row,
            "free_cash_flow_cr",
        )

        icr = get_latest_ratio(
            ratio_row,
            "interest_coverage",
        )

        opm = get_latest_ratio(
            ratio_row,
            "operating_profit_margin_pct",
        )

        if opm is None and pnl_row is not None:
            opm = (
                pnl_row["opm_percentage"]
                if not pd.isna(pnl_row["opm_percentage"])
                else None
            )

        revenue_cagr = get_latest_ratio(
            ratio_row,
            "revenue_cagr_5yr",
        )

        pat_cagr = get_latest_ratio(
            ratio_row,
            "pat_cagr_5yr",
        )

        eps_cagr = get_latest_ratio(
            ratio_row,
            "eps_cagr_5yr",
        )

        payout = get_latest_ratio(
            ratio_row,
            "dividend_payout_ratio_pct",
        )

        # ----------------------------------------------------
        # Derive missing CAGRs from P&L
        # ----------------------------------------------------

        if revenue_cagr is None:
            revenue_cagr = calculate_5yr_cagr(
                pnl,
                company_id,
                "sales",
            )

        if pat_cagr is None:
            pat_cagr = calculate_5yr_cagr(
                pnl,
                company_id,
                "net_profit",
            )

        if eps_cagr is None:
            eps_cagr = calculate_5yr_cagr(
                pnl,
                company_id,
                "eps",
            )

        # ====================================================
        # PRO 1
        # ROE >20% for 3+ consecutive years
        # ====================================================

        roe_high = ratios.copy()

        if not roe_high.empty:
            roe_high["roe_above_20"] = roe_high["return_on_equity_pct"] - 20

            if consecutive_condition(
                roe_high,
                company_id,
                "roe_above_20",
                lambda x: x > 0,
                3,
            ):
                add_signal(
                    results,
                    company_id,
                    "pro",
                    "PRO_01",
                    PRO_TEXT["PRO_01"],
                    85,
                )

        # Fallback using companies table only if historical
        # Ratio Engine data does not exist.
        if ratio_row is None and roe is not None and roe > 20:
            add_signal(
                results,
                company_id,
                "pro",
                "PRO_01",
                PRO_TEXT["PRO_01"],
                confidence_above(
                    roe,
                    20,
                    20,
                ),
            )

        # ====================================================
        # PRO 2
        # FCF positive for 5+ consecutive years
        # ====================================================

        if consecutive_condition(
            ratios,
            company_id,
            "free_cash_flow_cr",
            lambda x: x > 0,
            5,
        ):
            add_signal(
                results,
                company_id,
                "pro",
                "PRO_02",
                PRO_TEXT["PRO_02"],
                85,
            )

        # ====================================================
        # PRO 3
        # D/E = 0 latest year
        # ====================================================

        if de is not None and abs(de) < 1e-12:
            add_signal(
                results,
                company_id,
                "pro",
                "PRO_03",
                PRO_TEXT["PRO_03"],
                95,
            )

        # ====================================================
        # PRO 4
        # Revenue CAGR >15%
        # ====================================================

        if revenue_cagr is not None:
            confidence = confidence_above(
                revenue_cagr,
                15,
                15,
            )

            add_signal(
                results,
                company_id,
                "pro",
                "PRO_04",
                PRO_TEXT["PRO_04"],
                confidence,
            )

        # ====================================================
        # PRO 5
        # OPM >25%
        # ====================================================

        if opm is not None:
            confidence = confidence_above(
                opm,
                25,
                25,
            )

            add_signal(
                results,
                company_id,
                "pro",
                "PRO_05",
                PRO_TEXT["PRO_05"],
                confidence,
            )

        # ====================================================
        # PRO 6
        # PAT CAGR >20%
        # ====================================================

        if pat_cagr is not None:
            confidence = confidence_above(
                pat_cagr,
                20,
                20,
            )

            add_signal(
                results,
                company_id,
                "pro",
                "PRO_06",
                PRO_TEXT["PRO_06"],
                confidence,
            )

        # ====================================================
        # PRO 7
        # ICR >10 OR Debt Free
        # ====================================================

        if de is not None and abs(de) < 1e-12:

            add_signal(
                results,
                company_id,
                "pro",
                "PRO_07",
                PRO_TEXT["PRO_07"],
                95,
            )

        elif icr is not None and icr > 10:

            confidence = confidence_above(
                icr,
                10,
                20,
            )

            add_signal(
                results,
                company_id,
                "pro",
                "PRO_07",
                PRO_TEXT["PRO_07"],
                confidence,
            )

        # ====================================================
        # PRO 8
        # Dividend Yield >2% + Positive FCF
        # ====================================================

        if pnl_row is not None and payout is not None and fcf is not None and fcf > 0:

            eps = pnl_row["eps"]

            price = latest_stock_price(
                stock_prices,
                company_id,
            )

            if pd.notna(eps) and eps > 0 and price is not None and price > 0:

                dividend_per_share = float(eps) * float(payout) / 100.0

                dividend_yield = dividend_per_share / price * 100.0

                if dividend_yield > 2:

                    confidence = confidence_above(
                        dividend_yield,
                        2,
                        4,
                    )

                    add_signal(
                        results,
                        company_id,
                        "pro",
                        "PRO_08",
                        PRO_TEXT["PRO_08"],
                        confidence,
                    )

        # ====================================================
        # PRO 9
        # EPS CAGR >15%
        # ====================================================

        if eps_cagr is not None:

            confidence = confidence_above(
                eps_cagr,
                15,
                15,
            )

            add_signal(
                results,
                company_id,
                "pro",
                "PRO_09",
                PRO_TEXT["PRO_09"],
                confidence,
            )

        # ====================================================
        # PRO 10
        # ROE improving for 3 consecutive years
        # ====================================================

        if improving_trend(
            ratios,
            company_id,
            "return_on_equity_pct",
            3,
        ):

            add_signal(
                results,
                company_id,
                "pro",
                "PRO_10",
                PRO_TEXT["PRO_10"],
                80,
            )

        # ====================================================
        # PRO 11
        # Revenue CAGR > PAT CAGR
        #
        # Follows the explicit condition in the task.
        # ====================================================

        if (
            revenue_cagr is not None
            and pat_cagr is not None
            and revenue_cagr > pat_cagr
        ):

            difference = revenue_cagr - pat_cagr

            confidence = min(
                100,
                65 + difference * 3,
            )

            add_signal(
                results,
                company_id,
                "pro",
                "PRO_11",
                PRO_TEXT["PRO_11"],
                confidence,
            )

        # ====================================================
        # PRO 12
        # Assets growing + declining debt
        # ====================================================

        bal_hist = historical_annual(
            balance,
            company_id,
        )

        bal_hist = bal_hist.dropna(
            subset=[
                "total_assets",
                "borrowings",
            ]
        )

        if len(bal_hist) >= 3:

            recent = bal_hist.tail(3)

            assets = recent["total_assets"].tolist()

            debt = recent["borrowings"].tolist()

            if assets[0] < assets[1] < assets[2] and debt[0] > debt[1] > debt[2]:

                add_signal(
                    results,
                    company_id,
                    "pro",
                    "PRO_12",
                    PRO_TEXT["PRO_12"],
                    85,
                )

        # ====================================================
        # CON 1
        # D/E >2 for non-financial companies
        # ====================================================

        if company_id not in financial_companies and de is not None and de > 2:

            confidence = min(
                100,
                65 + (de - 2) * 10,
            )

            text = CON_TEXT["CON_01"].format(value=de)

            add_signal(
                results,
                company_id,
                "con",
                "CON_01",
                text,
                confidence,
            )

        # ====================================================
        # CON 2
        # FCF negative for 3 consecutive years
        # ====================================================

        if consecutive_condition(
            ratios,
            company_id,
            "free_cash_flow_cr",
            lambda x: x < 0,
            3,
        ):

            add_signal(
                results,
                company_id,
                "con",
                "CON_02",
                CON_TEXT["CON_02"],
                80,
            )

        # ====================================================
        # CON 3
        # OPM declining for 3 consecutive years
        #
        # Prefer P&L because it contains historical OPM.
        # ====================================================

        if declining_trend(
            pnl,
            company_id,
            "opm_percentage",
            3,
        ) or declining_trend(
            ratios,
            company_id,
            "operating_profit_margin_pct",
            3,
        ):

            add_signal(
                results,
                company_id,
                "con",
                "CON_03",
                CON_TEXT["CON_03"],
                80,
            )

        # ====================================================
        # CON 4
        # Net profit negative latest year
        # ====================================================

        if (
            pnl_row is not None
            and pd.notna(pnl_row["net_profit"])
            and pnl_row["net_profit"] < 0
        ):

            add_signal(
                results,
                company_id,
                "con",
                "CON_04",
                CON_TEXT["CON_04"],
                90,
            )

        # ====================================================
        # CON 5
        # Revenue declining for 2+ consecutive years
        # ====================================================

        if declining_trend(
            pnl,
            company_id,
            "sales",
            3,
        ):

            add_signal(
                results,
                company_id,
                "con",
                "CON_05",
                CON_TEXT["CON_05"],
                80,
            )

        # ====================================================
        # CON 6
        # ICR <1.5
        # ====================================================

        if icr is not None and icr < 1.5:

            confidence = min(
                100,
                65 + (1.5 - icr) * 20,
            )

            add_signal(
                results,
                company_id,
                "con",
                "CON_06",
                CON_TEXT["CON_06"],
                confidence,
            )

        # ====================================================
        # CON 7
        # Dividend payout >100%
        # ====================================================

        if payout is not None and payout > 100:

            confidence = min(
                100,
                65 + (payout - 100) * 0.5,
            )

            add_signal(
                results,
                company_id,
                "con",
                "CON_07",
                CON_TEXT["CON_07"],
                confidence,
            )

        # ====================================================
        # CON 8
        # D/E rising for 3 consecutive years
        # ====================================================

        if improving_trend(
            ratios,
            company_id,
            "debt_to_equity",
            3,
        ):

            add_signal(
                results,
                company_id,
                "con",
                "CON_08",
                CON_TEXT["CON_08"],
                80,
            )

        # ====================================================
        # CON 9
        # EPS declining for 3 consecutive years
        # ====================================================

        if declining_trend(
            pnl,
            company_id,
            "eps",
            3,
        ):

            add_signal(
                results,
                company_id,
                "con",
                "CON_09",
                CON_TEXT["CON_09"],
                80,
            )

        # ====================================================
        # CON 10
        # ROCE <10%
        # ====================================================

        if roce is not None and roce < 10:

            confidence = min(
                100,
                65 + (10 - roce) * 5,
            )

            add_signal(
                results,
                company_id,
                "con",
                "CON_10",
                CON_TEXT["CON_10"],
                confidence,
            )

        # ====================================================
        # CON 11
        # Net Debt >3x EBITDA
        #
        # NOT CALCULATED:
        # The current database does not contain:
        #   1. EBITDA
        #   2. cash balance
        #
        # We deliberately do not fabricate this signal.
        # ====================================================

        # ====================================================
        # CON 12
        # Revenue CAGR <5%
        # ====================================================

        if revenue_cagr is not None:

            confidence = confidence_below(
                revenue_cagr,
                5,
                5,
            )

            add_signal(
                results,
                company_id,
                "con",
                "CON_12",
                CON_TEXT["CON_12"],
                confidence,
            )

    # ========================================================
    # OUTPUT
    # ========================================================

    output_df = pd.DataFrame(
        results,
        columns=[
            "company_id",
            "type",
            "rule_id",
            "text",
            "confidence_pct",
        ],
    )

    # Remove accidental duplicate signals.
    output_df = output_df.drop_duplicates(
        subset=[
            "company_id",
            "type",
            "rule_id",
        ]
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # ========================================================
    # VERIFICATION
    # ========================================================

    expected_companies = set(companies["id"].astype(str))

    pro_companies = set(output_df[output_df["type"] == "pro"]["company_id"].astype(str))

    con_companies = set(output_df[output_df["type"] == "con"]["company_id"].astype(str))

    missing_pro = expected_companies - pro_companies

    missing_con = expected_companies - con_companies

    # ========================================================
    # REPORT
    # ========================================================

    print()
    print("=" * 70)
    print("DAY 30 VERIFICATION")
    print("=" * 70)

    print(f"Companies in universe : " f"{len(expected_companies)}")

    print(f"Companies with Pro    : " f"{len(pro_companies)}")

    print(f"Companies with Con    : " f"{len(con_companies)}")

    print(f"Total generated       : " f"{len(output_df)}")

    print()
    print("RULE COVERAGE")
    print("-" * 70)

    rule_counts = output_df.groupby("rule_id").size().sort_index()

    all_rules = [f"PRO_{i:02d}" for i in range(1, 13)] + [
        f"CON_{i:02d}" for i in range(1, 13)
    ]

    for rule_id in all_rules:
        print(f"{rule_id:<10} " f"{int(rule_counts.get(rule_id, 0)):>4}")

    print()
    print(
        "Missing Pro:",
        len(missing_pro),
    )

    if missing_pro:
        print(sorted(missing_pro))

    print()
    print(
        "Missing Con:",
        len(missing_con),
    )

    if missing_con:
        print(sorted(missing_con))

    print()
    print("Rules intentionally unavailable:")
    print(
        "CON_11 - EBITDA and cash balance are " "not present in the current database."
    )

    print()
    print(f"Output: {OUTPUT_PATH}")

    if not missing_pro and not missing_con:
        print()
        print("STATUS: PASS - " "All companies have at least " "one Pro and one Con.")
    else:
        print()
        print(
            "STATUS: REVIEW - "
            "Some companies do not satisfy "
            "both sides using the available "
            "rule-supported data."
        )

    return output_df


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    generate()
