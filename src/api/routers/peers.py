import sqlite3

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/peers", tags=["Peers"])

DB_PATH = "data/db/nifty100.db"

METRICS = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "operating_profit_margin_pct",
    "interest_coverage",
    "asset_turnover",
    "net_profit_margin_pct",
    "return_on_capital_employed_pct",
]


@router.get("/{group_name}")
def get_peer_group(group_name: str):
    "Get peer group."

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    peers = conn.execute(
        """
        SELECT
            pg.company_id,
            pg.is_benchmark,
            c.company_name
        FROM peer_groups pg
        JOIN companies c
            ON c.id = pg.company_id
        WHERE pg.peer_group_name = ?
        """,
        (group_name,),
    ).fetchall()

    if not peers:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Peer group '{group_name}' not found",
        )

    companies = [dict(row) for row in peers]

    ids = [x["company_id"] for x in companies]

    placeholders = ",".join("?" * len(ids))

    query = f"""
        SELECT *
        FROM financial_ratios
        WHERE company_id IN ({placeholders})
    """

    ratios = pd.read_sql_query(
        query,
        conn,
        params=ids,
    )

    conn.close()

    if ratios.empty:
        return {
            "peer_group": group_name,
            "companies": companies,
        }

    latest = ratios.sort_values("year").groupby("company_id").tail(1).copy()

    for metric in METRICS:
        if metric in latest.columns:
            latest[f"{metric}_percentile"] = (
                latest[metric].rank(pct=True).mul(100).round(2)
            )

    result = []

    for company in companies:

        row = latest[latest["company_id"] == company["company_id"]]

        item = {
            "company_id": company["company_id"],
            "company_name": company["company_name"],
            "is_benchmark": company["is_benchmark"],
        }

        if not row.empty:
            data = row.iloc[0]

            item["metrics"] = {
                metric: data.get(metric)
                for metric in METRICS
                if metric in latest.columns
            }

            item["percentile_rank"] = {
                metric: data.get(f"{metric}_percentile")
                for metric in METRICS
                if f"{metric}_percentile" in latest.columns
            }

        result.append(item)

    return {
        "peer_group": group_name,
        "count": len(result),
        "companies": result,
    }
