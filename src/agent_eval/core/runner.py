from __future__ import annotations

import platform
import statistics
import uuid
from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any

from agent_eval.adapters.base import AgentAdapter
from agent_eval.core.registry import EvaluatorRegistry
from agent_eval.models.dataset import EvaluationCase, EvaluationDataset
from agent_eval.models.enums import MetricStatus
from agent_eval.models.result import (
    CaseResult,
    EvaluationRun,
    ReproducibilityMetadata,
)
from agent_eval.models.trace import AgentInput, ExecutionContext
from agent_eval.policies.quality_gate import apply_quality_gate
from agent_eval.providers.protocol import JudgeProvider
from agent_eval.tracing.collector import evaluation_span


class EvaluationRunner:
    def __init__(
        self,
        adapter: AgentAdapter,
        registry: EvaluatorRegistry,
        judge_provider: JudgeProvider,
        quality_gate_config: dict[str, Any],
        *,
        framework_version: str = "1.0.0",
    ) -> None:
        self.adapter = adapter
        self.registry = registry
        self.judge_provider = judge_provider
        self.quality_gate_config = quality_gate_config
        self.framework_version = framework_version

    async def run(
        self,
        dataset: EvaluationDataset,
        *,
        tags: set[str] | None = None,
        runs_per_case: int = 1,
    ) -> EvaluationRun:
        if runs_per_case < 1:
            raise ValueError("runs_per_case must be at least 1")
        selected = [case for case in dataset.cases if not tags or tags.intersection(case.tags)]
        if not selected:
            raise ValueError("no evaluation cases matched the selected tags")
        started_at = datetime.now(UTC)
        run_id = str(uuid.uuid4())
        run = EvaluationRun(
            run_id=run_id,
            agent_name=self.adapter.name,
            agent_version=self.adapter.version,
            dataset_version=dataset.version,
            started_at=started_at,
            reproducibility=ReproducibilityMetadata(
                framework_version=self.framework_version,
                agent_name=self.adapter.name,
                agent_version=self.adapter.version,
                dataset_version=dataset.version,
                evaluator_version="1.0.0",
                judge_provider=self.judge_provider.name,
                judge_model=self.judge_provider.model,
                judge_prompt_version="response-quality-v1",
                temperature=0.0,
                runs_per_case=runs_per_case,
                python_version=platform.python_version(),
            ),
        )
        with evaluation_span(
            "evaluation.run",
            {"evaluation.run_id": run_id, "evaluation.case_count": len(selected)},
        ):
            for case in selected:
                for run_index in range(1, runs_per_case + 1):
                    result = await self._run_case(run_id, case, run_index)
                    run.case_results.append(result)
        run.completed_at = datetime.now(UTC)
        self._aggregate(run)
        run.gate = apply_quality_gate(run, self.quality_gate_config)
        return run

    async def _run_case(self, run_id: str, case: EvaluationCase, run_index: int) -> CaseResult:
        case_run_id = f"{run_id}:{case.id}:{run_index}"
        context = ExecutionContext(run_id=case_run_id, case_id=case.id, metadata=case.metadata)
        input_data = AgentInput.model_validate(case.input)
        with evaluation_span(
            "evaluation.case",
            {"evaluation.case_id": case.id, "evaluation.run_index": run_index},
        ):
            trace = await self.adapter.run(input_data, context)
            metrics = {
                evaluator.name: await evaluator.evaluate(case, trace)
                for evaluator in self.registry.all()
            }
        failures = [failure for metric in metrics.values() for failure in metric.failures]
        failed = any(metric.status == MetricStatus.FAIL for metric in metrics.values())
        return CaseResult(
            case_id=case.id,
            description=case.description,
            status=MetricStatus.FAIL if failed else MetricStatus.PASS,
            trace=trace,
            metrics=metrics,
            tags=case.tags,
            failures=failures,
            run_index=run_index,
        )

    @staticmethod
    def _aggregate(run: EvaluationRun) -> None:
        scores: dict[str, list[float]] = defaultdict(list)
        tag_scores: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        latencies: list[int] = []
        failures: Counter[str] = Counter()
        case_passes: dict[str, list[bool]] = defaultdict(list)
        for case in run.case_results:
            latencies.append(case.trace.total_duration_ms)
            case_passes[case.case_id].append(case.status == MetricStatus.PASS)
            for failure in case.failures:
                failures[failure.code.value] += 1
            for name, metric in case.metrics.items():
                if metric.status != MetricStatus.SKIP:
                    scores[name].append(metric.score)
                    for tag in case.tags:
                        tag_scores[tag][name].append(metric.score)
        run.metrics = {name: statistics.fmean(values) for name, values in scores.items() if values}
        run.tag_metrics = {
            tag: {name: statistics.fmean(values) for name, values in metrics.items() if values}
            for tag, metrics in tag_scores.items()
        }
        run.failure_summary = dict(failures.most_common())
        sorted_latency = sorted(latencies)
        run.percentiles_ms = {
            "p50": _nearest_rank(sorted_latency, 0.50),
            "p95": _nearest_rank(sorted_latency, 0.95),
            "p99": _nearest_rank(sorted_latency, 0.99),
        }
        stability_values = [sum(values) / len(values) for values in case_passes.values()]
        run.stability = statistics.fmean(stability_values) if stability_values else None


def _nearest_rank(sorted_values: list[int], percentile: float) -> float:
    if not sorted_values:
        return 0.0
    index = max(0, min(len(sorted_values) - 1, int(percentile * len(sorted_values) + 0.999) - 1))
    return float(sorted_values[index])
