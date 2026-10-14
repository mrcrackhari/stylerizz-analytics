"""
login.py — Simple login gate for Stylerizz Analytics.
Portfolio demo only. Replace with real hashed auth in production.
"""
import streamlit as st


def login_page():
    st.title("🛍️ Stylerizz Fashion Analytics")
    st.caption("Fashion E-Commerce & Multi-Vendor Marketplace")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🔐 Sign in")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            # Demo credentials — replace with real DB auth for production
            if username == "admin" and password == "stylerizz":
                st.session_state.logged_in = True
                st.success("✅ Welcome, admin!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Try admin / stylerizz")

        st.info("**Demo credentials** → username: `admin` · password: `stylerizz`")