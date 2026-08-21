from __future__ import annotations

from agent_eval.core.evaluator import Evaluator


class EvaluatorRegistry:
    def __init__(self) -> None:
        self._evaluators: dict[str, Evaluator] = {}

    def register(self, evaluator: Evaluator) -> None:
        if evaluator.name in self._evaluators:
            raise ValueError(f"evaluator already registered: {evaluator.name}")
        self._evaluators[evaluator.name] = evaluator

    def get(self, name: str) -> Evaluator:
        try:
            return self._evaluators[name]
        except KeyError as exc:
            raise KeyError(f"unknown evaluator: {name}") from exc

    def all(self) -> list[Evaluator]:
        return list(self._evaluators.values())
