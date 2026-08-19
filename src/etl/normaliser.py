import re

import pandas as pd


def normalize_year(year):
    "Normalize year."
    if pd.isna(year):
        return None

    year = str(year).strip().upper()
    year = year.replace("FY", "")

    if len(year) == 2 and year.isdigit():
        return 2000 + int(year)

    year = year.removesuffix(".0")

    if year.isdigit():
        return int(year)

    return None


def normalize_ticker(ticker):
    "Normalize ticker."
    if pd.isna(ticker):
        return None

    ticker = str(ticker).strip().upper()
    ticker = ticker.replace(".NS", "")
    ticker = ticker.replace(".BO", "")
    ticker = re.sub(r"[^A-Z0-9]", "", ticker)

    return ticker


def clean_text(text):
    "Clean text."
    if pd.isna(text):
        return None

    return " ".join(str(text).split())


def remove_commas(value):
    "Remove commas."
    if pd.isna(value):
        return None

    return str(value).replace(",", "")


def to_float(value):
    "To float."
    if pd.isna(value):
        return None

    try:
        value = remove_commas(value)
        return float(value)
    except ValueError:
        return None
