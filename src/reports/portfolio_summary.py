"""
DAY 35 - PORTFOLIO SUMMARY PDF

Generates one-page summary for every company in alphabetical
order by ticker.

Each page contains:
- Company name
- Sector
- Top 6 KPIs
- Trend arrows comparing latest year with previous year

Arrow logic:
↑ = improved
↓ = declined
→ = flat within 2%

For D/E, a decrease is considered an improvement.
"""

import re
import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "data" / "db" / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "reports" / "portfolio"

OUTPUT_FILE = OUTPUT_DIR / "portfolio_summary.pdf"


# ============================================================
# KPI CONFIGURATION
# ============================================================

# Six KPIs required for the portfolio summary.
#
# higher_is_better:
# True  -> increase is improvement
# False -> decrease is improvement
#
KPI_CONFIG = [
    {
        "name": "ROE",
        "column": "return_on_equity_pct",
        "higher_is_better": True,
        "suffix": "%",
    },
    {
        "name": "ROCE",
        "column": "return_on_capital_employed_pct",
        "higher_is_better": True,
        "suffix": "%",
    },
    {
        "name": "OPM",
        "column": "operating_profit_margin_pct",
        "higher_is_better": True,
        "suffix": "%",
    },
    {
        "name": "Debt / Equity",
        "column": "debt_to_equity",
        "higher_is_better": False,
        "suffix": "x",
    },
    {
        "name": "Interest Coverage",
        "column": "interest_coverage",
        "higher_is_better": True,
        "suffix": "x",
    },
    {
        "name": "Free Cash Flow",
        "column": "free_cash_flow_cr",
        "higher_is_better": True,
        "suffix": " Cr",
    },
]


# ============================================================
# DATABASE
# ============================================================


def get_connection():
    "Get connection."
    return sqlite3.connect(DB_PATH)


def extract_year(value):
    """
    Extract a four-digit year from values such as:
    Mar 2024
    Dec 2019
    TTM
    """

    if pd.isna(value):
        return None

    match = re.search(
        r"(19|20)\d{2}",
        str(value),
    )

    if match:
        return int(match.group())

    return None


# ============================================================
# COMPANY LIST
# ============================================================


