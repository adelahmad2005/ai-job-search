#!/usr/bin/env python3
"""Deadline and graduate-programme warnings.

Reads job_scraper/grad_programmes.csv and job_search_tracker.csv and prints
what needs action now:
  - programmes or drafted applications closing within 7 days (or already past)
  - programmes whose opening date has arrived
  - open programmes not yet applied to
  - watch-list entries not re-checked for 7+ days

Usage:
  python tools/deadlines.py [--today YYYY-MM-DD] [--days 7] [--json]
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRAMMES = ROOT / "job_scraper" / "grad_programmes.csv"
TRACKER = ROOT / "job_search_tracker.csv"

WAITING = {"not_open", "register_interest", "watch"}
FINAL_TRACKER = {"rejected", "withdrawn", "no_response", "offer_declined", "accepted", "offer_accepted"}


def parse_date(s: str | None) -> date | None:
    try:
        return date.fromisoformat((s or "").strip())
    except ValueError:
        return None


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def collect(today: date, days: int) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {"urgent": [], "past": [], "opened": [], "apply": [], "recheck": []}
    horizon = today + timedelta(days=days)

    for p in read_csv(PROGRAMMES):
        status = (p.get("status") or "").strip()
        name = f"{p.get('company')} - {p.get('programme')}"
        closes, opens, checked = parse_date(p.get("closes")), parse_date(p.get("opens")), parse_date(p.get("last_checked"))
        item = {"name": name, "url": p.get("url", ""), "status": status, "notes": p.get("notes", "")}

        if status in ("applied", "closed"):
            continue
        if closes and closes < today:
            out["past"].append({**item, "when": closes.isoformat()})
        elif closes and closes <= horizon:
            out["urgent"].append({**item, "when": closes.isoformat()})
        elif status in WAITING and opens and opens <= today:
            out["opened"].append({**item, "when": opens.isoformat()})
        elif status == "open":
            out["apply"].append({**item, "when": p.get("closes") or "rolling"})

        if status in WAITING and (checked is None or (today - checked).days >= days):
            out["recheck"].append({**item, "when": checked.isoformat() if checked else "never"})

    for r in read_csv(TRACKER):
        status = (r.get("status") or "").strip()
        deadline = parse_date(r.get("deadline"))
        # Only unsent applications can still miss their deadline.
        if status != "drafted" or deadline is None or status in FINAL_TRACKER:
            continue
        item = {"name": f"{r.get('company')} - {r.get('role')} (drafted, not submitted)", "url": "", "status": status, "notes": ""}
        if deadline < today:
            out["past"].append({**item, "when": deadline.isoformat()})
        elif deadline <= horizon:
            out["urgent"].append({**item, "when": deadline.isoformat()})
    return out


LABELS = {
    "urgent": "CLOSING SOON",
    "past": "DEADLINE PASSED",
    "opened": "SHOULD BE OPEN NOW - check and apply",
    "apply": "OPEN, NOT APPLIED",
    "recheck": "RE-CHECK (not verified recently)",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    ap.add_argument("--days", type=int, default=7, help="warning window in days (default 7)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    today = parse_date(args.today) if args.today else date.today()
    if today is None:
        print(f"invalid --today {args.today!r}", file=sys.stderr)
        return 1
    res = collect(today, args.days)

    if args.json:
        sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps({"today": today.isoformat(), **res}, indent=2, ensure_ascii=False))
        return 0

    sys.stdout.reconfigure(encoding="utf-8")
    if not any(res.values()):
        print(f"No deadline actions as of {today.isoformat()}.")
        return 0
    for key, label in LABELS.items():
        if res[key]:
            print(f"\n{label}")
            for i in res[key]:
                print(f"  - {i['name']} [{i['when']}] {i['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
