"""Streamlit UI: side-by-side triage, outcome feedback (learning loop), memory explorer."""
import streamlit as st

from src import agent, memory

st.set_page_config(page_title="On-call Copilot (Hindsight)", layout="wide")
st.title("On-call Copilot with Memory")
st.caption("An incident-response agent that remembers every outage, what fixed it, and what made it worse.")

SAMPLES = {
    "Payments latency after deploy": "payments-api p99 latency 4.2s and 5xx at 12%, started 6 min after deploy v2.41.0. Logs: 'HikariPool-1 - Connection is not available, request timed out after 30000ms'. DB CPU 70%.",
    "Partner logins failing": "auth-gateway: SAML assertion validation failed for users from partner org Acme, started exactly at 00:00 UTC, other users fine.",
    "Kafka lag": "notifications consumer lag 1.8M and growing, one partition not advancing, JSON parse exceptions in logs.",
}

with st.sidebar:
    st.header("Setup")
    if st.button("Seed incident history"):
        with st.spinner("Retaining postmortems into Hindsight..."):
            st.success(f"Retained {memory.seed()} incidents")
    st.caption(f"Bank: `{memory.BANK_ID}`")

triage_tab, feedback_tab, memory_tab = st.tabs(["Triage", "Log outcome", "Memory explorer"])

with triage_tab:
    pick = st.selectbox("Sample alert", list(SAMPLES))
    alert = st.text_area("Alert / symptoms", SAMPLES[pick], height=110)
    if st.button("Triage", type="primary"):
        left, right = st.columns(2)
        try:
            with left:
                st.subheader("Without memory")
                with st.spinner("..."):
                    st.markdown(agent.triage(alert, use_memory=False)["answer"])
            with right:
                st.subheader("With Hindsight memory")
                with st.spinner("Recalling past incidents..."):
                    res = agent.triage(alert, use_memory=True)
                st.session_state["last"] = {"alert": alert, "answer": res["answer"]}
                st.markdown(res["answer"])
                with st.expander(f"{len(res['memories'])} memories recalled"):
                    for m in res["memories"]:
                        st.markdown(f"- **{m['type']}**: {m['text']}")
        except Exception as e:
            st.error(f"Something failed: {e}")

with feedback_tab:
    st.write("Tell the copilot what actually happened. This is retained and shapes the next triage.")
    last = st.session_state.get("last")
    inc = st.text_input("Incident ID", "INC-2079")
    worked = st.radio("Did the suggestion work?", ["Yes", "No"], horizontal=True) == "Yes"
    note = st.text_area("What happened / what should be remembered?")
    if st.button("Retain outcome") and last and note:
        summary = agent.summarize_for_feedback(last["answer"])
        memory.retain_outcome(inc, last["alert"], summary, worked, note)
        st.success("Retained. Run the triage again to see the difference.")
    elif not last:
        st.info("Run a triage first.")

with memory_tab:
    q = st.text_input("Ask across all incidents", "What recurring root causes do we see for payments-api?")
    if st.button("Reflect"):
        with st.spinner("Reasoning over memory..."):
            st.markdown(memory.insights(q))
