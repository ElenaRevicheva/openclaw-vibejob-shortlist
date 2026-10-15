#!/usr/bin/env python3
"""Rebuild Elena's interview cards — and, since 15 Oct 2026, the lessons from her corrections — from her real
OpenClaw conversations. No model involved.

Why (7 Oct 2026): on gpt-4.1 the skill replied "💾 saved to your cards" without running the save command;
the cards folder stayed empty. A step left to the model gets skipped and then reported as done. The
conversation record (session .jsonl) is the truth, so the cards are rebuilt from it, idempotently.

Cron: */10. Reads only Elena's real sessions (UUID-named files; test sessions have other names).
Writes ~/.openclaw/workspace/interview-cards/<role-slug>.md — one file per role, rewritten each run.
"""
import glob, hashlib, json, os, re

# Overridable only so the lessons can be tested on a copy; the cron uses the defaults.
SESS = os.environ.get("OPENCLAW_SESSIONS") or os.path.expanduser("~/.openclaw/agents/main/sessions")
OUT = os.environ.get("OPENCLAW_CARDS_OUT") or os.path.expanduser("~/.openclaw/workspace/interview-cards")
# 12 Oct 2026: "/new" renames a finished session to <uuid>.jsonl.reset.<time>; those are her real answers too
# (the 11 Oct Puente PM session vanished from /cards when she sent /new at 11:28 UTC).
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl(\.reset\..+)?$")
# 14 Oct 2026: Spanish interviews — the model may drop " · <role>", write "(responde …)" and "✅ Tu respuesta, pulida".
# The cards must not depend on the model keeping English markers, so both spellings are read.
Q_RE = re.compile(r"🎙️\s*\**\s*Q(\d+)/(\d+)\s*(?:·\s*([^\n*]+))?\**\s*\n+\**(.+?)\**\s*(?:\n|\((?:answer|responde))", re.S | re.I)
A_RE = re.compile(r"✅\s*\**(?:Your answer, polished|(?:Tu )?respuesta,? pulida)\**[^\n]*\n+(.+?)(?:\n\s*\n?💡|\n\s*\n?🎯|\Z)", re.S | re.I)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "general"


# ── HER CORRECTIONS (15 Oct 2026, Elena: "make openclaw learn from my corrections like VJH does") ──────────────
# Same discipline as VJH's judge_feedback_sync: learn from HER words, never a model's paraphrase of them ("🔧 Corregido"
# is the model's), keep a permanent ledger (a session file can be reset or deleted), and put the lessons into every
# reply. Only clear correction signals count — on 11 Oct she answered "I served seven years being a CEO and deputy CEO",
# an answer to polish, not a rule; on 14 Oct "No soy developer full stack manual" IS one.
CORRECTION = re.compile(
    r"^\s*(?:remember|recuerda|запомни)\b"
    r"|\b(?:remember that|recuerda que|from now on|a partir de ahora|запомни)\b"
    r"|\b(?:don'?t|do not|never|stop) (?:say|call|write|use|saying|calling)\b"
    r"|\b(?:no|nunca) (?:digas|me llames|escribas|uses)\b|\bdeja de (?:decir|llamar)\b|\bне (?:говори|пиши|называй)\b"
    r"|\b(?:i'?m not|i am not|no soy)\b|(?:^|\s)я не\b"
    r"|\b(?:that'?s|that is|it'?s|this is) (?:wrong|not true|not right|incorrect)\b"
    r"|\b(?:eso|esto) (?:no es|está mal|es falso)\b|\bno es (?:así|cierto|correcto|verdad)\b|\bнеправильно\b",
    re.I)
FORGET = re.compile(r"^\s*(?:forget|olvida|забудь)\b[\s:,-]*(.+)$", re.I | re.S)
NOT_HERS = re.compile(r"HEARTBEAT|Note from Claude Code|To send an image back|A new session was started", re.I)
# Whisper mishearings actually seen in her notes (14 Oct: "con cursor y cloud code"). Only add a pair after SEEING it.
HEARD_AS = [(re.compile(r"\bcloud code\b", re.I), "Claude Code")]
LESSONS_MAX = 3000


