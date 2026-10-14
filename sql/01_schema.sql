-- ==========================================================
-- STYLERIZZ ANALYTICS — SCHEMA
-- MariaDB / MySQL compatible
-- ==========================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ============ MASTER TABLES ============

CREATE TABLE IF NOT EXISTS platform_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS customer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    gender VARCHAR(20),
    city VARCHAR(100),
    country_code VARCHAR(10),
    marketing_consent TINYINT(1) NOT NULL DEFAULT 0,
    user_type VARCHAR(50) NOT NULL,
    email VARCHAR(150),
    status VARCHAR(30) NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    birth_year INT,
    state_region VARCHAR(100),
    customer_since DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES platform_users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS customer_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    address_type VARCHAR(20) NOT NULL,
    state_region VARCHAR(100),
    country_code VARCHAR(10),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    is_default TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vendor_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    vendor_name VARCHAR(200) NOT NULL,
    commission_plan VARCHAR(100),
    status VARCHAR(30) NOT NULL,
    vendor_type VARCHAR(50) NOT NULL,
    onboarded_at DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES platform_users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vendor_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    contact_name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    role_title VARCHAR(100),
    phone VARCHAR(30),
    FOREIGN KEY (vendor_id) REFERENCES vendor_accounts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vendor_branches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    branch_name VARCHAR(150) NOT NULL,
    state_region VARCHAR(100),
    is_dispatch_location TINYINT(1) NOT NULL DEFAULT 0,
    city VARCHAR(100),
    country_code VARCHAR(10),
    FOREIGN KEY (vendor_id) REFERENCES vendor_accounts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS designer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    vendor_id INT,
    specialty VARCHAR(150),
    display_name VARCHAR(150) NOT NULL,
    profile_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES platform_users(id),
    FOREIGN KEY (vendor_id) REFERENCES vendor_accounts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS stylist_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    display_name VARCHAR(150) NOT NULL,
    consultation_fee DECIMAL(10,2),
    speciality VARCHAR(150),
    profile_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES platform_users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT,
    category_name VARCHAR(150) NOT NULL,
    category_slug VARCHAR(150) UNIQUE,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(150) NOT NULL,
    brand_type VARCHAR(50) NOT NULL,
    vendor_id INT,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (vendor_id) REFERENCES vendor_accounts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fabrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fabric_name VARCHAR(100) NOT NULL UNIQUE,
    fabric_group VARCHAR(100),
    care_notes TEXT,
    is_active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS occasions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    occasion_name VARCHAR(100) NOT NULL UNIQUE,
    season_tag VARCHAR(50),
    is_active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_attributes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attribute_type VARCHAR(50) NOT NULL,
    attribute_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS attribute_values (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attribute_id INT NOT NULL,
    value_label VARCHAR(100) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (attribute_id) REFERENCES product_attributes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS traffic_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_group VARCHAR(100) NOT NULL,
    platform_name VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ PRODUCT / INVENTORY ============

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT,
    brand_id INT,
    product_code VARCHAR(100) UNIQUE,
    product_name VARCHAR(250) NOT NULL,
    product_type VARCHAR(100) NOT NULL,
    listing_type VARCHAR(50) NOT NULL,
    description TEXT,
    base_price DECIMAL(12,2) NOT NULL,
    status VARCHAR(30) NOT NULL,
    listed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendor_accounts(id),
    FOREIGN KEY (brand_id) REFERENCES brands(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_variants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    sku VARCHAR(100) UNIQUE,
    size_label VARCHAR(50),
    colour_label VARCHAR(50),
    variant_price DECIMAL(12,2),
    customization_available TINYINT(1) NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    image_role VARCHAR(50) NOT NULL,
    display_order INT NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    is_primary TINYINT(1) NOT NULL DEFAULT 0,
    UNIQUE KEY uq_product_category (product_id, category_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_fabrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    fabric_id INT NOT NULL,
    fabric_share_percent DECIMAL(5,2),
    UNIQUE KEY uq_product_fabric (product_id, fabric_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (fabric_id) REFERENCES fabrics(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_occasions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    occasion_id INT NOT NULL,
    UNIQUE KEY uq_product_occasion (product_id, occasion_id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (occasion_id) REFERENCES occasions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS inventory_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT,
    location_name VARCHAR(200) NOT NULL,
    location_type VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    FOREIGN KEY (vendor_id) REFERENCES vendor_accounts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS inventory_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    variant_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id),
    FOREIGN KEY (location_id) REFERENCES inventory_locations(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ DISCOVERY / CART ============

CREATE TABLE IF NOT EXISTS browsing_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    session_key VARCHAR(200) UNIQUE NOT NULL,
    device_type VARCHAR(50),
    traffic_source_id INT,
    channel VARCHAR(50) NOT NULL,
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    landing_url VARCHAR(500),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id),
    FOREIGN KEY (traffic_source_id) REFERENCES traffic_sources(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_name VARCHAR(200) NOT NULL,
    campaign_channel VARCHAR(100),
    start_at DATETIME,
    end_at DATETIME,
    budget DECIMAL(12,2),
    campaign_status VARCHAR(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS web_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    session_id INT,
    product_id INT,
    campaign_id INT,
    event_type VARCHAR(100) NOT NULL,
    event_at DATETIME NOT NULL,
    event_value DECIMAL(12,2),
    page_or_screen VARCHAR(200),
    event_metadata JSON,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id),
    FOREIGN KEY (session_id) REFERENCES browsing_sessions(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_views (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    session_id INT,
    product_id INT NOT NULL,
    viewed_at DATETIME NOT NULL,
    duration_seconds INT,
    source_surface VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id),
    FOREIGN KEY (session_id) REFERENCES browsing_sessions(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_clicks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    session_id INT,
    product_id INT NOT NULL,
    clicked_at DATETIME NOT NULL,
    source_surface VARCHAR(100),
    click_position INT,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id),
    FOREIGN KEY (session_id) REFERENCES browsing_sessions(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS search_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    session_id INT,
    clicked_product_id INT,
    search_query VARCHAR(500) NOT NULL,
    searched_at DATETIME NOT NULL,
    results_count INT,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id),
    FOREIGN KEY (session_id) REFERENCES browsing_sessions(id),
    FOREIGN KEY (clicked_product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    list_name VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS favorite_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    favorite_id INT NOT NULL,
    product_id INT NOT NULL,
    added_at DATETIME NOT NULL,
    removed_at DATETIME,
    FOREIGN KEY (favorite_id) REFERENCES favorites(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    customer_id INT,
    cart_status VARCHAR(30) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    converted_order_id INT,
    FOREIGN KEY (session_id) REFERENCES browsing_sessions(id),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    item_status VARCHAR(30) NOT NULL,
    added_at DATETIME NOT NULL,
    removed_at DATETIME,
    FOREIGN KEY (cart_id) REFERENCES carts(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cart_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    cart_item_id INT,
    session_id INT,
    event_at DATETIME NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES carts(id),
    FOREIGN KEY (cart_item_id) REFERENCES cart_items(id),
    FOREIGN KEY (session_id) REFERENCES browsing_sessions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_recommendation_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    session_id INT,
    product_id INT NOT NULL,
    linked_order_id INT,
    recommendation_slot VARCHAR(100),
    event_type VARCHAR(50) NOT NULL,
    event_at DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id),
    FOREIGN KEY (session_id) REFERENCES browsing_sessions(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ ORDERS / FULFILMENT ============

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    session_id INT,
    ordered_at DATETIME NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    currency_code VARCHAR(10) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    shipping_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    grand_total DECIMAL(12,2) NOT NULL,
    vendor_count INT NOT NULL DEFAULT 1,
    source_channel VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id),
    FOREIGN KEY (session_id) REFERENCES browsing_sessions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT,
    vendor_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    line_total DECIMAL(12,2) NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id),
    FOREIGN KEY (vendor_id) REFERENCES vendor_accounts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS order_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    status_name VARCHAR(50) NOT NULL,
    status_at DATETIME NOT NULL,
    changed_by_user_id INT,
    order_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (changed_by_user_id) REFERENCES platform_users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS payment_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    attempt_number INT NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    attempted_at DATETIME NOT NULL,
    failure_reason VARCHAR(255),
    order_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_attempt_id INT NOT NULL,
    paid_amount DECIMAL(12,2) NOT NULL,
    paid_at DATETIME NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (payment_attempt_id) REFERENCES payment_attempts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS refunds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    refund_amount DECIMAL(12,2) NOT NULL,
    processed_at DATETIME NOT NULL,
    reason VARCHAR(255),
    FOREIGN KEY (order_id) REFERENCES orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS coupons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    coupon_code VARCHAR(50) UNIQUE NOT NULL,
    discount_type VARCHAR(30) NOT NULL,
    discount_value DECIMAL(12,2) NOT NULL,
    minimum_order_value DECIMAL(12,2),
    maximum_discount DECIMAL(12,2),
    valid_from DATETIME,
    valid_to DATETIME,
    usage_limit INT,
    status VARCHAR(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS designer_appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    designer_id INT,
    stylist_id INT,
    linked_order_id INT,
    appointment_type VARCHAR(100) NOT NULL,
    scheduled_at DATETIME NOT NULL,
    booked_at DATETIME NOT NULL,
    completed_at DATETIME,
    appointment_fee DECIMAL(10,2),
    appointment_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id),
    FOREIGN KEY (designer_id) REFERENCES designer_profiles(id),
    FOREIGN KEY (stylist_id) REFERENCES stylist_profiles(id),
    FOREIGN KEY (linked_order_id) REFERENCES orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS appointment_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    status_name VARCHAR(50) NOT NULL,
    status_at DATETIME NOT NULL,
    status_note VARCHAR(255),
    FOREIGN KEY (appointment_id) REFERENCES designer_appointments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vendor_commissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    order_id INT NOT NULL,
    order_item_id INT,
    commission_rate DECIMAL(5,4) NOT NULL,
    commission_amount DECIMAL(12,2) NOT NULL,
    eligible_sales DECIMAL(12,2) NOT NULL,
    calculated_at DATETIME NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendor_accounts(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (order_item_id) REFERENCES order_items(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vendor_payouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    gross_sales DECIMAL(12,2) NOT NULL,
    commission_deducted DECIMAL(12,2) NOT NULL,
    refund_adjustment DECIMAL(12,2) NOT NULL DEFAULT 0,
    net_payout DECIMAL(12,2) NOT NULL,
    payout_status VARCHAR(30) NOT NULL,
    paid_at DATETIME,
    FOREIGN KEY (vendor_id) REFERENCES vendor_accounts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS customer_support_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_id INT,
    ticket_category VARCHAR(100) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    ticket_status VARCHAR(30) NOT NULL,
    opened_at DATETIME NOT NULL,
    closed_at DATETIME,
    resolution_code VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customer_profiles(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============ IMPORT / AUDIT ============

CREATE TABLE IF NOT EXISTS import_batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(150) NOT NULL,
    source_file VARCHAR(500) NOT NULL,
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    rows_read INT NOT NULL DEFAULT 0,
    rows_loaded INT NOT NULL DEFAULT 0,
    rows_rejected INT NOT NULL DEFAULT 0,
    batch_status VARCHAR(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS import_errors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    source_row_number INT,
    source_key VARCHAR(200),
    error_code VARCHAR(50) NOT NULL,
    error_message TEXT NOT NULL,
    raw_row TEXT,
    resolution_note TEXT,
    resolved_at DATETIME,
    FOREIGN KEY (batch_id) REFERENCES import_batches(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS data_quality_checks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT,
    table_name VARCHAR(100) NOT NULL,
    check_name VARCHAR(150) NOT NULL,
    records_checked INT NOT NULL,
    records_failed INT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    checked_at DATETIME NOT NULL,
    details TEXT,
    FOREIGN KEY (batch_id) REFERENCES import_batches(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS report_runs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_code VARCHAR(50) NOT NULL,
    report_name VARCHAR(150) NOT NULL,
    generated_by INT,
    generated_at DATETIME NOT NULL,
    output_format VARCHAR(30) NOT NULL,
    output_reference VARCHAR(500),
    filter_context JSON,
    run_status VARCHAR(30) NOT NULL,
    error_message TEXT,
    FOREIGN KEY (generated_by) REFERENCES platform_users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;