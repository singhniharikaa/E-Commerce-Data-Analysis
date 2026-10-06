# Case Study 14 — E-Commerce Data Quality using Soda
## 2-Member Presentation Plan (6 Slides)

**Tech:** Python + Soda Core (+ DuckDB as local database)
**Task (syllabus):** Load dataset → define validation rules → check missing / duplicate / invalid records → generate validation report → analyze failures

---

## Overview Table

| Slide | Topic | Presenter | Kaunsa code / file | Time |
|-------|-------|-----------|--------------------|------|
| 1 | Introduction — E-commerce mein data quality ki dikkat kyu? | **Member 1** | (sirf theory + diagram) | 1.5 min |
| 2 | Dataset banana (Load dataset) | **Member 1** | `scripts/generate_data.py` | 2 min |
| 3 | Database mein load karna + joined view | **Member 1** | `scripts/load_duckdb.py`, `configuration.yml` | 2 min |
| 4 | Validation rules define karna | **Member 2** | `checks.yml` | 2 min |
| 5 | Live demo — scan chalana, report generate | **Member 2** | `scripts/run_demo.py` | 2 min |
| 6 | Failure analysis + conclusion | **Member 2** | Soda output (scan result) | 2 min |

**Handover line (Member 1 → 2):** "Humne data load kar diya aur DB ready hai. Ab ye data sahi hai ya nahi, ye kaise check karte hain — ye Member 2 batayega."

---

# MEMBER 1 — Slides 1, 2, 3

## Slide 1 — Introduction: E-commerce mein data quality ki dikkat

**Slide par likhna (bullets):**
- E-commerce platform pe roz hazaaron orders aate hain
- Har order = customer_id, product, price, quantity, payment mode, status
- Data galat / adhura / duplicate ho toh:
  - Revenue report galat (negative price, duplicate order double count)
  - Delivery fail (missing customer / address)
  - Customer analytics kharab
  - Business decisions galat data pe
- Solution: rules define karo → automatic validation → problem pehle hi pakdo

**Diagram (slide pe):**
`Dirty data → Quality rules → Automated validation (Soda) → Report`

**Kya bolna hai (explain):**
- "E-commerce mein data kai jagah se aata hai — website, app, payment gateway, warehouse. Har jagah galti ho sakti hai."
- Example do: "Agar ek order ka price -65,000 aa gaya toh company ka profit report galat ho jayega. Agar same order_id do baar aaya toh ek order do baar gina jayega."
- "Manually 10 lakh rows check nahi kar sakte, isliye data quality framework use karte hain."
- "Humne Soda Core use kiya kyunki rules YAML mein simple English jaise likhe jaate hain."
- Last line: "Is practical mein hum ek e-commerce dataset banate hain, usme jaan-boojhkar galtiyan daalte hain, aur Soda se unhe pakadte hain."

---

## Slide 2 — Dataset Load / Creation (`generate_data.py`)

**Slide par likhna:**
- 2 tables: `orders` (250 clean + 10 bad = 260 rows), `customers` (60 clean + 4 bad = 64 rows)
- `random.seed(42)` → har baar same data (reproducible)
- Galat rows jaan-boojhkar inject kiye gaye

**Code snippet (slide pe sirf ye dikhao):**
```python
random.seed(42)                      # same data every run

orders.append({
    "order_id":   f"O{i:04d}",
    "customer_id": f"C{random.randint(1, 60):03d}",
    "unit_price": round(base_price * random.uniform(0.90, 1.10)),
    "quantity":   random.randint(1, 5),
    ...
})

bad_rows = [
  {"order_id":"O9001", ..., "unit_price": -65000},   # negative price
  {"order_id":"O9002", ..., "quantity": 0},          # zero quantity
  {"order_id":"O9003", "customer_id": "", ...},      # missing value
  {"order_id":"O9005", ..., "status": "Unknown"},    # invalid status
  {**orders[0], "customer_id": "C050"},              # duplicate order_id
]
```

