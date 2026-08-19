"""
Day 36 - KMeans Clustering

Features:
- return_on_equity_pct
- debt_to_equity
- revenue_cagr_5yr
- fcf_cagr_5yr
- operating_profit_margin_pct

Process:
1. Use all 92 companies from sectors table
2. Get latest available financial ratios
3. Calculate 5-year FCF CAGR
4. Impute missing values using sector median
5. StandardScaler
6. KMeans with 5 clusters
7. Generate elbow plot for k=2 to 10
8. Generate cluster_labels.csv
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DB_PATH = ROOT_DIR / "data" / "db" / "nifty100.db"
OUTPUT_DIR = ROOT_DIR / "output"
REPORT_DIR = ROOT_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

N_CLUSTERS = 5
RANDOM_STATE = 42

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# LOAD DATA
# ============================================================


def load_data():
    """
    Load financial ratios and sector information.

    The sectors table contains all 92 companies and is therefore
    used as the base population.
    """

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            debt_to_equity,
            revenue_cagr_5yr,
            operating_profit_margin_pct,
            free_cash_flow_cr
        FROM financial_ratios
        """,
        conn,
    )

    sectors = pd.read_sql_query(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        conn,
    )

    conn.close()

    return ratios, sectors


# ============================================================
# YEAR PARSING
# ============================================================


def extract_year(year_value):
    """
    Extract numeric year from values such as:

        Mar 2024
        Dec 2023
        Jun 2019
    """

    if pd.isna(year_value):
        return np.nan

    text = str(year_value)

    for part in text.split():
        if part.isdigit() and len(part) == 4:
            return int(part)

    return np.nan


# ============================================================
# FCF CAGR
# ============================================================


def calculate_fcf_cagr(ratios):
    """
    Calculate 5-year FCF CAGR for each company.

    CAGR:

        ((Ending FCF / Beginning FCF) ** (1/5) - 1) * 100

    If beginning or ending FCF is <= 0, CAGR is treated as
    missing and will later be imputed using sector median.
    """

    fcf = ratios[
        [
            "company_id",
            "year",
            "free_cash_flow_cr",
        ]
    ].copy()

    # Extract numeric year
    fcf["year_num"] = fcf["year"].apply(extract_year)

    # Remove invalid years
    fcf = fcf.dropna(subset=["year_num"])

    fcf["year_num"] = fcf["year_num"].astype(int)

    # --------------------------------------------------------
    # Remove duplicate company-year records
    # --------------------------------------------------------

    fcf = fcf.groupby(
        [
            "company_id",
            "year_num",
        ],
        as_index=False,
    )["free_cash_flow_cr"].mean()

    results = []

    # --------------------------------------------------------
    # Calculate CAGR company by company
    # --------------------------------------------------------

    for company_id, group in fcf.groupby("company_id"):

        group = group.sort_values("year_num")

        latest_year = int(group["year_num"].max())

        beginning_year = latest_year - 5

        latest_rows = group[group["year_num"] == latest_year]

        beginning_rows = group[group["year_num"] == beginning_year]

        if latest_rows.empty or beginning_rows.empty:
            cagr = np.nan

        else:

            beginning_fcf = beginning_rows.iloc[0]["free_cash_flow_cr"]

            ending_fcf = latest_rows.iloc[0]["free_cash_flow_cr"]

            # CAGR is not meaningful when
            # either endpoint is zero/negative.
            if (
                pd.isna(beginning_fcf)
                or pd.isna(ending_fcf)
                or beginning_fcf <= 0
                or ending_fcf <= 0
            ):
                cagr = np.nan

            else:
                cagr = ((ending_fcf / beginning_fcf) ** (1 / 5) - 1) * 100

        results.append(
            {
                "company_id": company_id,
                "fcf_cagr_5yr": cagr,
            }
        )

    return pd.DataFrame(results)


# ============================================================
# PREPARE COMPANY DATA
# ============================================================


