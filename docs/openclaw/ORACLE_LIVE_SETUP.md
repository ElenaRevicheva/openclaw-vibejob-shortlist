# OpenClaw on Oracle — live setup (as of 7 Oct 2026)

What runs where. No secrets here: keys live only in `~/.openclaw/.env` and `~/.openclaw/openclaw.json` on Oracle.

## Process
- systemd **user** unit `openclaw-gateway` → `systemctl --user status openclaw-gateway` (a plain `systemctl` does not see it).
- npm `openclaw@2026.2.14`, state `~/.openclaw`, workspace `~/.openclaw/workspace`. Telegram @OpenClaw_VibeJobsList_bot.
- Shortlist pipeline (unchanged): `~/job-list-filter` (copy of `main`, not git), cron `0 */6 * * *`.
- **Genuine:** npm `openclaw`, MIT, maintainers steipete (Peter Steinberger) + vincentkoc, github.com/openclaw/openclaw.
- **WhatsApp channel — LINKED 15 Oct 2026 ~16:05 UTC to her WhatsApp Business number (her explicit go, after the risk was
  explained: OpenClaw docs recommend a dedicated number; WhatsApp Web/Baileys is an unofficial client).** Settings (backup
  `~/_session-backups/openclaw-wa-20261015/openclaw.json.before-wa`): `dmPolicy: allowlist`, `allowFrom` = her own number ONLY
  (the Feb value was a "+507XXXXXXXX" placeholder), `groupPolicy: allowlist`, `selfChatMode: true` (she talks to it in "Message
  yourself"; replies are prefixed), `sendReadReceipts: false` (read receipts only ever go to ACCEPTED senders, so clients' messages
  are never marked read and never answered). Linked with the documented `openclaw channels login --channel whatsapp` (QR shown to
  her as a PNG decoded-and-verified first); credentials `~/.openclaw/credentials/whatsapp` chmod 700/600. Gateway restart 16:07:23
  UTC: `[whatsapp] starting provider` + `Listening for personal WhatsApp inbound messages`, Telegram provider started too.
  Unlink: WhatsApp Business → Linked devices → log out the OpenClaw device (or `openclaw channels logout --channel whatsapp`).
  Do NOT import `dist/login-qr-*.js` from a script — it runs the whole CLI and exits.
  **Verified live 16:08 UTC:** `[whatsapp] Inbound message … (direct)` → `Auto-replied`; gpt-4.1; true ✅ Loaded line + Pitz 🎤 Q1 in
  Spanish; 0 truncation. WhatsApp and Telegram DMs share ONE main session (OpenClaw default) — a conversation continues across both.
  ⚠️ Everything she types in "Message yourself" now goes to the coach (she used that chat as a notepad for client drafts).

## Upgrade — TESTED 15 Oct 2026, NOT applied (Elena: "only with test, no rebuilding, no overwriting what you created")
Newest npm = 2026.10.3 needs Node ≥24.16; every release from 2026.7.1 needs Node ≥22.22.3 — Oracle's system Node 22.22.0 runs
13 processes (cto-aipa, DragonTrade, whitespace, n8n…), so upgrading Node for one bot was ruled out. Newest on Node 22.22.0 =
**2026.6.35**: installed side-by-side (`~/_scratch/openclaw-next`) and run on two COPIES of `~/.openclaw` (Telegram/WhatsApp
off, no bot token). Blockers, each against her conditions:
1. `Unknown model: openai/gpt-4.1` — not in its bundled catalog → every turn silently fell back to Gemini (needs a custom model entry).
2. Config is INVALID until relabelled: `messages.tts.openai/edge` → `messages.tts.providers.openai/microsoft` + `speakerVoice`;
   `channels.telegram.streamMode` → `streaming.mode`. Values map 1:1 (validated on the copy). `doctor --fix` would also rename
   `anthropic/claude-sonnet-4-5` to a newer Sonnet; gpt-4.1/gemini-2.5-flash/grok-3/gpt-oss-120b are not on its rename lists.
3. ONE-WAY state migrations on first start: cron store → SQLite (`cron/jobs.json.migrated`), update-check → shared SQLite. A rollback
   = restore `~/_session-backups/openclaw-upgrade-20261015/dot-openclaw.before.tgz`, not just reinstalling.
