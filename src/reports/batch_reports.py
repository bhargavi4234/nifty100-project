"""
DAY 34 - BATCH REPORT GENERATION

1. Generate company tearsheets for all companies.
2. Skip companies with fewer than 3 years of usable data.
3. Generate 11 sector reports.
4. Generate skipped_tearsheets.csv.
5. Generate verification summaries.
"""

import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from tearsheet import generate_tearsheet

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "data" / "db" / "nifty100.db"

TEARSHEET_DIR = BASE_DIR / "reports" / "tearsheets"
SECTOR_DIR = BASE_DIR / "reports" / "sector"

OUTPUT_DIR = BASE_DIR / "output"

SKIPPED_FILE = OUTPUT_DIR / "skipped_tearsheets.csv"
SECTOR_SUMMARY_FILE = OUTPUT_DIR / "sector_report_summary.csv"


# ============================================================
# DATABASE
# ============================================================


def get_connection():
    "Get connection."
    return sqlite3.connect(DB_PATH)


# ============================================================
# COMPANY LIST
# ============================================================


def get_companies():
    "Get companies."

    con = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        ORDER BY id
        """,
        con,
    )

    con.close()

    return df


# ============================================================
# YEAR EXTRACTION
# ============================================================


def extract_year(value):
    "Extract year."

    if pd.isna(value):
        return None

    text = str(value)

    import re

    match = re.search(r"(19|20)\d{2}", text)

    if match:
        return int(match.group(0))

    return None


# ============================================================
# DATA YEARS
# ============================================================


def get_company_year_count(company_id):
    "Get company year count."

    con = get_connection()

    counts = []

    tables = [
        "profitandloss",
        "balancesheet",
        "cashflow",
        "financial_ratios",
    ]

    for table in tables:

        try:

            df = pd.read_sql_query(
                f"""
                SELECT DISTINCT year
                FROM {table}
                WHERE company_id = ?
                """,
                con,
                params=(company_id,),
            )

            for year in df["year"]:
                parsed = extract_year(year)

                if parsed is not None:
                    counts.append(parsed)

        except (TypeError, ValueError):
            pass

    con.close()

    return len(set(counts))


# ============================================================
# BATCH TEARSHEETS
# ============================================================


def generate_company_tearsheets():
    "Generate company tearsheets."

    print("=" * 78)
    print("DAY 34 - BATCH TEARSHEET GENERATION")
    print("=" * 78)

    TEARSHEET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    companies = get_companies()

    print()
    print("Companies in database:", len(companies))

    generated = []
    skipped = []
    failed = []

    for _, row in companies.iterrows():

        ticker = row["company_id"]

        year_count = get_company_year_count(ticker)

        if year_count < 3:

            skipped.append(
                {
                    "company_id": ticker,
                    "reason": "Fewer than 3 years of data",
                    "year_count": year_count,
                }
            )

            print(f"SKIP  {ticker:<12} " f"{year_count} years")

            continue

        output_path = TEARSHEET_DIR / f"{ticker}_tearsheet.pdf"

        try:

            generate_tearsheet(
                ticker,
                output_path,
            )

            generated.append(
                {
                    "company_id": ticker,
                    "file": str(output_path),
                    "year_count": year_count,
                }
            )

            print(f"PASS  {ticker:<12} " f"{year_count} years")

        except (KeyError, TypeError, ValueError, OSError) as exc:

            failed.append(
                {
                    "company_id": ticker,
                    "error": str(exc),
                }
            )

            print(f"FAIL  {ticker:<12} " f"{exc}")

    skipped_df = pd.DataFrame(
        skipped,
        columns=[
            "company_id",
            "reason",
            "year_count",
        ],
    )

    skipped_df.to_csv(
        SKIPPED_FILE,
        index=False,
    )

    print()
    print("=" * 78)
    print("BATCH TEARSHEET SUMMARY")
    print("=" * 78)

    print(
        "Expected companies:",
        len(companies),
    )

    print(
        "Generated:",
        len(generated),
    )

    print(
        "Skipped:",
        len(skipped),
    )

    print(
        "Failed:",
        len(failed),
    )

    print(
        "Output directory:",
        TEARSHEET_DIR,
    )

    print(
        "Skipped file:",
        SKIPPED_FILE,
    )

    if failed:

        print()
        print("FAILED COMPANIES:")

        for item in failed:
            print(f" - {item['company_id']}: " f"{item['error']}")

    return companies, generated, skipped, failed


# ============================================================
# SECTOR DATA
# ============================================================


def get_sector_data():
    "Get sector data."

    con = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector AS sector
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        ORDER BY s.broad_sector, c.id
        """,
        con,
    )

    con.close()

    return df


