import os

import pandas as pd

RAW_DATA = "data/raw"
OUTPUT = "output"

HEADER1_FILES = {
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
}


def load_excel(file_name):
    "Load excel."
    file_path = os.path.join(RAW_DATA, file_name)

    header = 1 if file_name in HEADER1_FILES else 0

    df = pd.read_excel(file_path, header=header)

    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")

    return df


def save_failures(df):
    "Save failures."
    os.makedirs(OUTPUT, exist_ok=True)

    output_file = os.path.join(OUTPUT, "validation_failures.csv")

    df.to_csv(output_file, index=False)

    print(f"\nValidation report saved to: {output_file}")


# =====================================================
# DQ-01 Primary Key Uniqueness
# =====================================================


def dq01_primary_key(df):
    "Dq01 primary key."

    failures = []

    duplicates = df[df["id"].duplicated(keep=False)]

    for _, row in duplicates.iterrows():

        failures.append(
            {
                "rule": "DQ-01",
                "severity": "CRITICAL",
                "table": "companies",
                "record_id": row["id"],
                "message": "Duplicate Primary Key",
            }
        )

    return failures


# =====================================================
# DQ-02 company_id + year uniqueness
# =====================================================


def dq02_company_year(df, table_name):
    "Dq02 company year."

    failures = []

    duplicates = df[df.duplicated(subset=["company_id", "year"], keep=False)]

    for _, row in duplicates.iterrows():

        failures.append(
            {
                "rule": "DQ-02",
                "severity": "CRITICAL",
                "table": table_name,
                "record_id": row["id"],
                "message": "Duplicate company_id + year",
            }
        )

    return failures


# =====================================================
# DQ-03 Foreign Key Integrity
# =====================================================


def dq03_foreign_key(df, table_name, valid_company_ids):
    "Dq03 foreign key."

    failures = []

    company_ids = df["company_id"].astype(str).str.strip().str.upper()

    invalid_rows = df.loc[~company_ids.isin(valid_company_ids)]

    for _, row in invalid_rows.iterrows():

        failures.append(
            {
                "rule": "DQ-03",
                "severity": "CRITICAL",
                "table": table_name,
                "record_id": row["id"],
                "message": f"Invalid company_id : {row['company_id']}",
            }
        )

    return failures


# =====================================================
# DQ-04 Balance Sheet Balance (<1%)
# =====================================================


def dq04_balance_sheet(df):
    "Dq04 balance sheet."

    failures = []

    difference_pct = (
        (df["total_assets"] - df["total_liabilities"]).abs() / df["total_assets"]
    ) * 100

    invalid_rows = df.loc[difference_pct > 1]

    for _, row in invalid_rows.iterrows():

        failures.append(
            {
                "rule": "DQ-04",
                "severity": "WARNING",
                "table": "balancesheet",
                "record_id": row["id"],
                "message": "Balance Sheet mismatch > 1%",
            }
        )

    return failures


# =====================================================
# DQ-05 OPM Cross Check
# =====================================================


def dq05_opm_crosscheck(df):
    "Dq05 opm crosscheck."

    failures = []

    expected_op = df["sales"] - df["expenses"]

    op_diff = ((expected_op - df["operating_profit"]).abs() / df["sales"]) * 100

    expected_opm = (df["operating_profit"] / df["sales"]) * 100

    opm_diff = (expected_opm - df["opm_percentage"]).abs()

    invalid_rows = df.loc[(op_diff > 1) | (opm_diff > 1)]

    for _, row in invalid_rows.iterrows():

        failures.append(
            {
                "rule": "DQ-05",
                "severity": "WARNING",
                "table": "profitandloss",
                "record_id": row["id"],
                "message": "OPM cross-check failed",
            }
        )

    return failures


def dq06_positive_sales(df):
    "Dq06 positive sales."

    failures = []

    non_bank = ~df["company_id"].str.contains(
        "BANK|FINANCE|FINANCIAL|INSURANCE|NBFC",
        case=False,
        na=False,
    )

    invalid = df[non_bank & (df["sales"] <= 0)]

    for _, row in invalid.iterrows():

        failures.append(
            {
                "rule": "DQ-06",
                "severity": "WARNING",
                "table": "profitandloss",
                "record_id": row["id"],
                "message": "Sales <= 0",
            }
        )

    return failures


# =====================================================
# DQ-07 Reporting Period Format Validation
# =====================================================


