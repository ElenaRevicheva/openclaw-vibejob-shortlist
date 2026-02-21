#!/usr/bin/env python3
"""
YC AI Assistant company pipeline.

Tailored for: candidate based in Panama (UTC-5), US time alignment, seeking
LATAM remote / worldwide remote roles at startups (exec + applied AI background).

1. Fetches YC companies tagged "AI Assistant" from the official OSS API.
2. Filters to status == "Active".
3. Optionally keeps only remote-friendly / international (LATAM, Panama, worldwide).
4. Scores each company (remote, hiring, LATAM-friendly, team size, voice/agent/LLM, dev tools, ATS).
5. Outputs top N (default 50) to yc_ai_assistant_companies.json.

Usage:
  python yc_ai_assistant_ingest.py
  python yc_ai_assistant_ingest.py --top 30 --remote-only

Source: https://github.com/yc-oss/api (tags/ai-assistant.json)
"""

import argparse
import json
from pathlib import Path

import requests

# YC OSS API: by tag (AI Assistant) – 162 companies, updated daily
YC_TAG_AI_ASSISTANT = "https://yc-oss.github.io/api/tags/ai-assistant.json"
OUTPUT_FILE = Path(__file__).parent / "yc_ai_assistant_companies.json"
# VibeJobHunter sync: list of {company_name, source} for /priority sync yc
PRIORITY_EXPORT_FILE = Path(__file__).parent / "priority_companies_for_vibejob.json"

# ─── Scoring (strategic top 50) ───
SCORE_REMOTE = 3
SCORE_HIRING = 3
SCORE_LATAM = 2        # Explicit LATAM / Latin America in regions (best fit for Panama-based)
SCORE_SMALL_TEAM = 2   # team_size < 50
SCORE_VOICE_AGENT_LLM = 3
SCORE_DEVELOPER_TOOL = 2
SCORE_ATS = 1          # Ashby / Greenhouse / Lever – requires enrichment

# Region strings that indicate LATAM hiring (YC API uses e.g. "Latin America")
LATAM_REGION_KEYWORDS = {"latin america", "latam", "south america", "central america"}

# Tags that indicate voice/agent/LLM or developer focus (from API)
VOICE_AGENT_LLM_TAGS = {"voice", "agent", "llm", "conversational ai", "generative ai", "chatbot", "ai"}
DEVELOPER_TOOL_TAGS = {"developer tools", "api", "open source"}


