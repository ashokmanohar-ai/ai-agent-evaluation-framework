from __future__ import annotations

import os

from agent_eval.providers.anthropic import AnthropicJudgeProvider
from agent_eval.providers.mock import MockJudgeProvider
from agent_eval.providers.openai import AzureOpenAIJudgeProvider, OpenAIJudgeProvider
from agent_eval.providers.protocol import JudgeProvider


def create_judge_provider(name: str | None = None) -> JudgeProvider:
    provider = (name or os.getenv("EVAL_MODEL_PROVIDER") or "mock").casefold()
    if provider == "mock":
        return MockJudgeProvider()
    if provider in {"openai", "openai-compatible"}:
        return OpenAIJudgeProvider()
    if provider in {"azure", "azure-openai"}:
        return AzureOpenAIJudgeProvider()
    if provider == "anthropic":
        return AnthropicJudgeProvider()
    raise ValueError(f"unsupported judge provider: {provider}")
