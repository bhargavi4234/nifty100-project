import re
import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "data" / "db" / "nifty100.db"
TEARSHEET_DIR = BASE_DIR / "reports" / "tearsheets"


def get_db():
    "Get db."
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dict(rows):
    "Rows to dict."
    return [dict(row) for row in rows]


def extract_year(value):
    "Extract year."
    if value is None:
        return None

    match = re.search(r"(\d{4})", str(value))

    if match:
        return int(match.group(1))

    return None


def validate_year_filter(value):
    "Validate year filter."
    if value is None:
        return None

    if not re.fullmatch(r"\d{4}-\d{2}", value):
        raise HTTPException(
            status_code=400,
            detail="Year must be in YYYY-MM format.",
        )

    return value


def filter_history(rows, from_year=None, to_year=None):
    "Filter history."
    from_year = validate_year_filter(from_year)
    to_year = validate_year_filter(to_year)

    result = []

    for row in rows:
        data = dict(row)

        year_value = data.get("year") or data.get("date") or data.get("period")

        row_year = extract_year(year_value)

        if from_year:
            if row_year is None:
                continue

            if row_year < int(from_year[:4]):
                continue

        if to_year:
            if row_year is None:
                continue

            if row_year > int(to_year[:4]):
                continue

        result.append(data)

    return result


def get_company(conn, ticker):
    "Get company."
    row = conn.execute(
        """
        SELECT *
        FROM companies
        WHERE id = ?
        COLLATE NOCASE
        """,
        (ticker,),
    ).fetchone()

    return row


def get_sector(conn, ticker):
    "Get sector."
    return conn.execute(
        """
        SELECT *
        FROM sectors
        WHERE company_id = ?
        """,
        (ticker,),
    ).fetchall()


# ============================================================
# GET ALL COMPANIES
# ============================================================


@router.get("")
def get_companies(
    sector: str | None = Query(default=None),
    market_cap_category: str | None = Query(default=None),
    search: str | None = Query(default=None),
):
    "Get companies."
    conn = get_db()

    try:
        query = """
            SELECT
                c.id,
                c.company_name,
                s.broad_sector,
                s.sub_sector,
                c.roe_percentage AS roe_pct,
                c.roce_percentage AS roce_pct,
                s.market_cap_category
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            WHERE 1=1
        """

        params = []

        if sector:
            query += """
                AND s.broad_sector = ?
            """
            params.append(sector)

        if market_cap_category:
            query += """
                AND s.market_cap_category = ?
            """
            params.append(market_cap_category)

        if search:
            query += """
                AND (
                    c.id LIKE ?
                    OR c.company_name LIKE ?
                )
            """

            search_value = f"%{search}%"

            params.extend(
                [
                    search_value,
                    search_value,
                ]
            )

        query += """
            ORDER BY c.company_name
        """

        rows = conn.execute(
            query,
            params,
        ).fetchall()

        return {
            "count": len(rows),
            "companies": rows_to_dict(rows),
        }

    finally:
        conn.close()


# ============================================================
# GET COMPANY PROFILE
# ============================================================


@router.get("/{ticker}")
def get_company_profile(ticker: str):
    "Get company profile."

    conn = get_db()

    try:
        company = get_company(
            conn,
            ticker,
        )

        if company is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        company_data = dict(company)

        sectors = get_sector(
            conn,
            ticker,
        )

        sector_data = dict(sectors[0]) if sectors else {}

        latest_ratio = conn.execute(
            """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
            ORDER BY
                CAST(
                    substr(year, -4)
                    AS INTEGER
                ) DESC
            LIMIT 1
            """,
            (ticker,),
        ).fetchone()

        return {
            "company": company_data,
            "sector": sector_data,
            "latest_kpis": (dict(latest_ratio) if latest_ratio else {}),
        }

    finally:
        conn.close()


# ============================================================
# P&L HISTORY
# ============================================================


@router.get("/{ticker}/pl")
def get_profit_loss(
    ticker: str,
    from_year: str | None = Query(default=None),
    to_year: str | None = Query(default=None),
):
    "Get profit loss."

    conn = get_db()

    try:
        if get_company(conn, ticker) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        rows = conn.execute(
            """
            SELECT *
            FROM profitandloss
            WHERE company_id = ?
            ORDER BY year
            """,
            (ticker,),
        ).fetchall()

        history = filter_history(
            rows,
            from_year,
            to_year,
        )

        return {
            "company_id": ticker,
            "history": history,
        }

    finally:
        conn.close()


# ============================================================
# BALANCE SHEET HISTORY
# ============================================================


@router.get("/{ticker}/bs")
def get_balance_sheet(
    ticker: str,
    from_year: str | None = Query(default=None),
    to_year: str | None = Query(default=None),
):
    "Get balance sheet."

    conn = get_db()

    try:
        if get_company(conn, ticker) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        rows = conn.execute(
            """
            SELECT *
            FROM balancesheet
            WHERE company_id = ?
            ORDER BY year
            """,
            (ticker,),
        ).fetchall()

        history = filter_history(
            rows,
            from_year,
            to_year,
        )

        return {
            "company_id": ticker,
            "history": history,
        }

    finally:
        conn.close()


# ============================================================
# CASH FLOW HISTORY
# ============================================================


