"""
03_seed_data.py — Populates Stylerizz with synthetic data.
Run from project root:  python sql/03_seed_data.py

⚠️  Run only on an EMPTY database. If tables have data,
    truncate them first (see chat instructions).
"""
import random
import string
import sys
from datetime import datetime, timedelta

import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "stylerizz_analytics",
    "port": 3306,
    "charset": "utf8mb4",
    "use_pure": True,
    "autocommit": False,
    "raise_on_warnings": False,
}

random.seed(42)


# ---------- helpers ----------
def rand_phone():
    return "+91" + "".join(random.choices(string.digits, k=10))


def rand_email(name):
    slug = name.lower().replace(" ", ".").replace("'", "")
    return f"{slug}{random.randint(1, 999)}@example.com"


def rand_date(start_days_ago=730, end_days_ago=0):
    days = random.randint(end_days_ago, start_days_ago)
    return datetime.now() - timedelta(
        days=days,
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


# ---------- reference data ----------
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Pranav", "Dhruv",
    "Krishna", "Ishaan", "Ananya", "Diya", "Aadhya", "Saanvi", "Pari", "Anika",
    "Navya", "Myra", "Sara", "Riya", "Rohan", "Karan", "Neha", "Priya",
    "Pooja", "Sneha", "Meera", "Kavya", "Tara", "Zoya",
]
LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Iyer", "Nair", "Gupta", "Singh",
    "Khan", "Mehta", "Joshi", "Rao", "Das", "Bose", "Chopra", "Kapoor",
    "Malhotra", "Bhatia", "Sinha", "Agarwal",
]
CITIES = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata",
    "Pune", "Ahmedabad", "Jaipur", "Lucknow",
]
STATES = [
    "Maharashtra", "Delhi", "Karnataka", "Telangana", "Tamil Nadu",
    "West Bengal", "Maharashtra", "Gujarat", "Rajasthan", "Uttar Pradesh",
]

VENDOR_NAMES = [
    "Rangoli Boutique", "Meera Sarees", "Kalaa Threads", "Vastra House",
    "Zariya Couture", "Silk Route", "Bandhani Bazaar", "Chikan Studio",
    "Banaras Weaves", "Anarkali & Co.",
]

CATEGORY_TREE = [
    ("Women", None),
    ("Men", None),
    ("Kids", None),
    ("Sarees", "Women"),
    ("Lehengas", "Women"),
    ("Salwar Suits", "Women"),
    ("Kurta Sets", "Women"),
    ("Sherwanis", "Men"),
    ("Kurtas", "Men"),
    ("Dhotis", "Men"),
    ("Ethnic Frocks", "Kids"),
    ("Wedding Wear", None),
    ("Festive Wear", None),
    ("Casual Ethnic", None),
    ("Designer Wear", None),
]

FABRIC_DATA = [
    ("Banarasi Silk", "Silk", "Dry clean only"),
    ("Kanjeevaram Silk", "Silk", "Dry clean only"),
    ("Chanderi Cotton", "Cotton", "Hand wash cold"),
    ("Chiffon", "Synthetic", "Hand wash"),
    ("Georgette", "Synthetic", "Hand wash cold"),
    ("Organza", "Silk", "Dry clean"),
    ("Velvet", "Silk", "Dry clean"),
    ("Cotton Linen", "Cotton", "Machine wash cold"),
    ("Brocade", "Silk", "Dry clean only"),
    ("Net", "Synthetic", "Hand wash"),
]

OCCASION_DATA = [
    ("Wedding", "Wedding"),
    ("Sangeet", "Wedding"),
    ("Mehendi", "Wedding"),
    ("Reception", "Wedding"),
    ("Diwali", "Festive"),
    ("Eid", "Festive"),
    ("Navratri", "Festive"),
    ("Pongal", "Festive"),
    ("Karwa Chauth", "Festive"),
    ("Office Party", "Party"),
    ("Casual Day", "Casual"),
    ("Anniversary", "Party"),
]

