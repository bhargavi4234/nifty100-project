import numpy as np
import pandas as pd
import yaml


def load_config(config_path):
    """
    Load screener configuration from YAML.
    """

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config.get("filters", {})


def winsorised_score(series, higher_is_better=True):
    """
    Winsorise a metric using the 10th and 90th percentiles,
    then scale it to 0–100.
    """

    values = pd.to_numeric(series, errors="coerce")

    p10 = values.quantile(0.10)
    p90 = values.quantile(0.90)

    values = values.clip(lower=p10, upper=p90)

    if p90 == p10:
        scaled = pd.Series(50, index=values.index)
    else:
        scaled = ((values - p10) / (p90 - p10)) * 100

    if not higher_is_better:
        scaled = 100 - scaled

    return scaled.fillna(0)


def compute_quality_score(df):
    """
    Compute weighted composite quality score (0–100).

    Weights:
    Profitability (35%)
        ROE 15%
        ROCE 10%
        Net Profit Margin 10%

    Cash Quality (15% available)
        CFO/PAT Ratio 10%
        FCF Positive Flag 5%

    Growth (20%)
        Revenue CAGR 10%
        PAT CAGR 10%

    Leverage (15%)
        Debt/Equity 10%
        Interest Coverage 5%

    Note:
    FCF CAGR (15%) is not available in the database,
    so it is omitted.
    """

    score = pd.Series(0.0, index=df.index)

    def metric_score(col, higher_is_better=True):
        "Metric score."
        if col not in df.columns:
            return pd.Series(0, index=df.index)

        values = pd.to_numeric(df[col], errors="coerce")

        p10 = values.quantile(0.10)
        p90 = values.quantile(0.90)

        values = values.clip(lower=p10, upper=p90)

        if p90 == p10:
            score_series = pd.Series(50, index=values.index)
        else:
            score_series = ((values - p10) / (p90 - p10)) * 100

        if not higher_is_better:
            score_series = 100 - score_series

        return score_series.fillna(0)

    # ---------------- Profitability (35%) ----------------
    score += metric_score("return_on_equity_pct") * 0.15
    score += metric_score("return_on_capital_employed_pct") * 0.10
    score += metric_score("net_profit_margin_pct") * 0.10

    # ---------------- Cash Quality (15%) ----------------
    if "cash_from_operations_cr" in df.columns and "net_profit" in df.columns:
        ratio = df["cash_from_operations_cr"] / df["net_profit"].replace(0, np.nan)

        ratio = ratio.fillna(0)

        p10 = ratio.quantile(0.10)
        p90 = ratio.quantile(0.90)

        ratio = ratio.clip(lower=p10, upper=p90)

        if p90 != p10:
            ratio_score = ((ratio - p10) / (p90 - p10)) * 100
        else:
            ratio_score = pd.Series(50, index=ratio.index)

        score += ratio_score.fillna(0) * 0.10

    if "free_cash_flow_cr" in df.columns:
        score += (df["free_cash_flow_cr"] > 0).astype(int) * 100 * 0.05

    # ---------------- Growth (20%) ----------------
    score += metric_score("revenue_cagr_5yr") * 0.10
    score += metric_score("pat_cagr_5yr") * 0.10

    # ---------------- Leverage (15%) ----------------
    score += (
        metric_score(
            "debt_to_equity",
            higher_is_better=False,
        )
        * 0.10
    )

    if "interest_coverage" in df.columns:

        icr = df["interest_coverage"].replace("Debt Free", np.inf)

        icr = pd.to_numeric(icr, errors="coerce").fillna(0)

        p10 = icr.quantile(0.10)
        p90 = icr.quantile(0.90)

        icr = icr.clip(lower=p10, upper=p90)

        if p90 != p10:
            icr_score = ((icr - p10) / (p90 - p10)) * 100
        else:
            icr_score = pd.Series(50, index=icr.index)

        score += icr_score.fillna(0) * 0.05

        # Sector-relative normalisation
    if "broad_sector" in df.columns:

        sector_score = (
            pd.DataFrame({"score": score, "sector": df["broad_sector"]})
            .groupby("sector")["score"]
            .transform(
                lambda x: (
                    ((x - x.min()) / (x.max() - x.min()) * 100)
                    if x.max() != x.min()
                    else 50
                )
            )
        )

        return sector_score.round(2)

    return score.round(2)


