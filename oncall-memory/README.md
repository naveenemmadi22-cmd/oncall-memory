# On-call Copilot: an incident-response agent that learns with Hindsight

Built for **Hack with Hyderabad 3.0** (AI Agents That Learn Using Hindsight).

## The problem
When production breaks at 3 AM, engineers dig through old Slack threads and postmortems to find "have we seen this before, and what actually fixed it?" Generic LLMs suggest textbook fixes, including ones that have already burned this team.

## What it does
An on-call copilot with persistent memory of every incident: symptoms, root causes, fixes that worked, and fixes that **made things worse**. After each incident, the engineer tells it what really happened, and that feedback is retained so the next triage is better.

**Demo moment:** for a `HikariPool ... Connection is not available` alert, a generic LLM says "increase the connection pool size." The memory-powered agent recalls INC-2044, where exactly that caused a 12-minute extra outage, and instead recommends rollback and killing idle-in-transaction sessions, the fix that worked in INC-2031.

## How Hindsight memory is used
| Hindsight op | Where | Purpose |
|---|---|---|
| `create_bank` (mission + disposition) | `src/memory.py: ensure_bank` | Gives the bank an SRE identity and a skeptical disposition |
| `retain` | `retain_incident`, `retain_outcome` | Stores postmortems (with real timestamps) and engineer feedback on the agent's own suggestions |
| `recall` | `recall_similar` | Pulls relevant past incidents and failed remediations for a new alert (semantic, keyword, graph, temporal) |
| `reflect` | `insights` | Cross-incident reasoning: recurring root causes and failed fixes per service |

Learning loop: **triage -> engineer outcome -> `retain` -> better next triage**.

## Architecture
```
Alert -> agent.triage() --recall--> Hindsight bank (incidents + feedback)
              |                            ^
              v                            | retain (outcome)
        Groq LLM (gpt-oss-120b, fallback qwen3-32b)
              |
              v
   Streamlit UI: side-by-side "without memory" vs "with memory"
```

## Run it
```bash
pip install -r requirements.txt
cp .env.example .env        # add GROQ_API_KEY and Hindsight URL/key
```
Hindsight: use Cloud (https://ui.hindsight.vectorize.io, code `MEMHACK99` for credits) or run the open-source server locally (see https://hindsight.vectorize.io/developer/installation).

```bash
python demo.py --seed       # CLI: before/after + learning loop
streamlit run app.py        # UI: click "Seed incident history" first
```

## Realistic data
`data/incidents.json` holds 8 synthetic postmortems (Kafka poison message, expired SSO cert, Redis eviction, replica lag, etc.). Replace it with your own postmortems to make it real.

## Edge cases handled
- LLM retry plus automatic model fallback on rate limits or malformed responses
- Bank creation is idempotent; empty recall falls back to general practice
- UI surfaces errors instead of crashing

## Roadmap
PagerDuty and Slack ingestion, auto-retain from resolved incident channels, runbook links as Mental Models.
