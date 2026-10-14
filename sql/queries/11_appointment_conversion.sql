-- Appointment to order conversion
SELECT
    appointment_status,
    COUNT(*) AS appointments,
    SUM(CASE WHEN linked_order_id IS NOT NULL THEN 1 ELSE 0 END) AS converted,
    ROUND(100.0 * SUM(CASE WHEN linked_order_id IS NOT NULL THEN 1 ELSE 0 END) /
          COUNT(*), 2) AS conversion_rate
FROM designer_appointments
GROUP BY appointment_status;