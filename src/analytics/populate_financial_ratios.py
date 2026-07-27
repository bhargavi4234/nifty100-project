import sqlite3
import os
import pandas as pd

from src.analytics.ratios import calculate_profitability_ratios
from src.analytics.cashflow import (
    free_cash_flow,
    cfo_quality_score
)
from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)

DB_PATH = "data/db/nifty100.db"

PL_FILE = "data/raw/profitandloss.xlsx"
BS_FILE = "data/raw/balancesheet.xlsx"
CF_FILE = "data/raw/cashflow.xlsx"
COMPANIES_FILE = "data/raw/companies.xlsx"

print("Loading Excel files...")

pl = pd.read_excel(PL_FILE, header=1)
bs = pd.read_excel(BS_FILE, header=1)
cf = pd.read_excel(CF_FILE, header=1)

companies = pd.read_excel(
    COMPANIES_FILE,
    header=1
)


print("Merging datasets...")

df = (
    pl.merge(
        bs,
        on=["company_id", "year"],
        how="inner",
        suffixes=("", "_bs")
    )
    .merge(
        cf,
        on=["company_id", "year"],
        how="inner",
        suffixes=("", "_cf")
    )
)


df = df.sort_values(
    ["company_id", "year"]
).reset_index(drop=True)

def compute_company_cagr(company_df):

    company_df = company_df.sort_values("year").copy()

    company_df["revenue_cagr_5yr"] = None
    company_df["pat_cagr_5yr"] = None
    company_df["eps_cagr_5yr"] = None

    for i in range(len(company_df)):

        if i < 5:
            continue

        start = company_df.iloc[i - 5]
        end = company_df.iloc[i]

        years = 5
        rev, _ = revenue_cagr(
            start["sales"],
            end["sales"],
            years,
            years
        )

        pat, _ = pat_cagr(
            start["net_profit"],
            end["net_profit"],
            years,
            years
        )

        eps, _ = eps_cagr(
            start["eps"],
            end["eps"],
            years,
            years
        )

        company_df.at[
            company_df.index[i],
            "revenue_cagr_5yr"
        ] = rev

        company_df.at[
            company_df.index[i],
            "pat_cagr_5yr"
        ] = pat

        company_df.at[
            company_df.index[i],
            "eps_cagr_5yr"
        ] = eps

    return company_df

frames = []

for company in df["company_id"].unique():

    company_df = df[df["company_id"] == company]

    frames.append(
        compute_company_cagr(company_df)
    )

df = pd.concat(frames).reset_index(drop=True)

print("CAGR calculated.")

company_lookup = (
    companies[
        ["id", "roce_percentage", "roe_percentage"]
    ]
    .set_index("id")
    .to_dict("index")
)


os.makedirs("output", exist_ok=True)

log_file = open(
    "output/ratio_edge_cases.log",
    "w",
    encoding="utf-8"
)

def score_profitability(roe, roce, npm):

    score = 0

    if roe is not None:
        if roe >= 20:
            score += 15
        elif roe >= 15:
            score += 12
        elif roe >= 10:
            score += 8

    if roce is not None:
        if roce >= 20:
            score += 10
        elif roce >= 15:
            score += 8
        elif roce >= 10:
            score += 5

    if npm is not None:
        if npm >= 20:
            score += 10
        elif npm >= 10:
            score += 7
        elif npm >= 5:
            score += 4

    return score


def score_growth(revenue_cagr, pat_cagr):

    score = 0

    if revenue_cagr is not None:
        if revenue_cagr >= 15:
            score += 10
        elif revenue_cagr >= 10:
            score += 7
        elif revenue_cagr >= 5:
            score += 4

    if pat_cagr is not None:
        if pat_cagr >= 15:
            score += 10
        elif pat_cagr >= 10:
            score += 7
        elif pat_cagr >= 5:
            score += 4

    return score


def score_leverage(de_ratio, icr):

    score = 0

    if de_ratio is not None:

        if de_ratio == 0:
            score += 10

        elif de_ratio <= 0.5:
            score += 8

        elif de_ratio <= 1:
            score += 7

        elif de_ratio <= 2:
            score += 5

    if icr is not None:

        if icr > 10:
            score += 5

        elif icr > 5:
            score += 4

        elif icr > 3:
            score += 3

    return score

records = []

