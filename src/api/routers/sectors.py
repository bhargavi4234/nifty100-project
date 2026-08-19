import sqlite3

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/sectors", tags=["Sectors"])

DB_PATH = "data/db/nifty100.db"


@router.get("")
def get_sectors():
    "Get sectors."

    conn = sqlite3.connect(DB_PATH)

    sectors_df = pd.read_sql_query("SELECT DISTINCT broad_sector FROM sectors", conn)

    results = []

    for sector in sectors_df["broad_sector"]:

        companies = pd.read_sql_query(
            """
            SELECT company_id
            FROM sectors
            WHERE broad_sector = ?
            """,
            conn,
            params=(sector,),
        )

        ids = companies["company_id"].tolist()

        if not ids:
            continue

        placeholders = ",".join(["?"] * len(ids))

        ratios = pd.read_sql_query(
            f"""
            SELECT return_on_equity_pct, debt_to_equity
            FROM financial_ratios
            WHERE company_id IN ({placeholders})
            """,
            conn,
            params=ids,
        )

        pe = pd.read_sql_query(
            f"""
            SELECT pe_ratio
            FROM market_cap
            WHERE company_id IN ({placeholders})
            """,
            conn,
            params=ids,
        )

        results.append(
            {
                "sector": sector,
                "company_count": len(ids),
                "median_roe": round(ratios["return_on_equity_pct"].median(), 2),
                "median_pe": round(pe["pe_ratio"].median(), 2),
                "median_de": round(ratios["debt_to_equity"].median(), 2),
            }
        )

    conn.close()

    return {"count": len(results), "sectors": results}


@router.get("/{sector}/companies")
def get_sector_companies(sector: str):
    "Get sector companies."

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    exists = conn.execute(
        """
        SELECT 1
        FROM sectors
        WHERE broad_sector = ?
        LIMIT 1
        """,
        (sector,),
    ).fetchone()

    if not exists:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Sector '{sector}' not found",
        )

    rows = conn.execute(
        """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            fr.*
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        LEFT JOIN financial_ratios fr
            ON fr.company_id = c.id
        WHERE s.broad_sector = ?
        AND fr.id IN (
            SELECT MAX(fr2.id)
            FROM financial_ratios fr2
            WHERE fr2.company_id = c.id
        )
        ORDER BY c.company_name
        """,
        (sector,),
    ).fetchall()

    conn.close()

    return {
        "sector": sector,
        "count": len(rows),
        "companies": [dict(row) for row in rows],
    }
