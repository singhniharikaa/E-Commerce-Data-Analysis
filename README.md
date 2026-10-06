# E-Commerce Data Quality using Soda

## Purpose
A tiny academic implementation of the case study **E-Commerce Data Quality**.
The project intentionally contains a few bad records so Soda can detect real data-quality problems.

## What it demonstrates
- Completeness: missing values
- Uniqueness: duplicate order IDs
- Validity: allowed order status values
- Range validity: price and quantity
- Basic schema/data-source validation
- Automated data-quality scanning with Soda
- Local execution without Soda Cloud

## Architecture

Synthetic E-Commerce Data
        ↓
CSV Orders
        ↓
DuckDB
        ↓
Soda Core
        ↓
Data Quality Checks
        ↓
PASS / FAIL Report

## Setup

Recommended: Python 3.10–3.12 for this short demo.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `py -3.12` is unavailable, install Python 3.12 first.

## Run the complete demo

```powershell
python scripts/run_demo.py
```

Or run step-by-step:

```powershell
python scripts/generate_data.py
python scripts/load_duckdb.py
soda test-connection -d ecommerce -c configuration.yml
soda scan -d ecommerce -c configuration.yml checks.yml
```

## Pipeline UI (best for presentations)

```powershell
python app.py
```

Open http://localhost:8765. Click through the five stages (Generate data, Load into DuckDB, Define rules, Run Soda scan, Validation report), or use **Run full pipeline**. Failed checks expand to show the exact bad rows, and the report opens in a new tab.

`python scripts/run_demo.py` still runs the same pipeline in the terminal and writes `reports/validation_report.html`.

## What the checks mean

| Check | Meaning |
|---|---|
| row_count > 0 | Dataset is not empty |
| missing_count(order_id) = 0 | Every order has an ID |
| duplicate_count(order_id) = 0 | Order IDs are unique |
| missing_count(customer_id) = 0 | Customer ID is required |
| missing_count(product) = 0 | Product is required |
| missing_count(order_date) = 0 | Order date is required |
| valid status values | Status must be Pending/Shipped/Delivered/Cancelled |
| unit_price >= 0.01 | No negative/zero price |
| quantity >= 1 | No invalid quantities |

## Expected result

Some checks should FAIL because bad records are intentionally injected.

Example problems:
- negative product price
- zero/negative quantity
- missing customer ID
- missing product
- missing order date
- invalid order status
- duplicate order ID

This is intentional: **the point of the demo is to show Soda detecting data-quality problems.**

## Case study explanation

The case study can be presented as:

> E-commerce platforms depend on trustworthy order data. If prices, quantities, customer IDs or order statuses are incorrect, downstream analytics, revenue calculations and business decisions can become unreliable. We therefore define data-quality rules and automate their validation using Soda.

## 3-minute presentation flow

1. Show the problem: e-commerce data can contain missing, duplicate and invalid records.
2. Show `orders.csv` and highlight one or two bad rows.
3. Explain the pipeline: CSV → DuckDB → Soda.
4. Open `checks.yml` and explain 4–5 checks.
5. Run `python scripts/run_demo.py`.
6. Show PASS/FAIL output.
7. Explain that the failed checks identify exactly what must be cleaned or rejected before downstream analytics.

## Important
Do not claim that the project cleans the data automatically. This version **detects and reports** quality issues. That is enough for the case-study implementation.

## Future scope
- Great Expectations implementation
- PostgreSQL data source
- Soda Cloud dashboard
- Data-quality monitoring in CI/CD
- Automated quarantine/cleaning of failed rows
