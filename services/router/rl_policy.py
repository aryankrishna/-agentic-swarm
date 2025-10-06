# services/router/rl_policy.py
import csv, os
from collections import defaultdict

LOG_PATH = os.path.join("data", "logs", "route_log.csv")

def success_rate(decision: str) -> float:
    """Return success rate for 'graph' or 'vector' based on route_log.csv."""
    if not os.path.exists(LOG_PATH):
        return 0.5  # neutral default
    total = wins = 0
    with open(LOG_PATH) as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("decision") == decision:
                total += 1
                # had_answer may be '1'/'0' or 'True'/'False'
                had = str(row.get("had_answer", "0")).strip().lower()
                wins += 1 if had in ("1","true","yes") else 0
    return (wins / total) if total else 0.5

def prefer_order():
    """Return ['graph','vector'] or ['vector','graph'] based on observed success."""
    g = success_rate("graph")
    v = success_rate("vector")
    # tie-break: prefer graph
    return ["graph","vector"] if g >= v else ["vector","graph"]