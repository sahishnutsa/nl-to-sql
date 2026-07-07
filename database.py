import sqlite3
import random
import os

DB_FILE = "ecommerce.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def seed_database():
    # Only seed if DB doesn't exist yet
    if os.path.exists(DB_FILE):
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    # ---------------- CUSTOMERS ----------------
    first_names = ["Aarav", "Vivaan", "Aditya", "Ishaan", "Kabir", "Ananya", "Diya",
                   "Saanvi", "Meera", "Riya", "Arjun", "Kiran", "Neha", "Pooja",
                   "Rohan", "Sanya", "Tanvi", "Vikram", "Yash", "Zara"]
    last_names = ["Sharma", "Verma", "Iyer", "Nair", "Reddy", "Gupta", "Mehta",
                  "Kapoor", "Rao", "Joshi"]
    cities = ["Madurai", "Chennai", "Bengaluru", "Mumbai", "Delhi", "Pune",
              "Hyderabad", "Kolkata", "Ahmedabad", "Jaipur"]

    customers = []
    for i in range(60):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
        city = random.choice(cities)
        customers.append((name, email, city))

    cur.executemany("INSERT INTO customers (name, email, city) VALUES (?, ?, ?)", customers)

    # ---------------- PRODUCTS ----------------
    product_catalog = [
        "Wireless Mouse", "Mechanical Keyboard", "USB-C Cable", "Laptop Stand",
        "Bluetooth Speaker", "Smartwatch", "Noise Cancelling Headphones", "Webcam HD",
        "Portable SSD 1TB", "Power Bank 20000mAh", "Gaming Chair", "Monitor 27 inch",
        "Wireless Charger", "Router Wi-Fi 6", "Smart Bulb", "Fitness Tracker",
        "Backpack Laptop 15.6", "Desk Lamp LED", "Air Purifier", "Electric Kettle",
        "Coffee Maker", "Blender", "Yoga Mat", "Running Shoes", "Sunglasses",
        "Digital Camera", "Tripod Stand", "External Hard Drive 2TB", "Graphic Tablet",
        "Microphone USB", "Office Chair", "Study Table", "Bookshelf Wooden",
        "Sofa 3-Seater", "Dining Table Set", "Refrigerator 250L", "Washing Machine",
        "Microwave Oven", "Air Conditioner 1.5 Ton", "Ceiling Fan", "Table Fan",
        "Water Purifier", "Vacuum Cleaner", "Iron Box", "Hair Dryer",
        "Electric Toothbrush", "Sports Watch", "Bicycle Helmet", "Cricket Bat",
        "Football", "Badminton Racket", "Tennis Ball Pack", "Chess Set",
        "Puzzle Board Game", "Kids Tricycle", "Baby Stroller", "School Bag",
        "Notebook Pack", "Pen Set Premium"
    ]
    products = []
    for name in product_catalog:
        price = round(random.uniform(99, 45000), 2)
        stock = random.choice([0, 0, 0, 5, 10, 15, 20, 25, 40, 60, 100])
        products.append((name, price, stock))

    cur.executemany("INSERT INTO products (product_name, price, stock) VALUES (?, ?, ?)", products)

    conn.commit()

    # ---------------- ORDERS ----------------
    cur.execute("SELECT customer_id FROM customers")
    customer_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT product_id FROM products")
    product_ids = [r[0] for r in cur.fetchall()]

    orders = []
    for _ in range(150):
        cust = random.choice(customer_ids)
        prod = random.choice(product_ids)
        qty = random.randint(1, 5)
        # random date within last 90 days
        days_ago = random.randint(0, 90)
        order_date = f"date('now', '-{days_ago} days')"
        orders.append((cust, prod, qty, days_ago))

    for cust, prod, qty, days_ago in orders:
        cur.execute(
            "INSERT INTO orders (customer_id, product_id, quantity, order_date) "
            "VALUES (?, ?, ?, date('now', ? || ' days'))",
            (cust, prod, qty, f"-{days_ago}")
        )

    conn.commit()
    conn.close()
    print("Database seeded successfully.")


SCHEMA_DESCRIPTION = """
Table: customers
  - customer_id (INTEGER, PRIMARY KEY)
  - name (TEXT)
  - email (TEXT)
  - city (TEXT)

Table: products
  - product_id (INTEGER, PRIMARY KEY)
  - product_name (TEXT)
  - price (REAL)
  - stock (INTEGER)

Table: orders
  - order_id (INTEGER, PRIMARY KEY)
  - customer_id (INTEGER, FOREIGN KEY -> customers.customer_id)
  - product_id (INTEGER, FOREIGN KEY -> products.product_id)
  - quantity (INTEGER)
  - order_date (TEXT, format YYYY-MM-DD)

Relationships:
  - orders.customer_id references customers.customer_id
  - orders.product_id references products.product_id
"""