def prepare_company_data(
    ratios,
    sectors,
):
    """
    Create exactly one row per company.

    IMPORTANT:
    The sectors table is the base table so all 92 companies
    remain in the clustering dataset.

    Companies with no financial-ratio records will have
    missing financial metrics and will be handled by
    sector-median imputation.
    """

    ratios = ratios.copy()
    sectors = sectors.copy()

    # --------------------------------------------------------
    # Parse years
    # --------------------------------------------------------

    ratios["year_num"] = ratios["year"].apply(extract_year)

    # --------------------------------------------------------
    # Remove duplicate company-year records
    # --------------------------------------------------------

    ratios = ratios.sort_values(
        [
            "company_id",
            "year_num",
        ]
    ).drop_duplicates(
        subset=[
            "company_id",
            "year_num",
        ],
        keep="last",
    )

    # --------------------------------------------------------
    # Latest available financial observation
    # --------------------------------------------------------

    latest = (
        ratios.sort_values(
            [
                "company_id",
                "year_num",
            ]
        )
        .groupby("company_id")
        .tail(1)
        .copy()
    )

    # --------------------------------------------------------
    # Calculate FCF CAGR
    # --------------------------------------------------------

    fcf_cagr = calculate_fcf_cagr(ratios)

    latest = latest.merge(
        fcf_cagr,
        on="company_id",
        how="left",
    )

    # --------------------------------------------------------
    # Prepare sector data
    # --------------------------------------------------------

    sectors = (
        sectors[
            [
                "company_id",
                "broad_sector",
            ]
        ]
        .drop_duplicates(subset=["company_id"])
        .rename(columns={"broad_sector": "sector"})
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # LEFT JOIN from all companies/sectors
    # --------------------------------------------------------

    result = sectors.merge(
        latest[
            [
                "company_id",
                "return_on_equity_pct",
                "debt_to_equity",
                "revenue_cagr_5yr",
                "operating_profit_margin_pct",
                "fcf_cagr_5yr",
            ]
        ],
        on="company_id",
        how="left",
    )

    # --------------------------------------------------------
    # Final feature columns
    # --------------------------------------------------------

    result = result[
        [
            "company_id",
            "sector",
        ]
        + FEATURES
    ]

    return result


# ============================================================
# SECTOR MEDIAN IMPUTATION
# ============================================================


def impute_sector_medians(df):
    """
    Impute missing values using sector-specific medians.

    If a sector has no valid value for a feature, use the
    overall median as a fallback.
    """

    df = df.copy()

    for feature in FEATURES:

        # Calculate median within each sector
        sector_medians = df.groupby("sector")[feature].transform("median")

        # Fill using sector median
        df[feature] = df[feature].fillna(sector_medians)

        # Overall median fallback
        overall_median = df[feature].median()

        df[feature] = df[feature].fillna(overall_median)

    return df


# ============================================================
# STANDARD SCALER
# ============================================================


def scale_features(df):
    """
    Standardize all clustering features to zero mean
    and unit variance.
    """

    scaler = StandardScaler()

    X = df[FEATURES].copy()

    X_scaled = scaler.fit_transform(X)

    return X_scaled, scaler


# ============================================================
# KMEANS
# ============================================================


def run_kmeans(X_scaled):
    """
    Run KMeans with 5 clusters and random_state=42.
    """

    model = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=RANDOM_STATE,
        n_init=10,
    )

    labels = model.fit_predict(X_scaled)

    return model, labels


# ============================================================
# DISTANCE FROM CENTROID
# ============================================================


def calculate_distances(
    model,
    X_scaled,
    labels,
):
    """
    Calculate Euclidean distance from each company to
    its assigned cluster centroid.
    """

    distances = model.transform(X_scaled)

    assigned_distances = distances[
        np.arange(len(X_scaled)),
        labels,
    ]

    return assigned_distances


# ============================================================
# CLUSTER NAMES
# ============================================================


def assign_cluster_names(
    df,
    labels,
):
    """
    Assign descriptive names based on cluster characteristics.

    KMeans cluster IDs are arbitrary, so the names are based on
    relative financial characteristics rather than assuming that
    cluster 0 is automatically the best cluster.
    """

    analysis = df[FEATURES].copy()

    analysis["cluster_id"] = labels

    summary = analysis.groupby("cluster_id")[FEATURES].mean()

    # Higher is better:
    # ROE, revenue CAGR, FCF CAGR, OPM
    #
    # Lower is better:
    # debt-to-equity

    score = (
        summary["return_on_equity_pct"].rank(pct=True)
        + summary["revenue_cagr_5yr"].rank(pct=True)
        + summary["fcf_cagr_5yr"].rank(pct=True)
        + summary["operating_profit_margin_pct"].rank(pct=True)
        + (1 - summary["debt_to_equity"].rank(pct=True))
    )

    ranked_clusters = score.sort_values(ascending=False).index.tolist()

    names = {}

    name_order = [
        "High Quality Compounders",
        "Growth Leaders",
        "Balanced Performers",
        "Value / Moderate",
        "Weak / High Risk",
    ]

    for position, cluster_id in enumerate(ranked_clusters):

        if position < len(name_order):

            names[cluster_id] = name_order[position]

        else:

            names[cluster_id] = f"Cluster {cluster_id}"

    return names, summary


# ============================================================
# ELBOW PLOT
# ============================================================


