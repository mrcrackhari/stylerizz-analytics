-- Sales by fabric
SELECT
    f.fabric_name,
    f.fabric_group,
    COUNT(DISTINCT oi.order_id) AS orders,
    SUM(oi.quantity)            AS units,
    SUM(oi.line_total)          AS gmv
FROM order_items oi
JOIN products p         ON p.id = oi.product_id
JOIN product_fabrics pf ON pf.product_id = p.id
JOIN fabrics f          ON f.id = pf.fabric_id
JOIN orders o           ON o.id = oi.order_id
WHERE o.order_status NOT IN ('cancelled','failed')
GROUP BY f.id, f.fabric_name, f.fabric_group
ORDER BY gmv DESC;