def apply_filters(df, filters):
    """
    Apply screener filters.
    """

    result = df.copy()

    # ROE
    value = filters.get("roe_min")
    if value is not None:
        result = result[result["return_on_equity_pct"] >= value]

    # Debt to Equity
    value = filters.get("debt_equity_max")
    if value is not None:

        financials = result["broad_sector"].str.contains(
            "Financial",
            case=False,
            na=False,
        )

        result = pd.concat(
            [
                result[financials],
                result[(~financials) & (result["debt_to_equity"] <= value)],
            ]
        ).reset_index(drop=True)

    # Free Cash Flow
    value = filters.get("fcf_min")
    if value is not None:
        result = result[result["free_cash_flow_cr"] >= value]

    # Revenue CAGR
    value = filters.get("revenue_cagr_5yr_min")
    if value is not None:
        result = result[result["revenue_cagr_5yr"] >= value]

    # PAT CAGR
    value = filters.get("pat_cagr_5yr_min")
    if value is not None:
        result = result[result["pat_cagr_5yr"] >= value]

    # Operating Profit Margin
    value = filters.get("opm_min")
    if value is not None:
        result = result[result["operating_profit_margin_pct"] >= value]

    # Interest Coverage Ratio
    value = filters.get("icr_min")
    if value is not None:

        icr = result["interest_coverage"].replace(
            "Debt Free",
            np.inf,
        )

        icr = pd.to_numeric(
            icr,
            errors="coerce",
        )

        result = result[icr >= value]

    # EPS CAGR
    value = filters.get("eps_cagr_min")
    if value is not None:
        result = result[result["eps_cagr_5yr"] >= value]

    # Asset Turnover
    value = filters.get("asset_turnover_min")
    if value is not None:
        result = result[result["asset_turnover"] >= value]

    # Market Cap
    value = filters.get("market_cap_min")
    if value is not None:
        result = result[result["market_cap_crore"] >= value]

    # PE Ratio
    value = filters.get("pe_max")
    if value is not None:
        result = result[result["pe_ratio"] <= value]
    # PB Ratio
    value = filters.get("pb_max")
    if value is not None:
        result = result[result["pb_ratio"] <= value]
    # Dividend Yield
    value = filters.get("dividend_yield_min")
    if value is not None:
        result = result[result["dividend_yield_pct"] >= value]

    # Dividend Payout Ratio
    value = filters.get("dividend_payout_max")
    if value is not None:
        result = result[result["dividend_payout_ratio_pct"] <= value]

    # Sales
    value = filters.get("sales_min")
    if value is not None:
        result = result[result["sales"] >= value]

    # Net Profit
    value = filters.get("net_profit_min")
    if value is not None:
        result = result[result["net_profit"] >= value]

    # Add quality score
    result["composite_quality_score"] = compute_quality_score(result)

    # Sort by quality score
    result = result.sort_values(
        by="composite_quality_score",
        ascending=False,
    ).reset_index(drop=True)

    return result


if __name__ == "__main__":

    import sqlite3

    conn = sqlite3.connect("data/db/nifty100.db")

    query = """
    SELECT

        fr.*,

        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct,

        pl.sales,
        pl.net_profit,

        s.broad_sector

    FROM financial_ratios fr

    
    LEFT JOIN market_cap mc
        ON fr.company_id = mc.company_id
        AND SUBSTR(fr.year, -4) = CAST(mc.year AS TEXT)
        
    LEFT JOIN profitandloss pl
        ON fr.company_id = pl.company_id
        AND fr.year = pl.year

    LEFT JOIN sectors s
        ON fr.company_id = s.company_id
    """

    df = pd.read_sql(query, conn)

    filters = load_config("src/screener/screener_config.yaml")

    screened = apply_filters(
        df,
        filters,
    )

    print(screened.head())

    print(f"\nCompanies selected: {len(screened)}")

    conn.close()
