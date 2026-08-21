from __future__ import annotations

from pathlib import Path

from agent_eval.adapters.mock_agent import MockAgentAdapter
from agent_eval.core.registry import EvaluatorRegistry
from agent_eval.core.runner import EvaluationRunner
from agent_eval.evaluators.deterministic import (
    EfficiencyEvaluator,
    GroundingEvaluator,
    PlanAdherenceEvaluator,
    SequenceEvaluator,
    TaskCompletionEvaluator,
    ToolArgumentEvaluator,
    ToolResultUsageEvaluator,
    ToolSelectionEvaluator,
)
from agent_eval.evaluators.model_based import ResponseQualityEvaluator
from agent_eval.evaluators.performance import CostEvaluator, LatencyEvaluator, TokenUsageEvaluator
from agent_eval.evaluators.recovery import RecoveryEvaluator, RetryCorrectnessEvaluator
from agent_eval.evaluators.safety import (
    HumanApprovalEvaluator,
    MultiAgentSafetyEvaluator,
    SafetyEvaluator,
    SafetyPolicy,
)
from agent_eval.policies.loader import load_tool_policy, load_yaml
from agent_eval.providers.factory import create_judge_provider
from agent_eval.tracing.otel import configure_tracing


def build_default_runner(
    *,
    quality_gate_path: str | Path = "config/quality-gates.yaml",
    tool_policy_path: str | Path = "config/tool-policy.yaml",
    provider_name: str | None = None,
    judge_repeats: int = 1,
) -> EvaluationRunner:
    configure_tracing()
    provider = create_judge_provider(provider_name)
    policy = SafetyPolicy(load_tool_policy(tool_policy_path))
    registry = EvaluatorRegistry()
    for evaluator in [
        TaskCompletionEvaluator(),
        ToolSelectionEvaluator(),
        ToolArgumentEvaluator(),
        ToolResultUsageEvaluator(),
        PlanAdherenceEvaluator(),
        SequenceEvaluator(),
        GroundingEvaluator(),
        EfficiencyEvaluator(),
        RecoveryEvaluator(),
        RetryCorrectnessEvaluator(),
        HumanApprovalEvaluator(),
        SafetyEvaluator(policy),
        MultiAgentSafetyEvaluator(),
        LatencyEvaluator(),
        TokenUsageEvaluator(),
        CostEvaluator(),
        ResponseQualityEvaluator(provider, repeats=judge_repeats),
    ]:
        registry.register(evaluator)
    return EvaluationRunner(
        adapter=MockAgentAdapter(),
        registry=registry,
        judge_provider=provider,
        quality_gate_config=load_yaml(quality_gate_path),
    )
