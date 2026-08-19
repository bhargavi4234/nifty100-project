import io
import sqlite3
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

matplotlib.use("Agg")

import matplotlib.pyplot as plt

# ============================================================
# PATHS
# ============================================================

DB_PATH = Path("data/db/nifty100.db")

PROS_CONS_FILE = Path("output/pros_cons_generated.csv")

CASHFLOW_INTELLIGENCE_FILE = Path("output/cashflow_intelligence.xlsx")

OUTPUT_DIR = Path("output/tearsheets")


# ============================================================
# PAGE / COLORS
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

NAVY = colors.HexColor("#14213D")
LIGHT_BLUE = colors.HexColor("#EAF0F7")
GREEN = colors.HexColor("#2E7D32")
LIGHT_GREEN = colors.HexColor("#E8F5E9")
RED = colors.HexColor("#C62828")
LIGHT_RED = colors.HexColor("#FFEBEE")
GREY = colors.HexColor("#666666")
LIGHT_GREY = colors.HexColor("#F2F2F2")
WHITE = colors.white
BLACK = colors.black


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "TearsheetTitle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=17,
    leading=20,
    textColor=WHITE,
    alignment=TA_LEFT,
)

SUBTITLE_STYLE = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    textColor=WHITE,
)

SECTION_STYLE = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=13,
    textColor=NAVY,
    spaceBefore=3,
    spaceAfter=5,
)

BODY_STYLE = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=9.5,
    textColor=BLACK,
)

SMALL_STYLE = ParagraphStyle(
    "Small",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=6.5,
    leading=8,
    textColor=GREY,
)

KPI_LABEL_STYLE = ParagraphStyle(
    "KpiLabel",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=6.5,
    leading=8,
    textColor=GREY,
    alignment=TA_CENTER,
)

KPI_VALUE_STYLE = ParagraphStyle(
    "KpiValue",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=14,
    textColor=NAVY,
    alignment=TA_CENTER,
)

BULLET_STYLE = ParagraphStyle(
    "Bullet",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=7,
    leading=9,
    leftIndent=9,
    firstLineIndent=-6,
    spaceAfter=2,
)

BADGE_STYLE = ParagraphStyle(
    "Badge",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=10,
    textColor=WHITE,
    alignment=TA_CENTER,
)


# ============================================================
# DATABASE
# ============================================================