def dq07_year_format(df):
    "Dq07 year format."

    failures = []

    pattern = r"^(Mar|Jun|Sep|Dec) \d{4}( 9m)?$|^TTM$"

    invalid = df[~df["year"].astype(str).str.match(pattern, na=False)]

    for _, row in invalid.iterrows():

        failures.append(
            {
                "rule": "DQ-07",
                "severity": "WARNING",
                "table": "profitandloss",
                "record_id": row["id"],
                "message": "Invalid reporting period format",
            }
        )

    return failures


# =====================================================
# DQ-08 NSE Ticker Format Validation
# =====================================================


def dq08_ticker_format(df):
    "Dq08 ticker format."

    failures = []

    invalid = df[~df["id"].astype(str).str.fullmatch(r"[A-Z&-]+")]

    for _, row in invalid.iterrows():

        failures.append(
            {
                "rule": "DQ-08",
                "severity": "WARNING",
                "table": "companies",
                "record_id": row["id"],
                "message": "Invalid NSE ticker format",
            }
        )

    return failures


# =====================================================
# DQ-09 Net Cash Flow Validation
# =====================================================


def dq09_net_cash(df):
    "Dq09 net cash."

    failures = []

    expected_net_cash = (
        df["operating_activity"] + df["investing_activity"] + df["financing_activity"]
    )

    difference = (expected_net_cash - df["net_cash_flow"]).abs()

    invalid = df[difference > 1]

    for _, row in invalid.iterrows():

        failures.append(
            {
                "rule": "DQ-09",
                "severity": "WARNING",
                "table": "cashflow",
                "record_id": row["id"],
                "message": "Net cash flow mismatch",
            }
        )

    return failures


# =====================================================
# DQ-10 Fixed Assets Validation
# =====================================================
def dq10_fixed_assets(df):
    "Dq10 fixed assets."

    failures = []

    invalid = df[df["fixed_assets"] > df["total_assets"]]

    for _, row in invalid.iterrows():

        failures.append(
            {
                "rule": "DQ-10",
                "severity": "WARNING",
                "table": "balancesheet",
                "record_id": row["id"],
                "message": "Fixed assets exceed total assets",
            }
        )

    return failures


# =====================================================
# DQ-11 Tax Rate Validation
# =====================================================


def dq11_tax_rate(df):
    "Dq11 tax rate."

    failures = []

    invalid = df[(df["tax_percentage"] < -100) | (df["tax_percentage"] > 100)]

    for _, row in invalid.iterrows():

        failures.append(
            {
                "rule": "DQ-11",
                "severity": "WARNING",
                "table": "profitandloss",
                "record_id": row["id"],
                "message": "Invalid tax percentage",
            }
        )

    return failures


# =====================================================
# DQ-12 Dividend Payout Validation
# =====================================================


def dq12_dividend_payout(df):
    "Dq12 dividend payout."

    failures = []

    invalid = df[df["dividend_payout"] == -999]

    for _, row in invalid.iterrows():

        failures.append(
            {
                "rule": "DQ-12",
                "severity": "WARNING",
                "table": "profitandloss",
                "record_id": row["id"],
                "message": "Invalid dividend payout value (-999)",
            }
        )

    return failures


# =====================================================
# DQ-13 URL Validation
# =====================================================


def dq13_url_validation(df):
    "Dq13 url validation."

    failures = []

    url_columns = [
        "website",
        "nse_profile",
        "bse_profile",
        "chart_link",
        "company_logo",
    ]

    for column in url_columns:

        invalid = df[
            df[column].notna()
            & ~df[column].astype(str).str.startswith(("http://", "https://"))
        ]

        for _, row in invalid.iterrows():

            failures.append(
                {
                    "rule": "DQ-13",
                    "severity": "WARNING",
                    "table": "companies",
                    "record_id": row["id"],
                    "message": f"Invalid URL in {column}",
                }
            )

    return failures


# =====================================================
# DQ-14 EPS Sign Validation
# =====================================================


def dq14_eps_sign(df):
    "Dq14 eps sign."

    failures = []

    invalid = df[
        ((df["net_profit"] > 0) & (df["eps"] < 0))
        | ((df["net_profit"] < 0) & (df["eps"] > 0))
    ]

    for _, row in invalid.iterrows():

        failures.append(
            {
                "rule": "DQ-14",
                "severity": "WARNING",
                "table": "profitandloss",
                "record_id": row["id"],
                "message": "EPS sign does not match Net Profit",
            }
        )

    return failures


# =====================================================
# DQ-15 Liability Total Validation
# =====================================================


