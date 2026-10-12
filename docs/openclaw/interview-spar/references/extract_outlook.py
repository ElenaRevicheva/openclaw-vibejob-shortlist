# extract_outlook.py — the mechanical extract that makes outlook.txt from outlook.html (no human or model rewrites it).
# Rule: every tag becomes a space, the end of a block element becomes a line break; style/script are dropped.
# Proven 12 Oct 2026: re-running it on outlook.html @ 71a516d reproduces the 7 Oct outlook.txt byte for byte (202/202 lines).
# Usage (from cto-aipa): python3 <this file> < docs/applications/professional-outlook/outlook.html > body.txt
import sys, html.parser
BLOCK = set('address article aside blockquote body dd div dl dt figcaption figure footer form h1 h2 h3 h4 h5 h6 header li main nav ol p pre section table tbody td tfoot th thead title tr ul html head'.split())
class P(html.parser.HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.skip=0; s.buf=[]
    def handle_starttag(s,t,a):
        if t in ('style','script'): s.skip+=1
        else: s.buf.append('\n' if t=='br' else ' ')
    def handle_startendtag(s,t,a): s.buf.append('\n' if t=='br' else ' ')
    def handle_endtag(s,t):
        if t in ('style','script'): s.skip-=1
        else: s.buf.append('\n' if t in BLOCK else ' ')
    def handle_data(s,d):
        if not s.skip: s.buf.append(d)
p=P(); p.feed(sys.stdin.read())
lines=[' '.join(l.split()) for l in ''.join(p.buf).split('\n')]
sys.stdout.write('\n'.join(l for l in lines if l)+'\n')
