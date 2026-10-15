# OpenClaw on Oracle — live setup (as of 7 Oct 2026)

What runs where. No secrets here: keys live only in `~/.openclaw/.env` and `~/.openclaw/openclaw.json` on Oracle.

## Process
- systemd **user** unit `openclaw-gateway` → `systemctl --user status openclaw-gateway` (a plain `systemctl` does not see it).
- npm `openclaw@2026.2.14`, state `~/.openclaw`, workspace `~/.openclaw/workspace`. Telegram @OpenClaw_VibeJobsList_bot.
- Shortlist pipeline (unchanged): `~/job-list-filter` (copy of `main`, not git), cron `0 */6 * * *`.

## Models — `agents.defaults.model` (5 providers, the fleet's)
`openai/gpt-4.1` → `google/gemini-2.5-flash` → `xai/grok-3` → `groq/openai/gpt-oss-120b` → `anthropic/claude-sonnet-4-5`
- **Claude last:** v2026.2.14 returns an Anthropic billing error as a chat reply instead of failing over, so a Claude-first
  chain dies whenever Anthropic is empty.
- **Groq cannot serve OpenClaw:** free-tier 413 (8k TPM) is smaller than OpenClaw's base prompt, even for "hello".
- Measured, 7 Oct: right role named — gpt-4.1 10/10 live, Gemini 3/3, Grok 3/3 (with the deal sheet in context).
- **PATCHED 12 Oct 2026 (Elena's go) — an OpenClaw upgrade overwrites this; re-check it after any upgrade.** OpenAI's
  empty-balance text "You have no credits remaining" matched none of `ERROR_PATTERNS.billing`, so `classifyFailoverReason`
  returned `null` and the chain never left gpt-4.1 — the bot replied with the billing error. Added `"no credits remaining"`
  after `"insufficient balance"` in the 5 files that hold the list: `dist/pi-embedded-helpers-{1VoyogxV,CMPLJuLB,DLeTj87G,
  CUD7UoUC}.js` and `dist/plugin-sdk/index.js` (originals: `~/_session-backups/openclaw-20261011/dist-before-billing-patch/`).
  Check: `node --input-type=module -e 'const m=await import("/usr/lib/node_modules/openclaw/dist/pi-embedded-helpers-DLeTj87G.js");
  console.log(m.f("You have no credits remaining"))'` must print `billing`. Verified live: gpt-4.1 error → gemini-2.5-flash
  answered (proof line, Q1/4, title corrected, verified example, LIVE format).

## Voice
`messages.tts`: `auto: "tagged"`, **provider `openai`, model `gpt-4o-mini-tts`, voice `nova`** (since 14 Oct 2026; key from
`OPENAI_API_KEY` in `~/.openclaw/.env`), edge `en-US-AriaNeural` kept as the automatic fallback. The skill ends every message
with `[[tts:text]]…[[/tts:text]]` → Telegram voice note + full text. The `tts` tool is forbidden (double audio).
- **Why (14 Oct, Pitz Spanish interview):** Microsoft's free Edge voice service answers **403** for every voice — from Oracle AND
  from Elena's laptop, with node-edge-tts 1.2.10 (OpenClaw) and python edge_tts 7.2.7 (EspaLuz) — Microsoft-side, not our IP.
  EspaLuz is NOT degraded in practice: most replies call Google gTTS directly, its Edge path falls back to gTTS, and its
  journal has 0 "Neural TTS error/failed" lines since 1 Sep. Per-message voice
  directives only switch OpenAI/ElevenLabs voices, not Edge. OpenAI `nova` is multilingual: Whisper transcribed its Spanish and
  English samples word for word, and it returns Opus (a real Telegram voice note). Spanish mode = skill §0b.
- Voice notes she SENDS: Whisper (Groq `whisper-large-v3-turbo`, then OpenAI) with no fixed language — Spanish is detected.
  **`tools.media.audio.prompt` = her vocabulary** (14 Oct 2026, Pitz): "Pitz, Chalán, taller, cotización, repuestos, diagnóstico.
  AIdeazz, EspaLuz, HubSpot, OpenClaw, CTO AIPA, Claude Code, Cursor, LangGraph, Whisper." (Claude Code + Cursor added 15 Oct: her "con Cursor y Claude Code" was heard as "cloud code") — copied from CTO AIPA's `WHISPER_PROMPT` idea. Before it,
  OpenClaw sent Whisper only its default "Transcribe the audio." A/B on Oracle (same 2 models, same clips): test sentences
  groq 9/15 → 15/15 terms right, OpenAI 7/15 → 14/15 ("es Palus" → EspaLuz, "Landgraf" → LangGraph, "Pitts/Chalan" → Pitz/Chalán);
  English stayed English; her 7 real notes (7–11 Oct, all English) kept the same meaning — punctuation only. A plain list beat
  "Interview practice in English and Spanish. …" (OpenAI 14 vs 13). Add a word only after Whisper got it wrong in a real note.
  Rollback: `openclaw config unset tools.media.audio.prompt` + restart (backup
  `~/_session-backups/openclaw-glossary-20261014/openclaw.json.before-glossary`).
- Rollback: `openclaw config set messages.tts.provider edge` + `systemctl --user restart openclaw-gateway`
  (backup `~/_session-backups/pitz-20261014/openclaw.json.before-voice`).

## Context injected into EVERY reply (bundled hook `bootstrap-extra-files`)
`hooks.internal.entries.bootstrap-extra-files.paths = ["deals/TOOLS.md", "cards/TOOLS.md", "proof/TOOLS.md"]`; the other 3 bundled hooks are disabled.
- `deals/TOOLS.md` ← cron `*/30` `cd ~/cto-aipa && node scripts/hs-deal-prep.cjs --digest --out=… --proof-out=…/proof/TOOLS.md` (AIPA_AITCF repo). ≤11,000 chars.
- `cards/TOOLS.md` ← cron `*/10` `python3 …/skills/interview-spar/references/build-cards.py` (cards rebuilt from her real sessions).
- `proof/TOOLS.md` ← same cron line (15 Oct 2026): her VERIFIED FACTS — CV-bank summary, products, stack line, the stack of each
  product (verified from the code), career in Spanish, the 23 verified examples EN + ES, and for every deal with a 🔎 deep-dive its
  true ✅ Loaded line + its likely questions. ~21,400 chars. Last in the list = nearest the end of the prompt.
Why: anything left for a model to fetch got skipped and then invented (gpt-4.1 named "AI Product Engineer @ Shortical"; on
14–15 Oct it never ran the deal reader for Pitz, made up "✅ Loaded … 7 notes", a client demo, a Slack bot, React dashboards).
**Size caps — `agents.defaults.bootstrapMaxChars = 25000`, `bootstrapTotalMaxChars = 70000` (15 Oct 2026).** OpenClaw's defaults
are 20,000 per file and **24,000 in TOTAL**; AGENTS.md+SOUL+TOOLS+IDENTITY+USER+HEARTBEAT already take ~16,000, so since 7 Oct
the deals sheet was cut 10,984 → 7,676 chars and the cards sheet 4,247 → 661 on every reply — 189 warnings in the journal
(`truncating in injected context`), nothing told her. After the raise: 0 warnings on 8 test sessions. Check after any change:
`journalctl --user -u openclaw-gateway --since "-1 h" | grep -c "truncating in injected"` must print 0.

## Telegram commands
`channels.telegram.commands = {native: false, nativeSkills: false}` (only hers in the "/" list).
`customCommands`: /menu /spar /cards /shortlist /linkedin. `/new` is native: not listed, still works typed.
The menu text lives in `workspace/HELP.md` AND verbatim at the end of `workspace/IDENTITY.md` (bootstrap = always in context).

## Workspace files kept in git (this folder)
`workspace/AGENTS.md`, `workspace/IDENTITY.md`, `workspace/HELP.md`, `interview-spar/` (SKILL.md + references).
NOT in git (personal): `USER.md`, `RESUME_CONTEXT.md`, `interview-cards/`, `cards/`, `deals/`, sessions.

## Backups
`~/_session-backups/openclaw-spar-20261007/` on Oracle: every file and config before each 7 Oct change.
