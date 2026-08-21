from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ArgumentExpectation(BaseModel):
    value: Any
    match: Literal["exact", "casefold", "contains", "date_equivalent", "semantic"] = "exact"


class StepExpectation(BaseModel):
    name: str
    requirement: Literal["required", "optional", "forbidden"] = "required"


class EvaluationExpectations(BaseModel):
    task: str
    required_tools: list[str] = Field(default_factory=list)
    forbidden_tools: list[str] = Field(default_factory=list)
    expected_tool_arguments: dict[str, dict[str, Any | ArgumentExpectation]] = Field(
        default_factory=dict
    )
    expected_facts: dict[str, Any] = Field(default_factory=dict)
    mandatory_steps: list[str] = Field(default_factory=list)
    ordered_steps: list[str] = Field(default_factory=list)
    optional_steps: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    expected_outcome: str | None = None
    expected_escalation: bool = False
    approval_required_for: list[str] = Field(default_factory=list)
    expected_recovery: str | None = None
    maximum_tool_calls: int | None = Field(default=None, ge=0)
    maximum_latency_ms: int | None = Field(default=None, ge=0)
    maximum_tokens: int | None = Field(default=None, ge=0)
    expected_agent: str | None = None
    maximum_handoffs: int | None = Field(default=None, ge=0)
    allowed_retries: dict[str, int] = Field(default_factory=dict)
    forbidden_claims: list[str] = Field(default_factory=list)


class EvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    description: str
    input: dict[str, Any]
    expectations: EvaluationExpectations
    tags: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_case(self) -> EvaluationCase:
        overlap = set(self.expectations.required_tools) & set(self.expectations.forbidden_tools)
        if overlap:
            raise ValueError(f"tools cannot be required and forbidden: {sorted(overlap)}")
        if not self.tags:
            raise ValueError("at least one tag is required")
        return self


class EvaluationDataset(BaseModel):
    name: str
    version: str
    cases: list[EvaluationCase]
    source_files: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_ids(self) -> EvaluationDataset:
        ids = [case.id for case in self.cases]
        duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
        if duplicates:
            raise ValueError(f"duplicate case IDs: {duplicates}")
        return self


def load_jsonl(path: str | Path) -> list[EvaluationCase]:
    source = Path(path)
    cases: list[EvaluationCase] = []
    with source.open(encoding="utf-8") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                cases.append(EvaluationCase.model_validate_json(line))
            except (ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"{source}:{line_number}: {exc}") from exc
    if not cases:
        raise ValueError(f"dataset contains no cases: {source}")
    return cases


def load_dataset(paths: Sequence[str | Path], name: str = "agent-evaluation") -> EvaluationDataset:
    cases: list[EvaluationCase] = []
    source_files: list[str] = []
    versions: set[str] = set()
    for path in paths:
        source = Path(path)
        source_files.append(str(source))
        loaded = load_jsonl(source)
        cases.extend(loaded)
        versions.update(str(case.metadata.get("dataset_version", "1.0")) for case in loaded)
    version = "+".join(sorted(versions))
    return EvaluationDataset(name=name, version=version, cases=cases, source_files=source_files)


def validate_tool_references(dataset: EvaluationDataset, allowed_tools: set[str]) -> None:
    unknown: dict[str, list[str]] = {}
    for case in dataset.cases:
        referenced = set(case.expectations.required_tools)
        referenced.update(case.expectations.forbidden_tools)
        referenced.update(case.expectations.expected_tool_arguments)
        missing = sorted(referenced - allowed_tools)
        if missing:
            unknown[case.id] = missing
    if unknown:
        raise ValueError(f"dataset references tools absent from the policy allow-list: {unknown}")
