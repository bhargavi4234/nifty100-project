import sqlite3

import pandas as pd
from fastapi import APIRouter

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)

DB_PATH = "data/db/nifty100.db"

KPI_COLUMNS = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "return_on_capital_employed_pct",
]


@router.get("/stats")
def portfolio_stats():
    "Portfolio stats."

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT *
        FROM financial_ratios
        """,
        conn,
    )

    conn.close()

    latest = df.sort_values("year").groupby("company_id").tail(1)

    rows = []

    for metric in KPI_COLUMNS:

        series = latest[metric].dropna()

        rows.append(
            {
                "kpi": metric,
                "P10": series.quantile(0.10),
                "P25": series.quantile(0.25),
                "P50": series.quantile(0.50),
                "P75": series.quantile(0.75),
                "P90": series.quantile(0.90),
            }
        )

    return {
        "company_count": len(latest),
        "stats": rows,
    }
