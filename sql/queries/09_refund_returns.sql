-- Refunds and returns by reason
SELECT
    reason,
    COUNT(*) AS refunds,
    SUM(refund_amount) AS total_refunded,
    ROUND(AVG(refund_amount), 0) AS avg_refund
FROM refunds
GROUP BY reason
ORDER BY total_refunded DESC;