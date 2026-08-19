import sqlite3

import requests
import streamlit as st

# ==========================================================
# Configuration
# ==========================================================

DB_PATH = "data/db/nifty100.db"


# ==========================================================
# Database helpers
# ==========================================================


@st.cache_data(ttl=600)
def get_companies():
    """Return all companies with ticker and company name."""

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            id AS ticker,
            company_name
        FROM companies
        ORDER BY company_name
    """

    df = __import__("pandas").read_sql_query(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_reports(ticker):
    """Return annual reports available for a company."""

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            year,
            annual_report
        FROM documents
        WHERE company_id = ?
        ORDER BY year DESC
    """

    df = __import__("pandas").read_sql_query(query, conn, params=(ticker,))

    conn.close()

    return df


# ==========================================================
# Check URL
# ==========================================================


def check_report_url(url):
    """
    Check whether an annual report URL is available.

    Returns:
        True  -> URL appears available
        False -> URL unavailable / 404 / invalid
    """

    if not url:
        return False

    url = str(url).strip()

    if not url.startswith(("http://", "https://")):
        return False

    try:
        response = requests.head(url, allow_redirects=True, timeout=8)

        # Some servers do not support HEAD correctly.
        if response.status_code == 405:
            response = requests.get(url, allow_redirects=True, timeout=8, stream=True)

        return response.status_code < 400

    except requests.RequestException:
        return False


# ==========================================================
# Page
# ==========================================================

st.title("📄 Annual Reports")

st.write("Search for a company and view its available annual reports.")


# ==========================================================
# Company Search
# ==========================================================

companies = get_companies()

if companies.empty:
    st.warning("No companies found in the database.")
    st.stop()


search = st.text_input(
    "🔎 Search company or NSE ticker", placeholder="Example: TCS or Tata Consultancy"
)


# ==========================================================
# Filter companies
# ==========================================================

if search:

    search_text = search.strip().lower()

    matches = companies[
        companies["ticker"].str.lower().str.contains(search_text, na=False)
        | companies["company_name"].str.lower().str.contains(search_text, na=False)
    ]

else:
    matches = companies


# ==========================================================
# Company selection
# ==========================================================

if matches.empty:

    st.warning("Company not found — please try another name or ticker.")

    st.stop()


options = [f"{row.ticker} — {row.company_name}" for row in matches.itertuples()]

selected = st.selectbox("Select Company", options)


ticker = selected.split(" — ")[0]


# ==========================================================
# Company heading
# ==========================================================

company_name = companies.loc[companies["ticker"] == ticker, "company_name"].iloc[0]

st.divider()

st.subheader(f"📑 Annual Reports — {company_name}")

st.caption(f"NSE Ticker: {ticker}")


# ==========================================================
# Reports
# ==========================================================

reports = get_reports(ticker)


if reports.empty:

    st.info("No annual reports are available for this company.")

    st.stop()


# ==========================================================
# Display reports
# ==========================================================

st.write(f"**{len(reports)} report(s) found**")


for row in reports.itertuples(index=False):

    year = row.year
    url = row.annual_report

    col1, col2, col3 = st.columns([1.5, 4, 2])

    with col1:
        st.markdown(f"### {year}")

    with col2:

        if url and str(url).strip():

            clean_url = str(url).strip()

            if clean_url.startswith(("http://", "https://")):

                st.link_button("📄 Open BSE Annual Report", clean_url)

            else:

                st.markdown("🔴 **Report unavailable**")

        else:

            st.markdown("🔴 **Report unavailable**")

    with col3:

        if url and str(url).strip():

            available = check_report_url(url)

            if available:

                st.success("Available")

            else:

                st.error("Report unavailable")

        else:

            st.error("Report unavailable")

    st.divider()
