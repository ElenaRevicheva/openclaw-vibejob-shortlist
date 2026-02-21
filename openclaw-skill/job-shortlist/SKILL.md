# Job Shortlist skill – OpenClaw

## MANDATORY: /priority, priority list, priority companies

**When the user says "/priority", "/priority list", "priority list", or "priority companies":**
- You do NOT have access to the priority list. It lives ONLY in VibeJob Hunter.
- Do NOT invent, fabricate, or make up a list of companies.
- Do NOT run shell commands (ls, grep, find, etc.) to look for priority files.
- Reply ONLY with this exact message (or very close):

"The Priority Companies list is managed in **VibeJob Hunter** (@vibejob_hunter_bot). Use /priority list there to see your target companies. To sync: (1) Ask me for your job shortlist here, (2) In VibeJob Hunter use /priority sync yc."

---

When the user asks for **/menu** or "what can you do", describe these 4 options:

1. **Job shortlist** — Top 10 YC AI companies (LATAM/remote). Say "job shortlist" or tap Shortlist.
2. **LinkedIn post** — Top 5 ready to copy-paste. Say "LinkedIn post" or tap LinkedIn.
3. **Chat about your job search** — Ask in your own words; uses resume and situation.
4. **Priority Companies sync** — The priority list lives in VibeJob Hunter. To sync: (1) Ask me for your job shortlist (I'll run the pipeline with export), (2) In VibeJob Hunter use `/priority sync yc`.

---

When the user asks for their **job shortlist**, **YC companies**, **refresh job list**, **/shortlist**, or **companies to apply to**:

1. **ALWAYS run the pipeline fresh.** Never use cached or previously fetched output. Each request = new fetch from YC API.
2. **Run the pipeline** in the job-list-filter folder (--export-priority is included in run_shortlist.sh):
   - **Oracle (deployed server):** Run exactly: `cd /home/ubuntu/job-list-filter && ./run_shortlist.sh`
   - Path (WSL2): `cd /path/to/openclaw-vibejob-shortlist` then `./run_shortlist.sh`
   - Path (Windows): `cd /d C:\path\to\openclaw-vibejob-shortlist` then `run_shortlist.bat`
   - run_shortlist.sh already includes --export-priority. Or manually: `python3 yc_ai_assistant_ingest.py --remote-only --top 20 --export-priority` then `python3 shareable_output.py --top 10`.

2. **Return to the user**:
   - Summarize: "Here are your top 10 YC AI Assistant companies (remote-friendly, scored)."
   - Paste the shortlist (company name, one-liner, website) from the script output.
   - Add: "A 'Copy for LinkedIn' block is in the output. Say 'LinkedIn post' if you want me to format the top 5 for a post."
   - Add: "To sync these as Priority Companies in VibeJob Hunter, use /priority sync yc there."

3. **If the user says "LinkedIn post" or "shareable"**: Format the top 5 companies as name – one-liner, link. Add: "Building in public: how I keep my target list sharp. #AI #YC #RemoteJobs"

4. **If the user asks for "priority list", "priority companies", or "/priority"**:
   - Follow the MANDATORY section at the top. Do NOT invent a list. Do NOT run commands. Redirect to VibeJob Hunter only.

Do not make up companies. Only use output from the scripts. If the JSON is missing or commands fail, tell the user to run the pipeline once manually (see OPENCLAW_INTEGRATION.md in job-list-filter).