ATTRIBUTES = [
    ("colour", ["Red", "Blue", "Green", "Pink", "Yellow", "Purple", "White", "Black", "Gold", "Maroon"]),
    ("size", ["XS", "S", "M", "L", "XL", "XXL", "Free Size"]),
    ("style", ["A-line", "Anarkali", "Straight", "Flared", "Panelled", "Layered"]),
    ("silhouette", ["Fit and Flare", "Bodycon", "Loose", "Tailored"]),
]

TRAFFIC_SOURCES = [
    ("google", "Search", "Google"),
    ("instagram", "Social", "Instagram"),
    ("facebook", "Social", "Facebook"),
    ("direct", "Direct", "Direct"),
    ("youtube", "Social", "YouTube"),
    ("whatsapp", "Social", "WhatsApp"),
    ("email", "Email", "Email"),
    ("affiliate", "Affiliate", "Various"),
]

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet", "COD", "EMI"]
FAILURE_REASONS = [
    "Insufficient funds", "Card declined", "Timeout", "Invalid CVV",
    "Bank server error", "UPI failure", "Session expired",
]


# ---------- main ----------
def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

    cur = conn.cursor()
    print("✅ Connected to stylerizz_analytics\n")

    # 1. platform_users
    print("▶ platform_users...")
    users = [("Admin Stylerizz", rand_phone())]
    for _ in range(30):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        users.append((name, rand_phone()))
    cur.executemany(
        "INSERT INTO platform_users (full_name, phone) VALUES (%s,%s)", users
    )
    conn.commit()
    vendor_user_ids = list(range(2, 12))
    designer_stylist_user_ids = list(range(12, 32))

    # 2. vendor_accounts
    print("▶ vendor_accounts...")
    vendors = []
    for i, vname in enumerate(VENDOR_NAMES):
        vendors.append((
            vendor_user_ids[i], vname, "standard_15", "active",
            random.choice(["boutique", "designer", "wholesaler"]),
            rand_date(1500, 300).date(),
        ))
    cur.executemany(
        """INSERT INTO vendor_accounts
           (user_id, vendor_name, commission_plan, status, vendor_type, onboarded_at)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        vendors,
    )
    conn.commit()
    vendor_ids = list(range(1, 11))

    # 3. vendor contacts + branches
    print("▶ vendor_contacts + vendor_branches...")
    for vid in vendor_ids:
        cur.execute(
            """INSERT INTO vendor_contacts
               (vendor_id, contact_name, email, role_title, phone)
               VALUES (%s,%s,%s,%s,%s)""",
            (
                vid,
                f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                f"contact{vid}@vendor.com",
                "Manager",
                rand_phone(),
            ),
        )
        for _ in range(random.randint(1, 2)):
            cur.execute(
                """INSERT INTO vendor_branches
                   (vendor_id, branch_name, state_region, is_dispatch_location, city, country_code)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (
                    vid,
                    f"Branch {random.randint(1, 99)}",
                    random.choice(STATES),
                    random.choice([0, 1]),
                    random.choice(CITIES),
                    "IN",
                ),
            )
    conn.commit()

    # 4. designers + stylists
    print("▶ designer_profiles + stylist_profiles...")
    for i, uid in enumerate(designer_stylist_user_ids):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if i < 10:
            cur.execute(
                """INSERT INTO designer_profiles
                   (user_id, vendor_id, specialty, display_name, profile_status)
                   VALUES (%s,%s,%s,%s,%s)""",
                (
                    uid,
                    random.choice(vendor_ids),
                    random.choice(["Bridal", "Festive", "Indo-Western", "Luxury"]),
                    name,
                    "active",
                ),
            )
        else:
            cur.execute(
                """INSERT INTO stylist_profiles
                   (user_id, display_name, consultation_fee, speciality, profile_status)
                   VALUES (%s,%s,%s,%s,%s)""",
                (
                    uid,
                    name,
                    random.choice([500, 1000, 1500, 2000]),
                    random.choice(["Personal Shopping", "Bridal Styling", "Wardrobe"]),
                    "active",
                ),
            )
    conn.commit()

    # 5. categories
    print("▶ categories...")
    cat_ids = {}
    for cname, parent_name in CATEGORY_TREE:
        parent_id = cat_ids.get(parent_name)
        cur.execute(
            """INSERT INTO categories (parent_id, category_name, category_slug, is_active)
               VALUES (%s,%s,%s,1)""",
            (parent_id, cname, cname.lower().replace(" ", "-")),
        )
        cat_ids[cname] = cur.lastrowid
    conn.commit()

    # 6. brands
    print("▶ brands...")
    brand_ids = []
    cur.execute(
        """INSERT INTO brands (brand_name, brand_type, vendor_id, is_active)
           VALUES (%s,'platform_owned',NULL,1)""",
        ("Stylerizz Signature",),
    )
    brand_ids.append(cur.lastrowid)
    for vid in vendor_ids:
        cur.execute(
            """INSERT INTO brands (brand_name, brand_type, vendor_id, is_active)
               VALUES (%s,'third_party',%s,1)""",
            (f"Brand {vid}", vid),
        )
        brand_ids.append(cur.lastrowid)
    conn.commit()

    # 7. fabrics
    print("▶ fabrics...")
    cur.executemany(
        """INSERT INTO fabrics (fabric_name, fabric_group, care_notes, is_active)
           VALUES (%s,%s,%s,1)""",
        FABRIC_DATA,
    )
    conn.commit()
    fabric_ids = list(range(1, len(FABRIC_DATA) + 1))

    # 8. occasions
    print("▶ occasions...")
    cur.executemany(
        """INSERT INTO occasions (occasion_name, season_tag, is_active)
           VALUES (%s,%s,1)""",
        OCCASION_DATA,
    )
    conn.commit()
    occasion_ids = list(range(1, len(OCCASION_DATA) + 1))

    # 9. attributes
    print("▶ product_attributes + attribute_values...")
    for atype, values in ATTRIBUTES:
        cur.execute(
            """INSERT INTO product_attributes (attribute_type, attribute_name)
               VALUES (%s,%s)""",
            (atype, atype),
        )
        attr_id = cur.lastrowid
        for i, v in enumerate(values):
            cur.execute(
                """INSERT INTO attribute_values
                   (attribute_id, value_label, sort_order, is_active)
                   VALUES (%s,%s,%s,1)""",
                (attr_id, v, i),
            )
    conn.commit()

    # 10. traffic sources
    print("▶ traffic_sources...")
    cur.executemany(
        """INSERT INTO traffic_sources (source_name, source_group, platform_name)
           VALUES (%s,%s,%s)""",
        TRAFFIC_SOURCES,
    )
    conn.commit()
    traffic_ids = list(range(1, len(TRAFFIC_SOURCES) + 1))

    # 11. products
    print("▶ products...")
    N_PRODUCTS = 100
    product_ids = []
    cat_names = list(cat_ids.keys())
    adjectives = ["Royal", "Classic", "Modern", "Traditional", "Designer", "Handcrafted", "Premium", "Festive"]
    nouns = ["Saree", "Lehenga", "Kurta", "Sherwani", "Anarkali", "Salwar Suit", "Dupatta", "Blouse"]

    for i in range(N_PRODUCTS):
        listing = "vendor_listed" if i < 70 else "platform_owned"
        vid = random.choice(vendor_ids) if listing == "vendor_listed" else None
        bid = brand_ids[0] if listing == "platform_owned" else brand_ids[vid]
        base_price = round(random.uniform(1500, 25000), 2)
        name = f"{random.choice(adjectives)} {random.choice(nouns)} {random.randint(1, 999)}"
        cur.execute(
            """INSERT INTO products
               (vendor_id, brand_id, product_code, product_name, product_type,
                listing_type, description, base_price, status, listed_at,
                created_at, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                vid, bid, f"P{i+1:04d}", name,
                random.choice(["saree", "lehenga", "kurta", "sherwani"]),
                listing, f"Beautiful {name} perfect for occasions.",
                base_price, "active", rand_date(700, 30),
                rand_date(700, 30), datetime.now(),
            ),
        )
        pid = cur.lastrowid
        product_ids.append(pid)

        cur.execute(
            """INSERT INTO product_categories (product_id, category_id, is_primary)
               VALUES (%s,%s,1)""",
            (pid, cat_ids[random.choice(cat_names)]),
        )
        for _ in range(random.randint(1, 2)):
            cur.execute(
                """INSERT IGNORE INTO product_fabrics
                   (product_id, fabric_id, fabric_share_percent)
                   VALUES (%s,%s,%s)""",
                (pid, random.choice(fabric_ids), random.uniform(50, 100)),
            )
        for _ in range(random.randint(1, 3)):
            cur.execute(
                """INSERT IGNORE INTO product_occasions (product_id, occasion_id)
                   VALUES (%s,%s)""",
                (pid, random.choice(occasion_ids)),
            )
        for j in range(random.randint(2, 4)):
            cur.execute(
                """INSERT INTO product_images
                   (product_id, image_url, image_role, display_order)
                   VALUES (%s,%s,%s,%s)""",
                (
                    pid,
                    f"https://cdn.stylerizz.com/p{pid}_{j}.jpg",
                    "main" if j == 0 else "gallery",
                    j,
                ),
            )
    conn.commit()

    # 12. product variants
    print("▶ product_variants...")
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    colours = ["Red", "Blue", "Green", "Pink", "Yellow", "Gold", "Maroon", "Black"]
    for pid in product_ids:
        cur.execute("SELECT base_price FROM products WHERE id=%s", (pid,))
        base = float(cur.fetchone()[0])
        for k in range(random.randint(1, 4)):
            price = round(base * random.uniform(0.9, 1.15), 2)
            cur.execute(
                """INSERT INTO product_variants
                   (product_id, sku, size_label, colour_label, variant_price,
                    customization_available, status)
                   VALUES (%s,%s,%s,%s,%s,%s,'active')""",
                (
                    pid,
                    f"SKU-{pid}-{k}-{random.randint(1000, 9999)}",
                    random.choice(sizes),
                    random.choice(colours),
                    price,
                    random.choice([0, 1]),
                ),
            )
    conn.commit()

    # 13. inventory locations + stock
    print("▶ inventory_locations + inventory_stock...")
    loc_ids = []
    for vid in vendor_ids:
        cur.execute(
            """INSERT INTO inventory_locations
               (vendor_id, location_name, location_type, city)
               VALUES (%s,%s,'warehouse',%s)""",
            (vid, f"WH-{vid}", random.choice(CITIES)),
        )
        loc_ids.append(cur.lastrowid)
    cur.execute(
        """INSERT INTO inventory_locations
           (vendor_id, location_name, location_type, city)
           VALUES (NULL,'Platform Warehouse','warehouse','Mumbai')"""
    )
    loc_ids.append(cur.lastrowid)
    conn.commit()

    cur.execute("SELECT id FROM product_variants")
    variant_ids = [r[0] for r in cur.fetchall()]
    for vid in variant_ids:
        cur.execute(
            """INSERT INTO inventory_stock
               (variant_id, location_id, quantity, updated_at)
               VALUES (%s,%s,%s,%s)""",
            (vid, random.choice(loc_ids), random.randint(5, 100), datetime.now()),
        )
    conn.commit()

    # 14. customers
    print("▶ customer_profiles + addresses...")
    N_CUSTOMERS = 500
    customer_ids = []
    for _ in range(N_CUSTOMERS):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        cur.execute(
            "INSERT INTO platform_users (full_name, phone) VALUES (%s,%s)",
            (name, rand_phone()),
        )
        uid = cur.lastrowid
        cur.execute(
            """INSERT INTO customer_profiles
               (user_id, gender, city, country_code, marketing_consent, user_type,
                email, status, updated_at, birth_year, state_region,
                customer_since, created_at)
               VALUES (%s,%s,%s,'IN',%s,'customer',%s,'active',%s,%s,%s,%s,%s)""",
            (
                uid,
                random.choice(["male", "female", "other"]),
                random.choice(CITIES),
                random.choice([0, 1]),
                rand_email(name),
                datetime.now(),
                random.randint(1970, 2005),
                random.choice(STATES),
                rand_date(700, 5).date(),
                rand_date(700, 5),
            ),
        )
        cid = cur.lastrowid
        customer_ids.append(cid)
        for _ in range(random.randint(1, 2)):
            cur.execute(
                """INSERT INTO customer_addresses
                   (customer_id, address_type, state_region, country_code,
                    city, postal_code, is_default, created_at)
                   VALUES (%s,%s,%s,'IN',%s,%s,%s,%s)""",
                (
                    cid,
                    random.choice(["shipping", "billing"]),
                    random.choice(STATES),
                    random.choice(CITIES),
                    str(random.randint(100000, 999999)),
                    1,
                    rand_date(700, 5),
                ),
            )
    conn.commit()

    # 15. marketing campaigns
    print("▶ marketing_campaigns...")
    camp_names = [
        "Diwali Dhamaka", "Wedding Season Sale", "Navratri Special",
        "Republic Day Sale", "EOSS", "New Arrivals Launch",
        "Bridal Bonanza", "Festive Flash Sale",
    ]
    for cn in camp_names:
        cur.execute(
            """INSERT INTO marketing_campaigns
               (campaign_name, campaign_channel, start_at, end_at, budget, campaign_status)
               VALUES (%s,%s,%s,%s,%s,'active')""",
            (
                cn,
                random.choice(["email", "social", "search", "display"]),
                rand_date(400, 100),
                rand_date(100, 1),
                round(random.uniform(50000, 500000), 2),
            ),
        )
    conn.commit()

    # 16. browsing sessions  (FIXED: unique session_key)
    print("▶ browsing_sessions + product_views + product_clicks...")
    N_SESSIONS = 2000
    session_ids = []
    for i in range(N_SESSIONS):
        cid = random.choice(customer_ids) if random.random() < 0.8 else None
        started = rand_date(400, 1)
        unique_key = f"sess-{i:06d}-{random.randint(1000, 9999)}"
        cur.execute(
            """INSERT INTO browsing_sessions
               (customer_id, session_key, device_type, traffic_source_id, channel,
                started_at, ended_at, landing_url)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                cid,
                unique_key,
                random.choice(["mobile", "desktop", "tablet"]),
                random.choice(traffic_ids),
                random.choice(["organic", "paid", "direct", "social"]),
                started,
                started + timedelta(minutes=random.randint(1, 60)),
                random.choice(["/", "/sarees", "/lehengas", "/wedding", "/sale"]),
            ),
        )
        session_ids.append(cur.lastrowid)
    conn.commit()

    # product views
    for sid in session_ids:
        cur.execute("SELECT customer_id FROM browsing_sessions WHERE id=%s", (sid,))
        cid = cur.fetchone()[0]
        for _ in range(random.randint(1, 6)):
            cur.execute(
                """INSERT INTO product_views
                   (customer_id, session_id, product_id, viewed_at,
                    duration_seconds, source_surface)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (
                    cid, sid, random.choice(product_ids), rand_date(400, 1),
                    random.randint(5, 300),
                    random.choice(["home", "category", "search", "recommendation"]),
                ),
            )
    conn.commit()

    # clicks
    for sid in session_ids:
        cur.execute("SELECT customer_id FROM browsing_sessions WHERE id=%s", (sid,))
        cid = cur.fetchone()[0]
        for _ in range(random.randint(0, 3)):
            cur.execute(
                """INSERT INTO product_clicks
                   (customer_id, session_id, product_id, clicked_at,
                    source_surface, click_position)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (
                    cid, sid, random.choice(product_ids), rand_date(400, 1),
                    random.choice(["home", "category", "search"]),
                    random.randint(1, 20),
                ),
            )
    conn.commit()

    # 17. favorites
    print("▶ favorites + favorite_items...")
    for _ in range(300):
        cid = random.choice(customer_ids)
        cur.execute(
            """INSERT INTO favorites (customer_id, list_name, created_at)
               VALUES (%s,'My Wishlist',%s)""",
            (cid, rand_date(400, 1)),
        )
        fav_id = cur.lastrowid
        for _ in range(random.randint(1, 5)):
            cur.execute(
                """INSERT INTO favorite_items (favorite_id, product_id, added_at)
                   VALUES (%s,%s,%s)""",
                (fav_id, random.choice(product_ids), rand_date(400, 1)),
            )
    conn.commit()

    # 18. carts + cart_items
    print("▶ carts + cart_items...")
    converted_sessions = set(random.sample(session_ids, 800))
    for sid in session_ids[:1000]:
        cur.execute("SELECT customer_id FROM browsing_sessions WHERE id=%s", (sid,))
        cid = cur.fetchone()[0]
        status = "converted" if sid in converted_sessions else random.choice(["active", "abandoned"])
        cur.execute(
            """INSERT INTO carts (session_id, customer_id, cart_status, created_at, updated_at)
               VALUES (%s,%s,%s,%s,%s)""",
            (sid, cid, status, rand_date(400, 1), rand_date(400, 1)),
        )
        cart_id = cur.lastrowid
        for _ in range(random.randint(1, 3)):
            pid = random.choice(product_ids)
            cur.execute("SELECT base_price FROM products WHERE id=%s", (pid,))
            price = float(cur.fetchone()[0])
            cur.execute(
                """INSERT INTO cart_items
                   (cart_id, product_id, quantity, unit_price, item_status, added_at)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (cart_id, pid, random.randint(1, 2), price, "active", rand_date(400, 1)),
            )
    conn.commit()

    # 19. orders + order_items
    print("▶ orders + order_items...")
    N_ORDERS = 2000
    order_ids = []
    for i in range(N_ORDERS):
        cid = random.choice(customer_ids)
        subtotal = round(random.uniform(1500, 40000), 2)
        discount = round(subtotal * random.uniform(0, 0.3), 2)
        tax = round((subtotal - discount) * 0.05, 2)
        shipping = random.choice([0, 99, 149])
        grand = round(subtotal - discount + tax + shipping, 2)
        status = random.choices(
            ["delivered", "shipped", "processing", "cancelled", "returned"],
            weights=[60, 15, 10, 10, 5],
        )[0]
        cur.execute(
            """INSERT INTO orders
               (order_number, customer_id, session_id, ordered_at, order_status,
                currency_code, subtotal, discount_amount, tax_amount,
                shipping_amount, grand_total, vendor_count, source_channel)
               VALUES (%s,%s,%s,%s,%s,'INR',%s,%s,%s,%s,%s,%s,%s)""",
            (
                f"ORD-{100000 + i}",
                cid,
                random.choice(session_ids),
                rand_date(365, 1),
                status,
                subtotal, discount, tax, shipping, grand,
                random.randint(1, 3),
                random.choice(["web", "app", "marketplace"]),
            ),
        )
        oid = cur.lastrowid
        order_ids.append(oid)

        for _ in range(random.randint(1, 4)):
            pid = random.choice(product_ids)
            cur.execute("SELECT vendor_id, base_price FROM products WHERE id=%s", (pid,))
            row = cur.fetchone()
            vid, base = row[0], float(row[1])
            qty = random.randint(1, 3)
            line_total = round(base * qty, 2)
            cur.execute(
                """INSERT INTO order_items
                   (order_id, product_id, vendor_id, quantity,
                    unit_price, line_total, order_status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (oid, pid, vid, qty, base, line_total, status),
            )
    conn.commit()

    # 20. payments
    print("▶ payment_attempts + payments...")
    for oid in order_ids:
        cur.execute("SELECT grand_total, ordered_at FROM orders WHERE id=%s", (oid,))
        total, ordered = cur.fetchone()
        n_attempts = random.choices([1, 2, 3], weights=[75, 20, 5])[0]
        success = random.random() < 0.85
        for a in range(1, n_attempts + 1):
            is_last = a == n_attempts
            paid = is_last and success
            cur.execute(
                """INSERT INTO payment_attempts
                   (order_id, attempt_number, payment_method, attempted_at,
                    failure_reason, order_status)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (
                    oid, a, random.choice(PAYMENT_METHODS),
                    ordered + timedelta(minutes=a * 2),
                    None if paid else random.choice(FAILURE_REASONS),
                    "completed" if paid else "failed",
                ),
            )
            att_id = cur.lastrowid
            if paid:
                cur.execute(
                    """INSERT INTO payments
                       (order_id, payment_attempt_id, paid_amount, paid_at, order_status)
                       VALUES (%s,%s,%s,%s,'completed')""",
                    (oid, att_id, total, ordered + timedelta(minutes=a * 2 + 1)),
                )
    conn.commit()

    # 21. refunds
    print("▶ refunds...")
    cur.execute(
        "SELECT id, grand_total FROM orders WHERE order_status IN ('returned','cancelled')"
    )
    for oid, grand in cur.fetchall():
        amount = round(float(grand) * random.uniform(0.3, 1.0), 2)
        cur.execute(
            """INSERT INTO refunds (order_id, refund_amount, processed_at, reason)
               VALUES (%s,%s,%s,%s)""",
            (
                oid, amount, rand_date(300, 1),
                random.choice(["size issue", "wrong item", "quality", "changed mind"]),
            ),
        )
    conn.commit()

    # 22. designer appointments
    print("▶ designer_appointments...")
    cur.execute("SELECT id FROM designer_profiles")
    designer_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id FROM stylist_profiles")
    stylist_ids = [r[0] for r in cur.fetchall()]

    for _ in range(400):
        cid = random.choice(customer_ids)
        did = random.choice(designer_ids) if random.random() < 0.5 else None
        sty = random.choice(stylist_ids) if did is None else None
        status = random.choices(
            ["completed", "scheduled", "cancelled", "no_show"],
            weights=[50, 20, 20, 10],
        )[0]
        cur.execute(
            """INSERT INTO designer_appointments
               (customer_id, designer_id, stylist_id, linked_order_id,
                appointment_type, scheduled_at, booked_at, completed_at,
                appointment_fee, appointment_status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                cid, did, sty,
                random.choice(order_ids) if random.random() < 0.3 else None,
                random.choice(["Bridal Consultation", "Wardrobe Styling", "Designer Meet"]),
                rand_date(200, 1),
                rand_date(250, 10),
                rand_date(200, 1) if status == "completed" else None,
                random.choice([0, 500, 1000, 2000]),
                status,
            ),
        )
    conn.commit()

    # 23. vendor commissions
    print("▶ vendor_commissions...")
    cur.execute(
        """SELECT oi.id, oi.order_id, oi.vendor_id, oi.line_total
           FROM order_items oi WHERE oi.vendor_id IS NOT NULL"""
    )
    batch = []
    for oi_id, oid, vid, total in cur.fetchall():
        rate = 0.15
        batch.append((vid, oid, oi_id, rate, round(float(total) * rate, 2), total, datetime.now()))
    cur.executemany(
        """INSERT INTO vendor_commissions
           (vendor_id, order_id, order_item_id, commission_rate,
            commission_amount, eligible_sales, calculated_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        batch,
    )
    conn.commit()

    # 24. summary
    print("\n🎉 SEED COMPLETE — row counts:")
    tables = [
        "platform_users", "customer_profiles", "vendor_accounts", "products",
        "product_variants", "browsing_sessions", "product_views", "orders",
        "order_items", "payment_attempts", "payments", "refunds",
        "designer_appointments", "vendor_commissions",
    ]
    for tbl in tables:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"   {tbl:30s} {cur.fetchone()[0]:>8,}")

    cur.close()
    conn.close()
    print("\n✅ Done. Refresh your Streamlit dashboard.")


if __name__ == "__main__":
    main()