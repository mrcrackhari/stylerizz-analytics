-- Payment success rate by method + failure reasons
SELECT
    pa.payment_method,
    COUNT(*) AS attempts,
    SUM(CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END) AS successes,
    ROUND(100.0 * SUM(CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
    GROUP_CONCAT(DISTINCT pa.failure_reason SEPARATOR '; ') AS top_failures
FROM payment_attempts pa
LEFT JOIN payments p ON p.payment_attempt_id = pa.id
GROUP BY pa.payment_method
ORDER BY attempts DESC;