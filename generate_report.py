"""
generate_report.py — Export analytics reports as CSV or Excel.
"""
import io
from datetime import datetime

import streamlit as st
import pandas as pd
from db_connect import run_query


REPORTS = {
    "Top Products by GMV": """
        SELECT p.product_name, p.listing_type,
               SUM(oi.quantity)            AS units_sold,
               COUNT(DISTINCT oi.order_id) AS orders,
               SUM(oi.line_total)          AS gmv
        FROM products p
        JOIN order_items oi ON oi.product_id = p.id
        JOIN orders o       ON o.id = oi.order_id
        WHERE o.order_status NOT IN ('cancelled','failed')
        GROUP BY p.id, p.product_name, p.listing_type
        ORDER BY gmv DESC
    """,
    "Category Performance": """
        SELECT c.category_name,
               COUNT(DISTINCT oi.order_id) AS orders,
               SUM(oi.quantity)            AS units,
               SUM(oi.line_total)          AS gmv
        FROM order_items oi
        JOIN products p            ON p.id = oi.product_id
        JOIN product_categories pc ON pc.product_id = p.id AND pc.is_primary=1
        JOIN categories c          ON c.id = pc.category_id
        JOIN orders o              ON o.id = oi.order_id
        WHERE o.order_status NOT IN ('cancelled','failed')
        GROUP BY c.category_name
        ORDER BY gmv DESC
    """,
    "Vendor Scorecard": """
        SELECT v.vendor_name, v.vendor_type,
               COUNT(DISTINCT oi.order_id) AS orders,
               SUM(oi.quantity)            AS units,
               SUM(oi.line_total)          AS gmv,
               COALESCE(SUM(vc.commission_amount),0) AS commission
        FROM vendor_accounts v
        LEFT JOIN order_items oi  ON oi.vendor_id = v.id
        LEFT JOIN orders o        ON o.id = oi.order_id
        LEFT JOIN vendor_commissions vc ON vc.order_item_id = oi.id
        GROUP BY v.id, v.vendor_name, v.vendor_type
        ORDER BY gmv DESC
    """,
    "Monthly GMV": """
        SELECT DATE_FORMAT(ordered_at, '%Y-%m') AS month,
               COUNT(*) AS orders,
               SUM(grand_total) AS gmv
        FROM orders
        WHERE order_status NOT IN ('cancelled','failed')
        GROUP BY month
        ORDER BY month
    """,
    "Payment Success by Method": """
        SELECT pa.payment_method,
               COUNT(*) AS attempts,
               SUM(CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END) AS successes,
               ROUND(100.0 * SUM(CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END) /
                     COUNT(*), 2) AS success_rate
        FROM payment_attempts pa
        LEFT JOIN payments p ON p.payment_attempt_id = pa.id
        GROUP BY pa.payment_method
        ORDER BY attempts DESC
    """,
    "Refunds Detail": """
        SELECT r.id, o.order_number, r.refund_amount, r.reason,
               r.processed_at, o.grand_total
        FROM refunds r
        JOIN orders o ON o.id = r.order_id
        ORDER BY r.processed_at DESC
    """,
    "Appointment Conversion": """
        SELECT appointment_status,
               COUNT(*) AS appointments,
               SUM(CASE WHEN linked_order_id IS NOT NULL THEN 1 ELSE 0 END) AS converted
        FROM designer_appointments
        GROUP BY appointment_status
    """,
    "Repeat Purchase Rate": """
        SELECT customer_id, COUNT(*) AS order_count
        FROM orders
        WHERE order_status NOT IN ('cancelled','failed')
        GROUP BY customer_id
        ORDER BY order_count DESC
    """,
    "Product Views Summary": """
        SELECT p.product_name,
               COUNT(pv.id) AS views,
               ROUND(AVG(pv.duration_seconds),1) AS avg_seconds
        FROM products p
        LEFT JOIN product_views pv ON pv.product_id = p.id
        GROUP BY p.id, p.product_name
        ORDER BY views DESC
    """,
    "Cart Abandonment": """
        SELECT cart_status, COUNT(*) AS carts
        FROM carts
        GROUP BY cart_status
    """,
    "Order Status Distribution": """
        SELECT order_status, COUNT(*) AS orders, SUM(grand_total) AS gmv
        FROM orders
        GROUP BY order_status
    """,
    "Customer Cohort Sizes": """
        SELECT DATE_FORMAT(customer_since, '%Y-%m') AS cohort,
               COUNT(*) AS customers
        FROM customer_profiles
        GROUP BY cohort
        ORDER BY cohort
    """,
}


def generate_report_page():
    st.title("📄 Generate Report")
    st.caption("Pick a report, preview the data, and download as CSV or Excel.")

    report_name = st.selectbox("Choose a report", list(REPORTS.keys()))
    sql = REPORTS[report_name]

    with st.spinner("Running query..."):
        df = run_query(sql)

    if df.empty:
        st.warning("No data returned.")
        return

    st.success(f"✅ {len(df):,} rows returned.")
    st.dataframe(df, use_container_width=True, height=400)

    st.markdown("---")
    col1, col2 = st.columns(2)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    safe_name = report_name.lower().replace(" ", "_")

    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name=f"{safe_name}_{ts}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Report")
        xlsx = buf.getvalue()
        st.download_button(
            "⬇️ Download Excel",
            data=xlsx,
            file_name=f"{safe_name}_{ts}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )