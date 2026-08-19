import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/db/nifty100.db")

PARSED_FILE = Path("output/analysis_parsed.csv")

OUTPUT_FILE = Path("output/cagr_validation.csv")


# Mapping between NLP fields and Ratio Engine fields
METRIC_MAPPING = {
    "compounded_sales_growth": "revenue_cagr_5yr",
    "compounded_profit_growth": "pat_cagr_5yr",
}


def load_ratio_engine_data(db_path):
    """
    Load the latest available Ratio Engine values
    for each company.
    """

    con = sqlite3.connect(db_path)

    query = """
        SELECT
            company_id,
            year,
            revenue_cagr_5yr,
            pat_cagr_5yr
        FROM financial_ratios
        WHERE revenue_cagr_5yr IS NOT NULL
           OR pat_cagr_5yr IS NOT NULL
    """

    df = pd.read_sql_query(query, con)

    con.close()

    if df.empty:
        raise ValueError("No CAGR data found in financial_ratios.")

    return df


def select_latest_ratio_values(df):
    """
    Select the latest available financial-ratio record
    for each company.

    The 'year' column contains values such as:
        Mar 2016
        Mar 2024
        Dec 2024
    """

    df = df.copy()

    # Extract year from strings such as 'Mar 2024'
    df["year_num"] = df["year"].astype(str).str.extract(r"(\d{4})")[0]

    df["year_num"] = pd.to_numeric(
        df["year_num"],
        errors="coerce",
    )

    df = df.sort_values(["company_id", "year_num"])

    latest = df.groupby("company_id", as_index=False).tail(1).copy()

    return latest


def calculate_divergence(parsed_value, computed_value):
    """
    Calculate percentage divergence.

    divergence =
        abs(parsed - computed) / abs(computed) * 100
    """

    if pd.isna(parsed_value) or pd.isna(computed_value):
        return None

    if computed_value == 0:
        return None

    return abs(parsed_value - computed_value) / abs(computed_value) * 100


def validate_cagr():
    "Validate cagr."

    print("=" * 60)
    print("DAY 29 - RATIO ENGINE CAGR CROSS-VALIDATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load NLP parsed data
    # ---------------------------------------------------------

    parsed = pd.read_csv(PARSED_FILE)

    # Only 5-year CAGR values can be compared directly
    # with the Ratio Engine's 5-year CAGR fields.
    parsed = parsed[parsed["period_years"] == 5].copy()

    parsed = parsed[parsed["metric_type"].isin(METRIC_MAPPING.keys())].copy()

    print(f"Parsed 5-year CAGR records: {len(parsed)}")

    # ---------------------------------------------------------
    # Load Ratio Engine data
    # ---------------------------------------------------------

    ratio_df = load_ratio_engine_data(DB_PATH)

    latest_ratio = select_latest_ratio_values(ratio_df)

    print(f"Ratio Engine companies: " f"{latest_ratio['company_id'].nunique()}")

    # ---------------------------------------------------------
    # Compare values
    # ---------------------------------------------------------

    results = []

    for _, row in parsed.iterrows():

        company_id = row["company_id"]

        metric_type = row["metric_type"]

        parsed_value = row["value_pct"]

        ratio_column = METRIC_MAPPING[metric_type]

        matches = latest_ratio[latest_ratio["company_id"] == company_id]

        if matches.empty:

            results.append(
                {
                    "company_id": company_id,
                    "metric_type": metric_type,
                    "period_years": row["period_years"],
                    "parsed_value_pct": parsed_value,
                    "computed_value_pct": None,
                    "divergence_pct": None,
                    "validation_status": "NO_RATIO_DATA",
                }
            )

            continue

        computed_value = matches.iloc[0][ratio_column]

        divergence = calculate_divergence(
            parsed_value,
            computed_value,
        )

        if divergence is None:

            status = "NO_COMPARISON"

        elif divergence > 5:

            status = "MANUAL_REVIEW"

        else:

            status = "PASS"

        results.append(
            {
                "company_id": company_id,
                "metric_type": metric_type,
                "period_years": row["period_years"],
                "parsed_value_pct": parsed_value,
                "computed_value_pct": computed_value,
                "divergence_pct": (
                    round(divergence, 2) if divergence is not None else None
                ),
                "validation_status": status,
            }
        )

    validation_df = pd.DataFrame(results)

    # ---------------------------------------------------------
    # Save results
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    validation_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print()
    print("VALIDATION SUMMARY")
    print("-" * 60)

    if not validation_df.empty:

        print(validation_df["validation_status"].value_counts().to_string())

        manual_reviews = validation_df[
            validation_df["validation_status"] == "MANUAL_REVIEW"
        ]

        print()
        print(f"Manual review cases: " f"{len(manual_reviews)}")

        if not manual_reviews.empty:

            print()
            print(manual_reviews.to_string(index=False))

    print()
    print(f"Validation output: " f"{OUTPUT_FILE}")

    return validation_df


if __name__ == "__main__":
    validate_cagr()
