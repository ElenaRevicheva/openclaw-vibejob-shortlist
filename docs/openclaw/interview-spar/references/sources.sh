#!/usr/bin/env bash
# The ONLY proofs the interview-spar skill may quote: Elena's own verified records, read live from where they live.
# Nothing here is retyped by a human or a model.
here="$(cd "$(dirname "$0")" && pwd)"

echo "===== outlook (Professional Outlook, mechanical extract of outlook.html)"
cat "$here/outlook.txt"

echo
echo "===== defense-bank (verified interview answers used by the apply kit)"
python3 - <<'PY'
import json
d = json.load(open('/home/ubuntu/cto-aipa/docs/interview/defense-bank.json', encoding='utf-8'))
for e in d['entries']:
    print(f"## defense-bank · {e['id']} — {e['q']}\n{e['a'].strip()}\n")
PY

echo "===== wiki (published AI Ops Wiki incidents)"
for f in /home/ubuntu/aideazz/content/ai-ops-wiki/incidents/*.md; do
  echo "## wiki · $(basename "$f" .md)"
  grep -E '^(title|concepts|symptom|root_cause|fix|verified|rule):' "$f"
  echo
done
