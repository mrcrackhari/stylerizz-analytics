-- GMV by category over time
SELECT
    DATE_FORMAT(o.ordered_at, '%Y-%m') AS month,
    c.category_name,
    SUM(oi.line_total) AS gmv
FROM order_items oi
JOIN products p            ON p.id = oi.product_id
JOIN product_categories pc ON pc.product_id = p.id AND pc.is_primary = 1
JOIN categories c          ON c.id = pc.category_id
JOIN orders o              ON o.id = oi.order_id
WHERE o.order_status NOT IN ('cancelled','failed')
GROUP BY month, c.category_name
ORDER BY month, gmv DESC;