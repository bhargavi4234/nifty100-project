import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/market-cap",
    tags=["Market Cap"],
)

DB_PATH = "data/db/nifty100.db"


@router.get("/{ticker}")
def get_market_cap_history(ticker: str):
    "Get market cap history."

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    company = conn.execute(
        """
        SELECT id, company_name
        FROM companies
        WHERE id = ?
        COLLATE NOCASE
        """,
        (ticker,),
    ).fetchone()

    if company is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found",
        )

    rows = conn.execute(
        """
        SELECT
            year,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct
        FROM market_cap
        WHERE company_id = ?
        AND CAST(substr(year, -4) AS INTEGER)
            BETWEEN 2019 AND 2024
        ORDER BY year
        """,
        (ticker,),
    ).fetchall()

    conn.close()

    return {
        "company_id": ticker,
        "history": [dict(row) for row in rows],
    }
