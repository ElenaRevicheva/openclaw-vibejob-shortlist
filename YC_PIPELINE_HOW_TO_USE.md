# How to use the YC AI Assistant pipeline (simple guide)

You have a script that **gets a fresh list of YC “AI Assistant” companies**, **scores them** (remote, hiring, small team, etc.), and **saves the top 50** to a JSON file. No manual copying from the YC website.

---

## What it does in one sentence

**Run one command → get a file with 50 good YC AI Assistant companies (active, scored, ready to use).**

---

## What you need

- **Python** on your PC (you already use it for `filter_jobs.py`).
- **One install** (once): the script needs `requests` to download the list from the internet.

---

## Step 1: Install the dependency (once)

Open a terminal in this folder and run:

```bash
pip install requests
```

If that fails, try:

```bash
python -m pip install requests
```

You only need to do this once (or again if you reinstall Python).

---

## Step 2: Run the script

In the same folder, run:

```bash
python yc_ai_assistant_ingest.py
```

That’s it. The script will:

1. **Download** the list of YC companies tagged “AI Assistant” from the official API.
2. **Keep** only “Active” companies (no acquired/inactive).
3. **Score** each company (e.g. remote-friendly +3, hiring +3, small team +2, AI/agent/LLM +3, dev tools +2).
4. **Sort** by score and **save the top 50** into a file.

You’ll see something like:

```
Fetching YC AI Assistant companies...
  Fetched 162 companies with tag AI Assistant.
  After status=Active: 145
Saved top 50 companies to ...\yc_ai_assistant_companies.json
Sample scores: [13, 13, 13, 13, 11]
```

---

## Step 3: Where is the result?

The result is in this file (same folder as the script):

**`yc_ai_assistant_companies.json`**

Open it with any text editor (or VS Code). Each company has:

- **name** – company name  
- **website** – their site  
- **location** – e.g. "San Francisco; Remote"  
- **one_liner** – what they do  
- **batch** – e.g. "Winter 2024"  
- **score** – how well they matched (higher = better)  
- **isHiring** – true/false  
- **regions** – e.g. "Remote", "Fully Remote"  

So you get a **ready-made shortlist** of 50 companies to look at, with links and one-liners.

---

## Step 4: What to do with that file

- **Manual:** Open the JSON, skim the names and one-liners, click websites, check careers pages.
- **With your filter:** You can use this list as input to your existing job filter (e.g. copy names/websites into your workflow or a small script that reads the JSON).
- **Later:** If you use “VibeJobHunter” or another tool, you can feed it this file and tag the source as `yc_ai_assistant`.

You’re not changing VibeJobHunter or the rest of your setup; you’re just **getting a clean, renewable list** from YC instead of copying it by hand.

---

## Optional: only LATAM / remote / international companies

If you only want companies that are **LATAM remote, remote-friendly, or international** (e.g. you’re in Panama, US time, LATAM or worldwide remote):

```bash
python yc_ai_assistant_ingest.py --remote-only
```

That keeps only companies that list Remote / Fully Remote / Partly Remote or have non–US-only regions (including **Latin America**). Companies that explicitly list Latin America / LATAM get an extra score boost. See [PROFILE.md](PROFILE.md) for who this pipeline is for.

---

## Optional: change how many companies you get

Default is **top 50**. To get top 30 instead:

```bash
python yc_ai_assistant_ingest.py --top 30
```

You can combine:

```bash
python yc_ai_assistant_ingest.py --remote-only --top 30
```

---

## When to run it

- **Whenever you want a fresh list** (e.g. once a week).
- Just run the same command again; it **overwrites** `yc_ai_assistant_companies.json` with the latest data from YC.

So: **one command → fresh top 50 (or 30) in the JSON file.**

---

## Quick reference

| I want to…                    | Run this |
|------------------------------|----------|
| Get top 50 AI Assistant cos  | `python yc_ai_assistant_ingest.py` |
| Only remote/international    | `python yc_ai_assistant_ingest.py --remote-only` |
| Get top 30 instead of 50     | `python yc_ai_assistant_ingest.py --top 30` |
| See the result               | Open `yc_ai_assistant_companies.json` |

---

## If something breaks

- **“No module named 'requests'”** → Run `pip install requests` (Step 1).
- **“No companies left”** with `--remote-only` → Run without `--remote-only` first to get the full list.
- **Script not found** → Make sure you’re in the folder that contains `yc_ai_assistant_ingest.py` (same folder as `filter_jobs.py`).

That’s it. You run the script, you get a JSON with your shortlist; the rest is how you like to use it (manual check, your filter, or another tool).
