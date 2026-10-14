"""
reports.py — Deep-dive reports for Stylerizz.
Sections:
  1. Product performance (units, orders, GMV, net sales)
  2. Category / Fabric / Occasion mix
  3. Vendor scorecard
  4. Payment failures
  5. Coupon effectiveness
  6. Appointment conversion
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from db_connect import run_query


def _fmt_inr(x):
    try:
        return f"₹{float(x):,.0f}"
    except Exception:
        return "₹0"


def reports_page():
    st.title("📈 Reports")
    st.caption("Product, category, vendor, and payment deep-dives.")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🛍️ Products", "🧵 Categories/Fabrics/Occasions",
        "🏪 Vendors", "💳 Payments", "🎟️ Coupons", "📅 Appointments"
    ])

    # ============================================================
    # TAB 1 — PRODUCTS
    # ============================================================
    with tab1:
        st.subheader("Top Products by GMV")
        sql = """
            SELECT
                p.id,
                p.product_name,
                p.listing_type,
                SUM(oi.quantity)                AS units_sold,
                COUNT(DISTINCT oi.order_id)     AS orders,
                SUM(oi.line_total)              AS gmv,
                SUM(oi.line_total) -
                  COALESCE(SUM(r.refund_amount), 0) AS net_sales
            FROM products p
            JOIN order_items oi ON oi.product_id = p.id
            JOIN orders o       ON o.id = oi.order_id
            LEFT JOIN (
                SELECT order_id, SUM(refund_amount) AS refund_amount
                FROM refunds GROUP BY order_id
            ) r ON r.order_id = oi.order_id
            WHERE o.order_status NOT IN ('cancelled','failed')
            GROUP BY p.id, p.product_name, p.listing_type
            ORDER BY gmv DESC
            LIMIT 30
        """
        df = run_query(sql)
        if not df.empty:
            df["units_sold"] = df["units_sold"].astype(int)
            df["orders"] = df["orders"].astype(int)
            st.dataframe(
                df.style.format({
                    "gmv": _fmt_inr,
                    "net_sales": _fmt_inr,
                }),
                use_container_width=True, height=420,
            )
        else:
            st.info("No product data.")

        st.markdown("---")
        st.subheader("Platform-Owned vs Vendor-Listed")
        sql2 = """
            SELECT
                p.listing_type,
                COUNT(DISTINCT p.id)             AS products,
                SUM(oi.quantity)                 AS units,
                SUM(oi.line_total)               AS gmv,
                ROUND(AVG(oi.unit_price), 0)     AS avg_price
            FROM products p
            JOIN order_items oi ON oi.product_id = p.id
            JOIN orders o       ON o.id = oi.order_id
            WHERE o.order_status NOT IN ('cancelled','failed')
            GROUP BY p.listing_type
        """
        df2 = run_query(sql2)
        if not df2.empty:
            st.dataframe(
                df2.style.format({
                    "gmv": _fmt_inr,
                    "avg_price": _fmt_inr,
                }),
                use_container_width=True,
            )
            fig = px.bar(df2, x="listing_type", y="gmv",
                         color="listing_type", text="gmv")
            fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
            fig.update_layout(height=340, showlegend=False,
                              yaxis_tickformat=",.0f",
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 2 — CATEGORIES / FABRICS / OCCASIONS
    # ============================================================
    with tab2:
        colA, colB = st.columns(2)

        with colA:
            st.subheader("By Category")
            sql = """
                SELECT
                    c.category_name,
                    COUNT(DISTINCT oi.order_id) AS orders,
                    SUM(oi.quantity)            AS units,
                    SUM(oi.line_total)          AS gmv
                FROM order_items oi
                JOIN products p            ON p.id = oi.product_id
                JOIN product_categories pc ON pc.product_id = p.id AND pc.is_primary = 1
                JOIN categories c          ON c.id = pc.category_id
                JOIN orders o              ON o.id = oi.order_id
                WHERE o.order_status NOT IN ('cancelled','failed')
                GROUP BY c.category_name
                ORDER BY gmv DESC
            """
            df = run_query(sql)
            if not df.empty:
                st.dataframe(
                    df.style.format({"gmv": _fmt_inr}),
                    use_container_width=True, height=380,
                )

        with colB:
            st.subheader("By Fabric")
            sql = """
                SELECT
                    f.fabric_name,
                    COUNT(DISTINCT oi.order_id) AS orders,
                    SUM(oi.quantity)            AS units,
                    SUM(oi.line_total)          AS gmv
                FROM order_items oi
                JOIN products p        ON p.id = oi.product_id
                JOIN product_fabrics pf ON pf.product_id = p.id
                JOIN fabrics f         ON f.id = pf.fabric_id
                JOIN orders o          ON o.id = oi.order_id
                WHERE o.order_status NOT IN ('cancelled','failed')
                GROUP BY f.fabric_name
                ORDER BY gmv DESC
            """
            df = run_query(sql)
            if not df.empty:
                st.dataframe(
                    df.style.format({"gmv": _fmt_inr}),
                    use_container_width=True, height=380,
                )

        st.markdown("---")
        st.subheader("By Occasion")
        sql = """
            SELECT
                oc.occasion_name,
                oc.season_tag,
                COUNT(DISTINCT oi.order_id) AS orders,
                SUM(oi.quantity)            AS units,
                SUM(oi.line_total)          AS gmv
            FROM order_items oi
            JOIN products p          ON p.id = oi.product_id
            JOIN product_occasions po ON po.product_id = p.id
            JOIN occasions oc        ON oc.id = po.occasion_id
            JOIN orders o            ON o.id = oi.order_id
            WHERE o.order_status NOT IN ('cancelled','failed')
            GROUP BY oc.occasion_name, oc.season_tag
            ORDER BY gmv DESC
        """
        df = run_query(sql)
        if not df.empty:
            fig = px.bar(df, x="occasion_name", y="gmv",
                         color="season_tag", text="gmv")
            fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
            fig.update_layout(height=420, yaxis_tickformat=",.0f",
                              margin=dict(l=10, r=10, t=20, b=10),
                              xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 3 — VENDORS
    # ============================================================
    with tab3:
        st.subheader("Vendor Scorecard")
        sql = """
            SELECT
                v.id,
                v.vendor_name,
                v.vendor_type,
                COUNT(DISTINCT oi.order_id)      AS orders,
                SUM(oi.quantity)                 AS units,
                SUM(oi.line_total)               AS gmv,
                ROUND(AVG(oi.unit_price), 0)     AS avg_price,
                COALESCE(SUM(vc.commission_amount), 0) AS commission,
                SUM(CASE WHEN o.order_status='cancelled' THEN 1 ELSE 0 END) AS cancellations,
                SUM(CASE WHEN o.order_status='returned' THEN 1 ELSE 0 END) AS returns
            FROM vendor_accounts v
            LEFT JOIN order_items oi  ON oi.vendor_id = v.id
            LEFT JOIN orders o        ON o.id = oi.order_id
            LEFT JOIN vendor_commissions vc ON vc.order_item_id = oi.id
            GROUP BY v.id, v.vendor_name, v.vendor_type
            ORDER BY gmv DESC
        """
        df = run_query(sql)
        if not df.empty:
            st.dataframe(
                df.style.format({
                    "gmv": _fmt_inr,
                    "commission": _fmt_inr,
                    "avg_price": _fmt_inr,
                }),
                use_container_width=True, height=440,
            )
            fig = px.bar(df.head(10), x="vendor_name", y="gmv",
                         color="vendor_type", text="gmv")
            fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
            fig.update_layout(height=400, yaxis_tickformat=",.0f",
                              xaxis_tickangle=-30,
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 4 — PAYMENTS
    # ============================================================
    with tab4:
        colA, colB = st.columns(2)

        with colA:
            st.subheader("Success Rate by Method")
            sql = """
                SELECT
                    pa.payment_method,
                    COUNT(*) AS attempts,
                    SUM(CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END) AS successes,
                    ROUND(100.0 * SUM(CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END) /
                          COUNT(*), 2) AS success_rate
                FROM payment_attempts pa
                LEFT JOIN payments p ON p.payment_attempt_id = pa.id
                GROUP BY pa.payment_method
                ORDER BY attempts DESC
            """
            df = run_query(sql)
            if not df.empty:
                st.dataframe(df, use_container_width=True, height=380)
                fig = px.bar(df, x="payment_method", y="success_rate",
                             text="success_rate")
                fig.update_traces(texttemplate="%{text:.1f}%",
                                  textposition="outside",
                                  marker_color="#4ECDC4")
                fig.update_layout(height=340, yaxis_range=[0,110],
                                  margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig, use_container_width=True)

        with colB:
            st.subheader("Top Failure Reasons")
            sql = """
                SELECT
                    failure_reason,
                    COUNT(*) AS failures
                FROM payment_attempts
                WHERE failure_reason IS NOT NULL
                GROUP BY failure_reason
                ORDER BY failures DESC
            """
            df = run_query(sql)
            if not df.empty:
                st.dataframe(df, use_container_width=True, height=380)
                fig = px.pie(df, names="failure_reason", values="failures",
                             hole=0.4)
                fig.update_layout(height=340,
                                  margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 5 — COUPONS
    # ============================================================
    with tab5:
        st.subheader("Coupon Effectiveness")
        sql = """
            SELECT
                coupon_code,
                discount_type,
                discount_value,
                minimum_order_value,
                maximum_discount,
                status,
                valid_from,
                valid_to
            FROM coupons
            ORDER BY valid_from DESC
        """
        df = run_query(sql)
        if not df.empty:
            st.dataframe(df, use_container_width=True, height=340)
        else:
            st.info(
                "ℹ️ Coupon data is empty — the seed script didn't populate the "
                "`coupons` table. To add coupon data, insert sample rows into "
                "`coupons`, `orders.coupon_code` etc."
            )

    # ============================================================
    # TAB 6 — APPOINTMENTS
    # ============================================================
    with tab6:
        st.subheader("Designer / Stylist Appointments")
        sql = """
            SELECT
                appointment_status,
                COUNT(*)                                        AS appointments,
                SUM(CASE WHEN linked_order_id IS NOT NULL
                         THEN 1 ELSE 0 END)                     AS converted,
                ROUND(100.0 * SUM(CASE WHEN linked_order_id IS NOT NULL
                                       THEN 1 ELSE 0 END) /
                      COUNT(*), 2)                              AS conversion_rate,
                ROUND(AVG(appointment_fee), 0)                  AS avg_fee
            FROM designer_appointments
            GROUP BY appointment_status
        """
        df = run_query(sql)
        if not df.empty:
            st.dataframe(
                df.style.format({"avg_fee": _fmt_inr}),
                use_container_width=True, height=280,
            )
            fig = px.bar(df, x="appointment_status", y="appointments",
                         color="appointment_status", text="appointments")
            fig.update_traces(textposition="outside")
            fig.update_layout(height=340, showlegend=False,
                              margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No appointment data.")