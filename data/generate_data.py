#!/usr/bin/env python3
"""Генерация тестового набора данных для ML-анализа доступа к Smart-карте (stdlib)."""
import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate(n_normal: int = 400, n_attack: int = 100, seed: int = 216) -> list[dict]:
    rng = random.Random(seed)
    base_time = datetime(2025, 5, 1, 9, 0, 0)
    rows = []

    for i in range(n_normal):
        ts = base_time + timedelta(minutes=rng.randint(0, 500))
        rows.append(
            {
                "session_id": f"sess-n-{i:04d}",
                "card_id": f"SC-{rng.randint(10000, 19999)}",
                "timestamp": ts.isoformat(),
                "failed_pin_count": rng.randint(0, 1),
                "requests_per_min": rng.randint(1, 14),
                "access_granted": 1,
                "label": "normal",
            }
        )

    for i in range(n_attack):
        ts = base_time + timedelta(minutes=rng.randint(0, 500))
        rows.append(
            {
                "session_id": f"sess-a-{i:04d}",
                "card_id": f"SC-{rng.randint(20000, 29999)}",
                "timestamp": ts.isoformat(),
                "failed_pin_count": rng.randint(3, 7),
                "requests_per_min": rng.randint(35, 89),
                "access_granted": 0,
                "label": "attack",
            }
        )

    rng.shuffle(rows)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="testdata.csv")
    parser.add_argument("--normal", type=int, default=400)
    parser.add_argument("--attack", type=int, default=100)
    args = parser.parse_args()

    out = Path(__file__).resolve().parent / args.output
    rows = generate(args.normal, args.attack)
    fieldnames = list(rows[0].keys())
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    normal = sum(1 for r in rows if r["label"] == "normal")
    attack = sum(1 for r in rows if r["label"] == "attack")
    print(f"Generated {len(rows)} rows -> {out}")
    print(f"normal: {normal}, attack: {attack}")


if __name__ == "__main__":
    main()