def load_company_data(company_id):
    "Load company data."

    con = sqlite3.connect(DB_PATH)

    company = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            company_name,
            about_company,
            website,
            face_value,
            book_value,
            roce_percentage,
            roe_percentage
        FROM companies
        WHERE id = ?
        """,
        con,
        params=(company_id,),
    )

    sectors = pd.read_sql_query(
        """
        SELECT
            company_id,
            broad_sector,
            sub_sector
        FROM sectors
        WHERE company_id = ?
        """,
        con,
        params=(company_id,),
    )

    ratios = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            net_profit_margin_pct,
            operating_profit_margin_pct,
            return_on_equity_pct,
            debt_to_equity,
            interest_coverage,
            free_cash_flow_cr,
            capex_cr,
            earnings_per_share,
            dividend_payout_ratio_pct,
            total_debt_cr,
            cash_from_operations_cr,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            eps_cagr_5yr
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """,
        con,
        params=(company_id,),
    )

    pnl = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            sales,
            net_profit,
            eps
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year
        """,
        con,
        params=(company_id,),
    )

    balance = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            equity_capital,
            reserves,
            borrowings,
            other_liabilities,
            total_assets
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year
        """,
        con,
        params=(company_id,),
    )

    cashflow = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity,
            net_cash_flow
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year
        """,
        con,
        params=(company_id,),
    )

    con.close()

    return (
        company,
        sectors,
        ratios,
        pnl,
        balance,
        cashflow,
    )


# ============================================================
# HELPERS
# ============================================================


def extract_year(value):
    "Extract year."

    if pd.isna(value):
        return None

    import re

    match = re.search(
        r"\b(19|20)\d{2}\b",
        str(value),
    )

    if match:
        return int(match.group(0))

    return None


def prepare_year_data(df):
    "Prepare year data."

    df = df.copy()

    if df.empty:
        return df

    df["year_num"] = df["year"].apply(extract_year)

    df = df[df["year_num"].notna()].copy()

    df["year_num"] = df["year_num"].astype(int)

    # Remove duplicate company/year rows.
    if "company_id" in df.columns:
        df = df.sort_values("year_num").drop_duplicates(
            subset=[
                "company_id",
                "year_num",
            ],
            keep="last",
        )
    else:
        df = df.sort_values("year_num").drop_duplicates(
            subset=["year_num"],
            keep="last",
        )

    return df


def fmt_number(value, decimals=1):
    "Fmt number."

    if pd.isna(value):
        return "N/A"

    return f"{float(value):,.{decimals}f}"


def fmt_pct(value, decimals=1):
    "Fmt pct."

    if pd.isna(value):
        return "N/A"

    return f"{float(value):.{decimals}f}%"


def paragraph(text, style=BODY_STYLE):
    "Paragraph."

    if text is None:
        text = ""

    return Paragraph(
        str(text),
        style,
    )


# ============================================================
# PAGE HEADER
# ============================================================


def draw_page_header(
    canvas,
    doc,
    company_name,
    ticker,
):
    "Draw page header."

    canvas.saveState()

    # Header bar
    canvas.setFillColor(NAVY)

    canvas.rect(
        0,
        PAGE_HEIGHT - 25 * mm,
        PAGE_WIDTH,
        25 * mm,
        fill=1,
        stroke=0,
    )

    canvas.setFont(
        "Helvetica-Bold",
        16,
    )

    canvas.setFillColor(WHITE)

    canvas.drawString(
        15 * mm,
        PAGE_HEIGHT - 11 * mm,
        company_name[:55],
    )

    canvas.setFont(
        "Helvetica",
        9,
    )

    canvas.drawString(
        15 * mm,
        PAGE_HEIGHT - 18 * mm,
        f"Nifty 100 Company Tearsheet  |  {ticker}",
    )

    # Page number
    canvas.setFont(
        "Helvetica",
        7,
    )

    canvas.setFillColor(GREY)

    canvas.drawRightString(
        PAGE_WIDTH - 12 * mm,
        8 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


# ============================================================
# KPI TILES
# ============================================================


def create_kpi_tiles(kpis):
    "Create kpi tiles."

    cells = []

    for label, value in kpis:

        tile = Table(
            [
                [
                    paragraph(
                        label,
                        KPI_LABEL_STYLE,
                    )
                ],
                [
                    paragraph(
                        value,
                        KPI_VALUE_STYLE,
                    )
                ],
            ],
            colWidths=[53 * mm],
            rowHeights=[
                9 * mm,
                12 * mm,
            ],
        )

        tile.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        LIGHT_BLUE,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        colors.HexColor("#CBD5E1"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                ]
            )
        )

        cells.append(tile)

    rows = [
        cells[0:3],
        cells[3:6],
    ]

    table = Table(
        rows,
        colWidths=[
            56 * mm,
            56 * mm,
            56 * mm,
        ],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
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
                    1.5 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    1.5 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    1.5 * mm,
                ),
            ]
        )
    )

    return table


# ============================================================
# REVENUE / PROFIT CHART
# ============================================================


def create_revenue_profit_chart(
    pnl,
):
    "Create revenue profit chart."

    data = prepare_year_data(pnl)

    data = data.tail(10)

    if data.empty:
        return None

    years = data["year_num"].astype(str).tolist()

    revenue = pd.to_numeric(
        data["sales"],
        errors="coerce",
    ).fillna(0)

    profit = pd.to_numeric(
        data["net_profit"],
        errors="coerce",
    ).fillna(0)

    x = np.arange(len(years))

    width = 0.38

    fig, ax = plt.subplots(
        figsize=(7.0, 2.35),
        dpi=150,
    )

    ax.bar(
        x - width / 2,
        revenue,
        width,
        label="Revenue",
    )

    ax.bar(
        x + width / 2,
        profit,
        width,
        label="Net Profit",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        years,
        rotation=45,
        ha="right",
        fontsize=6,
    )

    ax.set_ylabel(
        "₹ Cr",
        fontsize=7,
    )

    ax.set_title(
        "10-Year Revenue and Net Profit",
        fontsize=9,
        fontweight="bold",
    )

    ax.tick_params(
        axis="y",
        labelsize=6,
    )

    ax.legend(
        fontsize=6,
        loc="upper left",
    )

    ax.grid(
        axis="y",
        alpha=0.2,
    )

    fig.tight_layout()

    buffer = io.BytesIO()

    fig.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
    )

    plt.close(fig)

    buffer.seek(0)

    return Image(
        buffer,
        width=91 * mm,
        height=48 * mm,
    )


# ============================================================
# ROE / ROCE DUAL AXIS CHART
# ============================================================


def create_roe_roce_chart(
    ratios,
    roce_value=None,
):
    "Create roe roce chart."

    data = prepare_year_data(ratios)

    if data.empty:
        return None

    data = data.tail(10)

    years = data["year_num"].astype(str).tolist()

    roe = pd.to_numeric(
        data["return_on_equity_pct"],
        errors="coerce",
    )

    roce = pd.Series(
        [roce_value] * len(data),
        index=data.index,
        dtype="float64",
    )

    fig, ax1 = plt.subplots(
        figsize=(7.0, 2.35),
        dpi=150,
    )

    ax1.plot(
        years,
        roe,
        marker="o",
        linewidth=1.6,
        label="ROE",
    )

    ax1.set_ylabel(
        "ROE (%)",
        fontsize=7,
    )

    ax1.tick_params(
        axis="both",
        labelsize=6,
    )

    ax2 = ax1.twinx()

    ax2.plot(
        years,
        roce,
        marker="s",
        linewidth=1.6,
        linestyle="--",
        label="ROCE",
    )

    ax2.set_ylabel(
        "ROCE (%)",
        fontsize=7,
    )

    ax2.tick_params(
        axis="y",
        labelsize=6,
    )

    ax1.set_title(
        "ROE and ROCE Trend",
        fontsize=9,
        fontweight="bold",
    )

    ax1.tick_params(
        axis="x",
        rotation=45,
    )

    ax1.grid(
        axis="y",
        alpha=0.2,
    )

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        fontsize=6,
        loc="upper left",
    )

    fig.tight_layout()

    buffer = io.BytesIO()

    fig.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
    )

    plt.close(fig)

    buffer.seek(0)

    return Image(
        buffer,
        width=91 * mm,
        height=48 * mm,
    )


# ============================================================
# BALANCE SHEET STACKED BAR
# ============================================================


def create_balance_chart(
    balance,
):
    "Create balance chart."

    data = prepare_year_data(balance)

    if data.empty:
        return None

    data = data.tail(8)

    years = data["year_num"].astype(str).tolist()

    equity = pd.to_numeric(
        data["equity_capital"],
        errors="coerce",
    ).fillna(
        0
    ) + pd.to_numeric(data["reserves"], errors="coerce",).fillna(0)

    borrowings = pd.to_numeric(
        data["borrowings"],
        errors="coerce",
    ).fillna(0)

    other = pd.to_numeric(
        data["other_liabilities"],
        errors="coerce",
    ).fillna(0)

    x = np.arange(len(years))

    fig, ax = plt.subplots(
        figsize=(7.0, 2.5),
        dpi=150,
    )

    ax.bar(
        x,
        equity,
        label="Equity",
    )

    ax.bar(
        x,
        borrowings,
        bottom=equity,
        label="Borrowings",
    )

    ax.bar(
        x,
        other,
        bottom=equity + borrowings,
        label="Other Liabilities",
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        years,
        rotation=45,
        ha="right",
        fontsize=6,
    )

    ax.set_ylabel(
        "₹ Cr",
        fontsize=7,
    )

    ax.set_title(
        "Balance Sheet Composition",
        fontsize=9,
        fontweight="bold",
    )

    ax.tick_params(
        axis="y",
        labelsize=6,
    )

    ax.legend(
        fontsize=6,
        loc="upper left",
    )

    ax.grid(
        axis="y",
        alpha=0.2,
    )

    fig.tight_layout()

    buffer = io.BytesIO()

    fig.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
    )

    plt.close(fig)

    buffer.seek(0)

    return Image(
        buffer,
        width=91 * mm,
        height=48 * mm,
    )


# ============================================================
# CASH FLOW WATERFALL
# ============================================================


def create_cashflow_waterfall(
    cashflow,
):
    "Create cashflow waterfall."

    data = prepare_year_data(cashflow)

    if data.empty:
        return None

    latest = data.iloc[-1]

    values = [
        latest["operating_activity"],
        latest["investing_activity"],
        latest["financing_activity"],
        latest["net_cash_flow"],
    ]

    labels = [
        "CFO",
        "CFI",
        "CFF",
        "Net Cash Flow",
    ]

    fig, ax = plt.subplots(
        figsize=(7.0, 2.5),
        dpi=150,
    )

    # Cumulative waterfall positions
    bottoms = []
    heights = []

    cumulative = 0

    for i, value in enumerate(values):

        value = 0 if pd.isna(value) else float(value)

        if i == 3:

            bottoms.append(0)
            heights.append(value)

        else:

            if value >= 0:

                bottoms.append(cumulative)
                heights.append(value)

            else:

                bottoms.append(cumulative + value)
                heights.append(abs(value))

            cumulative += value

    ax.bar(
        range(4),
        heights,
        bottom=bottoms,
    )

    ax.axhline(
        0,
        linewidth=0.8,
    )

    ax.set_xticks(range(4))

    ax.set_xticklabels(
        labels,
        fontsize=7,
    )

    ax.set_ylabel(
        "₹ Cr",
        fontsize=7,
    )

    ax.set_title(
        f"Cash Flow Waterfall — {latest['year_num']}",
        fontsize=9,
        fontweight="bold",
    )

    ax.tick_params(
        axis="y",
        labelsize=6,
    )

    ax.grid(
        axis="y",
        alpha=0.2,
    )

    fig.tight_layout()

    buffer = io.BytesIO()

    fig.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
    )

    plt.close(fig)

    buffer.seek(0)

    return Image(
        buffer,
        width=91 * mm,
        height=48 * mm,
    )


# ============================================================
# PROS / CONS
# ============================================================


def load_pros_cons(
    company_id,
):
    "Load pros cons."

    if not PROS_CONS_FILE.exists():
        return [], []

    df = pd.read_csv(PROS_CONS_FILE)

    company = df[df["company_id"] == company_id].copy()

    pros = company[company["type"].str.lower() == "pro"].sort_values(
        "confidence_pct",
        ascending=False,
    )

    cons = company[company["type"].str.lower() == "con"].sort_values(
        "confidence_pct",
        ascending=False,
    )

    return (
        pros["text"].dropna().tolist()[:6],
        cons["text"].dropna().tolist()[:6],
    )


# ============================================================
# CAPITAL ALLOCATION
# ============================================================


def load_capital_allocation(
    company_id,
):
    "Load capital allocation."

    if not CASHFLOW_INTELLIGENCE_FILE.exists():
        return "Insufficient Data"

    df = pd.read_excel(CASHFLOW_INTELLIGENCE_FILE)

    row = df[df["company_id"] == company_id]

    if row.empty:
        return "Insufficient Data"

    value = row.iloc[0].get("capital_allocation_label")

    if pd.isna(value):
        return "Insufficient Data"

    return str(value)


# ============================================================
# PAGE 1
# ============================================================


def build_page_1(
    story,
    company,
    sector,
    ratios,
    pnl,
):
    "Build page 1."

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    # Sector information
    sector_text = f"{sector} | " f"{company.iloc[0].get('about_company', '')}"

    story.append(
        paragraph(
            sector_text,
            SMALL_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    # --------------------------------------------------------
    # Six KPI tiles
    # --------------------------------------------------------

    latest_ratios = prepare_year_data(ratios)

    if not latest_ratios.empty:
        latest = latest_ratios.iloc[-1]
    else:
        latest = {}

    kpis = [
        (
            "ROE",
            fmt_pct(
                latest.get(
                    "return_on_equity_pct",
                    np.nan,
                )
            ),
        ),
        (
            "ROCE",
            fmt_pct(
                company.iloc[0].get(
                    "roce_percentage",
                    np.nan,
                )
            ),
        ),
        (
            "Debt / Equity",
            fmt_number(
                latest.get(
                    "debt_to_equity",
                    np.nan,
                ),
                2,
            ),
        ),
        (
            "Revenue CAGR 5Y",
            fmt_pct(
                latest.get(
                    "revenue_cagr_5yr",
                    np.nan,
                )
            ),
        ),
        (
            "PAT CAGR 5Y",
            fmt_pct(
                latest.get(
                    "pat_cagr_5yr",
                    np.nan,
                )
            ),
        ),
        (
            "Free Cash Flow",
            (
                "₹"
                + fmt_number(
                    latest.get(
                        "free_cash_flow_cr",
                        np.nan,
                    )
                    / 1,
                    0,
                )
                + " Cr"
                if not pd.isna(
                    latest.get(
                        "free_cash_flow_cr",
                        np.nan,
                    )
                )
                else "N/A"
            ),
        ),
    ]

    story.append(create_kpi_tiles(kpis))

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    # --------------------------------------------------------
    # Charts
    # --------------------------------------------------------

    revenue_chart = create_revenue_profit_chart(pnl)

    roe_chart = create_roe_roce_chart(
        ratios,
        company.iloc[0].get("roce_percentage"),
    )

    chart_table = Table(
        [
            [
                revenue_chart
                or paragraph(
                    "Revenue / Profit chart unavailable.",
                    SMALL_STYLE,
                ),
                roe_chart
                or paragraph(
                    "ROE / ROCE chart unavailable.",
                    SMALL_STYLE,
                ),
            ]
        ],
        colWidths=[
            93 * mm,
            93 * mm,
        ],
    )

    chart_table.setStyle(
        TableStyle(
            [
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
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm,
                ),
            ]
        )
    )

    story.append(chart_table)


# ============================================================
# PAGE 2
# ============================================================


def build_page_2(
    story,
    company_id,
    balance,
    cashflow,
):
    "Build page 2."

    # --------------------------------------------------------
    # Balance sheet chart
    # --------------------------------------------------------

    story.append(
        paragraph(
            "Balance Sheet Composition",
            SECTION_STYLE,
        )
    )

    balance_chart = create_balance_chart(balance)

    if balance_chart:
        story.append(balance_chart)
    else:
        story.append(
            paragraph(
                "Balance sheet data unavailable.",
                SMALL_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            2 * mm,
        )
    )

    # --------------------------------------------------------
    # Cash flow waterfall
    # --------------------------------------------------------

    story.append(
        paragraph(
            "Latest-Year Cash Flow",
            SECTION_STYLE,
        )
    )

    cashflow_chart = create_cashflow_waterfall(cashflow)

    if cashflow_chart:
        story.append(cashflow_chart)
    else:
        story.append(
            paragraph(
                "Cash-flow data unavailable.",
                SMALL_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            2 * mm,
        )
    )

    # --------------------------------------------------------
    # Pros / Cons
    # --------------------------------------------------------

    pros, cons = load_pros_cons(company_id)

    pros_flowables = []

    if pros:

        for item in pros:

            pros_flowables.append(
                paragraph(
                    "• " + item,
                    BULLET_STYLE,
                )
            )

    else:

        pros_flowables.append(
            paragraph(
                "• No generated pros available.",
                BULLET_STYLE,
            )
        )

    cons_flowables = []

    if cons:

        for item in cons:

            cons_flowables.append(
                paragraph(
                    "• " + item,
                    BULLET_STYLE,
                )
            )

    else:

        cons_flowables.append(
            paragraph(
                "• No generated cons available.",
                BULLET_STYLE,
            )
        )

    pros_table = Table(
        [
            [
                paragraph(
                    "<b>Pros</b>",
                    ParagraphStyle(
                        "ProsHeader",
                        parent=SECTION_STYLE,
                        textColor=GREEN,
                    ),
                ),
                paragraph(
                    "<b>Cons</b>",
                    ParagraphStyle(
                        "ConsHeader",
                        parent=SECTION_STYLE,
                        textColor=RED,
                    ),
                ),
            ],
            [
                pros_flowables,
                cons_flowables,
            ],
        ],
        colWidths=[
            93 * mm,
            93 * mm,
        ],
    )

    pros_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    LIGHT_GREEN,
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    LIGHT_RED,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#DDDDDD"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#DDDDDD"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm,
                ),
            ]
        )
    )

    story.append(pros_table)

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    # --------------------------------------------------------
    # Capital allocation badge
    # --------------------------------------------------------

    allocation = load_capital_allocation(company_id)

    badge = Table(
        [
            [
                paragraph(
                    f"CAPITAL ALLOCATION: {allocation}",
                    BADGE_STYLE,
                )
            ]
        ],
        colWidths=[186 * mm],
        rowHeights=[9 * mm],
    )

    badge.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    NAVY,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    NAVY,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
            ]
        )
    )

    story.append(badge)


# ============================================================
# GENERATE TEARSHEET
# ============================================================


def generate_tearsheet(
    company_id,
    output_path=None,
):
    "Generate tearsheet."

    (
        company,
        sectors,
        ratios,
        pnl,
        balance,
        cashflow,
    ) = load_company_data(company_id)

    if company.empty:

        raise ValueError(f"Company {company_id} not found.")

    company_name = company.iloc[0]["company_name"]

    sector = sectors.iloc[0]["broad_sector"] if not sectors.empty else "Unknown"

    if output_path is None:

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = OUTPUT_DIR / f"{company_id}_tearsheet.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=28 * mm,
        bottomMargin=12 * mm,
        title=(f"{company_name} " f"({company_id}) Tearsheet"),
        author="Nifty 100 Analytics",
    )

    story = []

    # Page 1
    build_page_1(
        story,
        company,
        sector,
        ratios,
        pnl,
    )

    # Page 2
    story.append(PageBreak())

    build_page_2(
        story,
        company_id,
        balance,
        cashflow,
    )

    def page_callback(
        canvas,
        doc,
    ):
        "Page callback."
        draw_page_header(
            canvas,
            doc,
            company_name,
            company_id,
        )

    doc.build(
        story,
        onFirstPage=page_callback,
        onLaterPages=page_callback,
    )

    return Path(output_path)


# ============================================================
# TEST 5 COMPANIES
# ============================================================

TEST_COMPANIES = [
    "TCS",
    "HDFCBANK",
    "RELIANCE",
    "SUNPHARMA",
    "TATASTEEL",
]


def test_tearsheets():
    "Test tearsheets."

    print("=" * 78)
    print("DAY 33 - PDF TEARSHEET TEMPLATE TEST")
    print("=" * 78)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []

    for ticker in TEST_COMPANIES:

        output = OUTPUT_DIR / f"{ticker}_tearsheet.pdf"

        try:

            generated = generate_tearsheet(
                ticker,
                output,
            )

            results.append(
                {
                    "company_id": ticker,
                    "status": "PASS",
                    "file": str(generated),
                }
            )

            print(f"PASS  {ticker:<12} " f"{generated}")

        except (KeyError, TypeError, ValueError, OSError) as exc:

            results.append(
                {
                    "company_id": ticker,
                    "status": "FAIL",
                    "file": str(output),
                    "error": str(exc),
                }
            )

            print(f"FAIL  {ticker:<12} " f"{exc}")

    print()
    print("=" * 78)
    print("DAY 33 TEST SUMMARY")
    print("=" * 78)

    result_df = pd.DataFrame(results)

    print(result_df.to_string(index=False))

    passed = int((result_df["status"] == "PASS").sum())

    failed = int((result_df["status"] == "FAIL").sum())

    print()
    print(
        "Passed:",
        passed,
    )

    print(
        "Failed:",
        failed,
    )

    print()
    print(
        "Generated files are in:",
        OUTPUT_DIR,
    )

    if failed == 0:

        print()
        print("STATUS: 5 test tearsheets generated successfully.")

        print(
            "IMPORTANT: Open all 5 PDFs and visually verify"
            " that no text/chart overlaps occur."
        )

    else:

        print()
        print("STATUS: FIX FAILURES BEFORE DAY 34.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    test_tearsheets()