# ============================================================
# LATEST FINANCIAL DATA
# ============================================================


def get_latest_metrics(company_id):
    "Get latest metrics."

    con = get_connection()

    ratio = pd.read_sql_query(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY
            CASE
                WHEN year LIKE '%TTM%' THEN 9999
                ELSE CAST(
                    substr(year, -4)
                    AS INTEGER
                )
            END DESC
        LIMIT 1
        """,
        con,
        params=(company_id,),
    )

    con.close()

    if ratio.empty:
        return {
            "ROE": None,
            "ROCE": None,
            "OPM": None,
            "D/E": None,
            "ICR": None,
            "FCF": None,
            "Revenue CAGR": None,
            "PAT CAGR": None,
        }

    row = ratio.iloc[0]

    return {
        "ROE": row.get("return_on_equity_pct"),
        "ROCE": row.get("return_on_capital_employed_pct"),
        "OPM": row.get("operating_profit_margin_pct"),
        "D/E": row.get("debt_to_equity"),
        "ICR": row.get("interest_coverage"),
        "FCF": row.get("free_cash_flow_cr"),
        "Revenue CAGR": row.get("revenue_cagr_5yr"),
        "PAT CAGR": row.get("pat_cagr_5yr"),
    }


# ============================================================
# FORMAT METRIC
# ============================================================


def format_metric(value):
    "Format metric."

    if value is None:
        return "N/A"

    try:

        if pd.isna(value):
            return "N/A"

        return f"{float(value):.2f}"

    except (TypeError, ValueError):

        return "N/A"


# ============================================================
# SECTOR REPORT
# ============================================================


def generate_sector_report(
    sector,
    sector_df,
):
    "Generate sector report."

    SECTOR_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_sector = str(sector).replace("/", "_").replace("\\", "_").replace(" ", "_")

    output_path = SECTOR_DIR / f"{safe_sector}_report.pdf"

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "SectorTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "SectorHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
    )

    body_style = ParagraphStyle(
        "SectorBody",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
    )

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    story = []

    # --------------------------------------------------------
    # SECTOR SUMMARY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            f"{sector} Sector Report",
            title_style,
        )
    )

    story.append(Spacer(1, 12))

    all_metrics = []

    for _, company in sector_df.iterrows():

        metrics = get_latest_metrics(company["company_id"])

        all_metrics.append(metrics)

    metric_names = [
        "ROE",
        "ROCE",
        "OPM",
        "D/E",
        "ICR",
        "FCF",
        "Revenue CAGR",
        "PAT CAGR",
    ]

    summary_rows = [
        [
            Paragraph(
                "<b>Metric</b>",
                body_style,
            ),
            Paragraph(
                "<b>Sector Median</b>",
                body_style,
            ),
        ]
    ]

    for metric in metric_names:

        values = []

        for metrics in all_metrics:

            value = metrics.get(metric)

            if value is not None:

                try:

                    if not pd.isna(value):
                        values.append(float(value))
                except (TypeError, ValueError):
                    pass

        median = pd.Series(values).median() if values else None

        summary_rows.append(
            [
                Paragraph(
                    metric,
                    body_style,
                ),
                Paragraph(
                    format_metric(median),
                    body_style,
                ),
            ]
        )

    summary_table = Table(
        summary_rows,
        colWidths=[
            220,
            250,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#17365D"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(
        Paragraph(
            "Sector Median KPIs",
            heading_style,
        )
    )

    story.append(summary_table)

    story.append(Spacer(1, 15))

    # --------------------------------------------------------
    # COMPANY LIST
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Companies and Latest KPIs",
            heading_style,
        )
    )

    company_rows = [
        [
            Paragraph("<b>Company</b>", body_style),
            Paragraph("<b>ROE</b>", body_style),
            Paragraph("<b>ROCE</b>", body_style),
            Paragraph("<b>OPM</b>", body_style),
            Paragraph("<b>D/E</b>", body_style),
            Paragraph("<b>ICR</b>", body_style),
            Paragraph("<b>FCF</b>", body_style),
            Paragraph("<b>Rev CAGR</b>", body_style),
            Paragraph("<b>PAT CAGR</b>", body_style),
        ]
    ]

    for _, company in sector_df.iterrows():

        metrics = get_latest_metrics(company["company_id"])

        company_rows.append(
            [
                Paragraph(
                    str(company["company_id"]),
                    body_style,
                ),
                Paragraph(
                    format_metric(metrics["ROE"]),
                    body_style,
                ),
                Paragraph(
                    format_metric(metrics["ROCE"]),
                    body_style,
                ),
                Paragraph(
                    format_metric(metrics["OPM"]),
                    body_style,
                ),
                Paragraph(
                    format_metric(metrics["D/E"]),
                    body_style,
                ),
                Paragraph(
                    format_metric(metrics["ICR"]),
                    body_style,
                ),
                Paragraph(
                    format_metric(metrics["FCF"]),
                    body_style,
                ),
                Paragraph(
                    format_metric(metrics["Revenue CAGR"]),
                    body_style,
                ),
                Paragraph(
                    format_metric(metrics["PAT CAGR"]),
                    body_style,
                ),
            ]
        )

    company_table = Table(
        company_rows,
        colWidths=[
            65,
            50,
            50,
            50,
            45,
            45,
            55,
            60,
            60,
        ],
        repeatRows=1,
    )

    company_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#17365D"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    story.append(company_table)

    doc.build(story)

    return output_path


# ============================================================
# GENERATE ALL SECTOR REPORTS
# ============================================================


def generate_sector_reports():
    "Generate sector reports."

    print()
    print("=" * 78)
    print("DAY 34 - SECTOR REPORT GENERATION")
    print("=" * 78)

    sectors = get_sector_data()

    sectors["sector"] = sectors["sector"].fillna("Unknown")

    results = []

    for sector, sector_df in sectors.groupby("sector"):

        try:

            output = generate_sector_report(
                sector,
                sector_df,
            )

            results.append(
                {
                    "sector": sector,
                    "company_count": len(sector_df),
                    "status": "PASS",
                    "file": str(output),
                }
            )

            print(f"PASS  {sector:<20} " f"{len(sector_df)} companies")

        except (KeyError, TypeError, ValueError, OSError) as exc:

            results.append(
                {
                    "sector": sector,
                    "company_count": len(sector_df),
                    "status": "FAIL",
                    "file": "",
                    "error": str(exc),
                }
            )

            print(f"FAIL  {sector:<20} " f"{exc}")

    result_df = pd.DataFrame(results)

    result_df.to_csv(
        SECTOR_SUMMARY_FILE,
        index=False,
    )

    print()
    print(
        "Sector PDFs generated:",
        int((result_df["status"] == "PASS").sum()),
    )

    print(
        "Expected sectors:",
        sectors["sector"].nunique(),
    )

    print(
        "Summary:",
        SECTOR_SUMMARY_FILE,
    )

    return result_df


# ============================================================
# FINAL VERIFICATION
# ============================================================


def verify_day_34(
    companies,
    generated,
    skipped,
    failed,
    sector_results,
):
    "Verify day 34."

    print()
    print("=" * 78)
    print("DAY 34 VERIFICATION")
    print("=" * 78)

    actual_tearsheets = list(TEARSHEET_DIR.glob("*_tearsheet.pdf"))

    actual_sector_reports = list(SECTOR_DIR.glob("*_report.pdf"))

    print(
        "Database companies:",
        len(companies),
    )

    print(
        "Generated tearsheets:",
        len(actual_tearsheets),
    )

    print(
        "Skipped tearsheets:",
        len(skipped),
    )

    print(
        "Failed tearsheets:",
        len(failed),
    )

    print(
        "Sector reports:",
        len(actual_sector_reports),
    )

    expected_tearsheets = len(companies) - len(skipped)

    print(
        "Expected tearsheets:",
        expected_tearsheets,
    )

    if len(actual_tearsheets) == expected_tearsheets and len(failed) == 0:
        print("TEARSHEET COUNT: PASS")
    else:
        print("TEARSHEET COUNT: REVIEW")

    if len(actual_sector_reports) == 11:
        print("SECTOR REPORT COUNT: PASS")
    else:
        print("SECTOR REPORT COUNT: REVIEW")

    if len(failed) == 0:
        print("BATCH GENERATION: PASS")
    else:
        print("BATCH GENERATION: REVIEW")


# ============================================================
# MAIN
# ============================================================


def main():
    "Main."

    (
        companies,
        generated,
        skipped,
        failed,
    ) = generate_company_tearsheets()

    sector_results = generate_sector_reports()

    verify_day_34(
        companies,
        generated,
        skipped,
        failed,
        sector_results,
    )


if __name__ == "__main__":
    main()
