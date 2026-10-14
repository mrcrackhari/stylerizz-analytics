"""
app.py — Main Streamlit entry point for Stylerizz Analytics.
"""
import streamlit as st

from login import login_page
from dashboard import dashboard_page
from reports import reports_page
from analysis import analysis_page
from powerbi import powerbi_page
from generate_report import generate_report_page

st.set_page_config(
    page_title="Stylerizz Fashion Analytics",
    page_icon="🛍️",
    layout="wide",
)

# ---------- Auth gate ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ---------- Sidebar ----------
st.sidebar.title("🛍️ STYLERIZZ")
st.sidebar.caption("Fashion E-Commerce & Marketplace Analytics")
st.sidebar.markdown("---")

PAGES = {
    "📊 Dashboard": dashboard_page,
    "📈 Reports": reports_page,
    "🔍 Analysis": analysis_page,
    "📄 Generate Report": generate_report_page,
    "📉 Power BI": powerbi_page,
}

page = st.sidebar.radio("🧭 Navigation", list(PAGES.keys()))

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# ---------- Route ----------
PAGES[page]()