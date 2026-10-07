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

## Voice
`messages.tts`: `auto: "tagged"`, provider `edge`, voice `en-US-AriaNeural`, rate `-5%` (no key). The skill ends every message
with `[[tts:text]]…[[/tts:text]]` → Telegram voice note + full text. The `tts` tool is forbidden (double audio).

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
