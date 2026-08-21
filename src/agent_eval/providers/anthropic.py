from __future__ import annotations

import json
import os
from importlib import import_module
from typing import Any

from agent_eval.providers.protocol import JudgeResult


class AnthropicJudgeProvider:
    name = "anthropic"

    def __init__(self) -> None:
        self.model: str = os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-5"
        module = import_module("anthropic")
        client_type: Any = module.AsyncAnthropic
        self.client: Any = client_type(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def judge(self, prompt: str, payload: dict[str, Any]) -> JudgeResult:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0,
            system=prompt,
            messages=[{"role": "user", "content": json.dumps(payload, default=str)}],
        )
        text = response.content[0].text
        if not isinstance(text, str):
            raise ValueError("judge returned no text content")
        return JudgeResult.model_validate_json(text)