def dq15_liability_total(df):
    "Dq15 liability total."

    failures = []

    expected = (
        df["equity_capital"]
        + df["reserves"]
        + df["borrowings"]
        + df["other_liabilities"]
    )

    invalid = df[(expected - df["total_liabilities"]).abs() > 1]

    for _, row in invalid.iterrows():

        failures.append(
            {
                "rule": "DQ-15",
                "severity": "WARNING",
                "table": "balancesheet",
                "record_id": row["id"],
                "message": "Liability components do not match Total Liabilities",
            }
        )

    return failures


# =====================================================
# DQ-16 Coverage Validation
# =====================================================


def dq16_coverage(companies, profit, balance, cash):
    "Dq16 coverage."

    failures = []

    tables = {
        "companies": companies,
        "profitandloss": profit,
        "balancesheet": balance,
        "cashflow": cash,
    }

    for table_name, df in tables.items():

        if df.empty:

            failures.append(
                {
                    "rule": "DQ-16",
                    "severity": "CRITICAL",
                    "table": table_name,
                    "record_id": None,
                    "message": "Table contains no records",
                }
            )

    return failures


def main():
    "Main."

    print("=" * 60)
    print("Running Data Quality Validation")
    print("=" * 60)

    companies = load_excel("companies.xlsx")

    profit = load_excel("profitandloss.xlsx")

    balance = load_excel("balancesheet.xlsx")

    cash = load_excel("cashflow.xlsx")

    analysis = load_excel("analysis.xlsx")

    documents = load_excel("documents.xlsx")

    pros = load_excel("prosandcons.xlsx")

    failures = []

    # -------------------------
    # DQ-01
    # -------------------------

    failures.extend(dq01_primary_key(companies))

    # -------------------------
    # DQ-02
    # -------------------------

    failures.extend(dq02_company_year(profit, "profitandloss"))

    failures.extend(dq02_company_year(balance, "balancesheet"))

    failures.extend(dq02_company_year(cash, "cashflow"))

    # -------------------------
    # DQ-03
    # -------------------------

    valid_company_ids = companies["id"].astype(str).str.strip().str.upper().unique()

    failures.extend(dq03_foreign_key(profit, "profitandloss", valid_company_ids))

    failures.extend(dq03_foreign_key(balance, "balancesheet", valid_company_ids))

    failures.extend(dq03_foreign_key(cash, "cashflow", valid_company_ids))

    failures.extend(dq03_foreign_key(analysis, "analysis", valid_company_ids))

    failures.extend(dq03_foreign_key(documents, "documents", valid_company_ids))

    failures.extend(dq03_foreign_key(pros, "prosandcons", valid_company_ids))
    # -------------------------
    # DQ-04
    # -------------------------

    failures.extend(dq04_balance_sheet(balance))

    # -------------------------
    # DQ-05
    # -------------------------

    failures.extend(dq05_opm_crosscheck(profit))

    # -------------------------
    # DQ-06
    # -------------------------

    failures.extend(dq06_positive_sales(profit))

    # -------------------------
    # DQ-07
    # -------------------------

    failures.extend(dq07_year_format(profit))
    # -------------------------
    # DQ-08
    # -------------------------

    failures.extend(dq08_ticker_format(companies))
    # -------------------------
    # DQ-09
    # -------------------------

    failures.extend(dq09_net_cash(cash))
    # -------------------------
    # DQ-10
    # -------------------------

    failures.extend(dq10_fixed_assets(balance))
    # -------------------------
    # DQ-11
    # -------------------------

    failures.extend(dq11_tax_rate(profit))
    # -------------------------
    # DQ-12
    # -------------------------

    failures.extend(dq12_dividend_payout(profit))

    # -------------------------
    # DQ-13
    # -------------------------

    failures.extend(dq13_url_validation(companies))

    # -------------------------
    # DQ-14
    # -------------------------

    failures.extend(dq14_eps_sign(profit))
    # -------------------------
    # DQ-15
    # -------------------------

    failures.extend(dq15_liability_total(balance))
    # -------------------------
    # DQ-16
    # -------------------------

    failures.extend(dq16_coverage(companies, profit, balance, cash))

    failures_df = pd.DataFrame(failures)

    save_failures(failures_df)

    print("=" * 60)
    print("Running Data Quality Validation")
    print("=" * 60)

    print("\nSummary")
    print("-" * 40)
    print("Total Failures Found :", len(failures_df))


if __name__ == "__main__":
    main()
