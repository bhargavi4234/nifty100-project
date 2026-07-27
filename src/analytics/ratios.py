import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_divide(numerator, denominator):
    """
    Safely divide two numbers.

    Returns:
        None if denominator is None or zero.
    """
    if denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


# -------------------------------------------------------
# Profitability Ratios
# -------------------------------------------------------

def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = (Net Profit / Sales) × 100

    Returns None when sales is zero.
    """

    value = safe_divide(net_profit, sales)

    if value is None:
        return None

    return round(value * 100, 2)


def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = (Operating Profit / Sales) × 100

    Returns None when sales is zero.
    """

    value = safe_divide(operating_profit, sales)

    if value is None:
        return None

    return round(value * 100, 2)


# -------------------------------------------------------
# OPM Validation
# -------------------------------------------------------

def check_opm_difference(calculated_opm, source_opm):
    """
    Compare calculated OPM with source OPM.

    Returns:
        True if difference > 1%
        False otherwise
    """

    if calculated_opm is None:
        return False

    if source_opm is None:
        return False

    difference = abs(calculated_opm - source_opm)

    if difference > 1:
        logger.warning(
            f"OPM mismatch detected | "
            f"Calculated={calculated_opm:.2f}% "
            f"Source={source_opm:.2f}% "
            f"Difference={difference:.2f}%"
        )
        return True

    return False


# -------------------------------------------------------
# Return Ratios
# -------------------------------------------------------

def return_on_equity(net_profit, equity_capital, reserves):
    """
    ROE = Net Profit / (Equity Capital + Reserves) × 100

    Returns None if Equity + Reserves <= 0
    """

    equity = equity_capital + reserves

    if equity <= 0:
        logger.warning("Negative or zero equity encountered while computing ROE.")
        return None

    return round((net_profit / equity) * 100, 2)


def return_on_capital_employed(
    ebit,
    equity_capital,
    reserves,
    borrowings
):
    """
    ROCE = EBIT / (Equity + Reserves + Borrowings) × 100

    Returns None if capital employed <= 0
    """

    capital_employed = (
        equity_capital +
        reserves +
        borrowings
    )

    if capital_employed <= 0:
        logger.warning("Invalid capital employed while computing ROCE.")
        return None

    return round((ebit / capital_employed) * 100, 2)


def return_on_assets(net_profit, total_assets):
    """
    ROA = Net Profit / Total Assets × 100

    Returns None if total assets = 0
    """

    value = safe_divide(net_profit, total_assets)

    if value is None:
        return None

    return round(value * 100, 2)


# -------------------------------------------------------
# Financial Sector Benchmark
# -------------------------------------------------------

def roce_benchmark(broad_sector):
    """
    Financial companies (Banks/NBFCs)
    should use sector-relative benchmark.

    Returns:
        sector_relative
        standard
    """

    if broad_sector is None:
        return "standard"

    if broad_sector.strip().lower() == "financials":
        return "sector_relative"

    return "standard"


# -------------------------------------------------------
# Helper Function
# -------------------------------------------------------
def calculate_profitability_ratios(row):
    """
    Calculate all profitability, leverage,
    and efficiency ratios from a dictionary.
    """

    npm = net_profit_margin(
        row["net_profit"],
        row["sales"]
    )

    opm = operating_profit_margin(
        row["operating_profit"],
        row["sales"]
    )

    check_opm_difference(
        opm,
        row.get("opm_percentage")
    )

    roe = return_on_equity(
        row["net_profit"],
        row["equity_capital"],
        row["reserves"]
    )

    roce = return_on_capital_employed(
        row["operating_profit"],
        row["equity_capital"],
        row["reserves"],
        row["borrowings"]
    )

    roa = return_on_assets(
        row["net_profit"],
        row["total_assets"]
    )

    benchmark = roce_benchmark(
        row.get("broad_sector")
    )

    # Day 09 calculations

    de_ratio = debt_to_equity(
        row["borrowings"],
        row["equity_capital"],
        row["reserves"]
    )

    leverage_flag = high_leverage_flag(
        de_ratio,
        row.get("broad_sector", "")
    )

    icr = interest_coverage_ratio(
        row["operating_profit"],
        row.get("other_income", 0),
        row.get("interest", 0)
    )

    label = icr_label(icr)

    warning = icr_warning_flag(icr)

    debt = net_debt(
        row["borrowings"],
        row.get("investments", 0)
    )

    turnover = asset_turnover(
        row["sales"],
        row["total_assets"]
    )

    return {
        "net_profit_margin": npm,
        "operating_profit_margin": opm,
        "roe": roe,
        "roce": roce,
        "roa": roa,
        "roce_benchmark": benchmark,
        "debt_to_equity": de_ratio,
        "high_leverage_flag": leverage_flag,
        "interest_coverage_ratio": icr,
        "icr_label": label,
        "icr_warning_flag": warning,
        "net_debt": debt,
        "asset_turnover": turnover
    }


# -------------------------------------------------------
# Day 09 - Leverage & Efficiency Ratios
# -------------------------------------------------------

def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt-to-Equity Ratio
    """

    if borrowings == 0:
        return 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(borrowings / equity, 2)


def high_leverage_flag(debt_equity, broad_sector):
    """
    Returns True if D/E > 5
    and company is NOT in Financials sector.
    """

    if debt_equity is None:
        return False

    if (
        debt_equity > 5
        and broad_sector.lower() != "financials"
    ):
        return True

    return False


def interest_coverage_ratio(
    operating_profit,
    other_income,
    interest
):
    """
    Interest Coverage Ratio
    """

    if interest == 0:
        return None

    return round(
        (operating_profit + other_income) / interest,
        2
    )


def icr_label(icr):
    """
    Label for debt-free companies.
    """

    if icr is None:
        return "Debt Free"

    return ""


def icr_warning_flag(icr):
    """
    Returns True if ICR < 1.5
    """

    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings, investments):
    """
    Net Debt
    """

    return borrowings - investments


def asset_turnover(sales, total_assets):
    """
    Asset Turnover Ratio
    """

    if total_assets == 0:
        return None

    return round(sales / total_assets, 2)


if __name__ == "__main__":

    sample = {
        "sales": 1000,
        "net_profit": 120,
        "operating_profit": 180,
        "equity_capital": 200,
        "reserves": 800,
        "borrowings": 500,
        "total_assets": 2500,
        "opm_percentage": 18.0,
        "broad_sector": "Industrials"
    }

    ratios = calculate_profitability_ratios(sample)

    print("\nFinancial Ratios\n")

    for key, value in ratios.items():
        print(f"{key:25}: {value}")