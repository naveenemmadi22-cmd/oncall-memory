"""Incident triage agent. Same prompt with and without Hindsight memory, so the difference is visible."""
from . import llm, memory

SYSTEM = (
    "You are an on-call incident response copilot for a fintech SRE team. Be concrete and brief. "
    "Respond in markdown with these sections: **Likely root cause**, **Confidence** (low/med/high and why), "
    "**First actions** (numbered, max 5), **What NOT to do**, **Evidence** (cite incident IDs, or say 'none')."
)

MEMORY_RULES = (
    "You are given TEAM MEMORY: past incidents, outcomes and engineer feedback from this team. "
    "Prefer remediations that worked for this team. Never suggest anything the memory says failed or made things worse. "
    "Cite incident IDs. If memory is irrelevant, say so and fall back to general practice."
)


def triage(alert: str, use_memory: bool = True) -> dict:
    memories: list[dict] = []
    if use_memory:
        memories = memory.recall_similar(alert)
        ctx = "\n".join(f"- ({m['type']}) {m['text']}" for m in memories) or "(nothing relevant)"
        user = f"ALERT:\n{alert}\n\nTEAM MEMORY:\n{ctx}"
        system = SYSTEM + " " + MEMORY_RULES
    else:
        user, system = f"ALERT:\n{alert}", SYSTEM
    return {"answer": llm.chat(system, user), "memories": memories}


def summarize_for_feedback(answer: str) -> str:
    return llm.chat("Summarize the recommended actions in one sentence.", answer)
