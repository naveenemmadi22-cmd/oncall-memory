Built an on-call copilot that remembers every outage your team has had. 🧠🚨

Ask a normal LLM about a DB connection-pool timeout: "increase the pool size."
Ask mine: "Don't. That took down prod for 12 extra minutes in INC-2044. Roll back, then kill idle-in-transaction sessions (worked in INC-2031)."

Same model. The difference is memory, powered by Hindsight from Vectorize.
It retains postmortems and engineer feedback, recalls them on new alerts, and gets better with every incident.

Built for Hack with Hyderabad 3.0. Repo + demo in comments 👇
#HackWithHyderabad #AIAgents #Hindsight #SRE #DevOps
