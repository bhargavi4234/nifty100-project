from src.analytics.cagr import (
    calculate_cagr,
    calculate_growth_metrics,
    eps_cagr,
    pat_cagr,
    revenue_cagr,
)

# -----------------------------------------------------
# CAGR Formula
# -----------------------------------------------------


def test_calculate_cagr_normal():

    cagr, flag = calculate_cagr(100, 200, 5, 5)

    assert round(cagr, 2) == 14.87
    assert flag is None


# -----------------------------------------------------
# Edge Cases
# -----------------------------------------------------


def test_turnaround():

    cagr, flag = calculate_cagr(-100, 200, 5, 5)

    assert cagr is None
    assert flag == "TURNAROUND"


def test_decline_to_loss():

    cagr, flag = calculate_cagr(100, -50, 5, 5)

    assert cagr is None
    assert flag == "DECLINE_TO_LOSS"


def test_both_negative():

    cagr, flag = calculate_cagr(-100, -50, 5, 5)

    assert cagr is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base():

    cagr, flag = calculate_cagr(0, 100, 5, 5)

    assert cagr is None
    assert flag == "ZERO_BASE"


def test_insufficient_years():

    cagr, flag = calculate_cagr(100, 200, 3, 5)

    assert cagr is None
    assert flag == "INSUFFICIENT"


# -----------------------------------------------------
# Wrapper Functions
# -----------------------------------------------------


def test_revenue_cagr():

    cagr, flag = revenue_cagr(100, 200, 5, 5)

    assert round(cagr, 2) == 14.87
    assert flag is None


def test_pat_cagr():

    cagr, flag = pat_cagr(100, 200, 5, 5)

    assert round(cagr, 2) == 14.87
    assert flag is None


def test_eps_cagr():

    cagr, flag = eps_cagr(100, 200, 5, 5)

    assert round(cagr, 2) == 14.87
    assert flag is None


# -----------------------------------------------------
# Growth Metrics
# -----------------------------------------------------


def test_calculate_growth_metrics():

    sample = {
        "revenue_start": 100,
        "revenue_end": 200,
        "pat_start": 50,
        "pat_end": 100,
        "eps_start": 10,
        "eps_end": 20,
        "years_available": 10,
    }

    result = calculate_growth_metrics(sample)

    assert "revenue_cagr_3yr" in result
    assert "revenue_cagr_5yr" in result
    assert "revenue_cagr_10yr" in result

    assert "pat_cagr_5yr_flag" in result
    assert "eps_cagr_10yr_flag" in result
