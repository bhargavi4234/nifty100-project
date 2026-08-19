import os
import sqlite3
from datetime import datetime, timezone

import pandas as pd

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

RAW_DATA = os.path.join(BASE_DIR, "data", "raw")
DB_PATH = os.path.join(BASE_DIR, "data", "db", "nifty100.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "db", "schema.sql")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Files with header=1
HEADER1_FILES = {
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
}

# Excel file -> SQLite table mapping
TABLE_MAP = {
    "companies.xlsx": "companies",
    "sectors.xlsx": "sectors",
    "peer_groups.xlsx": "peer_groups",
    "analysis.xlsx": "analysis",
    "prosandcons.xlsx": "prosandcons",
    "documents.xlsx": "documents",
    "profitandloss.xlsx": "profitandloss",
    "balancesheet.xlsx": "balancesheet",
    "cashflow.xlsx": "cashflow",
    "financial_ratios.xlsx": "financial_ratios",
    "market_cap.xlsx": "market_cap",
    "stock_prices.xlsx": "stock_prices",
}


# -----------------------------
# Clean Column Names
# -----------------------------
def clean_columns(df):
    "Clean columns."
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return df


# -----------------------------
# Create Database
# -----------------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    cursor.executescript(f.read())

conn.commit()

print("=" * 60)
print("Database Created Successfully")
print("=" * 60)
# -----------------------------
# Load Audit
# -----------------------------
audit = []
# -----------------------------
# Load Valid Company IDs
# -----------------------------
companies_df = pd.read_excel(os.path.join(RAW_DATA, "companies.xlsx"), header=1)

companies_df = clean_columns(companies_df)

valid_ids = set(companies_df["id"].astype(str).str.strip())

# -----------------------------
# Load Data into SQLite
# -----------------------------
for excel_file, table in TABLE_MAP.items():

    header = 1 if excel_file in HEADER1_FILES else 0

    file_path = os.path.join(RAW_DATA, excel_file)

    df = pd.read_excel(file_path, header=header)

    df = clean_columns(df)

    # Remove rows with invalid company_id
    if "company_id" in df.columns:

        before = len(df)

        df = df[df["company_id"].astype(str).str.strip().isin(valid_ids)]

        removed = before - len(df)

        if removed > 0:
            print(f"{table:<20} skipped {removed} invalid rows")

    df.to_sql(
        table,
        conn,
        if_exists="append",
        index=False,
    )

    print(f"{table:<20} {len(df):>5} rows loaded")

    audit.append(
        {
            "table_name": table,
            "rows_loaded": len(df),
            "status": "SUCCESS",
            "load_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
conn.commit()

# -----------------------------
# Verify Database
# -----------------------------
print("\n")
print("=" * 60)
print("Database Summary")
print("=" * 60)

for table in TABLE_MAP.values():

    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    print(f"{table:<20} {count}")

conn.close()
# -----------------------------
# Save Load Audit
# -----------------------------
audit_df = pd.DataFrame(audit)

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

audit_path = os.path.join(OUTPUT_DIR, "load_audit.csv")

audit_df.to_csv(audit_path, index=False)

print(f"\nLoad audit saved to: {audit_path}")
print("\nDatabase created successfully!")
