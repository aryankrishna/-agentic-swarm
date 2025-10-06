# services/router/logger.py
import csv
import os
from datetime import datetime

LOG_DIR = os.path.join("data", "logs")
LOG_PATH = os.path.join(LOG_DIR, "route_log.csv")

FIELDS = ["ts", "question", "rewritten", "decision", "had_answer", "latency_ms"]

def _ensure_header():
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(LOG_PATH) or os.path.getsize(LOG_PATH) == 0:
        with open(LOG_PATH, "w", newline="") as f:
            csv.writer(f).writerow(FIELDS)

def log_route(question: str, decision: str, had_answer: int, latency_ms: int, rewritten: str = ""):
    _ensure_header()
    ts = datetime.utcnow().isoformat()
    with open(LOG_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writerow({
            "ts": ts,
            "question": question,
            "rewritten": rewritten or "",
            "decision": decision,
            "had_answer": had_answer,
            "latency_ms": latency_ms,
        })