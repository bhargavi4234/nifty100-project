import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

DB_PATH = Path("data/db/nifty100.db")

CAPITAL_ALLOCATION_FILE = Path(
    "output/capital_allocation.csv"
)

CASHFLOW_INTELLIGENCE_FILE = Path(
    "output/cashflow_intelligence.xlsx"
)

DISTRIBUTION_FILE = Path(
    "output/capital_allocation_distribution.csv"
)

PATTERN_CHANGES_FILE = Path(
    "output/pattern_changes.csv"
)

VERIFICATION_FILE = Path(
    "output/capital_allocation_verification.csv"
)


# ============================================================
# EXPECTED 8 PATTERNS
# ============================================================

EXPECTED_PATTERNS = [
    "Reinvestor",
    "Shareholder Returns",
    "Liquidating Assets",
    "Distress Signal",
    "Growth Funded by Debt",
    "Cash Accumulator",
    "Pre-Revenue",
    "Mixed",
]


# ============================================================
# LOAD CURRENT COMPANY UNIVERSE
# ============================================================

def load_company_universe():

    con = sqlite3.connect(DB_PATH)

    companies = pd.read_sql_query(
        """
        SELECT id AS company_id
        FROM companies
        ORDER BY id
        """,
        con,
    )

    con.close()

    return companies


# ============================================================
# LOAD CAPITAL ALLOCATION
# ============================================================

def load_capital_allocation():

    df = pd.read_csv(
        CAPITAL_ALLOCATION_FILE
    )

    required_columns = [
        "company_id",
        "year",
        "cfo_sign",
        "cfi_sign",
        "cff_sign",
        "pattern_label",
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "capital_allocation.csv is missing columns: "
            + ", ".join(missing)
        )

    return df


# ============================================================
# NORMALIZE YEAR
# ============================================================

def extract_year(value):

    if pd.isna(value):
        return np.nan

    text = str(value)

    import re

    match = re.search(
        r"\b(19|20)\d{2}\b",
        text,
    )

    if match:
        return int(match.group(0))

    return np.nan


# ============================================================
# VERIFY CAPITAL ALLOCATION COVERAGE
# ============================================================

def verify_coverage(
    companies,
    capital_allocation,
):

    db_companies = set(
        companies["company_id"]
    )

    csv_companies = set(
        capital_allocation["company_id"]
    )

    missing_companies = sorted(
        db_companies - csv_companies
    )

    extra_companies = sorted(
        csv_companies - db_companies
    )

    verification_rows = []

    for company_id in sorted(
        db_companies
    ):

        company_rows = capital_allocation[
            capital_allocation["company_id"]
            == company_id
        ]

        if company_rows.empty:

            verification_rows.append(
                {
                    "company_id": company_id,
                    "status": "MISSING",
                    "row_count": 0,
                    "year_count": 0,
                }
            )

        else:

            verification_rows.append(
                {
                    "company_id": company_id,
                    "status": "PRESENT",
                    "row_count": len(
                        company_rows
                    ),
                    "year_count": company_rows[
                        "year"
                    ].nunique(),
                }
            )

    verification = pd.DataFrame(
        verification_rows
    )

    return (
        verification,
        missing_companies,
        extra_companies,
    )


# ============================================================
# CLEAN CURRENT-UNIVERSE CAPITAL ALLOCATION
# ============================================================

def prepare_current_universe(
    capital_allocation,
    companies,
):

    current_ids = set(
        companies["company_id"]
    )

    df = capital_allocation[
        capital_allocation["company_id"].isin(
            current_ids
        )
    ].copy()

    df["year_num"] = df["year"].apply(
        extract_year
    )

    # Remove rows where year cannot be interpreted.
    df = df[
        df["year_num"].notna()
    ].copy()

    df["year_num"] = df[
        "year_num"
    ].astype(int)

    # Remove duplicate company/year records.
    #
    # Your original file contains duplicated historical
    # records for some companies.
    df = (
        df.sort_values(
            [
                "company_id",
                "year_num",
            ]
        )
        .drop_duplicates(
            subset=[
                "company_id",
                "year_num",
            ],
            keep="last",
        )
    )

    return df


# ============================================================
# LATEST-YEAR DISTRIBUTION
# ============================================================

