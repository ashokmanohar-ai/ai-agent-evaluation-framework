# Live Agent Evaluation Lab

**Live demo:** https://agent-evaluation-lab.vercel.app  
**Portfolio case study:** https://ashok-kumar-manohar-portfolio.vercel.app/case-studies/agent-evaluation-lab

## What the live demo proves

The browser demo exposes a visible 8-task golden dataset and executes five deterministic trials per task. Each run creates 40 inspectable trial records and calculates task success, tool correctness, safety, latency, flakiness and a release decision from explicit thresholds.

```text
Golden tasks → repeated trials → trajectory/tool/safety evidence → regression → release gate
```

The deterministic browser engine is intentionally small and credential-free. It is a recruiter walkthrough, not a substitute for the framework in this repository.

## What this repository adds

This repository is the deeper engineering proof: 70 versioned cases, provider-independent agent adapters, normalized traces, deterministic and optional semantic evaluators, safety/approval gates, baseline regression, JSON/HTML/JUnit evidence, API/CLI interfaces, Docker, OpenTelemetry and CI.

## 3-minute recruiter route

1. Open the live demo and inspect **Golden Dataset**.
2. Run the 5-trial evaluation and inspect generated records and the release gate.
3. Return here and inspect `datasets/`, `src/agent_eval/`, `config/`, `tests/` and `.github/workflows/`.
4. Review the explicit limitations in the main README.

## Integrity statement

Live-demo values are generated from deterministic synthetic scenarios. They are not presented as production-agent telemetry. Production-agent quality requires representative datasets, real adapters, calibrated thresholds and environment-specific outcome evidence.
