from src.analytics.cagr import calculate_cagr
from src.analytics.cashflow import cfo_quality_score
from src.analytics.ratios import (
    check_opm_difference,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    return_on_equity,
)

# ============================================================
# ROE TESTS
# ============================================================


def test_roe_positive_equity():
    """ROE should calculate normally when equity is positive."""
    result = return_on_equity(net_profit=200, equity_capital=500, reserves=500)

    assert result == 20.0


def test_roe_negative_equity_returns_none():
    """ROE should return None when total equity is negative."""
    result = return_on_equity(net_profit=100, equity_capital=100, reserves=-150)

    assert result is None


# ============================================================
# DEBT-TO-EQUITY TESTS
# ============================================================


def test_debt_to_equity_debt_free_returns_zero():
    """Debt-free company should have D/E = 0."""
    result = debt_to_equity(borrowings=0, equity_capital=500, reserves=500)

    assert result == 0


def test_debt_to_equity_normal():
    """Normal D/E calculation."""
    result = debt_to_equity(borrowings=300, equity_capital=500, reserves=500)

    assert result == 0.3


def test_debt_to_equity_negative_equity_returns_none():
    """D/E should return None when total equity is <= 0."""
    result = debt_to_equity(borrowings=300, equity_capital=100, reserves=-100)

    assert result is None


# ============================================================
# HIGH LEVERAGE FLAG TESTS
# ============================================================


def test_high_leverage_non_financial_flag():
    """D/E > 5 should be flagged for non-financial companies."""
    result = high_leverage_flag(debt_equity=6.0, broad_sector="Industrials")

    assert result is True


def test_high_leverage_financial_sector_not_flagged():
    """D/E > 5 should not be flagged for Financials."""
    result = high_leverage_flag(debt_equity=6.0, broad_sector="Financials")

    assert result is False


# ============================================================
# INTEREST COVERAGE RATIO TESTS
# ============================================================


def test_icr_zero_interest_returns_none():
    """ICR should return None when interest expense is zero."""
    result = interest_coverage_ratio(operating_profit=500, other_income=50, interest=0)

    assert result is None


def test_icr_normal_calculation():
    """Normal ICR calculation."""
    result = interest_coverage_ratio(
        operating_profit=500, other_income=100, interest=100
    )

    assert result == 6.0


def test_icr_low_value():
    """ICR can correctly calculate a value below 1.5."""
    result = interest_coverage_ratio(
        operating_profit=100, other_income=20, interest=100
    )

    assert result == 1.2


# ============================================================
# OPM CROSS-CHECK TESTS
# ============================================================


def test_opm_difference_divergence_flag():
    """Difference greater than 1 percentage point should flag."""
    result = check_opm_difference(calculated_opm=15.0, source_opm=17.0)

    assert result is True


def test_opm_difference_within_threshold():
    """Difference of 1 percentage point or less should not flag."""
    result = check_opm_difference(calculated_opm=15.0, source_opm=15.5)

    assert result is False


# ============================================================
# CAGR TESTS
# ============================================================


def test_cagr_normal_calculation():
    """Normal CAGR should calculate correctly."""
    result, flag = calculate_cagr(
        start_value=100, end_value=121, years_available=5, required_years=2
    )

    assert result == 10.0
    assert flag is None


def test_cagr_turnaround_flag():
    """Negative start and positive end should be TURNAROUND."""
    result, flag = calculate_cagr(
        start_value=-100, end_value=200, years_available=5, required_years=5
    )

    assert result is None
    assert flag == "TURNAROUND"


def test_cagr_decline_to_loss_flag():
    """Positive start and negative end should be DECLINE_TO_LOSS."""
    result, flag = calculate_cagr(
        start_value=100, end_value=-50, years_available=5, required_years=5
    )

    assert result is None
    assert flag == "DECLINE_TO_LOSS"


def test_cagr_insufficient_years_flag():
    """Insufficient history should return INSUFFICIENT."""
    result, flag = calculate_cagr(
        start_value=100, end_value=150, years_available=3, required_years=5
    )

    assert result is None
    assert flag == "INSUFFICIENT"


def test_cagr_zero_base_flag():
    """Zero starting value should return ZERO_BASE."""
    result, flag = calculate_cagr(
        start_value=0, end_value=100, years_available=5, required_years=5
    )

    assert result is None
    assert flag == "ZERO_BASE"


# ============================================================
# CFO QUALITY SCORE TESTS
# ============================================================


def test_cfo_quality_high():
    """CFO/PAT > 1 should be High Quality."""
    ratio, label = cfo_quality_score(cfo_total=120, pat_total=100)

    assert ratio == 1.2
    assert label == "High Quality"


def test_cfo_quality_moderate():
    """CFO/PAT between 0.5 and 1 should be Moderate."""
    ratio, label = cfo_quality_score(cfo_total=75, pat_total=100)

    assert ratio == 0.75
    assert label == "Moderate"


def test_cfo_quality_accrual_risk():
    """CFO/PAT below 0.5 should be Accrual Risk."""
    ratio, label = cfo_quality_score(cfo_total=30, pat_total=100)

    assert ratio == 0.3
    assert label == "Accrual Risk"


def test_cfo_quality_zero_pat():
    """Zero PAT should return None values."""
    ratio, label = cfo_quality_score(cfo_total=100, pat_total=0)

    assert ratio is None
    assert label is None
