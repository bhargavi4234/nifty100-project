from src.analytics.ratios import (
    asset_turnover,
    calculate_profitability_ratios,
    check_opm_difference,
    debt_to_equity,
    high_leverage_flag,
    icr_label,
    icr_warning_flag,
    interest_coverage_ratio,
    net_debt,
    net_profit_margin,
    operating_profit_margin,
    return_on_assets,
    return_on_capital_employed,
    return_on_equity,
    roce_benchmark,
    safe_divide,
)

# -----------------------------------------------------
# Safe Divide
# -----------------------------------------------------


def test_safe_divide_normal():
    assert safe_divide(100, 10) == 10


def test_safe_divide_zero():
    assert safe_divide(100, 0) is None


# -----------------------------------------------------
# Net Profit Margin
# -----------------------------------------------------


def test_net_profit_margin_normal():
    assert net_profit_margin(100, 1000) == 10.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


# -----------------------------------------------------
# Operating Profit Margin
# -----------------------------------------------------


def test_operating_profit_margin_normal():
    assert operating_profit_margin(250, 1000) == 25.0


# -----------------------------------------------------
# OPM Cross Check
# -----------------------------------------------------


def test_opm_difference_true():
    assert check_opm_difference(18.0, 20.5) is True


def test_opm_difference_false():
    assert check_opm_difference(20.0, 20.8) is False


# -----------------------------------------------------
# Return on Equity
# -----------------------------------------------------


def test_return_on_equity_normal():
    assert return_on_equity(100, 500, 500) == 10.0


def test_return_on_equity_negative_equity():
    assert return_on_equity(100, -100, 50) is None


def test_return_on_equity_zero_equity():
    assert return_on_equity(100, 0, 0) is None


# -----------------------------------------------------
# Return on Capital Employed
# -----------------------------------------------------


def test_return_on_capital_employed_normal():
    assert return_on_capital_employed(200, 500, 500, 1000) == 10.0


def test_return_on_capital_employed_zero():
    assert return_on_capital_employed(100, 0, 0, 0) is None


# -----------------------------------------------------
# Return on Assets
# -----------------------------------------------------


def test_return_on_assets_normal():
    assert return_on_assets(100, 1000) == 10.0


def test_return_on_assets_zero_assets():
    assert return_on_assets(100, 0) is None


# -----------------------------------------------------
# ROCE Benchmark
# -----------------------------------------------------


def test_roce_benchmark_financial():
    assert roce_benchmark("Financials") == "sector_relative"


def test_roce_benchmark_non_financial():
    assert roce_benchmark("Information Technology") == "standard"


# -----------------------------------------------------
# Full Ratio Calculation
# -----------------------------------------------------


def test_calculate_profitability_ratios():

    sample = {
        "sales": 1000,
        "net_profit": 100,
        "operating_profit": 200,
        "equity_capital": 500,
        "reserves": 500,
        "borrowings": 1000,
        "total_assets": 2500,
        "opm_percentage": 20,
        "broad_sector": "Industrials",
    }

    result = calculate_profitability_ratios(sample)

    assert result["net_profit_margin"] == 10.0
    assert result["operating_profit_margin"] == 20.0
    assert result["roe"] == 10.0
    assert result["roce"] == 10.0
    assert result["roa"] == 4.0
    assert result["roce_benchmark"] == "standard"


# -----------------------------------------------------
# Financial Sector Test
# -----------------------------------------------------


def test_calculate_profitability_ratios_financial():

    sample = {
        "sales": 5000,
        "net_profit": 400,
        "operating_profit": 700,
        "equity_capital": 1000,
        "reserves": 1500,
        "borrowings": 3000,
        "total_assets": 12000,
        "opm_percentage": 14,
        "broad_sector": "Financials",
    }

    result = calculate_profitability_ratios(sample)

    assert result["roce_benchmark"] == "sector_relative"


# -----------------------------------------------------
# Edge Case
# -----------------------------------------------------


def test_calculate_profitability_ratios_zero_sales():

    sample = {
        "sales": 0,
        "net_profit": 100,
        "operating_profit": 150,
        "equity_capital": 100,
        "reserves": 100,
        "borrowings": 100,
        "total_assets": 1000,
        "opm_percentage": 15,
        "broad_sector": "Industrials",
    }

    result = calculate_profitability_ratios(sample)

    assert result["net_profit_margin"] is None
    assert result["operating_profit_margin"] is None


# -----------------------------------------------------
# Edge Case
# -----------------------------------------------------


def test_calculate_profitability_ratios_negative_equity():

    sample = {
        "sales": 1000,
        "net_profit": 100,
        "operating_profit": 150,
        "equity_capital": -200,
        "reserves": 100,
        "borrowings": 200,
        "total_assets": 1000,
        "opm_percentage": 15,
        "broad_sector": "Industrials",
    }

    result = calculate_profitability_ratios(sample)

    assert result["roe"] is None


# -----------------------------------------------------
# Day 09 - Debt to Equity
# -----------------------------------------------------


def test_debt_to_equity_normal():
    assert debt_to_equity(1000, 500, 500) == 1.0


def test_debt_to_equity_zero_borrowings():
    assert debt_to_equity(0, 500, 500) == 0


# -----------------------------------------------------
# High Leverage Flag
# -----------------------------------------------------


def test_high_leverage_flag_true():
    assert high_leverage_flag(6.0, "Industrials") is True


def test_high_leverage_flag_financial():
    assert high_leverage_flag(6.0, "Financials") is False


# -----------------------------------------------------
# Interest Coverage Ratio
# -----------------------------------------------------


def test_interest_coverage_ratio():
    assert interest_coverage_ratio(200, 50, 50) == 5.0


def test_interest_coverage_ratio_zero_interest():
    assert interest_coverage_ratio(200, 50, 0) is None


# -----------------------------------------------------
# ICR Label & Warning
# -----------------------------------------------------


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_icr_warning_flag():
    assert icr_warning_flag(1.2) is True


# -----------------------------------------------------
# Net Debt
# -----------------------------------------------------


def test_net_debt():
    assert net_debt(1000, 300) == 700


# -----------------------------------------------------
# Asset Turnover
# -----------------------------------------------------


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2.0


def test_asset_turnover_zero_assets():
    assert asset_turnover(1000, 0) is None
