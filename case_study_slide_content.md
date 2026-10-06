# PRACTICAL CASE STUDY — 6 SLIDES

## Case Study 14: E-Commerce Data Quality using Soda

> This is the practical implementation section (following the theory).
> We demonstrate how data quality frameworks like Soda Core validate
> real-world e-commerce data and catch issues before they reach downstream analytics.

---

## Slide 1 — Introduction

**Title:** *Why Data Quality Matters in E-Commerce*

- E-commerce platforms process thousands of orders daily
- Each order contains multiple data points — customer ID, product, price, quantity, payment mode, status
- If this data is incorrect, incomplete, or duplicated:
  - Revenue reports become unreliable
  - Deliveries fail
  - Customer analytics break down
  - Business decisions are based on flawed data
- In this case study, we generate a synthetic e-commerce dataset (orders + customers),
  inject intentional quality issues, and use **Soda Core** to automatically detect rule violations

```
  Real-World Problem (dirty data)
              ↓
  Define Quality Rules
              ↓
  Automate Validation (Soda Core)
              ↓
  Catch Issues Before They Cause Damage
```

---

## Slide 2 — Problem Statement & Quality Dimensions

**Title:** *What Data Problems Are We Checking?*

We validate data across 5 core quality dimensions:

| # | Dimension        | What We Check                              | Example from Our Data             |
|---|------------------|--------------------------------------------|-----------------------------------|
| 1 | **Completeness** | Are all required fields filled?            | customer_id is blank in an order  |
| 2 | **Uniqueness**   | Are there duplicate records?               | Same order_id appears twice       |
| 3 | **Validity**     | Are values from an approved list?          | Status = "Unknown" (not allowed)  |
| 4 | **Range**        | Are numbers within expected bounds?        | Price = −₹65,000 (negative)      |
| 5 | **Volume**       | Is the row count within expected range?    | Expected 200–300 orders           |

**Real-world impact:** A negative price in a revenue report corrupts profit calculations.
A duplicate order_id means the same order is counted twice.

---

## Slide 3 — Tools & Architecture

**Title:** *Tech Stack & Pipeline*

| Layer              | Tool                          | Purpose                                      |
|--------------------|-------------------------------|----------------------------------------------|
| Data Generation    | **Python** (csv, random)      | Generate realistic synthetic data             |
| Database           | **DuckDB** (local, serverless)| Lightweight analytical database — no server needed |
| Quality Validation | **Soda Core** (YAML-based)    | Human-readable validation rules               |

**Pipeline (single command: `python scripts/run_demo.py`):**

```
  generate_data.py    →  orders.csv (260 rows) + customers.csv (64 rows)
          ↓
  load_duckdb.py      →  DuckDB database (orders + customers + order_details view)
          ↓
  Soda test-connection →  Connection verified ✓
          ↓
  Soda scan           →  PASS / FAIL report for every rule
```

---

## Slide 4 — Data Model & Quality Rules

**Title:** *Our Data & The Rules We Defined*

**Tables:**

| Table / View       | Rows  | Key Columns                                                    |
|--------------------|-------|----------------------------------------------------------------|
| `orders`           | ~260  | order_id, customer_id, product, unit_price, quantity, status   |
| `customers`        | ~64   | customer_id, name, email, city, signup_date                    |
| `order_details`    | view  | Joined view with computed `total_amount = price × quantity`    |

**Quality checks defined in `checks.yml` (17 total):**

| Check Type          | Orders Table                                              | Customers Table                |
|---------------------|-----------------------------------------------------------|-------------------------------|
| Row count           | `row_count between 200 and 300`                           | `row_count > 0`               |
| No missing values   | order_id, customer_id, product, order_date, payment_mode  | customer_id, name, email      |
| No duplicates       | `duplicate_count(order_id) = 0`                           | `duplicate_count(customer_id) = 0` |
| Valid values only   | status ∈ {Pending, Shipped, Delivered, Cancelled, Returned} | —                           |
| Range               | price ≥ ₹0.01, price ≤ ₹5,00,000; quantity ≥ 1           | —                            |

**Sample from `checks.yml`:**
```yaml
checks for orders:
  - row_count between 200 and 300
  - missing_count(order_id) = 0
  - duplicate_count(order_id) = 0
  - invalid_count(status) = 0:
      valid values: ["Pending", "Shipped", "Delivered", "Cancelled", "Returned"]
  - invalid_count(unit_price) = 0:
      valid min: 0.01
```

---

## Slide 5 — Live Demo

**Title:** *Running the Pipeline*

**Command:**
```powershell
python scripts/run_demo.py
```

**Steps executed automatically:**

| Step | Action                              | Expected Output                       |
|------|-------------------------------------|---------------------------------------|
| 1    | Generate synthetic data             | `✔ Generated 260 orders`              |
| 2    | Load CSVs into DuckDB              | `✔ Loaded 260 rows → orders`          |
| 3    | Test Soda connection                | `Connection OK ✓`                     |
| 4    | Run all 17 Soda quality checks      | PASS ✓ / FAIL ✗ per check             |

**What to observe:**
- Green checks = data quality rule passed
- Red checks = rule failed — bad data detected
- Soda reports exactly which column, which rule, and how many rows failed

---

## Slide 6 — Results & Conclusion

**Title:** *Findings & Key Takeaways*

**Result:** Multiple checks FAIL — this is intentional. The following problems were injected:

| Injected Problem              | Table     | What Soda Detected              |
|-------------------------------|-----------|---------------------------------|
| Negative price (−₹65,000)    | orders    | `unit_price` below minimum      |
| Price ₹9,99,999 (outlier)    | orders    | `unit_price` above maximum      |
| Zero / negative quantity      | orders    | `quantity` below minimum         |
| Missing customer_id           | orders    | Completeness failure             |
| Missing product name          | orders    | Completeness failure             |
| Missing order_date            | orders    | Completeness failure             |
| Invalid status ("Unknown")   | orders    | Validity failure                 |
| Duplicate order_id            | orders    | Uniqueness failure               |
| Missing name / email          | customers | Completeness failure             |
| Duplicate customer_id         | customers | Uniqueness failure               |

**Key Takeaways:**
1. Data quality is about defining measurable rules and automating validation — not manual inspection
2. Soda Core uses human-readable YAML — accessible to both technical and non-technical stakeholders
3. DuckDB + Soda = zero infrastructure cost (no cloud, no server required)
4. This approach integrates into production CI/CD pipelines for continuous monitoring
5. Failed checks pinpoint exactly what needs to be fixed — no guesswork

> *"Data quality is not about cleaning data after the fact — it's about defining
> measurable rules and catching problems before they reach downstream analytics."*
