import os
import pandas as pd

from src.analytics.cashflow import capital_allocation_pattern


def main():

    df = pd.read_excel(
        "data/raw/cashflow.xlsx",
        header=1
    )

    records = []

    for _, row in df.iterrows():

        cfo_sign, cfi_sign, cff_sign, label = capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"]
        )

        records.append(
            {
                "company_id": row["company_id"],
                "year": row["year"],
                "cfo_sign": cfo_sign,
                "cfi_sign": cfi_sign,
                "cff_sign": cff_sign,
                "pattern_label": label,
            }
        )

    output = pd.DataFrame(records)

    os.makedirs("output", exist_ok=True)

    output.to_csv(
        "output/capital_allocation.csv",
        index=False
    )

    print(
        "capital_allocation.csv generated successfully."
    )


if __name__ == "__main__":
    main()