**Kya bolna hai:**
- "Real company ka data confidential hota hai, isliye hum synthetic data banate hain — 12 products, 10 cities, 5 statuses, 5 payment modes."
- "Pehle 250 clean orders banaye, price me ±10% variation taaki realistic lage."
- "Phir 10 bad rows daale — har ek ek alag type ki problem hai: negative price, zero/negative quantity, missing customer_id, missing product, missing date, invalid status, outlier price 9,99,999, future date 2099, aur duplicate order_id."
- "Customers me bhi 4 bad rows: missing name, missing email, duplicate customer_id C001."
- "Last me `random.shuffle` — taaki bad rows end me ek saath na ho, real data jaisa mix ho."
- Output: `data/orders.csv`, `data/customers.csv`

---

## Slide 3 — Database Loading + Joined View (`load_duckdb.py`)

**Slide par likhna:**
- DuckDB = local, serverless analytical database (koi installation/server nahi)
- CSV → SQL tables: `orders`, `customers`
- Extra: `order_details` view = orders LEFT JOIN customers
- Soda ko DB se `configuration.yml` ke through connect karte hain

**Code snippet:**
```python
con = duckdb.connect("ecommerce.duckdb")

con.execute("""
  CREATE TABLE orders AS
  SELECT * FROM read_csv_auto('data/orders.csv')
""")

con.execute("""
  CREATE VIEW order_details AS
  SELECT o.*, c.name AS customer_name,
         o.unit_price * o.quantity AS total_amount
  FROM orders o LEFT JOIN customers c USING (customer_id)
""")
```
```yaml
# configuration.yml
data_source ecommerce:
  type: duckdb
  database: ecommerce.duckdb
```

**Kya bolna hai:**
- "Soda ko SQL database chahiye scan karne ke liye, isliye CSV ko DuckDB me load kiya. `read_csv_auto` khud column types detect kar leta hai."
- "Maine ek view `order_details` bhi banaya jo orders ko customers se join karta hai aur `total_amount = price × quantity` nikalta hai. Isse cross-table checks possible hote hain, jaise order me aisa customer_id jo customers table me hi nahi hai (LEFT JOIN me customer_name NULL aayega)."
- "`configuration.yml` Soda ko batata hai ki kaunsa database use karna hai. Ab Member 2 batayega ki Soda is database pe kaunse rules chalata hai."

---

# MEMBER 2 — Slides 4, 5, 6

## Slide 4 — Validation Rules (`checks.yml`)

**Slide par likhna:**
- Soda rules = YAML file, SodaCL language, padhne me easy
- Total **17 checks** (orders: 12, customers: 5)
- 5 quality dimensions:

| Dimension | Rule | Example |
|-----------|------|---------|
| Volume | `row_count between 200 and 300` | table khali/truncated toh nahi |
| Completeness | `missing_count(customer_id) = 0` | blank nahi hona chahiye |
| Uniqueness | `duplicate_count(order_id) = 0` | ID repeat nahi |
| Validity | `invalid_count(status) = 0` + valid values list | sirf approved status |
| Range | `valid min: 0.01`, `valid max: 500000` | negative / outlier price nahi |

**Code snippet:**
```yaml
checks for orders:
  - row_count between 200 and 300
  - missing_count(customer_id) = 0
  - duplicate_count(order_id) = 0
  - invalid_count(status) = 0:
      valid values: ["Pending","Shipped","Delivered","Cancelled","Returned"]
  - invalid_count(unit_price) = 0:
      valid min: 0.01
```

**Kya bolna hai:**
- "Ab data load ho gaya, ab hum rules define karte hain — ye hi syllabus ka 'define validation rules' step hai."
- "Har rule ek condition hai. `missing_count(customer_id) = 0` ka matlab: customer_id blank wali rows ki ginti zero honi chahiye, warna fail."
- "Rules business logic se aate hain: price kabhi negative nahi ho sakta, quantity kam se kam 1, status sirf 5 allowed values me se."
- "Sabse badi baat: ye YAML hai, toh business team ya non-programmer bhi rules padh aur badal sakta hai."

