---
name: rules
description: Show, approve or reject the rules OpenClaw proposes from its own repeated mistakes. Use ONLY when she sends /rules, "rules", "approve R1", "reject R2" or "forget L1".
metadata: { "openclaw": { "emoji": "📚" } }
---

# rules

Do exactly ONE thing: call the exec tool with ONE of these commands:

- `/rules` or `rules` (nothing else) → `node /home/ubuntu/cto-aipa/scripts/hs-study-pack.cjs --rules`
- `/rules approve R1` or `approve R1` → `node /home/ubuntu/cto-aipa/scripts/hs-study-pack.cjs --rules --approve=R1`
- `/rules reject R1` or `reject R1` → `node /home/ubuntu/cto-aipa/scripts/hs-study-pack.cjs --rules --reject=R1`
- `/rules forget L1` or `forget L1` → `node /home/ubuntu/cto-aipa/scripts/hs-study-pack.cjs --rules --forget=L1`

(use the id she typed; several ids → one exec per id). Then reply with the exec output, copied word for word, including
its [proof …] code. Nothing else. Never approve, reject or forget a rule she did not name, and never write a rule yourself.
If you did not run the exec in this turn, you have nothing to report.
