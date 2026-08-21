# Datasets

The repository contains 70 curated cases:

| File | Cases | Coverage |
|---|---:|---|
| `support/support-v1.jsonl` | 16 | ticket, service, knowledge, policy, scheduling, HITL |
| `tool-use/tool-use-v1.jsonl` | 16 | writes, exact arguments, access order, cross-user denial |
| `recovery/recovery-v1.jsonl` | 12 | transient retry and persistent-failure escalation |
| `safety/safety-v1.jsonl` | 13 | prompt/tool injection, forbidden actions, rejection |
| `multi-agent/multi-agent-v1.jsonl` | 13 | routing, handoffs and memory isolation |

Cases carry version, category and tags such as `smoke`, `tool-use`, `grounding`,
`recovery`, `safety`, `high-risk`, `multi-agent` and `memory`. A version change must
document added, removed or materially altered expectations. Baseline comparisons
warn when dataset versions differ.

Validation occurs before agent execution: JSON syntax, Pydantic schema, duplicate
IDs, contradictory tool constraints, missing tags and references outside the tool
policy are rejected. Keep datasets small enough for review, diverse enough to expose
failure modes and separate from prompt/model training data where possible.
