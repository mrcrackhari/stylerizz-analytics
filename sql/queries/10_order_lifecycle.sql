-- Order status distribution and durations
SELECT
    order_status,
    COUNT(*) AS orders,
    ROUND(AVG(grand_total), 0) AS avg_value,
    ROUND(AVG(DATEDIFF(CURDATE(), ordered_at)), 1) AS avg_days_old
FROM orders
GROUP BY order_status
ORDER BY orders DESC;