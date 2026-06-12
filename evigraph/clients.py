from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class LLMClient:
    def chat_text(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        raise NotImplementedError

    def chat_json(self, messages: list[dict[str, str]], schema: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.chat_text(messages, temperature=0.0)
        return _extract_json(text)


class OpenAICompatibleLLMClient(LLMClient):
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int = 60,
    ) -> None:
        self.base_url = (base_url or os.getenv("LLM_BASE_URL") or "").rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model or os.getenv("LLM_MODEL")
        self.timeout = timeout
        if not self.base_url or not self.api_key or not self.model:
            raise ValueError("LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL are required for openai_compatible LLM.")

    def chat_text(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"LLM request failed with HTTP {exc.code}: {detail}") from exc
        return str(body["choices"][0]["message"]["content"])


class NullLLMClient(LLMClient):
    def chat_text(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        raise RuntimeError("No LLM client configured.")


def make_llm_client(config: dict[str, Any] | None = None) -> LLMClient:
    config = config or {}
    provider = str(config.get("provider") or os.getenv("LLM_PROVIDER") or "none").lower()
    if provider in {"none", "null", "mock"}:
        return NullLLMClient()
    if provider == "openai_compatible":
        return OpenAICompatibleLLMClient(
            base_url=config.get("base_url"),
            api_key=config.get("api_key"),
            model=config.get("model"),
            timeout=int(config.get("timeout", 60)),
        )
    raise ValueError(f"Unsupported LLM provider: {provider}")


def _extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"LLM did not return JSON: {text[:200]}")
    return json.loads(stripped[start : end + 1])
