# Technical White Papers

This directory is the publication index for technical white papers associated with the **AI Agent Evaluation Framework** and authored by **Ashok Kumar Manohar**.

## 1. Testing AI Agents

**Testing AI Agents: A Practical Quality Engineering Framework for Autonomous and Agentic Systems**

- [Read the white paper](../WHITEPAPER.md)
- [Citation metadata](../CITATION.cff)
- Version: 1.0
- Published: September 2026

Focus: practical end-to-end Quality Engineering for agentic systems across task completion, tool correctness, trajectories, grounding, approvals, safety, recovery, memory isolation, performance, observability, regression testing and CI/CD quality gates.

---

## 2. Evaluating AI Agents

**Evaluating AI Agents: Metrics, Test Strategies and Quality Gates for Autonomous Systems**

- [Read the white paper](EVALUATING_AI_AGENTS_METRICS_STRATEGIES_QUALITY_GATES.md)
- [Citation metadata](CITATION_EVALUATING_AI_AGENTS.cff)
- Version: 1.0
- Published: September 2026

Focus: Outcome–Trajectory–Tool–Safety–Reliability–Efficiency measurement; task success; tool selection and argument accuracy; trajectory correctness; groundedness; identity and authorization; approvals; recovery; repeated-run stability; efficiency; latency; cost; calibrated LLM judges; human evaluation; baseline regression; risk-based CI/CD profiles; hard gates; missing evidence; observability; and production-to-regression learning.

> **Measurement companion paper:** this publication goes deeper than the practical testing framework by defining how agent behavior should be quantified, compared, gated and governed across both deterministic and probabilistic dimensions.

---

## Reference Implementation

Both publications are supported by the open-source [AI Agent Evaluation Framework](https://github.com/ashokmanohar-ai/ai-agent-evaluation-framework), which demonstrates 70 versioned evaluation cases, provider-independent adapters, normalized traces, deterministic-first task/tool/argument/sequence checks, unsupported-claim detection, approval and safety gates, repeated-run evaluation, baseline regression, structured judges, JSON/HTML/JUnit evidence, FastAPI, CLI, Docker and OpenTelemetry/Phoenix-ready observability.

Related repositories extend these patterns into [Agentic Quality Engineering](https://github.com/ashokmanohar-ai/agentic-quality-engineering-platform), [Enterprise AI Quality Engineering](https://github.com/ashokmanohar-ai/enterprise-ai-quality-engineering-platform), [Continuous Quality Engineering](https://github.com/ashokmanohar-ai/continuous-quality-engineering), [LLM evaluation](https://github.com/ashokmanohar-ai/llm-quality-evaluation-harness) and [AI observability](https://github.com/ashokmanohar-ai/phoenix-llm-observability).

> These are independent practitioner white papers and are not peer-reviewed academic publications, professional certification standards, compliance certifications, security certifications, or statements of production readiness.