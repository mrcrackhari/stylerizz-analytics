"""
dashboard.py — Executive Overview for Stylerizz.
KPIs: orders, GMV, AOV, discounts, monthly trend, payment success, category mix.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from db_connect import run_query


def dashboard_page():
    st.title("📊 Executive Overview")
    st.caption("KPIs from Stylerizz orders, payments, and product data.")

    # ---------- KPI Cards ----------
    kpi_sql = """
        SELECT
            COUNT(DISTINCT o.id)                                  AS orders,
            COALESCE(SUM(o.grand_total), 0)                       AS gmv,
            COALESCE(AVG(o.grand_total), 0)                       AS aov,
            COALESCE(SUM(o.discount_amount), 0)                   AS discount_total,
            (SELECT COUNT(*) FROM customer_profiles WHERE status='active') AS customers,
            (SELECT COUNT(*) FROM refunds)                        AS refunds,
            (SELECT COUNT(*) FROM orders WHERE order_status='cancelled') AS cancelled
        FROM orders o
        WHERE o.order_status NOT IN ('cancelled','failed')
    """
    df = run_query(kpi_sql)
    if df.empty or int(df.iloc[0]["orders"]) == 0:
        st.warning(
            "⚠️ No orders found yet. Run `python sql/03_seed_data.py` "
            "and refresh."
        )
        return

    row = df.iloc[0]
    orders = int(row["orders"])
    gmv = float(row["gmv"])
    aov = float(row["aov"])
    disc = float(row["discount_total"])
    cust = int(row["customers"])
    refunds = int(row["refunds"])
    cancelled = int(row["cancelled"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Orders", f"{orders:,}")
    c2.metric("💰 GMV", f"₹{gmv:,.0f}")
    c3.metric("🛒 AOV", f"₹{aov:,.0f}")
    c4.metric("🎁 Discounts", f"₹{disc:,.0f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("👥 Customers", f"{cust:,}")
    c6.metric("🔄 Refunds", f"{refunds:,}")
    c7.metric("❌ Cancelled", f"{cancelled:,}")
    c8.metric(
        "📉 Return Rate",
        f"{(100 * refunds / max(orders, 1)):.1f}%"
    )

    st.markdown("---")

    # ---------- Monthly GMV Trend ----------
    st.subheader("📈 Monthly GMV Trend")
    trend_sql = """
        SELECT
            DATE_FORMAT(o.ordered_at, '%Y-%m') AS month,
            COUNT(*)                           AS orders,
            SUM(o.grand_total)                 AS gmv
        FROM orders o
        WHERE o.order_status NOT IN ('cancelled','failed')
        GROUP BY month
        ORDER BY month
    """
    tdf = run_query(trend_sql)
    if not tdf.empty:
        # Make sure columns are named right
        tdf["month"] = tdf["month"].astype(str)
        tdf["gmv"] = pd.to_numeric(tdf["gmv"], errors="coerce").fillna(0)

        fig = px.line(
            tdf,
            x="month",
            y="gmv",
            markers=True,
            labels={"month": "Month", "gmv": "GMV (₹)"},
        )
        fig.update_traces(line_color="#FF6B6B", line_width=3, marker_size=8)
        fig.update_layout(
            height=380,
            margin=dict(l=10, r=10, t=30, b=10),
            yaxis_tickformat=",.0f",
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Raw monthly data"):
            st.dataframe(tdf, use_container_width=True)
    else:
        st.info("No monthly trend data yet.")

    st.markdown("---")

    # ---------- Category mix ----------
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🧵 GMV by Category")
        cat_sql = """
            SELECT
                c.category_name,
                SUM(oi.line_total) AS gmv
            FROM order_items oi
            JOIN products p       ON p.id = oi.product_id
            JOIN product_categories pc ON pc.product_id = p.id AND pc.is_primary = 1
            JOIN categories c     ON c.id = pc.category_id
            JOIN orders o         ON o.id = oi.order_id
            WHERE o.order_status NOT IN ('cancelled','failed')
            GROUP BY c.category_name
            ORDER BY gmv DESC
            LIMIT 10
        """
        cdf = run_query(cat_sql)
        if not cdf.empty:
            fig2 = px.pie(
                cdf,
                names="category_name",
                values="gmv",
                hole=0.4,
            )
            fig2.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No category data.")

    with col_b:
        st.subheader("💳 Payment Method Split")
        pay_sql = """
            SELECT
                pa.payment_method,
                COUNT(*) AS attempts
            FROM payment_attempts pa
            GROUP BY pa.payment_method
            ORDER BY attempts DESC
        """
        pdf = run_query(pay_sql)
        if not pdf.empty:
            fig3 = px.bar(
                pdf,
                x="payment_method",
                y="attempts",
                labels={"payment_method": "", "attempts": "Attempts"},
            )
            fig3.update_traces(marker_color="#4ECDC4")
            fig3.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No payment data.")

    st.markdown("---")

    # ---------- Top products & vendors ----------
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("🏆 Top 10 Products by GMV")
        prod_sql = """
            SELECT
                p.product_name,
                SUM(oi.line_total) AS gmv,
                SUM(oi.quantity)   AS units
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            JOIN orders o   ON o.id = oi.order_id
            WHERE o.order_status NOT IN ('cancelled','failed')
            GROUP BY p.product_name
            ORDER BY gmv DESC
            LIMIT 10
        """
        prdf = run_query(prod_sql)
        if not prdf.empty:
            prdf["gmv"] = pd.to_numeric(prdf["gmv"], errors="coerce").fillna(0)
            st.dataframe(
                prdf.style.format({"gmv": "₹{:,.0f}"}),
                use_container_width=True,
                height=320,
            )

    with col_d:
        st.subheader("🏪 Top 10 Vendors by GMV")
        vend_sql = """
            SELECT
                v.vendor_name,
                COUNT(DISTINCT oi.order_id) AS orders,
                SUM(oi.line_total)          AS gmv
            FROM order_items oi
            JOIN vendor_accounts v ON v.id = oi.vendor_id
            JOIN orders o          ON o.id = oi.order_id
            WHERE o.order_status NOT IN ('cancelled','failed')
            GROUP BY v.vendor_name
            ORDER BY gmv DESC
            LIMIT 10
        """
        vdf = run_query(vend_sql)
        if not vdf.empty:
            vdf["gmv"] = pd.to_numeric(vdf["gmv"], errors="coerce").fillna(0)
            st.dataframe(
                vdf.style.format({"gmv": "₹{:,.0f}"}),
                use_container_width=True,
                height=320,
            )

    st.markdown("---")
    st.caption(
        "ℹ️ GMV excludes cancelled & failed orders. "
        "Synthetic data for portfolio demonstration."
    )