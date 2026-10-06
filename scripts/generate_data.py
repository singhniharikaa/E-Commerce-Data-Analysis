"""
generate_data.py
----------------
Generates synthetic e-commerce datasets for data-quality testing.

Tables produced
    data/customers.csv  — ~60 customer records
    data/orders.csv     — ~250 order records (with intentional quality issues)

A handful of deliberately bad rows are injected so that Soda can
detect real data-quality problems during the demo.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)  # reproducible output

# ── Reference data ──────────────────────────────────────────────

PRODUCTS = [
    ("Laptop",       "Electronics",  65000),
    ("Mouse",        "Accessories",    800),
    ("Keyboard",     "Accessories",   1500),
    ("Headphones",   "Audio",         2200),
    ("Monitor",      "Electronics",  12000),
    ("Webcam",       "Accessories",   1800),
    ("Smartwatch",   "Wearables",     4500),
    ("USB Hub",      "Accessories",    950),
    ("Tablet",       "Electronics",  28000),
    ("Speaker",      "Audio",         3200),
    ("Power Bank",   "Accessories",   1200),
    ("SSD 512 GB",   "Storage",       3500),
]

CITIES = [
    "Mumbai", "Pune", "Delhi", "Bangalore", "Hyderabad",
    "Chennai", "Kolkata", "Jaipur", "Nashik", "Thane",
]

STATUSES       = ["Pending", "Shipped", "Delivered", "Cancelled", "Returned"]
PAYMENT_MODES  = ["UPI", "Credit Card", "Debit Card", "COD", "Net Banking"]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
    "Ananya", "Diya", "Myra", "Sara", "Isha", "Kiara", "Priya",
    "Neha", "Riya", "Kriti", "Pooja", "Simran", "Meera",
]
LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar",
    "Reddy", "Nair", "Joshi", "Mehta",
]

# ── Helpers ─────────────────────────────────────────────────────

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

START_DATE = datetime(2026, 7, 1)
END_DATE   = datetime(2026, 10, 6)
DATE_RANGE = (END_DATE - START_DATE).days


def random_date():
    """Return a random date string between START_DATE and END_DATE."""
    return (START_DATE + timedelta(days=random.randint(0, DATE_RANGE))).strftime("%Y-%m-%d")


def random_email(first, last, cid):
    """Build a plausible email address."""
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com"])
    return f"{first.lower()}.{last.lower()}{cid}@{domain}"


# ── Generate customers.csv ──────────────────────────────────────

NUM_CUSTOMERS = 60
customers = []

for i in range(1, NUM_CUSTOMERS + 1):
    first = random.choice(FIRST_NAMES)
    last  = random.choice(LAST_NAMES)
    customers.append({
        "customer_id":  f"C{i:03d}",
        "name":         f"{first} {last}",
        "email":        random_email(first, last, i),
        "city":         random.choice(CITIES),
        "signup_date":  (START_DATE - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
    })

# Inject bad customer rows
customers.append({"customer_id": "C061", "name": "",        "email": "ghost@test.com",   "city": "Mumbai",  "signup_date": "2026-05-10"})
customers.append({"customer_id": "C062", "name": "Test",    "email": "",                 "city": "Pune",    "signup_date": "2026-06-15"})
customers.append({"customer_id": "C063", "name": "Duplicate","email": "dup@test.com",     "city": "Delhi",   "signup_date": "2099-01-01"})
customers.append({"customer_id": "C001", "name": "Clone",   "email": "clone@test.com",   "city": "Jaipur",  "signup_date": "2026-04-20"})  # duplicate ID

CUST_CSV = DATA_DIR / "customers.csv"
with CUST_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["customer_id", "name", "email", "city", "signup_date"])
    writer.writeheader()
    writer.writerows(customers)

print(f"  ✔ Generated {len(customers)} customers  →  {CUST_CSV}")

# ── Generate orders.csv ─────────────────────────────────────────

NUM_ORDERS = 250
orders = []

for i in range(1, NUM_ORDERS + 1):
    product, category, base_price = random.choice(PRODUCTS)
    # slight price variation (±10 %) to make data more realistic
    price = round(base_price * random.uniform(0.90, 1.10))
    qty   = random.randint(1, 5)

    orders.append({
        "order_id":     f"O{i:04d}",
        "customer_id":  f"C{random.randint(1, NUM_CUSTOMERS):03d}",
        "product":      product,
        "category":     category,
        "unit_price":   price,
        "quantity":     qty,
        "order_date":   random_date(),
        "city":         random.choice(CITIES),
        "payment_mode": random.choice(PAYMENT_MODES),
        "status":       random.choice(STATUSES),
    })

# ── Inject intentional quality problems ─────────────────────────

bad_rows = [
    # negative price
    {"order_id":"O9001","customer_id":"C010","product":"Laptop","category":"Electronics",
     "unit_price":-65000,"quantity":1,"order_date":"2026-09-15","city":"Mumbai",
     "payment_mode":"UPI","status":"Delivered"},
    # zero quantity
    {"order_id":"O9002","customer_id":"C012","product":"Mouse","category":"Accessories",
     "unit_price":800,"quantity":0,"order_date":"2026-09-20","city":"Pune",
     "payment_mode":"COD","status":"Delivered"},
    # missing customer_id
    {"order_id":"O9003","customer_id":"","product":"Keyboard","category":"Accessories",
     "unit_price":1500,"quantity":1,"order_date":"2026-08-10","city":"Delhi",
     "payment_mode":"Credit Card","status":"Shipped"},
    # missing product name
    {"order_id":"O9004","customer_id":"C020","product":"","category":"Accessories",
     "unit_price":900,"quantity":2,"order_date":"2026-08-25","city":"Mumbai",
     "payment_mode":"Debit Card","status":"Delivered"},
    # invalid status
    {"order_id":"O9005","customer_id":"C025","product":"Monitor","category":"Electronics",
     "unit_price":12000,"quantity":1,"order_date":"2026-09-01","city":"Chennai",
     "payment_mode":"Net Banking","status":"Unknown"},
    # missing order_date
    {"order_id":"O9006","customer_id":"C030","product":"Headphones","category":"Audio",
     "unit_price":2200,"quantity":1,"order_date":"","city":"Kolkata",
     "payment_mode":"UPI","status":"Delivered"},
    # negative quantity
    {"order_id":"O9007","customer_id":"C035","product":"Speaker","category":"Audio",
     "unit_price":3200,"quantity":-3,"order_date":"2026-09-18","city":"Bangalore",
     "payment_mode":"COD","status":"Shipped"},
    # unreasonably high price (outlier)
    {"order_id":"O9008","customer_id":"C040","product":"USB Hub","category":"Accessories",
     "unit_price":999999,"quantity":1,"order_date":"2026-10-01","city":"Pune",
     "payment_mode":"Credit Card","status":"Pending"},
    # future date (beyond data window)
    {"order_id":"O9009","customer_id":"C045","product":"Tablet","category":"Electronics",
     "unit_price":28000,"quantity":1,"order_date":"2099-12-31","city":"Hyderabad",
     "payment_mode":"UPI","status":"Delivered"},
    # duplicate order_id (same as first order)
    {**orders[0], "customer_id": "C050"},
]

orders.extend(bad_rows)

# shuffle so bad rows aren't all at the end
random.shuffle(orders)

ORDERS_CSV = DATA_DIR / "orders.csv"
FIELDS = ["order_id","customer_id","product","category","unit_price","quantity",
          "order_date","city","payment_mode","status"]

with ORDERS_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(orders)

print(f"  ✔ Generated {len(orders)} orders     →  {ORDERS_CSV}")
print(f"  ℹ {len(bad_rows)} intentional quality issues injected")
