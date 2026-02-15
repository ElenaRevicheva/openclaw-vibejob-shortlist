# How to integrate OpenClaw with job-list-filter

This doc is the **step-by-step** way to create the integration so you can say **"job shortlist"** in OpenClaw (Telegram, WebChat, or CLI) and get your YC AI Assistant shortlist back.

---

## What you already have in this folder

| Item | Purpose |
|------|--------|
| `yc_ai_assistant_ingest.py` | Fetches YC AI Assistant companies, scores them, writes `yc_ai_assistant_companies.json`. |
| `shareable_output.py` | Reads that JSON, prints your shortlist + a "Copy for LinkedIn" block. |
| `run_shortlist.sh` | One command (Linux/WSL2): runs ingest + shareable_output. |
| `run_shortlist.bat` | One command (Windows): same. |
| `openclaw-skill/job-shortlist/SKILL.md` | OpenClaw skill: when user asks for job shortlist, run the pipeline and return the list. |

---

## Prerequisites

- **Node.js ≥ 22** (for OpenClaw). [Node](https://nodejs.org/)
- **Python 3** with `requests` (you already use this for job-list-filter).  
  `pip install -r requirements.txt`
- **OpenClaw** recommends **WSL2** on Windows. So: Windows with WSL2 installed, or Linux/macOS.

---

## Step 1: Install OpenClaw

In **WSL2** (or Linux/macOS):

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

The wizard will ask for model (e.g. Anthropic/OpenAI), workspace path, and optionally Telegram/other channels. Complete it so the Gateway runs and you can talk to the agent (WebChat or Telegram).

On **Windows without WSL2**: You can try `npm install -g openclaw@latest` in PowerShell, but OpenClaw’s recommended path is [Windows via WSL2](https://github.com/openclaw/openclaw). If you run on Windows only, use the path to this repo on your machine (e.g. `D:\path\to\openclaw-vibejob-shortlist`) in the skill and run scripts via `run_shortlist.bat` (see Step 3).

---

## Step 2: Make job-list-filter available where OpenClaw runs

OpenClaw’s agent runs **bash** (or process) on the machine where the **Gateway** runs. So the agent must be able to `cd` into job-list-filter and run Python.

**Option A – OpenClaw in WSL2 (recommended)**  
Your folder on Windows is visible in WSL2 at:

```text
/path/to/openclaw-vibejob-shortlist
```

No copy needed. In WSL2 install Python and deps once:

```bash
cd /path/to/openclaw-vibejob-shortlist
pip3 install -r requirements.txt
chmod +x run_shortlist.sh
```

**Option B – OpenClaw on Windows (PowerShell)**  
Use the folder as-is:

```text
D:\path\to\openclaw-vibejob-shortlist
```

Ensure `python` is in PATH and `pip install -r requirements.txt` is done there.

---

## Step 3: Install the job-shortlist skill into OpenClaw

OpenClaw loads skills from:

```text
~/.openclaw/workspace/skills/<skill-name>/
```

You need a folder `job-shortlist` with a file `SKILL.md` inside it.

**From WSL2:**

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -r /path/to/openclaw-vibejob-shortlist/openclaw-skill/job-shortlist ~/.openclaw/workspace/skills/
```

**From Windows (PowerShell):**  
Copy the folder manually:

- Source: `D:\path\to\openclaw-vibejob-shortlist\openclaw-skill\job-shortlist`
- Target: `%USERPROFILE%\.openclaw\workspace\skills\job-shortlist`

(If `\.openclaw\workspace\skills` doesn’t exist, create it. You need `skills\job-shortlist\SKILL.md`.)

---

## Step 4: Point the skill at your path

The agent will run commands in the job-list-filter directory. Edit the skill so it uses **your** path.

Open in an editor:

- **WSL2:** `~/.openclaw/workspace/skills/job-shortlist/SKILL.md`  
- **Windows:** `%USERPROFILE%\.openclaw\workspace\skills\job-shortlist\SKILL.md`

Set the path once at the top (pick one):

- **WSL2:**  
  `JOBLIST_PATH=/path/to/openclaw-vibejob-shortlist`
- **Windows:**  
  `JOBLIST_PATH=D:\path\to\openclaw-vibejob-shortlist`

Then in the skill text, tell the agent to:

1. `cd $JOBLIST_PATH` (or `cd /mnt/d/...` / `cd D:\...`).
2. Run either:
   - `./run_shortlist.sh` (WSL2/Linux/Mac), or  
   - `run_shortlist.bat` (Windows).

So the agent always runs the same one-liner (ingest + shareable output), and you only maintain the path in one place. Below is an updated SKILL.md you can paste.

---

## Step 5: Updated SKILL.md (copy this)

Replace the contents of `~/.openclaw/workspace/skills/job-shortlist/SKILL.md` (or the Windows path above) with:

```markdown
# Job Shortlist skill – OpenClaw

When the user asks for their **job shortlist**, **YC companies**, **refresh job list**, or **companies to apply to**:

1. **Run the pipeline** in the job-list-filter folder:
   - Path (WSL2): `/path/to/openclaw-vibejob-shortlist`
   - Path (Windows): `D:\path\to\openclaw-vibejob-shortlist`
   - Commands to run (from that directory):
     - WSL2/Linux/Mac: `./run_shortlist.sh`
     - Windows: `run_shortlist.bat`
   - Or run manually: `python yc_ai_assistant_ingest.py --remote-only --top 20` then `python shareable_output.py --top 10`.

2. **Return to the user**:
   - Summarize: "Here are your top 10 YC AI Assistant companies (remote-friendly, scored)."
   - Paste the shortlist (company name, one-liner, website) from the script output so they can click and apply.
   - Mention: "A 'Copy for LinkedIn' block is in the output; I can format a short LinkedIn post from the top 5 if you say 'LinkedIn post'."

3. **If the user says "LinkedIn post" or "shareable"**: Format the top 5 companies as a short list (name – one-liner, link) and add: "Building in public: how I keep my target list sharp. #AI #YC #RemoteJobs"

Do not make up companies. Only use output from the scripts. If the JSON is missing or scripts fail, tell the user to run the commands in job-list-filter manually once (see OPENCLAW_INTEGRATION.md).
```

Adjust the paths if your drive letter or path is different (e.g. `D:` vs `C:`).

---

## Step 6: Restart OpenClaw and test

1. Restart the Gateway so it reloads skills:
   - If you use the daemon: `openclaw restart` or restart the service.
   - Or stop and start: `openclaw gateway --port 18789 --verbose`
2. In WebChat or Telegram (or CLI): say **"job shortlist"** or **"refresh my YC job list"**.
3. The agent should `cd` to job-list-filter, run `run_shortlist.sh` (or `.bat`), and reply with the shortlist from the script output.

If the agent says it can’t find the folder or Python, check:

- Path in SKILL.md matches where job-list-filter really is.
- Python and `requests` are installed in the same environment the Gateway uses (WSL2 or Windows).

---

## Summary

| Step | Action |
|------|--------|
| 1 | Install OpenClaw (Node ≥22), run `openclaw onboard --install-daemon` (prefer WSL2 on Windows). |
| 2 | In the environment where the Gateway runs: have job-list-filter at a known path; install Python + `pip install -r requirements.txt`; make `run_shortlist.sh` executable (WSL2/Linux) or use `run_shortlist.bat` (Windows). |
| 3 | Copy `openclaw-skill/job-shortlist` to `~/.openclaw/workspace/skills/job-shortlist`. |
| 4 | Edit `SKILL.md` so the path and command (`.sh` or `.bat`) match your setup. |
| 5 | Restart OpenClaw and ask **"job shortlist"** to verify. |

That’s the full integration: OpenClaw + job-list-filter in one flow. For more on OpenClaw (skills, channels, config), see the [OpenClaw repo](https://github.com/openclaw/openclaw) and docs.
