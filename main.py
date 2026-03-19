#!/usr/bin/env python3
"""atl-context-scout — Atlanta vibe report CLI.

Usage:
    python main.py
    python main.py --location "Atlanta, GA"
    python main.py --location "Midtown Atlanta" --no-personalize
    python main.py --output report.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent))

from src.config import load_config
from src.brave_client import search_news, search_weather, search_events
from src.notion_vault import get_phone_number
from src.report import build_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a personalized Atlanta context report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--location",
        default=None,
        help="City or area to report on (default: value from .env or 'Atlanta, GA').",
    )
    parser.add_argument(
        "--no-personalize",
        action="store_true",
        help="Skip Notion vault lookup — omit phone number from report.",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write report to FILE instead of stdout.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        config = load_config()
    except EnvironmentError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    location = args.location or config.default_location

    print(f"[atl-context-scout] Fetching context for: {location}", file=sys.stderr)

    # --- Brave searches ---
    print("[atl-context-scout] Running Brave searches...", file=sys.stderr)
    news = search_news(config.brave_api_key, location)
    weather = search_weather(config.brave_api_key, location)
    events = search_events(config.brave_api_key, location)

    # --- Notion vault ---
    phone = ""
    if not args.no_personalize:
        try:
            print("[atl-context-scout] Reading Notion vault...", file=sys.stderr)
            phone = get_phone_number(config.notion_token, config.notion_vault_page_id)
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] Could not read Notion vault: {exc}", file=sys.stderr)

    # --- Build report ---
    report = build_report(location, news, weather, events, phone)

    # --- Output ---
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"[atl-context-scout] Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
