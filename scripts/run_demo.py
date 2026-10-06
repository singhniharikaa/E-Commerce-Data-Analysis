"""
run_demo.py
-----------
One-command entry point that runs the full pipeline:
    1. Generate synthetic CSV data (orders + customers)
    2. Load CSVs into DuckDB
    3. Test database connection via Soda
    4. Run all Soda data-quality checks
"""

import subprocess
import sys
import time

DIVIDER = "─" * 60

def heading(text):
    """Print a section heading."""
    print(f"\n{DIVIDER}")
    print(f"  {text}")
    print(DIVIDER)

def run(cmd, label):
    """Run a subprocess and measure its execution time."""
    start = time.time()
    result = subprocess.run(cmd, check=True)
    elapsed = time.time() - start
    print(f"  ⏱  {label} completed in {elapsed:.1f}s")
    return result

# ── Banner ──────────────────────────────────────────────────────

print()
print("╔════════════════════════════════════════════════════════════╗")
print("║     E-COMMERCE DATA QUALITY PIPELINE  —  SODA CORE       ║")
print("╠════════════════════════════════════════════════════════════╣")
print("║  Dataset : orders.csv + customers.csv                    ║")
print("║  Engine  : DuckDB (local, no server)                     ║")
print("║  Checks  : completeness · uniqueness · validity · range  ║")
print("╚════════════════════════════════════════════════════════════╝")

# ── Step 1 : Generate data ──────────────────────────────────────

heading("STEP 1 — Generating synthetic data")
run([sys.executable, "scripts/generate_data.py"], "Data generation")

# ── Step 2 : Load into DuckDB ───────────────────────────────────

heading("STEP 2 — Loading into DuckDB")
run([sys.executable, "scripts/load_duckdb.py"], "DuckDB load")

# ── Step 3 : Test Soda connection ───────────────────────────────

heading("STEP 3 — Testing Soda connection")
subprocess.run([
    "soda", "test-connection",
    "-d", "ecommerce",
    "-c", "configuration.yml",
], check=True)

# ── Step 4 : Run quality checks ─────────────────────────────────

heading("STEP 4 — Running Soda data-quality checks")
result = subprocess.run([
    "soda", "scan",
    "-d", "ecommerce",
    "-c", "configuration.yml",
    "checks.yml",
    "--local",
])

# ── Summary ─────────────────────────────────────────────────────

heading("DONE")
if result.returncode == 0:
    print("  ✅  All checks passed!\n")
else:
    print("  ⚠️   Some checks FAILED (see above).  This is expected —")
    print("      bad records were injected intentionally to demonstrate")
    print("      Soda's data-quality detection capabilities.\n")

sys.exit(result.returncode)
