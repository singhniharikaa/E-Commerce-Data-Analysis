# E-Commerce Data Quality using Soda

## Purpose
An academic implementation of the case study **"E-Commerce Data Quality"**.
The project generates realistic synthetic data with intentional quality issues so that
[Soda Core](https://docs.soda.io/soda-core/overview-main.html) can detect and report
data-quality problems — exactly what a real-world data pipeline would need.

## What it demonstrates

| Dimension | What we check |
|---|---|
| **Completeness** | Missing values in required fields (order_id, customer_id, product, …) |
| **Uniqueness** | Duplicate order IDs, duplicate customer IDs |
| **Validity** | Order status and payment mode from an approved list |
| **Range** | unit_price ≥ 0.01, unit_price ≤ 5,00,000, quantity ≥ 1 |
| **Row count** | orders table has between 200–300 rows |
| **Cross-table** | Joined view (`order_details`) links orders ↔ customers |

## Architecture

```
  Synthetic Data Generator (Python)
            │
   ┌────────┴────────┐
   ▼                 ▼
orders.csv      customers.csv
   └────────┬────────┘
            ▼
     DuckDB (local DB)
        orders table
        customers table
        order_details view
            │
            ▼
       Soda Core Scan
            │
    ┌───────┴───────┐
    ▼               ▼
  PASS            FAIL
```

## Setup

**Prerequisites:** Python 3.10–3.12

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the complete demo

```powershell
python scripts/run_demo.py
```

This single command will:
1. Generate `data/orders.csv` (~260 rows) and `data/customers.csv` (~64 rows)
2. Load both into a local DuckDB database
3. Test the Soda connection
4. Run all data-quality checks and display a PASS / FAIL report

### Run step-by-step

```powershell
python scripts/generate_data.py
python scripts/load_duckdb.py
soda test-connection -d ecommerce -c configuration.yml
soda scan -d ecommerce -c configuration.yml checks.yml --local
```

## Soda Checks Explained

### Orders table

| # | Check | Meaning |
|---|---|---|
| 1 | `row_count between 200 and 300` | Dataset is within expected size |
| 2 | `missing_count(order_id) = 0` | Every order has an ID |
| 3 | `duplicate_count(order_id) = 0` | Order IDs are unique |
| 4 | `missing_count(customer_id) = 0` | Customer ID is required |
| 5 | `missing_count(product) = 0` | Product name is required |
| 6 | `missing_count(order_date) = 0` | Order date is required |
| 7 | `missing_count(payment_mode) = 0` | Payment mode is required |
| 8 | `invalid_count(status) = 0` | Status must be Pending / Shipped / Delivered / Cancelled / Returned |
| 9 | `invalid_count(payment_mode) = 0` | Payment mode from approved list |
| 10 | `invalid_count(unit_price) min` | No negative / zero prices |
| 11 | `invalid_count(unit_price) max` | No unreasonably high prices |
| 12 | `invalid_count(quantity) = 0` | No zero / negative quantities |

### Customers table

| # | Check | Meaning |
|---|---|---|
| 1 | `row_count > 0` | Table is not empty |
| 2 | `missing_count(customer_id) = 0` | Customer ID is required |
| 3 | `missing_count(name) = 0` | Name is required |
| 4 | `missing_count(email) = 0` | Email is required |
| 5 | `duplicate_count(customer_id) = 0` | Customer IDs are unique |

## Expected Result

**Several checks will FAIL.** This is *intentional* — the following problems
are injected by the data generator:

| Problem | Table | What Soda detects |
|---|---|---|
| Negative price (−₹65,000) | orders | `unit_price` below min |
| Unreasonably high price (₹9,99,999) | orders | `unit_price` above max |
| Zero / negative quantity | orders | `quantity` below min |
| Missing customer_id | orders | completeness failure |
| Missing product name | orders | completeness failure |
| Missing order_date | orders | completeness failure |
| Invalid status ("Unknown") | orders | validity failure |
| Duplicate order_id | orders | uniqueness failure |
| Missing customer name | customers | completeness failure |
| Missing email | customers | completeness failure |
| Duplicate customer_id | customers | uniqueness failure |

> **The point of the demo is to show Soda detecting data-quality problems,
> not to clean the data automatically.**

## Case study explanation

> E-commerce platforms depend on trustworthy order data. If prices, quantities,
> customer IDs or order statuses are incorrect, downstream analytics, revenue
> calculations and business decisions become unreliable. We therefore define
> data-quality rules across two tables (orders + customers) and automate their
> validation using Soda Core with a local DuckDB database.

## 3-minute presentation flow

1. **Problem statement** — e-commerce data can contain missing, duplicate, and invalid records.
2. Show `orders.csv` and `customers.csv`; highlight one or two bad rows.
3. Explain the pipeline: CSV → DuckDB → Soda.
4. Open `checks.yml` and walk through 4–5 checks.
5. Run `python scripts/run_demo.py`.
6. Show the PASS / FAIL output.
7. Explain that the failed checks pinpoint exactly what must be cleaned or rejected before downstream analytics.

## Project structure

```
ECommerce_Data_Quality_Soda/
├── configuration.yml          # Soda data-source config (DuckDB)
├── checks.yml                 # Soda quality checks (orders + customers)
├── requirements.txt           # Python dependencies
├── data_dictionary.md         # Column-level documentation
├── case_study_slide_content.md
├── README.md                  # ← you are here
├── data/
│   ├── orders.csv             # ~260 rows (generated)
│   └── customers.csv          # ~64  rows (generated)
└── scripts/
    ├── generate_data.py       # Synthetic data generator
    ├── load_duckdb.py         # CSV → DuckDB loader
    └── run_demo.py            # One-command pipeline runner
```

## Future scope
- Great Expectations as an alternative framework
- PostgreSQL / cloud data source
- Soda Cloud dashboard integration
- Data-quality monitoring in CI/CD pipelines
- Automated quarantine / cleaning of failed rows
- Email / Slack alerts on check failures
