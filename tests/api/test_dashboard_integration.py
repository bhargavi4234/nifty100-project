import sqlite3

import pandas as pd
from fastapi.testclient import TestClient

from src.api.main import app
from src.screener.engine import apply_filters

client = TestClient(app)

DB_PATH = "data/db/nifty100.db"


def load_dashboard_screener_data():
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

    # Same latest-year logic used by Streamlit
    df["year_number"] = df["year"].astype(str).str.extract(r"(\d{4})")[0]

    df["year_number"] = pd.to_numeric(df["year_number"], errors="coerce")

    df = (
        df.sort_values(["company_id", "year_number"])
        .drop_duplicates(subset=["company_id"], keep="last")
        .reset_index(drop=True)
    )

    return df


def test_dashboard_screener_matches_api_min_roe():
    min_roe = 15

    # -----------------------------
    # Streamlit screener result
    # -----------------------------
    dashboard_df = load_dashboard_screener_data()

    dashboard_result = apply_filters(dashboard_df, {"roe_min": min_roe})

    dashboard_companies = set(dashboard_result["company_id"].tolist())

    # -----------------------------
    # API screener result
    # -----------------------------
    response = client.get("/api/v1/screener", params={"min_roe": min_roe})

    assert response.status_code == 200

    api_data = response.json()

    api_companies = {company["company_id"] for company in api_data["companies"]}

    # -----------------------------
    # Integration comparison
    # -----------------------------
    assert dashboard_companies == api_companies
