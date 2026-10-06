import duckdb
from pathlib import Path

db = Path("ecommerce.duckdb")
csv_file = Path("data/orders.csv")

con = duckdb.connect(str(db))
con.execute("DROP TABLE IF EXISTS orders")
con.execute(f'''
    CREATE TABLE orders AS
    SELECT * FROM read_csv_auto('{csv_file.as_posix()}')
''')
count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
print(f"Loaded {count} rows into ecommerce.duckdb -> orders")
con.close()
