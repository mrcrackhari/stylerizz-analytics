-- Customer purchase funnel counts
SELECT 'Sessions'       AS stage, COUNT(*) AS count FROM browsing_sessions
UNION ALL SELECT 'Product Views',  COUNT(*) FROM product_views
UNION ALL SELECT 'Product Clicks', COUNT(*) FROM product_clicks
UNION ALL SELECT 'Favorites',      COUNT(*) FROM favorite_items
UNION ALL SELECT 'Cart Adds',      COUNT(*) FROM cart_items
UNION ALL SELECT 'Orders',         COUNT(*) FROM orders;