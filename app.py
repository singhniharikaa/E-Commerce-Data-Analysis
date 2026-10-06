"""Local web UI that walks through the pipeline step by step.

    python app.py      ->  http://localhost:8765

Uses only the standard library plus the packages already in requirements.txt.
"""
import csv
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "scripts"))

import duckdb  # noqa: E402
import generate_report  # noqa: E402

PORT = 8765
LOCK = threading.Lock()  # steps touch the same DuckDB file, so run them one at a time
LAST_SCAN = {}


def run_script(path, *args):
    result = subprocess.run(
        [sys.executable, path, *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"{path} failed")


def step_generate():
    run_script("scripts/generate_data.py")
    with open("data/orders.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    LAST_SCAN.clear()
    return {"columns": rows[0], "rows": rows[1:], "count": len(rows) - 1}


def step_load():
    run_script("scripts/load_duckdb.py")
    con = duckdb.connect("ecommerce.duckdb", read_only=True)
    try:
        count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        schema = [[r[0], r[1]] for r in con.execute("DESCRIBE orders").fetchall()]
    finally:
        con.close()
    return {"count": count, "schema": schema}


def step_rules():
    return {
        "yaml": Path("checks.yml").read_text(encoding="utf-8"),
        "rules": [
            {"name": n, "dimension": d, "reason": r} for n, (d, r, _) in generate_report.RULES.items()
        ],
    }


def step_scan():
    scan_json = ROOT / "reports" / "_scan.json"
    scan_json.parent.mkdir(exist_ok=True)
    run_script("scripts/generate_report.py", "--json-out", str(scan_json))
    data = json.loads(scan_json.read_text(encoding="utf-8"))
    scan_json.unlink()
    flagged = {}
    for c in data["checks"]:
        for row in c["rows"]:
            flagged.setdefault(row[0], [])
            if c["reason"] not in flagged[row[0]]:
                flagged[row[0]].append(c["reason"])
    data["flagged"] = flagged
    LAST_SCAN.clear()
    LAST_SCAN.update(data)
    return data


def step_report():
    data = LAST_SCAN or step_scan()
    generate_report.write_report(data)
    return {"url": "/report"}


ROUTES = {
    "/api/generate": step_generate,
    "/api/load": step_load,
    "/api/rules": step_rules,
    "/api/scan": step_scan,
    "/api/report": step_report,
}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, payload):
        self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._send(200, Path("ui/index.html").read_bytes(), "text/html; charset=utf-8")
        elif path == "/report" and generate_report.REPORT_PATH.exists():
            self._send(200, generate_report.REPORT_PATH.read_bytes(), "text/html; charset=utf-8")
        else:
            self._send(404, b"Not found", "text/plain")

    def do_POST(self):
        step = ROUTES.get(self.path)
        if step is None:
            return self._json(404, {"error": "unknown step"})
        try:
            with LOCK:
                self._json(200, step())
        except Exception as exc:  # surface the real error in the UI instead of a blank failure
            self._json(500, {"error": str(exc)})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Pipeline UI running at http://localhost:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
