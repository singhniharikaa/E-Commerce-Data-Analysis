# CASE STUDY PRESENTATION — IMPLEMENTATION SLIDE

## E-Commerce Data Quality using Soda

### Problem
E-commerce order data can contain:
- Missing customer/product IDs
- Duplicate orders
- Negative prices
- Invalid quantities
- Invalid order statuses

### Our Implementation
CSV Orders → DuckDB → Soda Core → Automated Quality Checks → Pass/Fail

### Checks Demonstrated
1. Completeness — no missing required fields
2. Uniqueness — order_id must be unique
3. Validity — status must be from an approved list
4. Range — unit_price >= 0.01
5. Range — quantity >= 1

### Demo
Run:
`python scripts/run_demo.py`

### Key Learning
"Data quality is not only about cleaning data; it is about defining measurable rules and automatically validating data before it reaches downstream analytics."

### Why Soda?
Soda Core lets us define data-quality checks in a human-readable YAML contract/check file and execute them against a data source. For this small prototype, everything runs locally; Soda Cloud is not required.
