-- Top products by GMV, net sales, orders, units
SELECT
    p.product_name,
    p.listing_type,
    COUNT(DISTINCT oi.order_id) AS orders,
    SUM(oi.quantity)            AS units,
    SUM(oi.line_total)          AS gmv,
    SUM(oi.line_total) - COALESCE(SUM(r.refund_amount),0) AS net_sales
FROM products p
JOIN order_items oi ON oi.product_id = p.id
JOIN orders o       ON o.id = oi.order_id
LEFT JOIN (SELECT order_id, SUM(refund_amount) refund_amount FROM refunds GROUP BY order_id) r
       ON r.order_id = oi.order_id
WHERE o.order_status NOT IN ('cancelled','failed')
GROUP BY p.id, p.product_name, p.listing_type
ORDER BY gmv DESC;