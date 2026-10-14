"""
analysis.py — Strategic analysis for Stylerizz.
Sections:
  1. Customer funnel (session → view → click → cart → order)
  2. Monthly retention / cohort
  3. RFM segmentation
  4. Order lifecycle times
  5. Rising views + weak conversion (opportunity detection)
  6. Data quality report
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from db_connect import run_query


def analysis_page():
    st.title("🔍 Analysis")
    st.caption("Funnel, cohorts, RFM, delays, and data quality.")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔻 Funnel", "📅 Cohorts", "🎯 RFM",
        "⏱️ Delays", "🔥 Rising Views",
        "✅ Data Quality"
    ])

    # ============================================================
    # TAB 1 — FUNNEL
    # ============================================================
    with tab1:
        st.subheader("Customer Purchase Funnel")
        sql = """
            SELECT 'Sessions'       AS stage, COUNT(*) AS count FROM browsing_sessions
            UNION ALL SELECT 'Product Views',  COUNT(*) FROM product_views
            UNION ALL SELECT 'Product Clicks', COUNT(*) FROM product_clicks
            UNION ALL SELECT 'Favorites',      COUNT(*) FROM favorite_items
            UNION ALL SELECT 'Cart Adds',      COUNT(*) FROM cart_items
            UNION ALL SELECT 'Orders',         COUNT(*) FROM orders
        """
        df = run_query(sql)
        if not df.empty:
            df["stage"] = pd.Categorical(
                df["stage"],
                categories=["Sessions", "Product Views", "Product Clicks",
                            "Favorites", "Cart Adds", "Orders"],
                ordered=True,
            )
            df = df.sort_values("stage")
            df["pct_of_sessions"] = (100.0 * df["count"] / df["count"].max()).round(1)

            fig = px.funnel(df, x="count", y="stage", text="pct_of_sessions")
            fig.update_traces(texttemplate="%{text}% of sessions")
            fig.update_layout(height=440, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True, height=280)

    # ============================================================
    # TAB 2 — COHORTS
    # ============================================================
    with tab2:
        st.subheader("Monthly Customer Retention")
        sql = """
            SELECT
                DATE_FORMAT(cp.customer_since, '%%Y-%%m') AS cohort_month,
                COUNT(DISTINCT cp.id)                     AS cohort_size
            FROM customer_profiles cp
            WHERE cp.customer_since IS NOT NULL
            GROUP BY cohort_month
            ORDER BY cohort_month
        """
        df = run_query(sql)
        if not df.empty:
            fig = px.bar(df, x="cohort_month", y="cohort_size",
                         text="cohort_size")
            fig.update_traces(textposition="outside",
                              marker_color="#FF6B6B")
            fig.update_layout(height=400,
                              margin=dict(l=10, r=10, t=20, b=10),
                              xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Repeat Purchase Rate")
        sql2 = """
            SELECT
                CASE
                    WHEN order_count = 1 THEN '1 order'
                    WHEN order_count BETWEEN 2 AND 3 THEN '2-3 orders'
                    WHEN order_count BETWEEN 4 AND 6 THEN '4-6 orders'
                    ELSE '7+ orders'
                END AS bucket,
                COUNT(*) AS customers
            FROM (
                SELECT customer_id, COUNT(*) AS order_count
                FROM orders
                WHERE order_status NOT IN ('cancelled','failed')
                GROUP BY customer_id
            ) t
            GROUP BY bucket
            ORDER BY bucket
        """
        df2 = run_query(sql2)
        if not df2.empty:
            fig = px.pie(df2, names="bucket", values="customers",
                         hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=380,
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 3 — RFM
    # ============================================================
    with tab3:
        st.subheader("RFM Segmentation")
        st.caption(
            "Recency · Frequency · Monetary. Customers scored 1-5 on each axis."
        )
        sql = """
            SELECT
                cp.id AS customer_id,
                cp.user_id,
                DATEDIFF(CURDATE(), MAX(o.ordered_at)) AS recency_days,
                COUNT(DISTINCT o.id)                    AS frequency,
                SUM(o.grand_total)                      AS monetary
            FROM customer_profiles cp
            LEFT JOIN orders o ON o.customer_id = cp.id
                AND o.order_status NOT IN ('cancelled','failed')
            GROUP BY cp.id, cp.user_id
            HAVING frequency > 0
        """
        df = run_query(sql)
        if not df.empty:
            df["R"] = pd.qcut(df["recency_days"], 5, labels=[5,4,3,2,1],
                              duplicates="drop").astype(int)
            df["F"] = pd.qcut(df["frequency"].rank(method="first"),
                              5, labels=[1,2,3,4,5]).astype(int)
            df["M"] = pd.qcut(df["monetary"].rank(method="first"),
                              5, labels=[1,2,3,4,5]).astype(int)

            def segment(row):
                r, f, m = row["R"], row["F"], row["M"]
                if r >= 4 and f >= 4 and m >= 4:
                    return "🏆 Champion"
                if r >= 4 and f >= 3:
                    return "💚 Loyal"
                if r >= 3 and f >= 2:
                    return "🌱 Potential Loyalist"
                if r >= 4 and f == 1:
                    return "🆕 New Customer"
                if r <= 2 and f >= 3:
                    return "⚠️ At Risk"
                if r <= 2 and f <= 2:
                    return "❌ Lost"
                return "Other"

            df["segment"] = df.apply(segment, axis=1)
            summary = (
                df.groupby("segment")
                .agg(customers=("customer_id","count"),
                     avg_recency=("recency_days","mean"),
                     avg_frequency=("frequency","mean"),
                     avg_monetary=("monetary","mean"))
                .reset_index()
                .sort_values("customers", ascending=False)
            )
            summary["avg_recency"] = summary["avg_recency"].round(0).astype(int)
            summary["avg_frequency"] = summary["avg_frequency"].round(1)
            summary["avg_monetary"] = summary["avg_monetary"].round(0)

            st.dataframe(
                summary.style.format({"avg_monetary": "₹{:,.0f}"}),
                use_container_width=True, height=340,
            )

            fig = px.bar(summary, x="segment", y="customers",
                         color="segment", text="customers")
            fig.update_traces(textposition="outside")
            fig.update_layout(height=380, showlegend=False,
                              xaxis_tickangle=-30,
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough order data to compute RFM.")

    # ============================================================
    # TAB 4 — DELAYS
    # ============================================================
    with tab4:
        st.subheader("Order Lifecycle Times")
        st.caption(
            "Business rule: order placed → dispatched → delivered. "
            "Since the seed data doesn't populate `order_status_history` "
            "with these transitions, we approximate using order date."
        )
        sql = """
            SELECT
                order_status,
                COUNT(*)                          AS orders,
                ROUND(AVG(grand_total), 0)        AS avg_value,
                ROUND(AVG(DATEDIFF(CURDATE(), ordered_at)), 1) AS avg_days_since
            FROM orders
            GROUP BY order_status
            ORDER BY orders DESC
        """
        df = run_query(sql)
        if not df.empty:
            st.dataframe(
                df.style.format({
                    "avg_value": "₹{:,.0f}",
                }),
                use_container_width=True, height=280,
            )
            fig = px.bar(df, x="order_status", y="orders",
                         color="order_status", text="orders")
            fig.update_traces(textposition="outside")
            fig.update_layout(height=340, showlegend=False,
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 5 — RISING VIEWS (opportunity)
    # ============================================================
    with tab5:
        st.subheader("🔥 Products: High Views, Low Conversion")
        st.caption(
            "Opportunity list — products with strong views but weak purchase "
            "conversion. Investigate pricing, images, stock availability."
        )
        sql = """
            SELECT
                p.product_name,
                p.listing_type,
                COUNT(DISTINCT pv.id)                  AS views,
                COUNT(DISTINCT pc.id)                  AS clicks,
                COALESCE(SUM(oi.quantity), 0)          AS units_sold,
                ROUND(
                    COALESCE(SUM(oi.quantity), 0) * 100.0 /
                    NULLIF(COUNT(DISTINCT pv.id), 0),
                2)                                     AS conversion_pct
            FROM products p
            LEFT JOIN product_views pv  ON pv.product_id = p.id
            LEFT JOIN product_clicks pc ON pc.product_id = p.id
            LEFT JOIN order_items oi    ON oi.product_id = p.id
            GROUP BY p.id, p.product_name, p.listing_type
            HAVING views > 30
            ORDER BY views DESC, conversion_pct ASC
            LIMIT 20
        """
        df = run_query(sql)
        if not df.empty:
            df["views"] = df["views"].astype(int)
            df["clicks"] = df["clicks"].astype(int)
            df["units_sold"] = df["units_sold"].astype(int)
            st.dataframe(df, use_container_width=True, height=460)

    # ============================================================
    # TAB 6 — DATA QUALITY
    # ============================================================
    with tab6:
        st.subheader("✅ Data Quality Checks")
        checks = []

        # Orphan FKs
        checks.append(("Orphan orders → customer", """
            SELECT COUNT(*) FROM orders o
            LEFT JOIN customer_profiles cp ON cp.id = o.customer_id
            WHERE cp.id IS NULL
        """))
        checks.append(("Orphan order_items → product", """
            SELECT COUNT(*) FROM order_items oi
            LEFT JOIN products p ON p.id = oi.product_id
            WHERE p.id IS NULL
        """))
        checks.append(("Orphan payments → order", """
            SELECT COUNT(*) FROM payments p
            LEFT JOIN orders o ON o.id = p.order_id
            WHERE o.id IS NULL
        """))

        # Negative amounts
        checks.append(("Negative order grand_total", """
            SELECT COUNT(*) FROM orders WHERE grand_total < 0
        """))
        checks.append(("Negative payment amount", """
            SELECT COUNT(*) FROM payments WHERE paid_amount < 0
        """))
        checks.append(("Negative refund amount", """
            SELECT COUNT(*) FROM refunds WHERE refund_amount < 0
        """))

        # Duplicates
        checks.append(("Duplicate order_number", """
            SELECT COUNT(*) - COUNT(DISTINCT order_number) FROM orders
        """))
        checks.append(("Duplicate session_key", """
            SELECT COUNT(*) - COUNT(DISTINCT session_key) FROM browsing_sessions
        """))

        # Invalid dates
        checks.append(("Orders before customer_since", """
            SELECT COUNT(*) FROM orders o
            JOIN customer_profiles cp ON cp.id = o.customer_id
            WHERE o.ordered_at < cp.customer_since
        """))

        rows = []
        for name, q in checks:
            try:
                df = run_query(q)
                failed = int(df.iloc[0, 0]) if not df.empty else 0
                rows.append({
                    "check": name,
                    "failed": failed,
                    "status": "✅ PASS" if failed == 0 else "⚠️ FAIL",
                })
            except Exception as e:
                rows.append({"check": name, "failed": -1, "status": f"❌ {e}"})

        qdf = pd.DataFrame(rows)
        st.dataframe(qdf, use_container_width=True, height=400)

        total_pass = (qdf["status"] == "✅ PASS").sum()
        st.success(f"**{total_pass}/{len(qdf)} checks passed**")