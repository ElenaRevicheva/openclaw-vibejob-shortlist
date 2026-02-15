# Who this pipeline is for

**Elena (Kirav)** — Panama-based, UTC-5, US time alignment. This codebase and the YC shortlist are tailored to her job search and location.

---

## Background (summary)

- **Earlier:** 7+ years senior executive leadership in large-scale public digital infrastructure in Russia (Deputy CEO & CLO) — enterprise governance, cross-functional technical programs, board-level communication, regulatory environments.
- **2022:** Relocated to Panama (war in Ukraine). Focus on family and stability.
- **2025:** Pivot into applied AI engineering; solo founder building production AI systems: autonomous code review agents, multilingual AI assistants, cross-model orchestration (Oracle Cloud).

**Not** a traditional “Field CTO at hyperscaler” path. **Does** bring:

- Executive-level communication
- Direct experience building AI systems (architecture → deployment)
- Modern AI engineering (LLMs, orchestration, DevOps, API integrations)
- Comfort at technical and strategic layers

Interested in startups that reshape engineering workflows (e.g. Devin, Windsurf-level ambition), and in bridging enterprise governance and hands-on engineering responsibly.

---

## What she’s searching for

- **Location scope:** LATAM remote, worldwide remote, or roles that accept Panama-based (US time). Open to travel if required.
- **Roles:** AI Product Engineer, Applied LLM Engineer, AI Engineer, Founding Engineer, AI Solutions Architect — at startups where exec + applied AI background is a fit (e.g. international expansion, product–governance bridge).
- **Fit:** AI/LLM/agent, dev tools, SaaS, API, automation; avoid on-site-only, embedded/hardware-only, or roles that require a classic hyperscaler CTO profile only.

---

## How the codebase reflects this

- **LATAM remote scope:** Ingest scores companies that explicitly list **Latin America / LATAM** in regions higher (`yc_ai_assistant_ingest.py`).
- **Remote / international filter:** `--remote-only` keeps remote-friendly or international (LATAM, Panama, worldwide).
- **Profile keywords:** `elena_profile.txt` holds target roles, skills, good-fit and avoid keywords for the CSV filter and for consistency.
- **Output:** Shortlist and LinkedIn block are “YC AI Assistant, remote-friendly” with a bias toward LATAM when the API has that data.

Edit `elena_profile.txt` and this file as your focus evolves.
