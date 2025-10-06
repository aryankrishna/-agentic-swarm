import os
import json
import random
import pandas as pd

LOG_PATH = "data/logs/route_log.csv"
MODEL_PATH = "data/models/router_bandit.json"


class EpsGreedyBandit:
    """
    Simple epsilon-greedy multi-armed bandit to pick best tool.
    Arms = ["vector", "graph", "math"]
    Reward = had_answer - latency_ms * 0.001 (so faster = better)
    """

    def __init__(self, arms=None, epsilon=0.2):
        self.arms = arms or ["vector", "graph", "math"]
        self.epsilon = epsilon
        self.counts = {a: 1 for a in self.arms}
        self.values = {a: 0.0 for a in self.arms}
        # try to load existing model so learning persists
        self._load()

    def _load(self):
        if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 0:
            try:
                d = json.loads(open(MODEL_PATH, "r").read())
                self.counts.update(d.get("counts", {}))
                self.values.update(d.get("values", {}))
                self.epsilon = d.get("epsilon", self.epsilon)
            except Exception:
                pass

    def _save(self):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "w") as f:
            json.dump(
                {"counts": self.counts, "values": self.values, "epsilon": self.epsilon},
                f,
                indent=2,
            )

    def select(self) -> str:
        # explore
        if random.random() < self.epsilon:
            return random.choice(self.arms)
        # exploit
        return max(self.arms, key=lambda a: self.values.get(a, 0.0))

    def update(self, arm: str, reward: float):
        if arm not in self.arms:
            return
        self.counts[arm] += 1
        n = self.counts[arm]
        old = self.values[arm]
        self.values[arm] = old + (reward - old) / n  # incremental mean
        self._save()


def reward_from_row(row) -> float:
    """+1 for answer, minus small latency penalty (ms → seconds * 0.001)."""
    base = 1.0 if int(row.get("had_answer", 0)) else 0.0
    lat = float(row.get("latency_ms", 0))
    return max(-1.0, min(1.0, base - 0.001 * lat))


def offline_learn_from_csv(path: str = LOG_PATH) -> EpsGreedyBandit:
    """Warm-start from existing logs (safe to call at app startup)."""
    b = EpsGreedyBandit()
    if not os.path.exists(path):
        return b
    try:
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            a = str(row.get("decision", "")).lower()
            if a not in b.arms:
                continue
            b.update(a, reward_from_row(row))
    except Exception:
        pass
    return b