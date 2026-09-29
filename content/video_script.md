# Demo video script (about 2 minutes)

**0:00 Hook.** "It's 3 AM. Payments latency is spiking. Do you remember what fixed this last time?"
**0:15 Problem.** Show the alert (Hikari timeouts after deploy v2.41.0).
**0:25 Without memory.** Click Triage; left panel: generic LLM says "increase pool size."
**0:45 With memory.** Right panel: rollback + kill idle-in-transaction sessions, cites INC-2031, warns about INC-2044. Open "memories recalled" to show the evidence.
**1:10 Learning loop.** Go to "Log outcome": "Rollback fixed it in 5 min, missing index in ledger query." Retain.
**1:30 Next incident.** Run a new payments alert; the agent now also cites the fresh outcome.
**1:45 Reflect.** Memory explorer: "What recurring root causes do we see for payments-api?"
**1:55 Close.** "Same model, different memory. Built on Hindsight."

Team-member content deliverables: each member records their own short video per the Content Guide.
