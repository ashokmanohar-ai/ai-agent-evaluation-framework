# LLM-as-a-Judge

Use model judgment for qualities that cannot be reliably reduced to exact trace
checks: clarity, relevance, plan feasibility and rationale quality. Do not use it to
decide whether an exact tool ran, arguments matched or approval preceded execution.

Controls implemented here:

- Pydantic-validated `score`, `passed` and non-empty `rationale`.
- versioned prompts outside source code.
- independent provider selection for agent and judge.
- temperature zero configuration and optional repeated judging with median score.
- timeout and malformed-output failure that closes safely.
- provider/model/prompt identity in the report.
- deterministic mock judge for credential-free CI.

Calibrate a live judge against a human-labelled set. Measure agreement, false
positive/negative rates and drift after provider or prompt changes. Blind reviewers
to agent identity when comparing models. Avoid evaluation leakage and do not tune an
agent solely against a fixed public benchmark. Self-evaluation can correlate errors;
prefer a separate judge family plus deterministic gates for material outcomes.
