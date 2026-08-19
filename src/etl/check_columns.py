import os

import pandas as pd

RAW_DATA = "data/raw"

HEADER1_FILES = {
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
}

files = [
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
    "financial_ratios.xlsx",
    "market_cap.xlsx",
    "peer_groups.xlsx",
    "sectors.xlsx",
    "stock_prices.xlsx",
]

for file in files:

    header = 1 if file in HEADER1_FILES else 0

    print(f"\n{'='*60}")
    print(file)
    print("=" * 60)

    df = pd.read_excel(os.path.join(RAW_DATA, file), header=header)

    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")

    print(df.columns.tolist())
