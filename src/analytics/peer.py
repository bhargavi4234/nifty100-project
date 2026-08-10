import sqlite3
import pandas as pd
import numpy as np


DB_PATH = "data/db/nifty100.db"


METRICS = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover",
]


def compute_percentile(series, inverse=False):
    """
    Compute percentile ranks.
    Lower values are better if inverse=True.
    """

    values = pd.to_numeric(series, errors="coerce")

    pct = values.rank(pct=True)

    if inverse:
        pct = 1 - pct

    return pct.round(4)


if __name__ == "__main__":

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            return_on_capital_employed_pct,
            net_profit_margin_pct,
            debt_to_equity,
            free_cash_flow_cr,
            pat_cagr_5yr,
            revenue_cagr_5yr,
            eps_cagr_5yr,
            interest_coverage,
            asset_turnover
        FROM financial_ratios
        """,
        conn,
    )

    peers = pd.read_sql(
        """
        SELECT
            peer_group_name,
            company_id,
            is_benchmark
        FROM peer_groups
        """,
        conn,
    )

    df = ratios.merge(
        peers,
        on="company_id",
        how="left",
    )

    missing = df["peer_group_name"].isna().sum()

    print(f"\nCompanies without peer group: {missing}")

    if missing > 0:
        print("No peer group assigned")

    results = []

    for group, group_df in df.groupby("peer_group_name", dropna=True):

        temp = group_df.copy()

        for metric in METRICS:

            inverse = metric == "debt_to_equity"

            temp[f"{metric}_percentile"] = compute_percentile(
                temp[metric],
                inverse=inverse,
            )

            subset = temp[
                [
                    "company_id",
                    "peer_group_name",
                    "year",
                    metric,
                    f"{metric}_percentile",
                ]
            ].rename(
                columns={
                    metric: "value",
                    f"{metric}_percentile": "percentile_rank",
                }
            )

            subset["metric"] = metric

            subset = subset[
                [
                    "company_id",
                    "peer_group_name",
                    "metric",
                    "value",
                    "percentile_rank",
                    "year",
                ]
            ]

            results.append(subset)

    peer_percentiles = pd.concat(
        results,
        ignore_index=True,
    )

    peer_percentiles.to_sql(
        "peer_percentiles",
        conn,
        if_exists="replace",
        index=False,
    )

    print("\nRows created:", len(peer_percentiles))
    print("\npeer_percentiles table created successfully.")

    conn.close()