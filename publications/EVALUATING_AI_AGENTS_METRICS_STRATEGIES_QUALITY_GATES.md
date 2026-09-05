# Evaluating AI Agents

## Metrics, Test Strategies and Quality Gates for Autonomous Systems

**Technical White Paper — Version 1.0**  
**September 2026**

**Author:** Ashok Kumar Manohar  
**GitHub:** [ashokmanohar-ai](https://github.com/ashokmanohar-ai)  
**Primary reference implementation:** [AI Agent Evaluation Framework](https://github.com/ashokmanohar-ai/ai-agent-evaluation-framework)  
**Related implementations:** [Agentic Quality Engineering Platform](https://github.com/ashokmanohar-ai/agentic-quality-engineering-platform), [Enterprise AI Quality Engineering Platform](https://github.com/ashokmanohar-ai/enterprise-ai-quality-engineering-platform), [LLM Quality Evaluation Harness](https://github.com/ashokmanohar-ai/llm-quality-evaluation-harness), [Continuous Quality Engineering](https://github.com/ashokmanohar-ai/continuous-quality-engineering), and [Phoenix LLM Observability](https://github.com/ashokmanohar-ai/phoenix-llm-observability)

> **Publication note:** This is an independent practitioner white paper supported by open-source reference implementations. It is not a peer-reviewed academic publication, professional certification standard, legal opinion, compliance certification, security certification, or statement of production readiness. Evaluation datasets, thresholds, judge models, safety policy and approval controls must be calibrated for each product, environment and risk profile.

---

## Abstract

AI agents are harder to evaluate than ordinary language-model responses because an agent does not merely produce text. It interprets an objective, plans, selects tools, supplies arguments, observes results, updates state, retries, delegates, requests approval, performs side effects and eventually returns an outcome. A final answer can appear correct even when the execution trajectory was unauthorized, inefficient, unsafe or factually unsupported. Conversely, an agent can follow a reasonable trajectory but fail because a dependency timed out or required data was unavailable.

This white paper presents **AI Agent Evaluation** as an evidence-driven Quality Engineering discipline for measuring the complete behavior of autonomous and semi-autonomous systems. It proposes an **Outcome–Trajectory–Tool–Safety–Reliability–Efficiency model** in which agent quality is assessed across six complementary dimensions rather than reduced to a single score.

The framework distinguishes deterministic evidence from probabilistic judgment. Exact tool selection, arguments, sequencing, authorization, approvals, state changes, retries, latency and structured outcomes should be verified deterministically whenever possible. Semantic qualities such as plan usefulness, final-response clarity or partial-task quality may use calibrated human or model-based judges. Critical safety and authorization failures remain hard blockers regardless of aggregate quality.

The companion open-source implementation demonstrates 70 versioned evaluation cases, provider-independent agent adapters, normalized traces, deterministic task/tool/trajectory/safety metrics, `COMPLETE`/`PARTIAL`/`FAILED` task outcomes, unsupported-claim detection, approval checks, memory isolation tests, repeated-run stability, baseline regression, structured LLM judges, JSON/HTML/JUnit evidence, FastAPI, CLI, Docker, OpenTelemetry-ready tracing and CI/CD gates.

The central proposition is:

> **An AI agent should be released only when the team can prove not just that it reached an acceptable answer, but that it reached the outcome through an authorized, correct, efficient, reproducible and sufficiently safe trajectory.**

---

## 1. Executive Summary

A conventional application test often has a relatively direct oracle:

```text
Input → Deterministic Logic → Output
```

An agentic system may instead execute:

```text
Objective
   ↓
Interpret Context
   ↓
Plan
   ↓
Choose Tool
   ↓
Validate Arguments
   ↓
Execute Tool
   ↓
Observe Result
   ↓
Update State / Retry / Delegate
   ↓
Request Approval if Required
   ↓
Perform Side Effect
   ↓
Generate Final Outcome
```

Every stage can fail independently.

An agent evaluation program therefore needs to answer at least six questions:

1. **Outcome:** Did the agent complete the intended task?
2. **Trajectory:** Did it take an acceptable path?
3. **Tooling:** Did it use the right tools with the right arguments?
4. **Safety:** Did it remain inside identity, authorization, approval and policy boundaries?
5. **Reliability:** Does behavior remain stable across repetition, failures and environment changes?
6. **Efficiency:** Did it complete the task with acceptable latency, model calls, tool calls, tokens and cost?

The evaluation architecture must retain enough evidence to explain every failed gate.

---

## 2. Why Final-Answer Evaluation Is Insufficient

A polished final response does not prove correct agent execution.

Examples:

- The agent says “ticket created” but never called the ticket API.
- The agent returns the right account balance after reading another tenant’s record.
- The agent completes a refund but skips mandatory approval.
- The agent reaches the correct answer after ten unnecessary tool calls and three repeated side effects.
- The agent reports success although the tool returned an error.
- The agent reaches a good answer only one out of three repeated runs.

Agent quality must therefore be based on **execution evidence**, not response plausibility.

---

## 3. The Outcome–Trajectory–Tool–Safety–Reliability–Efficiency Model

A practical agent quality model is:

\[
Q_{agent} = f(O, T_r, T_o, S, R, E)
\]

where:

- \(O\) = outcome quality;
- \(T_r\) = trajectory quality;
- \(T_o\) = tool-use quality;
- \(S\) = safety and authorization;
- \(R\) = reliability and stability;
- \(E\) = efficiency and operational quality.

This is not an invitation to hide everything inside one weighted score. Critical safety failures should remain explicit hard gates.

---

## 4. Evaluation Starts with a Quality Contract

Before choosing metrics, define the agent quality contract.

A useful contract specifies:

- intended objective;
- allowed and forbidden tools;
- required tool arguments;
- mandatory and forbidden steps;
- expected state changes;
- required facts in the final response;
- authorization boundaries;
- approval requirements;
- retry and loop limits;
- acceptable latency and cost;
- recovery expectations;
- safety policy;
- evidence required for release.

Without this contract, metrics become disconnected numbers rather than release controls.

---

## 5. Versioned Evaluation Datasets

Agent evaluation depends on representative tasks, not isolated demos.

Each case should have:

- stable ID;
- task description;
- input/context;
- expected task intent;
- required tools;
- forbidden tools;
- expected arguments;
- required steps or ordered subsequences;
- expected facts or state changes;
- approval expectations;
- risk tags;
- dataset version;
- provenance.

Production incidents should become permanent evaluation cases after sanitization and review.

---

## 6. Normalized Agent Traces

Every agent adapter should produce a normalized trace independent of framework or provider.

A trace should retain:

- agent name/version;
- model/deployment/version;
- input and redacted context;
- planning/state transitions where available;
- tool calls;
- tool arguments;
- tool results;
- errors;
- retries;
- approvals;
- handoffs;
- final output;
- latency;
- token/cost metadata;
- termination reason.

The trace is the primary evidence object for agent evaluation.

---

## 7. Deterministic-First Evaluation

Use deterministic assertions wherever software can establish truth.

Examples:

- exact tool name;
- forbidden-tool absence;
- argument type and value;
- account/tenant identifier;
- tool sequence;
- approval-before-execution;
- retry limit;
- loop limit;
- exact structured state change;
- final-output consistency with tool result;
- latency threshold;
- duplicate side-effect detection.

A language model should not judge something that code can prove directly.

---

## 8. Outcome Metrics

Outcome metrics answer whether the requested goal was achieved.

Useful metrics include:

- task success rate;
- complete/partial/failed rate;
- required-fact recall;
- state-change correctness;
- final-answer correctness;
- business-rule completion;
- escalation correctness.

Outcome should be derived from observed execution plus final evidence, not the agent’s self-reported success.

---

## 9. COMPLETE, PARTIAL and FAILED

Binary pass/fail can lose useful diagnostic information.

A practical model is:

- **COMPLETE:** required execution and outcome evidence are satisfied.
- **PARTIAL:** meaningful progress occurred, but one or more required outcomes are missing.
- **FAILED:** the task objective was not achieved or a hard blocker occurred.

Critical safety or authorization violations should force failure even when functional completion occurred.

---

## 10. Tool Selection Accuracy

The agent must choose a tool that is both relevant and permitted.

Measure:

- required-tool recall;
- forbidden-tool violation rate;
- unnecessary-tool rate;
- wrong-tool rate;
- tool hallucination rate.

Tool discovery does not imply authorization to use every discovered tool.

---

## 11. Tool Argument Correctness

Correct tool selection is insufficient if arguments are wrong.

Evaluate:

- required arguments present;
- types valid;
- identifiers exact;
- tenant/account/resource scope correct;
- values inside policy bounds;
- date/time equivalence where applicable;
- no prohibited fields;
- no untrusted values copied into privileged parameters without validation.

Argument validation is a high-value deterministic control.

---

## 12. Tool-Result Use

An agent must correctly interpret what a tool returned.

Check:

- final claims match tool output;
- failed tool calls are not reported as successful;
- partial results are represented accurately;
- stale results are not reused after state change;
- tool errors trigger expected recovery or safe stop.

This metric catches agents that “sound right” while ignoring execution evidence.

---

## 13. Trajectory Correctness

Trajectory evaluation asks whether the route to the outcome was acceptable.

Possible checks:

- mandatory step coverage;
- forbidden step absence;
- ordered subsequence correctness;
- approval placement;
- correct branching;
- no repeated write action;
- valid handoff;
- valid termination.

A trajectory can be correct even when implementations differ, so evaluate necessary constraints rather than overfitting to one exact path.

---

## 14. Sequence Metrics

For tasks where order matters, compare observed steps with required ordering constraints.

Examples:

```text
Authenticate → Read → Validate → Approve → Write → Verify
```

Useful failure codes include:

- `MISSING_STEP`;
- `WRONG_SEQUENCE`;
- `FORBIDDEN_STEP`;
- `DUPLICATE_SIDE_EFFECT`;
- `APPROVAL_AFTER_ACTION`.

Actionable failure codes improve debugging and regression ownership.

---

## 15. Planning Quality

Planning can be evaluated at two levels.

Deterministically verify:

- required plan stages;
- forbidden actions;
- policy-required checks;
- termination conditions.

Use calibrated semantic evaluation only for qualities such as:

- plan coherence;
- relevance;
- completeness;
- unnecessary complexity.

Internal chain-of-thought should not be required as evaluation evidence. Evaluate observable actions, structured plan artifacts where intentionally exposed, and traceable outcomes.

---

## 16. Groundedness and Evidence Use

An agent’s claims should be supported by observable input, retrieval, tool results or approved state.

For each structured fact:

```text
Claim → Supporting Evidence → Source/Tool/State
```

Flag:

- unsupported claims;
- contradicted claims;
- stale evidence;
- missing provenance;
- claimed actions with no matching execution event.

---

## 17. Hallucinated Tool Use

A particularly important agent failure is claiming that an action occurred when no tool call exists.

Examples:

- “I sent the email” without a send event.
- “The order was cancelled” without a cancellation call.
- “Your account was updated” without a state-changing operation.

This should be a deterministic hard failure for consequential workflows.

---

## 18. Identity and Authorization Metrics

Agents that act on systems require identity-aware evaluation.

Measure:

- correct principal used;
- correct delegated scope;
- tenant/account boundary respected;
- denied action remains denied;
- privilege escalation attempts rejected;
- resource ownership enforced;
- agent never substitutes discovery for authority.

Authorization is an application/security control, not an LLM quality score.

---

## 19. Human Approval Metrics

For high-impact actions, verify:

- approval was required;
- correct approver role was used;
- approval preceded execution;
- approval matched the exact action/artifact;
- approval had not expired;
- rejection stopped the action;
- execution did not exceed approved scope.

A rejected action that still executes is a critical failure.

---

## 20. Safety Metrics

Safety evaluation should cover both content and action.

Agent safety metrics may include:

- forbidden action rate;
- unauthorized tool-call rate;
- prompt-injection success rate;
- secret leakage rate;
- cross-tenant access rate;
- approval bypass rate;
- unsafe retry rate;
- unsafe fallback rate;
- policy adherence rate.

One critical safety event can be more important than hundreds of successful low-risk tasks.

---

## 21. Prompt-Injection Evaluation

Test direct and indirect injection through:

- user messages;
- retrieved documents;
- tool outputs;
- web pages;
- memory;
- delegated agent messages.

The expected result should be defined in terms of observable policy-compliant behavior rather than whether the model “recognized” the injection.

---

## 22. Memory Isolation

Stateful agents require memory-quality tests.

Evaluate:

- no cross-user memory leakage;
- no cross-tenant context reuse;
- stale memory expiration;
- sensitive fields not persisted unnecessarily;
- memory poisoning does not override authoritative policy;
- reset and session boundaries work.

Memory isolation should be treated as a security and correctness gate.

---

## 23. Recovery Metrics

Agents operate in failure-prone environments.

Measure behavior after:

- timeout;
- 429/rate limit;
- transient 5xx;
- unavailable tool;
- malformed tool result;
- missing data;
- partial completion;
- rejected approval.

A good recovery strategy may retry, choose an approved fallback, escalate or stop safely.

---

## 24. Retry Quality

Retry evaluation should check:

- retryable vs non-retryable classification;
- bounded attempt count;
- backoff policy;
- no duplicate side effect;
- no widening of authorization;
- recovery outcome;
- stop condition.

More retries are not automatically more reliable.

---

## 25. Loop Detection

Agent loops waste time and cost and may create repeated side effects.

Measure:

- total steps;
- repeated identical tool calls;
- repeated state transitions;
- lack of progress;
- maximum loop depth;
- termination reason.

Loop guards belong in runtime policy and evaluation policy.

---

## 26. Efficiency Metrics

Efficiency is task-relative.

Useful measures include:

- tool calls per successful task;
- model calls per successful task;
- steps per successful task;
- retries per task;
- tokens per successful task;
- cost per successful task;
- latency per successful task;
- useful-call ratio.

Efficiency should never incentivize bypassing safety or required verification.

---

## 27. Latency Metrics

For agentic systems, measure more than one request latency.

Potential metrics:

- time to first action;
- time to first token;
- per-tool latency;
- per-model-turn latency;
- total trajectory latency;
- approval wait time;
- recovery latency;
- p50/p95/p99 task latency.

Multi-turn agent workloads should be treated as trajectories, not unrelated requests.

---

## 28. Cost Metrics

Track:

- input/output tokens;
- model cost per turn;
- model cost per task;
- tool/API cost;
- judge/evaluator cost;
- retry cost;
- cost per successful task.

A cheaper agent that succeeds less often can be more expensive per useful outcome.

---

## 29. Reliability Across Repeated Runs

Because agents are probabilistic, run representative cases multiple times.

Measure:

- task success variance;
- tool-selection variance;
- argument variance;
- trajectory variance;
- safety variance;
- latency variance;
- cost variance.

A single successful run should not be interpreted as stable behavior.

---

## 30. Stability and Reproducibility

Store enough configuration to reproduce evaluation context:

- agent version;
- model/deployment;
- prompt version;
- tool schemas;
- policy version;
- dataset version;
- evaluator version;
- sampling parameters;
- environment;
- timestamp/build commit.

Reproducibility is imperfect in probabilistic systems, but configuration provenance is still mandatory.

---

## 31. Baseline Comparison

Compare a candidate agent with an approved baseline on shared cases.

Track:

- new task failures;
- fixed failures;
- tool correctness delta;
- safety drift;
- latency delta;
- cost delta;
- trajectory-length delta;
- per-risk-segment changes.

Absolute thresholds and candidate-versus-baseline regression both matter.

---

## 32. Regression Budgets

Not every small change warrants blocking, but critical dimensions need zero tolerance.

Example policy:

```text
Safety regression             = 0 tolerated
Authorization regression      = 0 tolerated
Approval bypass               = 0 tolerated
Task success delta            >= -2 percentage points
P95 latency delta             <= +10%
Cost per successful task      <= +10%
Tool-call efficiency          no material regression
```

Numbers are illustrative and must be calibrated to product risk.

---

## 33. Risk-Based Evaluation Profiles

Use different depth by delivery stage.

### Pull Request

- deterministic contract checks;
- smoke agent tasks;
- tool/argument checks;
- critical safety regressions;
- no missing mandatory evidence.

### Nightly

- broader datasets;
- repeated runs;
- recovery scenarios;
- adversarial cases;
- performance/cost trends.

### Release

- full risk-weighted suite;
- baseline comparison;
- high-impact approval cases;
- security and authorization;
- performance/cost;
- final retained evidence.

---

## 34. Hard Gates

Examples of hard blockers:

- unauthorized action;
- cross-tenant access;
- forbidden tool use;
- required approval bypassed;
- claimed side effect without execution;
- critical secret leakage;
- required evidence missing;
- evaluation infrastructure failure that invalidates decision confidence.

A weighted score must never turn these into a pass.

---

## 35. Warning Gates

Warnings can cover degradations that require review but are not automatically release-blocking.

Examples:

- moderate latency increase;
- mild tool-call inefficiency;
- judge-quality decrease inside approved tolerance;
- small cost increase;
- non-critical partial task degradation.

Warnings should produce an explicit conditional state, not disappear inside averages.

---

## 36. Advisory Metrics

Some metrics are useful for trend analysis without direct gating.

Examples:

- average trajectory length;
- average reasoning/tool turns;
- distribution of tool categories;
- average response verbosity;
- non-critical judge score;
- cost by task type.

Advisory metrics become gates only after sufficient calibration and governance.

---

## 37. LLM-as-a-Judge for Agents

Use judges for semantic dimensions that deterministic checks cannot establish reliably.

Examples:

- plan usefulness;
- response relevance;
- completeness;
- explanation quality;
- nuanced task fulfillment.

Do not delegate to a judge:

- exact tool names;
- exact arguments;
- authorization;
- approval timing;
- schema validity;
- duplicate side effects;
- deterministic state changes.

Judge prompt/model/version and calibration data should be recorded.

---

## 38. Human Evaluation

Human review remains valuable for:

- ambiguous task outcomes;
- high-impact domain behavior;
- judge disagreement;
- novel failure modes;
- policy exceptions;
- calibration datasets.

Human review should be structured with explicit rubrics rather than informal “looks good” assessment.

---

## 39. Agreement and Calibration

For semantic judges, evaluate agreement with human-labelled cases.

Useful diagnostics:

- percent agreement;
- confusion matrix;
- precision/recall by failure type;
- Cohen’s kappa where appropriate;
- judge disagreement rate;
- repeated-run stability;
- false-pass rate on critical examples.

Calibration is required before judge scores influence release gates.

---

## 40. Multi-Agent Evaluation

Multi-agent systems add new quality dimensions:

- correct delegation;
- role-boundary adherence;
- handoff completeness;
- no authority amplification;
- no circular delegation;
- shared-state consistency;
- conflict resolution;
- aggregate latency/cost;
- end-to-end task outcome.

Evaluate both each agent and the orchestration system.

---

## 41. Agent-to-Agent Handoffs

A handoff should preserve:

- task intent;
- required evidence;
- identity/authorization context;
- constraints;
- unresolved risks;
- provenance.

A downstream agent should not receive broader authority merely because another agent delegated work.

---

## 42. Observability as Evaluation Infrastructure

Evaluation requires traces that expose:

```text
Task
 → Agent state
 → Model call
 → Tool selection
 → Tool call
 → Tool result
 → Retry/handoff
 → Approval
 → Final output
```

Observability should make it possible to localize whether a failure originated in planning, retrieval, model generation, tool execution, authorization, dependency behavior or final synthesis.

---

## 43. Failure Taxonomy

A useful taxonomy includes:

- `TASK_INCOMPLETE`;
- `WRONG_TOOL`;
- `FORBIDDEN_TOOL`;
- `INVALID_ARGUMENT`;
- `WRONG_SEQUENCE`;
- `UNSUPPORTED_CLAIM`;
- `APPROVAL_MISSING`;
- `AUTHORIZATION_VIOLATION`;
- `CROSS_TENANT_ACCESS`;
- `RETRY_EXHAUSTED`;
- `LOOP_DETECTED`;
- `DUPLICATE_SIDE_EFFECT`;
- `TOOL_RESULT_IGNORED`;
- `MEMORY_LEAK`;
- `SAFETY_POLICY_VIOLATION`;
- `LATENCY_REGRESSION`;
- `COST_REGRESSION`;
- `EVALUATOR_FAILURE`.

Failure codes support routing, dashboards and trend analysis.

---

## 44. Quality-Gate Decision Model

A release decision can be expressed as:

```text
Required evidence complete?
        ↓ no
       FAIL
        ↓ yes
Any critical safety/auth failure?
        ↓ yes
       FAIL
        ↓ no
Task/tool/trajectory thresholds satisfied?
        ↓ no
  FAIL or CONDITIONAL
        ↓ yes
Baseline regression within budget?
        ↓ no
  FAIL or CONDITIONAL
        ↓ yes
Performance/cost acceptable?
        ↓ no
  CONDITIONAL or FAIL
        ↓ yes
       PASS
```

The decision and supporting evidence should be retained.

---

## 45. Missing Evidence Is Not a Pass

If a mandatory dataset, trace, security suite, approval test or evaluator did not run, the gate should report missing evidence explicitly.

Do not convert:

```text
not evaluated
```

into:

```text
zero defects
```

This is one of the most important controls in AI release governance.

---

## 46. Infrastructure Failure

Distinguish product quality failure from evaluation-system failure.

Examples:

- malformed dataset;
- missing evaluator configuration;
- trace ingestion failure;
- expired test credential;
- unavailable judge deployment;
- corrupt evidence artifact.

A broken evaluation system should block confidence in the release decision rather than silently pass the product.

---

## 47. CI/CD Integration

A production evaluation pipeline should:

1. detect relevant changes;
2. choose a risk-based evaluation profile;
3. validate datasets/configuration;
4. execute deterministic suites;
5. execute semantic evaluators where required;
6. retain normalized traces;
7. compare against baseline;
8. apply hard and warning gates;
9. publish machine-readable and human-readable evidence;
10. retain the release decision.

---

## 48. Production Monitoring and Feedback

Offline evaluation cannot predict every production failure.

Production signals should feed back into evaluation:

```text
Observed failure
   ↓
Locate trace
   ↓
Sanitize evidence
   ↓
Reproduce
   ↓
Add evaluation case
   ↓
Fix
   ↓
Verify candidate vs baseline
   ↓
Retain regression permanently
```

This creates durable quality intelligence.

---

## 49. Key Performance Indicators

Possible program-level KPIs include:

### Quality

- task success rate;
- critical safety failure rate;
- tool correctness;
- unsupported-claim rate;
- authorization violation rate;
- recovery success rate.

### Stability

- repeated-run variance;
- regression escape rate;
- baseline drift;
- flaky evaluation rate.

### Efficiency

- tool calls per success;
- model calls per success;
- tokens per success;
- cost per success;
- p95 task latency.

### Engineering

- production failures converted to regression cases;
- mean time to diagnose agent failure;
- evaluation coverage by risk category;
- percentage of release decisions with complete evidence.

---

## 50. Anti-Patterns

Avoid:

- evaluating only the final answer;
- judging exact tool use with another LLM;
- treating tool discovery as permission;
- averaging away critical safety failures;
- allowing retries to hide instability;
- using one tiny happy-path dataset;
- trusting self-reported agent success;
- hard-coding one exact trajectory when several paths are valid;
- reporting model-judge scores without calibration;
- treating missing evidence as zero findings;
- changing agent, model, prompts and tools simultaneously without versioning;
- claiming production readiness from synthetic evaluation alone.

---

## 51. Reference Implementation Mapping

The companion **AI Agent Evaluation Framework** demonstrates:

- 70 curated versioned evaluation cases;
- provider-independent `AgentAdapter`;
- normalized `AgentTrace`;
- deterministic task/tool/argument/sequence metrics;
- grounding and unsupported-claim checks;
- approval and safety checks;
- recovery and memory-isolation scenarios;
- repeated-run evaluation;
- hard safety gates;
- transparent weighted scoring;
- baseline creation and regression comparison;
- structured LLM judge integration;
- JSON, HTML and JUnit evidence;
- CLI, FastAPI and Docker;
- OpenTelemetry-ready boundaries and optional Phoenix integration;
- credential-free deterministic CI.

The implementation is reference evidence, not a claim that one fixed metric set is universal.

---

## 52. Standards and Industry Alignment

This framework is consistent with several current industry directions:

- **NIST AI Agent Standards Initiative (2026):** secure and interoperable agents, including research into agent authentication, identity infrastructure and security evaluations.
- **NIST NCCoE Agent Identity and Authorization work (2026):** applying identity and authorization controls to agents with emphasis on identification, auditing and prompt-injection risk.
- **MLCommons Agentic Inference work (2026):** treating agentic workloads as multi-turn trajectories with dependent turns and growing context rather than isolated requests.
- **NVIDIA/RAGAS-style agentic metrics:** distinguishing intermediate tool-use correctness, final goal accuracy and full-trajectory evaluation.
- **OpenTelemetry/OpenInference:** trace-based visibility for model, tool and agent execution.

Alignment is a design aid, not certification.

---

## 53. Adoption Roadmap

### Stage 1 — Trace

Capture tool calls, results, state, approvals and final output.

### Stage 2 — Deterministic Metrics

Add tool, arguments, sequence, task and safety checks.

### Stage 3 — Versioned Datasets

Create representative functional, recovery and adversarial cases.

### Stage 4 — Baselines and Stability

Run repeated evaluations and candidate-versus-baseline comparison.

### Stage 5 — Semantic Evaluation

Introduce calibrated judges only for genuinely semantic criteria.

### Stage 6 — CI/CD Gates

Add risk-based PR, nightly and release profiles.

### Stage 7 — Production Feedback

Convert confirmed incidents into permanent regression cases.

---

## 54. Conclusion

AI-agent evaluation is not a chatbot scoring exercise. It is a systems-quality discipline.

A trustworthy program measures:

- whether the task was completed;
- whether the execution trajectory was acceptable;
- whether the right tools and arguments were used;
- whether identity, authorization and approvals were respected;
- whether claims were grounded in observed evidence;
- whether the agent recovered safely from failure;
- whether behavior remained stable across repeated runs;
- whether latency and cost stayed inside acceptable envelopes;
- whether the release had complete, retained evidence.

The most important principle is simple:

> **Evaluate the outcome, the path, the authority, the evidence and the cost—not merely the sentence the agent produced at the end.**

---

## References

1. NIST, **AI Agent Standards Initiative**, 2026. https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative
2. NIST NCCoE, **Accelerating the Adoption of Software and Artificial Intelligence Agent Identity and Authorization**, 2026. https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd
3. MLCommons, **Agentic Inference for MLPerf Inference**, July 2026. https://mlcommons.org/2026/07/agentic-inference-for-mlperf-inference/
4. NVIDIA NeMo Platform, **Agentic Evaluation Metrics**. https://docs.nvidia.com/nemo-platform/documentation/evaluate-models/metrics/agentic-metrics
5. OpenTelemetry, **Generative AI Semantic Conventions**. https://opentelemetry.io/docs/specs/semconv/gen-ai/
6. OpenInference, **Semantic Conventions for AI Observability**. https://github.com/Arize-ai/openinference

---

## License

This white paper is released under the repository's MIT License.