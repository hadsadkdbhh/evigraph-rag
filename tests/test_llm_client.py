from __future__ import annotations

import json
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

from evigraph.clients import OpenAICompatibleLLMClient, _PreserveMethodRedirectHandler, _extract_json


class _FakeResponse:
    def __init__(self, body: dict | None = None) -> None:
        self.body = body or {"choices": [{"message": {"content": "ok"}}]}

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.body).encode("utf-8")


class OpenAICompatibleLLMClientTest(unittest.TestCase):
    def test_retries_transient_url_error(self) -> None:
        attempts = {"count": 0}

        def fake_urlopen(request, timeout):
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise urllib.error.URLError("handshake timed out")
            return _FakeResponse()

        client = OpenAICompatibleLLMClient(
            base_url="https://example.test/v1",
            api_key="test-key",
            model="test-model",
            timeout=1,
            max_retries=3,
            retry_backoff=0,
        )

        with patch.object(client.opener, "open", side_effect=fake_urlopen):
            text = client.chat_text([{"role": "user", "content": "hello"}])

        self.assertEqual(text, "ok")
        self.assertEqual(attempts["count"], 3)

    def test_responses_wire_api_parses_output_text(self) -> None:
        client = OpenAICompatibleLLMClient(
            base_url="https://example.test/v1",
            api_key="test-key",
            model="test-model",
            wire_api="responses",
        )
        body = {"output": [{"content": [{"type": "output_text", "text": '{"answer":"ok"}'}]}]}

        with patch.object(client.opener, "open", return_value=_FakeResponse(body)):
            text = client.chat_text([{"role": "user", "content": "hello"}])

        self.assertEqual(text, '{"answer":"ok"}')

    def test_redirect_handler_preserves_post_method_and_body(self) -> None:
        original = urllib.request.Request(
            "https://example.test/v1/responses",
            data=b'{"model":"x"}',
            headers={"Authorization": "Bearer test"},
            method="POST",
        )

        redirected = _PreserveMethodRedirectHandler().redirect_request(
            original,
            fp=None,
            code=302,
            msg="Found",
            headers={},
            newurl="https://example.test/v1/responses/",
        )

        self.assertIsNotNone(redirected)
        self.assertEqual(redirected.get_method(), "POST")
        self.assertEqual(redirected.data, b'{"model":"x"}')

    def test_extract_json_ignores_extra_content_after_first_object(self) -> None:
        payload = _extract_json('{"answer":"4.4%","citations":[]}\n{"debug":"extra"}')

        self.assertEqual(payload["answer"], "4.4%")

    def test_extract_json_finds_object_after_preface(self) -> None:
        payload = _extract_json('Here is the JSON:\n{"answer":"Insufficient evidence to answer.","citations":[]}\nthanks')

        self.assertEqual(payload["citations"], [])

    def test_extract_json_tolerates_missing_colon_in_calculation_field(self) -> None:
        payload = _extract_json(
            '```json\n{\n'
            '  "answer": "1495.939",\n'
            '  "citations": ["retrieved_3", "retrieved_4"],\n'
            '  "calculation "385373 + 1110566 = 1495939\n'
        )

        self.assertEqual(payload["answer"], "1495.939")
        self.assertEqual(payload["citations"], ["retrieved_3", "retrieved_4"])
        self.assertEqual(payload["calculation"], "385373 + 1110566 = 1495939")


if __name__ == "__main__":
    unittest.main()
