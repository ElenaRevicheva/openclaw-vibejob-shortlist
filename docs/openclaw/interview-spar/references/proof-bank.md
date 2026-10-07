# Proof bank — the ONLY proofs you may quote (copied verbatim, no model wrote these)

Source: /home/ubuntu/cto-aipa/docs/interview/defense-bank.json (verified 28 Sep 2026) + references/outlook-facts.md.

## code — Who writes the code?
Specialized AI agents do much of the implementation. I own what gets built, what gets accepted, what gets deployed and what happens when it breaks: I write the requirements, decide the tests a change must pass, and accept it only when the tests and the production logs prove it works.

## evals — How do you evaluate an AI system before it ships?
Two layers. Automated tests check every rule on every change — hundreds of them, in about a minute. Then an offline replay re-runs the model on real past decisions, each stored with the posting it was made on. If a change scores worse, it does not ship: a RAG upgrade stayed switched off for exactly that reason.

## rules — What does the model decide, and what does code decide?
Hard facts stated in the input go in code: a country restriction, a pay figure, 'no AI tools'. Judgment calls go to the model. When they disagree, the code checks the source facts, never the model's stated reason — models sometimes give the right verdict with the wrong reason.

## failclosed — What does fail-closed mean in your systems?
When something is wrong, the system refuses instead of guessing. My outreach sends only after one human click and refuses the whole send if an attachment fails to load; my publisher will not print a number it cannot trace to a source.

## fallback — What happens when your LLM provider fails?
Nothing breaks. Every model call has an ordered fallback across five providers — Anthropic, OpenAI, Gemini, Grok and Groq. My Anthropic balance has been at zero for weeks and the systems keep running on the next provider; when Groq retired the models I used, it was a config change, not an outage.

## memory — How do you implement agent memory?
Three kinds: a permanent ledger of decisions for learning; semantic memory — my tutor bot stores conversation turns as embeddings in Postgres with pgvector and retrieves the three most similar before replying (497 memories, no retrieval errors in the last week); and a short session memory, so 'change it' edits the item just created.

## bottleneck — How do you find a bottleneck?
I check the output, not whether the process ran. One of my search paths ran on schedule with its filters silently switched off: a library failed to load and the error went to a log level production never prints. I found it by loading the process exactly as production does; the first fixed run rejected five junk results that used to become CRM deals.

## kpi — How do you measure impact?
I pick the number that tracks money or time, measure it before and after, and keep only changes that move it. A new job source cleared my live filter 72% of the time, measured across all 345 of its postings, so it stayed. I also fix the measurement itself: my replay was scoring on blank postings until I stored the real one behind each decision.

## incident — Tell me about an incident you handled.
My server hit 95% disk because no log had ever been trimmed. I compressed 8.5 GB of logs to 310 MB — removing each original only after checking the copy byte for byte — kept every service running, capped the system journal after a full backup, and set up rotation so it cannot recur.

## client — How do you handle client delivery and SLAs?
I haven't run US-client SLAs yet. I ran delivery at board level for seven years in regulated e-government: vendor coordination, operational delivery, cost and performance reporting. My own systems work the same way: define what 'working' means, measure it from production logs, and get alerted before the client notices.

## growth — How would you grow an account?
Deliver one measurable win in their main bottleneck, show the number, then propose the next bottleneck with a cost and an expected result. As Deputy CEO for business development at a fintech, and in my own outreach loop, I learned clients buy outcomes, not models.

## mcp — What is MCP, and how do you use it?
The Model Context Protocol is a standard way to give an AI agent tools — a CRM, a search engine, a browser. My agents use MCP connectors in my development environment every day; in production my systems call the HubSpot, Resend, Telegram and Trello APIs directly, with code guards on what the model may decide.

## crm — Walk me through your CRM automation.
My acquisition loop runs in production: research, qualify, draft, one human tap, send, then delivery and opens written back to HubSpot — 2,800+ deals so far. Every writer tags its deals with a source prefix, and a daily read-back audit re-reads HubSpot to prove the notes and attachments really landed.

## seo — What is GEO/AEO, and how do you measure it?
Generative and answer-engine optimization: making a company visible and quotable in ChatGPT, Perplexity and Claude, not only Google. My public AI Visibility Audit API scores a site with 34 automated checks; it has run 420+ audits with a median score of 85, and my own hub scores 100/100.

## product — How do you decide what to build?
Bottleneck first: find where money or time is lost, ship the smallest change that tests the fix, measure it, then harden what works. My acceptance criteria are tests a change must pass, and a feature that measures worse does not ship — even a technically impressive one.

## regulated — How do you work under regulation?
Seven years as Deputy CEO and Chief Legal Officer in regulated e-government taught me to treat constraints as product inputs. In my AI systems that means hard rules in code, fail-closed defaults, a human approval before anything irreversible, and no number shown unless it traces back to a record.

## creative — How do you produce a film with AI?
Through a pipeline I built: poems from my own ATUONA universe become shots generated per type after a model bake-off; narration is locked to each clip and the mix is normalised to broadcast loudness; every render is checked before release. Eight films are published; the latest, Crimson Escape, runs 3:36 from 16 shots.

## nodegree — You don't have an engineering degree — why you?
Because the role is outcomes, not a degree: I find the real bottleneck, get the system built and measured, and explain it to the client. My degree isn't in engineering; since May 2025 I have built and run 15 production services through my AI environment.
