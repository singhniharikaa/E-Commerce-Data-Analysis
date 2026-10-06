import subprocess
import sys

print("="*60)
print("E-COMMERCE DATA QUALITY DEMO")
print("="*60)

subprocess.run([sys.executable, "scripts/generate_data.py"], check=True)
subprocess.run([sys.executable, "scripts/load_duckdb.py"], check=True)

print("\nRunning Soda data quality checks...\n")
result = subprocess.run([
    "soda", "scan",
    "-d", "ecommerce",
    "-c", "configuration.yml",
    "checks.yml"
])

print("\nGenerating validation report...")
subprocess.run([sys.executable, "scripts/generate_report.py"], check=True)
sys.exit(result.returncode)
