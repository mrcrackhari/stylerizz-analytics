"""
powerbi.py — Embed a published Power BI report.
Publish your report to Power BI Service → File → Embed report →
Publish to web (public) → copy the iframe src URL → paste below.
"""
import streamlit as st


def powerbi_page():
    st.title("📉 Power BI Dashboard")

    st.markdown(
        """
        ### How to embed your Power BI report

        1. Build the report in **Power BI Desktop** (connect via
           `MySQL Database` connector using `127.0.0.1:3306`).
        2. **Publish** to Power BI Service.
        3. In Power BI Service: **File → Embed report → Publish to web**.
        4. Copy the **iframe src URL** (starts with
           `https://app.powerbi.com/view?r=...`).
        5. Paste it in the code below and save.
        """
    )

    st.markdown("---")
    st.subheader("📊 Embedded report")

    POWERBI_URL = ""  # <-- paste your embed URL here

    if POWERBI_URL:
        st.components.v1.iframe(POWERBI_URL, height=800, scrolling=True)
    else:
        st.info(
            "🔗 **No URL configured yet.** "
            "Paste your Power BI embed URL into the `POWERBI_URL` variable "
            "in `powerbi.py` to display the report here."
        )
        st.markdown("### Suggested dashboard pages")
        st.markdown(
            """
            **Page 1 — Executive Overview**
            - GMV, orders, AOV, net sales, return rate cards
            - Monthly GMV trend line
            - Category doughnut

            **Page 2 — Products & Categories**
            - Top 20 products by GMV
            - Fabric / occasion mix
            - Price band analysis

            **Page 3 — Customer Funnel**
            - Sessions → views → clicks → cart → order
            - Drop-off percentages

            **Page 4 — Vendors**
            - Vendor ranking table
            - Commission breakdown
            - Fulfillment time by vendor

            **Page 5 — Payments & Promotions**
            - Success rate by method
            - Failure reason breakdown
            - Coupon effectiveness

            **Page 6 — Dispatches & Returns**
            - Order lifecycle duration
            - Return reasons
            - Delayed shipment heatmap
            """
        )