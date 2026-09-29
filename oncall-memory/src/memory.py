"""Thin wrapper around Hindsight. Every memory operation the agent uses lives here."""
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "oncall-copilot")
DATA = Path(__file__).resolve().parent.parent / "data" / "incidents.json"

MISSION = (
    "I am the on-call copilot for a fintech SRE team. I remember every incident: symptoms, "
    "root causes, fixes that worked, and fixes that failed. I learn which remediations this "
    "team trusts and which ones made things worse, and I use that to guide new incidents."
)


def client() -> Hindsight:
    return Hindsight(
        base_url=os.getenv("HINDSIGHT_BASE_URL", "http://localhost:8888"),
        api_key=os.getenv("HINDSIGHT_API_KEY") or None,
        timeout=120.0,
    )


def ensure_bank() -> None:
    """Create the memory bank with a mission (safe to call repeatedly)."""
    try:
        client().create_bank(
            bank_id=BANK_ID,
            name="On-call Copilot",
            mission=MISSION,
            disposition={"skepticism": 4, "literalism": 3, "empathy": 2},
        )
    except Exception:
        pass  # bank already exists


def incident_to_text(i: dict) -> str:
    return (
        f"Incident {i['id']} on {i['date']} in service {i['service']}: {i['title']}. "
        f"Symptoms: {i['symptoms']}. Root cause: {i['root_cause']}. "
        f"Resolution: {i['resolution']}. What did NOT work: {i['failed_attempts']}. "
        f"Time to resolve: {i['minutes_to_resolve']} minutes."
    )


def retain_incident(i: dict) -> None:
    client().retain(
        bank_id=BANK_ID,
        content=incident_to_text(i),
        context="incident postmortem",
        timestamp=datetime.fromisoformat(i["date"]),
        document_id=i["id"],
        retain_async=False,
    )


def seed() -> int:
    """Load the synthetic postmortem history into Hindsight."""
    ensure_bank()
    incidents = json.loads(DATA.read_text())
    for i in incidents:
        retain_incident(i)
    return len(incidents)


def retain_outcome(incident_id: str, alert: str, suggestion_summary: str, worked: bool, note: str) -> None:
    """The learning loop: store what the engineer says actually happened."""
    verdict = "WORKED" if worked else "DID NOT WORK"
    client().retain(
        bank_id=BANK_ID,
        content=(
            f"Feedback on incident {incident_id}. Alert: {alert}. Copilot suggested: {suggestion_summary}. "
            f"Outcome: the suggestion {verdict}. Engineer note: {note}"
        ),
        context="engineer feedback on copilot suggestion",
        document_id=f"feedback-{incident_id}",
        retain_async=False,
    )


def recall_similar(alert: str, max_tokens: int = 2500) -> list[dict]:
    res = client().recall(bank_id=BANK_ID, query=alert, budget="mid", max_tokens=max_tokens)
    return [{"type": r.type, "text": r.text} for r in res.results]


def insights(question: str) -> str:
    """Use reflect to reason across all stored incidents (patterns, recurring causes)."""
    ans = client().reflect(bank_id=BANK_ID, query=question, budget="mid", context="SRE retrospective")
    return ans.text
