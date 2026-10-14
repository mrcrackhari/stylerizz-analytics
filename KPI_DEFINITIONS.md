# Stylerizz Analytics — KPI Definitions

**Project:** PH-06 Fashion E-Commerce & Multi-Vendor Marketplace Analytics
**Data window:** Synthetic data, ~12 months ending Feb 2025
**Owner:** Stylerizz Analytics Intern

---

## Revenue KPIs

### GMV (Gross Merchandise Value)
- **Formula:** `SUM(orders.grand_total)`
- **Filter:** `order_status NOT IN ('cancelled', 'failed')`
- **Grain:** Per order header
- **Notes:** Includes tax + shipping. Excludes refunds.

### Net Sales
- **Formula:** `GMV - SUM(refunds.refund_amount)`
- **Notes:** Recognizes returned/cancelled orders at their refunded value.

### AOV (Average Order Value)
- **Formula:** `GMV / COUNT(DISTINCT orders.id)`
- **Grain:** Per order.

### Discount Cost
- **Formula:** `SUM(orders.discount_amount)`
- **Notes:** Only counts discounts actually applied at checkout.

---

## Customer & Funnel KPIs

### Conversion Rate (Session → Order)
- **Formula:** `COUNT(DISTINCT orders.session_id) / COUNT(DISTINCT browsing_sessions.id)`
- **Attribution window:** Last-touch, same session only.
- **Anonymous sessions:** Excluded from customer-level rollups but counted in the denominator.

### Cart Abandonment Rate
- **Formula:** `1 - (carts with cart_status='converted') / total_carts`

### Repeat Purchase Rate
- **Formula:** `customers with 2+ orders / customers with 1+ orders`

### Customer Cohort Retention
- **Definition:** Cohort by `customer_since` month.
- **Retention metric:** Percentage of cohort with an order in month N+1, N+2, ...

---

## Payment KPIs

### Payment Success Rate
- **Formula:** `SUCCESSFUL_PAYMENTS / PAYMENT_ATTEMPTS`
- **Notes:** Retries counted as separate attempts. Denominator includes failed attempts.

### Refund Rate
- **Formula:** `COUNT(refunds) / COUNT(orders)`
- **Filter:** All orders including cancellations.

---

## Fulfillment KPIs

### Order Confirmation → Dispatch Time
- **Formula:** `dispatch_event.at - confirmation_event.at`
- **Source:** `order_status_history` (where populated)
- **Notes:** Reported in hours.

### Dispatch → Delivery Time
- **Formula:** `delivery_event.at - dispatch_event.at`

### Delayed Shipment
- **Definition:** Any order with dispatch time > 48h.

---

## Vendor KPIs

### Vendor Commission
- **Formula:** `SUM(vendor_commissions.commission_amount)`
- **Grain:** Per order-item, stored after order completion.

### Vendor Fulfillment Rate
- **Formula:** `delivered_orders / total_orders` per vendor.

### Vendor Cancellation Rate
- **Formula:** `cancelled_orders / total_orders` per vendor.

---

## Appointment KPIs

### Appointment Conversion
- **Formula:** `appointments with linked_order_id / total appointments`
- **Filter:** Only appointments with reliably linked orders.
- **Warning:** Do NOT infer identity from anonymous browsing.

---

## Data Quality Rules

| Check | Threshold |
|-------|-----------|
| Orphan FKs | 0 |
| Duplicate source IDs | 0 |
| Negative amounts | 0 |
| Orders before customer_since | 0 |
| Duplicate session_key | 0 |

---

## Important Interpretation Cautions

1. **High views ≠ demand.** Views reflect discovery, not intent.
2. **Coupon usage ≠ incremental sales.** Need A/B holdout to prove causality.
3. **Attribution is last-touch, same-session only.** Multi-touch not modeled.
4. **Synthetic data.** All figures are illustrative; not real customer transactions.
5. **Returned vs cancelled.** Both treated separately; refunds applied at order level.