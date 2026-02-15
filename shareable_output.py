#!/usr/bin/env python3
"""
Produce two outputs from yc_ai_assistant_companies.json:
  1) Your shortlist (console) – for your own use.
  2) A "Copy for LinkedIn" block – top N companies, no personal data, ready to paste.

Run after: python yc_ai_assistant_ingest.py --remote-only --top 20

Usage:
  python shareable_output.py
  python shareable_output.py --top 5
  python shareable_output.py --top 10 --linkedin-only
"""

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
JSON_FILE = SCRIPT_DIR / "yc_ai_assistant_companies.json"


def main():
    ap = argparse.ArgumentParser(description="Shortlist + LinkedIn-ready output from YC AI Assistant list.")
    ap.add_argument("--top", type=int, default=10, help="Number of companies to include (default 10)")
    ap.add_argument("--linkedin-only", action="store_true", help="Print only the LinkedIn block, no shortlist")
    args = ap.parse_args()

    if not JSON_FILE.exists():
        print("Run first: python yc_ai_assistant_ingest.py --remote-only")
        return

    with open(JSON_FILE, encoding="utf-8") as f:
        companies = json.load(f)

    top = companies[: args.top]

    if not args.linkedin_only:
        print("YOUR SHORTLIST (from YC AI Assistant, LATAM remote / worldwide)")
        print("=" * 50)
        for i, c in enumerate(top, 1):
            hiring = " hiring" if c.get("isHiring") else ""
            print(f"  {i}. {c.get('name', '')} ({c.get('score', 0)} pts{hiring})")
            print(f"     {c.get('one_liner', '')}")
            print(f"     {c.get('website', '')}")
            print()
        print("-" * 50)

    # LinkedIn-ready block (no personal info, just companies)
    print("\n--- COPY BELOW FOR LINKEDIN ---\n")
    lines = [
        "This week's YC AI Assistant companies I'm watching (LATAM remote / worldwide, hiring):",
        "",
    ]
    for i, c in enumerate(top, 1):
        name = c.get("name", "")
        one_liner = c.get("one_liner", "")
        website = c.get("website", "")
        lines.append(f"{i}. {name} – {one_liner}")
        if website:
            lines.append(f"   {website}")
        lines.append("")
    lines.append("#AI #YC #RemoteJobs #AIProduct #BuildingInPublic")
    print("\n".join(lines))
    print("\n--- END COPY ---\n")


if __name__ == "__main__":
    main()
