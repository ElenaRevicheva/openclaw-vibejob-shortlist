---
name: pack
description: Load a company's study pack (case task + Elena's deliverables) for coaching. Use ONLY when she sends /pack <company> or "pack <company>". It is NOT a mock interview.
metadata: { "openclaw": { "emoji": "🎓" } }
---

# pack

Do exactly ONE thing: call the exec tool with this command (replace <company> with the company name she typed after pack):

`node /home/ubuntu/cto-aipa/scripts/hs-study-pack.cjs --activate --company="<company>"`

If she typed NO company name (just /pack), run `node /home/ubuntu/cto-aipa/scripts/hs-study-pack.cjs --list` instead.

Then reply with the exec output, copied word for word, including its [proof …] code. Nothing else — no questions, no
mock interview, no "✅ Loaded" deal line. If you did not run the exec in this turn, you have nothing to report.
