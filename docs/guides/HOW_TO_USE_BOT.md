# How to use the OpenClaw job-shortlist bot (Telegram)

**Bot:** @OpenClaw_VibeJobsList_bot  
**No impact on VibeJob Hunter** — this bot and the job-list-filter pipeline are separate. They don’t install or change VibeJob Hunter. You can use both.

---

## 1. Start the gateway (on your PC)

So the bot can reply, the OpenClaw gateway must be running on your machine:

```powershell
openclaw gateway --port 18789 --verbose --token openclaw-local-18789
```

Leave this terminal open. When you close it, the bot stops replying until you start the gateway again.

---

## 2. Chat by **typing** or **voice**

- **Type:** Send any text. Examples: “job shortlist”, “refresh my list”, “LinkedIn post”, or free-form: “which of these companies hire in Latin America?”, “help me tailor my pitch for Inkeep”.
- **Voice:** Send a voice message in Telegram. The bot gets the transcription and replies in text (or voice if you have TTS configured).
- You don’t have to use exact commands. You can ask for job-search help, shortlist, or LinkedIn formatting in natural language.

---

## 3. Commands in the Telegram menu

Tap the **menu** (/) next to the message box. You should see:

| Command     | What it does |
|------------|-------------------------------|
| `/shortlist` | Get your YC job shortlist (LATAM/remote, top 10). Runs the pipeline and pastes the list. |
| `/linkedin`  | Format the top 5 companies for a LinkedIn post (from the last shortlist). |
| `/help`      | Ask how to use the bot (the agent will use this doc). |

If the menu doesn’t show these, restart the gateway once after adding `customCommands` to your OpenClaw config.

---

## 4. What the bot can do (beyond exact commands)

- **Run the shortlist:** “job shortlist”, “YC companies”, “refresh job list”, “companies to apply to” → runs the pipeline and returns the list.
- **LinkedIn:** “LinkedIn post” or “shareable” → top 5 formatted for a post.
- **Job-search chat:** Ask things like “which of these fit my profile?”, “help me draft a one-liner for [company]”, “what should I emphasize for an AI Product Engineer role?” The agent has your profile and resume context (see below).

The bot uses the **job-shortlist skill** for the pipeline and your **USER.md + resume context** in the workspace for advice. It does **not** replace VibeJob Hunter; it’s a separate way to get the shortlist and chat about it.

---

## 5. Your resume in the bot

Your resume is used so the bot can give job-search and pitch advice that matches your background.

- **Path on your PC:** e.g. `C:\Users\YourName\OneDrive\Desktop\resume\Your_Resume.pdf` (put your own path in the bot's workspace docs)
- A **resume summary** is also in the OpenClaw workspace so the agent always has your profile in context (exec + applied AI, Panama, LATAM remote, target roles).

If you update the PDF, replace the file at that path or put a copy in the workspace `resume/` folder so the bot can use the latest version.

---

## 6. Quick reference

| You want to…              | Do this |
|---------------------------|--------|
| Get the shortlist         | Type “job shortlist” or use `/shortlist`. |
| Get a LinkedIn post       | After a shortlist, type “LinkedIn post” or use `/linkedin`. |
| Chat about roles / pitch  | Type or say in voice: e.g. “help me with my pitch for [company]”. |
| Know what the bot can do  | Type “help” or use `/help`. |
| Keep using VibeJob Hunter | Use it as usual; this bot doesn’t touch it. |
