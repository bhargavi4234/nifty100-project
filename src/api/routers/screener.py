import sqlite3

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/screener", tags=["Screener"])

DB_PATH = "data/db/nifty100.db"


def parse_float(value, name):
    "Parse float."
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"{name} must be a valid number")


@router.get("")
def screener(
    min_roe: str | None = Query(None),
    max_de: str | None = Query(None),
    min_fcf: str | None = Query(None),
    sector: str | None = Query(None),
    min_rev_cagr_5yr: str | None = Query(None),
    min_pat_cagr_5yr: str | None = Query(None),
    max_pe: str | None = Query(None),
):
    "Screener."
    min_roe = parse_float(min_roe, "min_roe")
    max_de = parse_float(max_de, "max_de")
    min_fcf = parse_float(min_fcf, "min_fcf")
    min_rev_cagr_5yr = parse_float(min_rev_cagr_5yr, "min_rev_cagr_5yr")
    min_pat_cagr_5yr = parse_float(min_pat_cagr_5yr, "min_pat_cagr_5yr")
    max_pe = parse_float(max_pe, "max_pe")

    # Validate parameter ranges
    if min_roe is not None and min_roe < -100:
        raise HTTPException(400, "min_roe is invalid")

    if max_de is not None and max_de < 0:
        raise HTTPException(400, "max_de cannot be negative")

    if min_rev_cagr_5yr is not None and min_rev_cagr_5yr < -100:
        raise HTTPException(400, "min_rev_cagr_5yr is invalid")

    if min_pat_cagr_5yr is not None and min_pat_cagr_5yr < -100:
        raise HTTPException(400, "min_pat_cagr_5yr is invalid")

    if max_pe is not None and max_pe <= 0:
        raise HTTPException(400, "max_pe must be greater than zero")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            fr.return_on_equity_pct AS roe_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            mc.pe_ratio
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id
        LEFT JOIN market_cap mc
            ON c.id = mc.company_id
            AND mc.year = (
                SELECT MAX(mc2.year)
                FROM market_cap mc2
                WHERE mc2.company_id = c.id
            )
        WHERE fr.id IN (
            SELECT MAX(fr2.id)
            FROM financial_ratios fr2
            WHERE fr2.company_id = c.id
        )
    """

    params = []

    if min_roe is not None:
        query += " AND fr.return_on_equity_pct >= ?"
        params.append(min_roe)

    if max_de is not None:
        query += " AND fr.debt_to_equity <= ?"
        params.append(max_de)

    if min_fcf is not None:
        query += " AND fr.free_cash_flow_cr >= ?"
        params.append(min_fcf)

    if sector:
        query += " AND s.broad_sector = ?"
        params.append(sector)

    if min_rev_cagr_5yr is not None:
        query += " AND fr.revenue_cagr_5yr >= ?"
        params.append(min_rev_cagr_5yr)

    if min_pat_cagr_5yr is not None:
        query += " AND fr.pat_cagr_5yr >= ?"
        params.append(min_pat_cagr_5yr)

    if max_pe is not None:
        query += " AND mc.pe_ratio <= ?"
        params.append(max_pe)

    query += """
        ORDER BY fr.return_on_equity_pct DESC
    """

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "count": len(rows),
        "companies": [dict(row) for row in rows],
    }
