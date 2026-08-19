import os
import sqlite3

import numpy as np
import pandas as pd

# ==========================================================
# Configuration
# ==========================================================

DB_PATH = "data/db/nifty100.db"
MARKET_CAP_FILE = "data/raw/market_cap.xlsx"

OUTPUT_XLSX = "output/valuation_summary.xlsx"
OUTPUT_CSV = "output/valuation_flags.csv"


# ==========================================================
# Load market-cap data
# ==========================================================


def load_market_cap():
    """Load market-cap and valuation data from Excel."""

    df = pd.read_excel(MARKET_CAP_FILE)

    required_columns = [
        "company_id",
        "year",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in market_cap.xlsx: {missing}")

    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    numeric_columns = [
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ==========================================================
# Load company / sector / FCF data
# ==========================================================


def load_database_data():
    """Load company names, sectors and FCF data."""

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        """,
        conn,
    )

    sectors = pd.read_sql_query(
        """
        SELECT
            company_id,
            broad_sector AS sector
        FROM sectors
        """,
        conn,
    )

    ratios = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            free_cash_flow_cr
        FROM financial_ratios
        """,
        conn,
    )

    conn.close()

    return companies, sectors, ratios


# ==========================================================
# Convert financial-ratio year to numeric year
# ==========================================================


def extract_year(value):
    """Extract four-digit year from values such as 'Mar 2024'."""

    if pd.isna(value):
        return np.nan

    value = str(value)

    import re

    match = re.search(r"(19|20)\d{2}", value)

    if match:
        return int(match.group())

    return np.nan


# ==========================================================
# Build valuation dataset
# ==========================================================


def build_valuation_data():
    "Build valuation data."

    market = load_market_cap()

    companies, sectors, ratios = load_database_data()

    # Convert financial-ratio year
    ratios["year_num"] = ratios["year"].apply(extract_year)

    # Keep valid FCF values
    ratios["free_cash_flow_cr"] = pd.to_numeric(
        ratios["free_cash_flow_cr"], errors="coerce"
    )

    # Latest FCF year for every company
    ratios = ratios.sort_values(["company_id", "year_num"])

    latest_fcf = (
        ratios.dropna(subset=["year_num"])
        .groupby("company_id", as_index=False)
        .tail(1)[
            [
                "company_id",
                "year_num",
                "free_cash_flow_cr",
            ]
        ]
        .rename(
            columns={
                "year_num": "fcf_year",
            }
        )
    )

    # Latest market-cap year
    market = market.sort_values(["company_id", "year"])

    latest_market = (
        market.dropna(subset=["year"])
        .groupby("company_id", as_index=False)
        .tail(1)
        .copy()
    )

    latest_year = int(latest_market["year"].max())

    # ======================================================
    # Sector median P/E for latest year
    # ======================================================

    latest_market_with_sector = latest_market.merge(
        sectors,
        on="company_id",
        how="left",
    )

    latest_sector_pe = (
        latest_market_with_sector[
            [
                "sector",
                "pe_ratio",
            ]
        ]
        .dropna(subset=["sector", "pe_ratio"])
        .query("pe_ratio > 0")
        .groupby("sector")["pe_ratio"]
        .median()
        .rename("latest_sector_median_pe")
        .reset_index()
    )

    # ======================================================
    # 5-year sector median P/E
    # ======================================================

    five_year_start = latest_year - 4

    five_year_market = market[
        market["year"].between(five_year_start, latest_year)
    ].copy()

    five_year_market = five_year_market.merge(
        sectors,
        on="company_id",
        how="left",
    )

    five_year_sector_pe = (
        five_year_market[
            [
                "sector",
                "pe_ratio",
            ]
        ]
        .dropna(subset=["sector", "pe_ratio"])
        .query("pe_ratio > 0")
        .groupby("sector")["pe_ratio"]
        .median()
        .rename("5yr_median_PE")
        .reset_index()
    )

    # ======================================================
    # Merge latest valuation data
    # ======================================================

    result = latest_market.merge(
        companies,
        on="company_id",
        how="left",
    )

    result = result.merge(
        sectors,
        on="company_id",
        how="left",
    )

    result = result.merge(
        latest_fcf[
            [
                "company_id",
                "fcf_year",
                "free_cash_flow_cr",
            ]
        ],
        on="company_id",
        how="left",
    )

    result = result.merge(
        latest_sector_pe,
        on="sector",
        how="left",
    )

    result = result.merge(
        five_year_sector_pe,
        on="sector",
        how="left",
    )

    # ======================================================
    # FCF Yield
    # ======================================================

    result["FCF_yield_pct"] = np.where(
        result["market_cap_crore"] > 0,
        (result["free_cash_flow_cr"] / result["market_cap_crore"] * 100),
        np.nan,
    )

    # ======================================================
    # P/E vs sector median
    #
    # Use latest-year sector median for the valuation flag.
    # ======================================================

    result["PE_vs_sector_median_pct"] = np.where(
        result["latest_sector_median_pe"] > 0,
        (
            (result["pe_ratio"] - result["latest_sector_median_pe"])
            / result["latest_sector_median_pe"]
        )
        * 100,
        np.nan,
    )

    # ======================================================
    # Valuation flags
    # ======================================================

    def valuation_flag(row):
        "Valuation flag."

        pe = row["pe_ratio"]
        sector_median = row["latest_sector_median_pe"]

        if pd.isna(pe) or pd.isna(sector_median):
            return "Fair"

        if pe > sector_median * 1.5:
            return "Caution"

        if pe < sector_median * 0.7:
            return "Discount"

        return "Fair"

    result["flag"] = result.apply(
        valuation_flag,
        axis=1,
    )

    # ======================================================
    # Final columns
    # ======================================================

    final_columns = [
        "company_id",
        "company_name",
        "sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "FCF_yield_pct",
        "5yr_median_PE",
        "PE_vs_sector_median_pct",
        "flag",
    ]

    result = result[final_columns].copy()

    # Rename valuation columns
    result = result.rename(
        columns={
            "pe_ratio": "P/E",
            "pb_ratio": "P/B",
            "ev_ebitda": "EV/EBITDA",
        }
    )

    # Round numeric values
    numeric_columns = [
        "P/E",
        "P/B",
        "EV/EBITDA",
        "FCF_yield_pct",
        "5yr_median_PE",
        "PE_vs_sector_median_pct",
    ]

    for col in numeric_columns:
        result[col] = result[col].round(2)

    return result, latest_year


# ==========================================================
# Export results
# ==========================================================


def export_valuation():
    "Export valuation."

    os.makedirs("output", exist_ok=True)

    result, latest_year = build_valuation_data()

    # ------------------------------------------------------
    # Excel
    # ------------------------------------------------------

    result.to_excel(
        OUTPUT_XLSX,
        index=False,
    )

    # ------------------------------------------------------
    # CSV
    # Only Caution and Discount
    # ------------------------------------------------------

    flags = result[
        result["flag"].isin(
            [
                "Caution",
                "Discount",
            ]
        )
    ].copy()

    flags.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    # ------------------------------------------------------
    # Console summary
    # ------------------------------------------------------

    print("=" * 70)
    print("VALUATION MODULE")
    print("=" * 70)

    print(f"Latest market year : {latest_year}")
    print(f"Companies analysed : {len(result)}")

    print("\nValuation flags:")

    print(result["flag"].value_counts().to_string())

    print("\nExcel output:")
    print(OUTPUT_XLSX)

    print("\nCSV output:")
    print(OUTPUT_CSV)

    print("\nSample results:")
    print(result.head(10).to_string(index=False))

    print("=" * 70)


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":
    export_valuation()