def load_companies():
    "Load companies."

    con = get_connection()

    companies = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        ORDER BY id
        """,
        con,
    )

    sectors = pd.read_sql_query(
        """
        SELECT
            company_id,
            broad_sector AS sector
        FROM sectors
        """,
        con,
    )

    con.close()

    df = companies.merge(
        sectors,
        on="company_id",
        how="left",
    )

    df["sector"] = df["sector"].fillna("Unknown")

    return df.sort_values("company_id").reset_index(drop=True)


# ============================================================
# LOAD RATIO HISTORY
# ============================================================


def load_ratio_history(company_id):
    "Load ratio history."

    con = get_connection()

    columns = [
        "year",
    ]

    columns.extend([config["column"] for config in KPI_CONFIG])

    query = f"""
        SELECT
            {", ".join(columns)}
        FROM financial_ratios
        WHERE company_id = ?
    """

    df = pd.read_sql_query(
        query,
        con,
        params=(company_id,),
    )

    con.close()

    if df.empty:
        return df

    df["parsed_year"] = df["year"].apply(extract_year)

    df = df[df["parsed_year"].notna()].copy()

    df["parsed_year"] = df["parsed_year"].astype(int)

    # One record per year.
    #
    # Your database contains some duplicate financial-ratio
    # rows, so keeping the last row prevents duplicate years
    # from affecting the trend calculation.
    df = df.sort_values(["parsed_year"]).drop_duplicates(
        subset=["parsed_year"],
        keep="last",
    )

    return df


# ============================================================
# FORMAT VALUE
# ============================================================


def format_value(value, suffix):
    "Format value."

    if value is None:
        return "N/A"

    try:

        if pd.isna(value):
            return "N/A"

        number = float(value)

        return f"{number:.2f}{suffix}"

    except (TypeError, ValueError):

        return "N/A"


# ============================================================
# TREND CALCULATION
# ============================================================


def trend_arrow(
    previous,
    latest,
    higher_is_better=True,
):
    """
    Determine trend.

    Flat:
        absolute percentage change <= 2%

    Improved:
        change direction is favorable

    Declined:
        change direction is unfavorable
    """

    if previous is None or latest is None:
        return "→"

    try:

        previous = float(previous)
        latest = float(latest)

    except (TypeError, ValueError):

        return "→"

    if pd.isna(previous) or pd.isna(latest):
        return "→"

    # Handle both zero.
    if previous == 0 and latest == 0:
        return "→"

    # If previous is zero, percentage change is undefined.
    if previous == 0:
        if latest == 0:
            return "→"

        if higher_is_better:
            return "↑"

        return "↓"

    relative_change = abs((latest - previous) / abs(previous)) * 100

    # Flat within 2%.
    if relative_change <= 2:
        return "→"

    increasing = latest > previous

    if higher_is_better:

        if increasing:
            return "↑"

        return "↓"

    else:

        # For D/E:
        # decreasing = improvement
        if increasing:
            return "↓"

        return "↑"


# ============================================================
# KPI TABLE
# ============================================================


def build_kpi_table(
    latest_row,
    previous_row,
):
    "Build kpi table."

    rows = [
        [
            Paragraph(
                "<b>KPI</b>",
                TABLE_STYLE,
            ),
            Paragraph(
                "<b>Latest</b>",
                TABLE_STYLE,
            ),
            Paragraph(
                "<b>Previous</b>",
                TABLE_STYLE,
            ),
            Paragraph(
                "<b>Trend</b>",
                TABLE_STYLE,
            ),
        ]
    ]

    for config in KPI_CONFIG:

        column = config["column"]

        latest = latest_row[column] if latest_row is not None else None

        previous = previous_row[column] if previous_row is not None else None

        arrow = trend_arrow(
            previous,
            latest,
            config["higher_is_better"],
        )

        rows.append(
            [
                Paragraph(
                    config["name"],
                    TABLE_STYLE,
                ),
                Paragraph(
                    format_value(
                        latest,
                        config["suffix"],
                    ),
                    TABLE_STYLE,
                ),
                Paragraph(
                    format_value(
                        previous,
                        config["suffix"],
                    ),
                    TABLE_STYLE,
                ),
                Paragraph(
                    arrow,
                    ARROW_STYLE,
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[
            55 * mm,
            45 * mm,
            45 * mm,
            25 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
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
                    colors.HexColor("#B7B7B7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    return table


# ============================================================
# PAGE HEADER
# ============================================================


def draw_header(
    canvas,
    doc,
):
    "Draw header."

    canvas.saveState()

    width, height = A4

    canvas.setFillColor(colors.HexColor("#17365D"))

    canvas.rect(
        0,
        height - 12 * mm,
        width,
        12 * mm,
        fill=1,
        stroke=0,
    )

    canvas.setFillColor(colors.HexColor("#666666"))

    canvas.setFont(
        "Helvetica",
        7,
    )

    canvas.drawRightString(
        width - 15 * mm,
        8 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


# ============================================================
# COMPANY PAGE
# ============================================================


def build_company_page(
    story,
    company,
):
    "Build company page."

    company_id = company["company_id"]

    company_name = company["company_name"]

    sector = company["sector"]

    history = load_ratio_history(company_id)

    # --------------------------------------------------------
    # Company title
    # --------------------------------------------------------

    story.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    story.append(
        Paragraph(
            f"<b>{company_name}</b>",
            COMPANY_TITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            f"Ticker: {company_id} &nbsp;&nbsp; " f"| &nbsp;&nbsp; Sector: {sector}",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            8 * mm,
        )
    )

    # --------------------------------------------------------
    # Latest / previous year
    # --------------------------------------------------------

    if history.empty:

        story.append(
            Paragraph(
                "No financial ratio data available.",
                BODY_STYLE,
            )
        )

        return

    history = history.sort_values("parsed_year")

    latest_row = history.iloc[-1]

    previous_row = history.iloc[-2] if len(history) >= 2 else None

    latest_year = latest_row["parsed_year"]

    previous_year = previous_row["parsed_year"] if previous_row is not None else "N/A"

    story.append(
        Paragraph(
            f"Latest financial year: "
            f"<b>{latest_year}</b> "
            f"&nbsp;&nbsp; "
            f"Previous: <b>{previous_year}</b>",
            YEAR_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    # --------------------------------------------------------
    # KPI table
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Top 6 KPIs",
            SECTION_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            2 * mm,
        )
    )

    story.append(
        build_kpi_table(
            latest_row,
            previous_row,
        )
    )

    story.append(
        Spacer(
            1,
            10 * mm,
        )
    )

    # --------------------------------------------------------
    # Trend legend
    # --------------------------------------------------------

    legend_data = [
        [
            Paragraph(
                "<b>Trend Legend</b>",
                TABLE_STYLE,
            ),
            Paragraph(
                "↑ Improved",
                TABLE_STYLE,
            ),
            Paragraph(
                "↓ Declined",
                TABLE_STYLE,
            ),
            Paragraph(
                "→ Flat (within 2%)",
                TABLE_STYLE,
            ),
        ]
    ]

    legend = Table(
        legend_data,
        colWidths=[
            50 * mm,
            40 * mm,
            40 * mm,
            55 * mm,
        ],
    )

    legend.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#F2F2F2"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#B7B7B7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
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
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(legend)

    story.append(
        Spacer(
            1,
            12 * mm,
        )
    )

    # --------------------------------------------------------
    # Data coverage
    # --------------------------------------------------------

    story.append(
        Paragraph(
            f"Financial history available: " f"<b>{len(history)} years</b>",
            BODY_STYLE,
        )
    )


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

COMPANY_TITLE_STYLE = ParagraphStyle(
    "CompanyTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#17365D"),
)

SUBTITLE_STYLE = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontSize=10,
    leading=13,
    textColor=colors.HexColor("#555555"),
)

YEAR_STYLE = ParagraphStyle(
    "Year",
    parent=styles["Normal"],
    fontSize=9,
    leading=12,
)

SECTION_STYLE = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontSize=13,
    leading=16,
    textColor=colors.HexColor("#17365D"),
)

BODY_STYLE = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=9,
    leading=12,
)

TABLE_STYLE = ParagraphStyle(
    "Table",
    parent=styles["BodyText"],
    fontSize=8,
    leading=10,
)

ARROW_STYLE = ParagraphStyle(
    "Arrow",
    parent=styles["BodyText"],
    fontSize=15,
    leading=16,
    alignment=TA_CENTER,
)


# ============================================================
# GENERATE PDF
# ============================================================


def generate_portfolio_summary():
    "Generate portfolio summary."

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    companies = load_companies()

    print("=" * 78)
    print("DAY 35 - PORTFOLIO SUMMARY PDF")
    print("=" * 78)

    print(
        "Companies:",
        len(companies),
    )

    print(
        "Output:",
        OUTPUT_FILE,
    )

    doc = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=15 * mm,
        title="Portfolio Summary",
        author="Nifty100 Analytics",
    )

    story = []

    for index, (_, company) in enumerate(companies.iterrows()):

        print(f"{index + 1:>3}/{len(companies)} " f"{company['company_id']}")

        build_company_page(
            story,
            company,
        )

        if index < len(companies) - 1:

            story.append(PageBreak())

    doc.build(
        story,
        onFirstPage=draw_header,
        onLaterPages=draw_header,
    )

    print()
    print("=" * 78)
    print("DAY 35 VERIFICATION")
    print("=" * 78)

    print(
        "Expected company pages:",
        len(companies),
    )

    print(
        "PDF:",
        OUTPUT_FILE,
    )

    print()
    print("STATUS: Portfolio summary generated.")

    return OUTPUT_FILE


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    generate_portfolio_summary()