def generate_latest_distribution(
    current_df,
    companies,
):

    rows = []

    for company_id in companies[
        "company_id"
    ]:

        company_data = current_df[
            current_df["company_id"]
            == company_id
        ]

        if company_data.empty:

            pattern = "Insufficient Data"
            latest_year = np.nan

        else:

            latest = company_data.sort_values(
                "year_num"
            ).iloc[-1]

            pattern = latest[
                "pattern_label"
            ]

            latest_year = latest[
                "year_num"
            ]

        rows.append(
            {
                "company_id": company_id,
                "latest_year": latest_year,
                "latest_pattern": pattern,
            }
        )

    latest_df = pd.DataFrame(
        rows
    )

    distribution = (
        latest_df[
            "latest_pattern"
        ]
        .value_counts()
        .rename_axis(
            "pattern_label"
        )
        .reset_index(
            name="company_count"
        )
    )

    # Ensure all eight expected patterns
    # appear even if count is zero.
    expected_df = pd.DataFrame(
        {
            "pattern_label":
                EXPECTED_PATTERNS
        }
    )

    distribution = expected_df.merge(
        distribution,
        on="pattern_label",
        how="left",
    )

    distribution[
        "company_count"
    ] = distribution[
        "company_count"
    ].fillna(0).astype(int)

    # Add insufficient-data count separately.
    insufficient_count = int(
        (
            latest_df[
                "latest_pattern"
            ]
            == "Insufficient Data"
        ).sum()
    )

    distribution = pd.concat(
        [
            distribution,
            pd.DataFrame(
                [
                    {
                        "pattern_label":
                            "Insufficient Data",
                        "company_count":
                            insufficient_count,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    return (
        latest_df,
        distribution,
    )


# ============================================================
# ADD CAPITAL ALLOCATION TO CASHFLOW INTELLIGENCE
# ============================================================

def update_cashflow_intelligence(
    latest_df,
):

    if not CASHFLOW_INTELLIGENCE_FILE.exists():

        raise FileNotFoundError(
            "cashflow_intelligence.xlsx not found."
        )

    intelligence = pd.read_excel(
        CASHFLOW_INTELLIGENCE_FILE
    )

    if "company_id" not in intelligence.columns:

        raise ValueError(
            "cashflow_intelligence.xlsx does not "
            "contain company_id."
        )

    # Remove old column if this script is run again.
    if (
        "capital_allocation_label"
        in intelligence.columns
    ):

        intelligence = intelligence.drop(
            columns=[
                "capital_allocation_label"
            ]
        )

    allocation_map = latest_df.set_index(
        "company_id"
    )[
        "latest_pattern"
    ].to_dict()

    intelligence[
        "capital_allocation_label"
    ] = intelligence[
        "company_id"
    ].map(
        allocation_map
    )

    intelligence[
        "capital_allocation_label"
    ] = intelligence[
        "capital_allocation_label"
    ].fillna(
        "Insufficient Data"
    )

    # Rewrite workbook.
    intelligence.to_excel(
        CASHFLOW_INTELLIGENCE_FILE,
        index=False,
    )

    return intelligence


# ============================================================
# PATTERN CHANGES YEAR-OVER-YEAR
# ============================================================

def generate_pattern_changes(
    current_df,
):

    changes = []

    for company_id, group in current_df.groupby(
        "company_id"
    ):

        group = group.sort_values(
            "year_num"
        ).copy()

        group = group[
            [
                "year_num",
                "pattern_label",
            ]
        ].dropna()

        if len(group) < 2:
            continue

        previous_row = None

        for _, row in group.iterrows():

            if previous_row is not None:

                old_pattern = previous_row[
                    "pattern_label"
                ]

                new_pattern = row[
                    "pattern_label"
                ]

                if old_pattern != new_pattern:

                    changes.append(
                        {
                            "company_id":
                                company_id,
                            "from_year":
                                int(
                                    previous_row[
                                        "year_num"
                                    ]
                                ),
                            "to_year":
                                int(
                                    row[
                                        "year_num"
                                    ]
                                ),
                            "previous_pattern":
                                old_pattern,
                            "new_pattern":
                                new_pattern,
                            "change":
                                (
                                    f"{old_pattern} "
                                    f"-> "
                                    f"{new_pattern}"
                                ),
                        }
                    )

            previous_row = row

    changes_df = pd.DataFrame(
        changes,
        columns=[
            "company_id",
            "from_year",
            "to_year",
            "previous_pattern",
            "new_pattern",
            "change",
        ],
    )

    return changes_df


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 78)
    print("DAY 32 - CAPITAL ALLOCATION REPORT")
    print("=" * 78)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    companies = load_company_universe()

    capital_allocation = (
        load_capital_allocation()
    )

    print()
    print(
        "Current database companies :",
        len(companies),
    )

    print(
        "Capital allocation CSV rows :",
        len(capital_allocation),
    )

    print(
        "CSV unique companies        :",
        capital_allocation[
            "company_id"
        ].nunique(),
    )

    # --------------------------------------------------------
    # Verify coverage
    # --------------------------------------------------------

    (
        verification,
        missing_companies,
        extra_companies,
    ) = verify_coverage(
        companies,
        capital_allocation,
    )

    verification.to_csv(
        VERIFICATION_FILE,
        index=False,
    )

    print()
    print("=" * 78)
    print("COVERAGE VERIFICATION")
    print("=" * 78)

    print(
        "Expected companies :",
        len(companies),
    )

    print(
        "CSV companies      :",
        capital_allocation[
            "company_id"
        ].nunique(),
    )

    print(
        "Missing companies  :",
        len(missing_companies),
    )

    print(
        "Extra companies    :",
        len(extra_companies),
    )

    if missing_companies:

        print()
        print("Missing:")
        for company in missing_companies:
            print(" -", company)

    if extra_companies:

        print()
        print("Extra / obsolete:")
        for company in extra_companies:
            print(" -", company)

    # --------------------------------------------------------
    # Prepare current universe
    # --------------------------------------------------------

    current_df = prepare_current_universe(
        capital_allocation,
        companies,
    )

    print()
    print(
        "Current-universe rows:",
        len(current_df),
    )

    print(
        "Current-universe companies:",
        current_df[
            "company_id"
        ].nunique(),
    )

    # --------------------------------------------------------
    # Latest distribution
    # --------------------------------------------------------

    (
        latest_df,
        distribution,
    ) = generate_latest_distribution(
        current_df,
        companies,
    )

    distribution.to_csv(
        DISTRIBUTION_FILE,
        index=False,
    )

    print()
    print("=" * 78)
    print("LATEST-YEAR PATTERN DISTRIBUTION")
    print("=" * 78)

    print(
        distribution.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Update Day 31 Excel
    # --------------------------------------------------------

    intelligence = (
        update_cashflow_intelligence(
            latest_df
        )
    )

    print()
    print("=" * 78)
    print("CASHFLOW INTELLIGENCE UPDATE")
    print("=" * 78)

    print(
        "Rows in Excel:",
        len(intelligence),
    )

    print(
        "Capital allocation column added:",
        "capital_allocation_label"
        in intelligence.columns,
    )

    # --------------------------------------------------------
    # Pattern changes
    # --------------------------------------------------------

    changes = (
        generate_pattern_changes(
            current_df
        )
    )

    changes.to_csv(
        PATTERN_CHANGES_FILE,
        index=False,
    )

    print()
    print("=" * 78)
    print("YEAR-OVER-YEAR PATTERN CHANGES")
    print("=" * 78)

    print(
        "Pattern changes:",
        len(changes),
    )

    if not changes.empty:

        print()
        print(
            changes.head(20).to_string(
                index=False
            )
        )

    else:

        print(
            "No year-over-year pattern changes found."
        )

    # --------------------------------------------------------
    # Final verification
    # --------------------------------------------------------

    print()
    print("=" * 78)
    print("DAY 32 VERIFICATION")
    print("=" * 78)

    print(
        "Companies in database :",
        len(companies),
    )

    print(
        "Companies represented  :",
        current_df[
            "company_id"
        ].nunique(),
    )

    print(
        "Missing current companies:",
        len(missing_companies),
    )

    print(
        "Extra CSV companies:",
        len(extra_companies),
    )

    print(
        "Latest distribution saved:",
        DISTRIBUTION_FILE,
    )

    print(
        "Pattern changes saved:",
        PATTERN_CHANGES_FILE,
    )

    print(
        "Verification saved:",
        VERIFICATION_FILE,
    )

    print(
        "Cash-flow workbook updated:",
        CASHFLOW_INTELLIGENCE_FILE,
    )

    print()
    print(
        "NOTE: ATGL has no CFO/CFI/CFF data in the current database."
    )

    if missing_companies:

        print(
            "ATGL/current-universe coverage limitation is documented."
        )

    print()
    print(
        "STATUS: Day 32 report generated."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()