def her_messages(path):
    """(day, her words, 'voice'|'text') for every message she sent — the gateway's wrapper stripped."""
    for line in open(path, encoding="utf-8"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        m = e.get("message") or {}
        if m.get("role") != "user":
            continue
        c = m.get("content")
        t = "\n".join(x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else str(c or "")
        if NOT_HERS.search(t):
            continue
        t = re.sub(r"Conversation info \(untrusted metadata\):\s*```json.*?```\s*", "", t, flags=re.S)
        v = re.search(r"Transcript:\s*(.*)$", t, re.S)
        words = (v.group(1) if v else re.sub(r"^\[[^\]]*\]\s*", "", t.strip())).strip()
        for bad, good in HEARD_AS:
            words = bad.sub(good, words)
        if words:
            yield str(e.get("timestamp", ""))[:16], re.sub(r"\s+", " ", words), "voice" if v else "text"   # to the minute: newest first


def learn(paths):
    """Merge her corrections into the permanent ledger; return the active lessons, newest first."""
    ledger_path = os.path.join(OUT, "lessons.json")
    try:
        led = json.load(open(ledger_path, encoding="utf-8"))
    except (OSError, ValueError):
        led = {"lessons": [], "forgotten": []}
    known = {l["id"] for l in led["lessons"]}
    forgets = []
    for path in paths:
        for day, words, via in her_messages(path):
            f = FORGET.match(words)
            if f:
                forgets.append((day, f.group(1).strip(" .\"'").lower()))
                continue
            # A pasted posting or interviewer question is long and not about her; a command is not a lesson.
            if words.startswith("/") or len(words) > 600 or re.match(r"(?i)prep me|prepárame", words):
                continue
            if CORRECTION.search(words):
                lid = hashlib.sha1(words.lower().encode()).hexdigest()[:10]
                if lid not in known:
                    led["lessons"].append({"id": lid, "text": words[:400], "date": day, "via": via})
                    known.add(lid)
    for day, w in forgets:   # "forget: full stack" drops the lessons she had given UP TO that day
        for l in led["lessons"]:
            if len(w) >= 3 and w in l["text"].lower() and l["date"] <= day and l["id"] not in led["forgotten"]:
                led["forgotten"].append(l["id"])
    os.makedirs(OUT, exist_ok=True)
    tmp = ledger_path + ".tmp"
    json.dump(led, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, ledger_path)
    gone = set(led["forgotten"])
    return sorted((l for l in led["lessons"] if l["id"] not in gone), key=lambda l: l["date"], reverse=True)


def texts(path):
    for line in open(path, encoding="utf-8"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        m = e.get("message") or {}
        if m.get("role") != "assistant" or not isinstance(m.get("content"), list):
            continue
        t = "\n".join(x.get("text", "") for x in m["content"] if isinstance(x, dict) and x.get("type") == "text")
        if t.strip():
            yield str(e.get("timestamp", ""))[:10], t


cards = {}
paths = [p for p in sorted(glob.glob(os.path.join(SESS, "*.jsonl*"))) if UUID.match(os.path.basename(p))]
for path in paths:
    pending = None  # the last question asked in this session
    for day, t in texts(path):
        a = A_RE.search(t)
        if a and pending:
            role, q = pending
            ans = re.sub(r"\[\[/?tts[^\]]*\]\]", "", a.group(1)).strip()
            key = (q, ans)
            cards.setdefault(role, {})[key] = day
        qs = Q_RE.findall(t)
        if qs:
            n, total, role, q = qs[-1]
            pending = ((role or "").strip() or "Interview", q.strip())

os.makedirs(OUT, exist_ok=True)
for role, items in cards.items():
    lines = [f"# Interview cards — {role}", "_Built from your real mock-interview sessions (no model rewrote them)._", ""]
    for (q, ans), day in sorted(items.items(), key=lambda kv: kv[1]):
        lines += [f"## {day}", f"**Q:** {q}", "", f"**A:** {ans}", ""]
    tmp = os.path.join(OUT, f".{slug(role)}.tmp")
    open(tmp, "w", encoding="utf-8").write("\n".join(lines))
    os.replace(tmp, os.path.join(OUT, f"{slug(role)}.md"))
# One combined sheet, injected into EVERY reply by the bundled bootstrap-extra-files hook (path cards/TOOLS.md —
# the hook only accepts standard bootstrap file names). "/cards" must not depend on a model running a command:
# on 7 Oct gpt-4.1 answered "/cards" with "you have no cards" while a card existed.
CAP = 9000   # 15 Oct 2026: room for her corrections on top (OpenClaw's total budget was raised to 70,000 the same day)
allc = sorted(((day, role, q, ans) for role, items in cards.items() for (q, ans), day in items.items()), reverse=True)
lessons = learn(paths)
sheet = []
if lessons:
    sheet = ["# ELENA'S CORRECTIONS — her own words, newest first, learned from her real sessions every 10 min (as VJH learns",
             "# from her No-fit reasons). Apply EVERY one in every reply — mock, LIVE and free questions; a newer one wins over an",
             "# older one. Facts and numbers still come only from her VERIFIED FACTS sheet. 'my lessons' → show these lines exactly.",
             ""]
    for l in lessons:
        line = f"- {l['date'][:10]} ({l['via']}): \"{l['text']}\""
        if sum(len(x) + 1 for x in sheet) + len(line) > LESSONS_MAX:
            break
        sheet.append(line)
    sheet.append("")
sheet += ["# ELENA'S INTERVIEW CARDS — her polished mock-interview answers, newest first (auto-built every 10 min).",
          "# When she sends /cards or 'my cards', show these EXACTLY (optionally only the role she names). Never invent cards.",
          ""]
if not allc:
    sheet.append("(no cards yet — they appear after her first answered mock-interview question)")
for day, role, q, ans in allc:
    block = f"## {role} · {day}\nQ: {q}\nA: {ans}\n"
    if sum(len(x) + 1 for x in sheet) + len(block) > CAP:
        break
    sheet.append(block)
sd = os.path.join(os.path.dirname(OUT), "cards")
os.makedirs(sd, exist_ok=True)
tmp = os.path.join(sd, ".TOOLS.tmp")
open(tmp, "w", encoding="utf-8").write("\n".join(sheet))
os.replace(tmp, os.path.join(sd, "TOOLS.md"))
print(f"cards: {sum(len(v) for v in cards.values())} answers across {len(cards)} role(s) · lessons: {len(lessons)} active")
