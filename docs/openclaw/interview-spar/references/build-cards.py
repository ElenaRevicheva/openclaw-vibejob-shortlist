#!/usr/bin/env python3
"""Rebuild Elena's interview cards from her real OpenClaw conversations — no model involved.

Why (7 Oct 2026): on gpt-4.1 the skill replied "💾 saved to your cards" without running the save command;
the cards folder stayed empty. A step left to the model gets skipped and then reported as done. The
conversation record (session .jsonl) is the truth, so the cards are rebuilt from it, idempotently.

Cron: */10. Reads only Elena's real sessions (UUID-named files; test sessions have other names).
Writes ~/.openclaw/workspace/interview-cards/<role-slug>.md — one file per role, rewritten each run.
"""
import glob, json, os, re

SESS = os.path.expanduser("~/.openclaw/agents/main/sessions")
OUT = os.path.expanduser("~/.openclaw/workspace/interview-cards")
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$")
Q_RE = re.compile(r"🎙️\s*\**\s*Q(\d+)/(\d+)\s*·\s*([^\n*]+)\**\s*\n+(.+?)(?:\n|\(answer)", re.S)
A_RE = re.compile(r"✅\s*\**Your answer, polished\**\s*\n+(.+?)(?:\n\s*\n?💡|\n\s*\n?🎯|\Z)", re.S)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "general"


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
for path in sorted(glob.glob(os.path.join(SESS, "*.jsonl"))):
    if not UUID.match(os.path.basename(path)):
        continue
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
            pending = (role.strip(), q.strip())

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
CAP = 6000
allc = sorted(((day, role, q, ans) for role, items in cards.items() for (q, ans), day in items.items()), reverse=True)
sheet = ["# ELENA'S INTERVIEW CARDS — her polished mock-interview answers, newest first (auto-built every 10 min).",
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
print(f"cards: {sum(len(v) for v in cards.values())} answers across {len(cards)} role(s)")
