from __future__ import annotations

import json
import os
from importlib import import_module
from typing import Any

from agent_eval.providers.protocol import JudgeResult


class OpenAIJudgeProvider:
    name = "openai"

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model: str = model or os.getenv("OPENAI_MODEL") or "gpt-5-mini"
        module = import_module("openai")
        client_type: Any = module.AsyncOpenAI
        self.client: Any = client_type(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or os.getenv("OPENAI_BASE_URL"),
        )

    async def judge(self, prompt: str, payload: dict[str, Any]) -> JudgeResult:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(payload, default=str)},
            ],
        )
        content = response.choices[0].message.content
        if not isinstance(content, str):
            raise ValueError("judge returned no text content")
        return JudgeResult.model_validate_json(content)


class AzureOpenAIJudgeProvider(OpenAIJudgeProvider):
    name = "azure-openai"

    def __init__(self) -> None:
        self.model = os.environ["AZURE_OPENAI_DEPLOYMENT"]
        module = import_module("openai")
        client_type: Any = module.AsyncAzureOpenAI
        self.client: Any = client_type(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )
