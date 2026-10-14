-- Vendor scorecard
SELECT
    v.vendor_name,
    v.vendor_type,
    COUNT(DISTINCT oi.order_id)     AS orders,
    SUM(oi.quantity)                AS units,
    SUM(oi.line_total)              AS gmv,
    COALESCE(SUM(vc.commission_amount),0) AS commission,
    SUM(CASE WHEN o.order_status='cancelled' THEN 1 ELSE 0 END) AS cancellations,
    SUM(CASE WHEN o.order_status='returned' THEN 1 ELSE 0 END) AS returns
FROM vendor_accounts v
LEFT JOIN order_items oi  ON oi.vendor_id = v.id
LEFT JOIN orders o        ON o.id = oi.order_id
LEFT JOIN vendor_commissions vc ON vc.order_item_id = oi.id
GROUP BY v.id, v.vendor_name, v.vendor_type
ORDER BY gmv DESC;