import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")


def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            city          TEXT NOT NULL,
            signup_date   TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name  TEXT NOT NULL,
            category      TEXT NOT NULL,
            price         REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id   INTEGER NOT NULL,
            order_date    TEXT NOT NULL,
            status        TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            item_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id      INTEGER NOT NULL,
            product_id    INTEGER NOT NULL,
            quantity      INTEGER NOT NULL,
            unit_price    REAL NOT NULL,
            FOREIGN KEY (order_id)   REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)


def seed_customers(cursor):
    customers = [
        ("Aarav Shah",    "aarav@example.com",   "Mumbai",    "2023-01-15"),
        ("Priya Nair",    "priya@example.com",   "Bangalore", "2023-02-20"),
        ("Rohan Mehta",   "rohan@example.com",   "Delhi",     "2023-03-10"),
        ("Sneha Iyer",    "sneha@example.com",   "Chennai",   "2023-04-05"),
        ("Vikram Patel",  "vikram@example.com",  "Ahmedabad", "2023-05-18"),
        ("Ananya Sharma", "ananya@example.com",  "Pune",      "2023-06-22"),
        ("Kiran Reddy",   "kiran@example.com",   "Hyderabad", "2023-07-30"),
        ("Divya Menon",   "divya@example.com",   "Kochi",     "2023-08-11"),
        ("Arjun Kapoor",  "arjun@example.com",   "Jaipur",    "2023-09-14"),
        ("Meera Joshi",   "meera@example.com",   "Kolkata",   "2023-10-03"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO customers (name, email, city, signup_date) VALUES (?, ?, ?, ?)",
        customers
    )


def seed_products(cursor):
    products = [
        ("Laptop Pro",         "Electronics", 75000.00),
        ("Wireless Earbuds",   "Electronics",  3999.00),
        ("Mechanical Keyboard","Electronics",  6500.00),
        ("USB-C Hub",          "Electronics",  2200.00),
        ("Smartphone X",       "Electronics", 55000.00),
        ("Running Shoes",      "Footwear",     4500.00),
        ("Casual Sneakers",    "Footwear",     2999.00),
        ("Leather Wallet",     "Accessories",  1200.00),
        ("Backpack 30L",       "Bags",         3500.00),
        ("Water Bottle 1L",    "Lifestyle",     799.00),
        ("Yoga Mat",           "Fitness",      1800.00),
        ("Protein Powder 1kg", "Fitness",      2500.00),
        ("Novel - Bestseller", "Books",         499.00),
        ("Notebook Pack",      "Stationery",    350.00),
        ("Desk Lamp LED",      "Home",         1599.00),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO products (product_name, category, price) VALUES (?, ?, ?)",
        products
    )


def seed_orders(cursor):
    random.seed(42)
    base_date = datetime(2024, 8, 1)
    statuses = ["completed", "completed", "completed", "pending", "cancelled"]

    order_records = []
    for customer_id in range(1, 11):
        num_orders = random.randint(3, 8)
        for _ in range(num_orders):
            days_ago = random.randint(0, 180)
            order_date = (base_date + timedelta(days=days_ago)).strftime("%Y-%m-%d")
            status = random.choice(statuses)
            order_records.append((customer_id, order_date, status))

    cursor.executemany(
        "INSERT INTO orders (customer_id, order_date, status) VALUES (?, ?, ?)",
        order_records
    )


def seed_order_items(cursor):
    random.seed(99)
    cursor.execute("SELECT order_id FROM orders")
    order_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT product_id, price FROM products")
    products = cursor.fetchall()

    item_records = []
    for order_id in order_ids:
        num_items = random.randint(1, 4)
        selected = random.sample(products, min(num_items, len(products)))
        for product_id, price in selected:
            quantity = random.randint(1, 3)
            item_records.append((order_id, product_id, quantity, price))

    cursor.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        item_records
    )


def setup_database():
    print(f"Setting up database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_tables(cursor)
    print("Tables created.")
    seed_customers(cursor)
    print("Customers seeded.")
    seed_products(cursor)
    print("Products seeded.")
    seed_orders(cursor)
    print("Orders seeded.")
    seed_order_items(cursor)
    print("Order items seeded.")

    conn.commit()
    conn.close()
    print("\nDatabase setup complete!")


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        confirm = input("ecommerce.db already exists. Recreate it? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            exit()
        os.remove(DB_PATH)

    setup_database()