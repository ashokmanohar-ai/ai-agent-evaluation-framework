from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class JudgeResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    rationale: str = Field(min_length=1)


@runtime_checkable
class JudgeProvider(Protocol):
    name: str
    model: str

    async def judge(self, prompt: str, payload: dict[str, Any]) -> JudgeResult: ...
