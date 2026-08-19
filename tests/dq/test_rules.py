import pandas as pd

from src.etl.validator import (
    dq01_primary_key,
    dq02_company_year,
    dq03_foreign_key,
    dq04_balance_sheet,
    dq05_opm_crosscheck,
    dq06_positive_sales,
    dq07_year_format,
    dq08_ticker_format,
    dq09_net_cash,
    dq10_fixed_assets,
    dq11_tax_rate,
    dq12_dividend_payout,
    dq13_url_validation,
    dq14_eps_sign,
)


def assert_failure(result, rule_id, severity):
    assert len(result) >= 1
    assert result[0]["rule"] == rule_id
    assert result[0]["severity"] == severity


def test_dq01_primary_key():
    df = pd.DataFrame({"id": ["TCS", "TCS"]})

    result = dq01_primary_key(df)

    assert_failure(result, "DQ-01", "CRITICAL")


def test_dq02_company_year():
    df = pd.DataFrame(
        {"id": [1, 2], "company_id": ["TCS", "TCS"], "year": ["Mar 2024", "Mar 2024"]}
    )

    result = dq02_company_year(df, "profitandloss")

    assert_failure(result, "DQ-02", "CRITICAL")


def test_dq03_foreign_key():
    df = pd.DataFrame({"id": [1], "company_id": ["INVALID"]})

    result = dq03_foreign_key(df, "profitandloss", {"TCS", "INFY"})

    assert_failure(result, "DQ-03", "CRITICAL")


def test_dq04_balance_sheet():
    df = pd.DataFrame({"id": [1], "total_assets": [1000], "total_liabilities": [900]})

    result = dq04_balance_sheet(df)

    assert_failure(result, "DQ-04", "WARNING")


def test_dq05_opm_crosscheck():
    df = pd.DataFrame(
        {
            "id": [1],
            "sales": [1000],
            "expenses": [700],
            "operating_profit": [100],
            "opm_percentage": [10],
        }
    )

    result = dq05_opm_crosscheck(df)

    assert_failure(result, "DQ-05", "WARNING")


def test_dq06_positive_sales():
    df = pd.DataFrame({"id": [1], "company_id": ["TCS"], "sales": [0]})

    result = dq06_positive_sales(df)

    assert_failure(result, "DQ-06", "WARNING")


def test_dq07_year_format():
    df = pd.DataFrame({"id": [1], "year": ["2024"]})

    result = dq07_year_format(df)

    assert_failure(result, "DQ-07", "WARNING")


def test_dq08_ticker_format():
    df = pd.DataFrame({"id": ["tcs.ns"]})

    result = dq08_ticker_format(df)

    assert_failure(result, "DQ-08", "WARNING")


def test_dq09_net_cash():
    df = pd.DataFrame(
        {
            "id": [1],
            "operating_activity": [100],
            "investing_activity": [-50],
            "financing_activity": [20],
            "net_cash_flow": [500],
        }
    )

    result = dq09_net_cash(df)

    assert_failure(result, "DQ-09", "WARNING")


def test_dq10_fixed_assets():
    df = pd.DataFrame({"id": [1], "fixed_assets": [1200], "total_assets": [1000]})

    result = dq10_fixed_assets(df)

    assert_failure(result, "DQ-10", "WARNING")


def test_dq11_tax_rate():
    df = pd.DataFrame({"id": [1], "tax_percentage": [150]})

    result = dq11_tax_rate(df)

    assert_failure(result, "DQ-11", "WARNING")


def test_dq12_dividend_payout():
    df = pd.DataFrame({"id": [1], "dividend_payout": [-999]})

    result = dq12_dividend_payout(df)

    assert_failure(result, "DQ-12", "WARNING")


def test_dq13_url_validation():
    df = pd.DataFrame(
        {
            "id": ["TCS"],
            "website": ["invalid-url"],
            "nse_profile": [None],
            "bse_profile": [None],
            "chart_link": [None],
            "company_logo": [None],
        }
    )

    result = dq13_url_validation(df)

    assert_failure(result, "DQ-13", "WARNING")


def test_dq14_eps_sign():
    df = pd.DataFrame({"id": [1], "net_profit": [100], "eps": [-5]})

    result = dq14_eps_sign(df)

    assert_failure(result, "DQ-14", "WARNING")
