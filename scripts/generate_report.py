"""Runs the Soda scan, finds the exact failing rows, and writes an HTML validation report.

Used both from the command line (python scripts/generate_report.py) and by the web UI (app.py).
"""
import html
import json
import sys
from datetime import datetime
from pathlib import Path

import duckdb
from soda.scan import Scan

REPORT_PATH = Path("reports/validation_report.html")

# For every check in checks.yml: (quality dimension, reason a row fails, SQL filter returning the offending rows).
RULES = {
    "row_count > 0": ("Volume", "Dataset is empty", "1=0"),
    "missing_count(order_id) = 0": ("Completeness", "order_id is missing", "order_id IS NULL"),
    "duplicate_count(order_id) = 0": (
        "Uniqueness",
        "order_id appears more than once",
        "order_id IN (SELECT order_id FROM orders GROUP BY order_id HAVING COUNT(*) > 1)",
    ),
    "missing_count(customer_id) = 0": ("Completeness", "customer_id is missing", "customer_id IS NULL"),
    "missing_count(product) = 0": ("Completeness", "product is missing", "product IS NULL"),
    "missing_count(order_date) = 0": ("Completeness", "order_date is missing", "order_date IS NULL"),
    "invalid_count(status) = 0": (
        "Validity",
        "status is not Pending/Shipped/Delivered/Cancelled",
        "status IS NOT NULL AND status NOT IN ('Pending','Shipped','Delivered','Cancelled')",
    ),
    "invalid_count(unit_price) = 0": ("Range", "unit_price is below 0.01", "unit_price < 0.01"),
    "invalid_count(quantity) = 0": ("Range", "quantity is below 1", "quantity < 1"),
}


def run_scan():
    scan = Scan()
    scan.set_data_source_name("ecommerce")
    scan.add_configuration_yaml_file("configuration.yml")
    scan.add_sodacl_yaml_file("checks.yml")
    scan.execute()
    return scan.get_scan_results()["checks"]


def collect():
    """Run Soda, then fetch the exact offending rows for every failed check."""
    checks = run_scan()
    con = duckdb.connect("ecommerce.duckdb", read_only=True)
    try:
        total = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        columns = [c[0] for c in con.execute("SELECT * FROM orders LIMIT 0").description]
        results = []
        for c in checks:
            name = c["name"]
            passed = c["outcome"] == "pass"
            dimension, reason, where = RULES.get(name, ("Other", name, "1=0"))
            bad = [] if passed else con.execute(f"SELECT * FROM orders WHERE {where}").fetchall()
            results.append({
                "name": name,
                "dimension": dimension,
                "reason": reason,
                "passed": passed,
                "count": len(bad),
                "rows": [[None if v is None else str(v) for v in r] for r in bad],
            })
    finally:
        con.close()
    return {"total": total, "columns": columns, "checks": results}


def _table(columns, rows):
    head = "".join(f"<th>{html.escape(c)}</th>" for c in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape('' if v is None else str(v))}</td>" for v in r) + "</tr>"
        for r in rows
    )
    return f"<table><tr>{head}</tr>{body}</table>"


def build_html(data):
    checks = data["checks"]
    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    bad_ids = {r[0] for c in checks for r in c["rows"]}

    summary = "".join(
        f"<tr class='{'pass' if c['passed'] else 'fail'}'><td>{html.escape(c['name'])}</td>"
        f"<td>{html.escape(c['dimension'])}</td><td>{'PASS' if c['passed'] else 'FAIL'}</td><td>{c['count']}</td></tr>"
        for c in checks
    )
    detail = "".join(
        f"<h3>{html.escape(c['name'])} &mdash; {html.escape(c['reason'])} ({c['count']} row(s))</h3>"
        + _table(data["columns"], c["rows"])
        for c in checks if c["rows"]
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Data Quality Report</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;margin:32px;color:#222}}
table{{border-collapse:collapse;margin:8px 0 24px}} td,th{{border:1px solid #ccc;padding:6px 10px;font-size:14px}}
th{{background:#f0f0f0;text-align:left}} .pass td:nth-child(3){{color:#0a7d2c;font-weight:bold}}
.fail td:nth-child(3){{color:#c0192b;font-weight:bold}} .kpi{{font-size:18px;margin:4px 0}}
</style></head><body>
<h1>E-Commerce Data Quality Report</h1>
<p>Generated {datetime.now():%Y-%m-%d %H:%M} | Source: data/orders.csv &rarr; DuckDB &rarr; Soda Core</p>
<div class="kpi">Rows scanned: <b>{data['total']}</b></div>
<div class="kpi">Checks passed: <b>{passed}</b> | failed: <b>{failed}</b></div>
<div class="kpi">Distinct order IDs with at least one problem: <b>{len(bad_ids)}</b></div>
<h2>1. Check summary</h2>
<table><tr><th>Check</th><th>Dimension</th><th>Result</th><th>Offending rows</th></tr>{summary}</table>
<h2>2. Failure analysis (the exact bad records)</h2>{detail or "<p>No failures.</p>"}
<h2>3. Recommended action</h2>
<ul><li>Reject or quarantine the rows above before they reach reports or analytics.</li>
<li>Fix the upstream source that produced them (missing fields, duplicate loads, invalid status codes).</li></ul>
</body></html>"""


def write_report(data):
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(build_html(data), encoding="utf-8")
    return REPORT_PATH


def main():
    data = collect()
    if len(sys.argv) > 2 and sys.argv[1] == "--json-out":
        # Used by app.py: run the scan in its own process so DuckDB's file lock is released afterwards.
        Path(sys.argv[2]).write_text(json.dumps(data), encoding="utf-8")
        return
    out = write_report(data)
    passed = sum(1 for c in data["checks"] if c["passed"])
    failed = len(data["checks"]) - passed
    bad_ids = {r[0] for c in data["checks"] for r in c["rows"]}
    print(f"\nValidation report written to {out}")
    print(f"{passed} passed, {failed} failed; {len(bad_ids)} order IDs affected out of {data['total']} rows")


if __name__ == "__main__":
    main()
