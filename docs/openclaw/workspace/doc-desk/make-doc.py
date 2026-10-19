#!/usr/bin/env python3
# OpenClaw document desk (Elena, 19 Oct 2026). Her document on stdin (first line = title, then light Markdown) becomes a
# PDF / Word / HTML file through the shared renderer ~/cto-aipa/scripts/build-lane-cv.cjs, called in place (never a copy).
# The file lands in <state dir>/media/outbound-docs, inside OpenClaw's outbound media roots. On success the last output
# line is the send line OpenClaw delivers to her by itself; on any failure there is no such line and the exit code is not 0.
# Why a file and not an inline one-liner: on 19 Oct gpt-4.1 re-typed the inline program and broke it (dropped a call,
# "simplified" a string), and in another run put a pipe after the heredoc terminator. A short fixed command cannot drift.
#
# HONESTY GATE, in code, before anything is rendered. A rule alone did not keep gpt-4.1 honest (17-19 Oct), so whatever can
# be checked is checked here, against her VERIFIED FACTS (the part of proof/TOOLS.md about HER, above the interview-deal
# briefs) plus THIS conversation's own sources: her messages (with an attached PDF's text), the hs-deal-prep output and the
# Word/PDF reader output. Assistant text is never a source. Nothing unverifiable reaches the file:
#   - a number (digits or a number word) no source has, or one used with a different noun than every source use
#     ("20 integraciones" when the facts say "20 scheduled jobs"), becomes [dato]
#   - an e-mail address or web address no source has becomes [email] / [web]
#   - a sentence with a fit / client / price claim no source makes ("ideal candidate", "clientes reales", "gratis") is removed
#   - a cover letter for a deal whose notes hold a ✅ READY TO SEND cover letter IS that letter, word for word
#   Today's date and numbers inside a worded [placeholder] are free. The output says exactly what was changed.
# Why repair and not refuse: on 19 Oct the refusing version stopped 2 of 6 files, and both times gpt-4.1 answered "I'll fix
# it and send it shortly" and never ran the command again. A visible [dato] is honest AND she still gets her file.
# The conversation's sources come from OpenClaw's own session file: the file whose last tool call is this very command.
# Not found = only the facts sheet counts (stricter, never looser).
#
# Every line printed passes through safe(): OpenClaw sends whatever follows "media" + ":" anywhere in a tool result, in
# any case, so a document line like "Social media" + colon + "Instagram" must never reach the output unchanged.
#
# usage:  python3 -I <this file> KIND LANG FORMAT NAME <<'DOC'
#         <title line>
#         <text>
#         DOC
import datetime, difflib, glob, json, os, re, subprocess, sys, time, unicodedata

KINDS = "letter proposal quote report prep answer evaluation other".split()
ALIASES = {"carta": "letter", "cover-letter": "letter", "propuesta": "proposal", "presentation": "proposal",
           "presentacion": "proposal", "one-pager": "proposal", "onepager": "proposal", "cotizacion": "quote",
           "informe": "report", "reporte": "report", "analisis": "report", "analysis": "report",
           "evaluacion": "evaluation", "respuesta": "answer"}
STATE = os.environ.get("OPENCLAW_STATE_DIR") or os.path.expanduser("~/.openclaw")   # what OpenClaw itself resolves
OUT = os.path.join(STATE, "media", "outbound-docs")
FACTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "proof", "TOOLS.md")
HER_END = "===== 🎤 INTERVIEW DEALS"            # below this line the sheet holds briefs about companies, not facts about her
CONTACT_OK = ["aipa@aideazz.xyz", "aideazz.xyz", "aideazz.xyz/portfolio"]   # the renderer's own contact header


def safe(s):
    return re.sub("(?i)medi(a):", "media :", s)   # written so this file never contains the send token itself


RETRY = (" No file was made. Run it again AT ONCE in this same turn, first line exactly: python3 -I " +
         os.path.abspath(__file__) + " KIND LANG FORMAT NAME <<'DOC' (four words after the file, nothing else), then the "
         "title line, the text and a last line DOC. Never tell Elena a file is coming.")


