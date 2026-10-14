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
- Rollback: `openclaw config set messages.tts.provider edge` + `systemctl --user restart openclaw-gateway`
  (backup `~/_session-backups/pitz-20261014/openclaw.json.before-voice`).

## Context injected into EVERY reply (bundled hook `bootstrap-extra-files`)
`hooks.internal.entries.bootstrap-extra-files.paths = ["deals/TOOLS.md", "cards/TOOLS.md"]`; the other 3 bundled hooks are disabled.
- `deals/TOOLS.md` ← cron `*/30` `cd ~/cto-aipa && node scripts/hs-deal-prep.cjs --digest --out=…` (AIPA_AITCF repo). ≤11,000 chars.
- `cards/TOOLS.md` ← cron `*/10` `python3 …/skills/interview-spar/references/build-cards.py` (cards rebuilt from her real sessions).
Why: anything left for a model to fetch got skipped and then invented (gpt-4.1 named "AI Product Engineer @ Shortical").

## Telegram commands
`channels.telegram.commands = {native: false, nativeSkills: false}` (only hers in the "/" list).
`customCommands`: /menu /spar /cards /shortlist /linkedin. `/new` is native: not listed, still works typed.
The menu text lives in `workspace/HELP.md` AND verbatim at the end of `workspace/IDENTITY.md` (bootstrap = always in context).

## Workspace files kept in git (this folder)
`workspace/AGENTS.md`, `workspace/IDENTITY.md`, `workspace/HELP.md`, `interview-spar/` (SKILL.md + references).
NOT in git (personal): `USER.md`, `RESUME_CONTEXT.md`, `interview-cards/`, `cards/`, `deals/`, sessions.

## Backups
`~/_session-backups/openclaw-spar-20261007/` on Oracle: every file and config before each 7 Oct change.