def fetch_yc_ai_assistant_companies():
    """Pull YC company list for tag AI Assistant. Returns list of company dicts.
    Uses cache-busting to ensure fresh data (no CDN/proxy stale cache)."""
    import time
    url = f"{YC_TAG_AI_ASSISTANT}?t={int(time.time())}"
    headers = {"Cache-Control": "no-cache", "Pragma": "no-cache"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def is_remote_friendly(company):
    """True if regions include Remote / Fully Remote / Partly Remote."""
    regions = company.get("regions") or []
    return any(
        r in regions
        for r in ("Remote", "Fully Remote", "Partly Remote")
    )


def is_international(company):
    """True if regions suggest non–US-only hiring (e.g. India, Europe, Latin America)."""
    regions = company.get("regions") or []
    us_only = {"United States of America", "America / Canada"}
    return any(r not in us_only for r in regions)


def is_latam_friendly(company):
    """True if regions explicitly include LATAM / Latin America (best fit for Panama-based candidate)."""
    regions = company.get("regions") or []
    return any(
        any(kw in (r or "").lower() for kw in LATAM_REGION_KEYWORDS)
        for r in regions
    )


def keep_for_panama_or_global(company):
    """Keep if remote-friendly OR international (LATAM remote / Panama / worldwide)."""
    return is_remote_friendly(company) or is_international(company)


def score_company(company):
    """Score 0+ using: remote, hiring, team size, voice/agent/LLM, developer tool, ATS (stub)."""
    score = 0
    tags = [t.lower() for t in (company.get("tags") or [])]
    one_liner = (company.get("one_liner") or "").lower()
    long_desc = (company.get("long_description") or "").lower()
    combined = " ".join(tags) + " " + one_liner + " " + long_desc

    if is_remote_friendly(company):
        score += SCORE_REMOTE
    if is_latam_friendly(company):
        score += SCORE_LATAM
    if company.get("isHiring") is True:
        score += SCORE_HIRING
    team_size = company.get("team_size")
    if isinstance(team_size, (int, float)) and 0 < team_size < 50:
        score += SCORE_SMALL_TEAM
    if any(k in combined for k in ("voice", "agent", "llm", "conversational", "generative ai", "chatbot")):
        score += SCORE_VOICE_AGENT_LLM
    if any(k in combined for k in ("developer tool", "api", "open source", "sdk")):
        score += SCORE_DEVELOPER_TOOL
    # ATS: would need careers page fetch; placeholder for future enrichment
    if company.get("ats") in ("ashby", "greenhouse", "lever"):
        score += SCORE_ATS

    return score


def slugify_company(name):
    """Normalize company name for VibeJobHunter matching (lowercase, alphanumeric + hyphen)."""
    if not name:
        return ""
    import re
    s = str(name).lower().strip()
    s = re.sub(r"[^a-z0-9\-\s]", " ", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s or name.lower()


def extract_company_record(company, score=0):
    """Minimal record for JSON output and downstream (e.g. VibeJobHunter source)."""
    return {
        "name": company.get("name"),
        "website": company.get("website") or "",
        "location": company.get("all_locations") or "",
        "one_liner": company.get("one_liner") or "",
        "batch": company.get("batch") or "",
        "status": company.get("status") or "",
        "score": score,
        "isHiring": company.get("isHiring"),
        "team_size": company.get("team_size"),
        "regions": company.get("regions") or [],
        "source": "yc_ai_assistant",
    }


def main():
    ap = argparse.ArgumentParser(description="Ingest YC AI Assistant companies, filter, score, output top N.")
    ap.add_argument("--top", type=int, default=50, help="Number of top-scored companies to output (default 50)")
    ap.add_argument("--remote-only", action="store_true", help="Keep only remote-friendly or international companies")
    ap.add_argument("--no-filter-status", action="store_true", help="Do not filter to status=Active only")
    ap.add_argument("--export-priority", action="store_true", help="Also write priority_companies_for_vibejob.json for VibeJobHunter sync")
    args = ap.parse_args()

    print("Fetching YC AI Assistant companies...")
    companies = fetch_yc_ai_assistant_companies()
    print(f"  Fetched {len(companies)} companies with tag AI Assistant.")

    # Filter: Active only (unless disabled)
    if not args.no_filter_status:
        companies = [c for c in companies if c.get("status") == "Active"]
        print(f"  After status=Active: {len(companies)}")

    # Optional: only remote-friendly or international (LATAM / Panama / worldwide)
    if args.remote_only:
        companies = [c for c in companies if keep_for_panama_or_global(c)]
        print(f"  After LATAM/remote/international filter: {len(companies)}")

    if not companies:
        print("No companies left after filters. Try without --remote-only.")
        return

    # Score and sort
    scored = [(c, score_company(c)) for c in companies]
    scored.sort(key=lambda x: -x[1])
    top = scored[: args.top]

    out = [extract_company_record(c, s) for c, s in top]
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Saved top {len(out)} companies to {OUTPUT_FILE}")
    print("Sample scores:", [s for _, s in top[:5]])

    # Optional: export for VibeJobHunter /priority sync yc (additive — Feb 2026)
    if args.export_priority:
        priority_out = [
            {"company_name": slugify_company(c.get("name")), "source": "yc"}
            for c, _ in top
            if slugify_company(c.get("name"))
        ]
        with open(PRIORITY_EXPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(priority_out, f, indent=2)
        print(f"Exported {len(priority_out)} to {PRIORITY_EXPORT_FILE} (for VibeJobHunter /priority sync yc)")


if __name__ == "__main__":
    main()