---

## Slide 5 — Live Demo: Scan chalana aur Report (`run_demo.py`)

**Slide par likhna:**
- Ek hi command: `python scripts/run_demo.py`
- 4 steps automatically:

| Step | Kya hota hai | Output |
|------|--------------|--------|
| 1 | Data generate | `Generated 260 orders` |
| 2 | DuckDB me load | `Loaded 260 rows → orders` |
| 3 | Soda connection test | `Connection OK` |
| 4 | 17 checks ka scan | PASS / FAIL har check ka |

**Code snippet:**
```python
subprocess.run(["soda", "scan",
                "-d", "ecommerce",
                "-c", "configuration.yml",
                "checks.yml"])
```

**Kya bolna hai:**
- "Ye script poori pipeline automate karti hai. Last step me `soda scan` configuration aur checks.yml leke har rule database pe SQL query ki tarah chalata hai."
- "Terminal me har check ke saamne PASS ya FAIL aata hai, aur kitni rows fail hui ye bhi. Yehi humari validation report hai."
- Demo me output dikhao, phir bolo: "Dekhiye, kuch checks fail hue, ye intentional hai."
- (Backup: demo fail ho jaye toh pehle se liya hua terminal screenshot slide me rakho.)

---

## Slide 6 — Failure Analysis + Conclusion

**Slide par likhna:**

| Injected problem | Table | Kaunsa rule pakda |
|------------------|-------|-------------------|
| Duplicate order_id | orders | `duplicate_count(order_id)` |
| Missing customer_id / product / order_date | orders | `missing_count(...)` |
| Status = "Unknown" | orders | `invalid_count(status)` |
| Price −65,000 | orders | `unit_price valid min` |
| Price 9,99,999 | orders | `unit_price valid max` |
| Quantity 0 / −3 | orders | `quantity valid min` |
| Missing name / email | customers | `missing_count(name/email)` |
| Duplicate customer_id C001 | customers | `duplicate_count(customer_id)` |

**Limitations (honestly bolo, marks milte hain):**
- Future dates (2099) abhi kisi rule se nahi pakde gaye → future me date-range check add karenge
- Orders ka customer_id jo customers table me nahi hai (referential integrity) abhi check nahi hota

**Takeaways:**
1. Data quality = measurable rules + automation, manual inspection nahi
2. Soda ka YAML sab ke liye readable hai
3. DuckDB + Soda = zero infrastructure
4. CI/CD pipeline me daal sakte hain taaki bad data production tak na pahunche
5. Failed check batata hai kaunsa column, kaunsa rule, kitni rows

**Kya bolna hai:**
- "Failure analysis ka matlab: har fail hue check ko dekhna aur samajhna ki data me kya galat hai aur kyu."
- "Real life me yahan se kaam aage jata hai: galat rows ko quarantine karna, source system ko fix karna, ya pipeline rok dena."
- Closing: *"Data quality cleaning ka kaam nahi, rules define karke problem ko pehle hi pakadna hai."*

---

## Possible Viva Questions (dono ke liye)

| Question | Short answer |
|----------|--------------|
| Data quality kya hai? | Data ka accurate, complete, consistent, valid aur unique hona |
| Soda aur Great Expectations me fark? | Soda: YAML (SodaCL) rules, SQL pe chalta hai. GE: Python code me "expectations". Dono ka kaam same hai |
| DuckDB kyu? | Local, serverless, setup zero, CSV directly read karta hai |
| Synthetic data kyu? | Real data confidential hota hai, aur humein controlled errors chahiye the |
| Checks fail kyu hue, kya ye error hai? | Nahi, jaan-boojhkar bad rows daali gayi thi detection dikhane ke liye |
| Production me kaise use hoga? | Airflow / CI-CD me scheduled scan, fail pe alert ya pipeline stop |
