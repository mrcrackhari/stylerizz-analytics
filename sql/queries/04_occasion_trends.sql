-- Sales by occasion and season tag
SELECT
    oc.occasion_name,
    oc.season_tag,
    COUNT(DISTINCT oi.order_id) AS orders,
    SUM(oi.quantity)            AS units,
    SUM(oi.line_total)          AS gmv
FROM order_items oi
JOIN products p           ON p.id = oi.product_id
JOIN product_occasions po ON po.product_id = p.id
JOIN occasions oc         ON oc.id = po.occasion_id
JOIN orders o             ON o.id = oi.order_id
WHERE o.order_status NOT IN ('cancelled','failed')
GROUP BY oc.id, oc.occasion_name, oc.season_tag
ORDER BY gmv DESC;