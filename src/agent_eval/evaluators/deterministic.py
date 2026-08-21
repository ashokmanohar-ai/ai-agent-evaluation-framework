from __future__ import annotations

from datetime import datetime
from typing import Any

from agent_eval.core.evaluator import Evaluator, bounded_score
from agent_eval.models.dataset import ArgumentExpectation, EvaluationCase
from agent_eval.models.enums import (
    CompletionLevel,
    EvaluationDimension,
    FailureCode,
    MetricStatus,
    Severity,
)
from agent_eval.models.result import Failure, MetricResult
from agent_eval.models.trace import AgentTrace, ToolCall


def _result(
    name: str,
    dimension: EvaluationDimension,
    score: float,
    rationale: str,
    failures: list[Failure] | None = None,
    details: dict[str, Any] | None = None,
    *,
    skipped: bool = False,
) -> MetricResult:
    bounded = bounded_score(score)
    status = (
        MetricStatus.SKIP if skipped else MetricStatus.PASS if bounded >= 1.0 else MetricStatus.FAIL
    )
    return MetricResult(
        name=name,
        dimension=dimension,
        score=bounded,
        status=status,
        rationale=rationale,
        failures=failures or [],
        details=details or {},
    )


def _find_value(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for candidate_key, candidate_value in value.items():
            if candidate_key == key:
                found.append(candidate_value)
            found.extend(_find_value(candidate_value, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(_find_value(item, key))
    return found


def _has_fact(value: Any, key: str, expected: Any) -> bool:
    candidates = _find_value(value, key)
    if expected == "*":
        return bool(candidates)
    return any(candidate == expected for candidate in candidates)


def _normalize(value: Any, match: str) -> Any:
    if match == "casefold" and isinstance(value, str):
        return value.strip().casefold()
    if match == "date_equivalent" and isinstance(value, str):
        cleaned = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(cleaned).date().isoformat()
        except ValueError:
            return cleaned
    return value


def _argument_matches(actual: Any, expected: Any | ArgumentExpectation) -> bool:
    if isinstance(expected, ArgumentExpectation):
        spec = expected
    elif isinstance(expected, dict) and "value" in expected:
        spec = ArgumentExpectation.model_validate(expected)
    else:
        spec = ArgumentExpectation(value=expected)
    if spec.match == "semantic":
        # Semantic matching belongs to a model-based evaluator and cannot be claimed
        # deterministically.
        return False
    if spec.match == "contains":
        return str(spec.value).casefold() in str(actual).casefold()
    return bool(_normalize(actual, spec.match) == _normalize(spec.value, spec.match))


class TaskCompletionEvaluator(Evaluator):
    name = "task_completion"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        expected = case.expectations
        actual_tools = set(trace.tool_names(successful_only=True))
        missing_tools = sorted(set(expected.required_tools) - actual_tools)
        missing_facts = [
            key
            for key, value in expected.expected_facts.items()
            if not _has_fact(trace.final_output, key, value)
        ]
        completed_outcome = True
        if expected.expected_outcome:
            completed_outcome = (
                expected.expected_outcome.casefold() in str(trace.final_output).casefold()
            )
        missing_parts = len(missing_tools) + len(missing_facts) + int(not completed_outcome)
        total_parts = (
            len(expected.required_tools)
            + len(expected.expected_facts)
            + int(expected.expected_outcome is not None)
        )
        score = 1.0 if total_parts == 0 else (total_parts - missing_parts) / total_parts
        level = (
            CompletionLevel.COMPLETE
            if score == 1.0
            else CompletionLevel.PARTIAL
            if score > 0.0
            else CompletionLevel.FAILED
        )
        failures: list[Failure] = []
        if missing_tools:
            failures.append(
                Failure(
                    code=FailureCode.TASK_NOT_COMPLETED,
                    message=f"required execution did not occur: {missing_tools}",
                    evidence={"missing_tools": missing_tools},
                )
            )
        if missing_facts:
            failures.append(
                Failure(
                    code=FailureCode.REQUIRED_FACT_MISSING,
                    message=f"final output omitted required facts: {missing_facts}",
                    evidence={"missing_facts": missing_facts},
                )
            )
        return _result(
            self.name,
            EvaluationDimension.TASK,
            score,
            f"task completion level is {level}",
            failures,
            {"level": level, "missing_tools": missing_tools, "missing_facts": missing_facts},
        )


class ToolSelectionEvaluator(Evaluator):
    name = "tool_selection"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        expected = case.expectations
        actual = set(trace.tool_names())
        required = set(expected.required_tools)
        forbidden = set(expected.forbidden_tools)
        allowed = required | set(expected.optional_steps)
        missing = sorted(required - actual)
        forbidden_used = sorted(forbidden & actual)
        unexpected = sorted(actual - allowed - forbidden)
        denominator = max(1, len(required | actual))
        score = bounded_score(
            1 - (len(missing) + len(forbidden_used) + len(unexpected)) / denominator
        )
        failures: list[Failure] = []
        if missing:
            failures.append(
                Failure(
                    code=FailureCode.MISSING_TOOL,
                    message=f"missing required tools: {missing}",
                    evidence={"actual": sorted(actual)},
                )
            )
        if unexpected:
            failures.append(
                Failure(
                    code=FailureCode.WRONG_TOOL,
                    message=f"unexpected tools: {unexpected}",
                    evidence={"allowed": sorted(allowed)},
                )
            )
        if forbidden_used:
            failures.append(
                Failure(
                    code=FailureCode.FORBIDDEN_TOOL,
                    message=f"forbidden tools executed: {forbidden_used}",
                    severity=Severity.CRITICAL,
                    evidence={"forbidden": sorted(forbidden)},
                )
            )
            score = 0.0
        return _result(
            self.name,
            EvaluationDimension.TOOLING,
            score,
            "tool selection is computed from required, optional, forbidden and observed sets",
            failures,
            {
                "required": sorted(required),
                "actual": sorted(actual),
                "missing": missing,
                "unexpected": unexpected,
                "forbidden_used": forbidden_used,
            },
        )


class ToolArgumentEvaluator(Evaluator):
    name = "tool_argument_correctness"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        expectations = case.expectations.expected_tool_arguments
        if not expectations:
            return _result(
                self.name,
                EvaluationDimension.TOOLING,
                1.0,
                "no argument expectations configured",
                skipped=True,
            )
        checks: list[dict[str, Any]] = []
        failures: list[Failure] = []
        passed = 0
        total = 0
        for tool_name, expected_arguments in expectations.items():
            calls = [call for call in trace.tool_calls if call.tool_name == tool_name]
            call = next((candidate for candidate in reversed(calls) if candidate.success), None)
            if call is None and calls:
                # A failed call is still real trajectory evidence and its arguments remain testable.
                call = calls[-1]
            for argument_name, expected in expected_arguments.items():
                total += 1
                actual = call.arguments.get(argument_name) if call else None
                matched = call is not None and _argument_matches(actual, expected)
                passed += int(matched)
                checks.append(
                    {
                        "tool": tool_name,
                        "argument": argument_name,
                        "expected": expected.model_dump()
                        if isinstance(expected, ArgumentExpectation)
                        else expected,
                        "actual": actual,
                        "matched": matched,
                    }
                )
                if not matched:
                    failures.append(
                        Failure(
                            code=FailureCode.WRONG_ARGUMENT,
                            message=f"{tool_name}.{argument_name} did not match",
                            evidence=checks[-1],
                        )
                    )
        return _result(
            self.name,
            EvaluationDimension.TOOLING,
            passed / total if total else 1.0,
            f"{passed}/{total} expected arguments matched",
            failures,
            {"checks": checks},
        )


class PlanAdherenceEvaluator(Evaluator):
    name = "plan_adherence"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        mandatory = case.expectations.mandatory_steps
        forbidden = case.expectations.forbidden_actions
        actual = trace.step_names()
        missing = [step for step in mandatory if step not in actual]
        forbidden_seen = [
            step for step in forbidden if step in actual or step in trace.tool_names()
        ]
        total = len(mandatory) + len(forbidden)
        score = 1.0 if total == 0 else (total - len(missing) - len(forbidden_seen)) / total
        failures = [
            Failure(
                code=FailureCode.MISSING_STEP,
                message=f"mandatory step missing: {step}",
                evidence={"actual_steps": actual},
            )
            for step in missing
        ]
        failures.extend(
            Failure(
                code=FailureCode.POLICY_VIOLATION,
                message=f"forbidden action observed: {step}",
                severity=Severity.CRITICAL,
                evidence={"actual_steps": actual},
            )
            for step in forbidden_seen
        )
        return _result(
            self.name,
            EvaluationDimension.PLANNING,
            score,
            "mandatory and forbidden trajectory steps were evaluated",
            failures,
            {"missing": missing, "forbidden_seen": forbidden_seen},
            skipped=total == 0,
        )


class SequenceEvaluator(Evaluator):
    name = "sequence_correctness"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        ordered = case.expectations.ordered_steps
        if len(ordered) < 2:
            return _result(
                self.name,
                EvaluationDimension.TRAJECTORY,
                1.0,
                "no ordered trajectory configured",
                skipped=True,
            )
        actual = trace.step_names()
        position = -1
        matched: list[str] = []
        for expected_step in ordered:
            try:
                position = actual.index(expected_step, position + 1)
                matched.append(expected_step)
            except ValueError:
                break
        score = len(matched) / len(ordered)
        failures = []
        if score < 1.0:
            failures.append(
                Failure(
                    code=FailureCode.WRONG_SEQUENCE,
                    message=f"required order was not observed: {ordered}",
                    evidence={"actual_steps": actual, "matched_prefix": matched},
                )
            )
        return _result(
            self.name,
            EvaluationDimension.TRAJECTORY,
            score,
            f"{len(matched)}/{len(ordered)} ordered steps matched",
            failures,
        )


class GroundingEvaluator(Evaluator):
    name = "groundedness"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        expected_facts = case.expectations.expected_facts
        if not expected_facts:
            return _result(
                self.name,
                EvaluationDimension.GROUNDING,
                1.0,
                "no structured facts configured",
                skipped=True,
            )
        evidence: list[Any] = [trace.input]
        evidence.extend(
            call.result for call in trace.tool_calls if call.success and call.result is not None
        )
        evidence.extend(step.output for step in trace.steps if step.output is not None)
        supported = 0
        unsupported: list[str] = []
        for key, value in expected_facts.items():
            output_has_fact = _has_fact(trace.final_output, key, value)
            evidence_has_fact = any(_has_fact(item, key, value) for item in evidence)
            if output_has_fact and evidence_has_fact:
                supported += 1
            elif output_has_fact:
                unsupported.append(key)
        score = supported / len(expected_facts)
        failures = [
            Failure(
                code=FailureCode.UNSUPPORTED_CLAIM,
                message=f"final fact has no execution evidence: {key}",
                evidence={"key": key},
            )
            for key in unsupported
        ]
        missing = [
            key
            for key, value in expected_facts.items()
            if not _has_fact(trace.final_output, key, value)
        ]
        failures.extend(
            Failure(
                code=FailureCode.REQUIRED_FACT_MISSING,
                message=f"required final fact missing: {key}",
                evidence={"key": key},
            )
            for key in missing
        )
        return _result(
            self.name,
            EvaluationDimension.GROUNDING,
            score,
            f"{supported}/{len(expected_facts)} final facts have trace evidence",
            failures,
            {"unsupported": unsupported, "missing": missing},
        )


class ToolResultUsageEvaluator(Evaluator):
    name = "tool_result_usage"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        facts = case.expectations.expected_facts
        relevant_calls = [
            call for call in trace.tool_calls if call.success and call.result is not None
        ]
        if not relevant_calls or not facts:
            return _result(
                self.name,
                EvaluationDimension.GROUNDING,
                1.0,
                "no structured tool-result usage check required",
                skipped=True,
            )
        used = sum(_has_fact(trace.final_output, key, value) for key, value in facts.items())
        score = used / len(facts)
        failures = []
        if score < 1.0:
            failures.append(
                Failure(
                    code=FailureCode.TASK_NOT_COMPLETED,
                    message="final response did not use all required tool-result facts",
                    evidence={"expected_facts": facts},
                )
            )
        return _result(
            self.name,
            EvaluationDimension.GROUNDING,
            score,
            f"{used}/{len(facts)} required tool facts were used",
            failures,
        )


class EfficiencyEvaluator(Evaluator):
    name = "step_efficiency"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        expected = case.expectations
        actual_count = len(trace.tool_calls)
        allowed_count = (
            len(expected.required_tools)
            + len(expected.optional_steps)
            + sum(expected.allowed_retries.values())
        )
        allowed_count = max(allowed_count, len(expected.required_tools))
        if actual_count == 0:
            score = 1.0 if not expected.required_tools else 0.0
        else:
            score = min(1.0, allowed_count / actual_count)
        maximum = expected.maximum_tool_calls
        breached = maximum is not None and actual_count > maximum
        if breached:
            score = 0.0
        failures = []
        if score < 1.0:
            failures.append(
                Failure(
                    code=FailureCode.EXCESSIVE_TOOL_CALLS,
                    message=(
                        f"observed {actual_count} calls; useful/allowed count is {allowed_count}"
                    ),
                    evidence={"actual": actual_count, "allowed": allowed_count, "maximum": maximum},
                )
            )
        return _result(
            self.name,
            EvaluationDimension.EFFICIENCY,
            score,
            "efficiency is allowed useful calls divided by observed calls",
            failures,
            {"actual_tool_calls": actual_count, "allowed_tool_calls": allowed_count},
        )


def calls_for(trace: AgentTrace, name: str) -> list[ToolCall]:
    return [call for call in trace.tool_calls if call.tool_name == name]
