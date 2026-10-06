import csv, random
from pathlib import Path

# Generates a small e-commerce order dataset.
# A few deliberately bad records are injected so the data-quality tool has failures to find.
products = [
    ("Laptop","Electronics",65000),
    ("Mouse","Accessories",800),
    ("Keyboard","Accessories",1500),
    ("Headphones","Audio",2200),
    ("Monitor","Electronics",12000),
    ("Webcam","Accessories",1800),
    ("Smartwatch","Wearables",4500),
]
cities = ["Mumbai","Pune","Nashik","Thane","Navi Mumbai"]
statuses = ["Pending","Shipped","Delivered","Cancelled"]

random.seed(42)  # same data on every run, so the demo is repeatable
out = Path("data/orders.csv")
out.parent.mkdir(exist_ok=True)
rows = []
for i in range(1, 101):
    product, category, price = random.choice(products)
    qty = random.randint(1, 3)
    rows.append([
        f"O{i:04d}", f"C{random.randint(1,50):03d}", product, category,
        price, qty, "2026-10-06", random.choice(cities), random.choice(statuses)
    ])

# Inject a few quality problems for demonstration.
rows += [
    ["O9001","C999","Laptop","Electronics",-65000,1,"2026-10-06","Mumbai","Delivered"],
    ["O9002","C998","Mouse","Accessories",800,0,"2026-10-06","Pune","Delivered"],
    ["O9003","","Keyboard","Accessories",1500,1,"2026-10-06","Mumbai","Delivered"],
    ["O9004","C997","","Accessories",900,1,"2026-10-06","Mumbai","Delivered"],
    ["O9005","C996","Monitor","Electronics",12000,1,"2026-10-06","Pune","Unknown"],
    ["O0001","C995","Mouse","Accessories",800,1,"2026-10-06","Pune","Delivered"],
]
# Duplicate an existing order id intentionally.
rows.append(rows[0].copy())

with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["order_id","customer_id","product","category","unit_price","quantity","order_date","city","status"])
    w.writerows(rows)

print(f"Generated {len(rows)} orders at {out}")