def generate_elbow_plot(
    X_scaled,
):
    """
    Calculate inertia for k=2 through k=10
    and save the elbow plot.
    """

    k_values = list(range(2, 11))

    inertias = []

    for k in k_values:

        model = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=10,
        )

        model.fit(X_scaled)

        inertias.append(model.inertia_)

    # --------------------------------------------------------
    # Create plot
    # --------------------------------------------------------

    plt.figure(figsize=(9, 6))

    plt.plot(
        k_values,
        inertias,
        marker="o",
    )

    plt.xlabel("Number of Clusters (k)")

    plt.ylabel("Inertia")

    plt.title("KMeans Elbow Plot")

    plt.xticks(k_values)

    plt.grid(
        True,
        alpha=0.3,
    )

    output_path = REPORT_DIR / "elbow_plot.png"

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=200,
    )

    plt.close()

    return (
        k_values,
        inertias,
    )


# ============================================================
# MAIN
# ============================================================


def main():
    "Main."

    print("=" * 70)

    print("DAY 36 - KMEANS CLUSTERING")

    print("=" * 70)

    # --------------------------------------------------------
    # 1. LOAD
    # --------------------------------------------------------

    print("\n[1/7] Loading database...")

    ratios, sectors = load_data()

    print(f"Financial ratio rows: " f"{len(ratios):,}")

    print(f"Sector rows: " f"{len(sectors):,}")

    # --------------------------------------------------------
    # 2. PREPARE
    # --------------------------------------------------------

    print("\n[2/7] Preparing company-level dataset...")

    df = prepare_company_data(
        ratios,
        sectors,
    )

    print(f"Companies: " f"{df['company_id'].nunique():,}")

    print(f"Rows: " f"{len(df):,}")

    # Verify expected population
    if len(df) != 92:

        raise ValueError(f"Expected 92 companies, " f"but found {len(df)}.")

    # --------------------------------------------------------
    # 3. MISSING VALUES
    # --------------------------------------------------------

    print("\n[3/7] Missing values before " "sector-median imputation:")

    print(df[FEATURES].isna().sum())

    # --------------------------------------------------------
    # 4. IMPUTE
    # --------------------------------------------------------

    print("\n[4/7] Applying sector median imputation...")

    df = impute_sector_medians(df)

    print("\nMissing values after imputation:")

    print(df[FEATURES].isna().sum())

    remaining_missing = df[FEATURES].isna().sum().sum()

    if remaining_missing > 0:

        raise ValueError("Missing values remain after " "sector median imputation.")

    # --------------------------------------------------------
    # 5. SCALE
    # --------------------------------------------------------

    print("\n[5/7] Applying StandardScaler...")

    X_scaled, _ = scale_features(df)

    print("Features scaled to approximately " "zero mean and unit variance.")

    # --------------------------------------------------------
    # 6. ELBOW
    # --------------------------------------------------------

    print("\n[6/7] Generating elbow plot...")

    k_values, inertias = generate_elbow_plot(X_scaled)

    print("\nInertia values:")

    for k, inertia in zip(
        k_values,
        inertias,
    ):

        print(f"k={k}: " f"inertia={inertia:.2f}")

    print("\nElbow plot saved to:")

    print(REPORT_DIR / "elbow_plot.png")

    # --------------------------------------------------------
    # FINAL KMEANS
    # --------------------------------------------------------

    print("\nRunning final KMeans with k=5...")

    model, labels = run_kmeans(X_scaled)

    # --------------------------------------------------------
    # DISTANCES
    # --------------------------------------------------------

    distances = calculate_distances(
        model,
        X_scaled,
        labels,
    )

    # --------------------------------------------------------
    # CLUSTER NAMES
    # --------------------------------------------------------

    cluster_names, cluster_summary = assign_cluster_names(
        df,
        labels,
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    output = pd.DataFrame(
        {
            "company_id": df["company_id"],
            "cluster_id": labels,
            "cluster_name": [cluster_names[label] for label in labels],
            "distance_from_centroid": distances,
        }
    )

    output = output.sort_values(
        [
            "cluster_id",
            "distance_from_centroid",
        ]
    )

    output_path = OUTPUT_DIR / "cluster_labels.csv"

    output.to_csv(
        output_path,
        index=False,
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    print("\nCluster counts:")

    print(output["cluster_id"].value_counts().sort_index())

    print("\nCluster names:")

    for cluster_id in sorted(cluster_names):

        print(f"{cluster_id}: " f"{cluster_names[cluster_id]}")

    print("\nCluster summary:")

    print(cluster_summary.round(2))

    print("\nOutput saved to:")

    print(output_path)


if __name__ == "__main__":
    main()