def stop(msg, code):
    print(safe(msg + (RETRY if code != 0 else "")))
    sys.exit(code)


def fold(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# ---------- this conversation's sources, from OpenClaw's session file ----------
SOURCE_CMD = re.compile(r"hs-deal-prep|docx\.Document|PyPDF2")


def text_of(content):
    if isinstance(content, str):
        return content
    return "".join(x.get("text", "") for x in content or [] if isinstance(x, dict) and x.get("type") == "text")


def clean_user(t):
    t = re.sub(r"^\s*\[(?:Telegram|WhatsApp|Signal|Discord|Slack|iMessage|Web|Channel)[^\]\n]*\]", " ", t, flags=re.I)
    t = re.sub(r"(?m)^\s*\[media attached[^\n]*$", " ", t)            # inbound file path: digits of a uuid, not facts
    t = re.sub(r"(?m)^\s*\[message_id:[^\]\n]*\]\s*$", " ", t)
    t = re.sub(r"(?m)^System: [^\n]*$", " ", t)
    return t


def session_sources(name):
    files = [f for f in glob.glob(os.path.join(STATE, "agents", "*", "sessions", "*.jsonl"))
             if time.time() - os.path.getmtime(f) < 1800]
    for f in sorted(files, key=os.path.getmtime, reverse=True)[:8]:
        msgs = []
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                if o.get("type") == "message" and isinstance(o.get("message"), dict):
                    msgs.append(o["message"])
        calls, last = {}, []
        for m in msgs:
            if m.get("role") == "assistant" and isinstance(m.get("content"), list):
                tc = [x for x in m["content"] if isinstance(x, dict) and x.get("type") == "toolCall"]
                for x in tc:
                    calls[x.get("id")] = str((x.get("arguments") or {}).get("command", ""))
                if tc:
                    last = [calls[x.get("id")] for x in tc]
        me = re.compile(r"make-doc\.py\s+\S+\s+\S+\s+\S+\s+" + re.escape(name) + r"(?![\w-])")
        if not any(me.search(c) for c in last):
            continue
        texts, used = [], {"her messages": 0, "deal lookups": 0, "document reads": 0}
        for m in msgs:
            role = m.get("role")
            if role == "user":
                texts.append(clean_user(text_of(m.get("content"))))
                used["her messages"] += 1
            elif role == "toolResult":
                cmd = calls.get(m.get("toolCallId") or m.get("toolUseId"), "")
                if "make-doc.py" not in cmd and SOURCE_CMD.search(cmd):
                    texts.append(text_of(m.get("content")))
                    used["deal lookups" if "hs-deal-prep" in cmd else "document reads"] += 1
        return texts, used
    return None, None


# ---------- the gate ----------
TOKEN = re.compile(r"[\w.,%]+(?:/[\w.,%]+)*")      # "24/7" and "1/12/2026" stay one token
WORD = re.compile(r"[^\W\d_]+")
EN = dict(zip(range(2, 21), "two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
                            "seventeen eighteen nineteen twenty".split()))
EN.update(zip(range(30, 100, 10), "thirty forty fifty sixty seventy eighty ninety".split()))
ES = dict(zip(range(2, 31), "dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis "
                            "diecisiete dieciocho diecinueve veinte veintiuno veintidos veintitres veinticuatro veinticinco "
                            "veintiseis veintisiete veintiocho veintinueve treinta".split()))
ES.update(zip(range(40, 100, 10), "cuarenta cincuenta sesenta setenta ochenta noventa".split()))
BIG = [("hundred hundreds", "cien cientos doscientos doscientas trescientos trescientas cuatrocientos quinientos "
                            "seiscientos setecientos ochocientos novecientos"),
       ("thousand thousands", "mil miles"), ("million millions", "millon millones"), ("billion billions", "billon billones"),
       ("dozen dozens", "docena docenas")]
CLAIMS = ["ideal candidate", "perfect candidate", "perfect fit", "perfect match", "strong fit", "great fit", "best fit",
          "meets all", "meet all the requirements", "meet all requirements", "meet every requirement", "meets every",
          "fully qualified", "exceed the requirements", "exceeds the requirements", "led a team", "lead a team",
          "managed a team", "our clients", "our customers", "my clients", "clients include", "trusted by", "by real clients",
          "happy clients", "satisfied clients", "for free", "free of charge", "free trial", "free consultation",
          "free diagnostic", "free session", "no cost",
          "candidata ideal", "candidato ideal", "candidata perfecta", "perfil ideal", "encaje perfecto", "encajo perfectamente",
          "cumplo con todos", "cumplo todos", "reuno todos", "lidere un equipo", "lidero un equipo", "dirigi un equipo",
          "nuestros clientes", "mis clientes", "clientes como", "confian en nosotros", "por clientes reales",
          "clientes satisfechos", "clientes de diversos", "clientes de distintos", "diversos sectores", "distintos sectores",
          "gratis", "gratuita", "gratuito", "sin costo", "various industries", "multiple industries", "across industries",
          "clients across", "clients in various"]
STOP = set("de del la el los las lo en y e o u a al mas than of the and in on at to for by with con por para un una an "
           "plus over more about around casi almost nearly its sus su your our my mis nuestros nuestras".split())
MONTHS = {"en": "january february march april may june july august september october november december",
          "es": "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
WEB = re.compile(r"(?<![@\w.])(?:https?://)?(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:xyz|com|net|org|io|ai|co|pa|es|dev|app)"
                 r"(?:/[^\s)\]]*)?", re.I)


def norm_num(w):
    w = w.lower().rstrip("%")
    return re.sub(r"[.,]", "", w) if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", w) else w


def num_spans(text):
    for m in TOKEN.finditer(text):
        s, e = m.span()
        while s < e and text[s] in ".,":
            s += 1
        while e > s and text[e - 1] in ".,":
            e -= 1
        if any(c.isdigit() for c in text[s:e]):
            yield s, e, text[s:e]


# proof7 (19 Oct): a Spanish analysis of an English NDA lost all 7 of its true numbers ("24 meses" vs "24 months" looked like
# "used for something else"). The same unit in either language, singular or plural, now counts as the same thing.
UNIT_EQ = {}
for _canon, _stems in {"MONTH": "month mes mese", "YEAR": "year ano", "DAY": "day dia", "WEEK": "week seman",
                       "HOUR": "hour hora", "MINUTE": "minut", "BUSINESS": "busin habil habile", "USER": "user usuar",
                       "TEST": "test prueb", "WEBSITE": "websi sitio", "AUDIT": "audit audito", "PERCENT": "perce porce",
                       "MONEY": "usd dolar dolla", "PAGE": "page pagin", "CLIENT": "clien", "DEAL": "deal",
                       "JAN": "janua enero", "FEB": "febru febre", "MAR": "march marzo", "APR": "april abril", "MAY": "may mayo",
                       "JUN": "june junio", "JUL": "july julio", "AUG": "augus agost", "SEP": "septe septi setie",
                       "OCT": "octob octub", "NOV": "novem novie", "DEC": "decem dicie"}.items():
    for _s in _stems.split():
        UNIT_EQ[_s] = _canon


def stem(w):
    w = w[:-1] if len(w) > 3 and w.endswith("s") else w
    w = w[:5]
    return UNIT_EQ.get(w, w)


def units(text, e):
    """The first two content words after a number, on the same line (stems): what the number counts."""
    tail = text[e:e + 120].split("\n", 1)[0]
    out = []
    for w in WORD.findall(fold(tail)):
        if w not in STOP:
            out.append(stem(w))
        if len(out) == 2:
            break
    return set(out)


QUAL_BEFORE = re.compile(r"(?:\bmore than|\bover|\bm[aá]s de|\bupwards of)\s*$", re.I)


def qualified(text, s, e):
    """'15+', 'more than 15', 'más de 15': the span of the qualifier, or None."""
    if text[e:e + 1] == "+":
        return (e, e + 1)
    m = QUAL_BEFORE.search(text[max(0, s - 16):s])
    return (max(0, s - 16) + m.start(), s) if m else None


def free_spans(text):
    """Where numbers are free: list markers, [placeholders] with a word in them, today's date."""
    spans = [m.span() for m in re.finditer(r"(?m)^\s*(?:#{1,6}\s*)?\d{1,3}[.)](?=\s)", text)]
    spans += [m.span() for m in re.finditer(r"\[[^\[\]\n]*[^\W\d_][^\[\]\n]*\]", text)]
    now = datetime.datetime.now(datetime.timezone.utc)
    for d in {now.date(), (now - datetime.timedelta(hours=5)).date()}:
        y, mo, dd = d.year, d.month, d.day
        names = "|".join(MONTHS["en"].split()[mo - 1:mo] + MONTHS["es"].split()[mo - 1:mo] + [MONTHS["en"].split()[mo - 1][:3]])
        for p in (rf"\b0?{dd}\s+(?:de\s+)?(?:{names})\.?(?:,?\s+(?:de\s+|del\s+)?{y})?\b",
                  rf"\b(?:{names})\.?\s+0?{dd}(?:st|nd|rd|th)?(?:,?\s+{y})?\b",
                  rf"\b{y}-0?{mo}-0?{dd}\b", rf"\b0?{dd}[/.]0?{mo}[/.]{y}\b", rf"\b0?{mo}/0?{dd}/{y}\b"):
            spans += [m.span() for m in re.finditer(p, text, flags=re.I)]
    return spans


class Sources:
    def __init__(self, texts):
        self.text = "\n".join(texts)
        self.nums, self.bind, self.qual = set(), {}, set()
        for t in texts:
            for s, e, w in num_spans(t):
                n = norm_num(w)
                self.nums.add(n)
                self.bind.setdefault(n, []).append(units(t, e))
                if qualified(t, s, e):
                    self.qual.add(n)
        self.words = set(WORD.findall(fold(self.text)))
        self.flat = " ".join(re.findall(r"[^\W_]+", fold(self.text)))
        self.folded = fold(self.text)

    def number_ok(self, n, doc_units):
        if n not in self.nums:
            return False
        if re.fullmatch(r"(19|20)\d\d", n) or not doc_units:       # a year, or a bare number: the token is enough
            return True
        uses = self.bind.get(n, [])
        return any(not u or (u & doc_units) for u in uses)          # some source uses it for the same thing


def repair(title, text, lang, src):
    """Returns (title, text, changes). Everything a source cannot back is replaced by a visible placeholder or removed."""
    whole = title + "\n" + text
    subs, bad_nums, other_use, contacts, protect, inflated = [], [], [], [], [], []
    for rx, ph in ((EMAIL, "[email]"), (WEB, "[web]")):          # addresses first: their digits are not numbers
        for m in rx.finditer(whole):
            s = m.start()
            v = m.group().rstrip(".,;:")
            e = s + len(v)
            if any(a < e and s < b for a, b in protect):
                continue
            protect.append((s, e))
            core = re.sub(r"^(https?://)?(www\.)?", "", fold(v)).rstrip("/")
            if core not in CONTACT_OK and core not in src.folded:
                subs.append((s, e, ph))
                contacts.append(v)
    free = free_spans(whole) + protect
    isfree = lambda s, e: any(a <= s and e <= b for a, b in free)
    for s, e, w in num_spans(whole):
        if isfree(s, e) or any(a < e and s < b for a, b in protect):
            continue
        n = norm_num(w)
        if not src.number_ok(n, units(whole, e)):
            subs.append((s, e, "[dato]"))
            (other_use if n in src.nums else bad_nums).append(w)
        else:
            q = qualified(whole, s, e)
            if q and n not in src.qual and not any(a < q[1] and q[0] < b for a, b in protect):
                subs.append((q[0], q[1], ""))
                inflated.append(whole[min(q[0], s):max(q[1], e)].strip())
    table = ES if lang == "es" else EN
    big = {w: set(en.split()) | set(es.split()) for en, es in BIG for w in (en + " " + es).split()}
    for m in WORD.finditer(whole):
        w = fold(m.group())
        hit = next((v for v, x in table.items() if x == w), None)
        if hit is not None:
            ok = w in src.words or str(hit) in src.nums or EN.get(hit) in src.words or ES.get(hit) in src.words
        elif w in big:
            ok = bool(src.words & big[w])
        else:
            continue
        if not ok and not isfree(*m.span()):
            subs.append((m.start(), m.end(), "[dato]"))
            bad_nums.append(m.group())
    for s, e, ph in sorted(subs, reverse=True):
        whole = whole[:s] + ph + whole[e:]
    whole = re.sub(r"(?<=\S) {2,}(?=\S)", " ", whole)      # a removed qualifier must not leave a double space
    title, _, text = whole.partition("\n")
    removed = []

    def claim_in(sentence):
        flat = " ".join(re.findall(r"[^\W_]+", fold(sentence)))
        return [c for c in CLAIMS if re.search(rf"\b{c}\b", flat) and not re.search(rf"\b{c}\b", src.flat)]

    lines = []
    for line in text.split("\n"):
        m = re.match(r"(\s*(?:#{1,6}\s+|[-*]\s+|\d{1,3}[.)]\s+)?)(.*)$", line)
        lead, body = m.group(1), m.group(2)
        parts = re.split(r"(?<=[.!?])\s+", body)
        keep = []
        for p in parts:
            c = claim_in(p)
            if c:
                removed.extend(c)
            else:
                keep.append(p)
        if body.strip() and not keep:
            continue                                   # a line made only of claims goes completely
        lines.append(lead + " ".join(keep))
    text = "\n".join(lines)
    title_claims = claim_in(title)
    changes = []
    if bad_nums:
        changes.append(f"{len(bad_nums)} number(s) no source states became [dato]: " + ", ".join(bad_nums))
    if other_use:
        changes.append(f"{len(other_use)} number(s) used for something else than in her sources became [dato]: " + ", ".join(other_use))
    if inflated:
        changes.append(f"{len(inflated)} 'more than' / '+' no source says was removed (the number stays): " + ", ".join(inflated))
    if contacts:
        changes.append(f"{len(contacts)} e-mail/web address(es) not in her sources became [email]/[web]: " + ", ".join(contacts))
    if removed:
        changes.append(f"{len(removed)} sentence(s) removed for a claim no source makes: " + "; ".join(f'"{c}"' for c in removed))
    return title, text, changes, title_claims


LETTER_MARK = "✅ READY TO SEND — cover letter"
SIGN_OFF = re.compile(r"\b(best regards|kind regards|sincerely|warm regards|saludos|atentamente|cordialmente)\b")


def ready_letters(sources):
    """The ✅ READY TO SEND cover letters in the deal notes: (text as she sends it, folded word string)."""
    out = []
    for s in sources:
        for part in s.split(LETTER_MARK)[1:]:
            body = part.split("\n", 1)[1] if "\n" in part else ""
            body = re.split(r"\n\s*The CV for this posting|\n=====|…\s*\[cut\]", body)[0]
            paras = [re.sub(r"\s+", " ", p).strip() for p in body.split("\n") if p.strip()]
            if len(" ".join(paras).split()) >= 40:
                out.append(("\n\n".join(paras), " ".join(re.findall(r"[^\W_]+", fold(" ".join(paras))))))
    return out


def is_cover_letter(kind, title, text):
    if re.search(r"cover letter|carta de presentacion|carta de motivacion", fold(title)):
        return True
    return kind == "letter" and re.search(r"cover letter|carta de presentacion|i am applying|i'm applying|applying for the|"
                                          r"my application|me postulo|mi postulacion", fold(text)) is not None


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    if len(args) < 4:
        stop("usage: make-doc.py KIND LANG FORMAT NAME <<'DOC' then the title line, the text and a last line DOC.", 2)
    kind, lang, fmt, name = args[:4]                  # proof7: gpt-4.1 added a quoted title as a 5th word and lost the file
    notes = ["extra word(s) after NAME ignored"] if len(args) > 4 else []
    kind = fold(kind)
    kind = kind if kind in KINDS else ALIASES.get(kind, "other")   # an invented kind must not cost her the file
    lang = lang[:2].lower()
    fmt = {"word": "docx", "doc": "docx", "htm": "html"}.get(fmt.lower(), fmt.lower())
    if fmt not in ("pdf", "docx", "html") or lang not in ("es", "en"):
        stop("FORMAT must be pdf, docx or html and LANG es or en.", 2)
    fname = re.sub(r"[^a-z0-9-]+", "-", fold(name)).strip("-")[:60] or "documento"   # a bad NAME must not cost the file
    title, _, text = sys.stdin.read().strip().partition("\n")
    title = title.strip().strip("# *")
    if not title or not text.strip():
        stop("no text: the title goes on the first line after the command, the document after it, then DOC", 2)

    facts = open(FACTS, encoding="utf-8").read().split(HER_END)[0] if os.path.exists(FACTS) else ""
    conv, used = session_sources(name)
    if conv is None:
        seen = "her VERIFIED FACTS only (this conversation's session file was not found)"
    else:
        seen = "her VERIFIED FACTS + " + ", ".join(f"{k}: {n}" for k, n in used.items())
    changes = []
    letters = ready_letters(conv or []) if is_cover_letter(kind, title, text) else []
    if letters:
        mine = " ".join(re.findall(r"[^\W_]+", fold(text)))
        best = max(letters, key=lambda L: difflib.SequenceMatcher(None, L[1].split(), mine.split(), autojunk=False).ratio())
        if best[1] not in mine:
            changes.append("the letter is now the ✅ READY TO SEND cover letter from the deal notes, word for word")
        text = best[0]
    src = Sources([facts] + (conv or []))
    title, text, fixed, title_claims = repair(title, text, lang, src)
    changes += fixed
    if title_claims:
        stop("REFUSED: the title makes a claim no source makes (" + "; ".join(title_claims) + "). Write a plain title.", 3)
    print(safe("honesty check (against " + seen + "): " + ("; ".join(changes) if changes else "nothing to change") + "."
               + (" (" + "; ".join(notes) + ")" if notes else "")))
    os.makedirs(OUT, mode=0o700, exist_ok=True)
    out, k = os.path.join(OUT, fname + "." + fmt), 1
    while os.path.exists(out):                         # the same NAME twice must not fail: never overwrite, number it
        k += 1
        out = os.path.join(OUT, f"{fname}-{k}.{fmt}")
    spec = {"kind": kind, "lang": lang, "title": title, "text": text}
    r = subprocess.run(["node", "scripts/build-lane-cv.cjs", "--text=-", "--format=" + fmt, "--out=" + out],
                       cwd=os.path.expanduser("~/cto-aipa"), input=json.dumps(spec), capture_output=True, text=True,
                       timeout=120)
    print(safe((r.stdout + r.stderr).strip()))
    if r.returncode != 0:
        print(safe("Fix what the line above names." + RETRY))
        sys.exit(r.returncode)
    print("Elena receives this file by itself. Reply in 1-3 lines in her language: what it is, what she must fill in "
          "(the placeholders above), what the honesty check changed, and that she reads it before sending it. Do not repeat "
          "the next line, the path or its first word.")
    print("MED" + "IA:" + out)   # the token is split here so reading this file never looks like a send line
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:   # never a traceback that could echo document text unfiltered
        stop("make-doc failed: " + type(e).__name__ + ": " + str(e)[:300], 4)
