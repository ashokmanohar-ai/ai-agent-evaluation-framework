from __future__ import annotations

from abc import ABC, abstractmethod

from agent_eval.models.dataset import EvaluationCase
from agent_eval.models.result import MetricResult
from agent_eval.models.trace import AgentTrace


class Evaluator(ABC):
    name: str
    version = "1.0.0"

    @abstractmethod
    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        """Evaluate observed evidence against one case's explicit expectations."""


def bounded_score(value: float) -> float:
    return max(0.0, min(1.0, value))
