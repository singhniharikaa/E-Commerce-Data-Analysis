"""
load_duckdb.py
--------------
Loads both CSV files (orders + customers) into a local DuckDB database.
Creates a view that joins the two tables for richer quality checks.
"""

import duckdb
from pathlib import Path

DB_PATH    = Path("ecommerce.duckdb")
ORDERS_CSV = Path("data/orders.csv")
CUST_CSV   = Path("data/customers.csv")

con = duckdb.connect(str(DB_PATH))

# ── Load orders table ───────────────────────────────────────────
con.execute("DROP TABLE IF EXISTS orders")
con.execute(f"""
    CREATE TABLE orders AS
    SELECT * FROM read_csv_auto('{ORDERS_CSV.as_posix()}')
""")
order_count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
print(f"  ✔ Loaded {order_count} rows  →  orders")

# ── Load customers table ───────────────────────────────────────
con.execute("DROP TABLE IF EXISTS customers")
con.execute(f"""
    CREATE TABLE customers AS
    SELECT * FROM read_csv_auto('{CUST_CSV.as_posix()}')
""")
cust_count = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
print(f"  ✔ Loaded {cust_count} rows  →  customers")

# ── Create a joined view for cross-table checks ────────────────
con.execute("DROP VIEW IF EXISTS order_details")
con.execute("""
    CREATE VIEW order_details AS
    SELECT
        o.order_id,
        o.customer_id,
        c.name          AS customer_name,
        c.email         AS customer_email,
        o.product,
        o.category,
        o.unit_price,
        o.quantity,
        o.unit_price * o.quantity  AS total_amount,
        o.order_date,
        o.city          AS order_city,
        c.city          AS customer_city,
        o.payment_mode,
        o.status
    FROM orders o
    LEFT JOIN customers c USING (customer_id)
""")
print(f"  ✔ Created view  →  order_details  (orders ⟕ customers)")

con.close()
print(f"\n  Database ready: {DB_PATH}")
