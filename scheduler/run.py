#!/usr/bin/env python3
"""Randomised daily commit scheduler.

Run this every ~20 minutes (see .github/workflows/auto-commit.yml). Each run:

1. Plans today's commits in IST: 2 or 3 of them, at random times between
   09:00 and 21:30, at least an hour apart. The plan is derived from the date,
   so every run on the same day sees the same plan.
2. Checks how many planned times have already passed and how many commits
   were already made today (recorded in scheduler/progress.json).
3. If a planned time has passed without its commit, applies the next step from
   scheduler/queue/ and commits it. One commit per run at most.

A queue step is a folder: ``NNN-slug/message.txt`` (the commit message) and
``NNN-slug/files/`` (a tree copied over the repository root). When the queue is
empty the scheduler does nothing -- it never makes filler commits.

Usage:
    python scheduler/run.py              # decide and commit locally
    python scheduler/run.py --push       # ...and push
    python scheduler/run.py --plan       # just print today's plan
    python scheduler/run.py --dry-run    # say what would happen, change nothing
    python scheduler/run.py --force      # commit the next step now, ignoring the plan
    python scheduler/run.py --now 2026-10-19T14:05   # pretend it is this IST time
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

IST = timezone(timedelta(hours=5, minutes=30))

ROOT = Path(__file__).resolve().parent.parent
QUEUE_DIR = ROOT / "scheduler" / "queue"
PROGRESS_FILE = ROOT / "scheduler" / "progress.json"

COMMITS_PER_DAY = (2, 3)
WINDOW_START = 9 * 60          # 09:00 IST, minutes after midnight
WINDOW_END = 21 * 60 + 30      # 21:30 IST; leaves room for runner delays before 22:00
MIN_GAP = 60                   # minutes between planned commits
DEFAULT_SALT = "fraud-rules-lab"


def plan_day(day: date, salt: str = DEFAULT_SALT) -> List[int]:
    """Planned commit times for ``day`` as sorted minutes after midnight IST."""
    rng = random.Random(f"{salt}:{day.isoformat()}")
    count = rng.randint(*COMMITS_PER_DAY)
    for _ in range(1000):
        slots = sorted(rng.randrange(WINDOW_START, WINDOW_END) for _ in range(count))
        if all(b - a >= MIN_GAP for a, b in zip(slots, slots[1:])):
            return slots
    spacing = (WINDOW_END - WINDOW_START) // count
    return [WINDOW_START + i * spacing for i in range(count)]


def fmt(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"done": []}


def next_step(progress: dict) -> Optional[Path]:
    done = {entry["id"] for entry in progress["done"]}
    if not QUEUE_DIR.exists():
        return None
    for path in sorted(p for p in QUEUE_DIR.iterdir() if p.is_dir()):
        if path.name not in done and (path / "message.txt").exists():
            return path
    return None


def git(*args: str) -> None:
    subprocess.run(["git", *args], cwd=ROOT, check=True)


def apply_step(step: Path, now: datetime, progress: dict, push: bool) -> None:
    files = step / "files"
    if files.exists():
        shutil.copytree(files, ROOT, dirs_exist_ok=True)
    progress["done"].append(
        {"id": step.name, "date": now.date().isoformat(), "time": now.strftime("%H:%M")}
    )
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2) + "\n")

    message = (step / "message.txt").read_text().strip()
    git("add", "-A")
    git("commit", "-m", message)
    if push:
        git("push")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--push", action="store_true", help="git push after committing")
    parser.add_argument("--plan", action="store_true", help="print today's plan and exit")
    parser.add_argument("--dry-run", action="store_true", help="decide but change nothing")
    parser.add_argument("--force", action="store_true", help="ignore the plan and commit the next step now")
    parser.add_argument("--now", help="pretend the current IST time is this ISO timestamp")
    parser.add_argument("--salt", default=DEFAULT_SALT, help="seed salt for the daily plan")
    args = parser.parse_args()

    now = datetime.fromisoformat(args.now).replace(tzinfo=IST) if args.now else datetime.now(IST)
    today = now.date().isoformat()
    slots = plan_day(now.date(), args.salt)
    now_min = now.hour * 60 + now.minute

    print(f"[{now:%Y-%m-%d %H:%M} IST] plan for today: {', '.join(fmt(s) for s in slots)}")
    if args.plan:
        return 0

    progress = load_progress()
    done_today = sum(1 for e in progress["done"] if e["date"] == today)
    due = sum(1 for s in slots if s <= now_min)
    print(f"planned times passed: {due}, commits already made today: {done_today}")

    if not args.force and done_today >= due:
        print("nothing due right now")
        return 0

    step = next_step(progress)
    if step is None:
        print("queue is empty -- add more steps under scheduler/queue/ (no filler commits are made)")
        return 0

    if args.dry_run:
        print(f"would commit: {step.name}: {(step / 'message.txt').read_text().strip()}")
        return 0

    apply_step(step, now, progress, args.push)
    print(f"committed {step.name}" + (" and pushed" if args.push else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