for _, row in df.iterrows():

    ratios = calculate_profitability_ratios(row)

    company = company_lookup.get(row["company_id"])

    if company is None:
        log_file.write(
            f"{row['company_id']} | Data source issue | Company not found in companies.xlsx\n"
        )
        continue

    source_roce = company["roce_percentage"]
    source_roe = company["roe_percentage"]

    calc_roce = ratios["roce"]
    calc_roe = ratios["roe"]

        # ROCE comparison
    if (
        pd.notna(source_roce)
        and calc_roce is not None
        and abs(calc_roce - source_roce) > 5
    ):

        category = "Formula discrepancy"

        if source_roce < 1:
            category = "Data source issue"
        elif abs(calc_roce - source_roce) <= 10:
            category = "Version difference"

        log_file.write(
            f"{row['company_id']} | ROCE | "
            f"Calculated={calc_roce:.2f} | "
            f"Source={source_roce:.2f} | "
            f"Difference={abs(calc_roce-source_roce):.2f} | "
            f"Category={category}\n"
        )

    # ROE comparison
    if (
        pd.notna(source_roe)
        and calc_roe is not None
        and abs(calc_roe - source_roe) > 5
    ):

        category = "Formula discrepancy"

        if source_roe < 1:
            category = "Data source issue"
        elif abs(calc_roe - source_roe) <= 10:
            category = "Version difference"

        log_file.write(
            f"{row['company_id']} | ROE | "
            f"Calculated={calc_roe:.2f} | "
            f"Source={source_roe:.2f} | "
            f"Difference={abs(calc_roe-source_roe):.2f} | "
            f"Category={category}\n"
        )

    fcf = free_cash_flow(
        row["operating_activity"],
        row["investing_activity"]
    )

    cfo_ratio, _ = cfo_quality_score(
        row["operating_activity"],
        row["net_profit"]
    )

    cash_score = 0

    if cfo_ratio is not None and cfo_ratio > 1:
        cash_score += 10

    if fcf > 0:
        cash_score += 5

    profit_score = score_profitability(
        ratios["roe"],
        ratios["roce"],
        ratios["net_profit_margin"]
    )

    growth_score = score_growth(
        row["revenue_cagr_5yr"],
        row["pat_cagr_5yr"]
    )

    leverage_score = score_leverage(
        ratios["debt_to_equity"],
        ratios["interest_coverage_ratio"]
    )

    composite_score = (
        profit_score +
        cash_score +
        growth_score +
        leverage_score
    )


    records.append({

        "company_id": row["company_id"],
        "year": row["year"],

        "net_profit_margin_pct": ratios["net_profit_margin"],
        "operating_profit_margin_pct": ratios["operating_profit_margin"],
        "return_on_equity_pct": ratios["roe"],

        "debt_to_equity": ratios["debt_to_equity"],
        "interest_coverage": ratios["interest_coverage_ratio"],
        "asset_turnover": ratios["asset_turnover"],

        "free_cash_flow_cr": fcf,
        "capex_cr": abs(row["investing_activity"]),
        "earnings_per_share": row["eps"],

        "book_value_per_share":
            (row["equity_capital"] + row["reserves"]) /
            row["equity_capital"]
            if row["equity_capital"] != 0
            else None,

        "dividend_payout_ratio_pct":
            row["dividend_payout"],

        "total_debt_cr":
            row["borrowings"],

        "cash_from_operations_cr":
            row["operating_activity"],

        "revenue_cagr_5yr":
            row["revenue_cagr_5yr"],

        "pat_cagr_5yr":
            row["pat_cagr_5yr"],

        "eps_cagr_5yr":
            row["eps_cagr_5yr"],

        "composite_quality_score":
            composite_score
    })

print("Financial ratios calculated.")

print("Updating SQLite database...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

updated = 0

for record in records:

    cursor.execute("""
    UPDATE financial_ratios
    SET
        net_profit_margin_pct=?,
        operating_profit_margin_pct=?,
        return_on_equity_pct=?,
        debt_to_equity=?,
        interest_coverage=?,
        asset_turnover=?,
        free_cash_flow_cr=?,
        capex_cr=?,
        earnings_per_share=?,
        book_value_per_share=?,
        dividend_payout_ratio_pct=?,
        total_debt_cr=?,
        cash_from_operations_cr=?,
        revenue_cagr_5yr=?,
        pat_cagr_5yr=?,
        eps_cagr_5yr=?,
        composite_quality_score=?
    WHERE
        company_id=?
        AND year=?
    """, (

        record["net_profit_margin_pct"],
        record["operating_profit_margin_pct"],
        record["return_on_equity_pct"],
        record["debt_to_equity"],
        record["interest_coverage"],
        record["asset_turnover"],
        record["free_cash_flow_cr"],
        record["capex_cr"],
        record["earnings_per_share"],
        record["book_value_per_share"],
        record["dividend_payout_ratio_pct"],
        record["total_debt_cr"],
        record["cash_from_operations_cr"],
        record["revenue_cagr_5yr"],
        record["pat_cagr_5yr"],
        record["eps_cagr_5yr"],
        record["composite_quality_score"],

        record["company_id"],
        record["year"]

    ))

    updated += cursor.rowcount

conn.commit()

cursor.execute("SELECT COUNT(*) FROM financial_ratios")
row_count = cursor.fetchone()[0]

print("\n====================================")
print("Financial Ratio Population Complete")
print("====================================")
print(f"Rows Updated : {updated}")
print(f"Rows in Table: {row_count}")

log_file.close()
conn.close()