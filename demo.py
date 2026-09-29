"""CLI demo: seed history, then show the same alert triaged without vs with memory, then the learning loop."""
import sys

from src import agent, memory

ALERT = (
    "payments-api p99 latency 4.2s and 5xx at 12%, started 6 minutes after deploy v2.41.0. "
    "Logs: 'HikariPool-1 - Connection is not available, request timed out after 30000ms'. DB CPU 70%."
)


def show(title: str, text: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}\n{text}")


if __name__ == "__main__":
    if "--seed" in sys.argv:
        print(f"Seeded {memory.seed()} incidents into Hindsight bank '{memory.BANK_ID}'")
    show("ALERT", ALERT)
    show("1) WITHOUT MEMORY (generic LLM)", agent.triage(ALERT, use_memory=False)["answer"])
    r = agent.triage(ALERT, use_memory=True)
    show("2) WITH HINDSIGHT MEMORY", r["answer"])
    show("Memories recalled", "\n".join(f"- {m['text'][:140]}..." for m in r["memories"][:5]))

    # Learning loop: engineer reports outcome, agent retains it, next incident benefits.
    memory.retain_outcome(
        "INC-2079", ALERT, "Roll back v2.41.0 then kill idle-in-transaction sessions", True,
        "Rollback fixed it in 5 min. Root cause was a missing index in the new ledger query.",
    )
    show("3) NEXT INCIDENT (after feedback was retained)",
         agent.triage("payments-api 5xx spike after deploy v2.44.1, Hikari timeouts", use_memory=True)["answer"])
    show("Patterns (reflect)", memory.insights("What recurring root causes and failed remediations do we see for payments-api?"))
