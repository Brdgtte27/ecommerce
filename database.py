import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "_file_" in globals() else os.getcwd()
DB_PATH = os.path.join(BASE_DIR, "database.db")
print("DB Path =", DB_PATH)


def init_db():
    """Initialize database and tables, and add missing columns if needed"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # --- USERS TABLE ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            age INTEGER,
            birthday TEXT,
            phone TEXT,
            barangay TEXT,
            city TEXT,
            province TEXT,
            postal_code TEXT,
            address TEXT,
            profile_img TEXT DEFAULT ''
        )
    ''')

    # --- PRODUCTS TABLE ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            category TEXT,
            img TEXT,
            stock INTEGER DEFAULT 0,
            description TEXT DEFAULT ''
        )
    ''')

    # --- ORDERS TABLE ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            status TEXT DEFAULT 'Processing',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure total_amount column exists
    try:
        cur.execute("ALTER TABLE orders ADD COLUMN total_amount REAL DEFAULT 0")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # --- ORDER ITEMS TABLE ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_name TEXT,
            price REAL,
            quantity INTEGER,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    ''')

    # --- BROWSING HISTORY TABLE ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS browsing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            product_name TEXT,
            price REAL,
            img TEXT,
            viewed_on TEXT
        )
    ''')

    conn.commit()
    conn.close()


# Initialize DB
init_db()

# ========================= CART =========================
def get_cart_by_user(user_email):
    """Retrieve saved cart for a user"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            product_name TEXT,
            price REAL,
            quantity INTEGER
        )
    """)
    cur.execute("SELECT product_name, price, quantity FROM cart WHERE user_email=?", (user_email,))
    rows = cur.fetchall()
    conn.close()
    return [{"name": r[0], "price": r[1], "quantity": r[2]} for r in rows]


def save_cart_for_user(user_email, cart_items):
    """Save cart for a user (overwrites existing cart)"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            product_name TEXT,
            price REAL,
            quantity INTEGER
        )
    """)
    # Remove old cart
    cur.execute("DELETE FROM cart WHERE user_email=?", (user_email,))
    # Insert new cart
    for item in cart_items:
        cur.execute(
            "INSERT INTO cart (user_email, product_name, price, quantity) VALUES (?, ?, ?, ?)",
            (user_email, item["name"], item["price"], item["quantity"])
        )
    conn.commit()
    conn.close()


def clear_cart(user_email):
    """Remove all items from user's cart"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE user_email=?", (user_email,))
    conn.commit()
    conn.close()

# ========================= BROWSING HISTORY =========================
def add_browsing_history(user_email, product_name, price, img):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO browsing_history (user_email, product_name, price, img, viewed_on)
        VALUES (?, ?, ?, ?, ?)
    """, (user_email, product_name, price, img, datetime.today().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()


def get_browsing_history_by_user(user_email):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT product_name, price, img, viewed_on
        FROM browsing_history
        WHERE user_email=?
        ORDER BY id DESC
        LIMIT 50
    """, (user_email,))
    rows = cur.fetchall()
    conn.close()
    return [{"name": r[0], "price": r[1], "img": r[2], "date": r[3]} for r in rows]


# ========================= USERS =========================
def add_user(first_name, last_name, email, password, age=None, birthday=None):
    """Add a new user"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO users (first_name, last_name, email, password, age, birthday)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, password, age, birthday))
        conn.commit()
        return True
    except Exception as e:
        print("Add user failed:", e)
        return False
    finally:
        conn.close()


def find_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()

    if row:
        keys = [
            "id", "first_name", "last_name", "email", "password", "age",
            "birthday", "phone", "barangay", "city", "province",
            "postal_code", "address", "profile_img"
        ]
        return dict(zip(keys, row))

    return None


def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    conn.close()

    keys = [
        "id", "first_name", "last_name", "email", "password", "age",
        "birthday", "phone", "barangay", "city", "province",
        "postal_code", "address", "profile_img"
    ]

    return [dict(zip(keys, row)) for row in rows]


def update_user_profile(email, first_name=None, last_name=None, age=None, birthday=None,
                        gender=None, phone=None, barangay=None, city=None, province=None,
                        postal_code=None, address=None, profile_img=None):
    """Update user fields dynamically"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    fields, values = [], []

    for key, val in [
        ("first_name", first_name),
        ("last_name", last_name),
        ("age", age),
        ("birthday", birthday),
        ("phone", phone),
        ("barangay", barangay),
        ("city", city),
        ("province", province),
        ("postal_code", postal_code if postal_code is not None else ""),
        ("address", address),
        ("profile_img", profile_img)
    ]:
        if val is not None:
            fields.append(f"{key}=?")
            values.append(val)

    if fields:
        sql = f"UPDATE users SET {', '.join(fields)} WHERE email=?"
        values.append(email)
        cur.execute(sql, values)
        conn.commit()

    conn.close()


def update_user_profile_with_img(email, profile_img_path):
    """Specifically update only profile image"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET profile_img=? WHERE email=?", (profile_img_path, email))
    conn.commit()
    conn.close()


# ========================= PRODUCTS =========================
def get_all_products():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, category, img, stock, description FROM products")
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "price": r[2], "category": r[3],
         "img": r[4], "stock": r[5], "description": r[6]}
        for r in rows
    ]


def add_product(name, category, price, img="default.png", stock=0, desc=""):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (name, category, price, img, stock, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, price, img, stock, desc))
    conn.commit()
    conn.close()


def update_product(old_name, name, category, price, img, stock, desc):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE products
        SET name=?, category=?, price=?, img=?, stock=?, description=?
        WHERE name=?
    """, (name, category, price, img, stock, desc, old_name))
    conn.commit()
    conn.close()


def delete_product_db(product_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

# ========================= ORDERS =========================
def add_order_full(user_email, cart_items):
    """
    Create an order and insert items into order_items table.
    cart_items is a list of dicts: [{'name':..., 'price':..., 'quantity':...}, ...]
    """
    if not cart_items:
        return None  # Cannot create empty order

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Calculate total
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)

    # Insert order
    cur.execute("INSERT INTO orders (user_email, total_amount) VALUES (?, ?)",
                (user_email, total_amount))
    order_id = cur.lastrowid

    # Insert order items
    for item in cart_items:
        cur.execute(
            "INSERT INTO order_items (order_id, product_name, price, quantity) VALUES (?, ?, ?, ?)",
            (order_id, item['name'], item['price'], item['quantity'])
        )

    conn.commit()
    conn.close()
    return order_id


def get_orders_by_user_full(user_email):
    """
    Retrieve all orders and their items for a user.
    Returns a list of orders, each with 'id', 'status', 'total_amount', 'created_at', 'items'.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get all orders for user
    cur.execute("SELECT id, status, total_amount, created_at FROM orders WHERE user_email=?", (user_email,))
    orders_rows = cur.fetchall()
    orders = []

    for order_row in orders_rows:
        order_id, status, total_amount, created_at = order_row

        # Get items for this order
        cur.execute("SELECT product_name, price, quantity FROM order_items WHERE order_id=?", (order_id,))
        items_rows = cur.fetchall()
        items = [{'name': r[0], 'price': r[1], 'quantity': r[2]} for r in items_rows]

        orders.append({
            'id': order_id,
            'status': status,
            'total_amount': total_amount,
            'created_at': created_at,
            'items': items
        })

    conn.close()
    return orders


def update_order_status(order_id, status):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()
