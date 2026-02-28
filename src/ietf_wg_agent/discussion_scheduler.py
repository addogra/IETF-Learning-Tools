from __future__ import annotations

"""Daily discussion-update scheduler.

Runs discussion-update delivery once or in a 24-hour loop.
"""

import argparse
import time

from ietf_wg_agent.daily import deliver_daily_discussion_updates_emails


def run_once() -> str:
    return deliver_daily_discussion_updates_emails(days=1)


def run_forever(interval_hours: int = 24) -> None:
    interval_seconds = max(1, interval_hours) * 3600
    while True:
        print(run_once())
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run daily discussion-update scheduler")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one cycle only",
    )
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=24,
        help="Loop interval for scheduler mode (default: 24)",
    )
    args = parser.parse_args()

    if args.once:
        print(run_once())
        return

    run_forever(interval_hours=args.interval_hours)


if __name__ == "__main__":
    main()
