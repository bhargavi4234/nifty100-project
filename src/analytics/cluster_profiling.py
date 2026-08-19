import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR / "data" / "db" / "nifty100.db"
OUTPUT_DIR = ROOT_DIR / "output"
REPORT_DIR = ROOT_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]

# 10 KPIs for correlation/statistics
KPI_COLUMNS = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "return_on_capital_employed_pct",
]


def load_data():
    "Load data."
    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql_query(
        """
        SELECT *
        FROM financial_ratios
        """,
        conn,
    )

    sectors = pd.read_sql_query(
        """
        SELECT
            company_id,
            broad_sector,
            sub_sector
        FROM sectors
        """,
        conn,
    )

    companies = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        """,
        conn,
    )

    conn.close()

    return ratios, sectors, companies


def extract_year(value):
    "Extract year."
    if pd.isna(value):
        return np.nan

    for part in str(value).split():
        if part.isdigit() and len(part) == 4:
            return int(part)

    return np.nan


def latest_year_data(ratios):
    "Latest year data."
    df = ratios.copy()

    df["year_num"] = df["year"].apply(extract_year)

    df = df.dropna(subset=["year_num"])

    df["year_num"] = df["year_num"].astype(int)

    # Remove duplicate company-year records
    df = df.sort_values(["company_id", "year_num"]).drop_duplicates(
        subset=["company_id", "year_num"],
        keep="last",
    )

    # Latest year per company
    latest = (
        df.sort_values(["company_id", "year_num"]).groupby("company_id").tail(1).copy()
    )

    return latest


def load_cluster_labels():
    "Load cluster labels."
    path = OUTPUT_DIR / "cluster_labels.csv"

    if not path.exists():
        raise FileNotFoundError(
            "output/cluster_labels.csv not found. " "Run Day 36 first."
        )

    return pd.read_csv(path)


def generate_cluster_profile(df):
    "Generate cluster profile."
    rows = []

    for cluster_id, group in df.groupby("cluster_id"):

        row = {
            "cluster_id": cluster_id,
            "cluster_name": group["cluster_name"].iloc[0],
            "company_count": len(group),
        }

        for feature in FEATURES:
            row[f"{feature}_mean"] = group[feature].mean()
            row[f"{feature}_median"] = group[feature].median()

        rows.append(row)

    profile = pd.DataFrame(rows)

    profile.to_csv(
        OUTPUT_DIR / "cluster_profile.csv",
        index=False,
    )

    return profile


def generate_correlation_heatmap(latest):
    "Generate correlation heatmap."
    correlation = latest[KPI_COLUMNS].corr(method="pearson")

    plt.figure(figsize=(12, 9))

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
    )

    plt.title("Pearson Correlation Matrix - 10 KPIs")

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "correlation_heatmap.png",
        dpi=200,
    )

    plt.close()


def generate_outlier_report(latest, sectors, companies):
    "Generate outlier report."
    df = latest[["company_id"] + KPI_COLUMNS].copy()

    # Add sector
    sector_data = sectors[["company_id", "broad_sector"]].drop_duplicates("company_id")

    df = df.merge(
        sector_data,
        on="company_id",
        how="left",
    )

    # Add company name
    df = df.merge(
        companies,
        on="company_id",
        how="left",
    )

    outlier_rows = []

    for sector, group in df.groupby("broad_sector"):

        group = group.copy()

        for metric in KPI_COLUMNS:

            values = group[metric]

            mean = values.mean()
            std = values.std()

            if pd.isna(std) or std == 0:
                group[f"{metric}_zscore"] = 0.0
            else:
                group[f"{metric}_zscore"] = (values - mean) / std

        zscore_columns = [f"{metric}_zscore" for metric in KPI_COLUMNS]

        for _, row in group.iterrows():

            flagged = []

            for metric in KPI_COLUMNS:

                z = row[f"{metric}_zscore"]

                if abs(z) > 3:
                    flagged.append(metric)

            if flagged:

                outlier_rows.append(
                    {
                        "company_id": row["company_id"],
                        "company_name": row["company_name"],
                        "broad_sector": sector,
                        "flagged_metrics": ", ".join(flagged),
                        "max_abs_zscore": max(abs(row[col]) for col in zscore_columns),
                    }
                )

    outliers = pd.DataFrame(outlier_rows)

    if outliers.empty:
        outliers = pd.DataFrame(
            columns=[
                "company_id",
                "company_name",
                "broad_sector",
                "flagged_metrics",
                "max_abs_zscore",
            ]
        )

    outliers.to_csv(
        OUTPUT_DIR / "outlier_report.csv",
        index=False,
    )

    return outliers


def generate_portfolio_stats(latest):
    "Generate portfolio stats."
    rows = []

    for metric in KPI_COLUMNS:

        series = latest[metric].dropna()

        rows.append(
            {
                "kpi": metric,
                "P10": series.quantile(0.10),
                "P25": series.quantile(0.25),
                "P50": series.quantile(0.50),
                "P75": series.quantile(0.75),
                "P90": series.quantile(0.90),
                "Mean": series.mean(),
                "Std": series.std(),
            }
        )

    stats = pd.DataFrame(rows)

    stats.to_csv(
        OUTPUT_DIR / "portfolio_stats.csv",
        index=False,
    )

    return stats


def main():
    "Main."

    ratios, sectors, companies = load_data()

    latest = latest_year_data(ratios)

    clusters = load_cluster_labels()

    # ---------------------------------------------------------
    # Add FCF CAGR from Day 36
    # ---------------------------------------------------------

    cluster_features = clusters[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ].copy()

    # ---------------------------------------------------------
    # Cluster profiling
    # ---------------------------------------------------------

    profile_data = cluster_features.copy()

    # Add the four features available directly
    profile_data = profile_data.merge(
        latest[
            [
                "company_id",
                "return_on_equity_pct",
                "debt_to_equity",
                "revenue_cagr_5yr",
                "operating_profit_margin_pct",
            ]
        ],
        on="company_id",
        how="left",
    )

    # FCF CAGR was calculated during Day 36.
    # Recalculate it here from the historical FCF data.

    fcf_data = ratios[
        [
            "company_id",
            "year",
            "free_cash_flow_cr",
        ]
    ].copy()

    fcf_data["year_num"] = fcf_data["year"].apply(extract_year)

    fcf_data = fcf_data.dropna(subset=["year_num"])

    fcf_data["year_num"] = fcf_data["year_num"].astype(int)

    fcf_data = fcf_data.groupby(
        ["company_id", "year_num"],
        as_index=False,
    )["free_cash_flow_cr"].mean()

    fcf_cagr_rows = []

    for company_id, group in fcf_data.groupby("company_id"):

        group = group.sort_values("year_num")

        latest_year = group["year_num"].max()
        beginning_year = latest_year - 5

        start = group[group["year_num"] == beginning_year]

        end = group[group["year_num"] == latest_year]

        if start.empty or end.empty:
            cagr = np.nan

        else:
            start_fcf = start.iloc[0]["free_cash_flow_cr"]
            end_fcf = end.iloc[0]["free_cash_flow_cr"]

            if pd.isna(start_fcf) or pd.isna(end_fcf) or start_fcf <= 0 or end_fcf <= 0:
                cagr = np.nan

            else:
                cagr = ((end_fcf / start_fcf) ** (1 / 5) - 1) * 100

        fcf_cagr_rows.append(
            {
                "company_id": company_id,
                "fcf_cagr_5yr": cagr,
            }
        )

    fcf_cagr = pd.DataFrame(fcf_cagr_rows)

    profile_data = profile_data.merge(
        fcf_cagr,
        on="company_id",
        how="left",
    )

    # ---------------------------------------------------------
    # Cluster profile
    # ---------------------------------------------------------

    generate_cluster_profile(profile_data)

    # ---------------------------------------------------------
    # Correlation heatmap
    # ---------------------------------------------------------

    generate_correlation_heatmap(latest)

    # ---------------------------------------------------------
    # Outlier detection
    # ---------------------------------------------------------

    generate_outlier_report(
        latest,
        sectors,
        companies,
    )

    # ---------------------------------------------------------
    # Portfolio statistics
    # ---------------------------------------------------------

    generate_portfolio_stats(latest)

    print("Day 37 completed.")


if __name__ == "__main__":
    main()
