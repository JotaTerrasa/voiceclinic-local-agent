from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

import httpx

from voiceclinic.config import Settings


class ChatLLM(Protocol):
    provider: str
    model: str

    async def complete(self, system: str, user: str) -> str | None:
        raise NotImplementedError

    async def extract_json(self, system: str, user: str) -> dict | None:
        raise NotImplementedError


@dataclass(frozen=True)
class OpenAICompatibleChatClient:
    provider: str
    base_url: str
    model: str
    api_key: str | None = None
    timeout_seconds: float = 8

    async def complete(self, system: str, user: str) -> str | None:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.1,
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else None
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException):
            return None
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def extract_json(self, system: str, user: str) -> dict | None:
        content = await self.complete(system, user)
        if not content:
            return None
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None


class OllamaClient(OpenAICompatibleChatClient):
    def __init__(self, base_url: str, model: str, timeout_seconds: float = 8):
        super().__init__(
            provider="ollama",
            base_url=base_url,
            model=model,
            timeout_seconds=timeout_seconds,
        )


def build_llm_client(settings: Settings | None) -> ChatLLM | None:
    if settings is None:
        return None

    if settings.llm_provider == "none":
        return None

    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            return None
        return OpenAICompatibleChatClient(
            provider="openai",
            base_url=settings.openai_base_url.rstrip("/"),
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            timeout_seconds=settings.openai_timeout_seconds,
        )

    return OpenAICompatibleChatClient(
        provider="ollama",
        base_url=settings.ollama_base_url.rstrip("/"),
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
