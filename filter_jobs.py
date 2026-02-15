#!/usr/bin/env python3
"""
Read paste_here.txt:
  - Main paste: Ben Lang list (company, focus, locations).
  - Optional: after "--- LINKS ---" paste Ben Lang's comment with career page URLs.
Filter: remote or Panama only, then realistic for your profile.
Output: result.txt + filtered_jobs.csv with apply links when you pasted the links.
"""

import csv
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PASTE_FILE = SCRIPT_DIR / "paste_here.txt"
PROFILE_PATH = SCRIPT_DIR / "elena_profile.txt"
RESULT_FILE = SCRIPT_DIR / "result.txt"


def normalize_name(name):
    """For matching company names from list vs links."""
    return re.sub(r"\s+", " ", name.lower().strip())


def load_profile():
    out = {"good_fit": [], "avoid": []}
    if not PROFILE_PATH.exists():
        return out
    with open(PROFILE_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if line.upper().startswith("GOOD_FIT_KEYWORDS="):
                out["good_fit"] = [x.strip().lower() for x in line.split("=", 1)[1].split(",")]
            elif line.upper().startswith("AVOID_KEYWORDS="):
                out["avoid"] = [x.strip().lower() for x in line.split("=", 1)[1].split(",")]
    return out


def parse_links_section(text):
    """
    Parse Ben Lang's comment: "1) CHAMP - https://..."
    Returns dict: normalized_company_name -> url
    """
    links = {}
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^\s*\d+[.)]\s*(.+?)\s*-\s*(https?://[^\s]+)", line, re.IGNORECASE)
        if m:
            name, url = m.group(1).strip(), m.group(2).strip()
            links[normalize_name(name)] = url
    return links


def parse_pasted_text(content):
    """
    Parse Ben Lang style lines:
    1) CHAMP - digital vehicle titles (US remote / Cleveland)
    """
    rows = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("PASTE") or line.startswith("(") or line.startswith("-"):
            continue
        m = re.match(r"^\s*\d+[.)]\s*(.+?)\s*-\s*(.+?)\s*\(\s*([^)]+)\s*\)", line, re.IGNORECASE)
        if m:
            name, focus, locations = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            rows.append({"company_name": name, "career_url": "", "locations": locations, "focus": focus})
            continue
        m2 = re.match(r"^\s*\d+[.)]\s*(.+?)\s*\(\s*([^)]+)\s*\)", line, re.IGNORECASE)
        if m2:
            name, locations = m2.group(1).strip(), m2.group(2).strip()
            rows.append({"company_name": name, "career_url": "", "locations": locations, "focus": ""})
    return rows


def matches_remote_or_panama(locations):
    if not locations or not locations.strip():
        return False
    loc = locations.lower().strip()
    return "panama" in loc or "remote" in loc


def score_fit(company_name, focus, profile):
    text = f"{company_name} {focus}".lower()
    for a in profile["avoid"]:
        if a and a in text:
            return "avoid"
    for g in profile["good_fit"]:
        if g and g in text:
            return "good_fit"
    if focus and focus.strip():
        return "maybe"
    if any(k in company_name.lower() for k in ("ai", "llm", "agent", "api", "dev")):
        return "maybe"
    return "maybe"


def main():
    if not PASTE_FILE.exists():
        print("Create paste_here.txt and paste the Ben Lang list into it.")
        return

    with open(PASTE_FILE, encoding="utf-8") as f:
        content = f.read()

    # Split list vs optional links section
    list_part = content
    links_part = ""
    if "--- LINKS ---" in content:
        parts = content.split("--- LINKS ---", 1)
        list_part, links_part = parts[0], parts[1]
    elif "--- links ---" in content.lower():
        idx = content.lower().index("--- links ---")
        list_part, links_part = content[:idx], content[idx:]

    if "---" in list_part:
        list_part = list_part.split("---", 1)[-1]
    rows = parse_pasted_text(list_part)
    links_by_company = parse_links_section(links_part) if links_part else {}

    # Attach career URL when we have it (match by normalized name)
    for r in rows:
        key = normalize_name(r["company_name"])
        r["career_url"] = links_by_company.get(key) or links_by_company.get(key.replace(" inc.", "").replace(" inc", "")) or ""

    if not rows:
        print("No companies found in paste_here.txt.")
        return

    profile = load_profile()
    location_ok = [r for r in rows if matches_remote_or_panama(r["locations"])]
    for r in location_ok:
        r["fit"] = score_fit(r["company_name"], r["focus"], profile)
    realistic = [r for r in location_ok if r["fit"] != "avoid"]

    lines = []
    lines.append("YOUR SHORT LIST - remote/Panama + realistic for your profile")
    lines.append("=" * 60)
    lines.append(f"From {len(rows)} companies -> {len(location_ok)} remote/Panama -> {len(realistic)} for you")
    lines.append("")
    lines.append("HOW THE ANALYSIS WORKS:")
    lines.append("  1) Location: kept only if locations mention 'remote' or 'Panama'.")
    lines.append("  2) Fit: your profile (elena_profile.txt) has good-fit and avoid keywords.")
    lines.append("     GOOD FIT = company/focus matches your target roles (AI, LLM, dev tools, etc.).")
    lines.append("     maybe = neutral. avoid = not shown (saves you time).")
    lines.append("")
    lines.append("-" * 60)
    lines.append("")
    for r in realistic:
        fit_label = "GOOD FIT" if r["fit"] == "good_fit" else "maybe"
        lines.append(f"  [{fit_label}] {r['company_name']}")
        lines.append(f"      {r['locations']}")
        if r["focus"]:
            lines.append(f"      {r['focus']}")
        if r["career_url"]:
            lines.append(f"      APPLY: {r['career_url']}")
        else:
            lines.append(f"      APPLY: Search LinkedIn or Google \"{r['company_name']} careers\"")
        lines.append("")
    if not links_by_company and realistic:
        lines.append("Tip: Paste Ben Lang's comment (with career page links) below \"--- LINKS ---\" in paste_here.txt and run again to get direct APPLY links.")

    result_text = "\n".join(lines)

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write(result_text)

    out_csv = SCRIPT_DIR / "filtered_jobs.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["company_name", "career_url", "locations", "focus", "fit"])
        w.writeheader()
        w.writerows(realistic)

    print(result_text)
    print("-" * 60)
    print(f"Result saved to: {RESULT_FILE}")
    print(f"Also: {out_csv}")


if __name__ == "__main__":
    main()
