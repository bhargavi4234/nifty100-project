import streamlit as st


st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("Nifty 100 Analytics")

st.markdown(
    """
    ## Welcome

    Nifty 100 Analytics is a financial analytics dashboard
    covering company profiles, financial ratios, peer comparison,
    trends, sectors, capital allocation and reports.

    Use the **sidebar** to navigate through the dashboard screens.
    """
)

st.sidebar.title("Nifty 100 Analytics")

st.sidebar.markdown(
    """
    ### Dashboard

    Select a screen from the navigation menu.

    **8 Screens**
    - Home
    - Profile
    - Screener
    - Peers
    - Trends
    - Sectors
    - Capital
    - Reports
    """
)

st.sidebar.markdown("---")
st.sidebar.caption("Nifty 100 Analytics Platform")