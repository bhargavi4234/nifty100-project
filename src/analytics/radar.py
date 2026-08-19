import os
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ------------------------------------------------------
# Paths
# ------------------------------------------------------

DB_PATH = "data/db/nifty100.db"
OUTPUT_DIR = "reports/radar_charts"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True,
)

# ------------------------------------------------------
# Radar Plot Function
# ------------------------------------------------------


def plot_radar(
    company_name,
    labels,
    company_values,
    peer_values,
    output_file,
):
    """
    Plot radar chart for one company.
    """

    N = len(labels)

    angles = np.linspace(
        0,
        2 * np.pi,
        N,
        endpoint=False,
    ).tolist()

    company_values = company_values.tolist()
    peer_values = peer_values.tolist()

    company_values += company_values[:1]
    peer_values += peer_values[:1]
    angles += angles[:1]

    plt.figure(figsize=(8, 8))

    ax = plt.subplot(
        111,
        polar=True,
    )

    ax.plot(
        angles,
        company_values,
        linewidth=2,
        label=company_name,
    )

    ax.fill(
        angles,
        company_values,
        alpha=0.25,
    )

    ax.plot(
        angles,
        peer_values,
        "--",
        linewidth=2,
        label="Peer Average",
    )

    ax.set_xticks(angles[:-1])

    ax.set_xticklabels(
        labels,
        fontsize=10,
    )

    ax.set_ylim(0, 100)

    plt.title(
        company_name,
        fontsize=14,
    )

    plt.legend(
        loc="upper right",
    )

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=150,
    )

    plt.close()


# ------------------------------------------------------
# Main
# ------------------------------------------------------

if __name__ == "__main__":

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        fr.company_id,
        fr.year,

        fr.return_on_equity_pct,
        fr.return_on_capital_employed_pct,
        fr.net_profit_margin_pct,
        fr.debt_to_equity,
        fr.free_cash_flow_cr,
        fr.pat_cagr_5yr,
        fr.revenue_cagr_5yr,
        fr.composite_quality_score,

        pg.peer_group_name

    FROM financial_ratios fr

    LEFT JOIN peer_groups pg
        ON fr.company_id = pg.company_id
    """

    df = pd.read_sql(query, conn)

    conn.close()

    metrics = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "pat_cagr_5yr",
        "revenue_cagr_5yr",
        "composite_quality_score",
    ]

    # Convert metrics to numeric
    for col in metrics:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    # Scale every metric to 0–100
    for col in metrics:

        minimum = df[col].min()
        maximum = df[col].max()

        if pd.isna(minimum) or minimum == maximum:
            df[col] = 50
            continue

        df[col] = ((df[col] - minimum) / (maximum - minimum)) * 100

    labels = [
        "ROE",
        "ROCE",
        "NPM",
        "D/E",
        "FCF",
        "PAT CAGR",
        "Revenue CAGR",
        "Composite",
    ]

    grouped = df.groupby("peer_group_name")

    total = 0

    for _, row in df.iterrows():

        company = row["company_id"]
        peer_group = row["peer_group_name"]

        company_values = row[metrics].fillna(0)

        # -----------------------------------------
        # Company belongs to a peer group
        # -----------------------------------------

        if pd.notna(peer_group):

            peer_avg = grouped.get_group(peer_group)[metrics].mean().fillna(0)

        # -----------------------------------------
        # No peer group → compare with Nifty100 average
        # -----------------------------------------

        else:

            peer_avg = df[metrics].mean().fillna(0)

        filename = os.path.join(
            OUTPUT_DIR,
            f"{company}_radar.png",
        )

        plot_radar(
            company_name=company,
            labels=labels,
            company_values=company_values,
            peer_values=peer_avg,
            output_file=filename,
        )

        total += 1

    print("\n====================================")
    print(f"Radar charts generated : {total}")
    print(f"Saved to : {OUTPUT_DIR}")
    print("====================================")
