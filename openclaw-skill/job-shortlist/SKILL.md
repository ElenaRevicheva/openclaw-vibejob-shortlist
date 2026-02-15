# Job Shortlist skill – OpenClaw

When the user asks for their **job shortlist**, **YC companies**, **refresh job list**, or **companies to apply to**:

1. **Run the pipeline** in the job-list-filter folder:
   - Path (WSL2): `cd /path/to/openclaw-vibejob-shortlist` (or e.g. /mnt/d/.../job-list-filter)
   - Path (Windows): `cd /d C:\path\to\openclaw-vibejob-shortlist`
   - Then run **one** of:
     - WSL2/Linux/Mac: `./run_shortlist.sh`
     - Windows: `run_shortlist.bat`
   - Or manually: `python yc_ai_assistant_ingest.py --remote-only --top 20` then `python shareable_output.py --top 10`.

2. **Return to the user**:
   - Summarize: "Here are your top 10 YC AI Assistant companies (remote-friendly, scored)."
   - Paste the shortlist (company name, one-liner, website) from the script output.
   - Add: "A 'Copy for LinkedIn' block is in the output. Say 'LinkedIn post' if you want me to format the top 5 for a post."

3. **If the user says "LinkedIn post" or "shareable"**: Format the top 5 companies as name – one-liner, link. Add: "Building in public: how I keep my target list sharp. #AI #YC #RemoteJobs"

Do not make up companies. Only use output from the scripts. If the JSON is missing or commands fail, tell the user to run the pipeline once manually (see OPENCLAW_INTEGRATION.md in job-list-filter).