@router.get("/{ticker}/cashflow")
def get_cashflow(
    ticker: str,
    from_year: str | None = Query(default=None),
    to_year: str | None = Query(default=None),
):
    "Get cashflow."

    conn = get_db()

    try:
        if get_company(conn, ticker) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        rows = conn.execute(
            """
            SELECT *
            FROM cashflow
            WHERE company_id = ?
            ORDER BY year
            """,
            (ticker,),
        ).fetchall()

        history = filter_history(
            rows,
            from_year,
            to_year,
        )

        return {
            "company_id": ticker,
            "history": history,
        }

    finally:
        conn.close()


# ============================================================
# FINANCIAL RATIOS
# ============================================================


@router.get("/{ticker}/ratios")
def get_ratios(
    ticker: str,
    year: str | None = Query(default=None),
):
    "Get ratios."

    conn = get_db()

    try:
        if get_company(conn, ticker) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        if year:
            if not re.fullmatch(
                r"\d{4}-\d{2}",
                year,
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Year must be in YYYY-MM format.",
                )

            year_number = int(year[:4])

            rows = conn.execute(
                """
                SELECT *
                FROM financial_ratios
                WHERE company_id = ?
                """,
                (ticker,),
            ).fetchall()

            rows = [
                dict(row) for row in rows if extract_year(row["year"]) == year_number
            ]

        else:
            rows = conn.execute(
                """
                SELECT *
                FROM financial_ratios
                WHERE company_id = ?
                ORDER BY year
                """,
                (ticker,),
            ).fetchall()

            rows = rows_to_dict(rows)

        return {
            "company_id": ticker,
            "ratios": rows,
        }

    finally:
        conn.close()


# ============================================================
# TEARSHEET PDF
# ============================================================


@router.get("/{ticker}/tearsheet")
def get_tearsheet(ticker: str):
    "Get tearsheet."

    conn = get_db()

    try:
        if get_company(conn, ticker) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )
    finally:
        conn.close()

    possible_files = [
        TEARSHEET_DIR / f"{ticker}.pdf",
        TEARSHEET_DIR / f"{ticker}_tearsheet.pdf",
        TEARSHEET_DIR / f"{ticker}_tearsheet.pdf".lower(),
    ]

    pdf_path = next(
        (path for path in possible_files if path.exists()),
        None,
    )

    if pdf_path is None:
        raise HTTPException(
            status_code=404,
            detail=f"Tearsheet for '{ticker}' not found.",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )


@router.get("/{ticker}/peers/compare")
def compare_with_peers(ticker: str):
    "Compare with peers."

    conn = get_db()
    conn.row_factory = sqlite3.Row

    company = conn.execute(
        """
        SELECT *
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

    peer = conn.execute(
        """
        SELECT peer_group_name
        FROM peer_groups
        WHERE company_id = ?
        LIMIT 1
        """,
        (ticker,),
    ).fetchone()

    if peer is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Peer group not found",
        )

    group_name = peer["peer_group_name"]

    peer_rows = conn.execute(
        """
        SELECT company_id, is_benchmark
        FROM peer_groups
        WHERE peer_group_name = ?
        """,
        (group_name,),
    ).fetchall()

    ids = [row["company_id"] for row in peer_rows]

    placeholders = ",".join("?" * len(ids))

    rows = conn.execute(
        f"""
        SELECT *
        FROM financial_ratios
        WHERE company_id IN ({placeholders})
        """,
        ids,
    ).fetchall()

    conn.close()

    import pandas as pd

    df = pd.DataFrame([dict(row) for row in rows])

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="No peer KPI data found",
        )

    df = df.sort_values("year").groupby("company_id").tail(1)

    axes = {
        "ROE": "return_on_equity_pct",
        "ROCE": "return_on_capital_employed_pct",
        "Revenue CAGR": "revenue_cagr_5yr",
        "PAT CAGR": "pat_cagr_5yr",
        "OPM": "operating_profit_margin_pct",
        "Debt/Equity": "debt_to_equity",
        "Asset Turnover": "asset_turnover",
        "Net Profit Margin": "net_profit_margin_pct",
    }

    company_row = df[df["company_id"] == ticker]

    if company_row.empty:
        raise HTTPException(
            status_code=404,
            detail="Company KPI data not found",
        )

    company_row = company_row.iloc[0]

    benchmark_ids = [row["company_id"] for row in peer_rows if row["is_benchmark"]]

    benchmark_row = df[df["company_id"].isin(benchmark_ids)]

    radar = []

    for axis, column in axes.items():

        company_value = company_row[column]

        peer_average = df[column].mean()

        benchmark_value = (
            benchmark_row[column].mean() if not benchmark_row.empty else None
        )

        radar.append(
            {
                "axis": axis,
                "company": company_value,
                "peer_group_average": peer_average,
                "benchmark": benchmark_value,
            }
        )

    return {
        "company_id": ticker,
        "peer_group": group_name,
        "radar": radar,
    }


@router.get("/{ticker}/documents")
def get_company_documents(ticker: str):
    "Get company documents."

    conn = get_db()

    company = get_company(
        conn,
        ticker,
    )

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
            annual_report
        FROM documents
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        (ticker,),
    ).fetchall()

    conn.close()

    documents = []

    for row in rows:

        data = dict(row)

        url = data["annual_report"]

        is_valid = isinstance(url, str) and (url.startswith(("http://", "https://")))

        documents.append(
            {
                "year": data["year"],
                "annual_report": url,
                "is_url_valid": is_valid,
            }
        )

    return {
        "company_id": ticker,
        "documents": documents,
    }
