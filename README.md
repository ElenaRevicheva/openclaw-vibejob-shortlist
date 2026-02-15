# OpenClaw + Job Search: How I Use OpenClaw to Complement My Autonomous Job Engine

**For [Peter Steinberger](https://github.com/petersteinberger) and the OpenClaw community** — here's what I built with OpenClaw and how it fits into my job search.

**Elena Revicheva** · [LinkedIn](https://linkedin.com/in/elenarevicheva) · [AIdeazz](https://aideazz.xyz) · Panama, remote worldwide

---

## What I built

I run two systems for my AI job search:

1. **[VibeJob Hunter](https://github.com/ElenaRevicheva/VibeJobHunterAIPA_AIMCF)** — My main **autonomous job engine**: 8 sources, Claude scoring, auto-apply (ATS forms), founder outreach, follow-ups, LinkedIn CMO. It runs 24/7 on Oracle Cloud and **applies for me** at scale.

2. **This: OpenClaw + YC shortlist** — A **focused, on-demand** layer on top:
   - One pipeline: **YC "AI Assistant"** companies (LATAM/remote, scored).
   - I ask in **Telegram** (text or **voice**): *"job shortlist"*, *"LinkedIn post"*, or *"help me with a pitch for [company]."*
   - OpenClaw runs the pipeline (Python) and uses my **resume in context** for pitch advice.
   - Runs on **Oracle** next to my other products, so it's always on.

So: **VibeJob Hunter = volume and apply. OpenClaw bot = sharp list + pitch quality + voice.**

---

## How OpenClaw complements the job engine

| I need… | Tool | Why |
|--------|------|-----|
| **Apply at scale** | VibeJob Hunter | Auto-apply (Greenhouse, etc.), founder outreach, follow-ups. |
| **Focused YC AI list** | OpenClaw + this repo | Single source (YC AI Assistant tag), LATAM/remote filter, scored. |
| **Pitch tailored to company** | OpenClaw | Agent has my resume; I say "help me with a pitch for Inkeep" and get a draft. |
| **LinkedIn post from shortlist** | OpenClaw | "LinkedIn post" → top 5 ready to copy-paste. |
| **Quick check from my phone** | OpenClaw | Voice message in Telegram → shortlist or advice. |

OpenClaw didn't replace my engine — it **added a conversational, high-signal layer** that makes my list and outreach sharper.

---

## What's in this repo

- **YC AI Assistant pipeline** — `yc_ai_assistant_ingest.py` (fetch, filter LATAM/remote, score) → `shareable_output.py` (shortlist + LinkedIn block). Source: [YC OSS API](https://github.com/yc-oss/api).
- **OpenClaw skill** — `openclaw-skill/job-shortlist/SKILL.md`: when I say "job shortlist" or "LinkedIn post", the agent runs the pipeline and returns the result.
- **Docs** — How to wire this into OpenClaw (Telegram, Oracle, or local), and how to use the bot.

You can clone this repo, add the skill to your OpenClaw workspace, point it at your own job-list path, and get the same "job shortlist in Telegram" flow.

---

## Quick start

```bash
git clone https://github.com/ElenaRevicheva/openclaw-vibejob-shortlist.git
cd openclaw-vibejob-shortlist
pip install -r requirements.txt
python yc_ai_assistant_ingest.py --remote-only --top 20
python shareable_output.py --top 10
```

To use with OpenClaw (Telegram/voice): see [OPENCLAW_INTEGRATION.md](OPENCLAW_INTEGRATION.md).

---

## Tech in one line

**OpenClaw** (Node, Telegram + voice via Groq Whisper) + **one skill** that runs a **Python pipeline** (YC API → ingest → score → shortlist). Deployed on **Oracle Cloud** (systemd) so the bot runs 24/7.

---

## Thanks

To **OpenClaw** for the gateway, skills model, and multi-channel + voice support — it's the layer that made "job shortlist in my pocket" and "pitch help with my resume in context" possible without building another bot from scratch.

If you're building with OpenClaw and want to plug in a job-search pipeline, this repo is a working example.

— Elena
