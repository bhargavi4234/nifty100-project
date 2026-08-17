import re
from pathlib import Path

import pandas as pd


# Required regex from the Sprint 5 specification
PATTERN = re.compile(
    r"(\d+)\s*Years?:?\s*([\d.]+)%"
)


TARGET_FIELDS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]


def parse_metric_text(text):
    """Parse period and percentage value from text."""

    if pd.isna(text):
        return []

    text = str(text).strip()

    matches = PATTERN.findall(text)

    results = []

    for period, value in matches:
        results.append(
            {
                "period_years": int(period),
                "value_pct": float(value),
            }
        )

    return results


def parse_analysis(input_file, output_file, failure_file):
    """Parse analysis.xlsx and create parsed/failure CSV files."""

    # The actual column header is on Excel row 2.
    df = pd.read_excel(
        input_file,
        header=1,
    )

    # Remove completely empty rows
    df = df.dropna(how="all")

    required_columns = [
        "company_id",
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    parsed_rows = []
    failures = []

    for _, row in df.iterrows():

        company_id = str(row["company_id"]).strip()

        for metric_type in TARGET_FIELDS:

            raw_text = row[metric_type]

            # Empty or missing value
            if pd.isna(raw_text) or str(raw_text).strip() == "":
                failures.append(
                    {
                        "company_id": company_id,
                        "metric_type": metric_type,
                        "raw_text": raw_text,
                        "reason": "Empty or missing value",
                    }
                )
                continue

            raw_text = str(raw_text).strip()

            matches = parse_metric_text(raw_text)

            # Regex did not find a match
            if not matches:
                failures.append(
                    {
                        "company_id": company_id,
                        "metric_type": metric_type,
                        "raw_text": raw_text,
                        "reason": "Regex pattern did not match",
                    }
                )
                continue

            # Store every match
            for match in matches:

                parsed_rows.append(
                    {
                        "company_id": company_id,
                        "metric_type": metric_type,
                        "period_years": match["period_years"],
                        "value_pct": match["value_pct"],
                    }
                )

    parsed_df = pd.DataFrame(
        parsed_rows,
        columns=[
            "company_id",
            "metric_type",
            "period_years",
            "value_pct",
        ],
    )

    failures_df = pd.DataFrame(
        failures,
        columns=[
            "company_id",
            "metric_type",
            "raw_text",
            "reason",
        ],
    )

    # Make sure output directory exists
    Path(output_file).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save parsed results
    parsed_df.to_csv(
        output_file,
        index=False,
    )

    # Save failures
    failures_df.to_csv(
        failure_file,
        index=False,
    )

    print("=" * 60)
    print("DAY 29 - NLP ANALYSIS TEXT PARSER")
    print("=" * 60)

    print(f"Input records   : {len(df)}")
    print(f"Parsed records  : {len(parsed_df)}")
    print(f"Parse failures  : {len(failures_df)}")

    print("\nMetric breakdown:")

    if not parsed_df.empty:
        print(
            parsed_df["metric_type"]
            .value_counts()
            .to_string()
        )

    print("\nOutput files:")
    print(f"Parsed   : {output_file}")
    print(f"Failures : {failure_file}")


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[2]

    input_file = (
        project_root
        / "data"
        / "raw"
        / "analysis.xlsx"
    )

    output_file = (
        project_root
        / "output"
        / "analysis_parsed.csv"
    )

    failure_file = (
        project_root
        / "output"
        / "parse_failures.csv"
    )

    parse_analysis(
        input_file=input_file,
        output_file=output_file,
        failure_file=failure_file,
    )