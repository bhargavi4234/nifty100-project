import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# DATABASE PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = PROJECT_ROOT / "data" / "db" / "nifty100.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================


def get_connection():
    """Create a SQLite database connection."""
    return sqlite3.connect(DB_PATH)


# ============================================================
# COMPANIES
# ============================================================


@st.cache_data(ttl=600)
def get_companies():
    """Return all companies with sector information."""

    query = """
        SELECT
            c.id AS ticker,
            c.company_name,
            c.about_company,
            c.company_logo,
            c.website,
            s.broad_sector AS sector,
            s.sub_sector,
            c.roce_percentage,
            c.roe_percentage
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        ORDER BY c.company_name
    """

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


# ============================================================
# FINANCIAL RATIOS
# ============================================================


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):
    """Return financial ratios for a company."""

    if year is None:
        query = """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
            ORDER BY year
        """
        params = (ticker,)

    else:
        query = """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
              AND year = ?
        """
        params = (ticker, year)

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


# ============================================================
# PROFIT AND LOSS
# ============================================================


@st.cache_data(ttl=600)
def get_pl(ticker):
    """Return profit and loss data for a company."""

    query = """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year
    """

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=(ticker,))


# ============================================================
# BALANCE SHEET
# ============================================================


@st.cache_data(ttl=600)
def get_bs(ticker):
    """Return balance sheet data for a company."""

    query = """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year
    """

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=(ticker,))


# ============================================================
# CASH FLOW
# ============================================================


@st.cache_data(ttl=600)
def get_cf(ticker):
    """Return cash flow data for a company."""

    query = """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year
    """

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=(ticker,))


# ============================================================
# SECTORS
# ============================================================


@st.cache_data(ttl=600)
def get_sectors():
    """Return sector information."""

    query = """
        SELECT *
        FROM sectors
        ORDER BY broad_sector
    """

    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


# ============================================================
# PEER GROUPS
# ============================================================


@st.cache_data(ttl=600)
def get_peers(group_name):
    """Return companies belonging to a peer group."""

    query = """
        SELECT *
        FROM peer_groups
        WHERE peer_group_name = ?
    """

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=(group_name,))


# ============================================================
# PROS AND CONS
# ============================================================


@st.cache_data(ttl=600)
def get_pros_cons(ticker):
    """Return pros and cons for a company."""

    query = """
        SELECT
            pros,
            cons
        FROM prosandcons
        WHERE company_id = ?
    """

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=(ticker,))


# ============================================================
# VALUATION
# ============================================================


@st.cache_data(ttl=600)
def get_valuation(ticker):
    """
    Return valuation data.

    The valuation table will be created during the
    valuation part of Sprint 4.
    """

    query = """
        SELECT *
        FROM valuation
        WHERE company_id = ?
    """

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=(ticker,))
