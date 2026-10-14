-- Orphan FKs, negative amounts, invalid dates
SELECT 'orphan_orders_customer' AS check_name,
       COUNT(*) AS failed
FROM orders o LEFT JOIN customer_profiles cp ON cp.id = o.customer_id
WHERE cp.id IS NULL
UNION ALL
SELECT 'orphan_items_product', COUNT(*)
FROM order_items oi LEFT JOIN products p ON p.id = oi.product_id
WHERE p.id IS NULL
UNION ALL
SELECT 'negative_order_total', COUNT(*)
FROM orders WHERE grand_total < 0
UNION ALL
SELECT 'negative_refund', COUNT(*)
FROM refunds WHERE refund_amount < 0
UNION ALL
SELECT 'duplicate_order_numbers',
       COUNT(*) - COUNT(DISTINCT order_number) FROM orders;