4. WhatsApp became an external plugin (`clawhub:@openclaw/whatsapp`) — unused here.
What worked on 2026.6.35: exec ran the deal reader, the true ✅ Loaded line, a verified example copied word for word.
**Test-harness trap:** `openclaw agent --local` does NOT inject `bootstrap-extra-files` (deals/cards/proof) in either version — a
faithful upgrade test needs a second GATEWAY on another port with channels off, not `--local`. Live untouched (config/.env/crontab
md5 OK, 0 migrated files, gateway start 11:11:35 UTC unchanged).

## Models — `agents.defaults.model` (4 providers since 23 Oct 2026)
`openai/gpt-4.1` → `google/gemini-2.5-flash` → `xai/grok-3` → `anthropic/claude-sonnet-4-5`
- **23 Oct 2026 — failover PROVEN live, Groq removed, alerts added.** `openclaw agent --local` with a fake OPENAI key →
  401 → gemini-2.5-flash answered in 1.4 s. But it fails over SILENTLY, and 133/133 replies in 40 real sessions were
  gpt-4.1, so nobody would notice a dead key. `groq/openai/gpt-oss-120b` removed (free tier 8,000 TPM vs prompts of
  38k median / 79k max tokens — it could never answer). AIPA_AITCF `scripts/openclaw-fallback-alert.cjs`: cron
  `2-59/10` `--scan` reads the session files → Telegram alert when a model failed and which backup answered (once per
  provider + reason per 12 h; `test-*` sessions ignored); cron `5 14 * * *` `--probe` = 1-token call to every model in
  the chain, alert on credits/key failure. The same Anthropic key serves OpenClaw, cto-aipa and VJH.
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
`messages.tts`: `auto: "tagged"`, **provider `openai`, model `tts-1` (since 15 Oct 16:17 UTC; was `gpt-4o-mini-tts`), voice `nova`**.
**Why tts-1:** gpt-4o-mini-tts STALLED — 7 of 15 voice replies failed on 15 Oct, each exactly 30 s (`messages.tts.timeoutMs` default
30000) then Edge fallback → 403. Bench on Oracle: gpt-4o-mini-tts 5.0/5.0/4.7 s and one 60 s stall (137 bytes); tts-1 12/12 in
1.7–3.5 s, Spanish read back clearly by Whisper. After: 3/3 voice replies through OpenClaw in 2–3 s. WhatsApp gets MP3 (fixed in
this version — flat-line bubble, plays); Telegram gets Opus. CTO AIPA spoken replies: `CTO_VOICE_TTS_MODEL=tts-1` in Oracle `.env`.
Was: `messages.tts`: `auto: "tagged"`, **provider `openai`, model `gpt-4o-mini-tts`, voice `nova`** (since 14 Oct 2026; key from
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

## Local patches inside OpenClaw's dist (root-owned; an upgrade OVERWRITES them — re-apply and re-test after any upgrade)
1. **Billing failover** (12 Oct): `"no credits remaining"` / `"insufficient balance"` added to ERROR_PATTERNS (4 files) so an empty
   OpenAI balance fails over instead of replying with the error. Backups `~/_session-backups/openclaw-20261011/`.
2. **WhatsApp voice = Opus** (15 Oct, Elena's go): `resolveOutputFormat()` returned Opus only for Telegram, MP3 for everything else,
   and the WhatsApp sender marks every audio `ptt: true` — an MP3 voice note plays on WhatsApp Web but NOT in the phone app (her
   report: "WA cell does not work"). Patched in 4 files (`pi-embedded-8DITBEle.js`, `pi-embedded-CM97XTkp.js`, `reply-CYMZTXlH.js`,
   `reply-CrwRmeCr.js`): `if (channelId === "telegram" || channelId === "whatsapp") return TELEGRAM_OUTPUT;` — one line each,
   `node --check` ok. The WA sender already rewrites `audio/ogg` → `audio/ogg; codecs=opus`. Verified: WA voice before = `.mp3`
   (16:12, 16:21 UTC), after = `[[audio_as_voice]] … .opus` (16:38:29), sent 16:38:31. Backups
   `~/_session-backups/openclaw-wa-20261015/dist-before-opus/`. Check: `grep -c 'channelId === "whatsapp") return TELEGRAM_OUTPUT' dist/*.js`.

## Context injected into EVERY reply (bundled hook `bootstrap-extra-files`)
`hooks.internal.entries.bootstrap-extra-files.paths = ["deals/TOOLS.md", "cards/TOOLS.md", "proof/TOOLS.md", "prod/TOOLS.md", "pack/TOOLS.md", "pack2/TOOLS.md", "pack3/TOOLS.md", "pack4/TOOLS.md"]` (23 Oct 2026); the other 3 bundled hooks are disabled.
- `deals/TOOLS.md` ← cron `*/30` `cd ~/cto-aipa && node scripts/hs-deal-prep.cjs --digest --out=… --proof-out=…/proof/TOOLS.md` (AIPA_AITCF repo). ≤11,000 chars.
- `cards/TOOLS.md` ← cron `*/10` `python3 …/skills/interview-spar/references/build-cards.py` (cards rebuilt from her real sessions).
  **Since 15 Oct 2026 it also LEARNS FROM HER CORRECTIONS** (her go: "like VJH does"): her own words that carry a clear signal —
  `no soy…`, `I'm not…`, `never say…`, `that's wrong…`, `remember:`/`recuerda:` — go into a permanent ledger
  `workspace/interview-cards/lessons.json` (survives /new and deleted sessions) and sit at the TOP of this sheet as "ELENA'S
  CORRECTIONS", newest first, in every reply. `my lessons` shows them; `forget: <words>` drops one. Her words only, never the
  model's "🔧" paraphrase; an answer like "I served seven years being a CEO…" is not a lesson. On her real history it learned exactly
  1 (14 Oct, "No soy developer full stack manual"); live test: the Spanish self-intro applied it unasked. Test:
  `OPENCLAW_SESSIONS=<copy> OPENCLAW_CARDS_OUT=<tmp> python3 build-cards.py` (never a UUID-named test session — it would become hers).
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

- `pack/…pack4/TOOLS.md` ← the ONE active study pack (23 Oct 2026): a company's case task + Elena's submitted deliverables, kept as `🎓 STUDY PACK` notes on its HubSpot deal by AIPA_AITCF `scripts/hs-study-pack.cjs` (file uploaded, text split by code, coaching by claude-opus-5-5 with every number checked, fallback = llm-resilience 'quality'); cron `15,45` `--refresh` rebuilds it from HubSpot and unloads it when the deal is won/lost or 30 days old. Every line the script prints ends `[proof xxxxxx]` — gpt-4.1 twice reported "loaded" with no tool call.
- Caps now `bootstrapMaxChars = 40000`, `bootstrapTotalMaxChars = 270000` (injected ~205k with the Pitz pack).

## Telegram commands
`channels.telegram.commands = {native: false, nativeSkills: false}` (only hers in the "/" list).
`customCommands`: /menu /spar /cards /shortlist /linkedin /pack /packs /unpack (study packs, 23 Oct 2026). `/pack <company>` is a SKILL (`workspace/skills/pack|packs|unpack/SKILL.md`): as plain rules gpt-4.1 ran it 3/5 times ("study X" was read as a mock interview); as a one-purpose skill 5/5 + 3/3 without the slash. `/new` is native: not listed, still works typed.
The menu text lives in `workspace/HELP.md` AND verbatim at the end of `workspace/IDENTITY.md` (bootstrap = always in context).

## Workspace files kept in git (this folder)
`workspace/AGENTS.md`, `workspace/IDENTITY.md`, `workspace/HELP.md`, `workspace/skills/pack|packs|unpack/`, `interview-spar/` (SKILL.md + references). Mirrored from Oracle 23 Oct 2026.
NOT in git (personal): `USER.md`, `RESUME_CONTEXT.md`, `interview-cards/`, `cards/`, `deals/`, sessions.

## Backups
`~/_session-backups/openclaw-studypacks-20261023/` and `openclaw-defend-20261023/` (23 Oct: openclaw.json, AGENTS/IDENTITY/HELP, crontab before each change).
`~/_session-backups/openclaw-spar-20261007/` on Oracle: every file and config before each 7 Oct change.
