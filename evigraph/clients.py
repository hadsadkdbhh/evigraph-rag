from __future__ import annotations

import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from typing import Any


class _PreserveMethodRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code not in (301, 302, 303, 307, 308):
            return None
        return urllib.request.Request(
            newurl,
            data=req.data,
            headers=dict(req.headers),
            origin_req_host=req.origin_req_host,
            unverifiable=True,
            method=req.get_method(),
        )


class LLMClient:
    def chat_text(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        raise NotImplementedError

    def chat_json(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, Any] | None = None,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        text = self.chat_text(messages, temperature=temperature)
        return _extract_json(text)


class OpenAICompatibleLLMClient(LLMClient):
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int = 60,
        max_retries: int = 2,
        retry_backoff: float = 2.0,
        wire_api: str = "chat_completions",
    ) -> None:
        self.base_url = (base_url or os.getenv("LLM_BASE_URL") or "").rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model or os.getenv("LLM_MODEL")
        self.timeout = timeout
        self.max_retries = max(0, max_retries)
        self.retry_backoff = max(0.0, retry_backoff)
        self.wire_api = wire_api
        self.opener = urllib.request.build_opener(_PreserveMethodRedirectHandler)
        if not self.base_url or not self.api_key or not self.model:
            raise ValueError("LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL are required for openai_compatible LLM.")

    def chat_text(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        payload = self._payload(messages, temperature)
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self._endpoint(),
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        body = self._open_with_retries(request)
        return self._response_text(body)

    def _endpoint(self) -> str:
        if self.wire_api == "responses":
            return f"{self.base_url}/responses"
        return f"{self.base_url}/chat/completions"

    def _payload(self, messages: list[dict[str, str]], temperature: float) -> dict[str, Any]:
        if self.wire_api == "responses":
            return {
                "model": self.model,
                "input": [{"role": item["role"], "content": item["content"]} for item in messages],
                "temperature": temperature,
            }
        return {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

    def _response_text(self, body: dict[str, Any]) -> str:
        if self.wire_api == "responses":
            output_text = body.get("output_text")
            if output_text:
                return str(output_text)
            for item in body.get("output", []):
                if not isinstance(item, dict):
                    continue
                for content in item.get("content", []):
                    if not isinstance(content, dict):
                        continue
                    if content.get("type") in {"output_text", "text"} and content.get("text") is not None:
                        return str(content["text"])
            raise RuntimeError(f"Responses API body did not contain text output: {str(body)[:200]}")
        choices = body.get("choices")
        if not choices or not isinstance(choices, list):
            raise RuntimeError(f"Chat completions body did not contain choices: {str(body)[:200]}")
        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message") if isinstance(first.get("message"), dict) else {}
        content = message.get("content")
        if content is None and first.get("text") is not None:
            content = first.get("text")
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("text") is not None:
                    parts.append(str(item["text"]))
                elif isinstance(item, str):
                    parts.append(item)
            content = "".join(parts)
        if content is None:
            raise RuntimeError(f"Chat completions body did not contain message content: {str(body)[:200]}")
        return str(content)

    def _open_with_retries(self, request: urllib.request.Request) -> dict[str, Any]:
        last_error: BaseException | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with self.opener.open(request, timeout=self.timeout) as response:
                    raw_body = response.read().decode("utf-8", errors="replace")
                    try:
                        return json.loads(raw_body)
                    except json.JSONDecodeError as exc:
                        raise RuntimeError(f"LLM response was not valid JSON: {raw_body[:200]}") from exc
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="ignore")
                if not self._retryable_http_error(exc.code) or attempt >= self.max_retries:
                    raise RuntimeError(f"LLM request failed with HTTP {exc.code}: {detail}") from exc
                last_error = RuntimeError(f"LLM request failed with HTTP {exc.code}: {detail}")
            except (TimeoutError, socket.timeout, urllib.error.URLError) as exc:
                if attempt >= self.max_retries:
                    raise RuntimeError(f"LLM request failed after {attempt + 1} attempts: {exc}") from exc
                last_error = exc
            self._sleep_before_retry(attempt)
        raise RuntimeError(f"LLM request failed after retries: {last_error}")

    def _sleep_before_retry(self, attempt: int) -> None:
        if self.retry_backoff <= 0:
            return
        time.sleep(self.retry_backoff * (attempt + 1))

    def _retryable_http_error(self, code: int) -> bool:
        return code == 429 or 500 <= code < 600


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
            max_retries=int(config.get("max_retries", 2)),
            retry_backoff=float(config.get("retry_backoff", 2.0)),
            wire_api=str(config.get("wire_api", "chat_completions")),
        )
    raise ValueError(f"Unsupported LLM provider: {provider}")


def _extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    decoder = json.JSONDecoder()
    for start, char in enumerate(stripped):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(stripped[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    loose = _extract_loose_json_fields(stripped)
    loose.update({key: value for key, value in _extract_loose_json_fields(text).items() if key not in loose})
    if loose:
        return loose
    raise ValueError(f"LLM did not return JSON: {text[:200]}")


def _extract_loose_json_fields(text: str) -> dict[str, Any]:
    answer = _loose_string_field(text, "answer")
    calculation = _loose_string_field(text, "calculation") or _loose_string_field(text, "calculations")
    citations = _loose_list_field(text, "citations")
    if answer is None and calculation is None and not citations:
        return {}
    payload: dict[str, Any] = {}
    if answer is not None:
        payload["answer"] = answer
    if citations:
        payload["citations"] = citations
    if calculation is not None:
        payload["calculation"] = calculation
    return payload


def _loose_string_field(text: str, key: str) -> str | None:
    match = re.search(rf'"{re.escape(key)}"\s*:?\s*"([^"]*)"', text)
    if not match and key in {"calculation", "calculations"}:
        match = re.search(rf'"{re.escape(key)}\s*"\s*:?\s*"?(.*?)(?:\r?\n|,\s*"|\}})', text)
    if not match:
        return None
    value = match.group(1).strip()
    return value if value else None


def _loose_list_field(text: str, key: str) -> list[str]:
    match = re.search(rf'"{re.escape(key)}"\s*:?\s*\[(.*?)\]', text, flags=re.DOTALL)
    if not match:
        return []
    return [item.strip() for item in re.findall(r'"([^"]+)"', match.group(1))]
