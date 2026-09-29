# Your On-Call Engineer Forgets. Your Agent Shouldn't.

*(Draft: adapt to the official Content Guide's format and length.)*

Every SRE team has the same 3 AM moment: an alert fires, and someone asks, "Haven't we seen this before?" Somebody digs through Slack, a stale wiki page, a postmortem PDF. Meanwhile the clock runs.

I built **On-call Copilot**, an incident-response agent with real memory, using Hindsight from Vectorize.

## Why a generic LLM isn't enough
Paste a `HikariPool: Connection is not available` error into a stateless chatbot and it says: increase the pool size. Reasonable. But on my team's data, that exact fix once turned a slowdown into a 12-minute full outage. The model can't know that. Our memory can.

## How memory works here
- **Retain:** every postmortem (symptoms, root cause, what worked, what failed) and every engineer's feedback on the agent's own advice.
- **Recall:** for a new alert, Hindsight's multi-strategy search finds past incidents by meaning, keywords, entities and time.
- **Reflect:** cross-incident questions like "what keeps breaking payments-api?"
- **Learning loop:** after an incident, the engineer says whether the advice worked. That outcome is retained, so the next triage improves.

## The before/after
Without memory: generic advice, including the harmful one. With memory: rollback first, kill idle-in-transaction sessions, cites INC-2031 and INC-2044, and explicitly warns against raising the pool size.

## What I learned
1. Store *failures*, not just fixes. "What did NOT work" is the most valuable memory.
2. Write memories as narratives with dates and IDs so recall is precise.
3. Keep memory visible in the UI. The recalled-memories panel is what makes people trust the answer.

Code: <your GitHub link>
