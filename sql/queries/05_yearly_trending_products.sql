-- Year-over-year product trend
SELECT
    YEAR(o.ordered_at) AS yr,
    p.product_name,
    SUM(oi.quantity)   AS units,
    SUM(oi.line_total) AS gmv
FROM products p
JOIN order_items oi ON oi.product_id = p.id
JOIN orders o       ON o.id = oi.order_id
WHERE o.order_status NOT IN ('cancelled','failed')
GROUP BY yr, p.id, p.product_name
ORDER BY yr DESC, gmv DESC;