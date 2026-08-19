from src.analytics.cashflow import (
    capex_intensity,
    capital_allocation_pattern,
    cfo_quality_score,
    fcf_conversion_rate,
    free_cash_flow,
    generate_capital_allocation_record,
)

# -----------------------------------------------------
# Free Cash Flow
# -----------------------------------------------------


def test_free_cash_flow():
    assert free_cash_flow(1000, -300) == 700


# -----------------------------------------------------
# CFO Quality Score
# -----------------------------------------------------


def test_cfo_quality_high():
    ratio, label = cfo_quality_score(600, 500)

    assert ratio == 1.2
    assert label == "High Quality"


def test_cfo_quality_moderate():
    ratio, label = cfo_quality_score(300, 500)

    assert ratio == 0.6
    assert label == "Moderate"


def test_cfo_quality_accrual():
    ratio, label = cfo_quality_score(100, 500)

    assert ratio == 0.2
    assert label == "Accrual Risk"


def test_cfo_quality_zero_pat():
    ratio, label = cfo_quality_score(100, 0)

    assert ratio is None
    assert label is None


# -----------------------------------------------------
# CapEx Intensity
# -----------------------------------------------------


def test_capex_asset_light():
    value, label = capex_intensity(-20, 1000)

    assert value == 2.0
    assert label == "Asset Light"


def test_capex_moderate():
    value, label = capex_intensity(-50, 1000)

    assert value == 5.0
    assert label == "Moderate"


def test_capex_capital_intensive():
    value, label = capex_intensity(-120, 1000)

    assert value == 12.0
    assert label == "Capital Intensive"


# -----------------------------------------------------
# FCF Conversion
# -----------------------------------------------------


def test_fcf_conversion():
    assert fcf_conversion_rate(700, 1000) == 70.0


def test_fcf_conversion_zero_profit():
    assert fcf_conversion_rate(700, 0) is None


# -----------------------------------------------------
# Capital Allocation Patterns
# -----------------------------------------------------


def test_pattern_reinvestor():
    _, _, _, label = capital_allocation_pattern(100, -50, -20, 0.8)

    assert label == "Reinvestor"


def test_pattern_shareholder_returns():
    _, _, _, label = capital_allocation_pattern(100, -50, -20, 1.2)

    assert label == "Shareholder Returns"


def test_pattern_distress():
    _, _, _, label = capital_allocation_pattern(-100, 50, 30)

    assert label == "Distress Signal"


# -----------------------------------------------------
# Summary Function
# -----------------------------------------------------


def test_generate_capital_allocation_record():

    sample = {
        "company_id": 1,
        "year": 2025,
        "operating_activity": 1000,
        "investing_activity": -300,
        "financing_activity": -200,
        "cfo_total": 1200,
        "pat_total": 1000,
        "sales": 5000,
        "operating_profit": 900,
    }

    result = generate_capital_allocation_record(sample)

    assert result["company_id"] == 1
    assert result["year"] == 2025
    assert result["pattern_label"] == "Shareholder Returns"
