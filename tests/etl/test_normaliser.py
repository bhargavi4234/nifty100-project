
from src.etl.normaliser import (
    normalize_year,
    normalize_ticker,
    clean_text,
    remove_commas,
    to_float,
)


# ==========================
# normalize_year() - 20 Tests
# ==========================

def test_year_01():
    assert normalize_year("FY20") == 2020


def test_year_02():
    assert normalize_year("FY21") == 2021


def test_year_03():
    assert normalize_year("FY22") == 2022


def test_year_04():
    assert normalize_year("FY23") == 2023


def test_year_05():
    assert normalize_year("FY24") == 2024


def test_year_06():
    assert normalize_year("20") == 2020


def test_year_07():
    assert normalize_year("21") == 2021


def test_year_08():
    assert normalize_year("22") == 2022


def test_year_09():
    assert normalize_year("2020") == 2020


def test_year_10():
    assert normalize_year("2021") == 2021


def test_year_11():
    assert normalize_year("2022") == 2022


def test_year_12():
    assert normalize_year("2023") == 2023


def test_year_13():
    assert normalize_year("2024") == 2024


def test_year_14():
    assert normalize_year("2025") == 2025


def test_year_15():
    assert normalize_year("2021.0") == 2021


def test_year_16():
    assert normalize_year(" 2022 ") == 2022


def test_year_17():
    assert normalize_year(None) is None


def test_year_18():
    assert normalize_year("") is None


def test_year_19():
    assert normalize_year("ABC") is None


def test_year_20():
    assert normalize_year("FYAB") is None


# ==========================
# normalize_ticker() - 15 Tests
# ==========================

def test_ticker_01():
    assert normalize_ticker("TCS.NS") == "TCS"


def test_ticker_02():
    assert normalize_ticker("tcs.ns") == "TCS"


def test_ticker_03():
    assert normalize_ticker("RELIANCE.BO") == "RELIANCE"


def test_ticker_04():
    assert normalize_ticker("reliance.bo") == "RELIANCE"


def test_ticker_05():
    assert normalize_ticker("INFY") == "INFY"


def test_ticker_06():
    assert normalize_ticker(" infy ") == "INFY"


def test_ticker_07():
    assert normalize_ticker("HDFC-BANK") == "HDFCBANK"


def test_ticker_08():
    assert normalize_ticker("SBI.NS") == "SBI"


def test_ticker_09():
    assert normalize_ticker("ITC.BO") == "ITC"


def test_ticker_10():
    assert normalize_ticker("LT.NS") == "LT"


def test_ticker_11():
    assert normalize_ticker("M&M") == "MM"


def test_ticker_12():
    assert normalize_ticker("A B C") == "ABC"


def test_ticker_13():
    assert normalize_ticker("") == ""


def test_ticker_14():
    assert normalize_ticker(None) is None


def test_ticker_15():
    assert normalize_ticker("123ABC") == "123ABC"


# ==========================
# Helper Function Tests
# ==========================

def test_clean_text():
    assert clean_text(" Hello   World ") == "Hello World"


def test_remove_commas():
    assert remove_commas("1,23,456") == "123456"


def test_to_float():
    assert to_float("12,345.67") == 12345.67